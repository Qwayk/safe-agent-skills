from __future__ import annotations

import io
import json
import os
import shlex
import stat
import tempfile
import unittest
from contextlib import redirect_stdout

from openai_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_private_settings_and_keeps_the_selected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, "custom folder", "account settings.env")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())["onboarding"]
            self.assertTrue(payload["env_created"])
            self.assertEqual(payload["missing"], ["OPENAI_API_KEY"])
            self.assertEqual(stat.S_IMODE(os.stat(env_path).st_mode), 0o600)
            args = shlex.split(payload["next_command"])
            self.assertEqual(args[1:3], ["--env-file", env_path])
