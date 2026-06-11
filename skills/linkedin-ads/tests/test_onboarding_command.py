from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from linkedin_ads_api_tool.cli import main


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
