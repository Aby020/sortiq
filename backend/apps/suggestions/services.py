"""Suggestion generator & plan preparation bridge."""

from __future__ import annotations

from typing import Any

from apps.rules.evaluator import evaluate_conditions
from apps.rules.models import OrganizationRule


class SuggestionService:
    def __init__(self, user: Any) -> None:
        self.user = user

    def generate_for_file(self, file_obj: Any) -> list[dict[str, Any]]:
        rules = OrganizationRule.objects.filter(user=self.user, is_active=True).order_by("priority")
        out = []
        for rule in rules:
            if evaluate_conditions(file_obj, rule.conditions or {}):
                out.append(
                    {
                        "rule_id": str(rule.id),
                        "rule_name": rule.name,
                        "file_id": str(getattr(file_obj, "id", "")),
                        "proposed_action": (rule.actions or {}).get("type", "move_to_category"),
                        "priority": rule.priority,
                    }
                )
                break
        return out
