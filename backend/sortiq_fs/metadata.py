"""Metadata extractor for files.

Gathers type and structural metadata into a plain dict.
Pure Python; no Django imports.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any

import filetype


def _path_kind(path: str) -> str:
    if ":" in path or "\\" in path:
        return "windows"
    return "posix"


def _native_path(path: str) -> str:
    if _path_kind(path) == "windows":
        return str(PureWindowsPath(path))
    return str(PurePosixPath(path))


def extract(path: str) -> dict[str, Any]:
    native = _native_path(path)
    metadata: dict[str, Any] = {
        "name": os.path.basename(native),
        "extension": os.path.splitext(native)[1].lower().lstrip("."),
        "size_bytes": 0,
        "mtime_ns": 0,
        "ctime_ns": 0,
        "is_symlink": os.path.islink(native),
        "mime_type": None,
        "filetype": None,
    }

    try:
        stat = os.stat(native)
        metadata["size_bytes"] = stat.st_size
        metadata["mtime_ns"] = stat.st_mtime_ns
        metadata["ctime_ns"] = stat.st_ctime_ns
    except OSError:
        return metadata

    kind = filetype.guess(native)
    if kind is not None:
        metadata["mime_type"] = kind.mime
        metadata["filetype"] = kind.extension

    if metadata["extension"] in ("json",):
        try:
            with open(native, "r", encoding="utf-8") as handle:
                json.load(handle)
            metadata["valid_json"] = True
        except (OSError, ValueError):
            metadata["valid_json"] = False

    if metadata["extension"] in ("md", "txt"):
        try:
            with open(native, "rb") as handle:
                head = handle.read(1024)
            metadata["head_sha256"] = hashlib.sha256(head).hexdigest()
        except OSError:
            pass

    return metadata
