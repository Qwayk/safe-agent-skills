from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from qwayk_pipedrive_safe_agent_cli.cli import main


class _Response:
    def __init__(self, status: int, body: dict[str, object], headers: dict[str, str] | None = None, url: str = "https://api.test.pipedrive.com") -> None:
        self.status = status
        self.headers = headers or {}
        self.body = json.dumps(body).encode("utf-8")
        self.url = url

    def json(self) -> object:
        return json.loads(self.body.decode("utf-8"))


class _HttpClient:
    def __init__(self, responses: list[_Response]):
        self._responses = list(responses)
        self.requests: list[tuple[str, str, dict[str, str] | None, dict[str, object] | None]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, object] | None = None,
        **kwargs: object,
    ) -> _Response:
        self.requests.append((method, url, headers, params))
        return self._responses.pop(0)


def _write_env(path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("PIPEDRIVE_API_DOMAIN=test-company\n")
        f.write("PIPEDRIVE_API_TOKEN=token-xyz\n")


class TestPagination(unittest.TestCase):
    def test_cursor_pagination_uses_next_cursor(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            _write_env(env_path)

            client = _HttpClient(
                [
                    _Response(200, {"data": [{"id": 1}], "additional_data": {"next_cursor": "c-2", "more_items_in_collection": True}}),
                    _Response(200, {"data": [{"id": 2}], "additional_data": {"more_items_in_collection": False}}),
                ]
            )

            buf = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", return_value=client):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "activities",
                            "list",
                            "--max-pages",
                            "2",
                        ]
                    )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["pagination"]["mode"], "cursor")
            self.assertEqual(payload["pagination"]["requested_pages"], 2)
            self.assertEqual(payload["pagination"]["fetched_pages"], 2)
            self.assertFalse(payload["pagination"]["has_more"])
            self.assertEqual(client.requests[1][3].get("cursor"), "c-2")

    def test_offset_pagination_uses_next_start(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            _write_env(env_path)

            client = _HttpClient(
                [
                    _Response(200, {"data": [{"id": 1}], "additional_data": {"pagination": {"more_items_in_collection": True, "next_start": 5}, "more_items_in_collection": True}}),
                    _Response(200, {"data": [{"id": 2}], "additional_data": {"pagination": {"more_items_in_collection": False, "next_start": 10}, "more_items_in_collection": False}}),
                ]
            )

            buf = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", return_value=client):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "call-logs",
                            "list",
                            "--max-pages",
                            "2",
                            "--limit",
                            "5",
                        ]
                    )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["pagination"]["mode"], "offset")
            self.assertEqual(payload["pagination"]["requested_pages"], 2)
            self.assertEqual(payload["pagination"]["fetched_pages"], 2)
            self.assertEqual(payload["pagination"]["has_more"], False)
            self.assertEqual(client.requests[1][3].get("start"), 5)
