"""Metadata extractor tests using tmp_path."""

from __future__ import annotations

import json
from pathlib import Path

from sortiq_fs.metadata import extract


def test_extract_basic(tmp_path: Path) -> None:
    file = tmp_path / "note.txt"
    file.write_text("hello", encoding="utf-8")
    meta = extract(str(file))
    assert meta["name"] == "note.txt"
    assert meta["extension"] == "txt"
    assert meta["size_bytes"] == 5
    assert meta["head_sha256"] is not None


def test_extract_json_valid(tmp_path: Path) -> None:
    file = tmp_path / "data.json"
    file.write_text(json.dumps({"a": 1}), encoding="utf-8")
    meta = extract(str(file))
    assert meta["valid_json"] is True


def test_extract_json_invalid(tmp_path: Path) -> None:
    file = tmp_path / "bad.json"
    file.write_text("{not json", encoding="utf-8")
    meta = extract(str(file))
    assert meta["valid_json"] is False
