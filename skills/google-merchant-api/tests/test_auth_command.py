from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from google_merchant_api_tool.cli import main


class TestAuthCommand(unittest.TestCase):
    def test_auth_check_reports_missing_service_account_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "GOOGLE_MERCHANT_API_BASE_URL=https://merchantapi.googleapis.com",
                        "GOOGLE_MERCHANT_API_AUTH_MODE=service_account_json",
                        "GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON=REPLACE_ME",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(payload["auth"].get("mode"), "service_account_json")
            self.assertNotIn("REPLACE_ME", payload["error"])

    def test_auth_check_honestly_handles_oauth_missing_client_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            token_path = Path(d) / "token.json"
            token_path.write_text(
                json.dumps(
                    {
                        "refresh_token": "refresh-secret-value",
                        "access_token": "access-secret-value",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            env_path.write_text(
                "\n".join(
                    [
                        "GOOGLE_MERCHANT_API_BASE_URL=https://merchantapi.googleapis.com",
                        "GOOGLE_MERCHANT_API_AUTH_MODE=oauth_refresh_token",
                        f"GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN={token_path}",
                        "GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID=REPLACE_ME_CLIENT_ID",
                        "GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET=REPLACE_ME_CLIENT_SECRET",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertNotIn("refresh-secret-value", buf.getvalue())
            self.assertNotIn("access-secret-value", buf.getvalue())
