from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_moderation_rules
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityModerationRulesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli community-moderation-rules",
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

    def test_parser_exposes_community_moderation_rules_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["community-moderation-rules", "create", "--rule-json", '{"rule":{"namespace":"comments/app"}}'], "create", True),
            (["community-moderation-rules", "get", "--rule-id", "rule-1"], "get", False),
            (
                ["community-moderation-rules", "update", "--rule-id", "rule-1", "--rule-json", '{"rule":{"revision":"1"}}'],
                "update",
                True,
            ),
            (["community-moderation-rules", "delete", "--rule-id", "rule-1"], "delete", True),
            (["community-moderation-rules", "query"], "query", False),
            (
                ["community-moderation-rules", "check-content", "--request-json", '{"namespace":"comments/app","content":{}}'],
                "check-content",
                False,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_moderation_rules_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths_and_bodies(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"rules": []})
        cases = [
            (
                community_moderation_rules.cmd_community_moderation_rules_get,
                SimpleNamespace(rule_id="rule-1"),
                "GET",
                "/moderation/v1/rules/rule-1",
                None,
            ),
            (
                community_moderation_rules.cmd_community_moderation_rules_query,
                SimpleNamespace(request_json='{"query":{"filter":{"namespace":"comments/app"}}}'),
                "POST",
                "/moderation/v1/rules/query",
                {"query": {"filter": {"namespace": "comments/app"}}},
            ),
            (
                community_moderation_rules.cmd_community_moderation_rules_check_content,
                SimpleNamespace(request_json='{"namespace":"comments/app","content":{"text":"hello"}}'),
                "POST",
                "/moderation/v1/rules/check",
                {"namespace": "comments/app", "content": {"text": "hello"}},
            ),
        ]
        for func, args, method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_with_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                community_moderation_rules.cmd_community_moderation_rules_create,
                SimpleNamespace(rule_json='{"rule":{"namespace":"comments/app"}}'),
                "POST",
                "/moderation/v1/rules",
            ),
            (
                community_moderation_rules.cmd_community_moderation_rules_update,
                SimpleNamespace(rule_id="rule-1", rule_json='{"rule":{"revision":"1","namespace":"comments/app"}}'),
                "PATCH",
                "/moderation/v1/rules/rule-1",
            ),
            (
                community_moderation_rules.cmd_community_moderation_rules_delete,
                SimpleNamespace(rule_id="rule-1"),
                "DELETE",
                "/moderation/v1/rules/rule-1",
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
    def test_rejects_empty_create_body(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_moderation_rules.cmd_community_moderation_rules_create(SimpleNamespace(rule_json="{}"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
