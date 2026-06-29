from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from zapier_safe_agent_cli.cli import main


class TestCliJsonParseErrors(unittest.TestCase):
    def test_missing_command_is_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_invalid_subcommand_is_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "auth"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_missing_config_path_is_single_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "missing-config.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--config", str(missing), "runs", "list"])

            payload_text = buf.getvalue()
            self.assertEqual(rc, 1)
            payload = json.loads(payload_text)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "RuntimeError")
            self.assertIn("Project config not found", payload["error"])
            self.assertNotIn("Traceback", payload_text)

    def test_invalid_config_json_is_single_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            invalid = Path(td) / "config.json"
            invalid.write_text("{not-json", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--config", str(invalid), "runs", "list"])

            payload_text = buf.getvalue()
            self.assertEqual(rc, 1)
            payload = json.loads(payload_text)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "JSONDecodeError")
            self.assertNotIn("Traceback", payload_text)
