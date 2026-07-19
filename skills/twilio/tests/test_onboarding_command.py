from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from twilio_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_is_read_only_until_write_env_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = main(["--env-file", str(env_path), "onboarding"])
            self.assertEqual(rc, 0)
            self.assertFalse(env_path.exists())
            self.assertFalse(json.loads(stdout.getvalue())["created"])

    def test_onboarding_creates_mode_600_twilio_env_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = main(["--env-file", str(env_path), "onboarding", "--write-env"])
            self.assertEqual(rc, 0)
            self.assertTrue(json.loads(stdout.getvalue())["created"])
            self.assertEqual(env_path.stat().st_mode & 0o777, 0o600)
            self.assertIn("TWILIO_API_KEY_SECRET", env_path.read_text(encoding="utf-8"))

            second = io.StringIO()
            with redirect_stdout(second):
                second_rc = main(["--env-file", str(env_path), "onboarding", "--write-env"])
            self.assertEqual(second_rc, 1)
            self.assertFalse(json.loads(second.getvalue())["ok"])
