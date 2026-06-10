from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from youtube_api_tool.cli import main


class _Creds:
    def to_json(self) -> str:  # noqa: D401
        # Intentionally contains secret-bearing fields; the command must not print them.
        return json.dumps(
            {
                "token": "SECRET_ACCESS_TOKEN",
                "refresh_token": "SECRET_REFRESH_TOKEN",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "CID",
                "client_secret": "CSECRET",
                "scopes": ["https://www.googleapis.com/auth/youtube"],
            }
        )


class _Flow:
    def run_console(self):  # noqa: ANN001
        return _Creds()


class TestAuthLogin(unittest.TestCase):
    def test_auth_login_apply_refuses_without_running_flow_or_writing_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            client_secrets = Path(d) / "client_secrets.json"
            client_secrets.write_text("{}", encoding="utf-8")

            buf = io.StringIO()
            with patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file", return_value=_Flow()) as mock_flow:
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_file),
                            "--apply",
                            "auth",
                            "login",
                            "--console",
                            "--client-secrets-file",
                            str(client_secrets),
                        ]
                    )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload["verification_plan"]["status"], "best_effort_after_apply")
            self.assertNotIn("SECRET_ACCESS_TOKEN", buf.getvalue())
            self.assertNotIn("SECRET_REFRESH_TOKEN", buf.getvalue())
            self.assertFalse(mock_flow.called)

            token_path = Path(d) / ".state" / "token.json"
            self.assertFalse(token_path.exists())
