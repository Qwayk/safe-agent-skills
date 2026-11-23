from __future__ import annotations

import io
import json
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from gcp_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_keeps_the_selected_settings_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "settings folder" / "chosen.env"
            args = ["--output", "json", "--env-file", str(path), "onboarding"]

            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(0, main(args))
            result = json.loads(out.getvalue())["onboarding"]
            self.assertTrue(result["env_created"])
            self.assertEqual([], result["missing"])
            self.assertEqual(0o600, path.stat().st_mode & 0o777)
            self.assertEqual(
                ["--output", "json", "--env-file", str(path), "auth", "check"],
                shlex.split(result["next_command"])[1:],
            )
            original = path.read_text()
            with redirect_stdout(io.StringIO()):
                self.assertEqual(0, main(args))
            self.assertEqual(original, path.read_text())
