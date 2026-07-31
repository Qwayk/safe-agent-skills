from __future__ import annotations

import io
import json
import os
import stat
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from namebright_safe_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("NAMEBRIGHT_CLIENT_ID=client-id\n")
                f.write("NAMEBRIGHT_CLIENT_SECRET=client-secret\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertEqual(stat.S_IMODE(os.stat(env_path).st_mode), 0o600)
            self.assertTrue(os.path.exists(env_path))

            env_text = Path(env_path).read_text(encoding="utf-8")
            self.assertIn("NAMEBRIGHT_CLIENT_ID", env_text)
            self.assertIn("NAMEBRIGHT_CLIENT_SECRET", env_text)
            self.assertIn("NAMEBRIGHT_TIMEOUT_S", env_text)
            self.assertNotIn("client-id", env_text)
            self.assertNotIn("client-secret", env_text)
            self.assertTrue(payload["onboarding"]["next_command"].endswith("auth check"))
            self.assertTrue(
                any("source IP" in step or "approved" in step for step in payload["onboarding"].get("steps", [])),
            )
