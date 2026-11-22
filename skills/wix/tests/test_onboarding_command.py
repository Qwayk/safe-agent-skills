from __future__ import annotations

import io
import json
import os
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from wix_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("WIX_API_BASE_URL=https://api.example.com\n")
                f.write("WIX_APP_ID=app_id_here\n")
                f.write("WIX_APP_SECRET=app_secret_here\n")
                f.write("WIX_INSTANCE_ID=instance_id_here\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

    def test_onboarding_works_without_example_and_preserves_selected_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            settings = Path(td) / "new folder" / "account settings.env"
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["--env-file", str(settings), "onboarding"])
            self.assertEqual(code, 0)
            self.assertIn("WIX_API_KEY=", settings.read_text())
            self.assertEqual(settings.stat().st_mode & 0o777, 0o600)
            command = shlex.split(json.loads(output.getvalue())["onboarding"]["next_command"])
            self.assertEqual(command[command.index("--env-file") + 1], str(settings))
