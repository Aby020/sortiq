"""WAL-style journal engine with stat-before-act verification."""

from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

Status = Literal["pending", "running", "completed", "failed", "partially_completed"]


@dataclass
class JournalEntry:
    index: int
    source: str
    target: str
    action: str
    status: str
    error: str | None = None
    pre_state: dict[str, Any] = None  # noqa: RUF013
    post_state: dict[str, Any] = None  # noqa: RUF013


def _stat_state(path: str) -> dict[str, Any]:
    try:
        st = os.stat(path)
        return {
            "size": st.st_size,
            "mtime_ns": st.st_mtime_ns,
            "inode": st.st_ino,
        }
    except OSError:
        return {}


def _fingerprint(path: str) -> str:
    state = _stat_state(path)
    return hashlib.sha256(f"{path}:{state}".encode()).hexdigest()


def _apply(item: JournalEntry) -> None:
    target_parent = Path(item.target).parent
    target_parent.mkdir(parents=True, exist_ok=True)
    if item.action == "move":
        shutil.move(item.source, item.target)
    elif item.action == "copy":
        shutil.copy2(item.source, item.target)
    elif item.action == "quarantine":
        shutil.move(item.source, item.target)
    elif item.action == "delete":
        raise NotImplementedError("delete is disabled; use quarantine instead")
    else:
        raise ValueError(f"unknown action: {item.action}")


def execute_plan(
    plan: Any,
    journal_path: str,
    verify: bool = True,
    on_progress: Any = None,
    persist: bool = True,
    user_id: str | None = None,
) -> dict[str, int]:
    journal: list[JournalEntry] = []
    metrics = {"executed": 0, "failed": 0, "skipped": 0}

    for idx, plan_item in enumerate(plan.items):
        entry = JournalEntry(
            index=idx,
            source=plan_item.source_path,
            target=plan_item.target_path,
            action=plan_item.action,
            status="pending",
            pre_state=_stat_state(plan_item.source_path),
        )

        if verify and not entry.pre_state:
            entry.status = "failed"
            entry.error = "source does not exist"
            journal.append(entry)
            metrics["failed"] += 1
            continue

        entry.status = "running"
        journal.append(entry)

        try:
            _apply(entry)
            entry.post_state = _stat_state(entry.target)
            entry.status = "success"
            metrics["executed"] += 1
        except Exception as exc:
            entry.status = "failed"
            entry.error = str(exc)
            metrics["failed"] += 1
            continue

        if on_progress:
            on_progress(idx + 1, len(plan.items))

    if persist:
        _persist_journal(journal, journal_path, user_id=user_id)
    return metrics


def _persist_journal(
    journal: list[JournalEntry], path: str, user_id: str | None = None
) -> None:
    from apps.operations.models import Operation, OperationItem

    executed = sum(1 for j in journal if j.status == "success")
    failed = sum(1 for j in journal if j.status == "failed")
    if failed == 0:
        status = "completed"
    elif executed > 0:
        status = "partially_completed"
    else:
        status = "failed"

    operation = Operation.objects.create(
        user_id=user_id or "",
        status=status,
        total_items=len(journal),
        successful_items=executed,
        failed_items=failed,
    )
    for entry in journal:
        OperationItem.objects.create(
            operation=operation,
            item_index=entry.index,
            source_path=entry.source,
            target_path=entry.target,
            action=entry.action,
            status=entry.status,
            pre_state=entry.pre_state or {},
            post_state=entry.post_state or {},
            error_message=entry.error or "",
        )
