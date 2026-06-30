from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from wix_safe_agent_cli.cli import main


class TestRunArtifacts(unittest.TestCase):
    def test_auth_token_set_creates_run_folder_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "WIX_API_BASE_URL=http://example.invalid",
                        "WIX_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            token_src = root / "token.json"
            token_src.write_text(
                "{\n  \"access_token\": \"tok-abc\",\n  \"refresh_token\": \"ref-def\"\n}\n",
                encoding="utf-8",
            )

            run_id = "2026-01-19T120000Z_deadbe"

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
                        str(token_src),
                    ]
                )
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["run_id"], run_id)

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())
            self.assertFalse((artifacts_dir / "plan.json").exists())

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            index_text = runs_index.read_text(encoding="utf-8")
            self.assertIn(run_id, index_text)

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("WIX_API_BASE_URL=http://example.invalid\nWIX_TIMEOUT_S=30\n", encoding="utf-8")
            token_src = root / "token.json"
            token_src.write_text(
                "{\n  \"access_token\": \"tok-abc\",\n  \"refresh_token\": \"ref-def\"\n}\n",
                encoding="utf-8",
            )

            run_id = "2026-01-19T120500Z_c0ffee"
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "auth",
                        "token",
                        "set",
                        "--file",
                        str(token_src),
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
            self.assertIsNotNone(payload3["summary_md"])

    def test_validation_error_still_creates_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("WIX_API_BASE_URL=http://example.invalid\nWIX_TIMEOUT_S=30\n", encoding="utf-8")

            run_id = "2026-01-19T121000Z_refuse1"
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
                        str(root / "missing_token.json"),
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("error", payload)

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue((artifacts_dir / "summary.md").exists())
            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))
