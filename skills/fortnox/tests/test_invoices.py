from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from fortnox_api_tool.cli import main


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _api_response(*, status: int, path: str, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestInvoicesWrites(unittest.TestCase):
    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict[str, object]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", str(env_path), *args])
        text = buf.getvalue().strip()
        self.assertTrue(text, "Command did not emit JSON output")
        return rc, json.loads(text)

    def _plan_from_output(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan = payload.get("plan")
        if isinstance(plan, dict):
            return plan
        plan_out = payload.get("plan_out") or payload.get("plan_path")
        self.assertTrue(plan_out)
        self.assertIsInstance(plan_out, str)
        return json.loads(Path(plan_out).read_text(encoding="utf-8"))

    def _make_invoice_payload(self, path: Path, *, document_number: str = "I-1001") -> None:
        payload = {
            "Invoice": {
                "DocumentNumber": document_number,
                "InvoiceDate": "2026-06-09",
                "DueDate": "2026-06-09",
                "CustomerNumber": "1",
                "Currency": "SEK",
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_invoices_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "invoice.json"
            self._make_invoice_payload(payload_path)
            expected_hash = _sha256(payload_path)

            rc, payload = self._run(
                env_path=env_path,
                args=["invoices", "create", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)

    def test_invoices_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "invoice.json"
            self._make_invoice_payload(payload_path)

            with patch("fortnox_api_tool.commands.invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["invoices", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "Invoice": {
                                "DocumentNumber": "I-1001",
                                "InvoiceDate": "2026-06-10",
                                "DueDate": "2026-06-10",
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
        self.assertEqual(request_json.call_count, 0)

    def test_invoices_bookkeep_apply_performs_put_and_verifies_booked_true(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["invoices", "bookkeep", "--document-number", "I-1001", "--yes"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/invoices/I-1001/bookkeep", body={"Invoice": {"DocumentNumber": "I-1001"}}),
                    _api_response(
                        status=200,
                        path="/invoices/I-1001",
                        body={"Invoice": {"DocumentNumber": "I-1001", "Booked": True}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "bookkeep",
                        "--document-number",
                        "I-1001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/invoices/I-1001")
        self.assertTrue(payload_apply["receipt"].get("verification_booked_true"))

    def test_invoices_cancel_apply_fails_when_cancelled_not_set(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["invoices", "cancel", "--document-number", "I-1001", "--yes"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/invoices/I-1001/cancel", body={"Invoice": {"DocumentNumber": "I-1001"}}),
                    _api_response(
                        status=200,
                        path="/invoices/I-1001",
                        body={"Invoice": {"DocumentNumber": "I-1001", "Cancelled": False}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "cancel",
                        "--document-number",
                        "I-1001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 1)
        self.assertFalse(payload_apply.get("ok", True))
        self.assertFalse(payload_apply["receipt"].get("verification_cancelled_true"))

    def test_invoices_update_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "invoice.json"
            self._make_invoice_payload(payload_path)

            with patch("fortnox_api_tool.commands.invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["invoices", "update", "--document-number", "I-1001", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/invoices/I-1001", body={"Invoice": {"DocumentNumber": "I-1001"}}),
                    _api_response(status=200, path="/invoices/I-1001", body={"Invoice": {"DocumentNumber": "I-1001"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "update",
                        "--document-number",
                        "I-1001",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "PUT")
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/invoices/I-1001")

    def test_invoices_credit_apply_verifies_credit_reference_present(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["invoices", "credit", "--document-number", "I-1001", "--yes"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/invoices/I-1001/credit",
                        body={"Invoice": {"DocumentNumber": "I-1001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/invoices/I-1001",
                        body={"Invoice": {"DocumentNumber": "I-1001", "Credit": True, "CreditReference": 3001}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "credit",
                        "--document-number",
                        "I-1001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertTrue(payload_apply["receipt"].get("verification_credit_reference_present"))

    def test_invoices_warehouseready_apply_verifies_true(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["invoices", "warehouseready", "--document-number", "I-1001", "--yes"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/invoices/I-1001/warehouseready",
                        body={"Invoice": {"DocumentNumber": "I-1001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/invoices/I-1001",
                        body={"Invoice": {"DocumentNumber": "I-1001", "WarehouseReady": True}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "warehouseready",
                        "--document-number",
                        "I-1001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertTrue(payload_apply["receipt"].get("verification_warehouseready_true"))

    def test_invoices_externalprint_apply_verifies_sent_true(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["invoices", "externalprint", "--document-number", "I-1001", "--yes"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/invoices/I-1001/externalprint",
                        body={"Invoice": {"DocumentNumber": "I-1001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/invoices/I-1001",
                        body={"Invoice": {"DocumentNumber": "I-1001", "Sent": True}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "externalprint",
                        "--document-number",
                        "I-1001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertTrue(payload_apply["receipt"].get("verification_sent_true"))

    def test_invoices_send_as_e_invoice_apply_verifies_sent_true(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["invoices", "send-an-invoice-as-e-invoice", "--document-number", "I-1001", "--yes"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/invoices/I-1001/einvoice",
                        body={"Invoice": {"DocumentNumber": "I-1001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/invoices/I-1001",
                        body={"Invoice": {"DocumentNumber": "I-1001", "Sent": True}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "send-an-invoice-as-e-invoice",
                        "--document-number",
                        "I-1001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertTrue(payload_apply["receipt"].get("verification_sent_true"))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/invoices/I-1001/einvoice")

    def test_invoices_send_as_e_print_apply_verifies_sent_true(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["invoices", "send-an-invoice-as-e-print", "--document-number", "I-1001", "--yes"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/invoices/I-1001/eprint",
                        body={"Invoice": {"DocumentNumber": "I-1001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/invoices/I-1001",
                        body={"Invoice": {"DocumentNumber": "I-1001", "Sent": True}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "send-an-invoice-as-e-print",
                        "--document-number",
                        "I-1001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertTrue(payload_apply["receipt"].get("verification_sent_true"))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/invoices/I-1001/eprint")

    def test_invoices_send_as_email_apply_verifies_sent_true(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["invoices", "send-an-invoice-as-email", "--document-number", "I-1001", "--yes"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/invoices/I-1001/email",
                        body={"Invoice": {"DocumentNumber": "I-1001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/invoices/I-1001",
                        body={"Invoice": {"DocumentNumber": "I-1001", "Sent": True}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "invoices",
                        "send-an-invoice-as-email",
                        "--document-number",
                        "I-1001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertTrue(payload_apply["receipt"].get("verification_sent_true"))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/invoices/I-1001/email")
