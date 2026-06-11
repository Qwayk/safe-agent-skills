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


class TestGeneratedCommandDispatch(unittest.TestCase):
    def test_preferred_v2_entry_is_used_without_api_version_flag(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            _write_env(env_path)
            client = _HttpClient([_Response(200, {"data": []})])

            buf = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", return_value=client):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "project-boards", "list"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["api_version"], "v2")
            self.assertIn("operation", payload)

    def test_dotted_query_flags_round_trip_to_request_keys(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            _write_env(env_path)
            client = _HttpClient([_Response(200, {"data": []})])

            buf = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", return_value=client):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "goals",
                            "search",
                            "--type-name",
                            "deals_won",
                        ]
                    )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertIn("type.name", payload["request"]["query"])
            self.assertEqual(payload["request"]["query"]["type.name"], "deals_won")

    def test_path_parameter_is_replaced_and_required(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            _write_env(env_path)
            client = _HttpClient([_Response(200, {"data": {}})])

            buf = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", return_value=client):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "activities", "get", "--id", "77"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["request"]["path"], "/activities/77")
            self.assertFalse(payload["pagination"]["has_more"])
