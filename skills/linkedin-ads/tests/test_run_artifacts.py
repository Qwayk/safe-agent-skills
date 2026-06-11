from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from linkedin_ads_api_tool.cli import main


class TestLinkedInRunArtifacts(unittest.TestCase):
    def test_write_dry_run_records_run_artifacts_and_runs_commands(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "LINKEDIN_ADS_LINKEDIN_VERSION=202605",
                        "LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION=2.0.0",
                        "LINKEDIN_ADS_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            run_id = "2026-01-19T120000Z_linkedintest"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--output",
                        "json",
                        "ad-accounts",
                        "create",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertTrue(payload["plan"]["before_state"]["required"])
            self.assertFalse(payload["plan"]["before_state"]["supported"])

            run_dir = root / ".state" / "runs" / run_id
            self.assertTrue(run_dir.exists())
            self.assertTrue((run_dir / "plan.json").exists())
            self.assertFalse((run_dir / "receipt.json").exists())
            self.assertTrue((run_dir / "summary.md").exists())
            self.assertTrue((run_dir / "audit.jsonl").exists())

            runs_index = root / ".state" / "runs" / "index.jsonl"
            self.assertTrue(runs_index.exists())
            rows = [
                json.loads(line)
                for line in runs_index.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertTrue(any(row.get("run_id") == run_id for row in rows))

            list_buf = io.StringIO()
            with redirect_stdout(list_buf):
                list_rc = main(["--env-file", str(env_path), "--output", "json", "runs", "list", "--limit", "10"])
            self.assertEqual(list_rc, 0)
            list_payload = json.loads(list_buf.getvalue())
            self.assertTrue(list_payload["ok"])
            self.assertTrue(any(row["run_id"] == run_id for row in list_payload["runs"]))

            show_buf = io.StringIO()
            with redirect_stdout(show_buf):
                show_rc = main(["--env-file", str(env_path), "--output", "json", "runs", "show", "--run-id", run_id])
            self.assertEqual(show_rc, 0)
            show_payload = json.loads(show_buf.getvalue())
            self.assertTrue(show_payload["ok"])
            self.assertEqual(show_payload["run"]["run_id"], run_id)
            self.assertIsNotNone(show_payload["summary_md"])
