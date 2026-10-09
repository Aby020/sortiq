"""Walker tests using tmp_path."""

from __future__ import annotations

from pathlib import Path

from sortiq_fs.walker import walk


def test_walk_lists_files_and_dirs(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hello")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("world")

    entries, stats = walk(str(tmp_path))
    assert stats.files == 2
    assert stats.directories >= 1
    assert len(entries) >= 3


def test_walk_non_recursive(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hello")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("world")

    entries, stats = walk(str(tmp_path), recursive=False)
    assert stats.files == 1
    assert stats.directories == 1
    assert all(e.relative_path.count("/") == 0 or e.is_directory for e in entries)
