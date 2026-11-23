from __future__ import annotations

import json
from typing import Any

from .errors import ToolError
from .http import HttpClient


def _is_item_id(value: object) -> bool:
    return type(value) is int and value > 0


def _is_item_id_list(value: object) -> bool:
    return isinstance(value, list) and all(_is_item_id(item_id) for item_id in value)


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
        data = self._get_json(f"/item/{item_id}.json")
        if data is None:
            return None
        if not isinstance(data, dict) or not _is_item_id(data.get("id")) or data["id"] != item_id:
            raise ToolError(f"Hacker News returned an unexpected reply for item {item_id}.")
        return data

    def get_user(self, user_id: str) -> Any:
        data = self._get_json(f"/user/{user_id}.json")
        if data is None:
            return None
        if not isinstance(data, dict) or data.get("id") != user_id:
            raise ToolError(f"Hacker News returned an unexpected reply for user {user_id!r}.")
        return data

    def get_stories(self, story_type: str) -> Any:
        data = self._get_json(f"/{story_type}stories.json")
        if not _is_item_id_list(data):
            raise ToolError(f"Hacker News returned an unexpected reply for the {story_type} story list.")
        return data

    def get_maxitem(self) -> Any:
        data = self._get_json("/maxitem.json")
        if not _is_item_id(data):
            raise ToolError("Hacker News did not return a valid latest item ID.")
        return data

    def get_updates(self) -> Any:
        data = self._get_json("/updates.json")
        if not isinstance(data, dict) or not _is_item_id_list(data.get("items")):
            raise ToolError("Hacker News returned an unexpected reply for recent updates.")
        profiles = data.get("profiles")
        if not isinstance(profiles, list) or not all(isinstance(name, str) for name in profiles):
            raise ToolError("Hacker News returned an unexpected profile list for recent updates.")
        return data
