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
from wix_safe_agent_cli.commands import order_billing
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestOrderBillingCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli order-billing",
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
    def _refundability_payload(*, max_refund: str = "15.00") -> dict:
        return {
            "payments": [{"paymentId": "pay-1", "refundable": {"amount": max_refund}}],
            "paymentsSummary": {"maxRefund": max_refund},
            "lineItems": [],
            "shipping": {},
            "additionalFees": [],
        }

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_order_billing_subcommands(self) -> None:
        parser = build_parser()
        refundability_args = parser.parse_args(["order-billing", "get-order-refundability", "--order-id", "order-1"])
        self.assertEqual(refundability_args.order_billing_cmd, "get-order-refundability")
        self.assertFalse(refundability_args.write_capable)

        calculate_args = parser.parse_args(
            ["order-billing", "calculate-refund", "--order-id", "order-1", "--refund-items-json", '{"lineItems":[{"lineItemId":"li-1","quantity":1}]}']
        )
        self.assertEqual(calculate_args.order_billing_cmd, "calculate-refund")
        self.assertFalse(calculate_args.write_capable)

        refund_args = parser.parse_args(
            ["order-billing", "refund-payments", "--order-id", "order-1", "--payment-refunds-json", '[{"paymentId":"pay-1","amount":"5.00"}]']
        )
        self.assertEqual(refund_args.order_billing_cmd, "refund-payments")
        self.assertTrue(refund_args.write_capable)

        authorize_args = parser.parse_args(
            [
                "order-billing",
                "authorize-charge-with-saved-payment-method",
                "--order-id",
                "order-1",
                "--amount-json",
                '{"amount":"1"}',
                "--currency",
                "USD",
            ]
        )
        self.assertEqual(authorize_args.order_billing_cmd, "authorize-charge-with-saved-payment-method")
        self.assertTrue(authorize_args.write_capable)

        capture_args = parser.parse_args(
            [
                "order-billing",
                "capture-authorized-payments",
                "--order-id",
                "order-1",
                "--payments-json",
                '[{"paymentId":"pay-1","amount":{"amount":"1"}}]',
            ]
        )
        self.assertEqual(capture_args.order_billing_cmd, "capture-authorized-payments")
        self.assertTrue(capture_args.write_capable)

        void_args = parser.parse_args(
            [
                "order-billing",
                "void-authorized-payments",
                "--order-id",
                "order-1",
                "--payment-ids-json",
                '["pay-1"]',
            ]
        )
        self.assertEqual(void_args.order_billing_cmd, "void-authorized-payments")
        self.assertTrue(void_args.write_capable)

        receipts_args = parser.parse_args(
            [
                "order-billing",
                "generate-receipts",
                "--order-id",
                "order-1",
                "--payment-ids-json",
                '["pay-1"]',
            ]
        )
        self.assertEqual(receipts_args.order_billing_cmd, "generate-receipts")
        self.assertTrue(receipts_args.write_capable)

        redeem_args = parser.parse_args(
            [
                "order-billing",
                "redeem-gift-card",
                "--order-id",
                "order-1",
                "--gift-card-code",
                "GC123",
                "--amount-json",
                '{"amount":"20"}',
                "--currency",
                "USD",
            ]
        )
        self.assertEqual(redeem_args.order_billing_cmd, "redeem-gift-card")
        self.assertTrue(redeem_args.write_capable)

    @patch("wix_safe_agent_cli.commands.order_billing.HttpClient")
    def test_get_order_refundability_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(self._refundability_payload())
        args = SimpleNamespace(order_id="order-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_get_order_refundability(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/ecom/v1/order-billing/get-order-refundability")
        self.assertEqual(payload["request"]["body"], {"orderId": "order-1"})

    def test_calculate_refund_requires_refund_items_json(self) -> None:
        args = SimpleNamespace(order_id="order-1", refund_items_json=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_calculate_refund(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("Missing --refund-items-json", payload["error"])

    @patch("wix_safe_agent_cli.commands.order_billing.HttpClient")
    def test_calculate_refund_builds_expected_body(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"summary": {"amount": "5.00"}})
        args = SimpleNamespace(
            order_id="order-1",
            refund_items_json='{"lineItems":[{"lineItemId":"li-1","quantity":1}]}',
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_calculate_refund(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/ecom/v1/order-billing/calculate-refund")
        self.assertEqual(
            payload["request"]["body"],
            {"orderId": "order-1", "refundItems": {"lineItems": [{"lineItemId": "li-1", "quantity": 1}]}},
        )

    @patch.object(order_billing, "_get_order_refundability")
    def test_refund_payments_dry_run_builds_plan(self, mock_get_refundability) -> None:
        mock_get_refundability.return_value = self._refundability_payload()
        args = SimpleNamespace(
            order_id="order-1",
            payment_refunds_json='[{"paymentId":"pay-1","amount":"5.00"}]',
            refund_items_json='{"lineItems":[{"lineItemId":"li-1","quantity":1}]}',
            side_effects_json='{"restock":true}',
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_refund_payments(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "order-billing.refund-payments")

    @patch("wix_safe_agent_cli.commands.order_billing.HttpClient")
    def test_refund_payments_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(
            order_id="order-1",
            payment_refunds_json='[{"paymentId":"pay-1","amount":"5.00"}]',
            refund_items_json=None,
            side_effects_json=None,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_refund_payments(
                args,
                self._ctx(apply=True, yes=True, ack_irreversible=True),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        mock_client.assert_not_called()

    @patch.object(order_billing, "_get_order_refundability")
    def test_refund_payments_dry_run_marks_ack_requirement(self, mock_get_refundability) -> None:
        mock_get_refundability.return_value = self._refundability_payload()
        args = SimpleNamespace(
            order_id="order-1",
            payment_refunds_json='[{"paymentId":"pay-1","amount":"5.00"}]',
            refund_items_json=None,
            side_effects_json=None,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_refund_payments(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.order_billing.HttpClient")
    def test_refund_payments_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(self._refundability_payload(max_refund="15.00")),
            _DummyResponse(self._refundability_payload(max_refund="15.00")),
            _DummyResponse({"refund": {"id": "refund-1"}, "orderTransactions": [{"id": "txn-1"}]}),
            _DummyResponse(self._refundability_payload(max_refund="10.00")),
        ]
        args = SimpleNamespace(
            order_id="order-1",
            payment_refunds_json='[{"paymentId":"pay-1","amount":"5.00"}]',
            refund_items_json=None,
            side_effects_json='{"restock":true}',
        )
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            order_billing.cmd_order_billing_refund_payments(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = order_billing.cmd_order_billing_refund_payments(
                    args,
                    self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path),
                )
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["verification"]["after"]["paymentsSummary"]["maxRefund"], "10.00")
        finally:
            Path(plan_path).unlink()

    @patch.object(order_billing, "_get_order_refundability")
    def test_authorize_charge_dry_run_builds_expected_body(self, mock_get_refundability) -> None:
        mock_get_refundability.return_value = self._refundability_payload()
        args = SimpleNamespace(
            order_id="order-1",
            amount_json='{"amount":"1"}',
            currency="USD",
            delayed_capture_settings_json='{"scheduledAction":"VOID","delayDuration":{"count":1,"unit":"DAYS"}}',
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_authorize_charge_with_saved_payment_method(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(
            payload["plan"]["request"]["body"],
            {
                "orderId": "order-1",
                "amount": {"amount": "1"},
                "currency": "USD",
                "delayedCaptureSettings": {
                    "scheduledAction": "VOID",
                    "delayDuration": {"count": 1, "unit": "DAYS"},
                },
            },
        )

    @patch.object(order_billing, "_get_order_refundability")
    def test_capture_authorized_payments_dry_run_builds_expected_body(self, mock_get_refundability) -> None:
        mock_get_refundability.return_value = self._refundability_payload()
        args = SimpleNamespace(
            order_id="order-1",
            payments_json='[{"paymentId":"pay-1","amount":{"amount":"1"}}]',
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_capture_authorized_payments(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(
            payload["plan"]["request"]["body"],
            {
                "orderId": "order-1",
                "payments": [{"paymentId": "pay-1", "amount": {"amount": "1"}}],
            },
        )
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch.object(order_billing, "_get_order_refundability")
    def test_void_authorized_payments_dry_run_builds_expected_body(self, mock_get_refundability) -> None:
        mock_get_refundability.return_value = self._refundability_payload()
        args = SimpleNamespace(order_id="order-1", payment_ids_json='["pay-1","pay-2"]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_void_authorized_payments(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(
            payload["plan"]["request"]["body"],
            {"orderId": "order-1", "paymentIds": ["pay-1", "pay-2"]},
        )
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch.object(order_billing, "_get_order_refundability")
    def test_generate_receipts_dry_run_builds_expected_body(self, mock_get_refundability) -> None:
        mock_get_refundability.return_value = self._refundability_payload()
        args = SimpleNamespace(order_id="order-1", payment_ids_json='["pay-1"]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_generate_receipts(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["plan"]["request"]["body"], {"orderId": "order-1", "paymentIds": ["pay-1"]})
        self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch.object(order_billing, "_get_order_refundability")
    def test_redeem_gift_card_dry_run_builds_expected_body(self, mock_get_refundability) -> None:
        mock_get_refundability.return_value = self._refundability_payload()
        args = SimpleNamespace(
            order_id="order-1",
            gift_card_code="GC123",
            amount_json='{"amount":"20"}',
            currency="USD",
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = order_billing.cmd_order_billing_redeem_gift_card(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(
            payload["plan"]["request"]["body"],
            {
                "orderId": "order-1",
                "giftCardCode": "GC123",
                "amount": {"amount": "20"},
                "currency": "USD",
            },
        )
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.order_billing.HttpClient")
    def test_new_order_billing_writes_refuse_live_apply_without_plan_in(self, mock_client) -> None:
        cases = [
            (
                order_billing.cmd_order_billing_authorize_charge_with_saved_payment_method,
                SimpleNamespace(
                    order_id="order-1",
                    amount_json='{"amount":"1"}',
                    currency="USD",
                    delayed_capture_settings_json=None,
                ),
                False,
            ),
            (
                order_billing.cmd_order_billing_capture_authorized_payments,
                SimpleNamespace(
                    order_id="order-1",
                    payments_json='[{"paymentId":"pay-1","amount":{"amount":"1"}}]',
                ),
                True,
            ),
            (
                order_billing.cmd_order_billing_void_authorized_payments,
                SimpleNamespace(order_id="order-1", payment_ids_json='["pay-1"]'),
                True,
            ),
            (
                order_billing.cmd_order_billing_generate_receipts,
                SimpleNamespace(order_id="order-1", payment_ids_json='["pay-1"]'),
                False,
            ),
            (
                order_billing.cmd_order_billing_redeem_gift_card,
                SimpleNamespace(
                    order_id="order-1",
                    gift_card_code="GC123",
                    amount_json='{"amount":"20"}',
                    currency="USD",
                ),
                True,
            ),
        ]
        for func, args, requires_ack in cases:
            with self.subTest(method=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(
                        args,
                        self._ctx(apply=True, yes=True, ack_irreversible=requires_ack),
                    )
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["refused"])
        mock_client.assert_not_called()
