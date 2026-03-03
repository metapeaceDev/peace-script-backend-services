"""
Data Quality Service - Theme Data Validation & Quality Checking
==============================================================

Service layer for data quality monitoring and validation.

This service provides:
- Complete theme validation
- Relationship validation
- Duplicate detection
- Completeness checking
- Data quality scoring
- Issue reporting and recommendations

Author: Peace Script Team
Date: 19 November 2025 (2568 BE)
Version: 1.0
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import Counter


@dataclass
class ValidationError:
    """Validation error details"""
    theme_id: str
    error_type: str
    message: str
    field: Optional[str] = None
    severity: str = 'warning'  # info, warning, error


@dataclass
class ValidationReport:
    """Report of validation results"""
    total_themes: int
    themes_with_errors: int
    errors: List[ValidationError]
    warnings: List[ValidationError]
    quality_score: float
    timestamp: str


class DataQualityService:
    """Service for data quality validation and monitoring"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def validate_all_themes(
        self,
        themes: Dict[str, Dict[str, Any]]
    ) -> ValidationReport:
        """
        Validate all themes comprehensively
        
        Args:
            themes: Dictionary of theme_id -> theme_data
            
        Returns:
            ValidationReport with all issues found
        """
        self.errors = []
        self.warnings = []
        
        from datetime import datetime
        
        # Validate each theme
        for theme_id, theme in themes.items():
            self._validate_single_theme(theme_id, theme)
        
        # Validate relationships
        self._validate_relationships(themes)
        
        # Check for duplicates
        self._check_duplicates(themes)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(len(themes))
        
        report = ValidationReport(
            total_themes=len(themes),
            themes_with_errors=len(set(e.theme_id for e in self.errors)),
            errors=self.errors,
            warnings=self.warnings,
            quality_score=quality_score,
            timestamp=datetime.now().isoformat()
        )
        
        return report
    
    def _validate_single_theme(
        self,
        theme_id: str,
        theme: Dict[str, Any]
    ) -> List[ValidationError]:
        """Validate a single theme and return list of errors"""
        local_errors = []
        
        # Check required fields
        required_fields = {
            'id': 'string',
            'thai_name': 'string',
            'pali_name': 'string',
            'category': 'string',
            'description': 'string',
            'story_guidelines': 'dict'
        }
        
        for field, _field_type in required_fields.items():
            if field not in theme:
                error = ValidationError(
                    theme_id=theme_id,
                    error_type='missing_field',
                    message=f"Missing required field: {field}",
                    field=field,
                    severity='error'
                )
                self.errors.append(error)
                local_errors.append(error)
            elif not theme[field]:
                error = ValidationError(
                    theme_id=theme_id,
                    error_type='empty_field',
                    message=f"Field is empty: {field}",
                    field=field,
                    severity='error'
                )
                self.errors.append(error)
                local_errors.append(error)
        
        # Validate story_guidelines
        if 'story_guidelines' in theme and isinstance(theme['story_guidelines'], dict):
            sg_fields = ['theme_stated', 'b_story', 'break_into_three', 'finale']
            for field in sg_fields:
                if field not in theme['story_guidelines']:
                    error = ValidationError(
                        theme_id=theme_id,
                        error_type='missing_story_guideline',
                        message=f"Missing story_guidelines field: {field}",
                        field=f"story_guidelines.{field}",
                        severity='error'
                    )
                    self.errors.append(error)
                    local_errors.append(error)
                elif not theme['story_guidelines'][field]:
                    warning = ValidationError(
                        theme_id=theme_id,
                        error_type='empty_story_guideline',
                        message=f"Story guideline is empty: {field}",
                        field=f"story_guidelines.{field}",
                        severity='warning'
                    )
                    self.warnings.append(warning)
                    local_errors.append(warning)
        
        # Validate arrays
        if 'recommended_sub_themes' in theme:
            if not isinstance(theme['recommended_sub_themes'], list):
                error = ValidationError(
                    theme_id=theme_id,
                    error_type='invalid_type',
                    message="recommended_sub_themes must be an array",
                    field='recommended_sub_themes',
                    severity='error'
                )
                self.errors.append(error)
                local_errors.append(error)
            elif len(theme['recommended_sub_themes']) == 0:
                warning = ValidationError(
                    theme_id=theme_id,
                    error_type='missing_sub_themes',
                    message="No recommended sub-themes",
                    field='recommended_sub_themes',
                    severity='warning'
                )
                self.warnings.append(warning)
                local_errors.append(warning)
        
        return local_errors
    
    def _validate_relationships(
        self,
        themes: Dict[str, Dict[str, Any]]
    ) -> None:
        """Validate relationships between themes"""
        
        theme_ids = set(themes.keys())
        
        for theme_id, theme in themes.items():
            sub_themes = theme.get('recommended_sub_themes', [])
            
            for sub_theme_id in sub_themes:
                # Check if sub-theme exists
                if sub_theme_id not in theme_ids:
                    self.warnings.append(ValidationError(
                        theme_id=theme_id,
                        error_type='missing_sub_theme',
                        message=f"Recommended sub-theme not found: {sub_theme_id}",
                        field='recommended_sub_themes',
                        severity='warning'
                    ))
    
    def _check_duplicates(self, themes: Dict[str, Dict[str, Any]]) -> None:
        """Check for duplicate themes"""
        
        # Check for duplicate IDs (should not happen if properly maintained)
        theme_ids = list(themes.keys())
        id_counts = Counter(theme_ids)
        
        for theme_id, count in id_counts.items():
            if count > 1:
                self.errors.append(ValidationError(
                    theme_id=theme_id,
                    error_type='duplicate_id',
                    message=f"Duplicate theme ID found",
                    field='id',
                    severity='error'
                ))
        
        # Check for duplicate names
        thai_names = {}
        pali_names = {}
        
        for theme_id, theme in themes.items():
            thai_name = theme.get('thai_name', '')
            pali_name = theme.get('pali_name', '')
            
            if thai_name in thai_names:
                self.warnings.append(ValidationError(
                    theme_id=theme_id,
                    error_type='duplicate_thai_name',
                    message=f"Duplicate Thai name: {thai_names[thai_name]} and {theme_id}",
                    field='thai_name',
                    severity='warning'
                ))
            else:
                thai_names[thai_name] = theme_id
            
            if pali_name in pali_names:
                self.warnings.append(ValidationError(
                    theme_id=theme_id,
                    error_type='duplicate_pali_name',
                    message=f"Duplicate Pali name: {pali_names[pali_name]} and {theme_id}",
                    field='pali_name',
                    severity='warning'
                ))
            else:
                pali_names[pali_name] = theme_id
    
    def _calculate_quality_score(self, total_themes: int) -> float:
        """Calculate overall data quality score (0-100)"""
        
        if total_themes == 0:
            return 0.0
        
        # Penalties
        error_penalty = len(self.errors) * 10  # 10 points per error
        warning_penalty = len(self.warnings) * 2  # 2 points per warning
        
        score = 100 - error_penalty - warning_penalty
        
        # Clamp between 0 and 100
        return max(0, min(100, score))
    
    def check_completeness(
        self,
        themes: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check completeness of themes"""
        
        if not themes:
            return {
                'total_themes': 0,
                'complete_themes': 0,
                'incomplete_themes': 0,
                'completeness_percentage': 0.0,
                'missing_fields_summary': {}
            }
        
        missing_fields = Counter()
        complete_count = 0
        
        for theme in themes.values():
            required_fields = [
                'id', 'thai_name', 'pali_name', 'category',
                'description', 'story_guidelines', 'recommended_sub_themes'
            ]
            
            is_complete = True
            for field in required_fields:
                if field not in theme or not theme[field]:
                    missing_fields[field] += 1
                    is_complete = False
            
            if is_complete:
                complete_count += 1
        
        completeness_percentage = (complete_count / len(themes)) * 100
        
        return {
            'total_themes': len(themes),
            'complete_themes': complete_count,
            'incomplete_themes': len(themes) - complete_count,
            'completeness_percentage': round(completeness_percentage, 2),
            'missing_fields_summary': dict(missing_fields)
        }
    
    def get_quality_issues(
        self,
        themes: Dict[str, Dict[str, Any]],
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of quality issues with recommendations
        
        Args:
            themes: Dictionary of themes
            severity: Filter by severity (info, warning, error) or None for all
            
        Returns:
            List of issues with recommendations
        """
        
        report = self.validate_all_themes(themes)
        
        issues = []
        
        # Combine errors and warnings
        all_issues = report.errors + report.warnings
        
        if severity:
            all_issues = [i for i in all_issues if i.severity == severity]
        
        for issue in all_issues:
            recommendation = self._get_recommendation(issue)
            
            issues.append({
                'theme_id': issue.theme_id,
                'error_type': issue.error_type,
                'message': issue.message,
                'field': issue.field,
                'severity': issue.severity,
                'recommendation': recommendation
            })
        
        return issues
    
    def _get_recommendation(self, error: ValidationError) -> str:
        """Get recommendation for fixing an issue"""
        
        recommendations = {
            'missing_field': f"Add missing field: {error.field}",
            'empty_field': f"Populate field: {error.field}",
            'missing_story_guideline': f"Add story guideline: {error.field}",
            'empty_story_guideline': f"Write content for: {error.field}",
            'missing_sub_themes': "Add related sub-themes recommendations",
            'invalid_id_format': "Use alphanumeric ID with underscores (e.g., THEME_EXAMPLE)",
            'missing_sub_theme': f"Add missing referenced theme or remove the reference",
            'duplicate_id': "Merge or rename duplicate theme",
            'duplicate_thai_name': "Ensure each theme has unique Thai name",
            'duplicate_pali_name': "Ensure each theme has unique Pali name",
            'encoding_error': "Ensure text is properly UTF-8 encoded",
            'invalid_type': f"Ensure {error.field} is correct type"
        }
        
        return recommendations.get(error.error_type, "Review and fix this issue")


# Singleton instance
_service_instance: Optional[DataQualityService] = None


def get_data_quality_service() -> DataQualityService:
    """Get singleton instance of DataQualityService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = DataQualityService()
    return _service_instance
