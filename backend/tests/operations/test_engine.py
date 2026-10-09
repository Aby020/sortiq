"""Engine tests using tmp_path; stat-before-act; conflict detection."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from apps.operations.engine import (
    JournalEntry,
    _apply,
    _fingerprint,
    _stat_state,
    execute_plan,
)
from apps.operations.plan import OperationPlan


class TestPlanConflicts:
    def test_duplicate_target_conflict(self, tmp_path: Path) -> None:
        plan = OperationPlan()
        plan.add(str(tmp_path / "a.txt"), str(tmp_path / "dest.txt"), "move")
        plan.add(str(tmp_path / "b.txt"), str(tmp_path / "dest.txt"), "copy")
        conflicts = plan.detect_conflicts()
        assert conflicts == [(0, 1)]
        assert plan.has_conflicts is True
        assert plan.conflict_count == 1

    def test_no_conflict(self, tmp_path: Path) -> None:
        plan = OperationPlan()
        plan.add(str(tmp_path / "a.txt"), str(tmp_path / "t1.txt"), "move")
        plan.add(str(tmp_path / "b.txt"), str(tmp_path / "t2.txt"), "copy")
        assert plan.detect_conflicts() == []
        assert plan.has_conflicts is False


class TestStatBeforeAct:
    def test_stat_existing_file(self, tmp_path: Path) -> None:
        f = tmp_path / "f.txt"
        f.write_text("hello")
        s = _stat_state(str(f))
        assert s.get("size") == 5
        assert "mtime_ns" in s

    def test_stat_missing_file(self, tmp_path: Path) -> None:
        s = _stat_state(str(tmp_path / "nope.txt"))
        assert s == {}

    def test_fingerprint_changes_with_content(self, tmp_path: Path) -> None:
        f = tmp_path / "f.txt"
        f.write_text("a")
        f.flush()
        os.utime(str(f), ns=(1_000_000_000, 1_000_000_000))
        fp1 = _fingerprint(str(f))
        f.write_text("bb")
        f.flush()
        os.utime(str(f), ns=(2_000_000_000, 2_000_000_000))
        fp2 = _fingerprint(str(f))
        assert fp1 != fp2


class TestApply:
    def test_move_and_copy(self, tmp_path: Path) -> None:
        src = tmp_path / "src.txt"
        src.write_text("data")
        dest = tmp_path / "dest.txt"
        entry = JournalEntry(
            index=0, source=str(src), target=str(dest), action="move", status="running"
        )
        _apply(entry)
        assert not src.exists()
        assert dest.read_text() == "data"

    def test_quarantine_is_move(self, tmp_path: Path) -> None:
        src = tmp_path / "bad.exe"
        src.write_text("x")
        q = tmp_path / "quarantine" / "bad.exe"
        entry = JournalEntry(
            index=0, source=str(src), target=str(q), action="quarantine", status="running"
        )
        _apply(entry)
        assert q.exists()
        assert not src.exists()

    def test_delete_raises(self, tmp_path: Path) -> None:
        src = tmp_path / "tmp.txt"
        src.write_text("x")
        entry = JournalEntry(
            index=0,
            source=str(src),
            target=str(tmp_path / "t.txt"),
            action="delete",
            status="running",
        )
        with pytest.raises(NotImplementedError):
            _apply(entry)


class TestExecutePlan:
    def test_successful_move(self, tmp_path: Path) -> None:
        src = tmp_path / "a.txt"
        src.write_text("hello")
        plan = OperationPlan()
        plan.add(str(src), str(tmp_path / "b.txt"), "move")
        metrics = execute_plan(plan, str(tmp_path / "journal.json"), verify=True, persist=False)
        assert metrics["executed"] == 1
        assert metrics["failed"] == 0
        assert not src.exists()
        assert (tmp_path / "b.txt").exists()

    def test_stat_before_act_rejects_missing(self, tmp_path: Path) -> None:
        plan = OperationPlan()
        plan.add(str(tmp_path / "missing.txt"), str(tmp_path / "out.txt"), "move")
        metrics = execute_plan(plan, str(tmp_path / "journal.json"), verify=True, persist=False)
        assert metrics["failed"] == 1
        assert metrics["executed"] == 0

    def test_partial_failure(self, tmp_path: Path) -> None:
        good = tmp_path / "good.txt"
        good.write_text("ok")
        plan = OperationPlan()
        plan.add(str(good), str(tmp_path / "out_good.txt"), "move")
        plan.add(str(tmp_path / "bad.txt"), str(tmp_path / "out_bad.txt"), "move")
        metrics = execute_plan(plan, str(tmp_path / "journal.json"), verify=True, persist=False)
        assert metrics["executed"] == 1
        assert metrics["failed"] == 1

    def test_copy_preserves_source(self, tmp_path: Path) -> None:
        src = tmp_path / "orig.txt"
        src.write_text("data")
        plan = OperationPlan()
        plan.add(str(src), str(tmp_path / "copy.txt"), "copy")
        metrics = execute_plan(plan, str(tmp_path / "journal.json"), verify=True, persist=False)
        assert metrics["executed"] == 1
        assert src.exists()
        assert (tmp_path / "copy.txt").read_text() == "data"
