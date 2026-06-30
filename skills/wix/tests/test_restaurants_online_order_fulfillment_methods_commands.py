from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_online_order_fulfillment_methods
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsOnlineOrderFulfillmentMethodsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-online-order-fulfillment-methods",
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_fulfillment_methods.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_fulfillment_methods.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"fulfillmentMethods": []})

        cases = [
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_list, SimpleNamespace(params_json='{"paging.limit":50}'), "GET", "/fulfillment-methods/v1/fulfillment-methods"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_get, SimpleNamespace(fulfillment_method_id="fm-1"), "GET", "/fulfillment-methods/v1/fulfillment-methods/fm-1"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_query, SimpleNamespace(query_json='{"query":{}}'), "POST", "/fulfillment-methods/v1/fulfillment-methods/query"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_list_available_for_address, SimpleNamespace(address_json='{"address":{"country":"US"}}'), "POST", "/fulfillment-methods/v1/fulfillment-methods/available-for-address"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_get_accumulated_availability, SimpleNamespace(params_json="{}"), "GET", "/fulfillment-methods/v1/fulfillment-methods/accumulated-availability"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_get_combined_availability, SimpleNamespace(params_json="{}"), "GET", "/fulfillment-methods/v1/fulfillment-methods/combined-availability"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_get_aggregated_availability, SimpleNamespace(availability_json='{"fulfillmentMethodIds":["fm-1"]}'), "POST", "/fulfillment-methods/v1/fulfillment-methods/aggregated-availability"),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-online-order-fulfillment-methods")

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_fulfillment_methods.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_fulfillment_methods.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_create, SimpleNamespace(fulfillment_method_json='{"fulfillmentMethod":{"name":"Pickup"}}'), "POST", "/fulfillment-methods/v1/fulfillment-methods"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_bulk_create, SimpleNamespace(fulfillment_methods_json='{"fulfillmentMethods":[{"name":"Pickup"}]}'), "POST", "/fulfillment-methods/v1/bulk/fulfillment-methods/create"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_update, SimpleNamespace(fulfillment_method_id="fm-1", fulfillment_method_json='{"fulfillmentMethod":{"revision":"1"}}'), "PATCH", "/fulfillment-methods/v1/fulfillment-methods/fm-1"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_delete, SimpleNamespace(fulfillment_method_id="fm-1"), "DELETE", "/fulfillment-methods/v1/fulfillment-methods/fm-1"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_bulk_update_tags, SimpleNamespace(tags_json='{"ids":["fm-1"],"assignTags":["featured"]}'), "POST", "/fulfillment-methods/v1/bulk/fulfillment-methods/update-tags"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_bulk_update_tags_by_filter, SimpleNamespace(filter_json='{"filter":{"type":"PICKUP"},"assignTags":["featured"]}'), "POST", "/fulfillment-methods/v1/bulk/fulfillment-methods/update-tags-by-filter"),
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_fulfillment_methods.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_fulfillment_methods.HttpClient")
    def test_irreversible_commands_require_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_delete, SimpleNamespace(fulfillment_method_id="fm-1")),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_bulk_update_tags_by_filter, SimpleNamespace(filter_json='{"filter":{"type":"PICKUP"},"assignTags":["featured"]}')),
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_fulfillment_methods.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_fulfillment_methods.HttpClient")
    def test_revision_and_tag_selectors_are_required(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_update, SimpleNamespace(fulfillment_method_id="fm-1", fulfillment_method_json='{"fulfillmentMethod":{"name":"Pickup"}}'), "revision"),
            (restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_bulk_update_tags, SimpleNamespace(tags_json='{"assignTags":["featured"]}'), "ids or fulfillmentMethodIds"),
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

    def test_parser_exposes_all_restaurants_online_order_fulfillment_methods_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-online-order-fulfillment-methods", "list"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_list, False),
            (["restaurants-online-order-fulfillment-methods", "get", "--fulfillment-method-id", "fm-1"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_get, False),
            (["restaurants-online-order-fulfillment-methods", "query"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_query, False),
            (["restaurants-online-order-fulfillment-methods", "list-available-for-address", "--address-json", "{}"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_list_available_for_address, False),
            (["restaurants-online-order-fulfillment-methods", "get-accumulated-availability"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_get_accumulated_availability, False),
            (["restaurants-online-order-fulfillment-methods", "get-combined-availability"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_get_combined_availability, False),
            (["restaurants-online-order-fulfillment-methods", "get-aggregated-availability", "--availability-json", "{}"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_get_aggregated_availability, False),
            (["restaurants-online-order-fulfillment-methods", "create", "--fulfillment-method-json", "{}"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_create, True),
            (["restaurants-online-order-fulfillment-methods", "bulk-create", "--fulfillment-methods-json", "{}"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_bulk_create, True),
            (["restaurants-online-order-fulfillment-methods", "update", "--fulfillment-method-id", "fm-1", "--fulfillment-method-json", "{}"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_update, True),
            (["restaurants-online-order-fulfillment-methods", "delete", "--fulfillment-method-id", "fm-1"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_delete, True),
            (["restaurants-online-order-fulfillment-methods", "bulk-update-tags", "--tags-json", "{}"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_bulk_update_tags, True),
            (["restaurants-online-order-fulfillment-methods", "bulk-update-tags-by-filter", "--filter-json", "{}"], restaurants_online_order_fulfillment_methods.cmd_restaurants_online_order_fulfillment_methods_bulk_update_tags_by_filter, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
