from __future__ import annotations

import json
from typing import Any

from .errors import ToolError
from .http import HttpClient


class HackerNewsClient:
    def __init__(self, *, api_root: str, timeout_s: float, verbose: bool, user_agent: str):
        self._api_root = api_root.rstrip("/")
        self._http = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent=user_agent)

    def _get_json(self, path: str) -> Any:
        url = f"{self._api_root}{path}"
        try:
            resp = self._http.request("GET", url)
        except RuntimeError as e:
            raise ToolError(str(e)) from e
        try:
            return resp.json()
        except json.JSONDecodeError as e:
            body_preview = resp.text()[:500]
            raise ToolError(f"Invalid JSON from {resp.url}: {e}. Body starts with: {body_preview!r}") from e

    def get_item(self, item_id: int) -> Any:
        return self._get_json(f"/item/{item_id}.json")

    def get_user(self, user_id: str) -> Any:
        return self._get_json(f"/user/{user_id}.json")

    def get_stories(self, story_type: str) -> Any:
        return self._get_json(f"/{story_type}stories.json")

    def get_maxitem(self) -> Any:
        return self._get_json("/maxitem.json")

    def get_updates(self) -> Any:
        return self._get_json("/updates.json")
