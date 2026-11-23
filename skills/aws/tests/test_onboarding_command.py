from __future__ import annotations

import io
import json
import os
import shlex
import stat
import tempfile
import unittest
from contextlib import redirect_stdout

from aws_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, "aws settings.env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("AWS_DEFAULT_REGION=us-east-1\n")
                f.write("AWS_PROFILE=demo-profile\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

            self.assertEqual(0o600, stat.S_IMODE(os.stat(env_path).st_mode))
            args = shlex.split(payload["onboarding"]["next_command"])
            self.assertEqual(env_path, args[args.index("--env-file") + 1])
            with redirect_stdout(io.StringIO()):
                self.assertEqual(0, main(["--env-file", env_path, "onboarding"]))
            with open(env_path, encoding="utf-8") as settings:
                self.assertIn("AWS_PROFILE=demo-profile", settings.read())
