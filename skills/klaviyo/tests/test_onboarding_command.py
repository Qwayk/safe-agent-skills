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

from klaviyo_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {}, clear=True):
            env_path = os.path.join(td, "my klaviyo.env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("KLAVIYO_API_BASE_URL=https://a.klaviyo.com\n")
                f.write("KLAVIYO_API_KEY=\n")
                f.write("KLAVIYO_COMPANY_ID=\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))
            self.assertEqual(Path(env_path).stat().st_mode & 0o777, 0o600)
            self.assertEqual(payload["onboarding"]["missing"], ["KLAVIYO_API_KEY"])
            follow_up = shlex.split(payload["onboarding"]["next_command"])
            self.assertEqual(follow_up[1:3], ["--env-file", env_path])
            self.assertEqual(follow_up[-3:], ["--live", "api", "get_lists"])
