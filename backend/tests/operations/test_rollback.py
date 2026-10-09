"""Rollback tests preserving audit history using ORM + tmp_path."""

from __future__ import annotations

from pathlib import Path

import pytest
from apps.authentication.models import User
from apps.operations.engine import execute_plan
from apps.operations.models import Operation
from apps.operations.plan import OperationPlan
from apps.operations.rollback import rollback_operation


@pytest.mark.django_db
class TestRollback:
    def test_rollback_restores_moved_file(self, tmp_path: Path) -> None:
        user = User.objects.create_user(username="rb", email="rb@test.local", password="p")
        src = tmp_path / "src.txt"
        src.write_text("content")
        dest = tmp_path / "dest.txt"
        plan = OperationPlan()
        plan.add(str(src), str(dest), "move")
        execute_plan(
            plan,
            str(tmp_path / "j.json"),
            verify=True,
            persist=True,
            user_id=str(user.id),
        )
        # retrieve operation
        op = Operation.objects.filter(user=user).last()
        assert op is not None
        # rollback
        result = rollback_operation(str(op.id))
        assert result.restored == 1
        assert result.failed == 0
        assert result.preserved_journal is True
        assert not dest.exists()
        assert src.exists()
        assert src.read_text() == "content"
        op.refresh_from_db()
        assert op.status == "rolled_back"
        # journal preserved
        assert op.items.count() == 1

    def test_rollback_preserves_failed_items_unchanged(self, tmp_path: Path) -> None:
        user = User.objects.create_user(username="rb2", email="rb2@test.local", password="p")
        src = tmp_path / "ok.txt"
        src.write_text("ok")
        plan = OperationPlan()
        plan.add(str(src), str(tmp_path / "ok_dest.txt"), "move")
        execute_plan(
            plan,
            str(tmp_path / "j.json"),
            verify=True,
            persist=True,
            user_id=str(user.id),
        )
        op = Operation.objects.filter(user=user).last()
        result = rollback_operation(str(op.id))
        assert result.restored == 1
        assert op.items.filter(status="success").count() == 1
