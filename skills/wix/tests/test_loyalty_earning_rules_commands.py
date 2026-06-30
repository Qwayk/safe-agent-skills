from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import loyalty_earning_rules
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestLoyaltyEarningRulesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli loyalty-earning-rules",
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

    def test_parser_exposes_loyalty_earning_rules_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["loyalty-earning-rules", "list"], "list", False),
            (["loyalty-earning-rules", "get", "--rule-id", "rule-1"], "get", False),
            (
                ["loyalty-earning-rules", "create", "--rule-json", '{"earningRule":{"title":"Buy"}}'],
                "create",
                True,
            ),
            (
                [
                    "loyalty-earning-rules",
                    "update",
                    "--rule-id",
                    "rule-1",
                    "--rule-json",
                    '{"earningRule":{"revision":"1"}}',
                ],
                "update",
                True,
            ),
            (["loyalty-earning-rules", "delete", "--rule-id", "rule-1", "--revision", "1"], "delete", True),
            (
                ["loyalty-earning-rules", "bulk-create", "--rules-json", '{"earningRules":[{"title":"Buy"}]}'],
                "bulk-create",
                True,
            ),
            (
                [
                    "loyalty-earning-rules",
                    "create-custom",
                    "--request-json",
                    '{"type":"SOCIAL_MEDIA","earningRule":{"title":"Follow"}}',
                ],
                "create-custom",
                True,
            ),
            (
                ["loyalty-earning-rules", "delete-automation", "--rule-id", "rule-1"],
                "delete-automation",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.loyalty_earning_rules_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"earningRules": []})
        cases = [
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_list,
                SimpleNamespace(params_json='{"triggerAppId":"app-1"}'),
                "GET",
                "/_api/loyalty-earning-rules/v1/earning-rules/rules",
                {"triggerAppId": "app-1"},
            ),
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_get,
                SimpleNamespace(rule_id="rule-1"),
                "GET",
                "/_api/loyalty-earning-rules/v1/earning-rules/rule-1",
                None,
            ),
        ]
        for func, args, method, path, params in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if params is not None:
                    self.assertEqual(payload["request"]["params"], params)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_and_ack_gated(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_create,
                SimpleNamespace(rule_json='{"earningRule":{"title":"Buy","status":"ACTIVE"}}'),
                "POST",
                "/_api/loyalty-earning-rules/v1/earning-rules",
            ),
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_update,
                SimpleNamespace(rule_id="rule-1", rule_json='{"earningRule":{"revision":"1","status":"PAUSED"}}'),
                "PUT",
                "/_api/loyalty-earning-rules/v1/earning-rules/rule-1",
            ),
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_delete,
                SimpleNamespace(rule_id="rule-1", revision="1"),
                "DELETE",
                "/_api/loyalty-earning-rules/v1/earning-rules/rule-1?revision=1",
            ),
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_bulk_create,
                SimpleNamespace(rules_json='{"earningRules":[{"title":"Buy"}]}'),
                "POST",
                "/_api/loyalty-earning-rules/v1/bulk/earning-rules/create",
            ),
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_create_custom,
                SimpleNamespace(request_json='{"type":"SOCIAL_MEDIA","earningRule":{"title":"Follow"}}'),
                "POST",
                "/_api/loyalty-earning-rules/v1/earning-rules/custom",
            ),
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_delete_automation,
                SimpleNamespace(rule_id="rule-1"),
                "DELETE",
                "/_api/loyalty-earning-rules/v1/automation-earning-rules/rule-1",
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
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_create,
                SimpleNamespace(rule_json="{}"),
            ),
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_update,
                SimpleNamespace(rule_id="rule-1", rule_json='{"earningRule":{"title":"Buy"}}'),
            ),
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_bulk_create,
                SimpleNamespace(rules_json='{"earningRules":[]}'),
            ),
            (
                loyalty_earning_rules.cmd_loyalty_earning_rules_create_custom,
                SimpleNamespace(request_json='{"earningRule":{"title":"Follow"}}'),
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
