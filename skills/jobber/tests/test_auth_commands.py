from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from jobber_safe_agent_cli.cli import main


class _FakeAuthClient:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def execute(self, query: str, variables=None) -> dict:
        return {"data": {"account": {"__typename": "Account"}}, "errors": None}


class _FakeTokenHttp:
    calls: list[dict] = []

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def request(self, **kwargs):
        self.calls.append(kwargs)

        class _Response:
            def json(self):
                return {"access_token": "new-access", "refresh_token": "new-refresh", "expires_in": 3600}

        return _Response()


class TestAuthCommands(unittest.TestCase):
    def test_auth_check_safe_without_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("JOBBER_API_BASE_URL=http://example.invalid\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env), "--output", "json", "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["missing_token"])
            self.assertFalse(payload["token_available"])

    def test_auth_check_uses_stored_token_or_env_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("JOBBER_API_BASE_URL=http://example.invalid\nJOBBER_API_TOKEN=env-token\n", encoding="utf-8")

            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.auth.GraphQLClient", _FakeAuthClient):
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env), "--output", "json", "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["token_available"])
            self.assertEqual(payload["account_probe"], {"account": {"__typename": "Account"}})

    def test_authorize_url_command(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text(
                "\n".join(["JOBBER_API_BASE_URL=http://example.invalid", "JOBBER_CLIENT_ID=abc"])
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env), "--output", "json", "auth", "authorize-url"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["command"], "auth.authorize_url")
            self.assertIn("http://example.invalid/api/oauth/authorize", payload["authorize_url"])
            self.assertNotIn("scope=read", payload["authorize_url"])

    def test_token_refresh_uses_form_encoding_and_never_prints_tokens(self) -> None:
        _FakeTokenHttp.calls = []
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text(
                "\n".join(
                    [
                        "JOBBER_API_BASE_URL=http://example.invalid",
                        "JOBBER_CLIENT_ID=client-id",
                        "JOBBER_CLIENT_SECRET=client-secret",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.auth.HttpClient", _FakeTokenHttp):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env),
                            "--output",
                            "json",
                            "--apply",
                            "--yes",
                            "auth",
                            "token",
                            "refresh",
                            "--refresh-token",
                            "old-refresh",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["received"]["has_access_token"], True)
            self.assertNotIn("new-access", buf.getvalue())
            self.assertNotIn("new-refresh", buf.getvalue())
            self.assertEqual(_FakeTokenHttp.calls[0]["headers"]["Content-Type"], "application/x-www-form-urlencoded")
            self.assertEqual(_FakeTokenHttp.calls[0]["data"]["grant_type"], "refresh_token")
            self.assertNotIn("json_body", _FakeTokenHttp.calls[0])
