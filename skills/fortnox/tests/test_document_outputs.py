from __future__ import annotations

import base64
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fortnox_api_tool.cli import main


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TestDocumentOutputs(unittest.TestCase):
    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", str(env_path), *args])
        text = buf.getvalue().strip()
        self.assertTrue(text, "Command did not emit JSON output")
        return rc, json.loads(text)

    def _write_env(self, directory: str) -> Path:
        env_path = Path(directory) / ".env"
        env_path.write_text(
            "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
            encoding="utf-8",
        )
        return env_path

    def test_invoices_preview_emits_base64_pdf_payload(self) -> None:
        pdf_bytes = b"%PDF-1.7 invoice preview"
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.accounting_reads.request_raw") as request_raw:
                request_raw.return_value = {
                    "status": 200,
                    "url": "https://api.fortnox.se/3/invoices/I-1001/preview",
                    "token_source": "env",
                    "token_expired": None,
                    "content_type": "application/pdf",
                    "body_bytes": pdf_bytes,
                }
                rc, payload = self._run(
                    env_path=env_path,
                    args=["invoices", "preview", "--document-number", "I-1001"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/invoices/I-1001/preview")
        self.assertEqual(payload["content_type"], "application/pdf")
        self.assertEqual(payload["byte_count"], len(pdf_bytes))
        self.assertEqual(payload["sha256"], _sha256_bytes(pdf_bytes))
        self.assertEqual(payload["data_encoding"], "base64")
        self.assertEqual(payload["data_base64"], base64.b64encode(pdf_bytes).decode("ascii"))
        self.assertEqual(request_raw.call_args.kwargs["path"], "/invoices/I-1001/preview")

    def test_invoices_print_reminder_writes_output_file(self) -> None:
        pdf_bytes = b"%PDF-1.7 invoice reminder"
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            output_path = Path(td) / "downloads" / "invoice-reminder.pdf"
            with patch("fortnox_api_tool.commands.accounting_reads.request_raw") as request_raw:
                request_raw.return_value = {
                    "status": 200,
                    "url": "https://api.fortnox.se/3/invoices/I-1001/printreminder",
                    "token_source": "env",
                    "token_expired": None,
                    "content_type": "application/pdf",
                    "body_bytes": pdf_bytes,
                }
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "print-reminder",
                        "--document-number",
                        "I-1001",
                        "--output-file",
                        str(output_path),
                    ],
                )
                self.assertEqual(rc, 0)
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["path"], "/invoices/I-1001/printreminder")
                self.assertEqual(payload["output_file"], str(output_path))
                self.assertTrue(output_path.exists())
                self.assertEqual(output_path.read_bytes(), pdf_bytes)
                self.assertNotIn("data_base64", payload)

    def test_invoices_print_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.accounting_reads.request_raw") as request_raw:
                request_raw.return_value = {
                    "status": 200,
                    "url": "https://api.fortnox.se/3/invoices/I-1001/print",
                    "token_source": "env",
                    "token_expired": None,
                    "content_type": "application/pdf",
                    "body_bytes": b"%PDF-1.7 invoice print",
                }
                rc, payload = self._run(
                    env_path=env_path,
                    args=["invoices", "print", "--document-number", "I-1001"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(request_raw.call_args.kwargs["path"], "/invoices/I-1001/print")

    def test_offers_preview_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.accounting_reads.request_raw") as request_raw:
                request_raw.return_value = {
                    "status": 200,
                    "url": "https://api.fortnox.se/3/offers/O-1001/preview",
                    "token_source": "env",
                    "token_expired": None,
                    "content_type": "application/pdf",
                    "body_bytes": b"%PDF-1.7 offer preview",
                }
                rc, payload = self._run(
                    env_path=env_path,
                    args=["offers", "preview", "--document-number", "O-1001"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(request_raw.call_args.kwargs["path"], "/offers/O-1001/preview")

    def test_offers_print_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.accounting_reads.request_raw") as request_raw:
                request_raw.return_value = {
                    "status": 200,
                    "url": "https://api.fortnox.se/3/offers/O-1001/print",
                    "token_source": "env",
                    "token_expired": None,
                    "content_type": "application/pdf",
                    "body_bytes": b"%PDF-1.7 offer print",
                }
                rc, payload = self._run(
                    env_path=env_path,
                    args=["offers", "print", "--document-number", "O-1001"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(request_raw.call_args.kwargs["path"], "/offers/O-1001/print")

    def test_orders_preview_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.accounting_reads.request_raw") as request_raw:
                request_raw.return_value = {
                    "status": 200,
                    "url": "https://api.fortnox.se/3/orders/OR-1001/preview",
                    "token_source": "env",
                    "token_expired": None,
                    "content_type": "application/pdf",
                    "body_bytes": b"%PDF-1.7 order preview",
                }
                rc, payload = self._run(
                    env_path=env_path,
                    args=["orders", "preview", "--document-number", "OR-1001"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(request_raw.call_args.kwargs["path"], "/orders/OR-1001/preview")

    def test_orders_print_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.accounting_reads.request_raw") as request_raw:
                request_raw.return_value = {
                    "status": 200,
                    "url": "https://api.fortnox.se/3/orders/OR-1001/print",
                    "token_source": "env",
                    "token_expired": None,
                    "content_type": "application/pdf",
                    "body_bytes": b"%PDF-1.7 order print",
                }
                rc, payload = self._run(
                    env_path=env_path,
                    args=["orders", "print", "--document-number", "OR-1001"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(request_raw.call_args.kwargs["path"], "/orders/OR-1001/print")
