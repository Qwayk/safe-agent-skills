from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import calendar_schedules_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCalendarSchedulesV3Parser(unittest.TestCase):
    def test_parser_recognizes_schedule_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["calendar-schedules-v3", "get", "--schedule-id", "schedule-1"])
        self.assertEqual(read_args.calendar_schedules_v3_cmd, "get")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, calendar_schedules_v3.cmd_calendar_schedules_v3_get)

        write_args = parser.parse_args(["calendar-schedules-v3", "create", "--schedule-json", '{"name":"Staff calendar"}'])
        self.assertEqual(write_args.calendar_schedules_v3_cmd, "create")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, calendar_schedules_v3.cmd_calendar_schedules_v3_create)

        expected = {"get", "query", "create", "update", "cancel"}
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["calendar-schedules-v3"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestCalendarSchedulesV3Commands(unittest.TestCase):
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
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }

    @patch("wix_safe_agent_cli.commands.calendar_schedules_v3.HttpClient")
    @patch("wix_safe_agent_cli.commands.calendar_schedules_v3.resolve_auth_mode")
    def test_get_uses_official_path(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"schedule": {"id": "schedule-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_schedules_v3.cmd_calendar_schedules_v3_get(SimpleNamespace(schedule_id="schedule-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "calendar-schedules-v3.get")
        self.assertEqual(payload["request"]["path"], "/calendar/v3/schedules/schedule-1")
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"], None)

    @patch("wix_safe_agent_cli.commands.calendar_schedules_v3.HttpClient")
    @patch("wix_safe_agent_cli.commands.calendar_schedules_v3.resolve_auth_mode")
    def test_query_wraps_filter_json_in_official_query_body(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"schedules": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_schedules_v3.cmd_calendar_schedules_v3_query(SimpleNamespace(query_json='{"filter":{"status":{"$eq":"ACTIVE"}}}'), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/calendar/v3/schedules/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"status": {"$eq": "ACTIVE"}}}})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "POST")

    def test_create_builds_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_schedules_v3.cmd_calendar_schedules_v3_create(
                SimpleNamespace(schedule_json='{"name":"Class calendar","appId":"13d21c63-b5ec-5912-8397-c3a5ddb27a97"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/calendar/v3/schedules")
        self.assertEqual(payload["plan"]["request"]["body"]["schedule"]["name"], "Class calendar")
        self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    def test_update_requires_revision_and_matching_schedule_id(self) -> None:
        missing_revision = io.StringIO()
        with redirect_stdout(missing_revision):
            rc_missing = calendar_schedules_v3.cmd_calendar_schedules_v3_update(
                SimpleNamespace(schedule_id="schedule-1", schedule_json='{"id":"schedule-1","name":"New"}'),
                self._ctx(),
            )
        missing_payload = json.loads(missing_revision.getvalue())

        mismatched_id = io.StringIO()
        with redirect_stdout(mismatched_id):
            rc_mismatch = calendar_schedules_v3.cmd_calendar_schedules_v3_update(
                SimpleNamespace(schedule_id="schedule-1", schedule_json='{"id":"schedule-2","revision":"1"}'),
                self._ctx(),
            )
        mismatch_payload = json.loads(mismatched_id.getvalue())

        self.assertEqual(rc_missing, 1)
        self.assertIn("schedule.revision is required", missing_payload["error"])
        self.assertEqual(rc_mismatch, 0)
        self.assertTrue(mismatch_payload["refused"])
        self.assertIn("does not match --schedule-id", mismatch_payload["reasons"][0])

    def test_cancel_builds_irreversible_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_schedules_v3.cmd_calendar_schedules_v3_cancel(
                SimpleNamespace(schedule_id="schedule-1", request_json='{"preserveFutureEventsWithParticipants":true}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/calendar/v3/schedules/schedule-1/cancel")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])


if __name__ == "__main__":
    unittest.main()
