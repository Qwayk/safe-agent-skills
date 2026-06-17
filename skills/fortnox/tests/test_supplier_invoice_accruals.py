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


class TestSupplierInvoiceAccruals(unittest.TestCase):
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

    def _make_payload_file(self, path: Path, *, supplier_invoice_number: str) -> None:
        payload = {
            "SupplierInvoiceAccrual": {
                "SupplierInvoiceNumber": supplier_invoice_number,
                "Description": "seed",
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_supplier_invoice_accruals_list(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch(
                "fortnox_api_tool.commands.supplier_invoice_accruals.get_json",
                return_value=_api_response(
                    status=200,
                    path="/supplierinvoiceaccruals",
                    body={"SupplierInvoiceAccruals": []},
                ),
            ):
                rc, payload = self._run(env_path=env_path, args=["supplier-invoice-accruals", "list"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/supplierinvoiceaccruals")
            self.assertEqual(payload["data"], {"SupplierInvoiceAccruals": []})

    def test_supplier_invoice_accruals_get_requires_supplier_invoice_number(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            rc, payload = self._run(env_path=env_path, args=["supplier-invoice-accruals", "get"])
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_supplier_invoice_accruals_get(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch(
                "fortnox_api_tool.commands.supplier_invoice_accruals.get_json",
                return_value=_api_response(
                    status=200,
                    path="/supplierinvoiceaccruals/2001",
                    body={"SupplierInvoiceAccrual": {"SupplierInvoiceNumber": "2001"}},
                ),
            ):
                rc, payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-accruals", "get", "--supplier-invoice-number", "2001"],
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/supplierinvoiceaccruals/2001")
            self.assertEqual(payload["data"], {"SupplierInvoiceAccrual": {"SupplierInvoiceNumber": "2001"}})

    def test_supplier_invoice_accruals_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, supplier_invoice_number="2001")

            with patch("fortnox_api_tool.commands.supplier_invoice_accruals.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-accruals", "create", "--json-file", str(payload_path)],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)
            self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), _sha256(payload_path))
            self.assertTrue(bool(payload["plan"]))
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoice_accruals_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, supplier_invoice_number="2001")

            with patch("fortnox_api_tool.commands.supplier_invoice_accruals.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-accruals", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "SupplierInvoiceAccrual": {
                                "SupplierInvoiceNumber": "2001",
                                "Description": "changed",
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-accruals",
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

    def test_supplier_invoice_accruals_create_apply_performs_post_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, supplier_invoice_number="2001")

            with patch("fortnox_api_tool.commands.supplier_invoice_accruals.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-accruals", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/supplierinvoiceaccruals",
                        body={"SupplierInvoiceAccrual": {"SupplierInvoiceNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoiceaccruals/2001",
                        body={"SupplierInvoiceAccrual": {"SupplierInvoiceNumber": "2001"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-accruals",
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
            self.assertFalse(payload_apply["dry_run"])
            self.assertEqual(request_json.call_count, 2)
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "POST")
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoiceaccruals")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoiceaccruals/2001")

    def test_supplier_invoice_accruals_update_dry_run_emits_plan(self) -> None:
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
                        "SupplierInvoiceAccrual": {
                            "SupplierInvoiceNumber": "2001",
                            "Description": "seed",
                        }
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoice_accruals.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-accruals",
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
            self.assertEqual(payload["plan"].get("selector", {}).get("supplier_invoice_number"), "2001")
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoice_accruals_update_apply_rechecks_json_payload_hash(self) -> None:
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
                        "SupplierInvoiceAccrual": {
                            "SupplierInvoiceNumber": "2001",
                            "Description": "seed",
                        }
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoice_accruals.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-accruals",
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
                            "SupplierInvoiceAccrual": {
                                "SupplierInvoiceNumber": "2001",
                                "Description": "changed",
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-accruals",
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

    def test_supplier_invoice_accruals_update_apply_performs_put_and_get_verify(self) -> None:
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
                        "SupplierInvoiceAccrual": {
                            "SupplierInvoiceNumber": "2001",
                            "Description": "updated",
                        }
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoice_accruals.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-accruals",
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
                        path="/supplierinvoiceaccruals/2001",
                        body={"SupplierInvoiceAccrual": {"SupplierInvoiceNumber": "2001", "Description": "updated"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoiceaccruals/2001",
                        body={"SupplierInvoiceAccrual": {"SupplierInvoiceNumber": "2001", "Description": "updated"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-accruals",
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
            self.assertEqual(request_json.call_count, 2)
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "PUT")
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoiceaccruals/2001")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoiceaccruals/2001")

    def test_supplier_invoice_accruals_remove_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoice_accruals.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-accruals", "remove", "--supplier-invoice-number", "2001"],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("selector", {}).get("path"), "/supplierinvoiceaccruals/2001")
            self.assertEqual(request_json.call_count, 0)

    def test_supplier_invoice_accruals_remove_apply_refuses_without_ack_and_confirms_with_delete_then_404(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.supplier_invoice_accruals.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-accruals", "remove", "--supplier-invoice-number", "2001"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_refused, payload_refused = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-accruals",
                        "remove",
                        "--supplier-invoice-number",
                        "2001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )
                self.assertEqual(rc_refused, 0)
                self.assertTrue(payload_refused.get("refused", False))
                self.assertIn("reasons", payload_refused)
                self.assertIn("ack-irreversible", " ".join(payload_refused["reasons"]).lower())

                request_json.side_effect = [
                    _api_response(
                        status=204,
                        path="/supplierinvoiceaccruals/2001",
                        body={},
                    ),
                    RuntimeError("HTTP 404 for GET https://api.fortnox.se/3/supplierinvoiceaccruals/2001"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-accruals",
                        "remove",
                        "--supplier-invoice-number",
                        "2001",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_count, 2)
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "DELETE")
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoiceaccruals/2001")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoiceaccruals/2001")
