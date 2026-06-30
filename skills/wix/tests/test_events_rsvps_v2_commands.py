from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_rsvps_v2
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsRsvpsV2Commands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-rsvps-v2",
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

    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.HttpClient")
    def test_get_uses_expected_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"rsvp": {"id": "rsvp-1"}})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_rsvps_v2.cmd_events_rsvps_v2_get(SimpleNamespace(rsvp_id="rsvp-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "events-rsvps-v2.get")
        self.assertEqual(payload["request"]["path"], "/events/v2/rsvps/rsvp-1")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "events-rsvps-v2")

    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.HttpClient")
    def test_query_and_search_post_bodies(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"rsvps": []})

        query_buf = io.StringIO()
        with redirect_stdout(query_buf):
            rc_query = events_rsvps_v2.cmd_events_rsvps_v2_query(SimpleNamespace(query_json='{"query":{"filter":{"eventId":"event-1"}}}'), self._ctx())
        query_payload = json.loads(query_buf.getvalue())

        search_buf = io.StringIO()
        with redirect_stdout(search_buf):
            rc_search = events_rsvps_v2.cmd_events_rsvps_v2_search(SimpleNamespace(search_json='{"search":{"filter":{"status":"YES"}}}'), self._ctx())
        search_payload = json.loads(search_buf.getvalue())

        self.assertEqual(rc_query, 0)
        self.assertEqual(query_payload["request"]["path"], "/events/v2/rsvps/query")
        self.assertEqual(query_payload["request"]["body"], {"query": {"filter": {"eventId": "event-1"}}})
        self.assertEqual(rc_search, 0)
        self.assertEqual(search_payload["request"]["path"], "/events/v2/rsvps/search")
        self.assertEqual(search_payload["request"]["body"], {"search": {"filter": {"status": "YES"}}})

    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.HttpClient")
    def test_list_summary_sends_repeated_event_ids_as_params(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"summaries": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_rsvps_v2.cmd_events_rsvps_v2_list_summary(SimpleNamespace(event_id=["event-1", "event-2"]), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/events/v2/rsvps/summaries")
        self.assertEqual(payload["request"]["params"], {"eventId": ["event-1", "event-2"]})

    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.HttpClient")
    def test_create_and_check_in_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        create_buf = io.StringIO()
        with redirect_stdout(create_buf):
            rc_create = events_rsvps_v2.cmd_events_rsvps_v2_create(SimpleNamespace(rsvp_json='{"rsvp":{"eventId":"event-1","status":"YES"}}'), self._ctx())
        create_payload = json.loads(create_buf.getvalue())

        check_in_buf = io.StringIO()
        with redirect_stdout(check_in_buf):
            rc_check_in = events_rsvps_v2.cmd_events_rsvps_v2_check_in(SimpleNamespace(rsvp_id="rsvp-1", request_json='{"guestIds":[1]}'), self._ctx())
        check_in_payload = json.loads(check_in_buf.getvalue())

        self.assertEqual(rc_create, 0)
        self.assertTrue(create_payload["dry_run"])
        self.assertEqual(create_payload["plan"]["request"]["path"], "/events/v2/rsvps")
        self.assertEqual(rc_check_in, 0)
        self.assertTrue(check_in_payload["dry_run"])
        self.assertEqual(check_in_payload["plan"]["request"]["path"], "/events/v2/rsvps/rsvp-1/check-in")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.HttpClient")
    def test_update_and_bulk_update_require_revisions(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        update_buf = io.StringIO()
        with redirect_stdout(update_buf):
            rc_update = events_rsvps_v2.cmd_events_rsvps_v2_update(SimpleNamespace(rsvp_id="rsvp-1", rsvp_json='{"rsvp":{"status":"YES"}}'), self._ctx())
        update_payload = json.loads(update_buf.getvalue())

        bulk_buf = io.StringIO()
        with redirect_stdout(bulk_buf):
            rc_bulk = events_rsvps_v2.cmd_events_rsvps_v2_bulk_update(SimpleNamespace(rsvps_json='{"rsvps":[{"rsvp":{"id":"rsvp-1"}}]}'), self._ctx())
        bulk_payload = json.loads(bulk_buf.getvalue())

        self.assertEqual(rc_update, 1)
        self.assertIn("rsvp.revision", update_payload["error"])
        self.assertEqual(rc_bulk, 1)
        self.assertIn("revision", bulk_payload["error"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.HttpClient")
    def test_check_in_and_cancel_check_in_enforce_guest_id_limit(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        request_json = json.dumps({"guestIds": list(range(1, 13))})

        check_in_buf = io.StringIO()
        with redirect_stdout(check_in_buf):
            rc_check_in = events_rsvps_v2.cmd_events_rsvps_v2_check_in(
                SimpleNamespace(rsvp_id="rsvp-1", request_json=request_json),
                self._ctx(),
            )
        check_in_payload = json.loads(check_in_buf.getvalue())

        cancel_buf = io.StringIO()
        with redirect_stdout(cancel_buf):
            rc_cancel = events_rsvps_v2.cmd_events_rsvps_v2_cancel_check_in(
                SimpleNamespace(rsvp_id="rsvp-1", request_json=request_json),
                self._ctx(),
            )
        cancel_payload = json.loads(cancel_buf.getvalue())

        self.assertEqual(rc_check_in, 1)
        self.assertIn("at most 11 guests", check_in_payload["error"])
        self.assertEqual(rc_cancel, 1)
        self.assertIn("at most 11 guests", cancel_payload["error"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_rsvps_v2.HttpClient")
    def test_delete_bulk_delete_and_cancel_check_in_require_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json")

        for label, func, args in [
            ("delete", events_rsvps_v2.cmd_events_rsvps_v2_delete, SimpleNamespace(rsvp_id="rsvp-1")),
            ("bulk-delete", events_rsvps_v2.cmd_events_rsvps_v2_bulk_delete_by_filter, SimpleNamespace(filter_json='{"filter":{"eventId":"event-1"}}')),
            ("cancel-check-in", events_rsvps_v2.cmd_events_rsvps_v2_cancel_check_in, SimpleNamespace(rsvp_id="rsvp-1", request_json="{}")),
        ]:
            with self.subTest(label=label):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, ctx)
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_events_rsvps_v2_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["events-rsvps-v2", "create", "--rsvp-json", "{}"], events_rsvps_v2.cmd_events_rsvps_v2_create, True),
            (["events-rsvps-v2", "get", "--rsvp-id", "rsvp-1"], events_rsvps_v2.cmd_events_rsvps_v2_get, False),
            (["events-rsvps-v2", "update", "--rsvp-id", "rsvp-1", "--rsvp-json", "{}"], events_rsvps_v2.cmd_events_rsvps_v2_update, True),
            (["events-rsvps-v2", "delete", "--rsvp-id", "rsvp-1"], events_rsvps_v2.cmd_events_rsvps_v2_delete, True),
            (["events-rsvps-v2", "query"], events_rsvps_v2.cmd_events_rsvps_v2_query, False),
            (["events-rsvps-v2", "search", "--search-json", "{}"], events_rsvps_v2.cmd_events_rsvps_v2_search, False),
            (["events-rsvps-v2", "bulk-update", "--rsvps-json", "{}"], events_rsvps_v2.cmd_events_rsvps_v2_bulk_update, True),
            (["events-rsvps-v2", "bulk-delete-by-filter", "--filter-json", "{}"], events_rsvps_v2.cmd_events_rsvps_v2_bulk_delete_by_filter, True),
            (["events-rsvps-v2", "check-in", "--rsvp-id", "rsvp-1"], events_rsvps_v2.cmd_events_rsvps_v2_check_in, True),
            (["events-rsvps-v2", "cancel-check-in", "--rsvp-id", "rsvp-1"], events_rsvps_v2.cmd_events_rsvps_v2_cancel_check_in, True),
            (["events-rsvps-v2", "count"], events_rsvps_v2.cmd_events_rsvps_v2_count, False),
            (["events-rsvps-v2", "list-summary", "--event-id", "event-1"], events_rsvps_v2.cmd_events_rsvps_v2_list_summary, False),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
