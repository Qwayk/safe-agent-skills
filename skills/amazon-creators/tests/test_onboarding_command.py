from __future__ import annotations

import io
import json
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from amazon_creators_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def _onboard(self, env_path: Path, *flags: str) -> dict:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--no-artifacts", "--env-file", str(env_path), *flags, "onboarding"])
        self.assertEqual(rc, 0)
        return json.loads(buf.getvalue())["onboarding"]

    def test_onboarding_shows_copyable_settings_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / ".env"
            setup = self._onboard(path)
            self.assertIn("AMAZON_CREATORS_PARTNER_TAG=", setup["settings_template"])
            self.assertIn("AMAZON_CREATORS_PARTNER_TAG", setup["missing"])
            self.assertFalse(setup["env_created"])
            self.assertFalse(path.exists())

    def test_apply_creates_private_file_and_keeps_selected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "account two.env"
            setup = self._onboard(path, "--apply")
            self.assertTrue(setup["env_created"])
            self.assertEqual(path.read_text(), setup["settings_template"])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(
                shlex.split(setup["next_command"])[1:],
                ["--env-file", str(path), "auth", "token", "fetch"],
            )

    def test_apply_leaves_existing_settings_as_they_are(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / ".env"
            path.write_text("AMAZON_CREATORS_PARTNER_TAG=keep-this-tag\n")
            setup = self._onboard(path, "--apply")
            self.assertFalse(setup["env_created"])
            self.assertNotIn("AMAZON_CREATORS_PARTNER_TAG", setup["missing"])
            self.assertEqual(path.read_text(), "AMAZON_CREATORS_PARTNER_TAG=keep-this-tag\n")
