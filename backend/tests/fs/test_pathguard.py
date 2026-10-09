"""PathGuard tests."""

from __future__ import annotations

from sortiq_fs.pathguard import (
    is_within,
    join,
    normalize,
    relative,
    validate,
)


def test_normalize_flattens_dots() -> None:
    assert normalize("/a/b/../c") == "/a/c"


def test_normalize_removes_dot_segments() -> None:
    assert normalize("/a/./b") == "/a/b"


def test_is_within_basic() -> None:
    assert is_within("/root", "/root/a/b")


def test_is_within_rejects_escape() -> None:
    assert not is_within("/root", "/other/file")


def test_join_root_and_segment() -> None:
    assert join("/root", "a", "b") == "/root/a/b"


def test_validate_allows_nested() -> None:
    result = validate("/root", "/root/a/b.txt")
    assert result.ok


def test_validate_rejects_escape() -> None:
    result = validate("/root", "/escape/file.txt")
    assert not result.ok
    assert "escapes" in result.reason


def test_relative_within_root() -> None:
    assert relative("/root", "/root/a/b") == "a/b"


def test_relative_root_returns_empty() -> None:
    assert relative("/root", "/root") == ""


def test_relative_raises_when_outside() -> None:
    try:
        relative("/root", "/other")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
