from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from amazon_creators_api_tool.cli import main


def _write_env(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "AMAZON_CREATORS_CREDENTIAL_ID=test-id",
                "AMAZON_CREATORS_CREDENTIAL_SECRET=secret",
                "AMAZON_CREATORS_CREDENTIAL_VERSION=2.x",
                "AMAZON_CREATORS_LOCALE=us",
                "AMAZON_CREATORS_TIMEOUT_S=1",
                "AMAZON_CREATORS_PARTNER_TAG=test-partner",
                "AMAZON_CREATORS_PARTNER_TYPE=Associates",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class TestRunArtifacts(unittest.TestCase):
    def test_runs_list_returns_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            _write_env(env_path)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "runs", "list", "--limit", "5"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertIn("count", payload)
            self.assertGreaterEqual(payload["count"], 0)

    def test_runs_show_handles_missing_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            _write_env(env_path)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "runs", "show", "--run-id", "missing"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload.get("error_type"), "NotFound")
