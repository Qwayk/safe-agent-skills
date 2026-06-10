from __future__ import annotations

import json
from typing import Any

from .errors import ToolError
from .http import HttpClient


class StatuspageClient:
    def __init__(self, *, base_url: str, timeout_s: float, verbose: bool, user_agent: str):
        self._base_url = base_url.rstrip("/")
        self._http = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent=user_agent)

    def _get_json(self, path: str) -> Any:
        url = f"{self._base_url}{path}"
        try:
            resp = self._http.request("GET", url)
        except RuntimeError as e:
            raise ToolError(str(e)) from e
        try:
            return resp.json()
        except json.JSONDecodeError as e:
            body_preview = resp.text()[:500]
            raise ToolError(f"Invalid JSON from {resp.url}: {e}. Body starts with: {body_preview!r}") from e

    def get_status(self) -> Any:
        return self._get_json("/api/v2/status.json")

    def get_summary(self) -> Any:
        return self._get_json("/api/v2/summary.json")

    def list_incidents(self) -> Any:
        return self._get_json("/api/v2/incidents.json")

    def list_scheduled_maintenances(self) -> Any:
        return self._get_json("/api/v2/scheduled-maintenances.json")
