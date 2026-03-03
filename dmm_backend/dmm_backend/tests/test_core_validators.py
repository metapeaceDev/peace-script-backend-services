"""
Tests for Core Input Validation Utilities.

Tests:
1. Password strength validation
2. Email format validation
3. UUID format validation
4. String length validation
5. Username validation
6. Buddhist scores validation (kusala, akusala)
7. Text sanitization
"""

import pytest
from core.validators import (
    validate_password_strength,
    validate_email,
    validate_uuid,
    validate_string_length,
    validate_username,
    validate_kusala_score,
    validate_akusala_score,
    validate_mental_state,
    validate_percentage,
    validate_url,
    sanitize_text,
)


class TestPasswordValidation:
    """Test password strength validation."""
    
    def test_valid_strong_password(self):
        """Test validation of a strong password."""
        password = "MyP@ssw0rd123!"
        result = validate_password_strength(password)
        assert result == password
    
    def test_password_too_short(self):
        """Test rejection of too short password."""
        with pytest.raises(ValueError, match="at least 8 characters"):
            validate_password_strength("Pass1!")
    
    def test_password_no_uppercase(self):
        """Test rejection of password without uppercase."""
        with pytest.raises(ValueError, match="uppercase letter"):
            validate_password_strength("myp@ssw0rd123!")
    
    def test_password_no_lowercase(self):
        """Test rejection of password without lowercase."""
        with pytest.raises(ValueError, match="lowercase letter"):
            validate_password_strength("MYP@SSW0RD123!")
    
    def test_password_no_digit(self):
        """Test rejection of password without digit."""
        with pytest.raises(ValueError, match="digit"):
            validate_password_strength("MyP@ssword!")
    
    def test_password_no_special_char(self):
        """Test rejection of password without special character."""
        with pytest.raises(ValueError, match="special character"):
            validate_password_strength("MyPassword123")


class TestEmailValidation:
    """Test email format validation."""
    
    def test_valid_email(self):
        """Test validation of valid email."""
        email = "user@example.com"
        result = validate_email(email)
        assert result == email
    
    def test_email_lowercase_conversion(self):
        """Test email is converted to lowercase."""
        result = validate_email("User@Example.COM")
        assert result == "user@example.com"
    
    def test_invalid_email_no_at(self):
        """Test rejection of email without @."""
        with pytest.raises(ValueError, match="Invalid email"):
            validate_email("userexample.com")


class TestUUIDValidation:
    """Test UUID format validation."""
    
    def test_valid_uuid(self):
        """Test validation of valid UUID."""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        result = validate_uuid(uuid_str)
        assert result == uuid_str
    
    def test_invalid_uuid_format(self):
        """Test rejection of invalid UUID format."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            validate_uuid("not-a-uuid")


class TestUsernameValidation:
    """Test username format validation."""
    
    def test_valid_username(self):
        """Test validation of valid username."""
        username = "user123"
        result = validate_username(username)
        assert result == username
    
    def test_username_too_short(self):
        """Test rejection of too short username."""
        with pytest.raises(ValueError, match="at least 3 characters"):
            validate_username("ab")


class TestBuddhistScoresValidation:
    """Test Buddhist scores validation."""
    
    def test_valid_kusala_score(self):
        """Test validation of valid kusala score."""
        assert validate_kusala_score(50) == 50
        assert validate_kusala_score(0) == 0
        assert validate_kusala_score(100) == 100
    
    def test_invalid_kusala_score(self):
        """Test rejection of invalid kusala score."""
        with pytest.raises(ValueError, match="between 0 and 100"):
            validate_kusala_score(101)
    
    def test_valid_akusala_score(self):
        """Test validation of valid akusala score."""
        assert validate_akusala_score(30) == 30
    
    def test_valid_mental_state(self):
        """Test validation of valid mental state."""
        result = validate_mental_state("calm")
        assert result == "calm"


class TestTextSanitization:
    """Test text sanitization."""
    
    def test_sanitize_clean_text(self):
        """Test sanitization of clean text."""
        text = "This is clean text"
        result = sanitize_text(text)
        assert result == text
    
    def test_sanitize_remove_script_tags(self):
        """Test removal of script tags."""
        text = "Hello<script>alert('xss')</script>World"
        result = sanitize_text(text)
        assert "<script>" not in result
        assert "alert" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
