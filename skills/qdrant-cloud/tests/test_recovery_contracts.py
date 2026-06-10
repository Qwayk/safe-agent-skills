from __future__ import annotations

import io
import json
import threading
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from qdrant_cloud_api_tool.cli import main


class _RecoveryStubHandler(BaseHTTPRequestHandler):
    post_paths: list[str] = []

    def _send_json(self, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/account/v1/accounts":
            self._send_json({"items": [{"id": "acct", "name": "Example"}]})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        self.__class__.post_paths.append(self.path)
        if self.path == "/api/account/v1/accounts":
            self._send_json({"account": {"id": "00000000-0000-0000-0000-000000000000", "name": "Example"}})
            return
        if "/backups/" in self.path and self.path.endswith("/restore"):
            self._send_json({"restore": "started"})
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, _fmt: str, *_args) -> None:
        return


def _start_server() -> tuple[HTTPServer, threading.Thread]:
    server = HTTPServer(("127.0.0.1", 0), _RecoveryStubHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, t


class TestRecoveryContracts(unittest.TestCase):
    def test_ordinary_write_plan_and_apply_refusal_have_no_recovery_contract(self) -> None:
        _RecoveryStubHandler.post_paths = []
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
                            "QDRANT_CLOUD_API_KEY=dummy-key",
                            "QDRANT_CLOUD_TIMEOUT_S=30",
                        ]
                    )
                    + "\n",
                    encoding="utf-8",
                )

                req_path = root / "request.json"
                req_path.write_text(json.dumps({"account": {"name": "Example"}}), encoding="utf-8")

                plan_out = root / "plan.json"
                receipt_out = root / "receipt.json"

                buf_plan = io.StringIO()
                with redirect_stdout(buf_plan):
                    rc_plan = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--plan-out",
                            str(plan_out),
                            "account-v1",
                            "create-account",
                            "--request-json",
                            str(req_path),
                        ]
                    )
                self.assertEqual(rc_plan, 0)
                payload_plan = json.loads(buf_plan.getvalue())
                self.assertEqual(payload_plan["plan"]["safety"]["recovery"]["contract"], "no-recovery")
                self.assertTrue(payload_plan["plan"]["safety"]["before_state"]["required"])
                self.assertFalse(payload_plan["plan"]["safety"]["before_state"]["supported"])
                self.assertEqual(payload_plan["plan"]["verification_plan"]["type"], "best_effort_after_apply")

                plan_obj = json.loads(plan_out.read_text(encoding="utf-8"))
                self.assertEqual(plan_obj["safety"]["recovery"]["contract"], "no-recovery")
                self.assertEqual(plan_obj["safety"]["before_state"]["status"], "no_snapshot_available")

                buf_apply = io.StringIO()
                with redirect_stdout(buf_apply):
                    rc_apply = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--live",
                            "--apply",
                            "--plan-in",
                            str(plan_out),
                            "--receipt-out",
                            str(receipt_out),
                            "account-v1",
                            "create-account",
                            "--request-json",
                            str(req_path),
                        ]
                    )
                self.assertEqual(rc_apply, 0)
                payload_apply = json.loads(buf_apply.getvalue())
                self.assertTrue(payload_apply["ok"])
                self.assertTrue(payload_apply["refused"])
                self.assertFalse(payload_apply["dry_run"])
                self.assertIn("before-state snapshot", " ".join(payload_apply["reasons"]))
                self.assertFalse(receipt_out.exists())
                self.assertEqual(_RecoveryStubHandler.post_paths, [])
        finally:
            server.shutdown()
            server.server_close()

    def test_backup_family_plan_and_receipt_have_provider_backup_restore_contract(self) -> None:
        _RecoveryStubHandler.post_paths = []
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
                            "QDRANT_CLOUD_API_KEY=dummy-key",
                            "QDRANT_CLOUD_TIMEOUT_S=30",
                        ]
                    )
                    + "\n",
                    encoding="utf-8",
                )

                req_path = root / "request.json"
                req_path.write_text(json.dumps({"snapshot": "example"}), encoding="utf-8")

                plan_out = root / "plan.json"
                receipt_out = root / "receipt.json"

                buf_plan = io.StringIO()
                with redirect_stdout(buf_plan):
                    rc_plan = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--plan-out",
                            str(plan_out),
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
                self.assertEqual(rc_plan, 0)
                payload_plan = json.loads(buf_plan.getvalue())
                self.assertEqual(payload_plan["plan"]["safety"]["recovery"]["contract"], "provider-backup-restore")
                self.assertFalse(payload_plan["plan"]["safety"]["before_state"]["required"])
                self.assertTrue(payload_plan["plan"]["safety"]["before_state"]["supported"])

                plan_obj = json.loads(plan_out.read_text(encoding="utf-8"))
                self.assertEqual(plan_obj["safety"]["recovery"]["contract"], "provider-backup-restore")
                self.assertIn("backup/restore", plan_obj["safety"]["recovery"]["details"])
                self.assertEqual(plan_obj["safety"]["before_state"]["status"], "provider-backup-restore-family")

                buf_apply = io.StringIO()
                with redirect_stdout(buf_apply):
                    rc_apply = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--live",
                            "--apply",
                            "--plan-in",
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
                self.assertEqual(rc_apply, 0)
                payload_apply = json.loads(buf_apply.getvalue())
                self.assertTrue(payload_apply["ok"])
                self.assertFalse(payload_apply.get("refused", False))
                self.assertEqual(payload_apply["receipt"]["safety"]["recovery"]["contract"], "provider-backup-restore")
                self.assertEqual(payload_apply["receipt"]["safety"]["before_state"]["status"], "provider-backup-restore-family")

                receipt_obj = json.loads(receipt_out.read_text(encoding="utf-8"))
                self.assertEqual(receipt_obj["safety"]["recovery"]["contract"], "provider-backup-restore")
                self.assertTrue(receipt_obj["safety"]["before_state"]["supported"])
                self.assertTrue(
                    any(
                        p.endswith("/backups/11111111-1111-1111-1111-111111111111/restore")
                        for p in _RecoveryStubHandler.post_paths
                    )
                )
        finally:
            server.shutdown()
            server.server_close()
