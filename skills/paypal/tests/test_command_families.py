from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from paypal_safe_agent_cli.cli import build_parser
from paypal_safe_agent_cli.commands import paypal


class TestPayPalCommandFamilies(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = build_parser()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.body = Path(self._tmp.name) / "body.json"
        self.body.write_text("{}\n", encoding="utf-8")

    def _path_value(self, name: str) -> str:
        values = {
            "product_id": "prod-123",
            "dispute_id": "disp-123",
            "id": "id-123",
            "setup_token_id": "setup-token-123",
            "payment_token_id": "payment-token-123",
            "customer_id": "cust-123",
            "invoice_id": "inv-123",
            "template_id": "template-123",
            "merchant_id": "merchant-123",
            "order_id": "order-123",
            "tracking_id": "track-123",
            "batch_id": "batch-123",
            "authorization_id": "auth-123",
            "capture_id": "cap-123",
            "refund_id": "refund-123",
            "webhook_id": "wh-123",
            "event_id": "event-123",
            "lookup_id": "lookup-123",
            "item_id": "item-123",
            "payout_batch_id": "batch-123",
            "payout_id": "payout-id-123",
            "partner_referral_id": "partner-ref-123",
            "plan_id": "plan-123",
            "subscription_id": "sub-123",
            "payout_id": "payout-id-123",
        }
        return values.get(name, f"{name}-123")

    def _argv_for_spec(self, family: str, action: str, spec: paypal.ActionSpec) -> list[str]:
        argv: list[str] = [family, action]
        for name in paypal._path_names(spec.path):
            argv.extend([f"--{name.replace('_', '-')}", self._path_value(name)])
        if spec.requires_body_file:
            argv.extend(["--body-file", str(self.body)])
        return argv

    def test_every_shipped_action_parses_with_required_args(self) -> None:
        for family, actions in paypal.actions().items():
            for action, spec in actions.items():
                with self.subTest(family=family, action=action):
                    argv = self._argv_for_spec(family, action, spec)
                    args = self.parser.parse_args(argv)
                    self.assertEqual(args.paypal_family, family)
                    self.assertEqual(args.paypal_action, action)
                    self.assertIs(args.func, paypal.cmd_paypal_api)
                    self.assertEqual(args.write_capable, spec.write)
