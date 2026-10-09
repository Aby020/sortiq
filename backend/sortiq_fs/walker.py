"""Directory walker producing a stream of entry records.

Emits dicts describing files and directories; never mutates the filesystem.
Pure Python; no Django imports.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterator


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


def iter_entries(root: str, *, recursive: bool = True, follow_symlinks: bool = False) -> Iterator[WalkEntry]:
    stats = WalkStats()
    root = os.path.abspath(root)

    try:
        entries = list(os.scandir(root))
    except OSError as exc:
        stats.errors.append(str(exc))
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
        except OSError:
            size = 0
            mtime_ns = 0
            ctime_ns = 0
            inode = ""

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
            yield from iter_entries(
                absolute,
                recursive=recursive,
                follow_symlinks=follow_symlinks,
            )


def walk(root: str, *, recursive: bool = True, follow_symlinks: bool = False) -> tuple[list[WalkEntry], WalkStats]:
    entries = list(iter_entries(root, recursive=recursive, follow_symlinks=follow_symlinks))
    stats = WalkStats(
        files=sum(1 for e in entries if not e.is_directory),
        directories=sum(1 for e in entries if e.is_directory),
        symlinks=sum(1 for e in entries if e.is_symlink),
    )
    return entries, stats
