from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_reservation_experiences
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsReservationExperiencesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-reservation-experiences",
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

    @patch("wix_safe_agent_cli.commands.restaurants_reservation_experiences.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservation_experiences.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"experiences": []})

        cases = [
            (restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_get, SimpleNamespace(experience_id="exp-1", params_json="{}"), "GET", "/table-reservations/experiences/v1/experiences/exp-1"),
            (restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_query, SimpleNamespace(query_json='{"query":{}}'), "POST", "/table-reservations/experiences/v1/experiences/query"),
            (restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_search, SimpleNamespace(search_json='{"search":{"expression":"chef"}}'), "POST", "/table-reservations/experiences/v1/experiences/search"),
            (restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_get_by_slug, SimpleNamespace(slug="chef-table", params_json="{}"), "GET", "/table-reservations/experiences/v1/experiences/slug/chef-table"),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-reservation-experiences")

    @patch("wix_safe_agent_cli.commands.restaurants_reservation_experiences.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservation_experiences.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_create, SimpleNamespace(experience_json='{"experience":{"reservationLocationId":"loc-1"}}'), "POST", "/table-reservations/experiences/v1/experiences"),
            (restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_update, SimpleNamespace(experience_id="exp-1", experience_json='{"experience":{"revision":"1"}}'), "PATCH", "/table-reservations/experiences/v1/experiences/exp-1"),
            (restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_bulk_update_tags, SimpleNamespace(tags_json='{"ids":["exp-1"],"assignTags":["tag-1"]}'), "POST", "/table-reservations/experiences/v1/bulk/experiences/update-tags"),
            (restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_bulk_update_tags_by_filter, SimpleNamespace(filter_json='{"filter":{},"assignTags":["tag-1"]}'), "POST", "/table-reservations/experiences/v1/bulk/experiences/update-tags-by-filter"),
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

    @patch("wix_safe_agent_cli.commands.restaurants_reservation_experiences.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservation_experiences.HttpClient")
    def test_update_requires_current_revision(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_update(
                SimpleNamespace(experience_id="exp-1", experience_json='{"experience":{"reservationLocationId":"loc-1"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("experience.revision", payload["error"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.restaurants_reservation_experiences.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_reservation_experiences.HttpClient")
    def test_bulk_update_tags_by_filter_apply_requires_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_bulk_update_tags_by_filter(
                SimpleNamespace(filter_json='{"filter":{},"assignTags":["tag-1"]}'),
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_restaurants_reservation_experiences_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-reservation-experiences", "create", "--experience-json", "{}"], restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_create, True),
            (["restaurants-reservation-experiences", "get", "--experience-id", "exp-1"], restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_get, False),
            (["restaurants-reservation-experiences", "update", "--experience-id", "exp-1", "--experience-json", "{}"], restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_update, True),
            (["restaurants-reservation-experiences", "query"], restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_query, False),
            (["restaurants-reservation-experiences", "search"], restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_search, False),
            (["restaurants-reservation-experiences", "bulk-update-tags", "--tags-json", "{}"], restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_bulk_update_tags, True),
            (["restaurants-reservation-experiences", "bulk-update-tags-by-filter", "--filter-json", "{}"], restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_bulk_update_tags_by_filter, True),
            (["restaurants-reservation-experiences", "get-by-slug", "--slug", "chef-table"], restaurants_reservation_experiences.cmd_restaurants_reservation_experiences_get_by_slug, False),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
