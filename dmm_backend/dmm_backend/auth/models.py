"""
User Model for Authentication
Extends FastAPI-Users BeanieBaseUserDocument with custom fields
"""

from typing import Optional
from beanie import PydanticObjectId
from fastapi_users_db_beanie import BeanieBaseUserDocument
from pydantic import Field
from pymongo import IndexModel
from pymongo.collation import Collation


class User(BeanieBaseUserDocument):
    """
    User model with Buddhist practice tracking integration
    
    Fields:
    - id: UUID (from BeanieBaseUser)
    - email: EmailStr (from BeanieBaseUser) 
    - hashed_password: str (from BeanieBaseUser)
    - is_active: bool (from BeanieBaseUser)
    - is_superuser: bool (from BeanieBaseUser)
    - is_verified: bool (from BeanieBaseUser)
    - display_name: Custom display name
    - mind_state_id: Link to MindState document
    """
    
    # Custom fields
    display_name: str = Field(default="", description="User's display name")
    mind_state_id: Optional[str] = Field(
        default=None, 
        description="Reference to user's MindState document"
    )
    
    # Profile fields
    bio: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = None
    
    # Practice preferences
    preferred_language: str = Field(default="th", description="th, en, or pali")
    notification_enabled: bool = Field(default=True)
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "display_name",
        ]
        # Email collation for case-insensitive email queries
        email_collation = Collation(locale="en", strength=2)
