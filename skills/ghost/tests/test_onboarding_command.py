import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from ghost_api_tool.cli import main as cli_main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_no_write_env_prints_json(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli_main(["--output", "json", "--env-file", env_path, "onboarding", "--no-write-env"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertIn("onboarding", payload)
            self.assertFalse(bool(payload["onboarding"]["env_created"]))
            self.assertIn("GHOST_ADMIN_API_URL", payload["onboarding"]["missing"])

    def test_onboarding_writes_env_and_normalizes_api_url(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("GHOST_ADMIN_API_URL=\n")
                f.write("GHOST_ADMIN_API_KEY=\n")
                f.write("GHOST_ACCEPT_VERSION=v5.0\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli_main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_path,
                        "onboarding",
                        "--api-url",
                        "your-site.ghost.io",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(bool(payload["onboarding"]["env_created"]))

            with open(env_path, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("GHOST_ADMIN_API_URL=https://your-site.ghost.io/ghost/api/admin/", text)
            self.assertIn("GHOST_ACCEPT_VERSION=v5.0", text)
            # key remains empty (not written by the tool)
            self.assertIn("GHOST_ADMIN_API_KEY=", text)
