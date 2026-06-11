from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from mercury_api_tool.cli import main


class TestFileWriteGates(unittest.TestCase):
    def test_export_transactions_dry_run_does_not_write_file(self) -> None:
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
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "export",
                        "transactions",
                        "--format",
                        "json",
                        "--out",
                        str(out_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(out_path.exists())

    def test_export_transactions_apply_refuses_overwrite_without_yes(self) -> None:
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
            out_path.write_text("[]\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "export",
                        "transactions",
                        "--format",
                        "json",
                        "--out",
                        str(out_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(out_path.read_text(encoding="utf-8"), "[]\n")

    def test_download_invoice_pdf_dry_run_does_not_write_file(self) -> None:
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

            out_path = root / "invoice.pdf"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "invoices",
                        "download-pdf",
                        "--invoice-id",
                        "inv_123",
                        "--out",
                        str(out_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(out_path.exists())
