from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from giantpanda_api_tool.cli import main


class TestAuthReadiness(unittest.TestCase):
    def test_auth_check_reports_missing_token_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            Path(env_path).write_text("GIANTPANDA_TIMEOUT_S=30\n", encoding="utf-8")

            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "auth", "check"])
                self.assertEqual(rc, 0)
                self.assertEqual(req.call_count, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["auth"]["ready"])

    def test_auth_check_placeholder_token_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("GIANTPANDA_API_TOKEN=your_token_here\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["auth"]["ready"])
            self.assertNotIn("your_token_here", buf.getvalue())

    def test_auth_check_does_not_leak_token_string(self) -> None:
        sentinel = "sentinel_token_123"
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"GIANTPANDA_API_TOKEN={sentinel}\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["auth"]["ready"])
            self.assertNotIn(sentinel, buf.getvalue())
