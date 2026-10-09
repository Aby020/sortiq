"""PathGuard: safe path validation and containment for sortiq_fs.

Rejects traversal outside a managed root, unsafe drive/UNC usage, and
non-normalized segments. Pure Python; no Django imports.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PathCheckResult:
    ok: bool
    reason: str
    resolved: str


_WINDOWS_RESERVED = {
    "con",
    "prn",
    "aux",
    "nul",
    "com1",
    "com2",
    "com3",
    "com4",
    "com5",
    "com6",
    "com7",
    "com8",
    "com9",
    "lpt1",
    "lpt2",
    "lpt3",
    "lpt4",
    "lpt5",
    "lpt6",
    "lpt7",
    "lpt8",
    "lpt9",
}


def _is_windows_reserved(name: str) -> bool:
    stem = name.split(".")[0].lower()
    return stem in _WINDOWS_RESERVED


def normalize(path: str) -> str:
    unified = path.replace("\\", "/")
    absolute = unified.startswith("/")
    parts: list[str] = []
    for segment in unified.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if parts:
                parts.pop()
            continue
        if len(segment) == 2 and segment[1] == ":":
            segment = segment[0].upper() + ":"
        parts.append(segment)
    joined = "/".join(parts)
    return "/" + joined if absolute else joined


def join(root: str, *segments: str) -> str:
    base = normalize(root)
    return normalize("/".join([base, *segments]))


def is_within(root: str, candidate: str) -> bool:
    root_norm = normalize(root)
    cand_norm = normalize(candidate)
    if root_norm == "":
        return True
    if root_norm == "/":
        return True
    if cand_norm == root_norm:
        return True
    return cand_norm.startswith(root_norm.rstrip("/") + "/")


def validate(root: str, candidate: str) -> PathCheckResult:
    root_norm = normalize(root)
    cand_norm = normalize(candidate)

    if not is_within(root_norm, cand_norm):
        return PathCheckResult(
            ok=False,
            reason="path escapes managed root",
            resolved=cand_norm,
        )

    if cand_norm.startswith("//") or cand_norm.startswith("\\\\"):
        return PathCheckResult(
            ok=False,
            reason="UNC paths are not permitted",
            resolved=cand_norm,
        )

    if len(cand_norm) > 1 and cand_norm[1] == ":":
        drive = cand_norm[0].upper()
        if drive not in ("C", "D", "E", "F"):
            return PathCheckResult(
                ok=False,
                reason=f"drive {drive}: is not permitted",
                resolved=cand_norm,
            )

    for segment in cand_norm.split("/"):
        if segment and _is_windows_reserved(segment):
            return PathCheckResult(
                ok=False,
                reason=f"reserved device name: {segment}",
                resolved=cand_norm,
            )

    return PathCheckResult(ok=True, reason="", resolved=cand_norm)


def relative(root: str, target: str) -> str:
    root_norm = normalize(root)
    target_norm = normalize(target)
    if not is_within(root_norm, target_norm):
        raise ValueError("target is outside root")
    if target_norm == root_norm:
        return ""
    prefix = root_norm.rstrip("/")
    if target_norm.startswith(prefix + "/"):
        return target_norm[len(prefix) + 1 :]
    return target_norm[len(prefix) :]
