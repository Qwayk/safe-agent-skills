from __future__ import annotations

import io
import json
import os
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from zapier_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("ZAPIER_BASE_URL=https://api.zapier.com\n")

            buf = io.StringIO()
            with patch.dict(os.environ, {}, clear=True), redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))
            self.assertIn("ZAPIER_ACCESS_TOKEN", payload["onboarding"]["missing"])
            self.assertEqual(Path(env_path).stat().st_mode & 0o777, 0o600)

    def test_setup_from_installed_tool_and_chosen_settings_file(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {}, clear=True):
            env_path = Path(td) / "my zapier.env"
            argv = ["--env-file", str(env_path), "--output", "json", "onboarding"]
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(main(argv), 0)
            onboarding = json.loads(buf.getvalue())["onboarding"]
            self.assertTrue(onboarding["env_created"])
            self.assertEqual(env_path.read_text(), "ZAPIER_ACCESS_TOKEN=\n")
            self.assertEqual(env_path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(onboarding["missing"], ["ZAPIER_ACCESS_TOKEN"])
            self.assertEqual(shlex.split(onboarding["next_command"])[1:3], ["--env-file", str(env_path)])
            self.assertEqual(shlex.split(onboarding["next_command"])[-2:], ["auth", "check"])

            contents = "ZAPIER_ACCESS_TOKEN=example-token\n"
            env_path.write_text(contents)
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(main(argv), 0)
            onboarding = json.loads(buf.getvalue())["onboarding"]
            self.assertFalse(onboarding["env_created"])
            self.assertEqual(onboarding["missing"], [])
            self.assertEqual(env_path.read_text(), contents)
            self.assertNotIn("example-token", buf.getvalue())

            absent = Path(td) / "check only.env"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--env-file", str(absent), "onboarding", "--no-write-env"]), 0)
            self.assertFalse(absent.exists())
