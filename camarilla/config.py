"""Centralized configuration for paths and constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INVENTARIO_PATH: Path = PROJECT_ROOT / "inventario.md"
BACKUPS_DIR: Path = PROJECT_ROOT / "backups"
MAX_BACKUPS: int = 10
BACKUP_PREFIX: str = "inventario_"
