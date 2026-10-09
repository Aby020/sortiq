"""Deduplication pipeline tests using tmp_path."""

from __future__ import annotations

from pathlib import Path

from apps.duplicates.services import (
    group_by_size,
    group_full_sha,
    group_partial_hash,
)


def make_file(path: Path, size: int) -> dict:
    file = path / f"file_{size}.bin"
    file.write_bytes(b"x" * size)
    return {
        "path": str(file),
        "size_bytes": size,
        "partial_hash": f"h{size}",
        "sha256": f"sha{size}",
    }


def test_group_by_size(tmp_path: Path) -> None:
    files = [make_file(tmp_path, 100), make_file(tmp_path, 100), make_file(tmp_path, 200)]
    groups = group_by_size(files)
    assert 100 in groups
    assert len(groups[100]) == 2
    assert 200 not in groups


def test_group_partial_hash(tmp_path: Path) -> None:
    files = [make_file(tmp_path, 100), make_file(tmp_path, 100), make_file(tmp_path, 300)]
    groups = group_partial_hash(files)
    assert "h100" in groups
    assert len(groups["h100"]) == 2


def test_group_full_sha(tmp_path: Path) -> None:
    files = [make_file(tmp_path, 100), make_file(tmp_path, 100), make_file(tmp_path, 400)]
    groups = group_full_sha(files)
    assert "sha100" in groups
    assert len(groups["sha100"]) == 2


def test_no_duplicates_returns_empty(tmp_path: Path) -> None:
    files = [make_file(tmp_path, 100), make_file(tmp_path, 200), make_file(tmp_path, 300)]
    assert group_by_size(files) == {}
    assert group_partial_hash(files) == {}
    assert group_full_sha(files) == {}
