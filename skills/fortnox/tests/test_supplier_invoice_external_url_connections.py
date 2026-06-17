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
from fortnox_api_tool.errors import ValidationError


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _api_response(*, status: int, path: str, body: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestSupplierInvoiceExternalUrlConnections(unittest.TestCase):
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

    def _make_payload_file(self, path: Path) -> None:
        payload: dict[str, Any] = {
            "ExternalURLConnection": "ERP-42",
            "SupplierInvoiceNumber": 2001,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_get_reads_one_external_url_connection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch(
                "fortnox_api_tool.commands.supplier_invoice_external_url_connections.get_json",
                return_value=_api_response(
                    status=200,
                    path="/supplierinvoiceexternalurlconnections/101",
                    body={"SupplierInvoiceExternalURLConnection": {"Id": 101, "Url": "https://example.com"}},
                ),
            ):
                rc, payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-external-url-connections", "get", "--id", "101"],
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/supplierinvoiceexternalurlconnections/101")

    def test_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.supplier_invoice_external_url_connections.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-external-url-connections",
                        "create",
                        "--json-file",
                        str(payload_path),
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), _sha256(payload_path))
            self.assertEqual(request_json.call_count, 0)

    def test_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.supplier_invoice_external_url_connections.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-external-url-connections",
                        "create",
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
                            "ExternalURLConnection": "ERP-99",
                            "SupplierInvoiceNumber": 2001,
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-external-url-connections",
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
            self.assertIn("hash", " ".join(payload_apply.get("reasons", [])).lower())
            self.assertEqual(request_json.call_count, 0)

    def test_create_apply_performs_post_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.supplier_invoice_external_url_connections.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-external-url-connections",
                        "create",
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
                        status=201,
                        path="/supplierinvoiceexternalurlconnections",
                        body={"SupplierInvoiceExternalURLConnection": {"Id": 101}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoiceexternalurlconnections/101",
                        body={"SupplierInvoiceExternalURLConnection": {"Id": 101}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-external-url-connections",
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
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoiceexternalurlconnections")
            self.assertEqual(
                request_json.call_args_list[0].kwargs["json_body"],
                {"ExternalURLConnection": "ERP-42", "SupplierInvoiceNumber": 2001},
            )
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoiceexternalurlconnections/101")

    def test_update_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.supplier_invoice_external_url_connections.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-external-url-connections",
                        "update",
                        "--id",
                        "101",
                        "--json-file",
                        str(payload_path),
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("selector", {}).get("id"), "101")
            self.assertEqual(request_json.call_count, 0)

    def test_update_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.supplier_invoice_external_url_connections.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-external-url-connections",
                        "update",
                        "--id",
                        "101",
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
                        path="/supplierinvoiceexternalurlconnections/101",
                        body={"SupplierInvoiceExternalURLConnection": {"Id": 101, "Url": "https://example.com/updated"}},
                    ),
                    _api_response(
                        status=200,
                        path="/supplierinvoiceexternalurlconnections/101",
                        body={"SupplierInvoiceExternalURLConnection": {"Id": 101, "Url": "https://example.com/updated"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-external-url-connections",
                        "update",
                        "--id",
                        "101",
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
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoiceexternalurlconnections/101")
            self.assertEqual(
                request_json.call_args_list[0].kwargs["json_body"],
                {"ExternalURLConnection": "ERP-42", "SupplierInvoiceNumber": 2001},
            )
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/supplierinvoiceexternalurlconnections/101")

    def test_remove_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.supplier_invoice_external_url_connections.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-external-url-connections", "remove", "--id", "101"],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("selector", {}).get("id"), "101")
            self.assertEqual(request_json.call_count, 0)

    def test_remove_apply_refuses_without_ack_and_confirms_with_delete_then_404(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.supplier_invoice_external_url_connections.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["supplier-invoice-external-url-connections", "remove", "--id", "101"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_missing_ack, payload_missing_ack = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-external-url-connections",
                        "remove",
                        "--id",
                        "101",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                    ],
                )
                self.assertEqual(rc_missing_ack, 0)
                self.assertTrue(payload_missing_ack.get("refused", False))
                self.assertEqual(request_json.call_count, 0)

                request_json.side_effect = [
                    _api_response(status=204, path="/supplierinvoiceexternalurlconnections/101", body=None),
                    ValidationError("HTTP 404: not found"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "supplier-invoice-external-url-connections",
                        "remove",
                        "--id",
                        "101",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "--ack-irreversible",
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "DELETE")
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/supplierinvoiceexternalurlconnections/101")
