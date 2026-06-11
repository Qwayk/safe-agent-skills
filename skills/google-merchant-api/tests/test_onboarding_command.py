from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from google_merchant_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def run_onboarding_json(self, env_path: str) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
        payload = json.loads(buf.getvalue())
        return rc, payload

    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("GOOGLE_MERCHANT_API_API_BASE_URL=https://api.example.com\n")
                f.write("GOOGLE_MERCHANT_API_AUTH_MODE=service_account_json\n")
                f.write("GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON=/tmp/merchant-account.json\n")

            rc, payload = self.run_onboarding_json(env_path)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

    def test_onboarding_checks_merchant_api_env_keys(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("GOOGLE_MERCHANT_API_BASE_URL=https://merchantapi.googleapis.com\n")
                f.write("GOOGLE_MERCHANT_API_AUTH_MODE=service_account_json\n")

            rc, payload = self.run_onboarding_json(env_path)
            self.assertEqual(rc, 0)
            missing = payload["onboarding"]["missing"]
            self.assertIn("GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON", missing)
            self.assertNotIn("GOOGLE_MERCHANT_API_API_BASE_URL", missing)
            self.assertNotIn("GOOGLE_MERCHANT_API_API_TOKEN", missing)
            self.assertEqual(payload["onboarding"]["auth_mode"], "service_account_json")

    def test_onboarding_checks_oauth_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("GOOGLE_MERCHANT_API_BASE_URL=https://merchantapi.googleapis.com\n")
                f.write("GOOGLE_MERCHANT_API_AUTH_MODE=oauth_refresh_token\n")

            rc, payload = self.run_onboarding_json(env_path)
            self.assertEqual(rc, 0)
            missing = payload["onboarding"]["missing"]
            self.assertIn("GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN", missing)
            self.assertIn("GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID", missing)
            self.assertIn("GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET", missing)
            self.assertEqual(payload["onboarding"]["auth_mode"], "oauth_refresh_token")
