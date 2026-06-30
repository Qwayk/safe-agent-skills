from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_time_slots_v2
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


class TestBookingsTimeSlotsV2Parser(unittest.TestCase):
    def test_parser_recognizes_bookings_time_slots_v2_commands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(
            [
                "bookings-time-slots-v2",
                "list-availability",
                "--list-availability-json",
                '{"serviceId":"service-1","fromLocalDate":"2026-06-24","toLocalDate":"2026-06-25","timeZone":"UTC"}',
            ]
        )
        self.assertEqual(list_args.bookings_time_slots_v2_cmd, "list-availability")
        self.assertFalse(list_args.write_capable)
        self.assertIs(list_args.func, bookings_time_slots_v2.cmd_bookings_time_slots_v2_list_availability)

        get_args = parser.parse_args(
            [
                "bookings-time-slots-v2",
                "get-availability",
                "--get-availability-json",
                '{"serviceId":"service-1","localStartDate":"2026-06-24T10:00:00Z","timeZone":"UTC"}',
            ]
        )
        self.assertEqual(get_args.bookings_time_slots_v2_cmd, "get-availability")
        self.assertFalse(get_args.write_capable)
        self.assertIs(get_args.func, bookings_time_slots_v2.cmd_bookings_time_slots_v2_get_availability)

        list_event_args = parser.parse_args(
            [
                "bookings-time-slots-v2",
                "list-event",
                "--list-event-json",
                '{"eventId":"event-1","fromLocalDate":"2026-06-24","toLocalDate":"2026-06-25"}',
            ]
        )
        self.assertEqual(list_event_args.bookings_time_slots_v2_cmd, "list-event")
        self.assertFalse(list_event_args.write_capable)
        self.assertIs(list_event_args.func, bookings_time_slots_v2.cmd_bookings_time_slots_v2_list_event)

        get_event_args = parser.parse_args(["bookings-time-slots-v2", "get-event", "--event-id", "event-1"])
        self.assertEqual(get_event_args.bookings_time_slots_v2_cmd, "get-event")
        self.assertFalse(get_event_args.write_capable)
        self.assertIs(get_event_args.func, bookings_time_slots_v2.cmd_bookings_time_slots_v2_get_event)

        list_multi_args = parser.parse_args(
            [
                "bookings-time-slots-v2",
                "list-multi-service",
                "--list-multi-service-json",
                '{"services":[{"serviceId":"service-1"},{"serviceId":"service-2"}],"fromLocalDate":"2026-06-24","toLocalDate":"2026-06-25","location":{"locationId":"loc-1"},"timeZone":"UTC"}',
            ]
        )
        self.assertEqual(list_multi_args.bookings_time_slots_v2_cmd, "list-multi-service")
        self.assertFalse(list_multi_args.write_capable)
        self.assertIs(list_multi_args.func, bookings_time_slots_v2.cmd_bookings_time_slots_v2_list_multi_service)

        get_multi_args = parser.parse_args(
            [
                "bookings-time-slots-v2",
                "get-multi-service",
                "--get-multi-service-json",
                '{"timeSlot":{"services":[{"serviceId":"service-1"}],"localStartDate":"2026-06-24T10:00:00Z"}}',
            ]
        )
        self.assertEqual(get_multi_args.bookings_time_slots_v2_cmd, "get-multi-service")
        self.assertFalse(get_multi_args.write_capable)
        self.assertIs(get_multi_args.func, bookings_time_slots_v2.cmd_bookings_time_slots_v2_get_multi_service)


class TestBookingsTimeSlotsV2Commands(unittest.TestCase):
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

    @patch("wix_safe_agent_cli.commands.bookings_time_slots_v2.HttpClient")
    def test_list_availability_rejects_missing_empty_and_non_object_json(self, mock_client: unittest.mock.MagicMock) -> None:
        ctx = self._ctx()

        missing_args = SimpleNamespace(list_availability_json=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_missing = bookings_time_slots_v2.cmd_bookings_time_slots_v2_list_availability(missing_args, ctx)
        missing_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_missing, 1)
        self.assertFalse(missing_payload["ok"])
        self.assertIn("Missing --list-availability-json", missing_payload["error"])

        empty_args = SimpleNamespace(list_availability_json="{}")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_empty = bookings_time_slots_v2.cmd_bookings_time_slots_v2_list_availability(empty_args, ctx)
        empty_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_empty, 1)
        self.assertFalse(empty_payload["ok"])
        self.assertIn("cannot be empty", empty_payload["error"])

        array_args = SimpleNamespace(list_availability_json="[]")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_array = bookings_time_slots_v2.cmd_bookings_time_slots_v2_list_availability(array_args, ctx)
        array_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_array, 1)
        self.assertFalse(array_payload["ok"])
        self.assertIn("must be a JSON object", array_payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.bookings_time_slots_v2.HttpClient")
    def test_list_availability_builds_expected_request_and_records_auth_mode(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"timeSlots": []})
        args = SimpleNamespace(
            list_availability_json='{"serviceId":"service-1","fromLocalDate":"2026-06-24","toLocalDate":"2026-06-25","timeZone":"UTC"}'
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_time_slots_v2.cmd_bookings_time_slots_v2_list_availability(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "bookings-time-slots-v2.list-availability")
        self.assertEqual(payload["auth_mode"], "app_token")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/service-availability/v2/time-slots")
        self.assertEqual(
            payload["request"]["body"],
            {
                "serviceId": "service-1",
                "fromLocalDate": "2026-06-24",
                "toLocalDate": "2026-06-25",
                "timeZone": "UTC",
            },
        )
        self.assertEqual(payload["response"], {"timeSlots": []})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/service-availability/v2/time-slots"))
        self.assertEqual(call.kwargs["json_body"], payload["request"]["body"])
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertEqual(call.kwargs["headers"]["Content-Type"], "application/json")

    @patch("wix_safe_agent_cli.commands.bookings_time_slots_v2.HttpClient")
    def test_list_event_builds_expected_request_and_records_auth_mode(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"timeSlots": []})
        args = SimpleNamespace(list_event_json='{"eventId":"event-1","fromLocalDate":"2026-06-24"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_time_slots_v2.cmd_bookings_time_slots_v2_list_event(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "bookings-time-slots-v2.list-event")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/service-availability/v2/time-slots/event")
        self.assertEqual(payload["request"]["body"], {"eventId": "event-1", "fromLocalDate": "2026-06-24"})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/service-availability/v2/time-slots/event"))
        self.assertEqual(call.kwargs["json_body"], payload["request"]["body"])

    @patch("wix_safe_agent_cli.commands.bookings_time_slots_v2.HttpClient")
    def test_get_event_builds_expected_request_and_records_auth_mode(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"timeSlot": {"id": "event-1"}})
        args = SimpleNamespace(event_id="event-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_time_slots_v2.cmd_bookings_time_slots_v2_get_event(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "bookings-time-slots-v2.get-event")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/_api/service-availability/v2/time-slots/event/event-1")
        self.assertEqual(payload["request"]["event_id"], "event-1")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/service-availability/v2/time-slots/event/event-1"))
        self.assertIsNone(call.kwargs["json_body"])

    @patch("wix_safe_agent_cli.commands.bookings_time_slots_v2.HttpClient")
    def test_get_event_rejects_missing_event_id(self, mock_client: unittest.mock.MagicMock) -> None:
        ctx = self._ctx()
        args = SimpleNamespace(event_id="")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_time_slots_v2.cmd_bookings_time_slots_v2_get_event(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("Missing --event-id", payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.bookings_time_slots_v2.HttpClient")
    def test_list_multi_service_builds_expected_request_and_records_auth_mode(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"timeSlots": []})
        args = SimpleNamespace(list_multi_service_json='{"services":[{"serviceId":"service-1"}],"timeZone":"UTC"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_time_slots_v2.cmd_bookings_time_slots_v2_list_multi_service(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "bookings-time-slots-v2.list-multi-service")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/service-availability/v2/multi-service-time-slots")
        self.assertEqual(payload["request"]["body"], {"services": [{"serviceId": "service-1"}], "timeZone": "UTC"})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/service-availability/v2/multi-service-time-slots"))

    @patch("wix_safe_agent_cli.commands.bookings_time_slots_v2.HttpClient")
    def test_get_multi_service_builds_expected_request_and_records_auth_mode(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"timeSlot": {"id": "slot-1"}})
        args = SimpleNamespace(get_multi_service_json='{"timeSlot":{"id":"slot-1"}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_time_slots_v2.cmd_bookings_time_slots_v2_get_multi_service(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "bookings-time-slots-v2.get-multi-service")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/service-availability/v2/multi-service-time-slots/get")
        self.assertEqual(payload["request"]["body"], {"timeSlot": {"id": "slot-1"}})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/service-availability/v2/multi-service-time-slots/get"))

    @patch("wix_safe_agent_cli.commands.bookings_time_slots_v2.HttpClient")
    def test_get_availability_rejects_missing_empty_and_non_object_json(self, mock_client: unittest.mock.MagicMock) -> None:
        ctx = self._ctx()

        missing_args = SimpleNamespace(get_availability_json=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_missing = bookings_time_slots_v2.cmd_bookings_time_slots_v2_get_availability(missing_args, ctx)
        missing_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_missing, 1)
        self.assertFalse(missing_payload["ok"])
        self.assertIn("Missing --get-availability-json", missing_payload["error"])

        empty_args = SimpleNamespace(get_availability_json="{}")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_empty = bookings_time_slots_v2.cmd_bookings_time_slots_v2_get_availability(empty_args, ctx)
        empty_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_empty, 1)
        self.assertFalse(empty_payload["ok"])
        self.assertIn("cannot be empty", empty_payload["error"])

        array_args = SimpleNamespace(get_availability_json="[]")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_array = bookings_time_slots_v2.cmd_bookings_time_slots_v2_get_availability(array_args, ctx)
        array_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_array, 1)
        self.assertFalse(array_payload["ok"])
        self.assertIn("must be a JSON object", array_payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.bookings_time_slots_v2.HttpClient")
    def test_get_availability_builds_expected_request_and_records_auth_mode(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"timeSlot": {"id": "slot-1"}})
        args = SimpleNamespace(
            get_availability_json='{"serviceId":"service-1","localStartDate":"2026-06-24T10:00:00Z","timeZone":"UTC"}'
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_time_slots_v2.cmd_bookings_time_slots_v2_get_availability(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "bookings-time-slots-v2.get-availability")
        self.assertEqual(payload["auth_mode"], "app_token")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/service-availability/v2/time-slots/get")
        self.assertEqual(
            payload["request"]["body"],
            {
                "serviceId": "service-1",
                "localStartDate": "2026-06-24T10:00:00Z",
                "timeZone": "UTC",
            },
        )
        self.assertEqual(payload["response"], {"timeSlot": {"id": "slot-1"}})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/service-availability/v2/time-slots/get"))
        self.assertEqual(call.kwargs["json_body"], payload["request"]["body"])
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertEqual(call.kwargs["headers"]["Content-Type"], "application/json")
