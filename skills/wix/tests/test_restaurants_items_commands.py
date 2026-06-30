from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_items
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsItemsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-items",
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

    @patch("wix_safe_agent_cli.commands.restaurants_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_items.HttpClient")
    def test_read_commands_use_official_rendered_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"items": []})

        cases = [
            (restaurants_items.cmd_restaurants_items_list, SimpleNamespace(params_json='{"paging":{"limit":50}}'), "GET", "/restaurants/menus-item/v1/items"),
            (restaurants_items.cmd_restaurants_items_get, SimpleNamespace(item_id="item-1"), "GET", "/restaurants/menus-item/v1/items/item-1"),
            (restaurants_items.cmd_restaurants_items_query, SimpleNamespace(query_json='{"query":{}}'), "POST", "/restaurants/menus-item/v1/items/query"),
            (restaurants_items.cmd_restaurants_items_search, SimpleNamespace(search_json='{"search":{"expression":"salad"}}'), "POST", "/restaurants/menus-item/v1/items/search"),
            (restaurants_items.cmd_restaurants_items_count, SimpleNamespace(filter_json='{"filter":{"visible":true}}'), "POST", "/restaurants/menus-item/v1/items/count"),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-items")

    @patch("wix_safe_agent_cli.commands.restaurants_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_items.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_items.cmd_restaurants_items_create, SimpleNamespace(item_json='{"item":{"name":"Salad"}}'), "POST", "/restaurants/menus-item/v1/items"),
            (
                restaurants_items.cmd_restaurants_items_update,
                SimpleNamespace(item_id="item-1", item_json='{"item":{"revision":"1","name":"Salad"}}'),
                "PATCH",
                "/restaurants/menus-item/v1/items/item-1",
            ),
            (restaurants_items.cmd_restaurants_items_delete, SimpleNamespace(item_id="item-1"), "DELETE", "/restaurants/menus-item/v1/items/item-1"),
            (
                restaurants_items.cmd_restaurants_items_bulk_create,
                SimpleNamespace(items_json='{"items":[{"item":{"name":"Salad"}}]}'),
                "POST",
                "/restaurants/menus-item/v1/bulk/items/create",
            ),
            (
                restaurants_items.cmd_restaurants_items_bulk_delete,
                SimpleNamespace(items_json='{"itemIds":["item-1"]}'),
                "DELETE",
                "/restaurants/menus-item/v1/bulk/items/delete",
            ),
            (
                restaurants_items.cmd_restaurants_items_bulk_update,
                SimpleNamespace(items_json='{"items":[{"item":{"id":"item-1","revision":"1"}}]}'),
                "POST",
                "/restaurants/menus-item/v1/bulk/items/update",
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

    @patch("wix_safe_agent_cli.commands.restaurants_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_items.HttpClient")
    def test_delete_commands_require_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (restaurants_items.cmd_restaurants_items_delete, SimpleNamespace(item_id="item-1")),
            (restaurants_items.cmd_restaurants_items_bulk_delete, SimpleNamespace(items_json='{"itemIds":["item-1"]}')),
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

    @patch("wix_safe_agent_cli.commands.restaurants_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_items.HttpClient")
    def test_revision_required_for_update_methods(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_items.cmd_restaurants_items_update, SimpleNamespace(item_id="item-1", item_json='{"item":{"name":"Salad"}}')),
            (restaurants_items.cmd_restaurants_items_bulk_update, SimpleNamespace(items_json='{"items":[{"item":{"id":"item-1"}}]}')),
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

    def test_parser_exposes_all_restaurants_items_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-items", "list"], restaurants_items.cmd_restaurants_items_list, False),
            (["restaurants-items", "get", "--item-id", "item-1"], restaurants_items.cmd_restaurants_items_get, False),
            (["restaurants-items", "query"], restaurants_items.cmd_restaurants_items_query, False),
            (["restaurants-items", "search"], restaurants_items.cmd_restaurants_items_search, False),
            (["restaurants-items", "count"], restaurants_items.cmd_restaurants_items_count, False),
            (["restaurants-items", "create", "--item-json", "{}"], restaurants_items.cmd_restaurants_items_create, True),
            (["restaurants-items", "update", "--item-id", "item-1", "--item-json", "{}"], restaurants_items.cmd_restaurants_items_update, True),
            (["restaurants-items", "delete", "--item-id", "item-1"], restaurants_items.cmd_restaurants_items_delete, True),
            (["restaurants-items", "bulk-create", "--items-json", "{}"], restaurants_items.cmd_restaurants_items_bulk_create, True),
            (["restaurants-items", "bulk-delete", "--items-json", "{}"], restaurants_items.cmd_restaurants_items_bulk_delete, True),
            (["restaurants-items", "bulk-update", "--items-json", "{}"], restaurants_items.cmd_restaurants_items_bulk_update, True),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
