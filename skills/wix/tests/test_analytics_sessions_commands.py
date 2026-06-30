from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import analytics_sessions
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestAnalyticsSessionsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli analytics-sessions",
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

    def test_parser_exposes_analytics_sessions_commands(self) -> None:
        parser = build_parser()
        cases = [
            (
                [
                    "analytics-sessions",
                    "get-list-job-result",
                    "--job-id",
                    "job-1",
                    "--limit",
                    "100",
                    "--offset",
                    "0",
                ],
                "get-list-job-result",
                False,
            ),
            (
                [
                    "analytics-sessions",
                    "list-async",
                    "--sessions-json",
                    '{"deviceType":{"type":"DESKTOP"},"predefinedTimePeriod":"LAST_7_DAYS"}',
                ],
                "list-async",
                True,
            ),
            (
                ["analytics-sessions", "mark-recordings-deleted", "--session-ids-json", '{"sessionIds":["s1"]}'],
                "mark-recordings-deleted",
                True,
            ),
            (
                ["analytics-sessions", "mark-session-recorded", "--session-id", "s1"],
                "mark-session-recorded",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.analytics_sessions_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_get_list_job_result_uses_official_path_and_params(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"result": {"jobStatus": "FINISHED"}})
        args = SimpleNamespace(job_id="job-1", limit="100", offset="0")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analytics_sessions.cmd_analytics_sessions_get_list_job_result(args, self._ctx())

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/analytics/v1/sessions/list/result")
        self.assertEqual(payload["request"]["params"], {"jobId": "job-1", "limit": 100, "offset": 0})

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_plan_first_writes_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                analytics_sessions.cmd_analytics_sessions_list_async,
                SimpleNamespace(sessions_json='{"deviceType":{"type":"DESKTOP"},"predefinedTimePeriod":"LAST_7_DAYS"}'),
                "/analytics/v1/sessions/list/async",
                False,
            ),
            (
                analytics_sessions.cmd_analytics_sessions_mark_recordings_deleted,
                SimpleNamespace(session_ids_json='{"sessionIds":["s1"]}'),
                "/analytics/v1/sessions/recordings-deleted",
                True,
            ),
            (
                analytics_sessions.cmd_analytics_sessions_mark_session_recorded,
                SimpleNamespace(session_id="s1"),
                "/analytics/v1/sessions/session-recorded",
                True,
            ),
        ]
        for func, args, path, needs_ack in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], "POST")
                self.assertEqual(payload["plan"]["request"]["path"], path)
                if needs_ack:
                    self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_validates_required_filters_and_ids(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (analytics_sessions.cmd_analytics_sessions_list_async, SimpleNamespace(sessions_json='{"deviceType":{"type":"DESKTOP"}}')),
            (
                analytics_sessions.cmd_analytics_sessions_mark_recordings_deleted,
                SimpleNamespace(session_ids_json='{"sessionIds":[]}'),
            ),
            (analytics_sessions.cmd_analytics_sessions_mark_session_recorded, SimpleNamespace(session_id="")),
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
