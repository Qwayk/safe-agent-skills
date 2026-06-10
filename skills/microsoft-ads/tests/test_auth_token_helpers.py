from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from msads_api_tool.cli import main


class _FakeResp:
    def __init__(self, *, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self.text = json.dumps(payload)


class TestAuthTokenHelpers(unittest.TestCase):
    def test_auth_token_show_redacts_access_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("MSADS_ENVIRONMENT=prod\n", encoding="utf-8")
            tok_path = Path(d) / ".state" / "token.json"
            tok_path.parent.mkdir(parents=True, exist_ok=True)
            tok_path.write_text(
                json.dumps({"access_token": "secret-access", "refresh_token": "secret-refresh"}, indent=2) + "\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "token", "show"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["token"]["access_token"], "***REDACTED***")
            self.assertNotIn("secret-access", buf.getvalue())
            self.assertNotIn("secret-refresh", buf.getvalue())

    def test_auth_token_refresh_requires_live(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("MSADS_OAUTH_CLIENT_ID=cid\nMSADS_ENVIRONMENT=prod\n", encoding="utf-8")
            tok_path = Path(d) / ".state" / "token.json"
            tok_path.parent.mkdir(parents=True, exist_ok=True)
            tok_path.write_text(json.dumps({"refresh_token": "secret-refresh"}) + "\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "token", "refresh"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    @patch("msads_api_tool.commands.auth.requests.post")
    def test_auth_token_refresh_never_prints_token_values(self, post) -> None:  # noqa: ANN001
        post.return_value = _FakeResp(
            status_code=200,
            payload={"access_token": "new-access", "refresh_token": "new-refresh", "expires_in": 3600},
        )
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "MSADS_ENVIRONMENT=prod",
                        "MSADS_OAUTH_CLIENT_ID=cid",
                        "MSADS_OAUTH_TENANT=common",
                        "MSADS_OAUTH_SCOPE=https://ads.microsoft.com/msads.manage offline_access",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            tok_path = Path(d) / ".state" / "token.json"
            tok_path.parent.mkdir(parents=True, exist_ok=True)
            tok_path.write_text(json.dumps({"refresh_token": "old-refresh"}) + "\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--live", "--env-file", str(env_path), "auth", "token", "refresh"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["token_refreshed"])
            self.assertNotIn("new-access", buf.getvalue())
            self.assertNotIn("new-refresh", buf.getvalue())

            written = json.loads(tok_path.read_text(encoding="utf-8"))
            self.assertEqual(written["access_token"], "new-access")
            self.assertEqual(written["refresh_token"], "new-refresh")

