from __future__ import annotations

import io
import json
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from gemini_api_tool.cli import main
from gemini_api_tool.config import API_KEY_PLACEHOLDER


class TestOnboardingCommand(unittest.TestCase):
    def run_cli(self, path: Path, *args: str) -> tuple[int, dict]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--output", "json", "--env-file", str(path), *args])
        return code, json.loads(output.getvalue())

    def test_onboarding_creates_private_settings_in_the_selected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict("os.environ", {}, clear=True):
            path = Path(td) / "new folder" / "settings.env"
            code, payload = self.run_cli(path, "onboarding")
            self.assertEqual(0, code)
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertIn(f"GEMINI_API_KEY={API_KEY_PLACEHOLDER}", path.read_text())
            self.assertEqual(0o600, path.stat().st_mode & 0o777)
            self.assertEqual(["GEMINI_API_KEY"], payload["onboarding"]["missing"])
            args = shlex.split(payload["onboarding"]["next_command"])
            self.assertEqual(["--output", "json", "--env-file", str(path), "auth", "check"], args[1:])

            self.assertEqual(1, self.run_cli(path, "auth", "check")[0])
            path.write_text("GEMINI_API_KEY=test-local-key\n")
            _, payload = self.run_cli(path, "onboarding")
            self.assertFalse(payload["onboarding"]["env_created"])
            self.assertEqual([], payload["onboarding"]["missing"])
            self.assertIn("test-local-key", path.read_text())
            self.assertTrue(self.run_cli(path, "auth", "check")[1]["api_key_present"])

    def test_onboarding_accepts_a_key_from_the_shell_without_writing_settings(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict("os.environ", {"GEMINI_API_KEY": "shell-test-key"}, clear=True):
            path = Path(td) / "settings.env"
            code, payload = self.run_cli(path, "onboarding", "--no-write-env")
            self.assertEqual(0, code)
            self.assertFalse(path.exists())
            self.assertEqual([], payload["onboarding"]["missing"])
            self.assertNotIn("shell-test-key", json.dumps(payload))
