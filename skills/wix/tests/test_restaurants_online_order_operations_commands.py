from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_online_order_operations
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsOnlineOrderOperationsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-online-order-operations",
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operations.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"operations": []})

        cases = [
            (restaurants_online_order_operations.cmd_restaurants_online_order_operations_get, SimpleNamespace(operation_id="operation-1"), "GET", "/restaurants-operations/v1/operations/operation-1"),
            (restaurants_online_order_operations.cmd_restaurants_online_order_operations_list, SimpleNamespace(params_json='{"paging":{"limit":50}}'), "GET", "/restaurants-operations/v1/operations"),
            (restaurants_online_order_operations.cmd_restaurants_online_order_operations_query, SimpleNamespace(query_json='{"query":{}}'), "POST", "/restaurants-operations/v1/operations/query"),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_first_available_time_slot_per_fulfillment_type,
                SimpleNamespace(operation_id="operation-1", params_json='{"date":"2026-06-28"}'),
                "GET",
                "/restaurants-operations/v1/operations/operation-1/first-available-time-slot-per-fulfillment-type",
            ),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_first_available_time_slots_per_menu,
                SimpleNamespace(operation_id="operation-1", params_json='{"date":"2026-06-28"}'),
                "GET",
                "/restaurants-operations/v1/operations/operation-1/first-available-time-slots-per-menus",
            ),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_available_time_slots_for_date,
                SimpleNamespace(operation_id="operation-1", params_json='{"date":"2026-06-28"}'),
                "GET",
                "/restaurants-operations/v1/operations/operation-1/available-time-slots-per-date",
            ),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_available_dates_in_range,
                SimpleNamespace(operation_id="operation-1", params_json='{"from":"2026-06-28"}'),
                "GET",
                "/restaurants-operations/v1/operations/operation-1/available-dates",
            ),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_validate_address,
                SimpleNamespace(operation_id="operation-1", params_json='{"address":{"country":"US"}}'),
                "GET",
                "/restaurants-operations/v1/operations/operation-1/validate-address",
            ),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_first_available_time_slots_per_operation,
                SimpleNamespace(operations_json='{"operationIds":["operation-1"]}'),
                "POST",
                "/restaurants-operations/v1/operations/first-available-time-slots-per-operations",
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-online-order-operations")

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operations.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_update,
                SimpleNamespace(operation_id="operation-1", operation_json='{"operation":{"revision":"1","enabled":true}}'),
                "PATCH",
                "/restaurants-operations/v1/operations/operation-1",
            ),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_delete,
                SimpleNamespace(operation_id="operation-1"),
                "DELETE",
                "/restaurants-operations/v1/operations/operation-1",
            ),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_bulk_update_tags,
                SimpleNamespace(tags_json='{"operationIds":["operation-1"],"assignTags":["busy"]}'),
                "POST",
                "/restaurants-operations/v1/bulk/operations/update-tags",
            ),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_bulk_update_tags_by_filter,
                SimpleNamespace(filter_json='{"filter":{"name":"Delivery"},"assignTags":["busy"]}'),
                "POST",
                "/restaurants-operations/v1/bulk/operations/update-tags-by-filter",
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operations.HttpClient")
    def test_irreversible_commands_require_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (restaurants_online_order_operations.cmd_restaurants_online_order_operations_delete, SimpleNamespace(operation_id="operation-1")),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_bulk_update_tags_by_filter,
                SimpleNamespace(filter_json='{"filter":{"name":"Delivery"},"assignTags":["busy"]}'),
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_operations.HttpClient")
    def test_revision_and_tag_selectors_are_required(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_update,
                SimpleNamespace(operation_id="operation-1", operation_json='{"operation":{"enabled":true}}'),
                "revision",
            ),
            (
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_bulk_update_tags,
                SimpleNamespace(tags_json='{"assignTags":["busy"]}'),
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

    def test_parser_exposes_all_restaurants_online_order_operations_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-online-order-operations", "get", "--operation-id", "operation-1"], restaurants_online_order_operations.cmd_restaurants_online_order_operations_get, False),
            (["restaurants-online-order-operations", "list"], restaurants_online_order_operations.cmd_restaurants_online_order_operations_list, False),
            (["restaurants-online-order-operations", "query"], restaurants_online_order_operations.cmd_restaurants_online_order_operations_query, False),
            (
                ["restaurants-online-order-operations", "first-available-time-slot-per-fulfillment-type", "--operation-id", "operation-1"],
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_first_available_time_slot_per_fulfillment_type,
                False,
            ),
            (
                ["restaurants-online-order-operations", "first-available-time-slots-per-operation", "--operations-json", "{}"],
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_first_available_time_slots_per_operation,
                False,
            ),
            (
                ["restaurants-online-order-operations", "first-available-time-slots-per-menu", "--operation-id", "operation-1"],
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_first_available_time_slots_per_menu,
                False,
            ),
            (
                ["restaurants-online-order-operations", "available-time-slots-for-date", "--operation-id", "operation-1"],
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_available_time_slots_for_date,
                False,
            ),
            (
                ["restaurants-online-order-operations", "available-dates-in-range", "--operation-id", "operation-1"],
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_available_dates_in_range,
                False,
            ),
            (["restaurants-online-order-operations", "validate-address", "--operation-id", "operation-1"], restaurants_online_order_operations.cmd_restaurants_online_order_operations_validate_address, False),
            (["restaurants-online-order-operations", "update", "--operation-id", "operation-1", "--operation-json", "{}"], restaurants_online_order_operations.cmd_restaurants_online_order_operations_update, True),
            (["restaurants-online-order-operations", "delete", "--operation-id", "operation-1"], restaurants_online_order_operations.cmd_restaurants_online_order_operations_delete, True),
            (["restaurants-online-order-operations", "bulk-update-tags", "--tags-json", "{}"], restaurants_online_order_operations.cmd_restaurants_online_order_operations_bulk_update_tags, True),
            (
                ["restaurants-online-order-operations", "bulk-update-tags-by-filter", "--filter-json", "{}"],
                restaurants_online_order_operations.cmd_restaurants_online_order_operations_bulk_update_tags_by_filter,
                True,
            ),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
