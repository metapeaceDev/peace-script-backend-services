import re
from typing import Iterable

from .logger import get_logger


logger = get_logger(__name__)


PAYMENT_KEYWORDS: Iterable[str] = (
    "buy",
    "checkout",
    "payment",
    "subscribe",
    "billing",
    "purchase",
    "order",
    "price",
    "pricing",
    "invoice",
    "paid",
    "pay",
    "cost",
    "fee",
    "charge",
    "transaction",
    "wallet",
    "crypto",
    "bitcoin",
    "ethereum",
    "money",
    "fund",
    "donate",
    "contribution",
)

URL_PAYMENT_HINTS: Iterable[str] = (
    "checkout",
    "cart",
    "billing",
    "subscribe",
    "pricing",
    "pay",
    "payment",
    "purchase",
    "buy",
    "order",
    "invoice",
    "wallet",
    "crypto",
    "donate",
)

DANGEROUS_CONTENT_KEYWORDS: Iterable[str] = (
    "hack",
    "exploit",
    "malware",
    "virus",
    "trojan",
    "ransomware",
    "phishing",
    "scam",
    "fraud",
    "illegal",
    "criminal",
    "weapon",
    "drug",
    "violence",
    "harm",
    "suicide",
    "self-harm",
)


def requires_payment_approval(text: str) -> bool:
    """
    Check if the text contains keywords that suggest payment-related actions.

    Args:
        text: Text to check

    Returns:
        True if payment approval is required
    """
    if not text or not text.strip():
        return False

    text_l = text.lower()

    # Check payment keywords
    for kw in PAYMENT_KEYWORDS:
        if kw in text_l:
            logger.info(f"Payment keyword detected: '{kw}'")
            return True

    # Check URLs for payment hints
    for url in re.findall(r"https?://\S+", text_l):
        for hint in URL_PAYMENT_HINTS:
            if hint in url:
                logger.info(f"Payment URL hint detected: '{hint}' in '{url}'")
                return True

    return False


def contains_dangerous_content(text: str) -> bool:
    """
    Check if the text contains dangerous or inappropriate content.

    Args:
        text: Text to check

    Returns:
        True if dangerous content is detected
    """
    if not text or not text.strip():
        return False

    text_l = text.lower()

    for kw in DANGEROUS_CONTENT_KEYWORDS:
        if kw in text_l:
            logger.warning(f"Dangerous content keyword detected: '{kw}'")
            return True

    return False


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input by trimming and limiting length.

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Trim whitespace
    text = text.strip()

    # Limit length
    if len(text) > max_length:
        logger.warning(f"Input text truncated from {len(text)} to {max_length} characters")
        text = text[:max_length]

    return text
