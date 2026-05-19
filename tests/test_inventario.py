"""Unit tests for inventory I/O."""

from unittest.mock import MagicMock, patch

import pytest

from camarilla import config
from camarilla.inventario import (
    InventarioError,
    _backup,
    _cleanup_backups,
    _parse,
    _render,
    escribir_inventario,
    leer_inventario,
)


class TestParse:
    """Tests for the markdown parser."""

    def test_valid_parse(self):
        lines = [
            "# Title",
            "## Kitchen",
            "### Pantry",
            "- Rice",
            "- Beans",
            "### Fridge",
            "- Milk",
        ]
        result = _parse(lines)
        assert result == {
            "Kitchen": {
                "Pantry": ["Rice", "Beans"],
                "Fridge": ["Milk"],
            }
        }

    def test_deep_headers(self):
        lines = [
            "# Title",
            "## Room",
            "### Furniture",
            "#### Drawer",
            "##### Sub",
            "- Item",
        ]
        result = _parse(lines)
        assert result == {
            "Room": {
                "Furniture": {
                    "Drawer": {
                        "Sub": ["Item"],
                    }
                }
            }
        }

    def test_empty_file_raises(self):
        with pytest.raises(InventarioError):
            _parse([])

    def test_no_room_headers_raises(self):
        with pytest.raises(InventarioError):
            _parse(["# Just a title"])

    def test_item_before_header_raises(self):
        with pytest.raises(InventarioError):
            _parse(["- Orphan item"])


class TestRender:
    """Tests for the markdown renderer."""

    def test_simple_render(self):
        data = {"Kitchen": {"Pantry": ["Rice", "Beans"]}}
        text = _render(data)
        assert "## Kitchen" in text
        assert "### Pantry" in text
        assert "- Rice" in text
        assert "- Beans" in text

    def test_round_trip(self):
        original = {"Room": {"Shelf": {"Drawer": ["Item"]}}}
        text = _render(original)
        parsed = _parse(text.splitlines())
        assert parsed == original


class TestRead:
    """Tests for leer_inventario."""

    def test_valid_read(self, tmp_path, monkeypatch):
        inv = tmp_path / "inventario.md"
        inv.write_text(
            "# T\n## Kitchen\n### Pantry\n- Rice\n", encoding="utf-8"
        )
        # Point config at our temporary file for this test.
        monkeypatch.setattr(config, "INVENTARIO_PATH", inv)
        result = leer_inventario()
        assert result == {"Kitchen": {"Pantry": ["Rice"]}}

    def test_missing_file_raises(self):
        with pytest.raises(InventarioError):
            leer_inventario("/nonexistent/inventario.md")

    def test_shared_lock(self, tmp_path, monkeypatch):
        inv = tmp_path / "inventario.md"
        inv.write_text("# T\n## Room\n- Item\n", encoding="utf-8")
        monkeypatch.setattr(config, "INVENTARIO_PATH", inv)

        with patch("camarilla.inventario.fcntl.flock") as mock_flock:
            mock_fd = MagicMock()
            mock_flock.return_value = None
            leer_inventario()

        # Find the LOCK_SH call.
        lock_sh_calls = [
            c for c in mock_flock.call_args_list if c.args[1] == __import__("fcntl").LOCK_SH
        ]
        assert len(lock_sh_calls) >= 1


class TestWrite:
    """Tests for escribir_inventario."""

    def test_atomic_write(self, tmp_path, monkeypatch):
        inv = tmp_path / "inventario.md"
        backups = tmp_path / "backups"
        monkeypatch.setattr(config, "INVENTARIO_PATH", inv)
        monkeypatch.setattr(config, "BACKUPS_DIR", backups)

        data = {"Room": {"Shelf": ["Item"]}}
        escribir_inventario(data)

        assert inv.exists()
        # No leftover temp file.
        assert not (tmp_path / "inventario.tmp").exists()

    def test_backup_creation(self, tmp_path, monkeypatch):
        inv = tmp_path / "inventario.md"
        inv.write_text("# T\n## Room\n- Old\n", encoding="utf-8")
        backups = tmp_path / "backups"
        monkeypatch.setattr(config, "INVENTARIO_PATH", inv)
        monkeypatch.setattr(config, "BACKUPS_DIR", backups)

        escribir_inventario({"Room": {"Shelf": ["New"]}})

        backup_files = list(backups.glob("*.md"))
        assert len(backup_files) == 1

    def test_backup_rotation(self, tmp_path, monkeypatch):
        inv = tmp_path / "inventario.md"
        backups = tmp_path / "backups"
        monkeypatch.setattr(config, "INVENTARIO_PATH", inv)
        monkeypatch.setattr(config, "BACKUPS_DIR", backups)
        monkeypatch.setattr(config, "MAX_BACKUPS", 3)

        # Write 4 times; only 3 backups should remain.
        for i in range(4):
            escribir_inventario({"Room": {"Shelf": [f"Item {i}"]}})

        backup_files = sorted(backups.glob("*.md"))
        assert len(backup_files) == 3

    def test_exclusive_lock(self, tmp_path, monkeypatch):
        inv = tmp_path / "inventario.md"
        backups = tmp_path / "backups"
        monkeypatch.setattr(config, "INVENTARIO_PATH", inv)
        monkeypatch.setattr(config, "BACKUPS_DIR", backups)

        with patch("camarilla.inventario.fcntl.flock") as mock_flock:
            mock_flock.return_value = None
            escribir_inventario({"Room": {"Shelf": ["Item"]}})

        lock_ex_calls = [
            c for c in mock_flock.call_args_list if c.args[1] == __import__("fcntl").LOCK_EX
        ]
        assert len(lock_ex_calls) >= 1

    def test_round_trip(self, tmp_path, monkeypatch):
        inv = tmp_path / "inventario.md"
        backups = tmp_path / "backups"
        monkeypatch.setattr(config, "INVENTARIO_PATH", inv)
        monkeypatch.setattr(config, "BACKUPS_DIR", backups)

        original = {
            "Kitchen": {
                "Pantry": ["Rice", "Beans"],
                "Fridge": ["Milk"],
            }
        }
        escribir_inventario(original)
        result = leer_inventario(inv)
        assert result == original

    def test_empty_corrupt_file_raises_on_read(self, tmp_path, monkeypatch):
        inv = tmp_path / "inventario.md"
        inv.write_text("", encoding="utf-8")
        monkeypatch.setattr(config, "INVENTARIO_PATH", inv)
        with pytest.raises(InventarioError):
            leer_inventario()

    def test_format_validation(self, tmp_path, monkeypatch):
        """Deep header nesting is preserved correctly."""
        inv = tmp_path / "inventario.md"
        backups = tmp_path / "backups"
        monkeypatch.setattr(config, "INVENTARIO_PATH", inv)
        monkeypatch.setattr(config, "BACKUPS_DIR", backups)

        deep = {
            "A": {
                "B": {
                    "C": {
                        "D": {
                            "E": ["Deep item"],
                        }
                    }
                }
            }
        }
        escribir_inventario(deep)
        result = leer_inventario(inv)
        assert result == deep


class TestBackupHelpers:
    """Tests for _backup and _cleanup_backups."""

    def test_backup_copies_file(self, tmp_path):
        src = tmp_path / "inventario.md"
        src.write_text("content", encoding="utf-8")
        backups = tmp_path / "backups"

        dest = _backup(src, backups)
        assert dest.exists()
        assert dest.read_text(encoding="utf-8") == "content"

    def test_cleanup_removes_oldest(self, tmp_path, monkeypatch):
        backups = tmp_path / "backups"
        backups.mkdir()
        monkeypatch.setattr(config, "BACKUP_PREFIX", "test_")

        # Create 3 backups with deterministic names.
        for name in ["test_20240101_120000.md", "test_20240102_120000.md", "test_20240103_120000.md"]:
            (backups / name).write_text("x", encoding="utf-8")

        _cleanup_backups(backups, 2)
        remaining = sorted(backups.glob("*.md"))
        assert len(remaining) == 2
        assert "test_20240102_120000.md" in [r.name for r in remaining]
        assert "test_20240103_120000.md" in [r.name for r in remaining]
        assert "test_20240101_120000.md" not in [r.name for r in remaining]
