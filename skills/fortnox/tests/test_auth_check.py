from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fortnox_api_tool.cli import main


class TestAuthCheck(unittest.TestCase):
    def test_auth_check_uses_env_token_for_live_probe(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=env-token\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with patch("fortnox_api_tool.commands.auth.get_me", return_value={"Id": "user-1"}):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["token_source"], "env")
            self.assertTrue(payload["live_probe"]["attempted"])
            self.assertEqual(payload["live_probe"]["status"], 200)

    def test_auth_check_fails_cleanly_when_no_token_exists(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check", "--skip-live"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["token_source"], "missing")
            self.assertEqual(payload["live_probe"]["status"], "blocked")
