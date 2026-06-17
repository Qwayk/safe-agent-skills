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


class TestSupplierInvoicePayments(unittest.TestCase):
    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict[str, Any]]:
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

    def _make_payload_file(self, path: Path, *, number: str, booked: bool = False) -> None:
        payload = {
            "SupplierInvoicePayment": {
                "Number": number,
                "InvoiceNumber": 1001,
                "Amount": 1000.0,
                "PaymentDate": "2026-06-09",
                "ModeOfPayment": "BG",
                "Booked": booked,
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_supplier_invoice_payments_list_calls_expected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.supplier_invoice_payments.get_json") as get_json:
                get_json.return_value = _api_response(
                    status=200,
                    path="/supplierinvoicepayments",
                    body={"SupplierInvoicePayments": []},
                )
                rc, payload = self._run(env_path=env_path, args=["supplier-invoice-payments", "list"])

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/supplierinvoicepayments")
            self.assertEqual(payload["http_status"], 200)
            self.assertEqual(payload["data"], {"SupplierInvoicePayments": []})
            get_json.assert_called_once_with(ctx=unittest.mock.ANY, path="/supplierinvoicepayments")

    def test_supplier_invoice_payments_get_calls_expected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.supplier_invoice_payments.get_json") as get_json:
                get_json.return_value = _api_response(
                    status=200,
                    path="/supplierinvoicepayments/42",
                    body={"SupplierInvoicePayment": {"Number": "42"}},
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-payments", "get", "--number", "42"],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/supplierinvoicepayments/42")
            self.assertEqual(payload["http_status"], 200)
            self.assertEqual(payload["data"], {"SupplierInvoicePayment": {"Number": "42"}})
            get_json.assert_called_once_with(ctx=unittest.mock.ANY, path="/supplierinvoicepayments/42")

    def test_supplier_invoice_payments_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-payments", "create", "--json-file", str(payload_path)],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), _sha256(payload_path))
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoice_payments_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-payments", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "SupplierInvoicePayment": {
                                "Number": "42",
                                "InvoiceNumber": 1001,
                                "Amount": 2000.0,
                                "PaymentDate": "2026-06-09",
                                "ModeOfPayment": "BG",
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
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

    def test_supplier_invoice_payments_create_apply_performs_post_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-payments", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/supplierinvoicepayments",
                        body={"SupplierInvoicePayment": {"Number": "42"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoicepayments/42",
                        body={"SupplierInvoicePayment": {"Number": "42", "Booked": False}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "POST")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")

    def test_supplier_invoice_payments_update_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "update",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/supplierinvoicepayments/42",
                        body={"SupplierInvoicePayment": {"Number": "42", "Booked": False}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoicepayments/42",
                        body={"SupplierInvoicePayment": {"Number": "42", "Booked": False}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "update",
                        "--number",
                        "42",
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
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")

    def test_supplier_invoice_payments_update_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "update",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), _sha256(payload_path))
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoice_payments_update_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "update",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "SupplierInvoicePayment": {
                                "Number": "42",
                                "InvoiceNumber": 1001,
                                "Amount": 2000.0,
                                "PaymentDate": "2026-06-09",
                                "ModeOfPayment": "BG",
                                "Booked": False,
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "update",
                        "--number",
                        "42",
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

    def test_supplier_invoice_payments_update_rejects_number_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, number="99")

            rc, payload = self._run(
                env_path=env_path,
                args=[
                    "supplier-invoice-payments",
                    "update",
                    "--number",
                    "42",
                    "--json-file",
                    str(payload_path),
                ],
            )

            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("must match --number", payload["error"])

    def test_supplier_invoice_payments_remove_apply_refuses_without_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-payments", "remove", "--number", "42"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_refused, payload_refused = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "remove",
                        "--number",
                        "42",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_refused, 0)
            self.assertTrue(payload_refused.get("refused", False))
            self.assertIn("ack-irreversible", " ".join(payload_refused["reasons"]).lower())
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoice_payments_remove_apply_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-payments", "remove", "--number", "42"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_refused, payload_refused = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "remove",
                        "--number",
                        "42",
                        "--apply",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_refused, 0)
            self.assertTrue(payload_refused.get("refused", False))
            self.assertIn("--apply --yes", " ".join(payload_refused["reasons"]))
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoice_payments_remove_apply_performs_delete_and_404_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-payments", "remove", "--number", "42"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=204, path="/supplierinvoicepayments/42", body={}),
                    RuntimeError("HTTP 404 for GET https://api.fortnox.se/3/supplierinvoicepayments/42"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "remove",
                        "--number",
                        "42",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "DELETE")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")

    def test_supplier_invoice_payments_bookkeep_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "bookkeep.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "bookkeep",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("risk_level"), "high")
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoice_payments_bookkeep_apply_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "bookkeep.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "bookkeep",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_refused, payload_refused = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "bookkeep",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_refused, 0)
            self.assertTrue(payload_refused.get("refused", False))
            self.assertIn("--apply --yes", " ".join(payload_refused["reasons"]))
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoice_payments_bookkeep_rejects_number_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "bookkeep.json"
            self._make_payload_file(payload_path, number="99")

            rc, payload = self._run(
                env_path=env_path,
                args=[
                    "supplier-invoice-payments",
                    "bookkeep",
                    "--number",
                    "42",
                    "--json-file",
                    str(payload_path),
                ],
            )

            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("must match --number", payload["error"])

    def test_supplier_invoice_payments_bookkeep_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "bookkeep.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "bookkeep",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "SupplierInvoicePayment": {
                                "Number": "42",
                                "InvoiceNumber": 1001,
                                "Amount": 2000.0,
                                "PaymentDate": "2026-06-09",
                                "ModeOfPayment": "BG",
                                "Booked": True,
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "bookkeep",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("refused", False))
            self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoice_payments_bookkeep_apply_performs_put_and_verifies_booked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "bookkeep.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "bookkeep",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/supplierinvoicepayments/42/bookkeep",
                        body={"SupplierInvoicePayment": {"Number": "42", "Booked": True}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoicepayments/42",
                        body={"SupplierInvoicePayment": {"Number": "42", "Booked": True}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "bookkeep",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "PUT")
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoicepayments/42/bookkeep")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoicepayments/42")

    def test_supplier_invoice_payments_bookkeep_apply_fails_when_verify_is_not_booked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "bookkeep.json"
            self._make_payload_file(payload_path, number="42")

            with patch("fortnox_api_tool.commands.supplier_invoice_payments.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "bookkeep",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/supplierinvoicepayments/42/bookkeep",
                        body={"SupplierInvoicePayment": {"Number": "42", "Booked": False}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoicepayments/42",
                        body={"SupplierInvoicePayment": {"Number": "42", "Booked": False}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-payments",
                        "bookkeep",
                        "--number",
                        "42",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 1)
            self.assertFalse(payload_apply.get("ok", True))
            self.assertFalse(payload_apply["receipt"]["verification_booked_true"])
