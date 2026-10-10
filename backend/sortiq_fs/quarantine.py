"""Safe quarantine primitives.

All destructive operations route through the Windows Recycle Bin
via ``send2trash``. Permanent deletion is never performed. A local
``.sortiq_quarantine`` directory is used only as a fallback when
the Recycle Bin API is unavailable.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from sortiq_fs.pathguard import is_blacklisted, normalize

QUARANTINE_DIRNAME = ".sortiq_quarantine"


def _local_quarantine_root() -> str:
    base = os.environ.get("SORTIQ_QUARANTINE_DIR")
    if base:
        return base
    local_app = os.environ.get("LOCALAPPDATA")
    if local_app:
        root = os.path.join(local_app, "Sortiq", QUARANTINE_DIRNAME)
        os.makedirs(root, exist_ok=True)
        return root
    return os.path.join(os.getcwd(), QUARANTINE_DIRNAME)


def safe_delete(source: str) -> str:
    """Move ``source`` to the Recycle Bin (or local fallback).

    Never performs a permanent ``os.remove`` / ``shutil.rmtree``.
    Returns the location the file was routed to.
    """

    source_norm = normalize(source)
    if is_blacklisted(source_norm):
        raise PermissionError(
            f"refusing to delete protected path: {source_norm}"
        )

    if not os.path.exists(source):
        raise FileNotFoundError(f"source does not exist: {source}")

    # Primary: Windows Recycle Bin (restorable by the user).
    try:
        import send2trash  # type: ignore

        send2trash.send2trash(source)
        return "recycle-bin"
    except Exception:
        pass

    # Fallback: local quarantine directory with unique naming.
    root = _local_quarantine_root()
    dest_dir = Path(root)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / os.path.basename(source)
    counter = 1
    while dest.exists():
        stem = f"{os.path.basename(source)}.{counter}"
        dest = dest_dir / stem
        counter += 1
    shutil.move(source, str(dest))
    return str(dest)


def quarantine_move(source: str, quarantine_root: str, dest_name: str | None = None) -> str:
    """Move a file into ``quarantine_root`` without deleting it."""

    source_norm = normalize(source)
    if is_blacklisted(source_norm):
        raise PermissionError(
            f"refusing to quarantine protected path: {source_norm}"
        )

    dest_name = dest_name or os.path.basename(source)
    dest = os.path.join(quarantine_root, dest_name)
    os.makedirs(quarantine_root, exist_ok=True)
    try:
        os.rename(source, dest)
    except OSError:
        shutil.move(source, dest)
    return dest


def quarantine_copy(source: str, quarantine_root: str, dest_name: str | None = None) -> str:
    dest_name = dest_name or os.path.basename(source)
    dest = os.path.join(quarantine_root, dest_name)
    os.makedirs(quarantine_root, exist_ok=True)
    shutil.copy2(source, dest)
    return dest


def restore(quarantine_path: str, target_path: str) -> None:
    os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
    shutil.move(quarantine_path, target_path)
