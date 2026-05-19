"""Shared pytest fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_inventario_path(tmp_path: Path) -> Path:
    """Return a temporary path for an inventario file."""
    return tmp_path / "inventario.md"


@pytest.fixture
def tmp_backups_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for backups."""
    d = tmp_path / "backups"
    d.mkdir()
    return d
