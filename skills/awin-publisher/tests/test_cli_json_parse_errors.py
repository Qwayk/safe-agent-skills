from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from typing import Any
from unittest.mock import patch

import requests

from awin_publisher_safe_agent_cli.cli import main


class TestCliJsonParseErrors(unittest.TestCase):
    def test_missing_command_is_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_missing_required_subcommand_is_json_error(self) -> None:
        # `auth` requires a subcommand.
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "auth"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("awin_publisher_safe_agent_cli.http.requests.Session.request")
    def test_auth_failure_does_not_leak_awin_token_in_json(self, mocked_request) -> None:
        token = "AWIN_TOKEN_SHOULD_NOT_LEAK_123"

        def fake_request(
            self,
            method: str,
            url: str,
            headers: dict[str, str] | None = None,
            params: dict[str, Any] | None = None,
            **kwargs: Any
        ) -> requests.Response:
            response = requests.Response()
            response.status_code = 401
            response._content = b'{"error":"unauthorized"}'
            response.headers["content-type"] = "application/json"
            response.url = requests.Request(method=method, url=url, params=params).prepare().url or url
            return response

        mocked_request.side_effect = fake_request

        with tempfile.TemporaryDirectory() as td:
            env_file = os.path.join(td, ".env")
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"AWIN_API_TOKEN={token}\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_file, "auth", "check"])

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        raw = json.dumps(payload)
        self.assertNotIn(token, raw)
        self.assertNotIn(token, payload["error"])
