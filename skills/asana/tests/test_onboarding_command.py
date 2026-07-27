from __future__ import annotations

import contextlib
import io
import json
import stat
import tempfile
import unittest
from pathlib import Path

from asana_safe_agent_cli.cli import main


class TestOnboarding(unittest.TestCase):
    def test_onboarding_creates_private_placeholder_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                rc = main(["--env-file", str(env), "onboarding"])
            payload = json.loads(stdout.getvalue())
            mode = stat.S_IMODE(env.stat().st_mode)
            content = env.read_text(encoding="utf-8")
        self.assertEqual(rc, 0)
        self.assertTrue(payload["created"])
        self.assertEqual(mode, 0o600)
        self.assertIn("ASANA_ACCESS_TOKEN=", content)
        self.assertNotIn("Bearer ", content)

    def test_onboarding_does_not_overwrite_existing_env(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text("KEEP=1\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                main(["--env-file", str(env), "onboarding"])
            self.assertEqual(env.read_text(encoding="utf-8"), "KEEP=1\n")


if __name__ == "__main__":
    unittest.main()
