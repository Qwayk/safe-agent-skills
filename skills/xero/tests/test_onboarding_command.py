from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from xero_safe_agent_cli.cli import main
from xero_safe_agent_cli.config import load_config


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["created_placeholder_env"])
            self.assertTrue(os.path.exists(env_path))
            self.assertEqual(os.stat(env_path).st_mode & 0o777, 0o600)
            with open(env_path, encoding="utf-8") as handle:
                rendered = handle.read()
            self.assertIn("XERO_CLIENT_ID=", rendered)
            self.assertNotIn("paste_token_here", rendered)

    def test_relative_state_dir_is_beside_selected_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / "private" / "xero.env"
            env_path.parent.mkdir()
            env_path.write_text("XERO_STATE_DIR=private-state\n", encoding="utf-8")
            with patch.dict(os.environ):
                os.environ.pop("XERO_STATE_DIR", None)
                config = load_config(env_path)
            self.assertEqual(config.state_root, (env_path.parent / "private-state").resolve())
