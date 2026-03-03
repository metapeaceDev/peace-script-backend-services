import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
import asyncio

from app.llm_client import chat_completion, extract_message_text


class TestChatCompletion:
    """Test chat completion functionality."""

    def test_chat_completion_missing_base_url(self):
        """Test chat_completion raises ValueError for missing base_url."""
        with pytest.raises(ValueError, match="base_url and model are required"):
            asyncio.run(chat_completion("", "test-model", [{"role": "user", "content": "test"}]))

    def test_chat_completion_missing_model(self):
        """Test chat_completion raises ValueError for missing model."""
        with pytest.raises(ValueError, match="base_url and model are required"):
            asyncio.run(chat_completion("http://test.com", "", [{"role": "user", "content": "test"}]))

    def test_chat_completion_empty_messages(self):
        """Test chat_completion raises ValueError for empty messages."""
        with pytest.raises(ValueError, match="messages must be a non-empty list"):
            asyncio.run(chat_completion("http://test.com", "test-model", []))

    def test_chat_completion_invalid_messages_type(self):
        """Test chat_completion raises ValueError for invalid messages type."""
        with pytest.raises(ValueError, match="messages must be a non-empty list"):
            asyncio.run(chat_completion("http://test.com", "test-model", "not a list"))

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_chat_completion_success(self, mock_client_class):
        """Test successful chat completion request."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_response.raise_for_status.return_value = None

        # Mock client
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = await chat_completion(
            base_url="http://test.com",
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}]
        )

        assert result == {"choices": [{"message": {"content": "Test response"}}]}
        mock_client.post.assert_called_once()

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_chat_completion_with_api_key(self, mock_client_class):
        """Test chat completion with API key."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        await chat_completion(
            base_url="http://test.com",
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            api_key="test-key"
        )

        # Check that Authorization header was set
        call_args = mock_client.post.call_args
        headers = call_args[1]['headers']
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-key"

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_chat_completion_with_parameters(self, mock_client_class):
        """Test chat completion with various parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        await chat_completion(
            base_url="http://test.com",
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.8,
            max_tokens=100,
            timeout=60.0
        )

        call_args = mock_client.post.call_args
        payload = call_args[1]['json']

        assert payload['temperature'] == 0.8
        assert payload['max_tokens'] == 100
        assert payload['model'] == "test-model"

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_chat_completion_temperature_clamping(self, mock_client_class):
        """Test temperature parameter clamping."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Test high temperature
        await chat_completion(
            base_url="http://test.com",
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=3.0  # Should be clamped to 2.0
        )

        call_args = mock_client.post.call_args
        payload = call_args[1]['json']
        assert payload['temperature'] == 2.0

        # Test negative temperature
        await chat_completion(
            base_url="http://test.com",
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=-1.0  # Should be clamped to 0.0
        )

        call_args = mock_client.post.call_args
        payload = call_args[1]['json']
        assert payload['temperature'] == 0.0

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_chat_completion_timeout_error(self, mock_client_class):
        """Test timeout error handling."""
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with pytest.raises(httpx.TimeoutException):
            await chat_completion(
                base_url="http://test.com",
                model="test-model",
                messages=[{"role": "user", "content": "Hello"}]
            )

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_chat_completion_http_error(self, mock_client_class):
        """Test HTTP error handling."""
        mock_client = AsyncMock()
        # Create HTTPError with proper httpx format
        http_error = httpx.HTTPError("HTTP Error")
        http_error.response = MagicMock()
        http_error.response.status_code = 500
        http_error.response.text = "Internal Server Error"
        mock_client.post.side_effect = http_error
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with pytest.raises(httpx.HTTPError):
            await chat_completion(
                base_url="http://test.com",
                model="test-model",
                messages=[{"role": "user", "content": "Hello"}]
            )

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_chat_completion_url_construction(self, mock_client_class):
        """Test URL construction."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        await chat_completion(
            base_url="http://test.com/",
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}]
        )

        call_args = mock_client.post.call_args
        url = call_args[0][0]
        assert url == "http://test.com/chat/completions"

        # Test without trailing slash
        await chat_completion(
            base_url="http://test.com",
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}]
        )

        call_args = mock_client.post.call_args
        url = call_args[0][0]
        assert url == "http://test.com/chat/completions"


class TestExtractMessageText:
    """Test message text extraction."""

    def test_extract_message_text_valid_response(self):
        """Test extraction from valid response."""
        response = {
            "choices": [
                {
                    "message": {
                        "content": "Hello, world!"
                    }
                }
            ]
        }

        result = extract_message_text(response)
        assert result == "Hello, world!"

    def test_extract_message_text_with_whitespace(self):
        """Test extraction with whitespace trimming."""
        response = {
            "choices": [
                {
                    "message": {
                        "content": "  Hello, world!  \n\t"
                    }
                }
            ]
        }

        result = extract_message_text(response)
        assert result == "Hello, world!"

    def test_extract_message_text_empty_response(self):
        """Test extraction from empty response."""
        response = {}
        result = extract_message_text(response)
        assert result == ""

    def test_extract_message_text_no_choices(self):
        """Test extraction when no choices in response."""
        response = {"choices": []}
        result = extract_message_text(response)
        assert result == ""

    def test_extract_message_text_invalid_choice(self):
        """Test extraction with invalid choice structure."""
        response = {"choices": ["invalid"]}
        result = extract_message_text(response)
        assert result == ""

    def test_extract_message_text_no_message(self):
        """Test extraction when no message in choice."""
        response = {"choices": [{}]}
        result = extract_message_text(response)
        assert result == ""

    def test_extract_message_text_invalid_message(self):
        """Test extraction with invalid message structure."""
        response = {"choices": [{"message": "invalid"}]}
        result = extract_message_text(response)
        assert result == ""

    def test_extract_message_text_no_content(self):
        """Test extraction when no content in message."""
        response = {"choices": [{"message": {}}]}
        result = extract_message_text(response)
        assert result == ""

    def test_extract_message_text_invalid_content(self):
        """Test extraction with invalid content type."""
        response = {"choices": [{"message": {"content": 123}}]}
        result = extract_message_text(response)
        assert result == ""

    def test_extract_message_text_non_dict_response(self):
        """Test extraction with non-dict response."""
        result = extract_message_text("not a dict")
        assert result == ""

    def test_extract_message_text_exception_handling(self):
        """Test exception handling in extraction."""
        # This should not raise an exception
        result = extract_message_text(None)
        assert result == ""

    def test_extract_message_text_multiple_choices(self):
        """Test extraction uses first choice."""
        response = {
            "choices": [
                {"message": {"content": "First choice"}},
                {"message": {"content": "Second choice"}}
            ]
        }

        result = extract_message_text(response)
        assert result == "First choice"