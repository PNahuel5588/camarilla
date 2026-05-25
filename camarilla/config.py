"""Centralized configuration for paths and constants."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INVENTARIO_PATH: Path = PROJECT_ROOT / "inventario.md"
BACKUPS_DIR: Path = PROJECT_ROOT / "backups"
MAX_BACKUPS: int = 10
BACKUP_PREFIX: str = "inventario_"

BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
AUTHORIZED_USER_IDS: set[int] = {
    int(uid.strip())
    for uid in os.environ.get("TELEGRAM_USER_IDS", "").split(",")
    if uid.strip().isdigit()
}

OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "qwen2:1.5b")
OLLAMA_URL: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")
