"""Safe inventory I/O with locking, atomic writes, and automatic backups."""

import fcntl
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from camarilla import config


class InventarioError(Exception):
    """Base exception for inventory I/O and format errors."""


def leer_inventario(path: Path | str | None = None) -> dict[str, Any]:
    """Read and parse inventario.md under LOCK_SH.

    Returns a nested dict: {room: {furniture: {section: [items]}}}.
    Raises InventarioError on empty or corrupt files.
    """
    path = Path(path) if path is not None else config.INVENTARIO_PATH

    if not path.exists():
        raise InventarioError(f"Inventory file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            content = f.read()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    lines = content.splitlines()
    return _parse(lines)


def escribir_inventario(data: dict[str, Any], path: Path | str | None = None) -> None:
    """Serialize data to inventario.md under LOCK_EX with backup + atomic write.

    Raises InventarioError on serialization or I/O failure.
    """
    path = Path(path) if path is not None else config.INVENTARIO_PATH
    backups_dir = config.BACKUPS_DIR

    try:
        content = _render(data)
    except Exception as exc:
        raise InventarioError(f"Failed to serialize inventory data: {exc}") from exc

    # Ensure parent directory exists so open() with O_CREAT works.
    path.parent.mkdir(parents=True, exist_ok=True)

    fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)

        if os.fstat(fd).st_size > 0:
            _backup(path, backups_dir)
            _cleanup_backups(backups_dir, config.MAX_BACKUPS)

        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as tmp:
            tmp.write(content)

        os.replace(str(temp_path), str(path))
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _parse(lines: list[str]) -> dict[str, Any]:
    """Parse markdown headers and bullets into a nested dict."""
    data: dict[str, Any] = {}
    # Stack of tuples: (header_level, parent_dict, key_in_parent)
    stack: list[tuple[int, dict[str, Any], str]] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("#"):
            level = 0
            for char in line:
                if char == "#":
                    level += 1
                else:
                    break

            title = line[level:].strip()
            if level == 1:
                # Document title — ignored in data model.
                continue

            # Pop higher-or-equal levels to find the correct parent.
            while stack and stack[-1][0] >= level:
                stack.pop()

            if level == 2:
                data[title] = []
                stack = [(2, data, title)]
            else:
                if not stack:
                    raise InventarioError(
                        f"Subsection header '{title}' found without a parent room (##)"
                    )

                _parent_level, parent_dict, parent_key = stack[-1]
                current = parent_dict[parent_key]

                # If the current container is already a non-empty list,
                # convert it to a dict so it can hold both items and subsections.
                if isinstance(current, list) and current:
                    parent_dict[parent_key] = {"": current}
                    current = parent_dict[parent_key]
                elif isinstance(current, list):
                    # Empty list — replace with a dict cleanly.
                    parent_dict[parent_key] = {}
                    current = parent_dict[parent_key]

                current[title] = []
                stack.append((level, current, title))

        elif line.startswith("- "):
            item = line[2:].strip()
            if not stack:
                raise InventarioError("Item found before any header")

            _level, parent_dict, key = stack[-1]
            current = parent_dict[key]

            if isinstance(current, dict):
                if "" not in current:
                    current[""] = []
                current[""].append(item)
            else:
                current.append(item)

    if not data:
        raise InventarioError("No room headers (##) found")

    return data


def _render(data: dict[str, Any], level: int = 2) -> str:
    """Serialize a nested dict back to markdown headers and bullets."""
    lines: list[str] = []

    if isinstance(data, list):
        for item in data:
            lines.append(f"- {item}")
        return "\n".join(lines)

    if isinstance(data, dict):
        for key, value in data.items():
            if key == "":
                # Direct items at this level — render without a header.
                for item in value:
                    lines.append(f"- {item}")
                continue

            lines.append(f"{'#' * level} {key}")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"- {item}")
            elif isinstance(value, dict):
                sub = _render(value, level + 1)
                if sub:
                    lines.append(sub)
            else:
                raise InventarioError(f"Unexpected value type for key '{key}': {type(value)}")

        return "\n".join(lines)

    raise InventarioError(f"Unexpected data type: {type(data)}")


def _backup(src_path: Path, backups_dir: Path) -> Path:
    """Copy the current inventario.md to backups/inventario_YYYYMMDD_HHMMSS.md."""
    backups_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    dest = backups_dir / f"{config.BACKUP_PREFIX}{timestamp}.md"
    shutil.copy2(str(src_path), str(dest))
    return dest


def _cleanup_backups(backups_dir: Path, max_backups: int) -> None:
    """Remove the oldest backup(s) when the count exceeds *max_backups*."""
    if not backups_dir.exists():
        return

    backups = sorted(backups_dir.glob(f"{config.BACKUP_PREFIX}*.md"))
    while len(backups) > max_backups:
        oldest = backups.pop(0)
        oldest.unlink()
