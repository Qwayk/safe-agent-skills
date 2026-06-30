from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_online_order_menu_ordering_settings
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsOnlineOrderMenuOrderingSettingsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-online-order-menu-ordering-settings",
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_menu_ordering_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_menu_ordering_settings.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"menuOrderingSettings": []})

        cases = [
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_get,
                SimpleNamespace(menu_ordering_settings_id="mos-1"),
                "GET",
                "/menu-ordering-settings/v1/menu-ordering-settings/mos-1",
            ),
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_query,
                SimpleNamespace(query_json='{"query":{}}'),
                "POST",
                "/menu-ordering-settings/v1/menu-ordering-settings/query",
            ),
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_list_menus_availability_status,
                SimpleNamespace(),
                "GET",
                "/menu-ordering-settings/v1/menu-ordering-settings/menus-availability-status",
            ),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-online-order-menu-ordering-settings")

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_menu_ordering_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_menu_ordering_settings.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_update,
                SimpleNamespace(menu_ordering_settings_id="mos-1", menu_ordering_settings_json='{"menuOrderingSettings":{"revision":"1"}}'),
                "PATCH",
                "/menu-ordering-settings/v1/menu-ordering-settings/mos-1",
            ),
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_bulk_update,
                SimpleNamespace(menu_ordering_settings_json='{"menuOrderingSettings":[{"id":"mos-1","revision":"1"}]}'),
                "POST",
                "/menu-ordering-settings/v1/bulk/menu-ordering-settings/update",
            ),
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_bulk_update_tags,
                SimpleNamespace(tags_json='{"ids":["mos-1"],"assignTags":["featured"]}'),
                "POST",
                "/menu-ordering-settings/v1/bulk/menu-ordering-settings/update-tags",
            ),
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_bulk_update_tags_by_filter,
                SimpleNamespace(filter_json='{"filter":{"name":"Lunch"},"assignTags":["featured"]}'),
                "POST",
                "/menu-ordering-settings/v1/bulk/menu-ordering-settings/update-tags-by-filter",
            ),
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_update_extended_fields,
                SimpleNamespace(menu_ordering_settings_id="mos-1", extended_fields_json='{"extendedFields":{"pickupOnly":true}}'),
                "POST",
                "/menu-ordering-settings/v1/menu-ordering-settings/mos-1/update-extended-fields",
            ),
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_upsert_by_menu_id,
                SimpleNamespace(menu_id="menu-1", upsert_json='{"menuOrderingSettings":{"menuId":"menu-1"}}'),
                "POST",
                "/menu-ordering-settings/v1/menu-ordering-settings/upsert/menu-id/menu-1",
            ),
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_menu_ordering_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_menu_ordering_settings.HttpClient")
    def test_irreversible_commands_require_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_bulk_update_tags_by_filter,
                SimpleNamespace(filter_json='{"filter":{"name":"Lunch"},"assignTags":["featured"]}'),
            ),
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_menu_ordering_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_menu_ordering_settings.HttpClient")
    def test_revision_and_tag_selectors_are_required(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_update,
                SimpleNamespace(menu_ordering_settings_id="mos-1", menu_ordering_settings_json='{"menuOrderingSettings":{"status":"enabled"}}'),
                "revision",
            ),
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_bulk_update,
                SimpleNamespace(menu_ordering_settings_json='{"menuOrderingSettings":[{"id":"mos-1"}]}'),
                "revision",
            ),
            (
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_bulk_update_tags,
                SimpleNamespace(tags_json='{"assignTags":["featured"]}'),
                "ids or menuOrderingSettingsIds",
            ),
        ]
        for func, args, error_text in cases:
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertIn(error_text, payload["error"])

        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_restaurants_online_order_menu_ordering_settings_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (
                ["restaurants-online-order-menu-ordering-settings", "get", "--menu-ordering-settings-id", "mos-1"],
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_get,
                False,
            ),
            (["restaurants-online-order-menu-ordering-settings", "query"], restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_query, False),
            (
                ["restaurants-online-order-menu-ordering-settings", "list-menus-availability-status"],
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_list_menus_availability_status,
                False,
            ),
            (
                ["restaurants-online-order-menu-ordering-settings", "update", "--menu-ordering-settings-id", "mos-1", "--menu-ordering-settings-json", "{}"],
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_update,
                True,
            ),
            (
                ["restaurants-online-order-menu-ordering-settings", "bulk-update", "--menu-ordering-settings-json", "{}"],
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_bulk_update,
                True,
            ),
            (
                ["restaurants-online-order-menu-ordering-settings", "bulk-update-tags", "--tags-json", "{}"],
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_bulk_update_tags,
                True,
            ),
            (
                ["restaurants-online-order-menu-ordering-settings", "bulk-update-tags-by-filter", "--filter-json", "{}"],
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_bulk_update_tags_by_filter,
                True,
            ),
            (
                [
                    "restaurants-online-order-menu-ordering-settings",
                    "update-extended-fields",
                    "--menu-ordering-settings-id",
                    "mos-1",
                    "--extended-fields-json",
                    "{}",
                ],
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_update_extended_fields,
                True,
            ),
            (
                ["restaurants-online-order-menu-ordering-settings", "upsert-by-menu-id", "--menu-id", "menu-1", "--upsert-json", "{}"],
                restaurants_online_order_menu_ordering_settings.cmd_restaurants_online_order_menu_ordering_settings_upsert_by_menu_id,
                True,
            ),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
