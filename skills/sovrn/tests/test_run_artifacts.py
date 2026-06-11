from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sovrn_safe_agent_cli.cli import main


class TestRunArtifacts(unittest.TestCase):
    def test_runs_list_is_empty_without_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("SOVRN_TIMEOUT_S=30\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "runs", "list", "--limit", "5"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)
            self.assertEqual(payload["runs"], [])

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("SOVRN_TIMEOUT_S=30\n", encoding="utf-8")

            run_id = "2026-01-19T120500Z_c0ffee"
            artifacts_dir = root / ".state" / "runs" / run_id
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            (artifacts_dir / "summary.md").write_text("# Seeded run summary\n", encoding="utf-8")
            index_path = root / ".state" / "runs" / "index.jsonl"
            index_row = {
                "ts": "2026-01-19T12:05:00Z",
                "run_id": run_id,
                "artifacts_dir": str(artifacts_dir),
                "tool": "sovrn-safe-cli",
                "version": "0.1.0",
                "command": "sovrn-safe-cli commerce campaigns get --search PRIMARY",
                "env_fingerprint": "commerce_secret=1|commerce_site_key=0|advertising_key=0|advertising_publisher=0",
                "dry_run": None,
                "apply": False,
                "yes": False,
                "ok": True,
                "refused": False,
                "plan_path": None,
                "receipt_path": None,
                "audit_log": None,
                "audit_log_global": None,
            }
            index_path.write_text(json.dumps(index_row) + "\n", encoding="utf-8")

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(["--env-file", str(env_path), "runs", "list", "--limit", "5"])
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(["--env-file", str(env_path), "runs", "show", "--run-id", run_id])
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertEqual(payload3["run"]["run_id"], run_id)
            self.assertIsNotNone(payload3["summary_md"])

    def test_read_only_commands_do_not_create_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("SOVRN_TIMEOUT_S=30\nSOVRN_COMMERCE_SECRET_KEY=abc123\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse((root / ".state").exists())
