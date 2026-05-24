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
        "You are a home inventory assistant. Answer the user's question about "
        "their belongings based on the inventory data below. Respond in the same "
        "language the user writes in.\n\n"
    )
    if inventory_context:
        system_prompt += f"Current inventory:\n{inventory_context}"

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
