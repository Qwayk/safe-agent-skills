from __future__ import annotations

import io
import json
import os
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout

from unsplash_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("UNSPLASH_API_BASE_URL=https://api.unsplash.com\n")
                f.write("UNSPLASH_ACCESS_KEY=paste_access_key_here\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

    def test_selected_settings_file_is_used_for_next_check(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, "chosen folder", "unsplash.env")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            setup = json.loads(buf.getvalue())["onboarding"]
            self.assertEqual(setup["missing"], ["UNSPLASH_ACCESS_KEY"])
            self.assertEqual(shlex.split(setup["next_command"])[1:], ["--output", "json", "--env-file", env_path, "auth", "check"])
            self.assertEqual(os.stat(env_path).st_mode & 0o777, 0o600)
