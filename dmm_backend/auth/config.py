"""
Authentication Configuration
JWT Strategy, Auth Backend, and FastAPI-Users setup
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

from beanie import PydanticObjectId
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from .models import User
from .manager import get_user_manager


# JWT Configuration - Load from environment
SECRET = os.getenv("SECRET_KEY")
if not SECRET:
    raise ValueError(
        "SECRET_KEY environment variable is required! "
        "Please set it in .env file or environment. "
        "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )

# Type assertion for SECRET (guaranteed non-None after check above)
SECRET_KEY: str = SECRET

# JWT token lifetime (configurable via environment)
JWT_LIFETIME_SECONDS = int(os.getenv("JWT_EXPIRATION_HOURS", "1")) * 3600
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def get_jwt_strategy() -> JWTStrategy:
    """Create JWT strategy with configured lifetime"""
    return JWTStrategy(
        secret=SECRET_KEY,
        lifetime_seconds=JWT_LIFETIME_SECONDS,
        algorithm=JWT_ALGORITHM
    )


# Bearer transport (Authorization: Bearer <token>)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# Auth backend combining transport + strategy
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, PydanticObjectId](
    get_user_manager,
    [auth_backend],
)

# Dependency to get current active user
current_active_user = fastapi_users.current_user(active=True)

# Dependency to get current active verified user
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)

# Dependency to get current superuser
current_superuser = fastapi_users.current_user(active=True, superuser=True)
