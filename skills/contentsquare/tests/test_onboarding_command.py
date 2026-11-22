from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from contentsquare_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("CONTENTSQUARE_CLIENT_ID=\n")
                f.write("CONTENTSQUARE_CLIENT_SECRET=\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))

    def test_custom_env_file_keeps_its_name_and_is_private(self) -> None:
        import shlex
        from pathlib import Path
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {}, clear=True):
            env_path = Path(td) / "new folder" / "team settings.env"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--oauth-project-id", "42", "onboarding"])
            self.assertEqual(rc, 0)
            self.assertEqual(env_path.stat().st_mode & 0o777, 0o600)
            self.assertIn("CONTENTSQUARE_CLIENT_SECRET=", env_path.read_text())
            result = json.loads(buf.getvalue())["onboarding"]
            self.assertEqual(
                shlex.split(result["next_command"]),
                ["contentsquare-safe-cli", "--output", "json", "--env-file", str(env_path), "--oauth-project-id", "42", "auth", "check"],
            )
