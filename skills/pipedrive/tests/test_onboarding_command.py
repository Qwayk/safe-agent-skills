from __future__ import annotations

import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout

from qwayk_pipedrive_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = os.fspath(td)
            example = os.path.join(root, ".env.example")
            env_path = os.path.join(root, ".env")

            with open(example, "w", encoding="utf-8") as f:
                f.write("PIPEDRIVE_API_TOKEN=YOUR_TOKEN\n")
                f.write("PIPEDRIVE_API_DOMAIN=your-company\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertEqual(payload["onboarding"]["env_file"], env_path)
            self.assertTrue(os.path.exists(env_path))
            self.assertEqual(payload["onboarding"]["required_env_vars"]["required"], ["PIPEDRIVE_API_TOKEN"])
            self.assertEqual(
                payload["onboarding"]["required_env_vars"]["required_one_of"],
                ["PIPEDRIVE_API_DOMAIN", "PIPEDRIVE_BASE_URL"],
            )
            self.assertEqual(payload["onboarding"]["required_env_vars"]["optional"], ["PIPEDRIVE_TIMEOUT_S"])

            env_text = Path(env_path).read_text(encoding="utf-8")
            self.assertIn("PIPEDRIVE_API_TOKEN=YOUR_TOKEN", env_text)
