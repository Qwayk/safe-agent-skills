from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import loyalty_checkout_discounts
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestLoyaltyCheckoutDiscountsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli loyalty-checkout-discounts",
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

    def test_parser_exposes_loyalty_checkout_discount_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["loyalty-checkout-discounts", "query"], "query", False),
            (
                [
                    "loyalty-checkout-discounts",
                    "apply",
                    "--discount-json",
                    '{"checkoutId":"checkout-1","rewardId":"reward-1"}',
                ],
                "apply",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.loyalty_checkout_discounts_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_query_uses_official_path_and_defaults(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"discounts": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = loyalty_checkout_discounts.cmd_loyalty_checkout_discounts_query(
                SimpleNamespace(query_json="{}"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(
            payload["request"]["path"],
            "/loyalty-checkout-exchange/v1/loyalty-checkout-discounts/query",
        )
        self.assertEqual(payload["request"]["body"]["query"]["paging"]["limit"], 50)
        self.assertEqual(
            payload["request"]["body"]["query"]["sort"],
            [{"fieldName": "createdDate", "order": "DESC"}],
        )

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_apply_is_plan_first_and_ack_gated(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = loyalty_checkout_discounts.cmd_loyalty_checkout_discounts_apply(
                SimpleNamespace(discount_json='{"checkoutId":"checkout-1","rewardId":"reward-1"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/loyalty-checkout-exchange/v1/loyalty-checkout-discount")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_apply_rejects_missing_or_ambiguous_discount_selector(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            "{}",
            '{"checkoutId":"checkout-1"}',
            '{"checkoutId":"checkout-1","rewardId":"reward-1","loyaltyCouponId":"coupon-1"}',
        ]
        for raw in cases:
            with self.subTest(raw=raw):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = loyalty_checkout_discounts.cmd_loyalty_checkout_discounts_apply(
                        SimpleNamespace(discount_json=raw),
                        self._ctx(),
                    )
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
