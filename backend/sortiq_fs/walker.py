"""Directory walker producing a stream of entry records.

Emits dicts describing files and directories; never mutates the filesystem.
Pure Python; no Django imports.

Hardening: Windows ``PermissionError`` / ``OSError`` while stat-ing a
locked or restricted entry is captured into ``WalkStats.errors`` so the
scan thread never crashes on protected items.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Iterator

from sortiq_fs.pathguard import is_blacklisted, normalize

logger = logging.getLogger(__name__)


@dataclass
class WalkEntry:
    absolute_path: str
    relative_path: str
    name: str
    is_directory: bool
    size_bytes: int = 0
    mtime_ns: int = 0
    ctime_ns: int = 0
    inode: str = ""
    is_symlink: bool = False


@dataclass
class WalkStats:
    files: int = 0
    directories: int = 0
    symlinks: int = 0
    errors: list[str] = field(default_factory=list)
    skipped: int = 0


def iter_entries(
    root: str, *, recursive: bool = True, follow_symlinks: bool = False
) -> Iterator[WalkEntry]:
    stats = WalkStats()
    root = os.path.abspath(root)

    try:
        entries = list(os.scandir(root))
    except OSError as exc:
        stats.errors.append(f"{root}: {exc}")
        logger.warning("cannot list directory %s: %s", root, exc)
        return

    for entry in entries:
        is_symlink = entry.is_symlink()
        is_dir = entry.is_dir(follow_symlinks=follow_symlinks)
        try:
            stat = entry.stat(follow_symlinks=follow_symlinks)
            size = stat.st_size
            mtime_ns = stat.st_mtime_ns
            ctime_ns = stat.st_ctime_ns
            inode = str(stat.st_ino)
        except (PermissionError, OSError) as exc:
            stats.skipped += 1
            stats.errors.append(f"{entry.path}: {exc}")
            logger.info("skipped inaccessible entry %s: %s", entry.path, exc)
            continue

        absolute = os.path.abspath(entry.path)
        relative = os.path.relpath(absolute, root).replace("\\", "/")

        if is_symlink:
            stats.symlinks += 1
        if is_dir:
            stats.directories += 1
        else:
            stats.files += 1

        yield WalkEntry(
            absolute_path=absolute,
            relative_path=relative,
            name=entry.name,
            is_directory=is_dir,
            size_bytes=size,
            mtime_ns=mtime_ns,
            ctime_ns=ctime_ns,
            inode=inode,
            is_symlink=is_symlink,
        )

        if is_dir and recursive and not (is_symlink and not follow_symlinks):
            if is_blacklisted(normalize(absolute)):
                stats.skipped += 1
                logger.info("skipped protected directory %s", absolute)
                continue
            yield from iter_entries(
                absolute,
                recursive=recursive,
                follow_symlinks=follow_symlinks,
            )


def walk(
    root: str, *, recursive: bool = True, follow_symlinks: bool = False
) -> tuple[list[WalkEntry], WalkStats]:
    entries = list(iter_entries(root, recursive=recursive, follow_symlinks=follow_symlinks))
    stats = WalkStats(
        files=sum(1 for e in entries if not e.is_directory),
        directories=sum(1 for e in entries if e.is_directory),
        symlinks=sum(1 for e in entries if e.is_symlink),
    )
    return entries, stats
