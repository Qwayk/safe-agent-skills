from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_online_order_service_fees
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsOnlineOrderServiceFeesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-online-order-service-fees",
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_service_fees.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_service_fees.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"rules": []})

        cases = [
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_calculate, SimpleNamespace(order_json='{"order":{"lineItems":[]}}'), "POST", "/service-fees/v1/calculate"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_list, SimpleNamespace(params_json='{"locationId":"loc-1"}'), "GET", "/service-fees/v1/rules"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_get, SimpleNamespace(rule_id="rule-1"), "GET", "/service-fees/v1/rules/rule-1"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_query, SimpleNamespace(query_json='{"query":{}}'), "POST", "/service-fees/v1/rules/query"),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-online-order-service-fees")

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_service_fees.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_service_fees.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_create, SimpleNamespace(rule_json='{"rule":{"name":"Delivery fee"}}'), "POST", "/service-fees/v1/rules"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_create, SimpleNamespace(rules_json='{"rules":[{"name":"Delivery fee"}]}'), "POST", "/service-fees/v1/bulk/rules/create"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_update, SimpleNamespace(rule_id="rule-1", rule_json='{"rule":{"revision":"1"}}'), "PATCH", "/service-fees/v1/rules/rule-1"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_update, SimpleNamespace(rules_json='{"rules":[{"id":"rule-1","revision":"1"}]}'), "PATCH", "/service-fees/v1/bulk/rules/update"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_delete, SimpleNamespace(rule_id="rule-1"), "DELETE", "/service-fees/v1/rules/rule-1"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_delete, SimpleNamespace(rules_json='{"ids":["rule-1"]}'), "DELETE", "/service-fees/v1/bulk/rules/delete"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_update_tags, SimpleNamespace(tags_json='{"ids":["rule-1"],"assignTags":["featured"]}'), "POST", "/service-fees/v1/bulk/rules/update-tags"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_update_tags_by_filter, SimpleNamespace(filter_json='{"filter":{"name":"Delivery"},"assignTags":["featured"]}'), "POST", "/service-fees/v1/bulk/rules/update-tags-by-filter"),
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_service_fees.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_service_fees.HttpClient")
    def test_irreversible_commands_require_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_delete, SimpleNamespace(rule_id="rule-1")),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_delete, SimpleNamespace(rules_json='{"ids":["rule-1"]}')),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_update_tags_by_filter, SimpleNamespace(filter_json='{"filter":{"name":"Delivery"},"assignTags":["featured"]}')),
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

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_service_fees.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_service_fees.HttpClient")
    def test_revision_and_tag_selectors_are_required(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_update, SimpleNamespace(rule_id="rule-1", rule_json='{"rule":{"name":"Delivery"}}'), "revision"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_update, SimpleNamespace(rules_json='{"rules":[{"id":"rule-1"}]}'), "revision"),
            (restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_update_tags, SimpleNamespace(tags_json='{"assignTags":["featured"]}'), "ids or ruleIds"),
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

    def test_parser_exposes_all_restaurants_online_order_service_fees_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-online-order-service-fees", "calculate", "--order-json", "{}"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_calculate, False),
            (["restaurants-online-order-service-fees", "list"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_list, False),
            (["restaurants-online-order-service-fees", "get", "--rule-id", "rule-1"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_get, False),
            (["restaurants-online-order-service-fees", "query"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_query, False),
            (["restaurants-online-order-service-fees", "create", "--rule-json", "{}"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_create, True),
            (["restaurants-online-order-service-fees", "bulk-create", "--rules-json", "{}"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_create, True),
            (["restaurants-online-order-service-fees", "update", "--rule-id", "rule-1", "--rule-json", "{}"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_update, True),
            (["restaurants-online-order-service-fees", "bulk-update", "--rules-json", "{}"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_update, True),
            (["restaurants-online-order-service-fees", "delete", "--rule-id", "rule-1"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_delete, True),
            (["restaurants-online-order-service-fees", "bulk-delete", "--rules-json", "{}"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_delete, True),
            (["restaurants-online-order-service-fees", "bulk-update-tags", "--tags-json", "{}"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_update_tags, True),
            (["restaurants-online-order-service-fees", "bulk-update-tags-by-filter", "--filter-json", "{}"], restaurants_online_order_service_fees.cmd_restaurants_online_order_service_fees_bulk_update_tags_by_filter, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
