from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from linkedin_ads_api_tool.cli import main
from linkedin_ads_api_tool.http import HttpClient


class _FakeResponse:
    def __init__(self, status: int, payload: dict | None = None, raw: str | None = None) -> None:
        self.status = status
        self._payload = payload if payload is not None else {}
        self._raw = raw if raw is not None else ""

    def json(self) -> dict:
        return self._payload

    def text(self) -> str:
        return self._raw


class TestAuthCommands(unittest.TestCase):
    def test_auth_check_success_with_live_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("LINKEDIN_ADS_TOKEN=TOKEN_OK\n", encoding="utf-8")

            with patch.object(
                HttpClient,
                "request",
                return_value=_FakeResponse(status=200, payload={"elements": [{"id": "a"}]}, raw='{"elements":[{"id":"a"}]}'),
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "--output", "json", "auth", "check"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["auth_check"]["status"], 200)
            self.assertEqual(payload["auth_check"]["authenticated_users_count"], 1)

    def test_auth_check_missing_or_invalid_token_does_not_leak_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("LINKEDIN_ADS_TOKEN=SECRET_TOKEN_123\n", encoding="utf-8")

            with patch.object(HttpClient, "request", side_effect=RuntimeError("request failed")):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "--output", "json", "auth", "check"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "RuntimeError")
            self.assertNotIn("SECRET_TOKEN_123", buf.getvalue())

    def test_auth_token_set_and_status_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            token_src = Path(d) / "oauth_token.json"
            token_src.write_text(
                json.dumps(
                    {
                        "access_token": "TOKEN_FROM_FILE",
                        "refresh_token": "REFRESH_FROM_FILE",
                        "scope": "r_liteprofile",
                    }
                ),
                encoding="utf-8",
            )

            set_buf = io.StringIO()
            with redirect_stdout(set_buf):
                set_rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "auth",
                        "token",
                        "set",
                        "--file",
                        str(token_src),
                    ]
                )
            self.assertEqual(set_rc, 0)
            set_payload = json.loads(set_buf.getvalue())
            self.assertTrue(set_payload["ok"])

            status_buf = io.StringIO()
            with redirect_stdout(status_buf):
                status_rc = main(["--env-file", str(env_path), "--output", "json", "auth", "token", "status"])
            self.assertEqual(status_rc, 0)
            status_payload = json.loads(status_buf.getvalue())
            self.assertTrue(status_payload["ok"])
            self.assertTrue(status_payload["token_status"]["exists"])
            self.assertEqual(status_payload["token_status"]["fields"], ["access_token", "refresh_token", "scope"])
