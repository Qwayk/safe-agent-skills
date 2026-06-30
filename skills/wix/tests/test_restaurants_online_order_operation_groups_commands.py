from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_online_order_operation_groups
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsOnlineOrderOperationGroupsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-online-order-operation-groups",
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operation_groups.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operation_groups.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"operationGroups": []})

        cases = [
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_get,
                SimpleNamespace(operation_group_id="operation-group-1"),
                "GET",
                "/restaurants/v1/operation-groups/operation-group-1",
            ),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_query,
                SimpleNamespace(query_json='{"query":{}}'),
                "POST",
                "/restaurants/v1/operation-groups/query",
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-online-order-operation-groups")

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operation_groups.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operation_groups.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_create,
                SimpleNamespace(operation_group_json='{"operationGroup":{"name":"Delivery"}}'),
                "POST",
                "/restaurants/v1/operation-groups",
            ),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_update,
                SimpleNamespace(operation_group_id="operation-group-1", operation_group_json='{"operationGroup":{"revision":"1","name":"Delivery"}}'),
                "PATCH",
                "/restaurants/v1/operation-groups/operation-group-1",
            ),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_delete,
                SimpleNamespace(operation_group_id="operation-group-1"),
                "DELETE",
                "/restaurants/v1/operation-groups/operation-group-1",
            ),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_create,
                SimpleNamespace(operation_groups_json='{"operationGroups":[{"name":"Delivery"}]}'),
                "POST",
                "/restaurants/v1/bulk/operation-groups/create",
            ),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_delete,
                SimpleNamespace(operation_groups_json='{"ids":["operation-group-1"]}'),
                "POST",
                "/restaurants/v1/bulk/operation-groups/delete",
            ),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_update,
                SimpleNamespace(operation_groups_json='{"operationGroups":[{"id":"operation-group-1","revision":"1"}]}'),
                "POST",
                "/restaurants/v1/bulk/operation-groups/update",
            ),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_update_tags,
                SimpleNamespace(tags_json='{"ids":["operation-group-1"],"assign":["busy"]}'),
                "POST",
                "/restaurants/v1/bulk/operation-groups/update-tags",
            ),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_update_tags_by_filter,
                SimpleNamespace(filter_json='{"filter":{"name":"Delivery"},"assign":["busy"]}'),
                "POST",
                "/restaurants/v1/bulk/operation-groups/update-tags-by-filter",
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operation_groups.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operation_groups.HttpClient")
    def test_irreversible_commands_require_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_delete, SimpleNamespace(operation_group_id="operation-group-1")),
            (restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_delete, SimpleNamespace(operation_groups_json='{"ids":["operation-group-1"]}')),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_update_tags_by_filter,
                SimpleNamespace(filter_json='{"filter":{"name":"Delivery"},"assign":["busy"]}'),
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operation_groups.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operation_groups.HttpClient")
    def test_revisions_and_tag_selectors_are_required(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_update,
                SimpleNamespace(operation_group_id="operation-group-1", operation_group_json='{"operationGroup":{"name":"Delivery"}}'),
                "revision",
            ),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_update,
                SimpleNamespace(operation_groups_json='{"operationGroups":[{"id":"operation-group-1"}]}'),
                "revision",
            ),
            (
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_update_tags,
                SimpleNamespace(tags_json='{"assign":["busy"]}'),
                "ids",
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

    def test_parser_exposes_all_restaurants_online_order_operation_groups_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-online-order-operation-groups", "get", "--operation-group-id", "operation-group-1"], restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_get, False),
            (["restaurants-online-order-operation-groups", "query"], restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_query, False),
            (["restaurants-online-order-operation-groups", "create", "--operation-group-json", "{}"], restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_create, True),
            (
                ["restaurants-online-order-operation-groups", "update", "--operation-group-id", "operation-group-1", "--operation-group-json", "{}"],
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_update,
                True,
            ),
            (["restaurants-online-order-operation-groups", "delete", "--operation-group-id", "operation-group-1"], restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_delete, True),
            (["restaurants-online-order-operation-groups", "bulk-create", "--operation-groups-json", "{}"], restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_create, True),
            (["restaurants-online-order-operation-groups", "bulk-delete", "--operation-groups-json", "{}"], restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_delete, True),
            (["restaurants-online-order-operation-groups", "bulk-update", "--operation-groups-json", "{}"], restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_update, True),
            (["restaurants-online-order-operation-groups", "bulk-update-tags", "--tags-json", "{}"], restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_update_tags, True),
            (
                ["restaurants-online-order-operation-groups", "bulk-update-tags-by-filter", "--filter-json", "{}"],
                restaurants_online_order_operation_groups.cmd_restaurants_online_order_operation_groups_bulk_update_tags_by_filter,
                True,
            ),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
