"""Rule evaluator with conditions, priorities, dry-run."""

from __future__ import annotations

import re
from typing import Any

from django.db import models


def _match_extension(file_obj: Any, value: list[str]) -> bool:
    return file_obj.name.split(".")[-1].lower() in [v.lower() for v in value]


def _match_size(file_obj: Any, op: str, value: int) -> bool:
    size = getattr(file_obj, "size_bytes", getattr(file_obj, "st_size", 0))
    if op == "gt":
        return size > value
    if op == "lt":
        return size < value
    return False


def _match_name_pattern(file_obj: Any, value: str) -> bool:
    return bool(re.search(value, file_obj.name))


def _match_category(file_obj: Any, value: str) -> bool:
    cat = getattr(file_obj, "category", None)
    return cat is not None and (
        getattr(cat, "slug", None) == value or str(getattr(cat, "name", "")) == value
    )


def _match_directory_name(file_obj: Any, value: str) -> bool:
    path = getattr(file_obj, "canonical_path", getattr(file_obj, "relative_path", ""))
    return value.lower() in path.lower()


def evaluate_conditions(file_obj: Any, conditions: dict[str, Any]) -> bool:
    if not conditions:
        return True
    results = []
    if "extension" in conditions:
        results.append(_match_extension(file_obj, conditions["extension"]))
    if "size_gt" in conditions:
        results.append(_match_size(file_obj, "gt", conditions["size_gt"]))
    if "size_lt" in conditions:
        results.append(_match_size(file_obj, "lt", conditions["size_lt"]))
    if "name_pattern" in conditions:
        results.append(_match_name_pattern(file_obj, conditions["name_pattern"]))
    if "category" in conditions:
        results.append(_match_category(file_obj, conditions["category"]))
    if "directory_name" in conditions:
        results.append(_match_directory_name(file_obj, conditions["directory_name"]))
    return all(results)


def evaluate_rule(rule: Any, files: models.QuerySet) -> list[int]:
    matched = []
    for f in files:
        if evaluate_conditions(f, getattr(rule, "conditions", {}) or {}):
            matched.append(getattr(f, "id", f))
    return matched


def dry_run(rule: Any, files: models.QuerySet) -> dict[str, Any]:
    matched_ids = evaluate_rule(rule, files)
    return {
        "count": len(matched_ids),
        "matched_ids": matched_ids,
        "rule_id": str(getattr(rule, "id", None)),
    }
