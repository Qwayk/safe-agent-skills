from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import loyalty_accounts
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestLoyaltyAccountsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli loyalty-accounts",
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

    def test_parser_exposes_loyalty_accounts_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["loyalty-accounts", "list"], "list", False),
            (["loyalty-accounts", "get", "--account-id", "acct-1"], "get", False),
            (["loyalty-accounts", "query"], "query", False),
            (["loyalty-accounts", "search"], "search", False),
            (["loyalty-accounts", "count"], "count", False),
            (["loyalty-accounts", "get-program-totals"], "get-program-totals", False),
            (["loyalty-accounts", "get-current-member-account"], "get-current-member-account", False),
            (["loyalty-accounts", "get-by-secondary-id", "--contact-id", "contact-1"], "get-by-secondary-id", False),
            (["loyalty-accounts", "create", "--account-json", '{"contactId":"contact-1"}'], "create", True),
            (
                [
                    "loyalty-accounts",
                    "adjust-points",
                    "--account-id",
                    "acct-1",
                    "--adjust-json",
                    '{"amount":10,"revision":"1"}',
                ],
                "adjust-points",
                True,
            ),
            (
                [
                    "loyalty-accounts",
                    "bulk-adjust-points",
                    "--adjust-json",
                    '{"search":{"filter":{"tier.id":{"$eq":"tier-1"}}},"amount":10}',
                ],
                "bulk-adjust-points",
                True,
            ),
            (
                [
                    "loyalty-accounts",
                    "earn-points",
                    "--account-id",
                    "acct-1",
                    "--earn-json",
                    '{"amount":10,"appId":"app-1","idempotencyKey":"key-1"}',
                ],
                "earn-points",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.loyalty_accounts_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_query_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"loyaltyAccounts": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = loyalty_accounts.cmd_loyalty_accounts_query(
                SimpleNamespace(query_json='{"query":{"filter":{"id":{"$eq":"acct-1"}}}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/loyalty-accounts/v1/accounts/query")

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        cases = [
            (
                loyalty_accounts.cmd_loyalty_accounts_list,
                SimpleNamespace(params_json='{"contactIds":["contact-1"]}'),
                "GET",
                "/loyalty-accounts/v1/accounts",
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_get,
                SimpleNamespace(account_id="acct 1"),
                "GET",
                "/loyalty-accounts/v1/accounts/acct%201",
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_search,
                SimpleNamespace(search_json='{"search":{"expression":"Ada"}}'),
                "POST",
                "/loyalty-accounts/v1/accounts/search",
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_count,
                SimpleNamespace(count_json='{"search":{"expression":"Ada"}}'),
                "POST",
                "/loyalty-accounts/v1/accounts/count",
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_get_program_totals,
                SimpleNamespace(),
                "GET",
                "/loyalty-accounts/v1/accounts/program-totals",
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_get_current_member_account,
                SimpleNamespace(),
                "GET",
                "/loyalty-accounts/v1/accounts/my-account",
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_get_by_secondary_id,
                SimpleNamespace(contact_id="contact-1", member_id=None),
                "GET",
                "/loyalty-accounts/v1/accounts/fetch-by",
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
        self.assertEqual(mock_client.return_value.request.call_count, len(cases))

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_and_ack_gated(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                loyalty_accounts.cmd_loyalty_accounts_create,
                SimpleNamespace(account_json='{"contactId":"contact-1"}'),
                "POST",
                "/loyalty-accounts/v1/accounts",
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_adjust_points,
                SimpleNamespace(account_id="acct-1", adjust_json='{"amount":10,"revision":"1"}'),
                "POST",
                "/loyalty-accounts/v1/accounts/acct-1/adjust-points",
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_bulk_adjust_points,
                SimpleNamespace(adjust_json='{"search":{"filter":{"id":{"$hasSome":["acct-1"]}}},"amount":10}'),
                "POST",
                "/loyalty-accounts/v1/accounts/bulk-adjust",
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_earn_points,
                SimpleNamespace(
                    account_id="acct-1",
                    earn_json='{"amount":10,"appId":"app-1","idempotencyKey":"key-1"}',
                ),
                "POST",
                "/loyalty-accounts/v1/accounts/acct-1/earn-points",
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
            (loyalty_accounts.cmd_loyalty_accounts_create, SimpleNamespace(account_json="{}")),
            (
                loyalty_accounts.cmd_loyalty_accounts_adjust_points,
                SimpleNamespace(account_id="acct-1", adjust_json='{"amount":10}'),
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_adjust_points,
                SimpleNamespace(account_id="acct-1", adjust_json='{"amount":10,"balance":20,"revision":"1"}'),
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_bulk_adjust_points,
                SimpleNamespace(adjust_json='{"amount":10}'),
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_earn_points,
                SimpleNamespace(account_id="acct-1", earn_json='{"amount":0,"appId":"app-1","idempotencyKey":"key-1"}'),
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_earn_points,
                SimpleNamespace(account_id="acct-1", earn_json='{"amount":10,"appId":"app-1"}'),
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_get_by_secondary_id,
                SimpleNamespace(contact_id="contact-1", member_id="member-1"),
            ),
            (
                loyalty_accounts.cmd_loyalty_accounts_get_by_secondary_id,
                SimpleNamespace(contact_id=None, member_id=None),
            ),
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
