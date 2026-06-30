from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_categories
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsCategoriesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-categories",
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

    @patch("wix_safe_agent_cli.commands.events_categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_categories.HttpClient")
    def test_get_uses_expected_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"category": {"id": "cat-1"}})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_categories.cmd_events_categories_get(SimpleNamespace(category_id="cat-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "events-categories.get")
        self.assertEqual(payload["request"]["path"], "/events/v1/categories/cat-1")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "events-categories")

    @patch("wix_safe_agent_cli.commands.events_categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_categories.HttpClient")
    def test_assign_events_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_categories.cmd_events_categories_assign_events(
                SimpleNamespace(category_id="cat-1", events_json='{"eventIds":["event-1"]}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/events/v1/categories/cat-1/events")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_categories.HttpClient")
    def test_unassign_events_requires_ack_and_encodes_repeated_event_ids(
        self,
        mock_client: unittest.mock.MagicMock,
        mock_auth: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json")
        with redirect_stdout(buf):
            rc = events_categories.cmd_events_categories_unassign_events(
                SimpleNamespace(category_id="cat-1", event_ids="event-1,event-2"),
                ctx,
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/events/v1/categories/cat-1/events?eventId=event-1&eventId=event-2",
        )
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_categories.HttpClient")
    def test_bulk_unassign_events_uses_official_bulk_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_categories.cmd_events_categories_bulk_unassign_events(
                SimpleNamespace(category_ids="cat-1,cat-2", event_ids="event-1"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/events/v1/bulk/categories/events?categoryId=cat-1&categoryId=cat-2&eventId=event-1",
        )
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_events_categories_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["events-categories", "create", "--category-json", "{}"], events_categories.cmd_events_categories_create, True),
            (["events-categories", "bulk-create", "--categories-json", "{}"], events_categories.cmd_events_categories_bulk_create, True),
            (["events-categories", "update", "--category-id", "cat-1", "--category-json", "{}"], events_categories.cmd_events_categories_update, True),
            (["events-categories", "delete", "--category-id", "cat-1"], events_categories.cmd_events_categories_delete, True),
            (["events-categories", "query"], events_categories.cmd_events_categories_query, False),
            (["events-categories", "assign-events", "--category-id", "cat-1", "--events-json", "{}"], events_categories.cmd_events_categories_assign_events, True),
            (["events-categories", "unassign-events", "--category-id", "cat-1", "--event-ids", "event-1"], events_categories.cmd_events_categories_unassign_events, True),
            (["events-categories", "bulk-assign-events", "--request-json", "{}"], events_categories.cmd_events_categories_bulk_assign_events, True),
            (["events-categories", "bulk-unassign-events", "--category-ids", "cat-1", "--event-ids", "event-1"], events_categories.cmd_events_categories_bulk_unassign_events, True),
            (["events-categories", "get", "--category-id", "cat-1"], events_categories.cmd_events_categories_get, False),
            (["events-categories", "reorder-events", "--category-id", "cat-1", "--request-json", "{}"], events_categories.cmd_events_categories_reorder_events, True),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
