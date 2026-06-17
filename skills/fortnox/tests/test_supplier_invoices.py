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


class TestSupplierInvoices(unittest.TestCase):
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

    def _make_payload_file(self, path: Path, *, given_number: str, booked: bool = False) -> None:
        payload = {
            "SupplierInvoice": {
                "GivenNumber": given_number,
                "Currency": "USD",
                "InvoiceDate": "2026-06-09",
                "DueDate": "2026-06-09",
                "SupplierName": "Acme",
                "Booked": booked,
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_supplier_invoices_list_calls_expected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.supplier_invoices.get_json") as get_json:
                get_json.return_value = _api_response(
                    status=200,
                    path="/supplierinvoices",
                    body={"SupplierInvoices": []},
                )
                rc, payload = self._run(env_path=env_path, args=["supplier-invoices", "list"])

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/supplierinvoices")
            self.assertEqual(payload["http_status"], 200)
            self.assertEqual(payload["data"], {"SupplierInvoices": []})
            get_json.assert_called_once_with(ctx=unittest.mock.ANY, path="/supplierinvoices")

    def test_supplier_invoices_get_calls_expected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.supplier_invoices.get_json") as get_json:
                get_json.return_value = _api_response(
                    status=200,
                    path="/supplierinvoices/2001",
                    body={"SupplierInvoice": {"GivenNumber": "2001"}},
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoices", "get", "--supplier-invoice-number", "2001"],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/supplierinvoices/2001")
            self.assertEqual(payload["http_status"], 200)
            self.assertEqual(payload["data"], {"SupplierInvoice": {"GivenNumber": "2001"}})
            get_json.assert_called_once_with(ctx=unittest.mock.ANY, path="/supplierinvoices/2001")

    def test_supplier_invoices_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, given_number="2001")

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoices", "create", "--json-file", str(payload_path)],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), _sha256(payload_path))
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoices_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, given_number="2001")

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoices", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "SupplierInvoice": {
                                "GivenNumber": "2001",
                                "Currency": "SEK",
                                "InvoiceDate": "2026-06-09",
                                "DueDate": "2026-06-09",
                                "SupplierName": "Acme",
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
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
            self.assertIn("reasons", payload_apply)
            self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoices_create_apply_performs_post_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, given_number="2001")

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoices", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/supplierinvoices",
                        body={"SupplierInvoice": {"GivenNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001",
                        body={"SupplierInvoice": {"GivenNumber": "2001"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
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
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoices")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoices/2001")

    def test_supplier_invoices_update_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, given_number="2001")

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "update",
                        "--supplier-invoice-number",
                        "2001",
                        "--json-file",
                        str(payload_path),
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("selector", {}).get("given_number"), "2001")
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoices_update_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "SupplierInvoice": {
                            "GivenNumber": "2001",
                            "Currency": "USD",
                            "InvoiceDate": "2026-06-09",
                        }
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "update",
                        "--supplier-invoice-number",
                        "2001",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "SupplierInvoice": {
                                "GivenNumber": "2001",
                                "Currency": "SEK",
                                "InvoiceDate": "2026-06-09",
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "update",
                        "--supplier-invoice-number",
                        "2001",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("refused", False))
            self.assertIn("reasons", payload_apply)
            self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoices_update_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, given_number="2001")

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "update",
                        "--supplier-invoice-number",
                        "2001",
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
                        path="/supplierinvoices/2001",
                        body={"SupplierInvoice": {"GivenNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001",
                        body={"SupplierInvoice": {"GivenNumber": "2001"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "update",
                        "--supplier-invoice-number",
                        "2001",
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
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoices/2001")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoices/2001")

    def test_supplier_invoices_update_rejects_number_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, given_number="2002")

            rc, payload = self._run(
                env_path=env_path,
                args=[
                    "supplier-invoices",
                    "update",
                    "--supplier-invoice-number",
                    "2001",
                    "--json-file",
                    str(payload_path),
                ],
            )

            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("must match --supplier-invoice-number", payload["error"])

    def test_supplier_invoices_approvalbookkeep_dry_run_without_payload(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "approvalbookkeep",
                        "--supplier-invoice-number",
                        "2001",
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("selector", {}).get("action"), "approvalbookkeep")
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoices_approvalbookkeep_apply_with_optional_payload_verifies_booked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "approvalbookkeep.json"
            self._make_payload_file(payload_path, given_number="2001")

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "approvalbookkeep",
                        "--supplier-invoice-number",
                        "2001",
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
                        path="/supplierinvoices/2001/approvalbookkeep",
                        body={"SupplierInvoice": {"GivenNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001",
                        body={"SupplierInvoice": {"GivenNumber": "2001", "Booked": True}},
                    ),
                ]

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "approvalbookkeep",
                        "--supplier-invoice-number",
                        "2001",
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
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoices/2001/approvalbookkeep")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoices/2001")
            self.assertTrue(payload_apply.get("receipt", {}).get("verification_booked_true"))

    def test_supplier_invoices_bookkeep_apply_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "bookkeep",
                        "--supplier-invoice-number",
                        "2001",
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "bookkeep",
                        "--supplier-invoice-number",
                        "2001",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("refused", False))
            self.assertTrue("yes" in " ".join(payload_apply.get("reasons", [])).lower())
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoices_bookkeep_apply_refuses_when_planned_payload_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "bookkeep.json"
            self._make_payload_file(payload_path, given_number="2001")

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "bookkeep",
                        "--supplier-invoice-number",
                        "2001",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "bookkeep",
                        "--supplier-invoice-number",
                        "2001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("refused", False))
            self.assertIn("json payload file", " ".join(payload_apply.get("reasons", [])).lower())
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoices_bookkeep_apply_put_and_verifies_booked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "bookkeep",
                        "--supplier-invoice-number",
                        "2001",
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001/bookkeep",
                        body={"SupplierInvoice": {"GivenNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001",
                        body={"SupplierInvoice": {"GivenNumber": "2001", "Booked": True}},
                    ),
                ]

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "bookkeep",
                        "--supplier-invoice-number",
                        "2001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "PUT")
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoices/2001/bookkeep")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoices/2001")
            self.assertTrue(payload_apply.get("receipt", {}).get("verification_booked_true"))

    def test_supplier_invoices_bookkeep_apply_verification_fails_when_not_booked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "bookkeep",
                        "--supplier-invoice-number",
                        "2001",
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001/bookkeep",
                        body={"SupplierInvoice": {"GivenNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001",
                        body={"SupplierInvoice": {"GivenNumber": "2001", "Booked": False}},
                    ),
                ]

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "bookkeep",
                        "--supplier-invoice-number",
                        "2001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 1)
            self.assertFalse(payload_apply.get("ok", True))
            self.assertFalse(payload_apply.get("receipt", {}).get("verification_booked_true"))

    def test_supplier_invoices_approvalpayment_apply_verifies_payment_pending_false(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "approvalpayment",
                        "--supplier-invoice-number",
                        "2001",
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001/approvalpayment",
                        body={"SupplierInvoice": {"GivenNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001",
                        body={"SupplierInvoice": {"GivenNumber": "2001", "PaymentPending": False}},
                    ),
                ]

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "approvalpayment",
                        "--supplier-invoice-number",
                        "2001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoices/2001/approvalpayment")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoices/2001")
            self.assertTrue(payload_apply.get("receipt", {}).get("verification_payment_pending_false"))

    def test_supplier_invoices_cancel_apply_verifies_cancelled(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoices", "cancel", "--supplier-invoice-number", "2001"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001/cancel",
                        body={"SupplierInvoice": {"GivenNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001",
                        body={"SupplierInvoice": {"GivenNumber": "2001", "Cancelled": True}},
                    ),
                ]

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "cancel",
                        "--supplier-invoice-number",
                        "2001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoices/2001/cancel")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoices/2001")
            self.assertTrue(payload_apply.get("receipt", {}).get("verification_cancelled_true"))

    def test_supplier_invoices_credit_apply_verifies_credit_reference(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoices", "credit", "--supplier-invoice-number", "2001"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001/credit",
                        body={"SupplierInvoice": {"GivenNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoices/2001",
                        body={
                            "SupplierInvoice": {
                                "GivenNumber": "2001",
                                "Credit": True,
                                "CreditReference": 3001,
                            }
                        },
                    ),
                ]

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoices",
                        "credit",
                        "--supplier-invoice-number",
                        "2001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoices/2001/credit")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoices/2001")
            self.assertTrue(payload_apply.get("receipt", {}).get("verification_credit_reference_present"))
