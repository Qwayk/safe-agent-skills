from __future__ import annotations

import io
import json
import stat
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from dynadot_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_private_settings_and_uses_selected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / "dynadot settings.env"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "onboarding"])
            self.assertEqual(rc, 0)
            onboarding = json.loads(buf.getvalue())["onboarding"]
            self.assertTrue(onboarding["env_created"])
            self.assertEqual(onboarding["missing"], ["DYNADOT_API_KEY"])
            self.assertIn(f"--env-file '{env_path}' auth check", onboarding["next_command"])
            self.assertEqual(stat.S_IMODE(env_path.stat().st_mode), 0o600)
            self.assertIn("https://api.dynadot.com/api3.json", env_path.read_text())
