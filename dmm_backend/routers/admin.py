"""
Admin API Router - REST endpoints for theme administration
========================================================

Provides REST API endpoints for:
- Theme CRUD operations
- Bulk import/export
- Analytics and reporting
- Data quality monitoring
- Audit logging

Author: Peace Script Team
Date: 19 November 2025 (2568 BE)
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from services.admin_theme_service import get_admin_theme_service, AdminThemeService
from services.admin_analytics_service import get_admin_analytics_service, AdminAnalyticsService
from services.data_quality_service import get_data_quality_service, DataQualityService

# Pydantic models for request/response validation
class ThemeCreate(BaseModel):
    """Model for creating a new theme"""
    id: str
    thai_name: str
    pali_name: str
    category: str
    description: str
    story_guidelines: Dict[str, str]
    recommended_sub_themes: List[str] = Field(default_factory=list)
    core_principles: List[str] = Field(default_factory=list)
    related_cetasikas: List[str] = Field(default_factory=list)
    related_sila: List[str] = Field(default_factory=list)
    scripture_refs: List[str] = Field(default_factory=list)
    applicable_conflicts: List[str] = Field(default_factory=list)
    example_loglines: List[str] = Field(default_factory=list)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)


class ThemeUpdate(BaseModel):
    """Model for updating a theme"""
    thai_name: Optional[str] = None
    pali_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    story_guidelines: Optional[Dict[str, str]] = None
    recommended_sub_themes: Optional[List[str]] = None
    core_principles: Optional[List[str]] = None
    related_cetasikas: Optional[List[str]] = None
    related_sila: Optional[List[str]] = None
    scripture_refs: Optional[List[str]] = None
    applicable_conflicts: Optional[List[str]] = None
    example_loglines: Optional[List[str]] = None


class ThemeResponse(BaseModel):
    """Model for theme response"""
    id: str
    thai_name: str
    pali_name: str
    category: str
    description: str
    story_guidelines: Dict[str, str]
    recommended_sub_themes: List[str]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None


# Create router
router = APIRouter(prefix="/api/admin", tags=["admin"])


# Theme CRUD Endpoints
@router.post("/themes", response_model=ThemeResponse)
def create_theme(
    theme: ThemeCreate,
    user_id: str = Query("admin", description="User ID performing the action"),
    admin_service: AdminThemeService = Depends(get_admin_theme_service)
) -> Dict[str, Any]:
    """Create a new theme"""
    try:
        theme_data = theme.dict()
        created_theme = admin_service.create_theme(theme_data, user_id)
        return created_theme
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating theme: {str(e)}")


@router.get("/themes/{theme_id}", response_model=ThemeResponse)
def get_theme(
    theme_id: str,
    admin_service: AdminThemeService = Depends(get_admin_theme_service)
) -> Dict[str, Any]:
    """Get a specific theme"""
    theme = admin_service.get_theme(theme_id)
    if not theme:
        raise HTTPException(status_code=404, detail=f"Theme '{theme_id}' not found")
    return theme


@router.put("/themes/{theme_id}", response_model=ThemeResponse)
def update_theme(
    theme_id: str,
    updates: ThemeUpdate,
    user_id: str = Query("admin", description="User ID performing the action"),
    admin_service: AdminThemeService = Depends(get_admin_theme_service)
) -> Dict[str, Any]:
    """Update an existing theme"""
    try:
        update_data = updates.dict(exclude_unset=True)
        updated_theme = admin_service.update_theme(theme_id, update_data, user_id)
        return updated_theme
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating theme: {str(e)}")


@router.delete("/themes/{theme_id}")
def delete_theme(
    theme_id: str,
    soft_delete: bool = Query(True, description="Use soft delete (archive)"),
    user_id: str = Query("admin", description="User ID performing the action"),
    admin_service: AdminThemeService = Depends(get_admin_theme_service)
) -> Dict[str, str]:
    """Delete a theme"""
    success = admin_service.delete_theme(theme_id, user_id, soft_delete)
    if not success:
        raise HTTPException(status_code=404, detail=f"Theme '{theme_id}' not found")
    return {"message": f"Theme '{theme_id}' deleted successfully", "theme_id": theme_id}


@router.post("/themes/{theme_id}/duplicate")
def duplicate_theme(
    theme_id: str,
    new_theme_id: str = Query(..., description="ID for the new theme"),
    user_id: str = Query("admin", description="User ID performing the action"),
    admin_service: AdminThemeService = Depends(get_admin_theme_service)
) -> Dict[str, Any]:
    """Duplicate a theme"""
    try:
        duplicated = admin_service.duplicate_theme(theme_id, new_theme_id, user_id=user_id)
        return duplicated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error duplicating theme: {str(e)}")


# Theme Listing & Search
@router.get("/themes")
def list_themes(
    include_archived: bool = Query(False, description="Include archived themes"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query"),
    admin_service: AdminThemeService = Depends(get_admin_theme_service)
) -> List[Dict[str, Any]]:
    """List themes with optional filtering"""
    try:
        if search:
            return admin_service.search_themes(search, category, include_archived)
        else:
            themes = admin_service.get_all_themes(include_archived)
            if category:
                themes = [t for t in themes if t.get('category') == category]
            return themes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing themes: {str(e)}")


# Analytics Endpoints
@router.get("/analytics/themes")
def get_theme_stats(
    admin_service: AdminThemeService = Depends(get_admin_theme_service),
    analytics_service: AdminAnalyticsService = Depends(get_admin_analytics_service)
) -> Dict[str, Any]:
    """Get theme statistics"""
    try:
        themes = admin_service.get_all_themes(include_archived=False)
        stats = analytics_service.get_theme_stats(themes)
        
        return {
            'total_themes': stats.total_themes,
            'total_categories': stats.total_categories,
            'archived_themes': stats.archived_themes,
            'active_themes': stats.active_themes,
            'creation_trend': stats.creation_trend,
            'most_used_categories': list(stats.most_used_categories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.get("/analytics/usage")
def get_usage_analytics(
    analytics_service: AdminAnalyticsService = Depends(get_admin_analytics_service)
) -> Dict[str, Any]:
    """Get usage analytics"""
    try:
        analytics = analytics_service.get_usage_analytics()
        
        return {
            'total_searches': analytics.total_searches,
            'total_selections': analytics.total_selections,
            'avg_selection_rate': analytics.avg_selection_rate,
            'most_selected': list(analytics.most_selected),
            'least_selected': list(analytics.least_selected),
            'top_search_queries': analytics.search_queries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting usage: {str(e)}")


@router.get("/analytics/categories")
def get_category_distribution(
    admin_service: AdminThemeService = Depends(get_admin_theme_service),
    analytics_service: AdminAnalyticsService = Depends(get_admin_analytics_service)
) -> Dict[str, int]:
    """Get category distribution"""
    try:
        themes = admin_service.get_all_themes(include_archived=False)
        return analytics_service.get_category_distribution(themes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting categories: {str(e)}")


@router.get("/analytics/performance")
def get_performance_metrics(
    admin_service: AdminThemeService = Depends(get_admin_theme_service),
    analytics_service: AdminAnalyticsService = Depends(get_admin_analytics_service)
) -> Dict[str, Any]:
    """Get performance metrics"""
    try:
        themes = admin_service.get_all_themes(include_archived=False)
        return analytics_service.get_performance_metrics(themes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


# Data Quality Endpoints
@router.get("/quality/check")
def check_data_quality(
    admin_service: AdminThemeService = Depends(get_admin_theme_service),
    quality_service: DataQualityService = Depends(get_data_quality_service)
) -> Dict[str, Any]:
    """Run comprehensive data quality check"""
    try:
        themes = admin_service._themes
        report = quality_service.validate_all_themes(themes)
        
        return {
            'timestamp': report.timestamp,
            'total_themes': report.total_themes,
            'themes_with_errors': report.themes_with_errors,
            'error_count': len(report.errors),
            'warning_count': len(report.warnings),
            'quality_score': report.quality_score,
            'errors': [
                {
                    'theme_id': e.theme_id,
                    'error_type': e.error_type,
                    'message': e.message,
                    'field': e.field,
                    'severity': e.severity
                } for e in report.errors
            ][:20]  # Limit to first 20 errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking quality: {str(e)}")


@router.get("/quality/completeness")
def check_completeness(
    admin_service: AdminThemeService = Depends(get_admin_theme_service),
    quality_service: DataQualityService = Depends(get_data_quality_service)
) -> Dict[str, Any]:
    """Check data completeness"""
    try:
        themes = admin_service._themes
        return quality_service.check_completeness(themes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking completeness: {str(e)}")


@router.get("/quality/issues")
def get_quality_issues(
    severity: Optional[str] = Query(None, description="Filter by severity (error, warning, info)"),
    admin_service: AdminThemeService = Depends(get_admin_theme_service),
    quality_service: DataQualityService = Depends(get_data_quality_service)
) -> List[Dict[str, Any]]:
    """Get quality issues with recommendations"""
    try:
        themes = admin_service._themes
        return quality_service.get_quality_issues(themes, severity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting issues: {str(e)}")


# Audit Log Endpoints
@router.get("/audit-log")
def get_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user"),
    action: Optional[str] = Query(None, description="Filter by action"),
    limit: int = Query(100, description="Maximum results"),
    admin_service: AdminThemeService = Depends(get_admin_theme_service)
) -> List[Dict[str, Any]]:
    """Get audit logs"""
    try:
        logs = admin_service.get_audit_logs(user_id, action, limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting audit logs: {str(e)}")


# Health check
@router.get("/health")
def admin_health() -> Dict[str, str]:
    """Admin API health check"""
    return {
        "status": "healthy",
        "service": "admin",
        "version": "1.0"
    }
