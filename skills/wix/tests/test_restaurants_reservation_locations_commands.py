from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_reservation_locations
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsReservationLocationsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-reservation-locations",
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

    @patch("wix_safe_agent_cli.commands.restaurants_reservation_locations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservation_locations.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"reservationLocations": []})

        cases = [
            (restaurants_reservation_locations.cmd_restaurants_reservation_locations_get, SimpleNamespace(reservation_location_id="loc-1", params_json='{"fieldsets":["FULL"]}'), "GET", "/table-reservations/reservation-locations/v1/reservation-locations/loc-1"),
            (restaurants_reservation_locations.cmd_restaurants_reservation_locations_query, SimpleNamespace(query_json='{"query":{}}'), "POST", "/table-reservations/reservation-locations/v1/reservation-locations/query"),
            (restaurants_reservation_locations.cmd_restaurants_reservation_locations_list, SimpleNamespace(params_json='{"limit":50}'), "GET", "/table-reservations/reservation-locations/v1/reservation-locations"),
        ]
        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-reservation-locations")

    @patch("wix_safe_agent_cli.commands.restaurants_reservation_locations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservation_locations.HttpClient")
    def test_update_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = restaurants_reservation_locations.cmd_restaurants_reservation_locations_update(
                SimpleNamespace(reservation_location_id="loc-1", reservation_location_json='{"reservationLocation":{"revision":"1"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "PATCH")
        self.assertEqual(payload["plan"]["request"]["path"], "/table-reservations/reservation-locations/v1/reservation-locations/loc-1")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.restaurants_reservation_locations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservation_locations.HttpClient")
    def test_update_requires_current_revision(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = restaurants_reservation_locations.cmd_restaurants_reservation_locations_update(
                SimpleNamespace(reservation_location_id="loc-1", reservation_location_json='{"reservationLocation":{"name":"Main"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("reservationLocation.revision", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_restaurants_reservation_locations_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-reservation-locations", "get", "--reservation-location-id", "loc-1"], restaurants_reservation_locations.cmd_restaurants_reservation_locations_get, False),
            (["restaurants-reservation-locations", "update", "--reservation-location-id", "loc-1", "--reservation-location-json", "{}"], restaurants_reservation_locations.cmd_restaurants_reservation_locations_update, True),
            (["restaurants-reservation-locations", "query"], restaurants_reservation_locations.cmd_restaurants_reservation_locations_query, False),
            (["restaurants-reservation-locations", "list"], restaurants_reservation_locations.cmd_restaurants_reservation_locations_list, False),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
