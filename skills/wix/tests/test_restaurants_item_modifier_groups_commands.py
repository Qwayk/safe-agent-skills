from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_item_modifier_groups
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsItemModifierGroupsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-item-modifier-groups",
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

    @patch("wix_safe_agent_cli.commands.restaurants_item_modifier_groups.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_modifier_groups.HttpClient")
    def test_read_commands_use_official_rendered_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"modifierGroups": []})

        cases = [
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_list,
                SimpleNamespace(params_json='{"paging":{"limit":50}}'),
                "GET",
                "/restaurants/item-modifier-group/v1/modifier-groups",
            ),
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_get,
                SimpleNamespace(modifier_group_id="modifier-group-1"),
                "GET",
                "/restaurants/item-modifier-group/v1/modifier-groups/modifier-group-1",
            ),
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_query,
                SimpleNamespace(query_json='{"query":{}}'),
                "POST",
                "/restaurants/item-modifier-group/v1/modifier-groups/query",
            ),
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_count,
                SimpleNamespace(filter_json='{"filter":{"name":"Almond milk"}}'),
                "POST",
                "/restaurants/item-modifier-group/v1/modifier-groups/count",
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-item-modifier-groups")

    @patch("wix_safe_agent_cli.commands.restaurants_item_modifier_groups.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_modifier_groups.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_create,
                SimpleNamespace(modifier_group_json='{"modifierGroup":{"name":"Pizza toppings"}}'),
                "POST",
                "/restaurants/item-modifier-group/v1/modifier-groups",
            ),
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_update,
                SimpleNamespace(modifier_group_id="modifier-group-1", modifier_group_json='{"modifierGroup":{"revision":"1","name":"Pizza toppings"}}'),
                "PATCH",
                "/restaurants/item-modifier-group/v1/modifier-groups/modifier-group-1",
            ),
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_delete,
                SimpleNamespace(modifier_group_id="modifier-group-1"),
                "DELETE",
                "/restaurants/item-modifier-group/v1/modifier-groups/modifier-group-1",
            ),
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_bulk_create,
                SimpleNamespace(modifier_groups_json='{"modifierGroups":[{"name":"Pizza toppings"}]}'),
                "POST",
                "/restaurants/item-modifier-group/v1/bulk/modifier-groups/create",
            ),
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_bulk_update,
                SimpleNamespace(modifier_groups_json='{"modifierGroups":[{"id":"modifier-group-1","revision":"1"}]}'),
                "POST",
                "/restaurants/item-modifier-group/v1/bulk/modifiers-groups/update",
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

    @patch("wix_safe_agent_cli.commands.restaurants_item_modifier_groups.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_modifier_groups.HttpClient")
    def test_delete_commands_require_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_delete, SimpleNamespace(modifier_group_id="modifier-group-1")),
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

    @patch("wix_safe_agent_cli.commands.restaurants_item_modifier_groups.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_modifier_groups.HttpClient")
    def test_revision_required_for_update_methods(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_update,
                SimpleNamespace(modifier_group_id="modifier-group-1", modifier_group_json='{"modifierGroup":{"name":"Pizza toppings"}}'),
            ),
            (
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_bulk_update,
                SimpleNamespace(modifier_groups_json='{"modifierGroups":[{"id":"modifier-group-1"}]}'),
            ),
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

    def test_parser_exposes_all_restaurants_item_modifier_groups_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-item-modifier-groups", "list"], restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_list, False),
            (["restaurants-item-modifier-groups", "get", "--modifier-group-id", "modifier-group-1"], restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_get, False),
            (["restaurants-item-modifier-groups", "query"], restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_query, False),
            (["restaurants-item-modifier-groups", "count"], restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_count, False),
            (["restaurants-item-modifier-groups", "create", "--modifier-group-json", "{}"], restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_create, True),
            (
                ["restaurants-item-modifier-groups", "update", "--modifier-group-id", "modifier-group-1", "--modifier-group-json", "{}"],
                restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_update,
                True,
            ),
            (["restaurants-item-modifier-groups", "delete", "--modifier-group-id", "modifier-group-1"], restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_delete, True),
            (["restaurants-item-modifier-groups", "bulk-create", "--modifier-groups-json", "{}"], restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_bulk_create, True),
            (["restaurants-item-modifier-groups", "bulk-update", "--modifier-groups-json", "{}"], restaurants_item_modifier_groups.cmd_restaurants_item_modifier_groups_bulk_update, True),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
