from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_reservation_time_slots
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsReservationTimeSlotsCommands(unittest.TestCase):
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
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli restaurants-reservation-time-slots",
        }

    @patch("wix_safe_agent_cli.commands.restaurants_reservation_time_slots.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservation_time_slots.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"timeSlots": []})
        body = '{"reservationLocationId":"loc-1","partySize":2,"date":"2026-07-01T18:00:00Z"}'

        cases = [
            (restaurants_reservation_time_slots.cmd_restaurants_reservation_time_slots_check, SimpleNamespace(time_slot_json=body), "/table-reservations/reservations/v1/check-time-slot"),
            (restaurants_reservation_time_slots.cmd_restaurants_reservation_time_slots_get_scheduled, SimpleNamespace(time_slots_json=body), "/table-reservations/reservations/v1/scheduled-time-slots"),
            (restaurants_reservation_time_slots.cmd_restaurants_reservation_time_slots_get, SimpleNamespace(time_slots_json=body), "/table-reservations/reservations/v1/time-slots"),
        ]
        for func, args, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], "POST")
                self.assertEqual(payload["request"]["path"], path)
                self.assertEqual(payload["request"]["body"]["reservationLocationId"], "loc-1")

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-reservation-time-slots")

    @patch("wix_safe_agent_cli.commands.restaurants_reservation_time_slots.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservation_time_slots.HttpClient")
    def test_body_json_is_required(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = restaurants_reservation_time_slots.cmd_restaurants_reservation_time_slots_get(SimpleNamespace(time_slots_json="{}"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("--time-slots-json cannot be empty", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_restaurants_reservation_time_slots_commands_as_reads(self) -> None:
        parser = build_parser()
        body = '{"reservationLocationId":"loc-1","partySize":2,"date":"2026-07-01T18:00:00Z"}'
        cases = [
            (["restaurants-reservation-time-slots", "check", "--time-slot-json", body], restaurants_reservation_time_slots.cmd_restaurants_reservation_time_slots_check),
            (["restaurants-reservation-time-slots", "get-scheduled", "--time-slots-json", body], restaurants_reservation_time_slots.cmd_restaurants_reservation_time_slots_get_scheduled),
            (["restaurants-reservation-time-slots", "get", "--time-slots-json", body], restaurants_reservation_time_slots.cmd_restaurants_reservation_time_slots_get),
        ]
        for argv, func in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertFalse(args.write_capable)
