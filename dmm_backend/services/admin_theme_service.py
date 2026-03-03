"""
Admin Theme Service - Theme Management & CRUD Operations
========================================================

Service layer for administrative management of Dhamma themes.

This service provides:
- Create, Read, Update, Delete operations for themes
- Theme validation and schema checking
- Duplicate detection
- Theme templating (duplicate with modifications)
- Bulk operations support

Author: Peace Script Team
Date: 19 November 2025 (2568 BE)
Version: 1.0
"""

import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
import uuid


@dataclass
class AuditLog:
    """Audit log entry for admin operations"""
    id: str
    timestamp: datetime
    user_id: str
    action: str  # CREATE, UPDATE, DELETE, IMPORT, EXPORT
    resource_type: str
    resource_id: str
    changes: Dict[str, Any]
    status: str  # SUCCESS, FAILED
    error_message: Optional[str] = None


class AdminThemeService:
    """Service for administrative theme management"""
    
    def __init__(self):
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._audit_logs: List[AuditLog] = []
        self._loaded = False
        
    def _get_themes_file_path(self) -> Path:
        """Get path to themes JSON file"""
        current_dir = Path(__file__).parent
        backend_dir = current_dir.parent
        project_root = backend_dir.parent
        return project_root / "definitions" / "dhamma_themes.json"
    
    def load_themes(self) -> None:
        """Load themes from file"""
        if self._loaded:
            return
        
        themes_path = self._get_themes_file_path()
        
        if not themes_path.exists():
            raise FileNotFoundError(f"Themes file not found: {themes_path}")
        
        with open(themes_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        themes_list = data.get('dhamma_themes', {}).get('themes', [])
        
        for theme in themes_list:
            self._themes[theme['id']] = theme
        
        self._loaded = True
        print(f"✅ Admin service loaded {len(self._themes)} themes")
    
    def create_theme(
        self,
        theme_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Create a new theme
        
        Args:
            theme_data: Theme data with all required fields
            user_id: User ID performing the action
            
        Returns:
            Created theme object
            
        Raises:
            ValueError: If theme data is invalid
        """
        if not self._loaded:
            self.load_themes()
        
        # Validate theme data
        errors = self._validate_theme(theme_data)
        if errors:
            self._log_action(
                user_id=user_id,
                action='CREATE',
                resource_id=theme_data.get('id', 'unknown'),
                changes=theme_data,
                status='FAILED',
                error_message=f"Validation errors: {', '.join(errors)}"
            )
            raise ValueError(f"Invalid theme data: {errors}")
        
        # Check if theme ID already exists
        theme_id = theme_data['id']
        if theme_id in self._themes:
            error = f"Theme with ID '{theme_id}' already exists"
            self._log_action(
                user_id=user_id,
                action='CREATE',
                resource_id=theme_id,
                changes=theme_data,
                status='FAILED',
                error_message=error
            )
            raise ValueError(error)
        
        # Add metadata
        theme = {
            **theme_data,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'created_by': user_id,
            'updated_by': user_id,
            'version': 1,
            'is_archived': False
        }
        
        # Store theme
        self._themes[theme_id] = theme
        
        # Log action
        self._log_action(
            user_id=user_id,
            action='CREATE',
            resource_id=theme_id,
            changes=theme,
            status='SUCCESS'
        )
        
        return theme
    
    def get_theme(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """Get theme by ID"""
        if not self._loaded:
            self.load_themes()
        return self._themes.get(theme_id)
    
    def update_theme(
        self,
        theme_id: str,
        updates: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Update existing theme
        
        Args:
            theme_id: ID of theme to update
            updates: Fields to update
            user_id: User ID performing the action
            
        Returns:
            Updated theme object
            
        Raises:
            ValueError: If theme not found or update invalid
        """
        if not self._loaded:
            self.load_themes()
        
        if theme_id not in self._themes:
            error = f"Theme '{theme_id}' not found"
            self._log_action(
                user_id=user_id,
                action='UPDATE',
                resource_id=theme_id,
                changes=updates,
                status='FAILED',
                error_message=error
            )
            raise ValueError(error)
        
        theme = self._themes[theme_id]
        
        # Don't allow changing ID or created_by
        if 'id' in updates:
            raise ValueError("Cannot change theme ID")
        if 'created_by' in updates or 'created_at' in updates:
            raise ValueError("Cannot change creation metadata")
        
        # Validate updates
        updated_theme = {**theme, **updates}
        errors = self._validate_theme(updated_theme)
        if errors:
            self._log_action(
                user_id=user_id,
                action='UPDATE',
                resource_id=theme_id,
                changes=updates,
                status='FAILED',
                error_message=f"Validation errors: {', '.join(errors)}"
            )
            raise ValueError(f"Invalid update: {errors}")
        
        # Track changes for audit
        changes = {k: v for k, v in updates.items() if theme.get(k) != v}
        
        # Update theme
        theme.update(updates)
        theme['updated_at'] = datetime.now().isoformat()
        theme['updated_by'] = user_id
        theme['version'] = theme.get('version', 1) + 1
        
        # Log action
        self._log_action(
            user_id=user_id,
            action='UPDATE',
            resource_id=theme_id,
            changes=changes,
            status='SUCCESS'
        )
        
        return theme
    
    def delete_theme(
        self,
        theme_id: str,
        user_id: str,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete theme (soft or hard delete)
        
        Args:
            theme_id: ID of theme to delete
            user_id: User ID performing the action
            soft_delete: If True, mark as archived; if False, hard delete
            
        Returns:
            True if deleted, False if not found
        """
        if not self._loaded:
            self.load_themes()
        
        if theme_id not in self._themes:
            self._log_action(
                user_id=user_id,
                action='DELETE',
                resource_id=theme_id,
                changes={},
                status='FAILED',
                error_message='Theme not found'
            )
            return False
        
        if soft_delete:
            # Soft delete: mark as archived
            self._themes[theme_id]['is_archived'] = True
            self._themes[theme_id]['deleted_at'] = datetime.now().isoformat()
            self._themes[theme_id]['deleted_by'] = user_id
        else:
            # Hard delete
            del self._themes[theme_id]
        
        self._log_action(
            user_id=user_id,
            action='DELETE',
            resource_id=theme_id,
            changes={'is_archived': soft_delete},
            status='SUCCESS'
        )
        
        return True
    
    def duplicate_theme(
        self,
        source_theme_id: str,
        new_theme_id: str,
        modifications: Optional[Dict[str, Any]] = None,
        user_id: str = 'system'
    ) -> Dict[str, Any]:
        """
        Create a copy of theme with modifications
        
        Args:
            source_theme_id: ID of theme to duplicate
            new_theme_id: ID for new theme
            modifications: Fields to modify in copy
            user_id: User ID performing the action
            
        Returns:
            New theme object
        """
        if not self._loaded:
            self.load_themes()
        
        source = self.get_theme(source_theme_id)
        if not source:
            raise ValueError(f"Source theme '{source_theme_id}' not found")
        
        # Create copy
        new_theme = {
            **source,
            'id': new_theme_id,
            **(modifications or {})
        }
        
        # Remove metadata from copy
        for key in ['created_at', 'updated_at', 'created_by', 'updated_by', 
                   'version', 'deleted_at', 'deleted_by']:
            new_theme.pop(key, None)
        
        # Create as new theme
        return self.create_theme(new_theme, user_id)
    
    def get_all_themes(self, include_archived: bool = False) -> List[Dict[str, Any]]:
        """Get all themes"""
        if not self._loaded:
            self.load_themes()
        
        themes = list(self._themes.values())
        
        if not include_archived:
            themes = [t for t in themes if not t.get('is_archived', False)]
        
        return themes
    
    def search_themes(
        self,
        query: str,
        category: Optional[str] = None,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """Search themes by text and optionally filter by category"""
        if not self._loaded:
            self.load_themes()
        
        results = []
        query_lower = query.lower()
        
        for theme in self._themes.values():
            # Skip archived if not requested
            if not include_archived and theme.get('is_archived', False):
                continue
            
            # Check if query matches
            if (query_lower in theme.get('id', '').lower() or
                query_lower in theme.get('thai_name', '').lower() or
                query_lower in theme.get('pali_name', '').lower() or
                query_lower in theme.get('description', '').lower()):
                
                # Check category filter if provided
                if category and theme.get('category') != category:
                    continue
                
                results.append(theme)
        
        return results
    
    def _validate_theme(self, theme: Dict[str, Any]) -> List[str]:
        """Validate theme structure and content"""
        errors = []
        
        # Required fields
        required_fields = ['id', 'thai_name', 'pali_name', 'category', 'description']
        for field in required_fields:
            if field not in theme or not theme[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate story_guidelines
        if 'story_guidelines' in theme:
            sg = theme['story_guidelines']
            sg_fields = ['theme_stated', 'b_story', 'break_into_three', 'finale']
            for field in sg_fields:
                if field not in sg or not sg[field]:
                    errors.append(f"Missing story_guidelines field: {field}")
        else:
            errors.append("Missing required field: story_guidelines")
        
        # Validate arrays
        if 'recommended_sub_themes' in theme:
            if not isinstance(theme['recommended_sub_themes'], list):
                errors.append("recommended_sub_themes must be an array")
        
        # Validate ID format (alphanumeric + underscores)
        theme_id = theme.get('id', '')
        if not theme_id or not theme_id.replace('_', '').replace('-', '').isalnum():
            errors.append("Invalid theme ID format")
        
        return errors
    
    def _log_action(
        self,
        user_id: str,
        action: str,
        resource_id: str,
        changes: Dict[str, Any],
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """Log an admin action"""
        log_entry = AuditLog(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            resource_type='theme',
            resource_id=resource_id,
            changes=changes,
            status=status,
            error_message=error_message
        )
        self._audit_logs.append(log_entry)
    
    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering"""
        logs = self._audit_logs
        
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        
        if action:
            logs = [l for l in logs if l.action == action]
        
        # Return most recent first
        logs = sorted(logs, key=lambda l: l.timestamp, reverse=True)
        
        return [asdict(l) for l in logs[:limit]]
    
    def save_to_file(self) -> None:
        """Save themes back to JSON file"""
        themes_path = self._get_themes_file_path()
        
        # Get active themes (exclude archived)
        active_themes = [
            t for t in self._themes.values()
            if not t.get('is_archived', False)
        ]
        
        # Prepare data structure
        data = {
            'dhamma_themes': {
                'version': '2.0',
                'total_themes': len(active_themes),
                'themes': active_themes
            }
        }
        
        # Write to file
        with open(themes_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(active_themes)} themes to file")


# Singleton instance
_service_instance: Optional[AdminThemeService] = None


def get_admin_theme_service() -> AdminThemeService:
    """Get singleton instance of AdminThemeService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = AdminThemeService()
        _service_instance.load_themes()
    return _service_instance
