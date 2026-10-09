"""Quarantine mutation primitives.

Moves or copies files to a quarantine directory; never mutates source.
Uses pure Python os.rename/os.link or shutil.copy2; no Django ORM.
"""

from __future__ import annotations

import os
import shutil


def quarantine_move(source: str, quarantine_root: str, dest_name: str | None = None) -> str:
    dest_name = dest_name or os.path.basename(source)
    dest = os.path.join(quarantine_root, dest_name)
    os.makedirs(quarantine_root, exist_ok=True)
    # Use rename for atomic move when on same filesystem
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
