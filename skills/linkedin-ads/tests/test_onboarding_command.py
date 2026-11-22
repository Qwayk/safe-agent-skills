from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from linkedin_ads_api_tool.cli import main
from linkedin_ads_api_tool.config import load_config


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_linkedin_env_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(env_path.exists())

            data = env_path.read_text(encoding="utf-8")
            for key in (
                "LINKEDIN_ADS_BASE_URL",
                "LINKEDIN_ADS_TOKEN",
                "LINKEDIN_ADS_LINKEDIN_VERSION",
                "LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION",
                "LINKEDIN_ADS_TIMEOUT_S",
            ):
                self.assertIn(f"{key}=", data)

    def test_setup_uses_alternate_token_and_preserves_existing_settings(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict("os.environ", {}, clear=True):
            env_path = Path(td) / "settings.env"
            contents = "LINKEDIN_ADS_TOKEN=\nLINKEDIN_ADS_ACCESS_TOKEN=token-from-file\n"
            env_path.write_text(contents, encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "onboarding"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(buf.getvalue())["onboarding"]["missing"], [])
            self.assertNotIn("token-from-file", buf.getvalue())
            self.assertEqual(env_path.read_text(encoding="utf-8"), contents)
            self.assertEqual(load_config(str(env_path)).token, "token-from-file")
            with patch.dict("os.environ", {"LINKEDIN_ADS_API_TOKEN": "later-alias"}):
                self.assertEqual(load_config(str(env_path)).token, "token-from-file")
            with patch.dict("os.environ", {"LINKEDIN_ADS_ACCESS_TOKEN": "token-from-shell"}):
                self.assertEqual(load_config(str(env_path)).token, "token-from-shell")
