from __future__ import annotations

import json
from typing import Any

from .errors import ToolError
from .http import HttpClient


class StatuspageClient:
    def __init__(self, *, base_url: str, timeout_s: float, verbose: bool, user_agent: str):
        self._base_url = base_url.rstrip("/")
        self._http = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent=user_agent)

    def _get_json(self, path: str, *, status: bool = False, lists: tuple[str, ...] = ()) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            resp = self._http.request("GET", url)
        except RuntimeError as e:
            raise ToolError(str(e)) from e
        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            body_preview = resp.text()[:500]
            raise ToolError(f"Invalid JSON from {resp.url}: {e}. Body starts with: {body_preview!r}") from e

        if not isinstance(data, dict):
            raise ToolError(f"Expected a JSON object from {url}")
        if status:
            page_status = data.get("status")
            indicator = page_status.get("indicator") if isinstance(page_status, dict) else None
            if not isinstance(indicator, str) or not indicator.strip():
                raise ToolError(f"Missing or invalid status indicator in the response from {url}")
        for name in lists:
            if not isinstance(data.get(name), list):
                raise ToolError(f"Missing or invalid '{name}' list in the response from {url}")
        return data

    def get_status(self) -> dict[str, Any]:
        return self._get_json("/api/v2/status.json", status=True)

    def get_summary(self) -> dict[str, Any]:
        return self._get_json(
            "/api/v2/summary.json", status=True, lists=("incidents", "scheduled_maintenances")
        )

    def list_incidents(self) -> dict[str, Any]:
        return self._get_json("/api/v2/incidents.json", lists=("incidents",))

    def list_scheduled_maintenances(self) -> dict[str, Any]:
        return self._get_json("/api/v2/scheduled-maintenances.json", lists=("scheduled_maintenances",))
