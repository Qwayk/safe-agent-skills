from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import orders
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestOrdersCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli orders",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    @staticmethod
    def _current_order(*, status: str = "APPROVED", email: str = "buyer@example.com") -> dict:
        return {"id": "order-1", "status": status, "buyerInfo": {"email": email}, "updatedDate": "2026-06-24T00:00:00Z"}

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_orders_subcommands(self) -> None:
        parser = build_parser()
        search_args = parser.parse_args(["orders", "search"])
        self.assertEqual(search_args.orders_cmd, "search")
        self.assertFalse(search_args.write_capable)

        get_args = parser.parse_args(["orders", "get", "--order-id", "order-1"])
        self.assertEqual(get_args.orders_cmd, "get")
        self.assertFalse(get_args.write_capable)

        create_args = parser.parse_args(["orders", "create", "--order-json", '{"lineItems":[{"quantity":1}]}'])
        self.assertEqual(create_args.orders_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(["orders", "update", "--order-id", "order-1", "--order-json", '{"archived":true}'])
        self.assertEqual(update_args.orders_cmd, "update")
        self.assertTrue(update_args.write_capable)

        cancel_args = parser.parse_args(["orders", "cancel", "--order-id", "order-1"])
        self.assertEqual(cancel_args.orders_cmd, "cancel")
        self.assertTrue(cancel_args.write_capable)

        bulk_args = parser.parse_args(["orders", "bulk-update", "--orders-json", '[{"id":"order-1","archived":true}]'])
        self.assertEqual(bulk_args.orders_cmd, "bulk-update")
        self.assertTrue(bulk_args.write_capable)

    @patch("wix_safe_agent_cli.commands.orders.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"order": self._current_order()})
        args = SimpleNamespace(order_id="order-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = orders.cmd_orders_get(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/ecom/v1/orders/order-1")

    @patch("wix_safe_agent_cli.commands.orders.HttpClient")
    def test_search_wraps_search_body(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"orders": [], "metadata": {"count": 0}})
        args = SimpleNamespace(search_json='{"filter":{"paymentStatus":"PAID"}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = orders.cmd_orders_search(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/ecom/v1/orders/search")
        self.assertEqual(payload["request"]["body"], {"search": {"filter": {"paymentStatus": "PAID"}}})

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(
            order_json='{"lineItems":[{"quantity":1,"productName":{"original":"Sample"},"itemType":{"preset":"PHYSICAL"},"price":{"amount":"10.00"}}]}'
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = orders.cmd_orders_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "orders.create")
        self.assertFalse(payload["plan"]["state_capture"]["before_state_available"])

    @patch("wix_safe_agent_cli.commands.orders.HttpClient")
    def test_create_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(
            order_json='{"lineItems":[{"quantity":1,"productName":{"original":"Sample"},"itemType":{"preset":"PHYSICAL"},"price":{"amount":"10.00"}}]}'
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = orders.cmd_orders_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        mock_client.assert_not_called()

    @patch("wix_safe_agent_cli.commands.orders.HttpClient")
    def test_update_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(order_id="order-1", order_json='{"archived":true}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = orders.cmd_orders_update(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "orders.update")
        mock_client.assert_not_called()

    @patch("wix_safe_agent_cli.commands.orders.HttpClient")
    def test_update_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"order": self._current_order()}),
            _DummyResponse({"order": self._current_order()}),
            _DummyResponse({"order": self._current_order()}),
            _DummyResponse({"order": self._current_order(email="new@example.com")}),
            _DummyResponse({"order": self._current_order(email="new@example.com")}),
        ]
        args = SimpleNamespace(order_id="order-1", order_json='{"buyerInfo":{"email":"new@example.com"}}')
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            orders.cmd_orders_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = orders.cmd_orders_update(args, self._ctx(apply=True, yes=True, plan_in=plan_path))
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["buyerInfo"]["email"], "new@example.com")
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.orders.HttpClient")
    def test_cancel_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(order_id="order-1", cancel_json=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = orders.cmd_orders_cancel(args, self._ctx(apply=True, yes=True, ack_irreversible=True))
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "orders.cancel")
        mock_client.assert_not_called()

    def test_cancel_dry_run_marks_ack_requirement(self) -> None:
        args = SimpleNamespace(order_id="order-1", cancel_json=None)
        with patch.object(orders, "_get_order", return_value=self._current_order()):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = orders.cmd_orders_cancel(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.orders.HttpClient")
    def test_bulk_update_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(orders_json='[{"id":"order-1","archived":true}]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = orders.cmd_orders_bulk_update(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "orders.bulk-update")
        mock_client.assert_not_called()

    def test_bulk_update_rejects_more_than_100_orders(self) -> None:
        entries = [{"id": f"order-{i}", "archived": True} for i in range(101)]
        args = SimpleNamespace(orders_json=json.dumps(entries))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = orders.cmd_orders_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("more than 100", payload["error"])
