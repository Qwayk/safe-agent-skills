from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from x_api_tool.cli import main


class TestDmBulkPolicyRefusals(unittest.TestCase):
    def _write_env(self, d: str) -> Path:
        env = Path(d) / ".env"
        env.write_text("X_API_BASE_URL=https://api.x.com/2\nX_API_TIMEOUT_S=30\n", encoding="utf-8")
        return env

    def test_missing_opt_out_line_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(d)
            csv_path = Path(d) / "job.csv"
            csv_path.write_text("recipient,message,intent_evidence\nalice,Hi,Asked for info\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env), "dm", "bulk-send", "--csv", str(csv_path)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload.get("refused"))

    def test_missing_evidence_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(d)
            csv_path = Path(d) / "job.csv"
            csv_path.write_text("recipient,message,intent_evidence\nalice,Hi,\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env),
                        "dm",
                        "bulk-send",
                        "--csv",
                        str(csv_path),
                        "--opt-out-line",
                        "Reply STOP to opt out.",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload.get("refused"))

    def test_all_required_fields_produces_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(d)
            csv_path = Path(d) / "job.csv"
            csv_path.write_text("recipient,message,intent_evidence\nalice,Hi,Asked for info\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env),
                        "dm",
                        "bulk-send",
                        "--csv",
                        str(csv_path),
                        "--opt-out-line",
                        "Reply STOP to opt out.",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload.get("dry_run"))
            self.assertIn("plan", payload)

