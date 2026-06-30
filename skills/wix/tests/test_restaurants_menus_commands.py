from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_menus
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsMenusCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-menus",
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

    @patch("wix_safe_agent_cli.commands.restaurants_menus.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_menus.HttpClient")
    def test_read_commands_use_official_rendered_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"menus": []})

        cases = [
            (restaurants_menus.cmd_restaurants_menus_list, SimpleNamespace(params_json='{"onlyVisible":true}'), "GET", "/restaurants/menus-menu/v1/menus"),
            (restaurants_menus.cmd_restaurants_menus_get, SimpleNamespace(menu_id="menu-1"), "GET", "/restaurants/menus-menu/v1/menus/menu-1"),
            (restaurants_menus.cmd_restaurants_menus_query, SimpleNamespace(query_json='{"query":{}}'), "POST", "/restaurants/menus-menu/v1/menus/query"),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-menus")

    @patch("wix_safe_agent_cli.commands.restaurants_menus.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_menus.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_menus.cmd_restaurants_menus_create, SimpleNamespace(menu_json='{"menu":{"name":"Dinner"}}'), "POST", "/restaurants/menus-menu/v1/menus"),
            (
                restaurants_menus.cmd_restaurants_menus_update,
                SimpleNamespace(menu_id="menu-1", menu_json='{"menu":{"revision":"1","name":"Dinner"}}'),
                "PATCH",
                "/restaurants/menus-menu/v1/menus/menu-1",
            ),
            (restaurants_menus.cmd_restaurants_menus_delete, SimpleNamespace(menu_id="menu-1"), "DELETE", "/restaurants/menus-menu/v1/menus/menu-1"),
            (restaurants_menus.cmd_restaurants_menus_bulk_create, SimpleNamespace(menus_json='{"menus":[{"name":"Dinner"}]}'), "POST", "/restaurants/menus-menu/v1/bulk/menus/create"),
            (
                restaurants_menus.cmd_restaurants_menus_bulk_update,
                SimpleNamespace(menus_json='{"menus":[{"menu":{"id":"menu-1","revision":"1"}}]}'),
                "POST",
                "/restaurants/menus-menu/v1/bulk/menus/update",
            ),
            (
                restaurants_menus.cmd_restaurants_menus_duplicate,
                SimpleNamespace(menu_id="menu-1", options_json='{"menuName":"Dinner Copy"}'),
                "POST",
                "/restaurants/menus-menu/v1/menus/menu-1/duplicate",
            ),
            (
                restaurants_menus.cmd_restaurants_menus_update_extended_fields,
                SimpleNamespace(menu_id="menu-1", extended_fields_json='{"namespace":"app","namespaceData":{}}'),
                "POST",
                "/restaurants/menus-menu/v1/menus/menu-1/updateExtendedFields",
            ),
        ]

        for func, args, http_method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.restaurants_menus.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_menus.HttpClient")
    def test_delete_requires_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = restaurants_menus.cmd_restaurants_menus_delete(
                SimpleNamespace(menu_id="menu-1"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.restaurants_menus.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_menus.HttpClient")
    def test_revision_required_for_update_methods(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_menus.cmd_restaurants_menus_update, SimpleNamespace(menu_id="menu-1", menu_json='{"menu":{"name":"Dinner"}}')),
            (restaurants_menus.cmd_restaurants_menus_bulk_update, SimpleNamespace(menus_json='{"menus":[{"menu":{"id":"menu-1"}}]}')),
        ]
        for func, args in cases:
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertIn("revision", payload["error"])

        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_restaurants_menus_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-menus", "list"], restaurants_menus.cmd_restaurants_menus_list, False),
            (["restaurants-menus", "get", "--menu-id", "menu-1"], restaurants_menus.cmd_restaurants_menus_get, False),
            (["restaurants-menus", "query"], restaurants_menus.cmd_restaurants_menus_query, False),
            (["restaurants-menus", "create", "--menu-json", "{}"], restaurants_menus.cmd_restaurants_menus_create, True),
            (["restaurants-menus", "update", "--menu-id", "menu-1", "--menu-json", "{}"], restaurants_menus.cmd_restaurants_menus_update, True),
            (["restaurants-menus", "delete", "--menu-id", "menu-1"], restaurants_menus.cmd_restaurants_menus_delete, True),
            (["restaurants-menus", "bulk-create", "--menus-json", "{}"], restaurants_menus.cmd_restaurants_menus_bulk_create, True),
            (["restaurants-menus", "bulk-update", "--menus-json", "{}"], restaurants_menus.cmd_restaurants_menus_bulk_update, True),
            (["restaurants-menus", "duplicate", "--menu-id", "menu-1"], restaurants_menus.cmd_restaurants_menus_duplicate, True),
            (
                ["restaurants-menus", "update-extended-fields", "--menu-id", "menu-1", "--extended-fields-json", "{}"],
                restaurants_menus.cmd_restaurants_menus_update_extended_fields,
                True,
            ),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
