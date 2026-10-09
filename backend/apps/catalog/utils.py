"""Path normalization for Windows paths."""

from __future__ import annotations

from pathlib import PurePosixPath, PureWindowsPath


def normalize_windows_path(path: str) -> str:
    """Normalize Windows paths to canonical forward-slash form."""
    p = str(path).replace("\\", "/")
    p = p.replace("//", "/")
    while "//" in p:
        p = p.replace("//", "/")
    return p.rstrip("/")


def is_windows_path(path: str) -> bool:
    """Detect Windows drive-letter paths."""
    return ":" in path or "\\" in path


def to_platform_path(path: str) -> str:
    """Convert canonical forward-slash path to native OS path."""
    if is_windows_path(path):
        return str(PureWindowsPath(path))
    return str(PurePosixPath(path))
