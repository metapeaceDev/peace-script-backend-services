"""
Authentication Router
Phase 2: Authentication & User Management

Provides user registration, login, token refresh, and user info endpoints
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from documents import User, MindState
from utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
    validate_password_strength,
    Token
)


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"]
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============================================================================
# Pydantic Models for Requests/Responses
# ============================================================================

class UserRegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: str = Field(..., min_length=2, description="User's full name")


class UserRegisterResponse(BaseModel):
    """User registration response"""
    user_id: str
    email: str
    full_name: str
    message: str


class UserLoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


class UserInfoResponse(BaseModel):
    """Current user information"""
    user_id: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    roles: list[str]
    created_at: datetime
    last_login: Optional[datetime]


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterRequest):
    """
    Register a new user account
    
    - Creates User document with hashed password
    - Automatically creates linked MindState for spiritual progress tracking
    - Returns user information
    
    **Requirements:**
    - Email must be unique
    - Password must be at least 8 characters with uppercase, lowercase, and number
    """
    
    # Validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Check if email already exists
    existing_user = await User.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_pwd = hash_password(request.password)
    
    # Create user document
    user = User(
        email=request.email,
        hashed_password=hashed_pwd,
        full_name=request.full_name,
        is_active=True,
        is_verified=False,
        roles=["user"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save to database
    await user.insert()
    
    # Create linked MindState for spiritual progress tracking
    mind_state = MindState(
        user_id=str(user.id),
        sila=5.0,
        samadhi=4.0,
        panna=4.0,
        sati_strength=5.0,
        current_anusaya={
            "lobha": 3.0,
            "dosa": 2.5,
            "moha": 3.5,
            "mana": 2.0,
            "ditthi": 2.0,
            "vicikiccha": 2.5,
            "thina": 3.0
        },
        kusala_count_today=0,
        akusala_count_today=0,
        kusala_count_total=0,
        akusala_count_total=0,
        current_bhumi="puthujjana",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await mind_state.insert()
    
    return UserRegisterResponse(
        user_id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        message="Registration successful. Please login to continue."
    )


@router.post("/login", response_model=Token)
async def login_user(request: UserLoginRequest):
    """
    Login with email and password
    
    - Verifies credentials
    - Returns JWT access token (15 min expiry) and refresh token (7 days)
    - Updates last login timestamp
    
    **Token Usage:**
    - Include access token in Authorization header: `Bearer <access_token>`
    - Use refresh token to get new access token when expired
    """
    
    # Find user by email
    user = await User.find_one({"email": request.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
    
    # Update last login
    user.update_last_login()
    await user.save()
    
    # Create tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=dict)
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    
    - Validates refresh token
    - Issues new access token
    - Original refresh token remains valid
    
    **Use Case:**
    When access token expires (after 15 min), use this endpoint to get a new one
    without requiring user to login again
    """
    
    # Decode and validate refresh token
    payload = decode_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify it's a refresh token (not access token)
    if not verify_token_type(payload, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected refresh token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user_id from token
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify user still exists and is active
    user = await User.get(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    token_data = {
        "sub": user_id,
        "email": email
    }
    new_access_token = create_access_token(data=token_data)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user information
    
    **Requires:** Valid access token in Authorization header
    
    **Returns:** User profile information
    """
    
    # Decode token
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify it's an access token
    if not verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Get user from database
    user_id = payload.get("sub")
    user = await User.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    return UserInfoResponse(
        user_id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        roles=user.roles,
        created_at=user.created_at,
        last_login=user.last_login
    )


# ============================================================================
# Health Check (Public)
# ============================================================================

@router.get("/health")
async def auth_health_check():
    """
    Authentication service health check (public endpoint)
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "endpoints": {
            "register": "/api/auth/register",
            "login": "/api/auth/login",
            "refresh": "/api/auth/refresh",
            "me": "/api/auth/me"
        }
    }
