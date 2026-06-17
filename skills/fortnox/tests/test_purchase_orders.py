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


def _api_response(*, status: int, path: str, body: Any) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestPurchaseOrders(unittest.TestCase):
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

    def _write_env(self, td: str) -> Path:
        env_path = Path(td) / ".env"
        env_path.write_text(
            "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
            encoding="utf-8",
        )
        return env_path

    def _write_purchase_order_payload(
        self,
        path: Path,
        *,
        purchase_order_id: int | None = None,
        supplier_number: int = 1000,
        note: str = "dock order",
    ) -> None:
        payload: dict[str, Any] = {
            "supplierNumber": supplier_number,
            "currencyCode": "SEK",
            "currencyRate": 1,
            "deliveryAddress": "Main street 1",
            "deliveryCity": "Stockholm",
            "deliveryName": "Qwayk",
            "deliveryZipCode": "11122",
            "orderDate": "2026-06-15",
            "paymentTermsCode": 30,
            "note": note,
            "rows": [{"articleNumber": "ART-1", "orderedQuantity": 1, "unitPrice": 100}],
        }
        if purchase_order_id is not None:
            payload["id"] = purchase_order_id
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_purchase_orders_list_reads_the_collection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.purchase_orders.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/purchaseorders-v1",
                    body=[{"id": 7}],
                )
                rc, payload = self._run(env_path=env_path, args=["purchase-orders", "list"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/api/warehouse/purchaseorders-v1")
        self.assertEqual(request_data.call_args.kwargs["method"], "GET")

    def test_purchase_orders_get_note_reads_list_response(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.purchase_orders.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/purchaseorders-v1/7/notes",
                    body=[{"note": "urgent dock"}],
                )
                rc, payload = self._run(env_path=env_path, args=["purchase-orders", "get-note", "--id", "7"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/api/warehouse/purchaseorders-v1/7/notes")
        self.assertEqual(request_data.call_args.kwargs["path"], "/api/warehouse/purchaseorders-v1/7/notes")

    def test_purchase_orders_get_csv_emits_text_payload(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.purchase_orders._csv_request") as csv_request:
                csv_request.return_value = {
                    "status": 200,
                    "token_source": "env",
                    "token_expired": None,
                    "content_type": "text/csv",
                    "body": "id,supplierNumber\n7,1000\n",
                }
                rc, payload = self._run(env_path=env_path, args=["purchase-orders", "get-csv"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["content_type"], "text/csv")
        self.assertIn("id,supplierNumber", payload["data"])

    def test_purchase_orders_create_rejects_wrapped_payload(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "wrapped.json"
            payload_path.write_text(
                json.dumps({"PurchaseOrder": {"supplierNumber": 1000}}, indent=2),
                encoding="utf-8",
            )

            rc, payload = self._run(
                env_path=env_path,
                args=["purchase-orders", "create", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("raw top-level object", payload["error"])

    def test_purchase_orders_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "create.json"
            self._write_purchase_order_payload(payload_path, purchase_order_id=None)
            expected_hash = _sha256(payload_path)

            with patch("fortnox_api_tool.commands.purchase_orders.request_data") as request_data:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["purchase-orders", "create", "--json-file", str(payload_path)],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)
        self.assertEqual(request_data.call_count, 0)

    def test_purchase_orders_create_apply_uses_response_id_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "create.json"
            self._write_purchase_order_payload(payload_path, purchase_order_id=None)

            with patch("fortnox_api_tool.commands.purchase_orders.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["purchase-orders", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=201, path="/api/warehouse/purchaseorders-v1", body={"id": 7001}),
                    _api_response(
                        status=200,
                        path="/api/warehouse/purchaseorders-v1/7001",
                        body={"id": 7001, "purchaseOrderState": "DRAFT"},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "purchase-orders",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["method"], "POST")
        self.assertEqual(request_data.call_args_list[1].kwargs["path"], "/api/warehouse/purchaseorders-v1/7001")

    def test_purchase_orders_update_rejects_payload_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "update.json"
            self._write_purchase_order_payload(payload_path, purchase_order_id=8)

            rc, payload = self._run(
                env_path=env_path,
                args=["purchase-orders", "update", "--id", "7", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("must match --id", payload["error"])

    def test_purchase_orders_partial_update_apply_uses_patch_and_readback(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "partial.json"
            payload_path.write_text(
                json.dumps({"note": "updated dock note", "supplierName": "Qwayk Supply"}, indent=2),
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.purchase_orders.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "purchase-orders",
                        "partial-update-purchase-order",
                        "--id",
                        "7",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=200, path="/api/warehouse/purchaseorders-v1/7/partial", body={"id": 7}),
                    _api_response(
                        status=200,
                        path="/api/warehouse/purchaseorders-v1/7",
                        body={"id": 7, "note": "updated dock note"},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "purchase-orders",
                        "partial-update-purchase-order",
                        "--id",
                        "7",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["method"], "PATCH")
        self.assertEqual(request_data.call_args_list[0].kwargs["path"], "/api/warehouse/purchaseorders-v1/7/partial")

    def test_purchase_orders_manual_complete_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            rc, plan_payload = self._run(
                env_path=env_path,
                args=["purchase-orders", "manually-complete-purchase-order", "--id", "7"],
            )
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=[
                    "purchase-orders",
                    "manually-complete-purchase-order",
                    "--id",
                    "7",
                    "--apply",
                    "--plan-in",
                    str(plan_path),
                ],
            )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("--apply --yes", " ".join(payload_apply["reasons"]))

    def test_purchase_orders_manual_complete_apply_handles_204_and_verifies_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.purchase_orders.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["purchase-orders", "manually-complete-purchase-order", "--id", "7"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=204, path="/api/warehouse/purchaseorders-v1/7/complete", body=None),
                    _api_response(
                        status=200,
                        path="/api/warehouse/purchaseorders-v1/7",
                        body={"id": 7, "manuallyCompleted": True},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "purchase-orders",
                        "manually-complete-purchase-order",
                        "--id",
                        "7",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["expect_json"], False)

    def test_purchase_orders_send_many_apply_posts_id_array_and_verifies_sent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.purchase_orders.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "purchase-orders",
                        "sends-multiple-purchase-orders-via-email",
                        "--id",
                        "7",
                        "--id",
                        "8",
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=204, path="/api/warehouse/purchaseorders-v1/sendpurchaseorders", body=None),
                    _api_response(
                        status=200,
                        path="/api/warehouse/purchaseorders-v1/7",
                        body={"id": 7, "purchaseOrderState": "SENT"},
                    ),
                    _api_response(
                        status=200,
                        path="/api/warehouse/purchaseorders-v1/8",
                        body={"id": 8, "purchaseOrderState": "SENT"},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "purchase-orders",
                        "sends-multiple-purchase-orders-via-email",
                        "--id",
                        "7",
                        "--id",
                        "8",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["json_body"], ["7", "8"])

    def test_purchase_orders_update_response_bulk_apply_uses_query_ids_and_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "response.json"
            payload_path.write_text(json.dumps({"responseState": "REJECTED"}, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.purchase_orders.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "purchase-orders",
                        "update-response-bulk",
                        "--id",
                        "7",
                        "--id",
                        "8",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=200, path="/api/warehouse/purchaseorders-v1/response", body=[{"id": 7}, {"id": 8}]),
                    _api_response(
                        status=200,
                        path="/api/warehouse/purchaseorders-v1/7",
                        body={"id": 7, "responseState": "REJECTED"},
                    ),
                    _api_response(
                        status=200,
                        path="/api/warehouse/purchaseorders-v1/8",
                        body={"id": 8, "responseState": "REJECTED"},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "purchase-orders",
                        "update-response-bulk",
                        "--id",
                        "7",
                        "--id",
                        "8",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["query_params"], {"ids": "7,8"})

    def test_purchase_orders_void_requires_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            rc, plan_payload = self._run(env_path=env_path, args=["purchase-orders", "void", "--id", "7"])
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=[
                    "purchase-orders",
                    "void",
                    "--id",
                    "7",
                    "--apply",
                    "--yes",
                    "--plan-in",
                    str(plan_path),
                ],
            )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("ack-irreversible", " ".join(payload_apply["reasons"]).lower())

    def test_purchase_orders_void_apply_verifies_void_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.purchase_orders.request_data") as request_data:
                rc, plan_payload = self._run(env_path=env_path, args=["purchase-orders", "void", "--id", "7"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=204, path="/api/warehouse/purchaseorders-v1/7/void", body=None),
                    _api_response(
                        status=200,
                        path="/api/warehouse/purchaseorders-v1/7",
                        body={"id": 7, "purchaseOrderState": "VOIDED"},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "purchase-orders",
                        "void",
                        "--id",
                        "7",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["expect_json"], False)
