"""WAL-style journal engine with stat-before-act verification.

Hardening:
- All file mutations are wrapped for Windows-specific failures
  (``PermissionError``, ``FileNotFoundError``, ``OSError``) so a
  single locked file never crashes the engine thread.
- ``delete`` actions are routed through the safe quarantine layer
  (Recycle Bin first, local ``.sortiq_quarantine`` fallback).
  Permanent deletion is never performed.
"""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from sortiq_fs.pathguard import is_blacklisted, normalize
from sortiq_fs.quarantine import safe_delete

logger = logging.getLogger(__name__)

Status = Literal["pending", "running", "completed", "failed", "partially_completed"]

# Windows error codes that mean "file is locked / in use".
_WINDOWS_LOCKED_HRESULT = {32, 33}


@dataclass
class JournalEntry:
    index: int
    source: str
    target: str
    action: str
    status: str
    error: str | None = None
    pre_state: dict[str, Any] = None  # noqa: RUF012
    post_state: dict[str, Any] = None  # noqa: RUF012


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


def _is_locked(exc: Exception) -> bool:
    """Detect Windows sharing-violation (file open in another process)."""

    winerror = getattr(exc, "winerror", None)
    if winerror in _WINDOWS_LOCKED_HRESULT:
        return True
    if hasattr(exc, "hresult"):
        try:
            return (exc.hresult & 0xFFFF) in _WINDOWS_LOCKED_HRESULT
        except (TypeError, ValueError):
            pass
    return False


def _apply(item: JournalEntry) -> None:
    source_norm = normalize(item.source)
    target_norm = normalize(item.target)

    if is_blacklisted(source_norm):
        raise PermissionError(
            f"refusing to mutate protected system path: {source_norm}"
        )

    target_parent = Path(item.target).parent
    target_parent.mkdir(parents=True, exist_ok=True)

    if item.action == "move":
        shutil.move(item.source, item.target)
    elif item.action == "copy":
        shutil.copy2(item.source, item.target)
    elif item.action == "quarantine":
        shutil.move(item.source, item.target)
    elif item.action == "delete":
        # Never hard-delete: route through the Recycle Bin / local quarantine.
        safe_delete(item.source)
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
        except (PermissionError, FileNotFoundError, OSError) as exc:
            if _is_locked(exc):
                entry.status = "failed"
                entry.error = f"file is locked or in use: {exc}"
                logger.warning(
                    "operation skipped (locked file): %s — %s",
                    entry.source,
                    exc,
                )
            else:
                entry.status = "failed"
                entry.error = f"{type(exc).__name__}: {exc}"
                logger.warning(
                    "operation failed (OS error): %s — %s",
                    entry.source,
                    exc,
                )
            metrics["failed"] += 1
            continue
        except Exception as exc:  # pragma: no cover - defensive
            entry.status = "failed"
            entry.error = f"{type(exc).__name__}: {exc}"
            logger.exception("unexpected operation failure on %s", entry.source)
            metrics["failed"] += 1
            continue

        if on_progress:
            on_progress(idx + 1, len(plan.items))

    if persist:
        _persist_journal(journal, journal_path, user_id=user_id)
    return metrics


def _persist_journal(journal: list[JournalEntry], path: str, user_id: str | None = None) -> None:
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
