"""
Dependencies package
"""

from .auth import (
    get_current_user,
    get_current_active_user,
    get_optional_user,
    require_roles,
    require_verified_email,
    get_admin_user,
    get_verified_user
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "require_roles",
    "require_verified_email",
    "get_admin_user",
    "get_verified_user"
]
