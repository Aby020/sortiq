"""Operation plan builder with conflict detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Action = Literal["move", "copy", "quarantine", "delete"]


@dataclass
class PlanItem:
    source_path: str
    target_path: str
    action: Action


@dataclass
class OperationPlan:
    items: list[PlanItem] = field(default_factory=list)
    conflict_count: int = 0
    has_conflicts: bool = False

    def add(self, source: str, target: str, action: Action) -> PlanItem:
        self.items.append(PlanItem(source_path=source, target_path=target, action=action))
        return self.items[-1]

    def detect_conflicts(self) -> list[tuple[int, int]]:
        seen: dict[str, int] = {}
        conflicts: list[tuple[int, int]] = []
        for idx, item in enumerate(self.items):
            key = item.target_path
            if key in seen:
                conflicts.append((seen[key], idx))
            else:
                seen[key] = idx
        self.conflict_count = len(conflicts)
        self.has_conflicts = self.conflict_count > 0
        return conflicts
