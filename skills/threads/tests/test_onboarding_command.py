from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from threads_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_accepts_a_token_without_other_app_settings(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {}, clear=True):
            env = Path(td) / "nested" / ".env"
            flags = ["--output", "json", "--env-file", str(env), "onboarding"]
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(flags), 0)
            self.assertIn("THREADS_API_TOKEN=", env.read_text(encoding="utf-8"))
            env.write_text("THREADS_API_TOKEN=fixture-user-token\n", encoding="utf-8")

            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(flags), 0)
            result = json.loads(out.getvalue())["onboarding"]
            self.assertEqual(result["missing"], [])
            self.assertFalse(result["env_created"])
            self.assertIn(str(env), result["next_command"])

    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("THREADS_API_BASE_URL=https://api.example.com\n")
                f.write("THREADS_API_TOKEN=paste_token_here\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

