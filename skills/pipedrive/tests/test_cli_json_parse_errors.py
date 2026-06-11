from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from qwayk_pipedrive_safe_agent_cli.cli import main


class TestCliValidationAndConfig(unittest.TestCase):
    def test_missing_config_is_single_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8"):
                pass

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "activities", "list"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_missing_required_path_argument_returns_validation_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("PIPEDRIVE_API_TOKEN=token123\n")
                f.write("PIPEDRIVE_API_DOMAIN=example-company\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "activities", "get"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_missing_required_term_query_argument_returns_validation_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("PIPEDRIVE_API_TOKEN=token123\n")
                f.write("PIPEDRIVE_API_DOMAIN=example-company\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "deals", "search"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(payload["error"], "Missing required query parameter: term")

    def test_missing_required_deal_ids_query_argument_returns_validation_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("PIPEDRIVE_API_TOKEN=token123\n")
                f.write("PIPEDRIVE_API_DOMAIN=example-company\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "deal-installments", "list"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(payload["error"], "Missing required query parameter: deal_ids")
