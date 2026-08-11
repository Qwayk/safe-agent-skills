from __future__ import annotations

import io
import json
import os
import stat
import tempfile
import unittest
from contextlib import redirect_stdout

from giantpanda_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("GIANTPANDA_API_TOKEN=your_token_here\n")
                f.write("GIANTPANDA_TIMEOUT_S=30\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))
            self.assertEqual(stat.S_IMODE(os.stat(env_path).st_mode), 0o600)

    def test_onboarding_marks_placeholder_as_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("GIANTPANDA_API_TOKEN=your_token_here\n")
            payload_buf = io.StringIO()
            with redirect_stdout(payload_buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(payload_buf.getvalue())
            self.assertIn("GIANTPANDA_API_TOKEN", payload["onboarding"]["missing"])
