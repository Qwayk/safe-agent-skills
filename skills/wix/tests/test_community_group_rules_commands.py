from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_group_rules
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityGroupRulesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli community-group-rules",
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

    def test_parser_exposes_community_group_rules_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["community-group-rules", "list", "--group-id", "group-1"], "list", False),
            (
                ["community-group-rules", "create-or-replace", "--group-id", "group-1", "--rules-json", '{"rules":[]}'],
                "create-or-replace",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_group_rules_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_list_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"rules": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_rules.cmd_community_group_rules_list(SimpleNamespace(group_id="group-1"), self._ctx())
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith("/social-groups/v2/rules/group-1"))

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_create_or_replace_is_plan_first_and_requires_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"rules": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_rules.cmd_community_group_rules_create_or_replace(
                SimpleNamespace(group_id="group-1", rules_json='{"rules":[]}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "PUT")
        self.assertEqual(payload["plan"]["request"]["path"], "/social-groups/v2/rules/group-1")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_create_or_replace_validates_rules_array_limit(self, mock_client: unittest.mock.MagicMock) -> None:
        rules = [{"title": str(i)} for i in range(101)]
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_rules.cmd_community_group_rules_create_or_replace(
                SimpleNamespace(group_id="group-1", rules_json=json.dumps({"rules": rules})),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
