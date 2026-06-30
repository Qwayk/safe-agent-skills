from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import referral_rewards
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestReferralRewardsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
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
            "command_str": "wix-safe-agent-cli referral-rewards",
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

    def test_parser_recognizes_referral_rewards_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["referral-rewards", "get", "--referral-reward-id", "reward-123"],
            ["referral-rewards", "query", "--query-json", '{"query":{"filter":{"rewardType":{"$eq":"COUPON"}}}}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))
                self.assertFalse(args.write_capable)

    @patch("wix_safe_agent_cli.commands.referral_rewards.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referral_rewards.HttpClient")
    def test_get_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referralReward": {"id": "reward-123"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referral_rewards.cmd_referral_rewards_get(SimpleNamespace(referral_reward_id="reward-123"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/_api/referral-rewards/v1/referral-rewards/reward-123")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "referral-rewards")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.referral_rewards.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referral_rewards.HttpClient")
    def test_query_uses_official_path_and_body(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referralRewards": []})

        query_json = '{"query":{"filter":{"rewardType":{"$eq":"COUPON"}},"sort":[{"fieldName":"createdDate","order":"DESC"}]}}'
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referral_rewards.cmd_referral_rewards_query(SimpleNamespace(query_json=query_json), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/referral-rewards/v1/referral-rewards/query")
        self.assertEqual(payload["request"]["body"]["query"]["filter"]["rewardType"]["$eq"], "COUPON")
        request_kwargs = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(request_kwargs["json_body"]["query"]["sort"][0]["fieldName"], "createdDate")

    @patch("wix_safe_agent_cli.commands.referral_rewards.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referral_rewards.HttpClient")
    def test_query_requires_query_object_before_http(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referral_rewards.cmd_referral_rewards_query(SimpleNamespace(query_json='{"filter":{}}'), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("query", payload["error"])
        mock_client.return_value.request.assert_not_called()
