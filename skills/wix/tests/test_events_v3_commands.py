from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsV3Commands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-v3",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.events_v3.HttpClient")
    def test_get_event_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"event": {"id": "event-1"}})
        args = SimpleNamespace(event_id="event-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_v3.cmd_events_v3_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "events-v3.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/events/v3/events/event-1")

    @patch("wix_safe_agent_cli.commands.events_v3.HttpClient")
    def test_create_event_dry_run_emits_reviewed_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"event": {"id": "event-1"}})
        args = SimpleNamespace(event_json='{"event":{"title":"Launch night"},"draft":true}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_v3.cmd_events_v3_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["method"], "events-v3.create")
        self.assertEqual(plan["request"]["method"], "POST")
        self.assertEqual(plan["request"]["path"], "/events/v3/events")
        self.assertIn("apply requires --plan-in, --apply, and --yes", plan["preconditions"])

    @patch("wix_safe_agent_cli.commands.events_v3.HttpClient")
    def test_cancel_event_without_irreversible_ack_stays_dry_run(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        args = SimpleNamespace(event_id="event-1", request_json="{}")
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/plan.json", ack_irreversible=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_v3.cmd_events_v3_cancel(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_events_v3_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["events-v3", "create", "--event-json", "{}"], events_v3.cmd_events_v3_create, True),
            (["events-v3", "get", "--event-id", "event-1"], events_v3.cmd_events_v3_get, False),
            (["events-v3", "update", "--event-id", "event-1", "--event-json", "{}"], events_v3.cmd_events_v3_update, True),
            (["events-v3", "delete", "--event-id", "event-1"], events_v3.cmd_events_v3_delete, True),
            (["events-v3", "query", "--query-json", "{}"], events_v3.cmd_events_v3_query, False),
            (["events-v3", "bulk-cancel-by-filter", "--filter-json", "{}"], events_v3.cmd_events_v3_bulk_cancel_by_filter, True),
            (["events-v3", "bulk-delete-by-filter", "--filter-json", "{}"], events_v3.cmd_events_v3_bulk_delete_by_filter, True),
            (["events-v3", "cancel", "--event-id", "event-1"], events_v3.cmd_events_v3_cancel, True),
            (["events-v3", "clone", "--event-id", "event-1"], events_v3.cmd_events_v3_clone, True),
            (["events-v3", "count-by-status"], events_v3.cmd_events_v3_count_by_status, False),
            (["events-v3", "get-by-slug", "--slug", "launch-night"], events_v3.cmd_events_v3_get_by_slug, False),
            (["events-v3", "list-by-category", "--category-id", "cat-1"], events_v3.cmd_events_v3_list_by_category, False),
            (["events-v3", "publish-draft", "--event-id", "event-1"], events_v3.cmd_events_v3_publish_draft, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
