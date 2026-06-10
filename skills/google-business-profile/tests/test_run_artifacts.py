from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from google_business_profile_safe_agent_cli.cli import main


class TestRunArtifacts(unittest.TestCase):
    def test_token_set_creates_run_folder_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\nGBP_OAUTH_SCOPES=https://www.googleapis.com/auth/business.manage\n", encoding="utf-8")

            src_token = root / "token.json"
            src_token.write_text(
                json.dumps(
                    {
                        "token": "abc",
                        "refresh_token": "def",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "client_id": "client-id",
                        "client_secret": "client-secret",
                        "scopes": ["https://www.googleapis.com/auth/business.manage"],
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            run_id = "2026-01-19T120000Z_run_artifacts"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "auth",
                        "token",
                        "set",
                        "--file",
                        str(src_token),
                    ]
                )
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["run_id"], run_id)
            self.assertTrue(payload["ok"])

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\nGBP_OAUTH_SCOPES=https://www.googleapis.com/auth/business.manage\n", encoding="utf-8")

            src_token = root / "token.json"
            src_token.write_text(
                json.dumps(
                    {
                        "token": "abc",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "scopes": ["https://www.googleapis.com/auth/business.manage"],
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            run_id = "2026-01-19T120100Z_runs"

            with redirect_stdout(io.StringIO()):
                main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "auth",
                        "token",
                        "set",
                        "--file",
                        str(src_token),
                    ]
                )

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
