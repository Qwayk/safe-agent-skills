from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.cli import main


class TestAuthCheck(unittest.TestCase):
    def test_auth_check_accepts_refreshable_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")

            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(
                json.dumps(
                    {
                        "refresh_token": "refresh-token",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.commands.auth._load_validated_credentials",
                return_value=({"refresh_token": "refresh-token"}, False),
            ), patch(
                "google_business_profile_safe_agent_cli.commands.auth._can_refresh_credentials",
                return_value=True,
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["needs_reauth"])
            self.assertIn("valid access token", payload["note"])
