from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import accounts
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestAccountsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token=None,
            api_key="acct-api-key",
            account_id="acct-001",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        if cfg_override:
            for key, value in cfg_override.items():
                setattr(cfg, key, value)

        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli accounts get",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_accounts_get(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["accounts", "get", "--account-id", "5f2c6d47-2c24-4ab5-8c3a-1d7d3d1d8e2a"])

        self.assertEqual(parsed.accounts_cmd, "get")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.account_id, "5f2c6d47-2c24-4ab5-8c3a-1d7d3d1d8e2a")
        self.assertEqual(parsed.func.__name__, "cmd_accounts_get")

    def test_parser_recognizes_accounts_list_child_accounts(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["accounts", "list-child-accounts", "--limit", "0", "--offset", "3"])

        self.assertEqual(parsed.accounts_cmd, "list-child-accounts")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.limit, 0)
        self.assertEqual(parsed.offset, 3)
        self.assertEqual(parsed.func.__name__, "cmd_accounts_list_child_accounts")

    @patch("wix_safe_agent_cli.commands.accounts.HttpClient")
    def test_accounts_get_builds_expected_request_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "account": {
                    "accountId": "5f2c6d47-2c24-4ab5-8c3a-1d7d3d1d8e2a",
                    "accountName": "Example Co",
                }
            }
        )
        args = SimpleNamespace(account_id="5f2c6d47-2c24-4ab5-8c3a-1d7d3d1d8e2a")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = accounts.cmd_accounts_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "accounts.get")
        self.assertEqual(payload["auth_mode"], "account_api_key")
        self.assertEqual(
            payload["request"],
            {
                "method": "GET",
                "path": "/accounts/v1/accounts/5f2c6d47-2c24-4ab5-8c3a-1d7d3d1d8e2a",
            },
        )
        self.assertEqual(
            payload["response"],
            {
                "account": {
                    "accountId": "5f2c6d47-2c24-4ab5-8c3a-1d7d3d1d8e2a",
                    "accountName": "Example Co",
                }
            },
        )

        call = mock_client.return_value.request.call_args
        headers = call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")
        self.assertNotIn("Content-Type", headers)

        self.assertEqual(ctx["audit"].writes[0][0], "accounts.get")
        self.assertEqual(ctx["audit"].writes[0][1]["request"]["path"], "/accounts/v1/accounts/5f2c6d47-2c24-4ab5-8c3a-1d7d3d1d8e2a")

    @patch("wix_safe_agent_cli.commands.accounts.HttpClient")
    def test_accounts_list_child_accounts_builds_expected_request_and_params(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "childAccounts": [{"accountId": "child-1"}],
                "pagingMetadata": {"count": 1, "offset": 3, "total": 1, "tooManyToCount": False},
            }
        )
        args = SimpleNamespace(limit=0, offset=3)
        ctx = self._ctx(command_str="wix-safe-agent-cli accounts list-child-accounts")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = accounts.cmd_accounts_list_child_accounts(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "accounts.list-child-accounts")
        self.assertEqual(payload["auth_mode"], "account_api_key")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/accounts/v1/account/child-accounts")
        self.assertEqual(payload["request"]["params"], {"paging.limit": 0, "paging.offset": 3})
        self.assertEqual(payload["response"]["childAccounts"], [{"accountId": "child-1"}])

        call = mock_client.return_value.request.call_args
        headers = call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")
        self.assertNotIn("Content-Type", headers)

    @patch("wix_safe_agent_cli.commands.accounts.HttpClient")
    def test_accounts_get_rejects_empty_account_id(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(account_id="   ")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = accounts.cmd_accounts_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("Missing --account-id", payload["error"])

    @patch("wix_safe_agent_cli.commands.accounts.HttpClient")
    def test_accounts_list_child_accounts_rejects_limit_over_50(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(limit=51, offset=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = accounts.cmd_accounts_list_child_accounts(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--limit must be between 0 and 50", payload["error"])

    @patch("wix_safe_agent_cli.commands.accounts.HttpClient")
    def test_accounts_list_child_accounts_rejects_negative_offset(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(limit=None, offset=-1)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = accounts.cmd_accounts_list_child_accounts(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--offset must be 0 or greater", payload["error"])
