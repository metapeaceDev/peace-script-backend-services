"""
Rate Limiting Middleware for Authentication Endpoints
Applies to FastAPI-Users endpoints before they are processed
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from core.rate_limiter import rate_limit_store
import time
import logging

logger = logging.getLogger(__name__)


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply rate limiting to authentication endpoints
    """
    
    # Rate limit configurations
    RATE_LIMITS = {
        "/auth/jwt/login": {
            "max_attempts": 5,
            "window_seconds": 60,
            "name": "Login"
        },
        "/auth/register": {
            "max_attempts": 3,
            "window_seconds": 3600,
            "name": "Register"
        },
        "/auth/forgot-password": {
            "max_attempts": 3,
            "window_seconds": 3600,
            "name": "Password Reset"
        },
        "/auth/request-verify-token": {
            "max_attempts": 5,
            "window_seconds": 3600,
            "name": "Verification"
        },
    }
    
    async def dispatch(self, request: Request, call_next):
        """Process request and apply rate limiting if needed"""
        
        # Check if this is an auth endpoint
        path = request.url.path
        rate_config = None
        
        for endpoint, config in self.RATE_LIMITS.items():
            if path.startswith(endpoint):
                rate_config = config
                break
        
        # If not an auth endpoint, pass through
        if not rate_config:
            return await call_next(request)
        
        # Apply rate limiting
        client_id = request.client.host if request.client else "unknown"
        key = f"{path}:{client_id}"
        
        current_time = time.time()
        max_attempts = rate_config["max_attempts"]
        window_seconds = rate_config["window_seconds"]
        endpoint_name = rate_config["name"]
        
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
                f"Path: {path}, Attempts: {len(rate_limit_store[key])}/{max_attempts}"
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    "detail": {
                        "error": "rate_limit_exceeded",
                        "message": f"Too many {endpoint_name.lower()} attempts. Please try again later.",
                        "retry_after": retry_after,
                        "max_attempts": max_attempts,
                        "window_seconds": window_seconds
                    }
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_attempts),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + retry_after))
                }
            )
        
        # Record this attempt
        rate_limit_store[key].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max_attempts - len(rate_limit_store[key])
        response.headers["X-RateLimit-Limit"] = str(max_attempts)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + window_seconds))
        
        # Log successful attempts
        if response.status_code < 400:
            logger.info(
                f"{endpoint_name} attempt from {client_id}. "
                f"Remaining: {remaining}/{max_attempts}"
            )
        
        return response
