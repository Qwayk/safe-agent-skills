from __future__ import annotations

import io
import json
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

from qdrant_cloud_api_tool.cli import main


class _StubHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj: dict) -> None:
        data = json.dumps(obj).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/account/v1/accounts":
            self._send_json({"api_key": "SHOULD_REDACT"})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/account/v1/accounts":
            self._send_json({"token": "SHOULD_REDACT"})
            return
        if "/backups/" in self.path and self.path.endswith("/restore"):
            self._send_json({"token": "SHOULD_REDACT"})
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, _fmt: str, *_args) -> None:  # silence stderr
        return


def _start_server() -> tuple[HTTPServer, threading.Thread]:
    server = HTTPServer(("127.0.0.1", 0), _StubHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, t


class TestRedaction(unittest.TestCase):
    def test_response_and_plan_and_receipt_are_redacted(self) -> None:
        server, _t = _start_server()
        try:
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            with TemporaryDirectory() as td:
                root = Path(td)
                env_path = root / ".env"
                env_path.write_text(
                    "\n".join(
                        [
                            f"QDRANT_CLOUD_API_BASE_URL={base_url}",
                            "QDRANT_CLOUD_API_KEY=REAL_SECRET_KEY_SHOULD_NOT_APPEAR",
                            "QDRANT_CLOUD_TIMEOUT_S=30",
                        ]
                    )
                    + "\n",
                    encoding="utf-8",
                )

                # Live GET response redaction
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "--live", "account-v1", "list-accounts"])
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["response"]["api_key"], "<REDACTED>")

                # Backup/restore apply with plan/provider-receipt outputs written to disk and redacted.
                req_path = root / "req.json"
                req_path.write_text(json.dumps({"api_key": "REQ_SECRET"}), encoding="utf-8")
                plan_out = root / "plan.json"
                receipt_out = root / "receipt.json"

                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--live",
                            "--apply",
                            "--plan-out",
                            str(plan_out),
                            "--receipt-out",
                            str(receipt_out),
                            "cluster-backup-v1",
                            "restore-backup",
                            "--account-id",
                            "00000000-0000-0000-0000-000000000000",
                            "--backup-id",
                            "11111111-1111-1111-1111-111111111111",
                            "--request-json",
                            str(req_path),
                        ]
                    )
                self.assertEqual(rc2, 0)

                plan_obj = json.loads(plan_out.read_text(encoding="utf-8"))
                self.assertEqual(plan_obj["request"]["api_key"], "<REDACTED>")

                receipt_obj = json.loads(receipt_out.read_text(encoding="utf-8"))
                # Response comes from stub and must be redacted.
                self.assertEqual(receipt_obj["response"]["token"], "<REDACTED>")
                # Never leak the env API key anywhere in artifacts.
                self.assertNotIn("REAL_SECRET_KEY_SHOULD_NOT_APPEAR", plan_out.read_text(encoding="utf-8"))
                self.assertNotIn("REAL_SECRET_KEY_SHOULD_NOT_APPEAR", receipt_out.read_text(encoding="utf-8"))
        finally:
            server.shutdown()
            server.server_close()
