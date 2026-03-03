"""
Enhanced Input Validation Utilities for DMM Backend.

This module provides custom Pydantic validators for:
- Password strength validation
- Email format validation
- UUID format validation
- String length and pattern validation
- Buddhist concept validation

Usage:
    from core.validators import validate_password_strength, validate_email
    
    class UserCreate(BaseModel):
        email: str
        password: str
        
        @validator('email')
        def validate_email_format(cls, v):
            return validate_email(v)
        
        @validator('password')
        def validate_password_format(cls, v):
            return validate_password_strength(v)
"""

import re
from typing import Optional
from pydantic import validator
import uuid


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_password_strength(password: str, min_length: int = 8) -> str:
    """
    Validate password strength.
    
    Requirements:
    - Minimum length (default 8 characters)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password string to validate
        min_length: Minimum password length (default 8)
        
    Returns:
        The validated password string
        
    Raises:
        ValueError: If password doesn't meet requirements
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if len(password) < min_length:
        raise ValueError(f"Password must be at least {min_length} characters long")
    
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    
    return password


def validate_email(email: str) -> str:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        The validated email string (lowercase)
        
    Raises:
        ValueError: If email format is invalid
    """
    if not email:
        raise ValueError("Email cannot be empty")
    
    # Basic email regex pattern
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    # Return lowercase for consistency
    return email.lower().strip()


def validate_uuid(value: str, field_name: str = "UUID") -> str:
    """
    Validate UUID format.
    
    Args:
        value: UUID string to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        The validated UUID string
        
    Raises:
        ValueError: If UUID format is invalid
    """
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    
    try:
        uuid.UUID(value)
        return value
    except ValueError:
        raise ValueError(f"Invalid {field_name} format. Must be a valid UUID.")


def validate_string_length(
    value: str, 
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    field_name: str = "Field"
) -> str:
    """
    Validate string length.
    
    Args:
        value: String to validate
        min_length: Minimum length (optional)
        max_length: Maximum length (optional)
        field_name: Name of the field (for error messages)
        
    Returns:
        The validated string
        
    Raises:
        ValueError: If string length is invalid
    """
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    
    length = len(value.strip())
    
    if min_length and length < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters long")
    
    if max_length and length > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters long")
    
    return value.strip()


def validate_username(username: str) -> str:
    """
    Validate username format.
    
    Requirements:
    - 3-30 characters
    - Only alphanumeric, underscore, and hyphen
    - Must start with alphanumeric
    
    Args:
        username: Username string to validate
        
    Returns:
        The validated username string
        
    Raises:
        ValueError: If username format is invalid
    """
    if not username:
        raise ValueError("Username cannot be empty")
    
    username = username.strip()
    
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters long")
    
    if len(username) > 30:
        raise ValueError("Username must be at most 30 characters long")
    
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$", username):
        raise ValueError(
            "Username must start with alphanumeric character and "
            "contain only alphanumeric, underscore, and hyphen"
        )
    
    return username


def validate_kusala_score(score: int) -> int:
    """
    Validate kusala (wholesome) score.
    
    Score must be between 0 and 100.
    
    Args:
        score: Kusala score to validate
        
    Returns:
        The validated score
        
    Raises:
        ValueError: If score is out of range
    """
    if score < 0 or score > 100:
        raise ValueError("Kusala score must be between 0 and 100")
    
    return score


def validate_akusala_score(score: int) -> int:
    """
    Validate akusala (unwholesome) score.
    
    Score must be between 0 and 100.
    
    Args:
        score: Akusala score to validate
        
    Returns:
        The validated score
        
    Raises:
        ValueError: If score is out of range
    """
    if score < 0 or score > 100:
        raise ValueError("Akusala score must be between 0 and 100")
    
    return score


def validate_mental_state(state: str) -> str:
    """
    Validate mental state string.
    
    Must be one of the valid Buddhist mental states.
    
    Args:
        state: Mental state string to validate
        
    Returns:
        The validated state string
        
    Raises:
        ValueError: If state is invalid
    """
    valid_states = {
        "calm", "peaceful", "anxious", "stressed", "happy", "sad",
        "angry", "fearful", "content", "restless", "focused", "distracted",
        "compassionate", "neutral", "agitated", "serene"
    }
    
    state_lower = state.lower().strip()
    
    if state_lower not in valid_states:
        raise ValueError(
            f"Invalid mental state. Must be one of: {', '.join(sorted(valid_states))}"
        )
    
    return state_lower


def validate_percentage(value: float, field_name: str = "Percentage") -> float:
    """
    Validate percentage value.
    
    Value must be between 0.0 and 100.0.
    
    Args:
        value: Percentage value to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        The validated percentage
        
    Raises:
        ValueError: If percentage is out of range
    """
    if value < 0.0 or value > 100.0:
        raise ValueError(f"{field_name} must be between 0.0 and 100.0")
    
    return value


def validate_url(url: str, schemes: Optional[list] = None) -> str:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
        schemes: Allowed URL schemes (default: ['http', 'https'])
        
    Returns:
        The validated URL string
        
    Raises:
        ValueError: If URL format is invalid
    """
    if not url:
        raise ValueError("URL cannot be empty")
    
    if schemes is None:
        schemes = ["http", "https"]
    
    url = url.strip()
    
    # Basic URL validation
    url_pattern = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
    
    if not re.match(url_pattern, url, re.IGNORECASE):
        raise ValueError("Invalid URL format")
    
    # Check scheme
    scheme = url.split("://")[0].lower()
    if scheme not in schemes:
        raise ValueError(f"URL scheme must be one of: {', '.join(schemes)}")
    
    return url


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text input by removing potentially dangerous characters.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length (optional)
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove control characters except newline and tab
    text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)
    
    # Remove potential XSS patterns
    text = re.sub(r"<script.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)
    text = re.sub(r"on\w+\s*=", "", text, flags=re.IGNORECASE)
    
    # Trim whitespace
    text = text.strip()
    
    # Enforce max length
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


# Pydantic validator decorators for common use cases

def password_validator(field_name: str = "password"):
    """
    Create a Pydantic validator for password fields.
    
    Usage:
        class UserCreate(BaseModel):
            password: str
            
            _validate_password = password_validator()
    """
    def validator_func(cls, v):
        return validate_password_strength(v)
    
    return validator(field_name)(validator_func)


def email_validator(field_name: str = "email"):
    """
    Create a Pydantic validator for email fields.
    
    Usage:
        class UserCreate(BaseModel):
            email: str
            
            _validate_email = email_validator()
    """
    def validator_func(cls, v):
        return validate_email(v)
    
    return validator(field_name)(validator_func)


def uuid_validator(field_name: str):
    """
    Create a Pydantic validator for UUID fields.
    
    Usage:
        class CharacterUpdate(BaseModel):
            character_id: str
            
            _validate_id = uuid_validator("character_id")
    """
    def validator_func(cls, v):
        return validate_uuid(v, field_name)
    
    return validator(field_name)(validator_func)
