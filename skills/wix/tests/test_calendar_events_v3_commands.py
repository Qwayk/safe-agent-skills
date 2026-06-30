from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import calendar_events_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCalendarEventsV3Commands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli calendar-events-v3",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.calendar_events_v3.HttpClient")
    @patch("wix_safe_agent_cli.commands.calendar_events_v3.resolve_auth_mode")
    def test_get_event_builds_expected_request(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"event": {"id": "event-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_events_v3.cmd_calendar_events_v3_get(
                SimpleNamespace(event_id="event-1", fields_json='["PI_FIELDS"]', time_zone="UTC"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "calendar-events-v3.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/calendar/v3/events/event-1")
        self.assertEqual(payload["request"]["params"], {"fields": ["PI_FIELDS"], "timeZone": "UTC"})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"], None)

    @patch("wix_safe_agent_cli.commands.calendar_events_v3.HttpClient")
    @patch("wix_safe_agent_cli.commands.calendar_events_v3.resolve_auth_mode")
    def test_list_event_uses_required_event_ids_query_param(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"events": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_events_v3.cmd_calendar_events_v3_list(
                SimpleNamespace(event_ids_json='["event-1","event-2"]', fields_json=None, time_zone=None),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/calendar/v3/events")
        self.assertEqual(payload["request"]["params"], {"eventIds": ["event-1", "event-2"]})

    @patch("wix_safe_agent_cli.commands.calendar_events_v3.HttpClient")
    @patch("wix_safe_agent_cli.commands.calendar_events_v3.resolve_auth_mode")
    def test_query_event_merges_helper_options_into_official_body(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"events": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_events_v3.cmd_calendar_events_v3_query(
                SimpleNamespace(
                    query_json='{"query":{"filter":{"type":{"$eq":"EVENT"}}}}',
                    time_zone="UTC",
                    from_local_date="2026-07-01T00:00:00",
                    to_local_date="2026-07-31T23:59:59",
                    recurrence_type_json='["NONE"]',
                    fields_json=None,
                ),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        body = payload["request"]["body"]
        self.assertEqual(body["timeZone"], "UTC")
        self.assertEqual(body["fromLocalDate"], "2026-07-01T00:00:00")
        self.assertEqual(body["recurrenceType"], ["NONE"])

    def test_create_event_dry_run_emits_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_events_v3.cmd_calendar_events_v3_create(
                SimpleNamespace(
                    event_json='{"scheduleId":"schedule-1","start":{"localDate":"2026-07-01T09:00:00"},"end":{"localDate":"2026-07-01T10:00:00"}}',
                    idempotency_key="550e8400-e29b-41d4-a716-446655440000",
                    time_zone=None,
                    return_entity=None,
                    participant_notification_json=None,
                ),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["method"], "calendar-events-v3.create")
        self.assertEqual(plan["request"]["path"], "/calendar/v3/events")
        self.assertEqual(plan["request"]["body"]["event"]["scheduleId"], "schedule-1")
        self.assertEqual(plan["request"]["body"]["idempotencyKey"], "550e8400-e29b-41d4-a716-446655440000")

    def test_update_requires_matching_event_id_and_revision(self) -> None:
        missing_revision = io.StringIO()
        with redirect_stdout(missing_revision):
            rc_missing = calendar_events_v3.cmd_calendar_events_v3_update(
                SimpleNamespace(event_id="event-1", event_json='{"id":"event-1","title":"New"}', time_zone=None, return_entity=None, participant_notification_json=None),
                self._ctx(),
            )
        missing_payload = json.loads(missing_revision.getvalue())

        mismatched_id = io.StringIO()
        with redirect_stdout(mismatched_id):
            rc_mismatch = calendar_events_v3.cmd_calendar_events_v3_update(
                SimpleNamespace(event_id="event-1", event_json='{"id":"event-2","revision":"1"}', time_zone=None, return_entity=None, participant_notification_json=None),
                self._ctx(),
            )
        mismatch_payload = json.loads(mismatched_id.getvalue())

        self.assertEqual(rc_missing, 1)
        self.assertIn("event.revision is required", missing_payload["error"])
        self.assertEqual(rc_mismatch, 0)
        self.assertTrue(mismatch_payload["refused"])
        self.assertIn("does not match --event-id", mismatch_payload["reasons"][0])

    def test_cancel_and_restore_defaults_require_irreversible_ack(self) -> None:
        for func, args in (
            (
                calendar_events_v3.cmd_calendar_events_v3_cancel,
                SimpleNamespace(event_id="event-1", time_zone=None, return_entity=None, participant_notification_json=None),
            ),
            (
                calendar_events_v3.cmd_calendar_events_v3_restore_defaults,
                SimpleNamespace(event_id="event-1", fields_json='["TIME"]', time_zone=None, return_entity=None, participant_notification_json=None),
            ),
        ):
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx(apply=True, yes=True, plan_in="/tmp/plan.json", ack_irreversible=False))
                payload = json.loads(buf.getvalue())

                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    def test_list_by_contact_requires_date_window_or_cursor(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_events_v3.cmd_calendar_events_v3_list_by_contact(
                SimpleNamespace(contact_id="contact-1", from_local_date=None, to_local_date=None, time_zone=None, app_id=None, cursor_paging_json=None, sort_json=None),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("--from-local-date and --to-local-date are required", payload["error"])

    def test_parser_exposes_all_calendar_events_v3_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["calendar-events-v3", "create", "--event-json", "{}"], calendar_events_v3.cmd_calendar_events_v3_create, True),
            (["calendar-events-v3", "get", "--event-id", "event-1"], calendar_events_v3.cmd_calendar_events_v3_get, False),
            (["calendar-events-v3", "update", "--event-id", "event-1", "--event-json", "{}"], calendar_events_v3.cmd_calendar_events_v3_update, True),
            (["calendar-events-v3", "query"], calendar_events_v3.cmd_calendar_events_v3_query, False),
            (["calendar-events-v3", "list", "--event-ids-json", '["event-1"]'], calendar_events_v3.cmd_calendar_events_v3_list, False),
            (["calendar-events-v3", "bulk-create", "--events-json", "[]"], calendar_events_v3.cmd_calendar_events_v3_bulk_create, True),
            (["calendar-events-v3", "bulk-update", "--events-json", "[]"], calendar_events_v3.cmd_calendar_events_v3_bulk_update, True),
            (["calendar-events-v3", "bulk-cancel", "--event-ids-json", '["event-1"]'], calendar_events_v3.cmd_calendar_events_v3_bulk_cancel, True),
            (["calendar-events-v3", "cancel", "--event-id", "event-1"], calendar_events_v3.cmd_calendar_events_v3_cancel, True),
            (["calendar-events-v3", "list-by-contact", "--contact-id", "contact-1"], calendar_events_v3.cmd_calendar_events_v3_list_by_contact, False),
            (["calendar-events-v3", "list-by-member", "--member-id", "member-1"], calendar_events_v3.cmd_calendar_events_v3_list_by_member, False),
            (["calendar-events-v3", "restore-defaults", "--event-id", "event-1", "--fields-json", '["TIME"]'], calendar_events_v3.cmd_calendar_events_v3_restore_defaults, True),
            (["calendar-events-v3", "split-recurring", "--recurring-event-id", "event-1", "--split-local-date", "2026-07-01T09:00:00"], calendar_events_v3.cmd_calendar_events_v3_split_recurring, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)


if __name__ == "__main__":
    unittest.main()
