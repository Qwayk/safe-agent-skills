from __future__ import annotations

import io
import json
import os
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sovrn_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("SOVRN_COMMERCE_SECRET_KEY=\n")
                f.write("SOVRN_COMMERCE_SITE_API_KEY=\n")
                f.write("SOVRN_ADVERTISING_API_KEY=\n")
                f.write("SOVRN_ADVERTISING_PUBLISHER_ID=\n")
                f.write("SOVRN_TIMEOUT_S=30\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))
            self.assertIn("SOVRN_COMMERCE_SECRET_KEY", payload["onboarding"]["missing"])

    def test_onboarding_uses_private_file_and_keeps_it_in_next_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chosen settings.env"
            with redirect_stdout(out := io.StringIO()):
                self.assertEqual(main(["--env-file", str(path), "onboarding"]), 0)
            setup = json.loads(out.getvalue())["onboarding"]
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertIn("SOVRN_COMMERCE_SITE_API_KEY=", path.read_text())
            self.assertIn(str(path), shlex.split(setup["next_command"]))
