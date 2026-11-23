from __future__ import annotations

import io
import json
import os
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from skimlinks_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_clean_install_creates_a_private_template_and_keeps_its_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "other account.env"
            options = ["--env-file", str(path), "onboarding"]
            for expected_created in (True, False):
                with self.subTest(created=expected_created):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        self.assertEqual(main(options), 0)
                    setup = json.loads(buf.getvalue())["onboarding"]
                    self.assertEqual(setup["env_created"], expected_created)
                    self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                    self.assertEqual(shlex.split(setup["next_command"])[3:5], ["--env-file", str(path)])
                    if expected_created:
                        self.assertIn("SKIMLINKS_LINK_WRAPPER_ID=", path.read_text())
                        path.write_text("SKIMLINKS_CLIENT_ID=keep-this-value\n")
                    else:
                        self.assertEqual(path.read_text(), "SKIMLINKS_CLIENT_ID=keep-this-value\n")
                        self.assertNotIn("SKIMLINKS_CLIENT_ID", setup["missing"])

    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("SKIMLINKS_CLIENT_ID=\n")
                f.write("SKIMLINKS_CLIENT_SECRET=\n")
                f.write("SKIMLINKS_PUBLISHER_ID=\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertIn("SKIMLINKS_CLIENT_ID", payload["onboarding"]["missing"])
            self.assertIn(
                "SKIMLINKS_PUBLISHER_DOMAIN_ID",
                " ".join(payload["onboarding"]["steps"]),
            )
            self.assertTrue(os.path.exists(env_path))
