"""
Optimized Dhamma Theme Service with Caching & Performance
=========================================================

Enhanced version of DhammaThemeService with:
- In-memory caching layer using LRU cache
- Indexed lookups for O(1) performance
- Query optimization for filtering and search
- Performance monitoring and metrics
- Cache invalidation strategies

Author: Peace Script Team
Date: 18 November 2025 (2568 BE)
Version: 2.0 (Optimized)
"""

import json
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

from .cache_optimization import ThemeQueryOptimizer, PerformanceMonitor


class DhammaThemeServiceOptimized:
    """Optimized service for managing Dhamma themes with caching"""
    
    def __init__(self, enable_cache: bool = True):
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._themes_by_category: Dict[str, List[str]] = {}
        self._loaded = False
        self.enable_cache = enable_cache
        self.optimizer: Optional[ThemeQueryOptimizer] = None
        self.monitor: Optional[PerformanceMonitor] = None
        self.load_start_time = None
        self.load_end_time = None
        
    def _get_themes_file_path(self) -> Path:
        """Get absolute path to dhamma_themes.json"""
        current_dir = Path(__file__).parent
        backend_dir = current_dir.parent
        project_root = backend_dir.parent
        themes_path = project_root / "definitions" / "dhamma_themes.json"
        return themes_path
    
    def load_themes(self) -> None:
        """Load themes from JSON file with optimization indices"""
        if self._loaded:
            return
        
        self.load_start_time = datetime.now()
        themes_path = self._get_themes_file_path()
        
        if not themes_path.exists():
            raise FileNotFoundError(f"Dhamma themes file not found: {themes_path}")
        
        with open(themes_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        themes_list = data.get('dhamma_themes', {}).get('themes', [])
        
        # Build indices
        for theme in themes_list:
            theme_id = theme['id']
            self._themes[theme_id] = theme
            
            # Index by category
            category = theme.get('category', 'อื่นๆ')
            if category not in self._themes_by_category:
                self._themes_by_category[category] = []
            self._themes_by_category[category].append(theme_id)
        
        # Initialize cache optimizer if enabled
        if self.enable_cache:
            self.optimizer = ThemeQueryOptimizer(themes_list)
            self.monitor = PerformanceMonitor(self.optimizer)
        
        self._loaded = True
        self.load_end_time = datetime.now()
        
        load_time = (self.load_end_time - self.load_start_time).total_seconds() * 1000
        print(f"✅ Loaded {len(self._themes)} Dhamma themes in {load_time:.2f}ms")
        if self.enable_cache:
            print(f"✅ Cache optimization enabled with {len(themes_list)} indexed themes")
    
    def get_theme(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """Get theme by ID - uses indexed lookup O(1)"""
        if not self._loaded:
            self.load_themes()
        
        if self.optimizer:
            return self.optimizer.get_theme_by_id(theme_id)
        return self._themes.get(theme_id)
    
    def get_all_themes(self) -> List[Dict[str, Any]]:
        """Get all available themes"""
        if not self._loaded:
            self.load_themes()
        return list(self._themes.values())
    
    def get_themes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get themes by category - uses index"""
        if not self._loaded:
            self.load_themes()
        
        if self.optimizer:
            return self.optimizer.get_themes_by_category(category)
        
        theme_ids = self._themes_by_category.get(category, [])
        return [self._themes[tid] for tid in theme_ids]
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        if not self._loaded:
            self.load_themes()
        
        if self.optimizer:
            return self.optimizer.get_all_categories()
        
        return sorted(list(self._themes_by_category.keys()))
    
    def search_themes(
        self, 
        query: str,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search themes with optimized query"""
        if not self._loaded:
            self.load_themes()
        
        # Use optimizer if available
        if self.optimizer:
            results = self.optimizer.search_themes(query)
            
            # Apply category filter if provided
            if category:
                results = [t for t in results if t.get('category') == category]
            
            if limit:
                results = results[:limit]
            
            return results
        
        # Fallback to basic search
        results = []
        query_lower = query.lower()
        
        for theme in self._themes.values():
            if (query_lower in theme.get('id', '').lower() or
                query_lower in theme.get('thai_name', '').lower() or
                query_lower in theme.get('pali_name', '').lower() or
                query_lower in theme.get('description', '').lower()):
                
                if category and theme.get('category') != category:
                    continue
                
                results.append(theme)
        
        if limit:
            results = results[:limit]
        
        return results
    
    def get_sub_themes(self, theme_id: str) -> List[Dict[str, Any]]:
        """Get sub-themes with optimization"""
        if not self._loaded:
            self.load_themes()
        
        if self.optimizer:
            return self.optimizer.get_sub_themes(theme_id)
        
        # Fallback
        theme = self._themes.get(theme_id)
        if not theme:
            return []
        
        sub_theme_ids = theme.get('recommended_sub_themes', [])
        return [self._themes[sid] for sid in sub_theme_ids if sid in self._themes]
    
    def filter_themes(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        has_story_guidelines: Optional[bool] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Filter themes with multiple criteria"""
        if not self._loaded:
            self.load_themes()
        
        filters = {}
        if category:
            filters['category'] = category
        if search:
            filters['search'] = search
        if has_story_guidelines is not None:
            filters['has_story_guidelines'] = has_story_guidelines
        
        # Use optimizer if available
        if self.optimizer and filters:
            results = self.optimizer.filter_themes(**filters)
        else:
            # Fallback to basic filtering
            results = list(self._themes.values())
            
            if category:
                results = [t for t in results if t.get('category') == category]
            
            if search:
                search_lower = search.lower()
                results = [t for t in results if
                          search_lower in t.get('id', '').lower() or
                          search_lower in t.get('thai_name', '').lower()]
            
            if has_story_guidelines:
                results = [t for t in results if 'story_guidelines' in t and
                          all(f in t['story_guidelines'] for f in 
                              ['theme_stated', 'b_story', 'break_into_three', 'finale'])]
        
        if limit:
            results = results[:limit]
        
        return results
    
    def validate_theme(self, theme_id: str) -> Dict[str, Any]:
        """Validate a theme structure"""
        theme = self.get_theme(theme_id)
        
        if not theme:
            return {
                'valid': False,
                'theme_id': theme_id,
                'error': 'Theme not found'
            }
        
        required_fields = [
            'id', 'thai_name', 'pali_name', 'category',
            'description', 'story_guidelines', 'recommended_sub_themes'
        ]
        
        missing_fields = [f for f in required_fields if f not in theme]
        
        # Check story_guidelines completeness
        story_guidelines_fields = ['theme_stated', 'b_story', 'break_into_three', 'finale']
        story_guidelines = theme.get('story_guidelines', {})
        missing_sg_fields = [f for f in story_guidelines_fields if f not in story_guidelines]
        
        is_valid = len(missing_fields) == 0 and len(missing_sg_fields) == 0
        
        return {
            'valid': is_valid,
            'theme_id': theme_id,
            'missing_fields': missing_fields,
            'missing_story_guidelines_fields': missing_sg_fields,
            'story_guidelines_complete': len(missing_sg_fields) == 0
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self._loaded:
            return {'loaded': False}
        
        stats = {
            'loaded': True,
            'themes_count': len(self._themes),
            'categories_count': len(self._themes_by_category),
            'cache_enabled': self.enable_cache
        }
        
        if self.load_start_time and self.load_end_time:
            load_time = (self.load_end_time - self.load_start_time).total_seconds() * 1000
            stats['load_time_ms'] = f"{load_time:.2f}"
        
        if self.monitor:
            stats['cache_stats'] = self.monitor.optimizer.cache_manager.get_stats()
        
        return stats
    
    def clear_cache(self):
        """Clear the optimization cache"""
        if self.optimizer:
            self.optimizer.cache_manager.invalidate()
    
    def invalidate_theme_cache(self, theme_id: str):
        """Invalidate cache for specific theme"""
        if self.optimizer:
            self.optimizer.invalidate_cache(theme_id)
    
    def batch_get_themes(self, theme_ids: List[str]) -> Dict[str, Dict]:
        """Get multiple themes efficiently"""
        if not self._loaded:
            self.load_themes()
        
        if self.optimizer:
            return self.optimizer.batch_get_themes(theme_ids)
        
        # Fallback
        return {tid: self._themes[tid] for tid in theme_ids if tid in self._themes}


# Singleton instance
_service_instance: Optional[DhammaThemeServiceOptimized] = None


def get_dhamma_theme_service() -> DhammaThemeServiceOptimized:
    """Get singleton instance of optimized DhammaThemeService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = DhammaThemeServiceOptimized(enable_cache=True)
        _service_instance.load_themes()
    return _service_instance


def reset_service():
    """Reset service instance (for testing)"""
    global _service_instance
    _service_instance = None
