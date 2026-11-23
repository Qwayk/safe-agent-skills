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

from cloudflare_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("CLOUDFLARE_API_BASE_URL=https://api.cloudflare.com/client/v4\n")
                f.write("CLOUDFLARE_API_TOKEN=paste_token_here\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

    def test_installed_setup_uses_a_private_file_and_keeps_the_selected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            for command in (["config", "init"], ["onboarding"]):
                selected = Path(td) / command[0] / "team settings.env"
                with self.subTest(command=command), redirect_stdout(output := io.StringIO()):
                    self.assertEqual(main(["--output", "json", "--env-file", str(selected), *command]), 0)
                self.assertEqual(stat.S_IMODE(selected.stat().st_mode), 0o600)
                self.assertIn("CLOUDFLARE_API_TOKEN=", selected.read_text())
                if command == ["onboarding"]:
                    setup = json.loads(output.getvalue())["onboarding"]
                    self.assertEqual(shlex.split(setup["next_command"])[1:3], ["--env-file", str(selected)])
                    self.assertEqual(setup["missing"], ["CLOUDFLARE_API_TOKEN"])
