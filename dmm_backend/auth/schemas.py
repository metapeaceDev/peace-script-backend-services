"""
Pydantic Schemas for User API
Read, Create, Update models for FastAPI-Users
"""

from typing import Optional
from beanie import PydanticObjectId
from fastapi_users import schemas


class UserRead(schemas.BaseUser[PydanticObjectId]):
    """Schema for reading user data (public fields)"""
    display_name: str
    mind_state_id: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: str
    notification_enabled: bool


class UserCreate(schemas.BaseUserCreate):
    """Schema for user registration"""
    display_name: str = ""
    preferred_language: str = "th"


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user profile"""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = None
    notification_enabled: Optional[bool] = None
