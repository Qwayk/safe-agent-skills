from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import loyalty_coupons
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestLoyaltyCouponsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli loyalty-coupons",
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

    def test_parser_exposes_loyalty_coupon_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["loyalty-coupons", "get", "--coupon-id", "coupon-1"], "get", False),
            (["loyalty-coupons", "query"], "query", False),
            (["loyalty-coupons", "get-current-member"], "get-current-member", False),
            (["loyalty-coupons", "redeem-current-member", "--redeem-json", '{"rewardId":"reward-1"}'], "redeem-current-member", True),
            (["loyalty-coupons", "redeem", "--redeem-json", '{"accountId":"account-1","rewardId":"reward-1"}'], "redeem", True),
            (["loyalty-coupons", "delete", "--coupon-id", "coupon-1"], "delete", True),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.loyalty_coupons_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"coupons": []})
        cases = [
            (loyalty_coupons.cmd_loyalty_coupons_get, SimpleNamespace(coupon_id="coupon-1"), "GET", "/loyalty-coupons/v1/coupons/coupon-1"),
            (loyalty_coupons.cmd_loyalty_coupons_query, SimpleNamespace(query_json="{}"), "POST", "/loyalty-coupons/v1/coupons/query"),
            (loyalty_coupons.cmd_loyalty_coupons_get_current_member, SimpleNamespace(), "GET", "/loyalty-coupons/v1/coupons/my-coupons"),
        ]
        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_and_ack_gated(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                loyalty_coupons.cmd_loyalty_coupons_redeem_current_member,
                SimpleNamespace(redeem_json='{"rewardId":"reward-1"}'),
                "POST",
                "/loyalty-coupons/v1/coupons/redeem-my-coupon",
            ),
            (
                loyalty_coupons.cmd_loyalty_coupons_redeem,
                SimpleNamespace(redeem_json='{"accountId":"account-1","rewardId":"reward-1"}'),
                "POST",
                "/loyalty-coupons/v1/coupons",
            ),
            (
                loyalty_coupons.cmd_loyalty_coupons_delete,
                SimpleNamespace(coupon_id="coupon-1"),
                "DELETE",
                "/loyalty-coupons/v1/coupons/coupon-1",
            ),
        ]
        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_redeem_rejects_empty_body(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = loyalty_coupons.cmd_loyalty_coupons_redeem(SimpleNamespace(redeem_json="{}"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
