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

from meta_ads_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("META_ADS_BASE_URL=https://graph.facebook.com\n")
                f.write("META_ADS_API_VERSION=v24.0\n")
                f.write("META_ADS_ACCESS_TOKEN=paste_token_here\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

    def test_fresh_install_uses_the_selected_file_and_preserves_it(self) -> None:
        with tempfile.TemporaryDirectory() as d, patch.dict("os.environ", {}, clear=True):
            path = Path(d) / "meta settings.env"
            output = io.StringIO()
            with redirect_stdout(output):
                rc = main(["--env-file", str(path), "onboarding"])
            self.assertEqual(rc, 0)
            setup = json.loads(output.getvalue())["onboarding"]
            self.assertEqual(path.read_text(), "META_ADS_ACCESS_TOKEN=\nMETA_ADS_AD_ACCOUNT_ID=\n")
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(
                shlex.split(setup["next_command"])[1:],
                ["--output", "json", "--env-file", str(path), "auth", "check"],
            )
            path.write_text("META_ADS_ACCESS_TOKEN=fixture\n")
            output = io.StringIO()
            with redirect_stdout(output):
                rc = main(["--env-file", str(path), "onboarding"])
            self.assertEqual(rc, 0)
            self.assertEqual(path.read_text(), "META_ADS_ACCESS_TOKEN=fixture\n")
            self.assertEqual(json.loads(output.getvalue())["onboarding"]["missing"], [])
            self.assertNotIn("fixture", output.getvalue())
