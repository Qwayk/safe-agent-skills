from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import activity_counters
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestActivityCountersCommands(unittest.TestCase):
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
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli activity-counters",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.activity_counters.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.activity_counters.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"activityCounters": []})

        cases = [
            (
                activity_counters.cmd_activity_counters_get,
                SimpleNamespace(member_id="member-1"),
                "GET",
                "/members/v1/activity-counters/member-1",
                None,
            ),
            (
                activity_counters.cmd_activity_counters_query,
                SimpleNamespace(query_json='{"query":{"filter":{"memberId":{"$eq":"member-1"}}}}'),
                "POST",
                "/members/v1/activity-counters/query",
                {"query": {"filter": {"memberId": {"$eq": "member-1"}}}},
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "activity-counters")

    @patch("wix_safe_agent_cli.commands.activity_counters.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.activity_counters.HttpClient")
    def test_set_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = activity_counters.cmd_activity_counters_set(
                SimpleNamespace(member_id="member-1", activity_counters_json='{"activityCounters":{"counters":[{"key":"posts","value":4}]}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "PUT")
        self.assertEqual(payload["plan"]["request"]["path"], "/members/v1/activity-counters/member-1")
        self.assertEqual(payload["plan"]["selector"], {"kind": "activity-counters", "member_id": "member-1", "operation": "set"})
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.activity_counters.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.activity_counters.HttpClient")
    def test_reviewed_plan_apply_sends_request_and_emits_receipt(
        self,
        mock_client: unittest.mock.MagicMock,
        mock_auth: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"activityCounters": {"memberId": "member-1"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = str(Path(tmp) / "plan.json")
            args = SimpleNamespace(
                member_id="member-1",
                activity_counters_json='{"activityCounters":{"counters":[{"key":"posts","value":4}]}}',
            )
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = activity_counters.cmd_activity_counters_set(args, self._ctx(plan_out=plan_path))
            self.assertEqual(dry_rc, 0)
            self.assertTrue(Path(plan_path).exists())
            mock_client.return_value.request.assert_not_called()

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = activity_counters.cmd_activity_counters_set(args, self._ctx(apply=True, yes=True, plan_in=plan_path))
            payload = json.loads(apply_buf.getvalue())

        self.assertEqual(apply_rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["path"], "/members/v1/activity-counters/member-1")
        self.assertEqual(payload["receipt"]["response"], {"activityCounters": {"memberId": "member-1"}})
        call = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(call["method"], "PUT")
        self.assertTrue(str(call["url"]).endswith("/members/v1/activity-counters/member-1"))

    def test_parser_exposes_activity_counters_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["activity-counters", "get", "--member-id", "member-1"], activity_counters.cmd_activity_counters_get, False),
            (["activity-counters", "query"], activity_counters.cmd_activity_counters_query, False),
            (
                ["activity-counters", "set", "--member-id", "member-1", "--activity-counters-json", "{}"],
                activity_counters.cmd_activity_counters_set,
                True,
            ),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
