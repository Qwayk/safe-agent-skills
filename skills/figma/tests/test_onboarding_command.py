from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from figma_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("FIGMA_BASE_URL=https://api.figma.com\n")
                f.write("FIGMA_AUTH_MODE=personal\n")
                f.write("FIGMA_ACCESS_TOKEN=YOUR_FIGMA_ACCESS_TOKEN\n")
                f.write("FIGMA_TIMEOUT_S=30\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))
            self.assertEqual(payload["onboarding"]["missing"], [])

    def test_onboarding_uses_defaults_without_an_example_and_keeps_the_selected_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = os.path.join(td, "config folder", "figma.env")
            args = ["--env-file", env_file, "onboarding"]
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main([*args, "--no-write-env"]), 0)
            self.assertFalse(os.path.exists(env_file))

            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(main(args), 0)
            setup = json.loads(buf.getvalue())["onboarding"]
            self.assertTrue(setup["env_created"])
            self.assertEqual(setup["missing"], ["FIGMA_ACCESS_TOKEN"])
            self.assertIn(f"--env-file '{env_file}'", setup["next_command"])

            with open(env_file, "w", encoding="utf-8") as settings:
                settings.write("FIGMA_ACCESS_TOKEN=fixture-token\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(main(args), 0)
            self.assertEqual(json.loads(buf.getvalue())["onboarding"]["missing"], [])
            with open(env_file, encoding="utf-8") as settings:
                self.assertEqual(settings.read(), "FIGMA_ACCESS_TOKEN=fixture-token\n")
