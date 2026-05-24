"""Centralized configuration for paths and constants."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INVENTARIO_PATH: Path = PROJECT_ROOT / "inventario.md"
BACKUPS_DIR: Path = PROJECT_ROOT / "backups"
MAX_BACKUPS: int = 10
BACKUP_PREFIX: str = "inventario_"

BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
AUTHORIZED_USER_ID: int = int(os.environ["TELEGRAM_USER_ID"]) if "TELEGRAM_USER_ID" in os.environ else 0
