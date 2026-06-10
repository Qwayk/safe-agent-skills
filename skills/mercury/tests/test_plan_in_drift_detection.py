from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from mercury_api_tool.cli import main


class TestPlanInDriftDetection(unittest.TestCase):
    def test_export_apply_refuses_when_plan_params_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "MERCURY_API_BASE_URL=https://api.mercury.com/api/v1\n"
                "MERCURY_API_TOKEN=secret-token:TEST_TOKEN_DO_NOT_LEAK\n"
                "MERCURY_AUTH_SCHEME=bearer\n"
                "MERCURY_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            out_path = root / "txns.json"
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "action": "transactions.export",
                        "baseline": {
                            "env_fingerprint": "https://api.mercury.com/api/v1",
                            "request": {
                                "format": "json",
                                "params": {"status": "pending"},
                                "max_pages": 10,
                            },
                            "out": str(out_path),
                        },
                        "files": [{"path": str(out_path), "kind": "export"}],
                    }
                ),
                encoding="utf-8",
            )

            seen: list[str] = []

            def _fake_request(self, method, url, headers=None, params=None, json=None, data=None, timeout=None):  # noqa: ANN001
                seen.append(url)
                raise AssertionError("Network should not be called when plan drift is detected")

            buf = io.StringIO()
            with patch("mercury_api_tool.http.requests.Session.request", new=_fake_request):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--apply",
                            "--plan-in",
                            str(plan_path),
                            "export",
                            "transactions",
                            "--format",
                            "json",
                            "--out",
                            str(out_path),
                            "--status",
                            "posted",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(seen, [])

    def test_statement_download_apply_refuses_when_plan_out_path_drifts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "MERCURY_API_BASE_URL=https://api.mercury.com/api/v1\n"
                "MERCURY_API_TOKEN=secret-token:TEST_TOKEN_DO_NOT_LEAK\n"
                "MERCURY_AUTH_SCHEME=bearer\n"
                "MERCURY_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            planned_out = root / "statement_st_123.pdf"
            plan_path = root / "plan_statement.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "action": "statements.download_pdf",
                        "baseline": {"env_fingerprint": "https://api.mercury.com/api/v1", "request": {"statement_id": "st_123"}},
                        "files": [{"path": str(planned_out), "kind": "pdf"}],
                    }
                ),
                encoding="utf-8",
            )

            seen: list[str] = []

            def _fake_request(self, method, url, headers=None, params=None, json=None, data=None, timeout=None):  # noqa: ANN001
                seen.append(url)
                raise AssertionError("Network should not be called when plan drift is detected")

            buf = io.StringIO()
            with patch("mercury_api_tool.http.requests.Session.request", new=_fake_request):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--apply",
                            "--plan-in",
                            str(plan_path),
                            "statements",
                            "download-pdf",
                            "--statement-id",
                            "st_123",
                            "--out",
                            str(root / "different.pdf"),
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(seen, [])

    def test_attachment_download_apply_refuses_when_attachment_id_drifts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "MERCURY_API_BASE_URL=https://api.mercury.com/api/v1\n"
                "MERCURY_API_TOKEN=secret-token:TEST_TOKEN_DO_NOT_LEAK\n"
                "MERCURY_AUTH_SCHEME=bearer\n"
                "MERCURY_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            planned_out = root / "attachment.pdf"
            plan_path = root / "plan_attachment.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "action": "invoices.attachments.download",
                        "baseline": {
                            "env_fingerprint": "https://api.mercury.com/api/v1",
                            "request": {
                                "attachment_id": "att_123",
                                "file_name": "attachment.pdf",
                                "source_endpoint": "/ar/attachments/att_123",
                            },
                        },
                        "files": [{"path": str(planned_out), "kind": "binary"}],
                    }
                ),
                encoding="utf-8",
            )

            seen: list[str] = []

            def _fake_request(self, method, url, headers=None, params=None, json=None, data=None, timeout=None):  # noqa: ANN001
                seen.append(url)
                raise AssertionError("Network should not be called when plan drift is detected")

            buf = io.StringIO()
            with patch("mercury_api_tool.http.requests.Session.request", new=_fake_request):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--apply",
                            "--plan-in",
                            str(plan_path),
                            "invoices",
                            "download-attachment",
                            "--attachment-id",
                            "att_999",
                            "--out",
                            str(planned_out),
                            "--file-name",
                            "attachment.pdf",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(seen, [])

