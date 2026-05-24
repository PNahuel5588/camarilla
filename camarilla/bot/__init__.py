"""Camarilla Telegram bot package."""

from camarilla.bot.main import create_bot_and_dispatcher
from camarilla.bot.main import main as main  # noqa: F401

__all__ = ["create_bot_and_dispatcher", "main"]
