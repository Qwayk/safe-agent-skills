from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from amazon_creators_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def _sample_example(self, td: str) -> str:
        example_path = os.path.join(td, ".env.example")
        with open(example_path, "w", encoding="utf-8") as f:
            f.write("AMAZON_CREATORS_API_BASE_URL=https://api.example.com\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_ID=cred-id\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_SECRET=secret\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_VERSION=2\n")
            f.write("AMAZON_CREATORS_LOCALE=en_US\n")
            f.write("AMAZON_CREATORS_PARTNER_TAG=partner-tag\n")
        return example_path

    def test_onboarding_keeps_env_dry_run_without_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._sample_example(td)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["onboarding"]["env_created"])
            self.assertFalse(os.path.exists(env_path))

    def test_onboarding_apply_refuses_before_env_write(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._sample_example(td)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "--apply", "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["plan"]["before_state"]["status"], "true_blocker")
            self.assertEqual(payload["verification_plan"]["status"], "true_blocker")
            self.assertFalse(payload["onboarding"]["env_created"])
            self.assertFalse(os.path.exists(env_path))

    def test_onboarding_reports_partner_tag_and_next_command(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("AMAZON_CREATORS_API_BASE_URL=https://api.example.com\n")
                f.write("AMAZON_CREATORS_CREDENTIAL_ID=cred-id\n")
                f.write("AMAZON_CREATORS_CREDENTIAL_SECRET=secret\n")
                f.write("AMAZON_CREATORS_CREDENTIAL_VERSION=2.1\n")
                f.write("AMAZON_CREATORS_LOCALE=en_US\n")
                # partner tag intentionally missing

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertIn("AMAZON_CREATORS_PARTNER_TAG", payload["onboarding"]["missing"])
            self.assertEqual(
                payload["onboarding"]["next_command"],
                "amazon-creators-api-tool --output json auth token fetch",
            )
