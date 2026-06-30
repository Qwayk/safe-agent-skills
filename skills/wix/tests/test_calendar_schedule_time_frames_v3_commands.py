from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import calendar_schedule_time_frames_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCalendarScheduleTimeFramesV3Parser(unittest.TestCase):
    def test_parser_recognizes_time_frame_commands_as_reads(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["calendar-schedule-time-frames-v3", "get", "--schedule-id", "schedule-1"])
        self.assertEqual(get_args.calendar_schedule_time_frames_v3_cmd, "get")
        self.assertFalse(get_args.write_capable)
        self.assertIs(get_args.func, calendar_schedule_time_frames_v3.cmd_calendar_schedule_time_frames_v3_get)

        list_args = parser.parse_args(["calendar-schedule-time-frames-v3", "list", "--ids-json", '["schedule-1"]'])
        self.assertEqual(list_args.calendar_schedule_time_frames_v3_cmd, "list")
        self.assertFalse(list_args.write_capable)
        self.assertIs(list_args.func, calendar_schedule_time_frames_v3.cmd_calendar_schedule_time_frames_v3_list)

        expected = {"get", "list"}
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["calendar-schedule-time-frames-v3"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestCalendarScheduleTimeFramesV3Commands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    @patch("wix_safe_agent_cli.commands.calendar_schedule_time_frames_v3.HttpClient")
    @patch("wix_safe_agent_cli.commands.calendar_schedule_time_frames_v3.resolve_auth_mode")
    def test_get_uses_official_path_and_optional_time_zone(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"scheduleTimeFrame": {"id": "schedule-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_schedule_time_frames_v3.cmd_calendar_schedule_time_frames_v3_get(
                SimpleNamespace(schedule_id="schedule-1", time_zone="America/New_York"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "calendar-schedule-time-frames-v3.get")
        self.assertEqual(payload["request"]["path"], "/calendar/v3/schedules/timeframe/schedule-1")
        self.assertEqual(payload["request"]["params"], {"timeZone": "America/New_York"})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"], None)

    @patch("wix_safe_agent_cli.commands.calendar_schedule_time_frames_v3.HttpClient")
    @patch("wix_safe_agent_cli.commands.calendar_schedule_time_frames_v3.resolve_auth_mode")
    def test_list_uses_required_ids_query_param(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"scheduleTimeFrames": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_schedule_time_frames_v3.cmd_calendar_schedule_time_frames_v3_list(
                SimpleNamespace(ids_json='["schedule-1","schedule-2"]', time_zone=None),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/calendar/v3/schedules/timeframe")
        self.assertEqual(payload["request"]["params"], {"ids": ["schedule-1", "schedule-2"]})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], {"ids": ["schedule-1", "schedule-2"]})

    def test_list_requires_non_empty_ids_json_array(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_schedule_time_frames_v3.cmd_calendar_schedule_time_frames_v3_list(
                SimpleNamespace(ids_json="[]", time_zone=None),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("at least one schedule ID", payload["error"])


if __name__ == "__main__":
    unittest.main()
