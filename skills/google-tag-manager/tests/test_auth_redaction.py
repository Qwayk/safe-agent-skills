from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from gtm_api_tool.auth import auth_summary
from gtm_api_tool.cli import main
from gtm_api_tool.config import Config


class TestAuthRedaction(unittest.TestCase):
    def test_auth_check_missing_oauth_vars_is_clean_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("GTM_AUTH_MODE=oauth_refresh_token\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--output", "json", "auth", "check"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Missing required env var", payload["error"])

    def test_auth_summary_never_includes_secret_values(self) -> None:
        cfg = Config(
            base_url="https://tagmanager.googleapis.com/",
            timeout_s=30.0,
            min_delay_s=4.0,
            read_retries=5,
            auth_mode="oauth_refresh_token",
            scopes=("https://www.googleapis.com/auth/tagmanager.readonly",),
            oauth_client_id="CLIENT_ID_SECRET",
            oauth_client_secret="CLIENT_SECRET_VALUE",
            oauth_refresh_token="REFRESH_TOKEN_VALUE",
            service_account_json_path=None,
        )
        s = auth_summary(cfg)
        dumped = json.dumps(s, sort_keys=True)
        self.assertNotIn("CLIENT_ID_SECRET", dumped)
        self.assertNotIn("CLIENT_SECRET_VALUE", dumped)
        self.assertNotIn("REFRESH_TOKEN_VALUE", dumped)
