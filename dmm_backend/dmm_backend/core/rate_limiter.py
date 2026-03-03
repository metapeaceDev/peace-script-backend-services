"""
Rate Limiting Middleware for Authentication Endpoints
Provides custom rate limiters for login, register, and other auth operations
"""

from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from functools import wraps
import time
from typing import Dict, Callable
import logging

logger = logging.getLogger(__name__)

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# In-memory rate limit storage (for development)
# In production, use Redis or similar
rate_limit_store: Dict[str, list] = {}


def custom_rate_limit(max_attempts: int, window_seconds: int, endpoint_name: str):
    """
    Custom rate limiter decorator
    
    Args:
        max_attempts: Maximum number of attempts allowed
        window_seconds: Time window in seconds
        endpoint_name: Name of the endpoint for logging
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get client identifier (IP address)
            client_id = get_remote_address(request)
            key = f"{endpoint_name}:{client_id}"
            
            current_time = time.time()
            
            # Initialize or get existing attempts
            if key not in rate_limit_store:
                rate_limit_store[key] = []
            
            # Clean old attempts outside window
            rate_limit_store[key] = [
                timestamp for timestamp in rate_limit_store[key]
                if current_time - timestamp < window_seconds
            ]
            
            # Check if limit exceeded
            if len(rate_limit_store[key]) >= max_attempts:
                oldest_attempt = min(rate_limit_store[key])
                retry_after = int(window_seconds - (current_time - oldest_attempt))
                
                logger.warning(
                    f"Rate limit exceeded for {endpoint_name} from {client_id}. "
                    f"Attempts: {len(rate_limit_store[key])}/{max_attempts}"
                )
                
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": f"Too many {endpoint_name} attempts. Please try again later.",
                        "retry_after": retry_after,
                        "max_attempts": max_attempts,
                        "window_seconds": window_seconds
                    },
                    headers={"Retry-After": str(retry_after)}
                )
            
            # Record this attempt
            rate_limit_store[key].append(current_time)
            
            # Add rate limit headers to response
            remaining = max_attempts - len(rate_limit_store[key])
            
            try:
                result = await func(request, *args, **kwargs)
                
                # Add custom headers if result is a Response object
                if hasattr(result, 'headers'):
                    result.headers['X-RateLimit-Limit'] = str(max_attempts)
                    result.headers['X-RateLimit-Remaining'] = str(remaining)
                    result.headers['X-RateLimit-Reset'] = str(int(current_time + window_seconds))
                
                return result
            except Exception as e:
                # Still count as an attempt even if it fails
                logger.error(f"Error in {endpoint_name}: {e}")
                raise
        
        return wrapper
    return decorator


# Predefined rate limiters for auth endpoints
def rate_limit_login(func: Callable):
    """Rate limiter for login endpoint: 5 attempts per minute"""
    return custom_rate_limit(
        max_attempts=5,
        window_seconds=60,
        endpoint_name="login"
    )(func)


def rate_limit_register(func: Callable):
    """Rate limiter for register endpoint: 3 attempts per hour"""
    return custom_rate_limit(
        max_attempts=3,
        window_seconds=3600,
        endpoint_name="register"
    )(func)


def rate_limit_password_reset(func: Callable):
    """Rate limiter for password reset: 3 attempts per hour"""
    return custom_rate_limit(
        max_attempts=3,
        window_seconds=3600,
        endpoint_name="password_reset"
    )(func)


def rate_limit_verification(func: Callable):
    """Rate limiter for email verification: 5 attempts per hour"""
    return custom_rate_limit(
        max_attempts=5,
        window_seconds=3600,
        endpoint_name="verification"
    )(func)


# Cleanup old entries periodically (optional)
def cleanup_rate_limit_store():
    """Remove old entries from rate limit store"""
    current_time = time.time()
    max_age = 3600  # 1 hour
    
    keys_to_remove = []
    for key, timestamps in rate_limit_store.items():
        # Remove timestamps older than 1 hour
        rate_limit_store[key] = [
            ts for ts in timestamps
            if current_time - ts < max_age
        ]
        # Mark empty keys for removal
        if not rate_limit_store[key]:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del rate_limit_store[key]
    
    logger.info(f"Cleaned up rate limit store. Active keys: {len(rate_limit_store)}")
