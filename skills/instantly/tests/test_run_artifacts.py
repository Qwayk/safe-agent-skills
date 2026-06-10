from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from instantly_api_tool.cli import main


class TestRunArtifacts(unittest.TestCase):
    def test_write_dry_run_creates_run_folder_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "INSTANTLY_API_BASE_URL=http://example.invalid",
                        "INSTANTLY_API_KEY=test_api_key",
                        "INSTANTLY_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            run_id = "2026-01-19T120000Z_deadbe"
            campaign_json = root / "campaign.json"
            campaign_json.write_text('{"name":"Test"}\n', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "campaigns",
                        "create",
                        "--file",
                        str(campaign_json),
                    ]
                )
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["run_id"], run_id)

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            index_text = runs_index.read_text(encoding="utf-8")
            self.assertIn(run_id, index_text)

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "INSTANTLY_API_BASE_URL=http://example.invalid\nINSTANTLY_API_KEY=test_api_key\nINSTANTLY_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            campaign_json = root / "campaign.json"
            campaign_json.write_text('{"name":"Test"}\n', encoding="utf-8")

            run_id = "2026-01-19T120500Z_c0ffee"
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "campaigns",
                        "create",
                        "--file",
                        str(campaign_json),
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

    def test_refusal_still_creates_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "INSTANTLY_API_BASE_URL=http://example.invalid\nINSTANTLY_API_KEY=test_api_key\nINSTANTLY_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            leads_json = root / "leads.json"
            leads_json.write_text('[{"email":"a@example.com"}]\n', encoding="utf-8")

            run_id = "2026-01-19T121000Z_refuse1"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--apply",
                        "leads",
                        "add-bulk",
                        "--campaign-id",
                        "C1",
                        "--json",
                        str(leads_json),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue((artifacts_dir / "summary.md").exists())
            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))
