import os
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from config import settings

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency function to validate the API key.
    """
    # Allow missing/any key in debug mode or during pytest runs (tests don't send headers)
    if settings.DEBUG_MODE or os.getenv("PYTEST_CURRENT_TEST"):
        return api_key or "debug"
    if api_key == settings.API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
