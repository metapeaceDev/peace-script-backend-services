"""
Dhamma Theme Service
====================
Service layer for managing Dhamma-based themes for Peace Script narratives.

This service provides:
- Loading and caching of dhamma themes from definitions/dhamma_themes.json
- Theme search and filtering by category, conflict type, keywords
- Validation of user-provided themes against dhamma principles
- Recommendation of appropriate themes based on story context

Author: Peace Script Team
Date: 18 November 2025 (2568 BE)
Version: 1.0
"""

import json
from typing import List, Dict, Optional, Any
from pathlib import Path


class DhammaThemeService:
    """Service for managing Dhamma themes"""
    
    def __init__(self):
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._themes_by_category: Dict[str, List[str]] = {}
        self._theme_categories_map: Dict[str, List[str]] = {}  # theme_id -> [categories]
        self._loaded = False
        
    def _get_themes_file_path(self) -> Path:
        """Get absolute path to dhamma_themes.json"""
        # Navigate from dmm_backend/services/ to definitions/
        current_dir = Path(__file__).parent
        backend_dir = current_dir.parent
        project_root = backend_dir.parent
        themes_path = project_root / "definitions" / "dhamma_themes.json"
        return themes_path
    
    def load_themes(self) -> None:
        """Load themes from JSON file and build indices"""
        if self._loaded:
            return
            
        themes_path = self._get_themes_file_path()
        
        if not themes_path.exists():
            raise FileNotFoundError(f"Dhamma themes file not found: {themes_path}")
        
        with open(themes_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        dhamma_themes_root = data.get('dhamma_themes', {})
        
        # Load theme_categories first to build multi-category mapping
        theme_categories = dhamma_themes_root.get('theme_categories', {})
        for category_name, theme_ids in theme_categories.items():
            for theme_id in theme_ids:
                # Track which categories each theme belongs to
                if theme_id not in self._theme_categories_map:
                    self._theme_categories_map[theme_id] = []
                self._theme_categories_map[theme_id].append(category_name)
        
        # Load individual themes (from the themes array)
        themes_array = dhamma_themes_root.get('themes', [])
        for theme_data in themes_array:
            if isinstance(theme_data, dict):
                theme_id = theme_data.get('id')
                if not theme_id:
                    continue
                    
                # Add categories information to theme
                theme_data['categories'] = self._theme_categories_map.get(theme_id, [])
                
                self._themes[theme_id] = theme_data
                
                # Index by primary category (first one in the list)
                category = theme_data.get('category', 'อื่นๆ')
                if category not in self._themes_by_category:
                    self._themes_by_category[category] = []
                self._themes_by_category[category].append(theme_id)
        
        self._loaded = True
        
        # Report loading stats
        multi_category_count = sum(1 for cats in self._theme_categories_map.values() if len(cats) > 1)
        print(f"✅ Loaded {len(self._themes)} Dhamma themes")
        print(f"   📚 {multi_category_count} themes belong to multiple categories (ธรรมะที่ใช้ได้หลายทาง)")
    
    def get_theme(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """Get theme by ID with category relationships"""
        if not self._loaded:
            self.load_themes()
        theme = self._themes.get(theme_id)
        if theme:
            # Ensure categories list is included
            theme['categories'] = self._theme_categories_map.get(theme_id, [])
        return theme
    
    def get_theme_categories(self, theme_id: str) -> List[str]:
        """Get all categories a theme belongs to"""
        if not self._loaded:
            self.load_themes()
        return self._theme_categories_map.get(theme_id, [])
    
    def is_multi_category_theme(self, theme_id: str) -> bool:
        """Check if theme belongs to multiple categories"""
        categories = self.get_theme_categories(theme_id)
        return len(categories) > 1
    
    def get_all_themes(self) -> List[Dict[str, Any]]:
        """Get all available themes"""
        if not self._loaded:
            self.load_themes()
        return list(self._themes.values())
    
    def search_themes(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        conflict_keyword: Optional[str] = None,
        search_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search themes by various criteria
        
        Args:
            category: Filter by category (e.g., "ปัญญา/สัมมาทิฏฐิ")
            subcategory: Filter by subcategory
            conflict_keyword: Match against applicable_conflicts
            search_text: General text search in description/principles
        
        Returns:
            List of matching themes
        """
        if not self._loaded:
            self.load_themes()
        
        results = list(self._themes.values())
        
        # Filter by category
        if category:
            results = [t for t in results if t.get('category') == category]
        
        # Filter by subcategory
        if subcategory:
            results = [t for t in results if t.get('subcategory') == subcategory]
        
        # Filter by conflict keyword
        if conflict_keyword:
            keyword_lower = conflict_keyword.lower()
            results = [
                t for t in results 
                if any(keyword_lower in c.lower() for c in t.get('applicable_conflicts', []))
            ]
        
        # General text search
        if search_text:
            search_lower = search_text.lower()
            filtered = []
            for theme in results:
                # Search in multiple fields
                searchable_text = (
                    theme.get('thai_name', '') + ' ' +
                    theme.get('description', '') + ' ' +
                    ' '.join(theme.get('core_principles', [])) + ' ' +
                    ' '.join(theme.get('applicable_conflicts', []))
                )
                if search_lower in searchable_text.lower():
                    filtered.append(theme)
            results = filtered
        
        return results
    
    def suggest_themes(
        self,
        big_idea: Optional[str] = None,
        premise: Optional[str] = None,
        tags: Optional[List[str]] = None,
        conflict_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest appropriate themes based on story context
        
        Args:
            big_idea: The story's big idea
            premise: The story's premise question
            tags: Tags from Step 1
            conflict_type: Type of conflict (e.g., "family", "justice")
        
        Returns:
            List of recommended themes, ranked by relevance
        """
        if not self._loaded:
            self.load_themes()
        
        suggestions = []
        
        # Build search keywords from context
        keywords = []
        if big_idea:
            keywords.extend(big_idea.split())
        if premise:
            keywords.extend(premise.split())
        if tags:
            keywords.extend(tags)
        
        # Keyword mapping to theme categories
        keyword_map = {
            'ความจริง': ['THEME_SACCA_TRUTH'],
            'โกหก': ['THEME_SACCA_TRUTH'],
            'สติ': ['THEME_SATI_MINDFULNESS'],
            'ตื่นรู้': ['THEME_SATI_MINDFULNESS'],
            'รัก': ['THEME_METTA_COMPASSION'],
            'เมตตา': ['THEME_METTA_COMPASSION'],
            'โกรธ': ['THEME_METTA_COMPASSION', 'THEME_KHANTI_PATIENCE'],
            'ปัญญา': ['THEME_PANNA_WISDOM'],
            'ปล่อยวาง': ['THEME_PANNA_WISDOM', 'THEME_UPEKKHA_EQUANIMITY'],
            'อดทน': ['THEME_KHANTI_PATIENCE'],
            'กรุณา': ['THEME_KARUNA_COMPASSION'],
            'ช่วยเหลือ': ['THEME_KARUNA_COMPASSION'],
            'ทุกข์': ['THEME_KARUNA_COMPASSION'],
            'ยินดี': ['THEME_MUDITA_JOY'],
            'ริษยา': ['THEME_MUDITA_JOY'],
            'อิจฉา': ['THEME_MUDITA_JOY'],
            'อุเบกขา': ['THEME_UPEKKHA_EQUANIMITY'],
            'วางเฉย': ['THEME_UPEKKHA_EQUANIMITY'],
            'ทาน': ['THEME_DANA_GENEROSITY'],
            'ให้': ['THEME_DANA_GENEROSITY'],
            'แบ่งปัน': ['THEME_DANA_GENEROSITY'],
            'เพียร': ['THEME_VIRIYA_EFFORT'],
            'มานะ': ['THEME_VIRIYA_EFFORT'],
            'ความพยายาม': ['THEME_VIRIYA_EFFORT']
        }
        
        # Score themes based on keyword matches
        theme_scores = {}
        for keyword in keywords:
            for key, theme_ids in keyword_map.items():
                if key in keyword:
                    for theme_id in theme_ids:
                        theme_scores[theme_id] = theme_scores.get(theme_id, 0) + 1
        
        # Sort by score
        sorted_theme_ids = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top themes
        for theme_id, _ in sorted_theme_ids[:3]:
            theme = self.get_theme(theme_id)
            if theme:
                suggestions.append(theme)
        
        # If no matches, return general popular themes
        if not suggestions:
            suggestions = [
                self.get_theme('THEME_SACCA_TRUTH'),
                self.get_theme('THEME_METTA_COMPASSION'),
                self.get_theme('THEME_PANNA_WISDOM')
            ]
            suggestions = [t for t in suggestions if t is not None]
        
        return suggestions
    
    def validate_theme_text(
        self,
        theme_id: str,
        text: str,
        section: str = "general"
    ) -> Dict[str, Any]:
        """
        Validate if text adheres to theme's dhamma principles
        
        Args:
            theme_id: ID of the theme to validate against
            text: Text to validate (e.g., beat content)
            section: Which section (e.g., "beat_2", "beat_7", "beat_13")
        
        Returns:
            Validation result with pass/fail and feedback
        """
        theme = self.get_theme(theme_id)
        if not theme:
            return {
                "valid": False,
                "error": f"Theme ID '{theme_id}' not found"
            }
        
        validation_rules = theme.get('validation_rules', {})
        text_lower = text.lower()
        
        # Check required keywords
        required_keywords = validation_rules.get('must_include_keywords', [])
        found_keywords = [kw for kw in required_keywords if kw in text_lower]
        
        # Check forbidden patterns
        forbidden_patterns = validation_rules.get('forbidden_patterns', [])
        found_forbidden = [pat for pat in forbidden_patterns if pat in text_lower]
        
        # Determine if valid
        has_required = len(found_keywords) > 0
        has_forbidden = len(found_forbidden) > 0
        
        is_valid = has_required and not has_forbidden
        
        # Build feedback
        feedback = []
        if not has_required:
            feedback.append(f"❌ ไม่พบคำสำคัญที่เกี่ยวกับ '{theme['thai_name']}' เช่น: {', '.join(required_keywords[:3])}")
        else:
            feedback.append(f"✅ พบคำสำคัญ: {', '.join(found_keywords[:3])}")
        
        if has_forbidden:
            feedback.append(f"⚠️ พบคำต้องห้ามตามหลักธรรม: {', '.join(found_forbidden)}")
        
        # Check critical beats
        critical_beats = validation_rules.get('min_mentions', {}).get('beats', [])
        if section.startswith('beat_'):
            beat_num = int(section.split('_')[1])
            if beat_num in critical_beats and not has_required:
                feedback.append(f"🔴 Beat {beat_num} เป็น critical beat ต้องกล่าวถึงหลักธรรมชัดเจน!")
        
        return {
            "valid": is_valid,
            "theme_id": theme_id,
            "theme_name": theme['thai_name'],
            "section": section,
            "found_keywords": found_keywords,
            "found_forbidden": found_forbidden,
            "feedback": feedback,
            "suggestion": self._get_suggestion(theme, has_required, has_forbidden)
        }
    
    def _get_suggestion(
        self,
        theme: Dict[str, Any],
        has_required: bool,
        has_forbidden: bool
    ) -> str:
        """Generate improvement suggestion"""
        if has_forbidden:
            return f"ลบข้อความที่ขัดหลักธรรม แล้วเน้นหลักการ: {theme['core_principles'][0]}"
        elif not has_required:
            return f"เพิ่มเนื้อหาเกี่ยวกับ '{theme['thai_name']}' เช่น: {theme['core_principles'][0]}"
        else:
            return "ดีมาก! สอดคล้องกับหลักธรรม"
    
    def validate_structure(
        self,
        theme_id: str,
        structure: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate entire 15-beat structure against theme
        
        Args:
            theme_id: Theme ID
            structure: List of 15 beats with id, name, content
        
        Returns:
            Overall validation result with beat-by-beat feedback
        """
        theme = self.get_theme(theme_id)
        if not theme:
            return {
                "valid": False,
                "error": f"Theme ID '{theme_id}' not found"
            }
        
        beat_results = []
        critical_beats_passed = 0
        critical_beats_total = 0
        
        for beat in structure:
            beat_id = beat.get('id', 0)
            beat_name = beat.get('name', '')
            beat_content = beat.get('content', '')
            
            # Check if this is a critical beat
            validation_rules = theme.get('validation_rules', {})
            critical_beats = validation_rules.get('min_mentions', {}).get('beats', [])
            is_critical = beat_id in critical_beats
            
            if is_critical:
                critical_beats_total += 1
            
            # Validate beat content
            section = f"beat_{beat_id}"
            result = self.validate_theme_text(theme_id, beat_content, section)
            result['beat_id'] = beat_id
            result['beat_name'] = beat_name
            result['is_critical'] = is_critical
            
            if is_critical and result['valid']:
                critical_beats_passed += 1
            
            beat_results.append(result)
        
        # Overall validation
        overall_valid = critical_beats_passed == critical_beats_total
        
        return {
            "valid": overall_valid,
            "theme_id": theme_id,
            "theme_name": theme['thai_name'],
            "critical_beats_passed": critical_beats_passed,
            "critical_beats_total": critical_beats_total,
            "beat_results": beat_results,
            "summary": self._generate_summary(beat_results, overall_valid)
        }
    
    def _generate_summary(
        self,
        beat_results: List[Dict[str, Any]],
        overall_valid: bool
    ) -> str:
        """Generate human-readable summary"""
        total_beats = len(beat_results)
        valid_beats = sum(1 for r in beat_results if r['valid'])
        
        if overall_valid:
            return f"✅ ผ่าน! {valid_beats}/{total_beats} beats สอดคล้องหลักธรรม และ critical beats ทั้งหมดผ่าน"
        else:
            critical_failed = [r for r in beat_results if r['is_critical'] and not r['valid']]
            failed_nums = [r['beat_id'] for r in critical_failed]
            return f"❌ ไม่ผ่าน! Critical beats {failed_nums} ยังไม่กล่าวถึงหลักธรรมชัดเจน กรุณาแก้ไข"


# Singleton instance
_service_instance: Optional[DhammaThemeService] = None


def get_dhamma_theme_service() -> DhammaThemeService:
    """Get singleton instance of DhammaThemeService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = DhammaThemeService()
        _service_instance.load_themes()
    return _service_instance
