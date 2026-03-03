"""
Authentication Module for Peace Script v1.4
Implements FastAPI-Users with JWT authentication
"""

from .models import User
from .manager import get_user_manager
from .config import auth_backend, current_active_user, fastapi_users

__all__ = [
    "User",
    "get_user_manager",
    "auth_backend",
    "current_active_user",
    "fastapi_users",
]
