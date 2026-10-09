"""Quarantine mutation primitives tests using tmp_path."""

from __future__ import annotations

from pathlib import Path

from sortiq_fs.quarantine import quarantine_copy, quarantine_move, restore


def test_quarantine_move(tmp_path: Path) -> None:
    source = tmp_path / "a.txt"
    source.write_text("move me")
    quarantine = tmp_path / "quarantine"
    dest = quarantine_move(str(source), str(quarantine))
    assert Path(dest).exists()
    assert not source.exists()


def test_quarantine_copy(tmp_path: Path) -> None:
    source = tmp_path / "a.txt"
    source.write_text("copy me")
    quarantine = tmp_path / "quarantine"
    dest = quarantine_copy(str(source), str(quarantine))
    assert Path(dest).exists()
    assert source.exists()


def test_restore(tmp_path: Path) -> None:
    source = tmp_path / "a.txt"
    source.write_text("restore me")
    quarantine = tmp_path / "quarantine"
    dest = quarantine_move(str(source), str(quarantine))
    target = tmp_path / "restored.txt"
    restore(dest, str(target))
    assert target.exists()
    assert not Path(dest).exists()
