"""Phase 5: Duplicate detection pipeline (size grouping -> partial -> full SHA-256)."""

from __future__ import annotations

from collections import defaultdict


def group_by_size(files: list[dict]) -> dict[int, list[dict]]:
    groups: dict[int, list[dict]] = defaultdict(list)
    for f in files:
        groups[f.get("size_bytes", 0)].append(f)
    return {k: v for k, v in groups.items() if len(v) > 1}


def group_partial_hash(files: list[dict], partial_size: int = 1024) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for f in files:
        partial = f.get("partial_hash") or ""
        if partial:
            groups[partial].append(f)
    return {k: v for k, v in groups.items() if len(v) > 1}


def group_full_sha(files: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for f in files:
        sha = f.get("sha256") or ""
        if sha:
            groups[sha].append(f)
    return {k: v for k, v in groups.items() if len(v) > 1}
