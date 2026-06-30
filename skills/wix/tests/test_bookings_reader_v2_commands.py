from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_reader_v2
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBookingsReaderV2Parser(unittest.TestCase):
    def test_parser_recognizes_bookings_reader_v2_commands(self) -> None:
        parser = build_parser()

        query_args = parser.parse_args(
            [
                "bookings-reader-v2",
                "query-extended-bookings",
                "--query-json",
                '{"filter":{"id":{"$eq":"booking-1"}}}',
            ]
        )
        self.assertEqual(query_args.bookings_reader_v2_cmd, "query-extended-bookings")
        self.assertFalse(query_args.write_capable)
        self.assertIs(
            query_args.func,
            bookings_reader_v2.cmd_bookings_reader_v2_query_extended_bookings,
        )

        count_args = parser.parse_args(["bookings-reader-v2", "count-extended-bookings"])
        self.assertEqual(count_args.bookings_reader_v2_cmd, "count-extended-bookings")
        self.assertFalse(count_args.write_capable)
        self.assertIs(
            count_args.func,
            bookings_reader_v2.cmd_bookings_reader_v2_count_extended_bookings,
        )


class TestBookingsReaderV2Commands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token=None,
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    @patch("wix_safe_agent_cli.commands.bookings_reader_v2.HttpClient")
    def test_query_extended_bookings_rejects_missing_empty_and_non_object_json(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        ctx = self._ctx()

        missing_args = SimpleNamespace(query_extended_bookings_json=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_missing = bookings_reader_v2.cmd_bookings_reader_v2_query_extended_bookings(missing_args, ctx)
        missing_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_missing, 1)
        self.assertFalse(missing_payload["ok"])
        self.assertIn("Missing --query-json", missing_payload["error"])

        empty_args = SimpleNamespace(query_extended_bookings_json="{}")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_empty = bookings_reader_v2.cmd_bookings_reader_v2_query_extended_bookings(empty_args, ctx)
        empty_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_empty, 1)
        self.assertFalse(empty_payload["ok"])
        self.assertIn("cannot be empty", empty_payload["error"])

        array_args = SimpleNamespace(query_extended_bookings_json="[]")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_array = bookings_reader_v2.cmd_bookings_reader_v2_query_extended_bookings(array_args, ctx)
        array_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_array, 1)
        self.assertFalse(array_payload["ok"])
        self.assertIn("must be a JSON object", array_payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.bookings_reader_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_reader_v2.resolve_auth_mode")
    def test_query_extended_bookings_builds_expected_request_and_records_auth_mode(
        self,
        mock_auth: unittest.mock.MagicMock,
        mock_client: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"mode": "app_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"extendedBookings": []})
        args = SimpleNamespace(
            query_extended_bookings_json='{"filter":{"id":{"$eq":"booking-1"}},"cursorPaging":{"limit":10}}'
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_reader_v2.cmd_bookings_reader_v2_query_extended_bookings(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "bookings-reader-v2.query-extended-bookings")
        self.assertEqual(payload["auth_mode"], "app_token")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/bookings-reader/v2/extended-bookings/query")
        self.assertEqual(
            payload["request"]["body"],
            {"filter": {"id": {"$eq": "booking-1"}}, "cursorPaging": {"limit": 10}},
        )
        self.assertEqual(payload["response"], {"extendedBookings": []})
        mock_auth.assert_called_once()
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "bookings-reader-v2")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/bookings-reader/v2/extended-bookings/query"))
        self.assertEqual(call.kwargs["json_body"], payload["request"]["body"])
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertEqual(call.kwargs["headers"]["Content-Type"], "application/json")

    @patch("wix_safe_agent_cli.commands.bookings_reader_v2.HttpClient")
    def test_count_extended_bookings_rejects_non_object_json(self, mock_client: unittest.mock.MagicMock) -> None:
        ctx = self._ctx()

        array_args = SimpleNamespace(filter_json="[]")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_array = bookings_reader_v2.cmd_bookings_reader_v2_count_extended_bookings(array_args, ctx)
        array_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_array, 1)
        self.assertFalse(array_payload["ok"])
        self.assertIn("must be a JSON object", array_payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.bookings_reader_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_reader_v2.resolve_auth_mode")
    def test_count_extended_bookings_uses_empty_filter_when_omitted_and_records_auth_mode(
        self,
        mock_auth: unittest.mock.MagicMock,
        mock_client: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"mode": "app_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"count": 0})
        args = SimpleNamespace(filter_json=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_reader_v2.cmd_bookings_reader_v2_count_extended_bookings(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "bookings-reader-v2.count-extended-bookings")
        self.assertEqual(payload["auth_mode"], "app_token")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/bookings-reader/v2/extended-bookings/count")
        self.assertEqual(payload["request"]["body"], {"filter": {}})
        self.assertEqual(payload["response"], {"count": 0})
        mock_auth.assert_called_once()
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "bookings-reader-v2")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/bookings-reader/v2/extended-bookings/count"))
        self.assertEqual(call.kwargs["json_body"], payload["request"]["body"])
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertEqual(call.kwargs["headers"]["Content-Type"], "application/json")
