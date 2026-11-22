from __future__ import annotations

import io
import json
import os
import shlex
import stat
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from instantly_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("INSTANTLY_API_BASE_URL=https://api.example.com\n")
                f.write("INSTANTLY_API_KEY=paste_token_here\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))



    def test_custom_file_is_private_and_used_by_next_command(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"INSTANTLY_API_KEY": ""}):
            env_path = Path(td) / "work settings.env"
            argv = ["--output", "json", "--env-file", str(env_path), "onboarding"]
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(main(argv), 0)
            result = json.loads(buf.getvalue())["onboarding"]
            self.assertEqual(result["missing"], ["INSTANTLY_API_KEY"])
            self.assertEqual(shlex.split(result["next_command"])[1:], [*argv[:-1], "auth", "check"])
            self.assertEqual(stat.S_IMODE(env_path.stat().st_mode), 0o600)

        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / "work settings.env"
            env_path.write_text("INSTANTLY_API_KEY=example-key\n", encoding="utf-8")
            with redirect_stdout(buf := io.StringIO()), patch.dict(os.environ):
                os.environ.pop("INSTANTLY_API_KEY", None)
                self.assertEqual(main(["--env-file", str(env_path), "onboarding"]), 0)
            result = json.loads(buf.getvalue())["onboarding"]
            self.assertEqual(result["missing"], [])
            self.assertFalse(result["env_created"])
