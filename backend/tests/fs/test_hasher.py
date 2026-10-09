"""Staged hasher tests using tmp_path."""

from __future__ import annotations

import hashlib
from pathlib import Path

from sortiq_fs.hasher import hash_file


def test_hash_file_full(tmp_path: Path) -> None:
    data = b"sortiq content" * 100
    file = tmp_path / "f.bin"
    file.write_bytes(data)
    result = hash_file(str(file))
    assert result.sha256 == hashlib.sha256(data).hexdigest()
    assert result.stage == "full"


def test_hash_file_partial_matches_prefix(tmp_path: Path) -> None:
    data = b"x" * 4096
    file = tmp_path / "f.bin"
    file.write_bytes(data)
    result = hash_file(str(file), partial_size=1024)
    expected_partial = hashlib.sha256(data[:1024]).hexdigest()
    assert result.partial_hash == expected_partial
    assert result.stage == "full"


def test_hash_file_empty(tmp_path: Path) -> None:
    file = tmp_path / "empty.bin"
    file.write_bytes(b"")
    result = hash_file(str(file))
    assert result.stage == "none"
    assert result.sha256 == hashlib.sha256(b"").hexdigest()
