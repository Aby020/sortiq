"""Rollback engine preserving audit history."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from apps.operations.models import Operation


@dataclass
class RollbackResult:
    operation_id: str
    restored: int
    failed: int
    preserved_journal: bool


def rollback_operation(operation_id: str) -> RollbackResult:
    operation = Operation.objects.get(id=operation_id)
    restored = 0
    failed = 0

    for item in operation.items.all():
        if item.status != "success":
            continue
        try:
            target_parent = Path(item.source_path).parent
            target_parent.mkdir(parents=True, exist_ok=True)
            shutil.move(item.target_path, item.source_path)
            restored += 1
        except Exception:
            failed += 1

    operation.status = "rolled_back"
    operation.save(update_fields=["status"])

    return RollbackResult(
        operation_id=operation_id,
        restored=restored,
        failed=failed,
        preserved_journal=True,
    )
