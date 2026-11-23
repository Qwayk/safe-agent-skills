from __future__ import annotations

import io
import json
import os
import shlex
import stat
import tempfile
import unittest
from contextlib import redirect_stdout

from spaceship_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_private_settings_and_prints_chosen_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, "account settings.env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("SPACESHIP_API_KEY=dummy_key\n")
                f.write("SPACESHIP_API_SECRET=dummy_secret\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertEqual(stat.S_IMODE(os.stat(env_path).st_mode), 0o600)
            next_command = shlex.split(payload["onboarding"]["next_command"])
            self.assertEqual(next_command[next_command.index("--env-file") + 1], env_path)
            self.assertEqual(next_command[-2:], ["auth", "check"])
            with open(env_path, encoding="utf-8") as settings:
                self.assertEqual(settings.read().splitlines()[:2], ["SPACESHIP_API_KEY=", "SPACESHIP_API_SECRET="])
