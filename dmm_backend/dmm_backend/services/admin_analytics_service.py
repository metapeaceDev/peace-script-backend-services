"""
Admin Analytics Service - Theme Usage & Performance Analytics
============================================================

Service layer for gathering and analyzing theme usage data.

This service provides:
- Theme usage statistics
- Category distribution analysis
- Search and filter analytics
- Performance metrics
- Trend analysis
- Report generation

Author: Peace Script Team
Date: 19 November 2025 (2568 BE)
Version: 1.0
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import Counter
from dataclasses import dataclass


@dataclass
class ThemeStats:
    """Statistics about themes"""
    total_themes: int
    total_categories: int
    archived_themes: int
    active_themes: int
    creation_trend: Dict[str, int]
    most_used_categories: List[tuple]


@dataclass
class UsageAnalytics:
    """Usage statistics"""
    total_searches: int
    total_selections: int
    avg_selection_rate: float
    most_selected: List[tuple]
    least_selected: List[tuple]
    search_queries: Dict[str, int]


class AdminAnalyticsService:
    """Service for theme analytics and reporting"""
    
    def __init__(self):
        self._usage_data: Dict[str, Dict[str, Any]] = {}
        self._search_history: List[Dict[str, Any]] = []
        self._selection_history: List[Dict[str, Any]] = []
    
    def record_search(
        self,
        query: str,
        results_count: int,
        user_id: Optional[str] = None
    ) -> None:
        """Record a search operation"""
        self._search_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'results_count': results_count,
            'user_id': user_id
        })
    
    def record_selection(
        self,
        theme_id: str,
        user_id: Optional[str] = None
    ) -> None:
        """Record a theme selection"""
        self._selection_history.append({
            'timestamp': datetime.now().isoformat(),
            'theme_id': theme_id,
            'user_id': user_id
        })
        
        # Update usage data
        if theme_id not in self._usage_data:
            self._usage_data[theme_id] = {
                'selection_count': 0,
                'last_selected': None
            }
        
        self._usage_data[theme_id]['selection_count'] += 1
        self._usage_data[theme_id]['last_selected'] = datetime.now().isoformat()
    
    def get_theme_stats(self, themes: List[Dict[str, Any]]) -> ThemeStats:
        """Get overall theme statistics"""
        active_themes = [t for t in themes if not t.get('is_archived', False)]
        archived_themes = [t for t in themes if t.get('is_archived', False)]
        
        # Get categories
        categories = set(t.get('category', 'Unknown') for t in active_themes)
        
        # Get creation trend (by month)
        creation_trend = self._get_creation_trend(active_themes)
        
        # Get most used categories
        category_counts = Counter(t.get('category') for t in active_themes)
        most_used = category_counts.most_common(5)
        
        return ThemeStats(
            total_themes=len(themes),
            total_categories=len(categories),
            archived_themes=len(archived_themes),
            active_themes=len(active_themes),
            creation_trend=creation_trend,
            most_used_categories=most_used
        )
    
    def get_usage_analytics(self) -> UsageAnalytics:
        """Get usage analytics"""
        total_searches = len(self._search_history)
        total_selections = len(self._selection_history)
        
        # Calculate average selection rate
        if total_searches > 0:
            avg_selection_rate = total_selections / total_searches
        else:
            avg_selection_rate = 0.0
        
        # Get most and least selected themes
        selection_counts = Counter(r['theme_id'] for r in self._selection_history)
        most_selected = selection_counts.most_common(10)
        least_selected = selection_counts.most_common()[-10:] if selection_counts else []
        
        # Get search queries frequency
        search_queries = Counter(r['query'] for r in self._search_history)
        
        return UsageAnalytics(
            total_searches=total_searches,
            total_selections=total_selections,
            avg_selection_rate=avg_selection_rate,
            most_selected=most_selected,
            least_selected=least_selected,
            search_queries=dict(search_queries.most_common(20))
        )
    
    def get_category_distribution(self, themes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of themes across categories"""
        active_themes = [t for t in themes if not t.get('is_archived', False)]
        category_counts = Counter(t.get('category', 'Unknown') for t in active_themes)
        return dict(category_counts)
    
    def get_performance_metrics(self, themes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get performance-related metrics"""
        active_themes = [t for t in themes if not t.get('is_archived', False)]
        
        # Themes with complete story guidelines
        complete_sg = sum(1 for t in active_themes 
                         if 'story_guidelines' in t and 
                         all(f in t['story_guidelines'] 
                             for f in ['theme_stated', 'b_story', 'break_into_three', 'finale']))
        
        # Themes with sub-theme recommendations
        with_subthemes = sum(1 for t in active_themes 
                            if t.get('recommended_sub_themes'))
        
        # Average sub-themes per theme
        avg_subthemes = 0
        if with_subthemes > 0:
            total_subthemes = sum(len(t.get('recommended_sub_themes', [])) 
                                 for t in active_themes)
            avg_subthemes = total_subthemes / len(active_themes)
        
        # Themes with descriptions
        with_descriptions = sum(1 for t in active_themes if t.get('description'))
        
        # Data quality score (0-100)
        quality_score = 0
        if active_themes:
            quality_score = (
                (complete_sg / len(active_themes) * 25) +  # 25% for complete SG
                (with_subthemes / len(active_themes) * 25) +  # 25% for sub-themes
                (with_descriptions / len(active_themes) * 25) +  # 25% for descriptions
                (25)  # 25% for all themes existing
            )
        
        return {
            'total_active_themes': len(active_themes),
            'themes_with_complete_story_guidelines': complete_sg,
            'themes_with_sub_theme_recommendations': with_subthemes,
            'avg_sub_themes_per_theme': round(avg_subthemes, 2),
            'themes_with_descriptions': with_descriptions,
            'data_quality_score': round(quality_score, 2)
        }
    
    def get_search_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get search analytics for last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_searches = [
            s for s in self._search_history
            if datetime.fromisoformat(s['timestamp']) > cutoff_date
        ]
        
        if not recent_searches:
            return {
                'period_days': days,
                'total_searches': 0,
                'unique_queries': 0,
                'avg_results_per_search': 0,
                'top_queries': []
            }
        
        total_searches = len(recent_searches)
        unique_queries = len(set(s['query'] for s in recent_searches))
        avg_results = sum(s['results_count'] for s in recent_searches) / total_searches
        
        query_counts = Counter(s['query'] for s in recent_searches)
        top_queries = query_counts.most_common(10)
        
        return {
            'period_days': days,
            'total_searches': total_searches,
            'unique_queries': unique_queries,
            'avg_results_per_search': round(avg_results, 2),
            'top_queries': list(top_queries)
        }
    
    def get_selection_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get selection analytics for last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_selections = [
            s for s in self._selection_history
            if datetime.fromisoformat(s['timestamp']) > cutoff_date
        ]
        
        if not recent_selections:
            return {
                'period_days': days,
                'total_selections': 0,
                'unique_themes_selected': 0,
                'most_selected': [],
                'least_selected': []
            }
        
        total_selections = len(recent_selections)
        
        theme_counts = Counter(s['theme_id'] for s in recent_selections)
        unique_themes = len(theme_counts)
        
        most_selected = theme_counts.most_common(5)
        least_selected = [(t, c) for t, c in theme_counts.most_common() if c == 1][:5]
        
        return {
            'period_days': days,
            'total_selections': total_selections,
            'unique_themes_selected': unique_themes,
            'most_selected': most_selected,
            'least_selected': least_selected
        }
    
    def _get_creation_trend(self, themes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get theme creation trend by month"""
        trend = {}
        
        for theme in themes:
            created_at = theme.get('created_at')
            if created_at:
                # Extract year-month
                date_obj = datetime.fromisoformat(created_at)
                month_key = date_obj.strftime('%Y-%m')
                
                if month_key not in trend:
                    trend[month_key] = 0
                trend[month_key] += 1
        
        return dict(sorted(trend.items()))
    
    def generate_report(
        self,
        themes: List[Dict[str, Any]],
        days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        return {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'theme_stats': self.get_theme_stats(themes),
            'usage_analytics': self.get_usage_analytics(),
            'category_distribution': self.get_category_distribution(themes),
            'performance_metrics': self.get_performance_metrics(themes),
            'search_analytics': self.get_search_analytics(days),
            'selection_analytics': self.get_selection_analytics(days)
        }


# Singleton instance
_service_instance: Optional[AdminAnalyticsService] = None


def get_admin_analytics_service() -> AdminAnalyticsService:
    """Get singleton instance of AdminAnalyticsService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = AdminAnalyticsService()
    return _service_instance
