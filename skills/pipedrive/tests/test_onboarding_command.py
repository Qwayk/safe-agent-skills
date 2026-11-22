from __future__ import annotations

import io
import json
import os
import shlex
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from qwayk_pipedrive_safe_agent_cli.cli import main
from qwayk_pipedrive_safe_agent_cli.config import load_config


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

    def test_onboarding_without_example_creates_blank_settings(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / "work" / "crm settings.env"
            with patch("pathlib.Path.is_file", return_value=False), io.StringIO() as output, redirect_stdout(output):
                self.assertEqual(main(["--env-file", str(env), "onboarding"]), 0)
                result = json.loads(output.getvalue())["onboarding"]
            self.assertTrue(result["env_created"])
            self.assertEqual(env.read_text(encoding="utf-8"), "")
            self.assertEqual(shlex.split(result["next_command"])[1:], ["--env-file", str(env), "auth", "check"])

            env.write_text("PIPEDRIVE_API_DOMAIN=example-company\n", encoding="utf-8")
            with io.StringIO() as output, redirect_stdout(output):
                self.assertEqual(main(["--env-file", str(env), "onboarding"]), 0)
                self.assertFalse(json.loads(output.getvalue())["onboarding"]["env_created"])
            self.assertIn("example-company", env.read_text(encoding="utf-8"))

    def test_company_slug_works_with_old_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {}, clear=True):
            env = Path(td) / ".env"
            env.write_text(
                "PIPEDRIVE_API_DOMAIN=example-company\nPIPEDRIVE_BASE_URL=https://your-company.pipedrive.com\n",
                encoding="utf-8",
            )
            self.assertEqual(load_config(str(env)).api_root, "https://example-company.pipedrive.com")
