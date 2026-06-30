from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import loyalty_rewards
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestLoyaltyRewardsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli loyalty-rewards",
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

    def test_parser_exposes_loyalty_rewards_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["loyalty-rewards", "list"], "list", False),
            (["loyalty-rewards", "get", "--reward-id", "reward-1"], "get", False),
            (["loyalty-rewards", "query"], "query", False),
            (
                ["loyalty-rewards", "create", "--reward-json", '{"reward":{"id":"reward-1","title":"10% Off"}}'],
                "create",
                True,
            ),
            (
                ["loyalty-rewards", "update", "--reward-json", '{"reward":{"id":"reward-1","title":"20% Off"}}'],
                "update",
                True,
            ),
            (["loyalty-rewards", "delete", "--reward-id", "reward-1"], "delete", True),
            (
                ["loyalty-rewards", "bulk-create", "--rewards-json", '{"rewards":[{"id":"reward-1"},{"id":"reward-2"}]}'],
                "bulk-create",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.loyalty_rewards_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"rewards": []})
        cases = [
            (
                loyalty_rewards.cmd_loyalty_rewards_list,
                SimpleNamespace(params_json='{"cursorPaging":{"limit":10}}'),
                "GET",
                "/loyalty-rewards/v1/rewards",
            ),
            (
                loyalty_rewards.cmd_loyalty_rewards_get,
                SimpleNamespace(reward_id="reward-1"),
                "GET",
                "/loyalty-rewards/v1/rewards/reward-1",
            ),
            (
                loyalty_rewards.cmd_loyalty_rewards_query,
                SimpleNamespace(query_json='{}'),
                "POST",
                "/loyalty-rewards/v1/rewards/query",
            ),
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
                if func is loyalty_rewards.cmd_loyalty_rewards_query:
                    self.assertEqual(payload["request"]["body"]["cursorPaging"]["limit"], 50)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_and_ack_gated(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                loyalty_rewards.cmd_loyalty_rewards_create,
                SimpleNamespace(reward_json='{"reward":{"id":"reward-1","title":"10% Off"}}'),
                "POST",
                "/loyalty-rewards/v1/rewards",
            ),
            (
                loyalty_rewards.cmd_loyalty_rewards_update,
                SimpleNamespace(reward_json='{"reward":{"id":"reward-1","title":"20% Off"}}'),
                "PUT",
                "/loyalty-rewards/v1/rewards/reward-1",
            ),
            (
                loyalty_rewards.cmd_loyalty_rewards_delete,
                SimpleNamespace(reward_id="reward-1"),
                "DELETE",
                "/loyalty-rewards/v1/rewards/reward-1",
            ),
            (
                loyalty_rewards.cmd_loyalty_rewards_bulk_create,
                SimpleNamespace(rewards_json='{"rewards":[{"id":"reward-1"},{"id":"reward-2"}]}'),
                "POST",
                "/loyalty-rewards/v1/bulk/rewards/create",
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
    def test_rejects_missing_required_body_fields(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (loyalty_rewards.cmd_loyalty_rewards_create, SimpleNamespace(reward_json="{}")),
            (loyalty_rewards.cmd_loyalty_rewards_update, SimpleNamespace(reward_json='{"reward":{}}')),
            (loyalty_rewards.cmd_loyalty_rewards_bulk_create, SimpleNamespace(rewards_json='{"rewards":[]}')),
            (loyalty_rewards.cmd_loyalty_rewards_update, SimpleNamespace(reward_json='{"reward":{"title":"missing-id"}}')),
        ]
        for func, args in cases:
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
