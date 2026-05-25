"""Bot lifecycle: creation, registration, and polling startup."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from camarilla.bot.handlers import router as handlers_router
from camarilla.bot.middleware import LoggingMiddleware
from camarilla.config import BOT_TOKEN

logger = logging.getLogger(__name__)


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    """Create and return a Bot + Dispatcher pair with default settings."""
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
    dp = Dispatcher()
    dp.include_router(handlers_router)
    dp.message.middleware(LoggingMiddleware())
    return bot, dp


async def main() -> None:
    """Set up the bot and start polling."""
    # Fail fast if required env vars are missing.
    from camarilla import config

    if not config.BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is required but not set."
        )
    if not config.AUTHORIZED_USER_IDS:
        raise RuntimeError(
            "TELEGRAM_USER_IDS environment variable is required but not set. "
            "Use comma-separated user IDs, e.g.: TELEGRAM_USER_IDS=123456,789012"
        )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    bot, dp = create_bot_and_dispatcher()
    logger.info("Starting bot polling …")
    await dp.start_polling(bot)
