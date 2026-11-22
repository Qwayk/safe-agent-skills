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

from hubspot_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("HUBSPOT_API_BASE_URL=https://api.example.com\n")
                f.write("HUBSPOT_ACCESS_TOKEN=paste_token_here\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

    def test_onboarding_keeps_selected_settings_and_recognizes_existing_auth(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {}, clear=True):
            env = Path(td) / "my settings.env"
            token_file = env.parent / ".state" / "token.json"
            token_file.parent.mkdir()
            token_file.write_text('{"access_token":"stored-fixture-token"}')
            for config, expected_missing in (
                ("HUBSPOT_API_TOKEN=fixture-token\nHUBSPOT_TIMEOUT_S=bad-value\n", []),
                ("", []),
            ):
                env.write_text(config)
                with io.StringIO() as buffer, redirect_stdout(buffer):
                    rc = main(["--env-file", str(env), "onboarding", "--no-write-env"])
                    result = buffer.getvalue()
                self.assertEqual(rc, 0)
                data = json.loads(result)["onboarding"]
                self.assertEqual(data["missing"], expected_missing)
                self.assertEqual(shlex.split(data["next_command"])[-4:], ["--env-file", str(env), "auth", "check"])
                self.assertNotIn("fixture-token", result)
