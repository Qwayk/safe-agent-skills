from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import loyalty_transactions
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestLoyaltyTransactionsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli loyalty-transactions",
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

    def test_parser_exposes_loyalty_transaction_commands_as_reads(self) -> None:
        parser = build_parser()
        cases = [
            (["loyalty-transactions", "get", "--transaction-id", "tx-1"], "get"),
            (["loyalty-transactions", "query"], "query"),
        ]
        for argv, command in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.loyalty_transactions_cmd, command)
                self.assertFalse(args.write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"loyaltyTransactions": []})
        cases = [
            (
                loyalty_transactions.cmd_loyalty_transactions_get,
                SimpleNamespace(transaction_id="tx-1"),
                "GET",
                "/loyalty-transactions/v1/loyalty-transactions/tx-1",
            ),
            (
                loyalty_transactions.cmd_loyalty_transactions_query,
                SimpleNamespace(query_json='{"query":{"filter":{"transactionType":{"$eq":"EARN"}}}}'),
                "POST",
                "/loyalty-transactions/v1/loyalty-transactions/query",
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

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_get_requires_transaction_id(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = loyalty_transactions.cmd_loyalty_transactions_get(SimpleNamespace(transaction_id=" "), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
