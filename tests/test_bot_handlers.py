"""Unit tests for the Telegram bot message handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from camarilla.bot.handlers import (
    ai_handler,
    cmd_help,
    cmd_inventario,
    cmd_start,
)


@pytest.fixture
def mock_message():
    """Return a mocked aiogram Message with an async answer method."""
    msg = MagicMock()
    msg.answer = AsyncMock()
    msg.text = "mock text"
    return msg


class TestCmdStart:
    """Tests for the /start handler."""

    @pytest.mark.asyncio
    async def test_welcome_message(self, mock_message):
        await cmd_start(mock_message)

        mock_message.answer.assert_awaited_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Welcome to Camarilla" in call_args


class TestCmdHelp:
    """Tests for the /help handler."""

    @pytest.mark.asyncio
    async def test_lists_commands(self, mock_message):
        await cmd_help(mock_message)

        mock_message.answer.assert_awaited_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "/start" in call_args
        assert "/help" in call_args
        assert "/inventario" in call_args


class TestCmdInventario:
    """Tests for the /inventario handler."""

    @pytest.mark.asyncio
    async def test_formatted_inventory(self, mock_message):
        inventory_data = {
            "Kitchen": {
                "Pantry": ["Rice", "Beans"],
                "Fridge": ["Milk"],
            }
        }

        with patch(
            "camarilla.bot.handlers.leer_inventario", return_value=inventory_data
        ):
            await cmd_inventario(mock_message)

        mock_message.answer.assert_awaited_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Kitchen" in call_args
        assert "Pantry" in call_args
        assert "Rice" in call_args
        assert "Beans" in call_args
        assert "Milk" in call_args

    @pytest.mark.asyncio
    async def test_inventory_error(self, mock_message):
        from camarilla.inventario import InventarioError

        with patch(
            "camarilla.bot.handlers.leer_inventario",
            side_effect=InventarioError("File not found"),
        ):
            await cmd_inventario(mock_message)

        mock_message.answer.assert_awaited_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Error reading inventory" in call_args
        assert "File not found" in call_args


class TestAIHandler:
    """Tests for the AI fallback handler."""

    @pytest.mark.asyncio
    async def test_ai_handler_success(self, mock_message):
        mock_message.text = "Where is the screwdriver?"

        with patch(
            "camarilla.bot.handlers.leer_inventario",
            return_value={"Garage": ["Screwdriver"]},
        ):
            with patch(
                "camarilla.bot.handlers.ask",
                return_value="It's in the garage.",
            ):
                await ai_handler(mock_message)

        mock_message.answer.assert_awaited_once()
        call_args = mock_message.answer.call_args
        assert call_args[0][0] == "It's in the garage."
        assert call_args[1].get("parse_mode") is None

    @pytest.mark.asyncio
    async def test_ai_handler_ollama_error(self, mock_message):
        from camarilla.bot.ollama import OllamaError

        mock_message.text = "Where is the screwdriver?"

        with patch(
            "camarilla.bot.handlers.leer_inventario",
            return_value={"Garage": ["Screwdriver"]},
        ):
            with patch(
                "camarilla.bot.handlers.ask",
                side_effect=OllamaError("Connection refused"),
            ):
                await ai_handler(mock_message)

        mock_message.answer.assert_awaited_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "unavailable" in call_args.lower()

    @pytest.mark.asyncio
    async def test_ai_handler_truncates_long_response(self, mock_message):
        mock_message.text = "List everything."

        long_response = "A" * 5000
        with patch(
            "camarilla.bot.handlers.leer_inventario",
            return_value={"Garage": ["Screwdriver"]},
        ):
            with patch(
                "camarilla.bot.handlers.ask",
                return_value=long_response,
            ):
                await ai_handler(mock_message)

        mock_message.answer.assert_awaited_once()
        call_args = mock_message.answer.call_args[0][0]
        assert len(call_args) == 4000
