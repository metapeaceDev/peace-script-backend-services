"""
User Manager for handling user operations
Implements FastAPI-Users UserManager with custom logic
"""

import os
from typing import Optional
from beanie import PydanticObjectId
from fastapi import Depends, Request
from fastapi_users import BaseUserManager
from fastapi_users_db_beanie import BeanieUserDatabase, ObjectIDIDMixin

from .models import User


# Secret key for JWT (should be in environment variable in production)
SECRET = os.getenv("SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION_TO_SECURE_RANDOM_STRING")


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    """
    Custom User Manager with Buddhist practice integration
    """
    
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Called after successful user registration
        Creates initial MindState for new user
        """
        print(f"✅ User {user.email} registered (ID: {user.id})")
        
        # Auto-create MindState for new user
        try:
            from documents import MindState
            
            # Create initial MindState with default values
            mind_state = MindState(user_id=str(user.id))
            await mind_state.insert()
            
            # Link MindState to User
            user.mind_state_id = str(mind_state.id)
            await user.save()
            
            print(f"✅ MindState created and linked for {user.email} (MindState ID: {mind_state.id})")
        except Exception as e:
            print(f"❌ Failed to create MindState for {user.email}: {e}")
        
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called when user requests password reset"""
        print(f"🔑 User {user.email} forgot password. Reset token: {token}")
        
    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called when user requests email verification"""
        print(f"📧 Verification requested for {user.email}. Token: {token}")


async def get_user_db():
    """Dependency to get User database"""
    yield BeanieUserDatabase(User)


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    """Dependency to get User Manager"""
    yield UserManager(user_db)
