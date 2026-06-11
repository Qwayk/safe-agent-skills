from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from hubspot_safe_agent_cli.cli import main


class TestHubspotImportValidation(unittest.TestCase):
    def _env(self, root: Path) -> Path:
        env = root / ".env"
        env.write_text(
            "\n".join(
                [
                    "HUBSPOT_API_BASE_URL=http://example.invalid",
                    "HUBSPOT_ACCESS_TOKEN=token",
                    "HUBSPOT_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env

    def test_import_create_missing_request_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env), "hubspot", "imports", "create", "--file", "file.csv"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("request-file", payload["error"])

    def test_import_create_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)
            request = root / "request.json"
            request.write_text('{"name": "sample"}', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "--apply",
                        "hubspot",
                        "imports",
                        "create",
                        "--request-file",
                        str(request),
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Missing --file for import create", payload["error"])
