from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import referral_tracker
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestReferralTrackerCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli referral-tracker",
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

    def test_parser_recognizes_referral_tracker_commands_as_reads(self) -> None:
        parser = build_parser()
        cases = [
            ["referral-tracker", "get", "--referral-event-id", "event-123"],
            ["referral-tracker", "query", "--query-json", '{"query":{"filter":{"createdDate":{"$exists":true}}}}'],
            ["referral-tracker", "get-statistics"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))
                self.assertFalse(args.write_capable)

    @patch("wix_safe_agent_cli.commands.referral_tracker.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referral_tracker.HttpClient")
    def test_get_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referralEvent": {"id": "event-123"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referral_tracker.cmd_referral_tracker_get(SimpleNamespace(referral_event_id="event-123"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "referralTracker.getReferralEvent")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/_api/referral-tracker/v1/referral-events/event-123")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "referral-tracker")

    @patch("wix_safe_agent_cli.commands.referral_tracker.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referral_tracker.HttpClient")
    def test_query_uses_official_path_and_body(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referralEvents": []})
        query_json = '{"query":{"filter":{"createdDate":{"$exists":true}},"sort":[{"fieldName":"createdDate","order":"DESC"}],"cursorPaging":{"limit":10}}}'

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referral_tracker.cmd_referral_tracker_query(SimpleNamespace(query_json=query_json), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "referralTracker.queryReferralEvent")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/referral-tracker/v1/referral-events/query")
        self.assertEqual(payload["request"]["body"]["query"]["filter"]["createdDate"]["$exists"], True)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"]["query"]["cursorPaging"]["limit"], 10)

    @patch("wix_safe_agent_cli.commands.referral_tracker.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referral_tracker.HttpClient")
    def test_get_statistics_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"statistics": {"totalReferralEvents": 2}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referral_tracker.cmd_referral_tracker_get_statistics(SimpleNamespace(), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "referralTracker.getReferralStatistics")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/_api/referral-tracker/v1/referral-statistics")

    @patch("wix_safe_agent_cli.commands.referral_tracker.HttpClient")
    def test_query_requires_query_object(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referral_tracker.cmd_referral_tracker_query(SimpleNamespace(query_json='{"filter":{}}'), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()
