"""Custom aiogram filters for access control."""

import logging

from aiogram.filters.base import Filter
from aiogram.types import Message

from camarilla import config

logger = logging.getLogger(__name__)


class AuthorizedUser(Filter):
    """Allow only messages from the configured authorized user."""

    async def __call__(self, message: Message) -> bool:
        """Return True if the sender matches AUTHORIZED_USER_ID."""
        user_id = message.from_user.id if message.from_user else None
        if user_id is not None and user_id == config.AUTHORIZED_USER_ID:
            return True

        text_preview = (message.text or "")[:100]
        logger.warning(
            "Unauthorized access attempt: user_id=%s message_text=%r",
            user_id,
            text_preview,
        )
        return False
