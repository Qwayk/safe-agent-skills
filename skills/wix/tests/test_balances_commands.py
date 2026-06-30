from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import balances
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBalancesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli balances",
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
    def _instance_payload() -> dict:
        return {"site": {"installedWixApps": ["pricingPlans"]}}

    @staticmethod
    def _balance(*, available_credits: int = 7) -> dict:
        return {
            "id": "pool-1",
            "poolId": "pool-1",
            "availableCredits": available_credits,
            "beneficiary": {"memberId": "member-1"},
        }

    def _http_side_effect(self, responses: list[dict]) -> list[dict]:
        queue = list(responses)

        def _side_effect(*args, **kwargs):
            _ = (args, kwargs)
            return _DummyResponse(queue.pop(0))

        return _side_effect

    def _request_paths(self, mock_client) -> list[str]:
        paths: list[str] = []
        for call in mock_client.return_value.request.call_args_list:
            kwargs = call.kwargs
            url = str(kwargs.get("url", ""))
            paths.append(url.removeprefix("https://www.wixapis.com"))
        return paths

    def test_parser_recognizes_balances_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["balances", "get", "--pool-id", "pool-1"])
        self.assertEqual(get_args.balances_cmd, "get")
        self.assertFalse(get_args.write_capable)

        list_args = parser.parse_args(["balances", "list"])
        self.assertEqual(list_args.balances_cmd, "list")
        self.assertFalse(list_args.write_capable)

        query_args = parser.parse_args(["balances", "query"])
        self.assertEqual(query_args.balances_cmd, "query")
        self.assertFalse(query_args.write_capable)

        change_args = parser.parse_args(
            [
                "balances",
                "change",
                "--pool-id",
                "pool-1",
                "--change-json",
                '{"availableCredits":12}',
            ]
        )
        self.assertEqual(change_args.balances_cmd, "change")
        self.assertTrue(change_args.write_capable)

        revert_args = parser.parse_args(["balances", "revert-change", "--transaction-id", "txn-1"])
        self.assertEqual(revert_args.balances_cmd, "revert-change")
        self.assertTrue(revert_args.write_capable)

    @patch("wix_safe_agent_cli.commands.balances.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect(
            [self._instance_payload(), {"balance": self._balance()}]
        )
        args = SimpleNamespace(pool_id="pool-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = balances.cmd_balances_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/benefit-programs/v1/balances/pool-1")

    @patch("wix_safe_agent_cli.commands.balances.HttpClient")
    def test_list_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect(
            [self._instance_payload(), {"balances": [self._balance()]}]
        )
        args = SimpleNamespace()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = balances.cmd_balances_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/benefit-programs/v1/balances")

    @patch("wix_safe_agent_cli.commands.balances.HttpClient")
    def test_query_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect(
            [self._instance_payload(), {"balances": []}]
        )
        args = SimpleNamespace(query_json='{"paging":{"limit":25}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = balances.cmd_balances_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/benefit-programs/v1/balances/query")
        self.assertEqual(payload["request"]["body"], {"paging": {"limit": 25}})

    @patch("wix_safe_agent_cli.commands.balances.HttpClient")
    def test_change_dry_run_returns_plan(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect(
            [self._instance_payload(), {"balance": self._balance()}]
        )
        args = SimpleNamespace(pool_id="pool-1", change_json='{"availableCredits":12}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = balances.cmd_balances_change(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "balances.change")
        self.assertEqual(payload["plan"]["request"]["path"], "/benefit-programs/v1/balances/pool-1/change")
        self.assertEqual(payload["plan"]["request"]["body"], {"availableCredits": 12})

    @patch("wix_safe_agent_cli.commands.balances.HttpClient")
    def test_change_apply_without_reviewed_plan_refuses_before_write(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect(
            [self._instance_payload(), {"balance": self._balance()}]
        )
        args = SimpleNamespace(pool_id="pool-1", change_json='{"availableCredits":12}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = balances.cmd_balances_change(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertNotIn("/benefit-programs/v1/balances/pool-1/change", self._request_paths(mock_client))

    @patch("wix_safe_agent_cli.commands.balances.HttpClient")
    def test_revert_change_dry_run_returns_plan(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect([self._instance_payload()])
        args = SimpleNamespace(transaction_id="txn-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = balances.cmd_balances_revert_change(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "balances.revert-change")
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/benefit-programs/v1/balances/changes/txn-1/revert",
        )

    @patch("wix_safe_agent_cli.commands.balances.HttpClient")
    def test_revert_change_apply_without_reviewed_plan_refuses_before_write(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect([self._instance_payload()])
        args = SimpleNamespace(transaction_id="txn-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = balances.cmd_balances_revert_change(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertNotIn("/benefit-programs/v1/balances/changes/txn-1/revert", self._request_paths(mock_client))
