"""Rule evaluator tests."""

from __future__ import annotations

import pytest
from apps.rules.evaluator import (
    dry_run,
    evaluate_conditions,
)
from apps.rules.models import OrganizationRule


class FakeFile:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


@pytest.mark.django_db
def test_evaluate_conditions_extension() -> None:
    f = FakeFile(name="archive.iso")
    assert evaluate_conditions(f, {"extension": ["iso", "dmg"]}) is True
    assert evaluate_conditions(f, {"extension": ["txt"]}) is False


def test_evaluate_size_gt_lt() -> None:
    f = FakeFile(name="big.bin", size_bytes=5000)
    assert evaluate_conditions(f, {"size_gt": 1000}) is True
    assert evaluate_conditions(f, {"size_lt": 10000}) is True


def test_dry_run_accuracy() -> None:
    rule = OrganizationRule(
        name="test",
        conditions={"extension": ["pdf"]},
        actions={"type": "tag"},
        priority=1,
        user_id="dummy",
    )
    fake_files = [FakeFile(name="a.pdf"), FakeFile(name="b.txt")]
    files = type("Q", (), {"__iter__": lambda s: iter(fake_files)})()
    res = dry_run(rule, files)
    assert res["count"] == 1
    assert len(res["matched_ids"]) == 1
