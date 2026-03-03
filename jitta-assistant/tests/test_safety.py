import pytest

from app.safety import (
    requires_payment_approval,
    contains_dangerous_content,
    sanitize_input,
    PAYMENT_KEYWORDS,
    DANGEROUS_CONTENT_KEYWORDS,
    URL_PAYMENT_HINTS,
)


class TestRequiresPaymentApproval:
    """Test payment approval detection."""

    def test_empty_text(self):
        """Test with empty or whitespace-only text."""
        assert requires_payment_approval("") is False
        assert requires_payment_approval("   ") is False
        assert requires_payment_approval("\n\t") is False

    def test_payment_keywords(self):
        """Test detection of payment-related keywords."""
        for keyword in PAYMENT_KEYWORDS:
            assert requires_payment_approval(f"I want to {keyword} something") is True
            assert requires_payment_approval(f"Please {keyword.upper()} now") is True
            assert requires_payment_approval(f"About {keyword}ing") is True

    def test_no_payment_keywords(self):
        """Test text without payment keywords."""
        safe_texts = [
            "Hello, how are you?",
            "Tell me about Python programming",
            "What's the weather like?",
            "Explain quantum physics",
            "How to cook pasta?",
        ]

        for text in safe_texts:
            assert requires_payment_approval(text) is False

    def test_payment_urls(self):
        """Test detection of payment-related URLs."""
        payment_urls = [
            "https://example.com/checkout",
            "http://store.com/cart",
            "https://billing.example.com/pay",
            "http://crypto.wallet.com/transaction",
        ]

        for url in payment_urls:
            assert requires_payment_approval(f"Check this: {url}") is True

    def test_safe_urls(self):
        """Test URLs that don't contain payment hints."""
        safe_urls = [
            "https://example.com/about",
            "http://docs.python.org/tutorial",
            "https://github.com/user/repo",
            "http://stackoverflow.com/questions",
        ]

        for url in safe_urls:
            assert requires_payment_approval(f"Check this: {url}") is False

    def test_case_insensitive(self):
        """Test case-insensitive keyword detection."""
        assert requires_payment_approval("I want to BUY something") is True
        assert requires_payment_approval("please PAY now") is True
        assert requires_payment_approval("About PAYMENT") is True


class TestContainsDangerousContent:
    """Test dangerous content detection."""

    def test_empty_text(self):
        """Test with empty or whitespace-only text."""
        assert contains_dangerous_content("") is False
        assert contains_dangerous_content("   ") is False

    def test_dangerous_keywords(self):
        """Test detection of dangerous content keywords."""
        for keyword in DANGEROUS_CONTENT_KEYWORDS:
            assert contains_dangerous_content(f"How to {keyword}?") is True
            assert contains_dangerous_content(f"Learn about {keyword.upper()}") is True
            assert contains_dangerous_content(f"{keyword}ing techniques") is True

    def test_no_dangerous_keywords(self):
        """Test text without dangerous keywords."""
        safe_texts = [
            "Hello, how are you?",
            "Tell me about Python programming",
            "What's the weather like?",
            "Explain quantum physics",
            "How to cook pasta?",
            "Learn about machine learning",
        ]

        for text in safe_texts:
            assert contains_dangerous_content(text) is False

    def test_case_insensitive(self):
        """Test case-insensitive keyword detection."""
        assert contains_dangerous_content("How to HACK a website?") is True
        assert contains_dangerous_content("Learn about MALWARE") is True
        assert contains_dangerous_content("EXPLOIT techniques") is True


class TestSanitizeInput:
    """Test input sanitization."""

    def test_empty_input(self):
        """Test sanitization of empty input."""
        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""

    def test_whitespace_trimming(self):
        """Test whitespace trimming."""
        assert sanitize_input("  hello  ") == "hello"
        assert sanitize_input("\t\nhello\t\n") == "hello"
        assert sanitize_input("  \n  hello  \n  ") == "hello"

    def test_length_limiting(self):
        """Test length limiting."""
        long_text = "a" * 15000
        sanitized = sanitize_input(long_text, max_length=100)
        assert len(sanitized) == 100
        assert sanitized == "a" * 100

    def test_normal_text(self):
        """Test normal text sanitization."""
        text = "Hello, world!"
        assert sanitize_input(text) == text

    def test_default_max_length(self):
        """Test default max length."""
        long_text = "a" * 20000
        sanitized = sanitize_input(long_text)
        assert len(sanitized) == 10000  # Default max_length

    @pytest.mark.parametrize("max_length", [10, 100, 1000])
    def test_custom_max_length(self, max_length):
        """Test custom max length."""
        long_text = "a" * (max_length + 100)
        sanitized = sanitize_input(long_text, max_length=max_length)
        assert len(sanitized) == max_length
        assert sanitized == "a" * max_length

    def test_unicode_text(self):
        """Test sanitization with unicode characters."""
        text = "  こんにちは 世界 🌍  "
        sanitized = sanitize_input(text)
        assert sanitized == "こんにちは 世界 🌍"

    def test_special_characters(self):
        """Test sanitization with special characters."""
        text = "  Hello@#$%^&*()  "
        sanitized = sanitize_input(text)
        assert sanitized == "Hello@#$%^&*()"