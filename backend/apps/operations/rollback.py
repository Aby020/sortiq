"""Rollback engine preserving audit history."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from apps.operations.models import Operation
from sortiq_fs.pathguard import is_blacklisted, normalize

logger = logging.getLogger(__name__)


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
            source_norm = normalize(item.source_path)
            if is_blacklisted(source_norm):
                logger.warning("rollback blocked for protected path: %s", source_norm)
                failed += 1
                continue

            target_parent = Path(item.source_path).parent
            target_parent.mkdir(parents=True, exist_ok=True)
            shutil.move(item.target_path, item.source_path)
            restored += 1
        except (PermissionError, FileNotFoundError, OSError) as exc:
            logger.warning("rollback failed for %s: %s", item.source_path, exc)
            failed += 1
        except Exception as exc:  # pragma: no cover
            logger.exception("rollback unexpected error on %s", item.source_path)
            failed += 1

    operation.status = "rolled_back"
    operation.save(update_fields=["status"])

    return RollbackResult(
        operation_id=operation_id,
        restored=restored,
        failed=failed,
        preserved_journal=True,
    )
