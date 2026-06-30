from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_schedule_items
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsScheduleItemsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-schedule-items",
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

    @patch("wix_safe_agent_cli.commands.events_schedule_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_schedule_items.HttpClient")
    def test_get_uses_expected_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"scheduleItem": {"id": "item-1"}})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_schedule_items.cmd_events_schedule_items_get(SimpleNamespace(item_id="item-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "events-schedule-items.get")
        self.assertEqual(payload["request"]["path"], "/events/v1/schedule/item-1")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "events-schedule-items")

    @patch("wix_safe_agent_cli.commands.events_schedule_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_schedule_items.HttpClient")
    def test_add_is_plan_first_for_draft_schedule(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_schedule_items.cmd_events_schedule_items_add(
                SimpleNamespace(schedule_item_json='{"scheduleItem":{"eventId":"event-1","name":"Opening"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/events/v1/schedule/draft")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_schedule_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_schedule_items.HttpClient")
    def test_delete_schedule_item_requires_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json")
        with redirect_stdout(buf):
            rc = events_schedule_items.cmd_events_schedule_items_delete(
                SimpleNamespace(request_json='{"eventId":"event-1","itemId":"item-1"}'),
                ctx,
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/events/v1/schedule/draft/items")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_schedule_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_schedule_items.HttpClient")
    def test_list_bookmarks_accepts_official_query_params(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"bookmarks": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_schedule_items.cmd_events_schedule_items_list_bookmarks(
                SimpleNamespace(params_json='{"eventId":"event-1"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/events/v1/schedule/bookmarks")
        self.assertEqual(payload["request"]["params"], {"eventId": "event-1"})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], {"eventId": "event-1"})

    def test_parser_exposes_all_events_schedule_items_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["events-schedule-items", "get", "--item-id", "item-1"], events_schedule_items.cmd_events_schedule_items_get, False),
            (["events-schedule-items", "query"], events_schedule_items.cmd_events_schedule_items_query, False),
            (["events-schedule-items", "add", "--schedule-item-json", "{}"], events_schedule_items.cmd_events_schedule_items_add, True),
            (["events-schedule-items", "create-bookmark", "--item-id", "item-1"], events_schedule_items.cmd_events_schedule_items_create_bookmark, True),
            (["events-schedule-items", "delete-bookmark", "--item-id", "item-1"], events_schedule_items.cmd_events_schedule_items_delete_bookmark, True),
            (["events-schedule-items", "delete", "--request-json", "{}"], events_schedule_items.cmd_events_schedule_items_delete, True),
            (["events-schedule-items", "discard-draft", "--request-json", "{}"], events_schedule_items.cmd_events_schedule_items_discard_draft, True),
            (["events-schedule-items", "list-bookmarks"], events_schedule_items.cmd_events_schedule_items_list_bookmarks, False),
            (["events-schedule-items", "list"], events_schedule_items.cmd_events_schedule_items_list, False),
            (["events-schedule-items", "publish-draft", "--request-json", "{}"], events_schedule_items.cmd_events_schedule_items_publish_draft, True),
            (["events-schedule-items", "reschedule-draft", "--request-json", "{}"], events_schedule_items.cmd_events_schedule_items_reschedule_draft, True),
            (["events-schedule-items", "update", "--item-id", "item-1", "--schedule-item-json", "{}"], events_schedule_items.cmd_events_schedule_items_update, True),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
