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

from awin_publisher_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("AWIN_API_TOKEN=YOUR_AWIN_TOKEN\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

    def test_installed_setup_uses_a_private_settings_file_and_the_selected_token(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "new folder" / "publisher settings.env"
            with redirect_stdout(stdout := io.StringIO()):
                self.assertEqual(main(["--env-file", str(path), "onboarding"]), 0)
            setup = json.loads(stdout.getvalue())["onboarding"]
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(setup["missing"], ["AWIN_API_TOKEN"])
            command = shlex.split(setup["next_command"])
            self.assertEqual(command[1:3], ["--env-file", str(path)])
            path.write_text("AWIN_API_TOKEN=fixture-file-token\n", encoding="utf-8")

            with (
                patch.dict(os.environ, {"AWIN_API_TOKEN": "fixture-shell-token"}),
                patch("awin_publisher_safe_agent_cli.commands.auth.fetch_accounts", return_value=([], 200)) as read,
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(main(command[1:]), 0)
                self.assertEqual(read.call_args.args[0].token, "fixture-file-token")
                read.reset_mock()
                path.unlink()
                self.assertEqual(main(command[1:]), 1)
                read.assert_not_called()
