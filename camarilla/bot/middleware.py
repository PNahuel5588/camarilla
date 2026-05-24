"""Lightweight logging middleware for incoming updates."""

import logging

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Log every incoming message at INFO level."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Log user_id, message type, and truncated text, then proceed."""
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            text = (event.text or "")[:100]
            logger.info(
                "Incoming message: user_id=%s type=%s text=%r",
                user_id,
                event.content_type,
                text,
            )
        return await handler(event, data)
