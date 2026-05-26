"""Unit tests for the Ollama client module."""

from unittest.mock import MagicMock, patch

import pytest

from camarilla.bot.ollama import OllamaError, ask


class TestAskSuccess:
    """Tests for successful ask() calls."""

    @patch("camarilla.bot.ollama.ollama.Client")
    def test_ask_returns_response_content(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.chat.return_value = {
            "message": {"content": "The screwdriver is in the garage."}
        }
        mock_client_class.return_value = mock_client

        result = ask("Where is the screwdriver?")

        assert result == "The screwdriver is in the garage."
        mock_client.chat.assert_called_once()
        call_kwargs = mock_client.chat.call_args[1]
        assert call_kwargs["model"] == "qwen2:1.5b"
        messages = call_kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert "home inventory assistant" in messages[0]["content"]
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Where is the screwdriver?"

    @patch("camarilla.bot.ollama.ollama.Client")
    def test_ask_includes_inventory_context(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.chat.return_value = {
            "message": {"content": "Found it."}
        }
        mock_client_class.return_value = mock_client

        context = "## Garage\n- Screwdriver\n- Hammer"
        result = ask("Where is the screwdriver?", inventory_context=context)

        assert result == "Found it."
        messages = mock_client.chat.call_args[1]["messages"]
        assert "INVENTORY DATA:" in messages[0]["content"]
        assert context in messages[0]["content"]


class TestAskError:
    """Tests for ask() error handling."""

    @patch("camarilla.bot.ollama.ollama.Client")
    def test_ask_raises_ollama_error_on_connection_failure(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.chat.side_effect = ConnectionError("Connection refused")
        mock_client_class.return_value = mock_client

        with pytest.raises(OllamaError, match="Failed to connect to Ollama"):
            ask("Where is the screwdriver?")
