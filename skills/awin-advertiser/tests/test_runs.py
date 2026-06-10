from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from awin_advertiser_safe_agent_cli.cli import main
from awin_advertiser_safe_agent_cli.runs import append_index_row, runs_index_path_for_env_file


class TestRuns(unittest.TestCase):
    def test_runs_list_without_index_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "runs", "list", "--limit", "5"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

    def test_runs_show_returns_created_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\n", encoding="utf-8")
            run_index = runs_index_path_for_env_file(str(env_path))
            append_index_row(
                run_index,
                {
                    "ts": "2026-06-09T120000Z",
                    "run_id": "abc",
                    "artifacts_dir": str(Path(td) / ".state" / "runs" / "abc"),
                    "tool": "awin-advertiser-safe-cli",
                    "version": "0.1.1",
                    "command": "auth check",
                    "env_fingerprint": "https://api.awin.com",
                    "dry_run": True,
                    "apply": False,
                    "yes": False,
                    "ok": True,
                    "refused": False,
                    "plan_path": None,
                    "receipt_path": None,
                    "audit_log": None,
                    "audit_log_global": None,
                },
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "runs", "show", "--run-id", "abc"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["run"]["run_id"], "abc")
