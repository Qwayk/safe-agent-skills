from __future__ import annotations

import io
import json
import os
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from awin_advertiser_safe_agent_cli.cli import main
from awin_advertiser_safe_agent_cli.config import load_config


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("AWIN_API_BASE_URL=https://api.awin.com\n")
                f.write("AWIN_API_TOKEN=token_here\n")
                f.write("AWIN_ADVERTISER_ID=123\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

    def test_first_run_creates_private_file_and_keeps_its_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "advertiser settings.env"
            with redirect_stdout(out := io.StringIO()):
                self.assertEqual(main(["--env-file", str(path), "onboarding"]), 0)
            setup = json.loads(out.getvalue())["onboarding"]
            self.assertEqual(setup["missing"], ["AWIN_API_TOKEN", "AWIN_ADVERTISER_ID"])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(shlex.split(setup["next_command"])[3:5], ["--env-file", str(path)])

            path.write_text("AWIN_API_TOKEN=fixture-file\nAWIN_ADVERTISER_ID=111\n")
            with patch.dict(os.environ, {"AWIN_API_TOKEN": "fixture-shell", "AWIN_ADVERTISER_ID": "222"}):
                self.assertEqual(load_config(str(path)).advertiser_id, "111")
                self.assertEqual(load_config(str(path)).token, "fixture-file")
                self.assertEqual(load_config(None).advertiser_id, "222")
                self.assertEqual(load_config(None).token, "fixture-shell")
