from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_reservations
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsReservationsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-reservations",
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

    @patch("wix_safe_agent_cli.commands.restaurants_reservations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservations.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"reservations": []})

        cases = [
            (restaurants_reservations.cmd_restaurants_reservations_get, SimpleNamespace(reservation_id="res-1", params_json='{"fieldsets":["FULL"]}'), "GET", "/table-reservations/reservations/v1/reservations/res-1"),
            (restaurants_reservations.cmd_restaurants_reservations_query, SimpleNamespace(query_json='{"query":{}}'), "POST", "/table-reservations/reservations/v1/reservations/query"),
            (restaurants_reservations.cmd_restaurants_reservations_list, SimpleNamespace(params_json='{"limit":50}'), "GET", "/table-reservations/reservations/v1/reservations"),
            (restaurants_reservations.cmd_restaurants_reservations_search, SimpleNamespace(search_json='{"search":{"expression":"Ada"}}'), "POST", "/table-reservations/reservations/v1/reservations/search"),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-reservations")

    @patch("wix_safe_agent_cli.commands.restaurants_reservations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservations.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_reservations.cmd_restaurants_reservations_create, SimpleNamespace(reservation_json='{"reservation":{"reservee":{"firstName":"Ada","phone":"+15555550123"}}}'), "POST", "/table-reservations/reservations/v1/reservations"),
            (restaurants_reservations.cmd_restaurants_reservations_update, SimpleNamespace(reservation_id="res-1", reservation_json='{"reservation":{"revision":"1"}}'), "PATCH", "/table-reservations/reservations/v1/reservations/res-1"),
            (restaurants_reservations.cmd_restaurants_reservations_delete, SimpleNamespace(reservation_id="res-1"), "DELETE", "/table-reservations/reservations/v1/reservations/res-1"),
            (restaurants_reservations.cmd_restaurants_reservations_bulk_archive, SimpleNamespace(reservations_json='{"reservationIds":["res-1"]}'), "POST", "/table-reservations/reservations/v1/bulk/reservations/archive"),
            (restaurants_reservations.cmd_restaurants_reservations_bulk_unarchive, SimpleNamespace(reservations_json='{"reservationIds":["res-1"]}'), "POST", "/table-reservations/reservations/v1/bulk/reservations/unarchive"),
            (restaurants_reservations.cmd_restaurants_reservations_cancel, SimpleNamespace(reservation_id="res-1", request_json="{}"), "POST", "/table-reservations/reservations/v1/reservations/res-1/cancel"),
            (restaurants_reservations.cmd_restaurants_reservations_create_held, SimpleNamespace(reservation_json='{"reservation":{"details":{"partySize":2}}}'), "POST", "/table-reservations/reservations/v1/reservations/hold"),
            (restaurants_reservations.cmd_restaurants_reservations_reserve, SimpleNamespace(reservation_id="res-1", request_json="{}"), "POST", "/table-reservations/reservations/v1/reservations/res-1/reserve"),
        ]
        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.restaurants_reservations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservations.HttpClient")
    def test_irreversible_commands_require_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_reservations.cmd_restaurants_reservations_delete, SimpleNamespace(reservation_id="res-1")),
            (restaurants_reservations.cmd_restaurants_reservations_cancel, SimpleNamespace(reservation_id="res-1", request_json="{}")),
        ]
        for func, args in cases:
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"))
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.restaurants_reservations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservations.HttpClient")
    def test_update_requires_current_revision(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = restaurants_reservations.cmd_restaurants_reservations_update(
                SimpleNamespace(reservation_id="res-1", reservation_json='{"reservation":{"status":"RESERVED"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("reservation.revision", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_restaurants_reservations_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-reservations", "create", "--reservation-json", "{}"], restaurants_reservations.cmd_restaurants_reservations_create, True),
            (["restaurants-reservations", "get", "--reservation-id", "res-1"], restaurants_reservations.cmd_restaurants_reservations_get, False),
            (["restaurants-reservations", "update", "--reservation-id", "res-1", "--reservation-json", "{}"], restaurants_reservations.cmd_restaurants_reservations_update, True),
            (["restaurants-reservations", "delete", "--reservation-id", "res-1"], restaurants_reservations.cmd_restaurants_reservations_delete, True),
            (["restaurants-reservations", "query"], restaurants_reservations.cmd_restaurants_reservations_query, False),
            (["restaurants-reservations", "list"], restaurants_reservations.cmd_restaurants_reservations_list, False),
            (["restaurants-reservations", "search"], restaurants_reservations.cmd_restaurants_reservations_search, False),
            (["restaurants-reservations", "bulk-archive", "--reservations-json", "{}"], restaurants_reservations.cmd_restaurants_reservations_bulk_archive, True),
            (["restaurants-reservations", "bulk-unarchive", "--reservations-json", "{}"], restaurants_reservations.cmd_restaurants_reservations_bulk_unarchive, True),
            (["restaurants-reservations", "cancel", "--reservation-id", "res-1"], restaurants_reservations.cmd_restaurants_reservations_cancel, True),
            (["restaurants-reservations", "create-held", "--reservation-json", "{}"], restaurants_reservations.cmd_restaurants_reservations_create_held, True),
            (["restaurants-reservations", "reserve", "--reservation-id", "res-1"], restaurants_reservations.cmd_restaurants_reservations_reserve, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
