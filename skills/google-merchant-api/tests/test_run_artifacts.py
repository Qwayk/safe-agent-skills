from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_merchant_api_tool.cli import main


class TestRunArtifacts(unittest.TestCase):
    def test_merchant_insert_write_creates_run_folder_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "GOOGLE_MERCHANT_API_BASE_URL=http://example.invalid",
                        "GOOGLE_MERCHANT_API_TIMEOUT_S=30",
                    ]
                )
                + "\n",
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
                        "accounts",
                        "product-inputs",
                        "insert",
                        "--parent",
                        "accounts/123456",
                        "--body-json",
                        json.dumps(
                            {
                                "channel": "ONLINE",
                                "contentLanguage": "en",
                                "offerId": "SKU-RED-123",
                                "feedLabel": "US",
                            }
                        ),
                    ]
                )
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["run_id"], run_id)
            self.assertTrue(payload["plan"]["before_state"]["required"])
            self.assertFalse(payload["plan"]["before_state"]["supported"])
            self.assertEqual(payload["plan"]["verification_plan"]["mode"], "best_effort_after_apply")

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            index_text = runs_index.read_text(encoding="utf-8")
            self.assertIn(run_id, index_text)

    def test_runs_list_and_show_work_for_discovery_command(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GOOGLE_MERCHANT_API_BASE_URL=http://example.invalid\nGOOGLE_MERCHANT_API_TIMEOUT_S=30\n", encoding="utf-8")

            run_id = "2026-01-19T120500Z_c0ffee"
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "accounts",
                        "product-inputs",
                        "insert",
                        "--parent",
                        "accounts/123456",
                        "--body-json",
                        json.dumps(
                            {
                                "channel": "ONLINE",
                                "contentLanguage": "en",
                                "offerId": "SKU-RED-123",
                                "feedLabel": "US",
                            }
                        ),
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
            env_path.write_text("GOOGLE_MERCHANT_API_BASE_URL=http://example.invalid\nGOOGLE_MERCHANT_API_TIMEOUT_S=30\n", encoding="utf-8")

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
                        "accounts",
                        "conversion-sources",
                        "delete",
                        "--name",
                        "accounts/123456/conversionSources/abc",
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

    def test_apply_refusal_for_discovery_command_creates_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            sa_path = root / "service-account.json"
            sa_path.write_text("{}", encoding="utf-8")
            env_path.write_text(
                "\n".join(
                    [
                        "GOOGLE_MERCHANT_API_BASE_URL=http://example.invalid",
                        "GOOGLE_MERCHANT_API_AUTH_MODE=service_account_json",
                        f"GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON={sa_path}",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch(
                "google_merchant_api_tool.commands.discovery.load_credentials_from_config",
            ) as mock_load_creds:
                with patch("google_merchant_api_tool.commands.discovery.HttpClient") as mock_http_client:
                    run_id = "2026-06-04T123000Z_write_refusal"
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(
                            [
                                "--env-file",
                                str(env_path),
                                "--run-id",
                                run_id,
                                "--apply",
                                "--output",
                                "json",
                                "accounts",
                                "product-inputs",
                                "insert",
                                "--parent",
                                "accounts/123456",
                                "--body-json",
                                json.dumps(
                                    {
                                        "channel": "ONLINE",
                                        "contentLanguage": "en",
                                        "offerId": "SKU-RED-123",
                                        "feedLabel": "US",
                                    }
                                ),
                            ]
                        )
                    self.assertEqual(rc, 0)

                    payload = json.loads(buf.getvalue())
                    self.assertTrue(payload["ok"])
                    self.assertTrue(payload["refused"])
                    self.assertIn("before-state snapshot", payload["reasons"][0])
                    self.assertIn("ack-no-snapshot", payload["reasons"][0])
                    self.assertEqual(payload["run_id"], run_id)
                    self.assertNotIn("receipt", payload)

                    artifacts_dir = Path(payload["artifacts_dir"])
                    self.assertTrue((artifacts_dir / "summary.md").exists())
                    self.assertTrue((artifacts_dir / "audit.jsonl").exists())
                    self.assertFalse((artifacts_dir / "receipt.json").exists())
                    runs_index = Path(payload["runs_index"])
                    self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))

                    mock_load_creds.assert_not_called()
                    mock_http_client.assert_not_called()
