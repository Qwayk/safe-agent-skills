from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_item_variants
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsItemVariantsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli restaurants-item-variants",
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

    @patch("wix_safe_agent_cli.commands.restaurants_item_variants.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_variants.HttpClient")
    def test_read_commands_use_official_rendered_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"variants": []})

        cases = [
            (
                restaurants_item_variants.cmd_restaurants_item_variants_list,
                SimpleNamespace(params_json='{"paging":{"limit":50}}'),
                "GET",
                "/restaurants/item-variants/v1/variants",
            ),
            (
                restaurants_item_variants.cmd_restaurants_item_variants_get,
                SimpleNamespace(variant_id="variant-1"),
                "GET",
                "/restaurants/item-variants/v1/variants/variant-1",
            ),
            (
                restaurants_item_variants.cmd_restaurants_item_variants_query,
                SimpleNamespace(query_json='{"query":{}}'),
                "POST",
                "/restaurants/item-variants/v1/variants/query",
            ),
            (
                restaurants_item_variants.cmd_restaurants_item_variants_count,
                SimpleNamespace(filter_json='{"filter":{"name":"Large"}}'),
                "POST",
                "/restaurants/item-variants/v1/variants/count",
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-item-variants")

    @patch("wix_safe_agent_cli.commands.restaurants_item_variants.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_variants.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_item_variants.cmd_restaurants_item_variants_create,
                SimpleNamespace(variant_json='{"variant":{"name":"Large"}}'),
                "POST",
                "/restaurants/item-variants/v1/variants",
            ),
            (
                restaurants_item_variants.cmd_restaurants_item_variants_update,
                SimpleNamespace(variant_id="variant-1", variant_json='{"variant":{"revision":"1","name":"Large"}}'),
                "PATCH",
                "/restaurants/item-variants/v1/variants/variant-1",
            ),
            (
                restaurants_item_variants.cmd_restaurants_item_variants_delete,
                SimpleNamespace(variant_id="variant-1"),
                "DELETE",
                "/restaurants/item-variants/v1/variants/variant-1",
            ),
            (
                restaurants_item_variants.cmd_restaurants_item_variants_bulk_create,
                SimpleNamespace(variants_json='{"variants":[{"variant":{"name":"Large"}}]}'),
                "POST",
                "/restaurants/item-variants/v1/bulk/variants/create",
            ),
            (
                restaurants_item_variants.cmd_restaurants_item_variants_bulk_delete,
                SimpleNamespace(variants_json='{"variantIds":["variant-1"]}'),
                "DELETE",
                "/restaurants/item-variants/v1/bulk/variants/delete",
            ),
            (
                restaurants_item_variants.cmd_restaurants_item_variants_bulk_update,
                SimpleNamespace(variants_json='{"variants":[{"variant":{"id":"variant-1","revision":"1"}}]}'),
                "POST",
                "/restaurants/item-variants/v1/bulk/variants/update",
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

    @patch("wix_safe_agent_cli.commands.restaurants_item_variants.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_variants.HttpClient")
    def test_delete_commands_require_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (restaurants_item_variants.cmd_restaurants_item_variants_delete, SimpleNamespace(variant_id="variant-1")),
            (restaurants_item_variants.cmd_restaurants_item_variants_bulk_delete, SimpleNamespace(variants_json='{"variantIds":["variant-1"]}')),
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

    @patch("wix_safe_agent_cli.commands.restaurants_item_variants.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_item_variants.HttpClient")
    def test_revision_required_for_update_methods(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                restaurants_item_variants.cmd_restaurants_item_variants_update,
                SimpleNamespace(variant_id="variant-1", variant_json='{"variant":{"name":"Large"}}'),
            ),
            (
                restaurants_item_variants.cmd_restaurants_item_variants_bulk_update,
                SimpleNamespace(variants_json='{"variants":[{"variant":{"id":"variant-1"}}]}'),
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

    def test_parser_exposes_all_restaurants_item_variants_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-item-variants", "list"], restaurants_item_variants.cmd_restaurants_item_variants_list, False),
            (["restaurants-item-variants", "get", "--variant-id", "variant-1"], restaurants_item_variants.cmd_restaurants_item_variants_get, False),
            (["restaurants-item-variants", "query"], restaurants_item_variants.cmd_restaurants_item_variants_query, False),
            (["restaurants-item-variants", "count"], restaurants_item_variants.cmd_restaurants_item_variants_count, False),
            (["restaurants-item-variants", "create", "--variant-json", "{}"], restaurants_item_variants.cmd_restaurants_item_variants_create, True),
            (
                ["restaurants-item-variants", "update", "--variant-id", "variant-1", "--variant-json", "{}"],
                restaurants_item_variants.cmd_restaurants_item_variants_update,
                True,
            ),
            (["restaurants-item-variants", "delete", "--variant-id", "variant-1"], restaurants_item_variants.cmd_restaurants_item_variants_delete, True),
            (["restaurants-item-variants", "bulk-create", "--variants-json", "{}"], restaurants_item_variants.cmd_restaurants_item_variants_bulk_create, True),
            (["restaurants-item-variants", "bulk-delete", "--variants-json", "{}"], restaurants_item_variants.cmd_restaurants_item_variants_bulk_delete, True),
            (["restaurants-item-variants", "bulk-update", "--variants-json", "{}"], restaurants_item_variants.cmd_restaurants_item_variants_bulk_update, True),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
