"""Staged content hasher with partial-hash support.

Computes a partial (prefix) hash and a full SHA-256 in bounded stages.
Pure Python; no Django imports.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import BinaryIO

PARTIAL_SIZE = 1024 * 1024
STAGE_CHUNK = 1024 * 1024


@dataclass(frozen=True)
class HashResult:
    sha256: str
    partial_hash: str
    stage: str


def hash_file(path: str, *, partial_size: int = PARTIAL_SIZE) -> HashResult:
    hasher = hashlib.sha256()
    partial_hasher = hashlib.sha256()
    bytes_hashed = 0

    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(STAGE_CHUNK)
            if not chunk:
                break
            hasher.update(chunk)
            if bytes_hashed < partial_size:
                remaining = partial_size - bytes_hashed
                partial_hasher.update(chunk[:remaining])
            bytes_hashed += len(chunk)

    stage = "full" if bytes_hashed > 0 else "none"
    return HashResult(
        sha256=hasher.hexdigest(),
        partial_hash=partial_hasher.hexdigest(),
        stage=stage,
    )


def hash_stream(handle: BinaryIO, *, partial_size: int = PARTIAL_SIZE) -> HashResult:
    hasher = hashlib.sha256()
    partial_hasher = hashlib.sha256()
    bytes_hashed = 0

    while True:
        chunk = handle.read(STAGE_CHUNK)
        if not chunk:
            break
        hasher.update(chunk)
        if bytes_hashed < partial_size:
            remaining = partial_size - bytes_hashed
            partial_hasher.update(chunk[:remaining])
        bytes_hashed += len(chunk)

    stage = "full" if bytes_hashed > 0 else "none"
    return HashResult(
        sha256=hasher.hexdigest(),
        partial_hash=partial_hasher.hexdigest(),
        stage=stage,
    )
