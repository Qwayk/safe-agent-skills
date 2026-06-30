from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_item_modifiers
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsItemModifiersCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-item-modifiers",
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

    @patch("wix_safe_agent_cli.commands.restaurants_item_modifiers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_modifiers.HttpClient")
    def test_read_commands_use_official_rendered_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"modifiers": []})

        cases = [
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_list,
                SimpleNamespace(params_json='{"paging":{"limit":50}}'),
                "GET",
                "/restaurants/item-modifiers/v1/modifiers",
            ),
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_get,
                SimpleNamespace(modifier_id="modifier-1"),
                "GET",
                "/restaurants/item-modifiers/v1/modifiers/modifier-1",
            ),
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_query,
                SimpleNamespace(query_json='{"query":{}}'),
                "POST",
                "/restaurants/item-modifiers/v1/modifiers/query",
            ),
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_count,
                SimpleNamespace(filter_json='{"filter":{"name":"Almond milk"}}'),
                "POST",
                "/restaurants/item-modifiers/v1/modifiers/count",
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-item-modifiers")

    @patch("wix_safe_agent_cli.commands.restaurants_item_modifiers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_modifiers.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_create,
                SimpleNamespace(modifier_json='{"modifier":{"name":"Almond milk"}}'),
                "POST",
                "/restaurants/item-modifiers/v1/modifiers",
            ),
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_update,
                SimpleNamespace(modifier_id="modifier-1", modifier_json='{"modifier":{"revision":"1","name":"Almond milk"}}'),
                "PATCH",
                "/restaurants/item-modifiers/v1/modifiers/modifier-1",
            ),
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_delete,
                SimpleNamespace(modifier_id="modifier-1"),
                "DELETE",
                "/restaurants/item-modifiers/v1/modifiers/modifier-1",
            ),
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_bulk_create,
                SimpleNamespace(modifiers_json='{"modifiers":[{"modifier":{"name":"Almond milk"}}]}'),
                "POST",
                "/restaurants/item-modifiers/v1/bulk/modifiers/create",
            ),
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_bulk_delete,
                SimpleNamespace(modifiers_json='{"modifierIds":["modifier-1"]}'),
                "DELETE",
                "/restaurants/item-modifiers/v1/bulk/modifiers/delete",
            ),
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_bulk_update,
                SimpleNamespace(modifiers_json='{"modifiers":[{"modifier":{"id":"modifier-1","revision":"1"}}]}'),
                "POST",
                "/restaurants/item-modifiers/v1/bulk/modifiers/update",
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

    @patch("wix_safe_agent_cli.commands.restaurants_item_modifiers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_modifiers.HttpClient")
    def test_delete_commands_require_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (restaurants_item_modifiers.cmd_restaurants_item_modifiers_delete, SimpleNamespace(modifier_id="modifier-1")),
            (restaurants_item_modifiers.cmd_restaurants_item_modifiers_bulk_delete, SimpleNamespace(modifiers_json='{"modifierIds":["modifier-1"]}')),
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

    @patch("wix_safe_agent_cli.commands.restaurants_item_modifiers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_modifiers.HttpClient")
    def test_revision_required_for_update_methods(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_update,
                SimpleNamespace(modifier_id="modifier-1", modifier_json='{"modifier":{"name":"Almond milk"}}'),
            ),
            (
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_bulk_update,
                SimpleNamespace(modifiers_json='{"modifiers":[{"modifier":{"id":"modifier-1"}}]}'),
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

    def test_parser_exposes_all_restaurants_item_modifiers_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-item-modifiers", "list"], restaurants_item_modifiers.cmd_restaurants_item_modifiers_list, False),
            (["restaurants-item-modifiers", "get", "--modifier-id", "modifier-1"], restaurants_item_modifiers.cmd_restaurants_item_modifiers_get, False),
            (["restaurants-item-modifiers", "query"], restaurants_item_modifiers.cmd_restaurants_item_modifiers_query, False),
            (["restaurants-item-modifiers", "count"], restaurants_item_modifiers.cmd_restaurants_item_modifiers_count, False),
            (["restaurants-item-modifiers", "create", "--modifier-json", "{}"], restaurants_item_modifiers.cmd_restaurants_item_modifiers_create, True),
            (
                ["restaurants-item-modifiers", "update", "--modifier-id", "modifier-1", "--modifier-json", "{}"],
                restaurants_item_modifiers.cmd_restaurants_item_modifiers_update,
                True,
            ),
            (["restaurants-item-modifiers", "delete", "--modifier-id", "modifier-1"], restaurants_item_modifiers.cmd_restaurants_item_modifiers_delete, True),
            (["restaurants-item-modifiers", "bulk-create", "--modifiers-json", "{}"], restaurants_item_modifiers.cmd_restaurants_item_modifiers_bulk_create, True),
            (["restaurants-item-modifiers", "bulk-delete", "--modifiers-json", "{}"], restaurants_item_modifiers.cmd_restaurants_item_modifiers_bulk_delete, True),
            (["restaurants-item-modifiers", "bulk-update", "--modifiers-json", "{}"], restaurants_item_modifiers.cmd_restaurants_item_modifiers_bulk_update, True),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
