from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from shlex import split
from unittest.mock import patch

from tiktok_marketing_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_without_sample_uses_saved_token_and_keeps_settings(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict("os.environ", {}, clear=True):
            settings = Path(td) / "account.env"
            args = ["--output", "json", "--env-file", str(settings), "onboarding"]
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(args), 0)
            created = json.loads(output.getvalue())["onboarding"]
            self.assertTrue(created["env_created"])
            self.assertEqual(split(created["next_command"])[-3:], [str(settings), "auth", "check"])
            template = settings.read_text(encoding="utf-8")
            self.assertIn("TIKTOK_MARKETING_APP_ID=\n", template)
            self.assertIn("TIKTOK_MARKETING_APP_SECRET=\n", template)
            self.assertIn("TIKTOK_MARKETING_ACCESS_TOKEN=\n", template)

            token_file = settings.parent / ".state" / "token.json"
            token_file.parent.mkdir()
            token_file.write_text('{"access_token":"fixture-token"}', encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(args), 0)
            result = json.loads(output.getvalue())["onboarding"]
            self.assertFalse(result["env_created"])
            self.assertNotIn("TIKTOK_MARKETING_ACCESS_TOKEN", result["missing"])
            self.assertNotIn("fixture-token", output.getvalue())
            self.assertEqual(settings.read_text(encoding="utf-8"), template)

    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("TIKTOK_MARKETING_API_BASE_URL=https://business-api.tiktok.com\n")
                f.write("TIKTOK_MARKETING_ACCESS_TOKEN=paste_access_token_here\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

