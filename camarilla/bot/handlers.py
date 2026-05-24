"""Message handlers for the Camarilla Telegram bot."""

import asyncio
import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from camarilla.bot.filters import AuthorizedUser
from camarilla.bot.ollama import OllamaError, ask
from camarilla.inventario import InventarioError, _render, leer_inventario

logger = logging.getLogger(__name__)
router = Router()


@router.message(AuthorizedUser(), CommandStart())
async def cmd_start(message: Message) -> None:
    """Send a welcome message."""
    await message.answer(
        "Welcome to Camarilla!\n\n"
        "I help you manage your home inventory. "
        "Use /help to see available commands."
    )


@router.message(AuthorizedUser(), Command("help"))
async def cmd_help(message: Message) -> None:
    """List available commands."""
    await message.answer(
        "Available commands:\n"
        "/start — Welcome message\n"
        "/help — This help text\n"
        "/inventario — Show current inventory"
    )


@router.message(AuthorizedUser(), Command("inventario"))
async def cmd_inventario(message: Message) -> None:
    """Read inventory and send it formatted."""
    try:
        data = await asyncio.to_thread(leer_inventario)
    except InventarioError as exc:
        logger.exception("Failed to read inventory")
        await message.answer(f"Error reading inventory: {exc}")
        return

    lines = ["*Current Inventory*"]
    for room, sections in data.items():
        lines.append(f"\n*🏠 {room}*")
        if isinstance(sections, list):
            for item in sections:
                lines.append(f"  • {item}")
        elif isinstance(sections, dict):
            for section, items in sections.items():
                lines.append(f"  📦 {section}")
                if isinstance(items, list):
                    for item in items:
                        lines.append(f"    • {item}")
                elif isinstance(items, dict):
                    for subsection, subitems in items.items():
                        lines.append(f"    🔹 {subsection}")
                        if isinstance(subitems, list):
                            for item in subitems:
                                lines.append(f"      • {item}")

    text = "\n".join(lines)
    await message.answer(text)


@router.message(AuthorizedUser())
async def ai_handler(message: Message) -> None:
    """Handle non-command text by querying Ollama with inventory context."""
    try:
        inventory_data = await asyncio.to_thread(leer_inventario)
        context = _render(inventory_data)
    except InventarioError:
        context = None

    try:
        response = await asyncio.to_thread(ask, message.text, context)
    except OllamaError:
        logger.exception("Ollama query failed")
        await message.answer(
            "AI service is currently unavailable. Please try again later."
        )
        return

    response = response[:4000]
    await message.answer(response, parse_mode=None)
