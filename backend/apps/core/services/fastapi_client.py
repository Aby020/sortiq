"""Internal FastAPI client for Django-to-service communication."""

from __future__ import annotations

import os
from typing import Any

import requests

FASTAPI_INTERNAL_URL = os.environ.get("FASTAPI_INTERNAL_URL", "http://localhost:8100")
INTERNAL_SERVICE_TOKEN = os.environ.get("INTERNAL_SERVICE_TOKEN", "change-me")


class FastAPIClient:
    def __init__(self, base_url: str = FASTAPI_INTERNAL_URL) -> None:
        self.base_url = base_url

    def _headers(self) -> dict[str, str]:
        return {"X-Internal-Service-Token": INTERNAL_SERVICE_TOKEN}

    def health(self) -> dict[str, Any]:
        r = requests.get(f"{self.base_url}/internal/health", headers=self._headers(), timeout=5)
        r.raise_for_status()
        return r.json()

    def scan_stream(self, folder_id: str) -> dict[str, Any]:
        r = requests.get(
            f"{self.base_url}/internal/scan-stream",
            headers={**self._headers(), "X-Folder-ID": folder_id},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def hash_batch(self, paths: list[str]) -> dict[str, Any]:
        r = requests.post(
            f"{self.base_url}/internal/hash-batch",
            headers=self._headers(),
            json={"paths": paths},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()


fastapi_client = FastAPIClient()
