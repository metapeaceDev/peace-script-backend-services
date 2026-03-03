from typing import Any, Dict, List, Optional
import httpx

from .logger import get_logger


logger = get_logger(__name__)


async def chat_completion(
    base_url: str,
    model: str,
    messages: List[Dict[str, str]],
    api_key: str = "",
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
    timeout: float = 120.0,
) -> Dict[str, Any]:
    """
    Make a chat completion request to an OpenAI-compatible API.

    Args:
        base_url: Base URL of the LLM API
        model: Model name to use
        messages: List of message dictionaries
        api_key: API key for authentication (optional)
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds

    Returns:
        API response as dictionary

    Raises:
        httpx.HTTPError: On HTTP errors
        ValueError: On invalid parameters
    """
    if not base_url or not model:
        raise ValueError("base_url and model are required")

    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a non-empty list")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": max(0.0, min(2.0, temperature)),  # Clamp to valid range
    }
    if max_tokens is not None and max_tokens > 0:
        payload["max_tokens"] = max_tokens

    url = f"{base_url.rstrip('/')}/chat/completions"

    logger.debug(f"Making request to {url} with model {model}")

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Received response with {len(result.get('choices', []))} choices")
            return result
    except httpx.TimeoutException as e:
        logger.error(f"Request timeout after {timeout}s: {e}")
        raise
    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat_completion: {e}")
        raise


def extract_message_text(response: Dict[str, Any]) -> str:
    """
    Extract the message text from an OpenAI-compatible API response.

    Args:
        response: API response dictionary

    Returns:
        Extracted message text, or empty string if extraction fails
    """
    try:
        if not isinstance(response, dict):
            logger.warning("Response is not a dictionary")
            return ""

        choices = response.get("choices", [])
        if not choices:
            logger.warning("No choices in response")
            return ""

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            logger.warning("First choice is not a dictionary")
            return ""

        message = first_choice.get("message", {})
        if not isinstance(message, dict):
            logger.warning("Message is not a dictionary")
            return ""

        content = message.get("content", "")
        if not isinstance(content, str):
            logger.warning("Content is not a string")
            return ""

        return content.strip()
    except Exception as e:
        logger.error(f"Error extracting message text: {e}")
        return ""
