"""
Authentication Dependencies
FastAPI dependencies for protecting routes with JWT authentication

Usage:
    @router.get("/protected")
    async def protected_route(current_user: User = Depends(get_current_user)):
        return {"user_id": str(current_user.id)}
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime

from documents import User
from utils.security import decode_token, verify_token_type

# OAuth2 scheme for Bearer tokens
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        User: Authenticated user document
        
    Raises:
        HTTPException 401: If token is invalid or user not found
        HTTPException 403: If user is inactive
    """
    token = credentials.credentials
    
    # Decode and verify token
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token type (must be access token)
    if not verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Please use access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Load user from database
    user = await User.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Update last login timestamp (optional - comment out if too frequent)
    # user.last_login = datetime.utcnow()
    # await user.save()
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user
    (Wrapper for explicit clarity)
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User: Active user
    """
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise
    Useful for endpoints that work both with and without authentication
    
    Args:
        credentials: Optional Bearer token
        
    Returns:
        User or None: User if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        if not payload or not verify_token_type(payload, "access"):
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await User.get(user_id)
        
        if not user or not user.is_active:
            return None
        
        return user
        
    except Exception:
        return None


async def require_roles(
    required_roles: list[str],
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to check if user has required roles
    
    Args:
        required_roles: List of required role names
        current_user: Current authenticated user
        
    Returns:
        User: User if has required roles
        
    Raises:
        HTTPException 403: If user lacks required roles
        
    Usage:
        @router.post("/admin-only")
        async def admin_route(
            user: User = Depends(lambda: require_roles(["admin"]))
        ):
            return {"message": "Admin access granted"}
    """
    user_roles = set(current_user.roles)
    required_roles_set = set(required_roles)
    
    if not required_roles_set.intersection(user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Required roles: {', '.join(required_roles)}",
        )
    
    return current_user


async def require_verified_email(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require verified email
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: User if email is verified
        
    Raises:
        HTTPException 403: If email not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )
    
    return current_user


# Convenience dependency combinations
async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user with admin role"""
    return await require_roles(["admin"], current_user)


async def get_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user with verified email"""
    return await require_verified_email(current_user)
