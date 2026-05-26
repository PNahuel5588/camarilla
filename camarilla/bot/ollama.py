"""Ollama client for AI-powered inventory queries."""

import logging

import ollama

from camarilla import config

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Base exception for Ollama connection/response errors."""


def ask(question: str, inventory_context: str | None = None) -> str:
    """Send a question to Ollama and return the response.

    inventory_context is the raw inventario.md content injected as system prompt.
    Raises OllamaError on connection/timeout failures.
    """
    system_prompt = (
        "You are a home inventory assistant. Your ONLY job is to answer questions "
        "about where things are located based on the inventory data provided below.\n\n"
        "STRICT RULES:\n"
        "- ONLY use information from the inventory data below. Never invent locations.\n"
        "- If the item is not in the inventory, say you don't have it registered.\n"
        "- If you're not sure where something is, say so. Never guess.\n"
        "- When you know the location, be specific: room, furniture, drawer/section.\n"
        "- Respond in the same language the user writes in.\n\n"
    )
    if inventory_context:
        system_prompt += f"INVENTORY DATA:\n{inventory_context}\n\n"
        system_prompt += (
            "IMPORTANT: Only reference items and locations that appear in the "
            "inventory data above. If something is not listed, it is NOT in the inventory."
        )
    else:
        system_prompt += "WARNING: No inventory data is available. Tell the user the inventory is empty."

    client = ollama.Client(host=config.OLLAMA_URL)

    try:
        response = client.chat(
            model=config.OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
        )
    except Exception as exc:
        logger.error("Ollama request failed: %s", exc)
        raise OllamaError(f"Failed to connect to Ollama: {exc}") from exc

    content = response["message"]["content"]
    if len(content) > 4000:
        return content[:4000]
    return content
