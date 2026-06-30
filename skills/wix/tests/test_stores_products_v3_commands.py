from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import stores_products_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestStoresProductsV3Commands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli stores-products-v3",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    @staticmethod
    def _current_product(*, revision: int = 3, slug: str = "sample-product") -> dict:
        return {
            "id": "product-1",
            "revision": revision,
            "slug": slug,
            "name": "Sample Product",
            "visible": True,
        }

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_stores_products_v3_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["stores-products-v3", "get", "--product-id", "product-1"])
        self.assertEqual(get_args.stores_products_v3_cmd, "get")
        self.assertFalse(get_args.write_capable)

        slug_args = parser.parse_args(["stores-products-v3", "get-by-slug", "--slug", "sample-product"])
        self.assertEqual(slug_args.stores_products_v3_cmd, "get-by-slug")
        self.assertFalse(slug_args.write_capable)

        category_args = parser.parse_args(["stores-products-v3", "get-all-products-category"])
        self.assertEqual(category_args.stores_products_v3_cmd, "get-all-products-category")
        self.assertFalse(category_args.write_capable)

        query_args = parser.parse_args(["stores-products-v3", "query"])
        self.assertEqual(query_args.stores_products_v3_cmd, "query")
        self.assertFalse(query_args.write_capable)

        search_args = parser.parse_args(["stores-products-v3", "search"])
        self.assertEqual(search_args.stores_products_v3_cmd, "search")
        self.assertFalse(search_args.write_capable)

        count_args = parser.parse_args(["stores-products-v3", "count"])
        self.assertEqual(count_args.stores_products_v3_cmd, "count")
        self.assertFalse(count_args.write_capable)

        create_args = parser.parse_args(["stores-products-v3", "create", "--product-json", '{"name":"Sample"}'])
        self.assertEqual(create_args.stores_products_v3_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(
            ["stores-products-v3", "update", "--product-id", "product-1", "--product-json", '{"revision":3}']
        )
        self.assertEqual(update_args.stores_products_v3_cmd, "update")
        self.assertTrue(update_args.write_capable)

        write_commands = [
            (["delete", "--product-id", "product-1"], "delete"),
            (["bulk-create", "--products-json", '[{"name":"Sample"}]'], "bulk-create"),
            (["bulk-delete", "--request-json", '{"productIds":["product-1"]}'], "bulk-delete"),
            (["bulk-update", "--products-json", '[{"id":"product-1","revision":3}]'], "bulk-update"),
            (["create-with-inventory", "--product-json", '{"name":"Sample"}'], "create-with-inventory"),
            (
                ["update-with-inventory", "--product-id", "product-1", "--product-json", '{"revision":3}'],
                "update-with-inventory",
            ),
            (["bulk-create-with-inventory", "--products-json", '[{"name":"Sample"}]'], "bulk-create-with-inventory"),
            (
                ["bulk-update-with-inventory", "--products-json", '[{"id":"product-1","revision":3}]'],
                "bulk-update-with-inventory",
            ),
            (["bulk-add-info-sections", "--request-json", '{"productIds":["product-1"]}'], "bulk-add-info-sections"),
            (
                ["bulk-add-info-sections-by-filter", "--request-json", '{"filter":{"visible":true}}'],
                "bulk-add-info-sections-by-filter",
            ),
            (
                ["bulk-add-to-categories-by-filter", "--request-json", '{"filter":{"visible":true}}'],
                "bulk-add-to-categories-by-filter",
            ),
            (
                ["bulk-adjust-variants-by-filter", "--request-json", '{"filter":{"visible":true}}'],
                "bulk-adjust-variants-by-filter",
            ),
            (["bulk-delete-by-filter", "--request-json", '{"filter":{"visible":false}}'], "bulk-delete-by-filter"),
            (
                ["bulk-remove-info-sections", "--request-json", '{"productIds":["product-1"]}'],
                "bulk-remove-info-sections",
            ),
            (
                ["bulk-remove-info-sections-by-filter", "--request-json", '{"filter":{"visible":true}}'],
                "bulk-remove-info-sections-by-filter",
            ),
            (
                ["bulk-remove-from-categories-by-filter", "--request-json", '{"filter":{"visible":true}}'],
                "bulk-remove-from-categories-by-filter",
            ),
            (
                ["bulk-update-variants-by-filter", "--request-json", '{"filter":{"visible":true}}'],
                "bulk-update-variants-by-filter",
            ),
            (["bulk-update-by-filter", "--request-json", '{"filter":{"visible":true}}'], "bulk-update-by-filter"),
        ]
        for argv, command_name in write_commands:
            with self.subTest(command_name=command_name):
                parsed = parser.parse_args(["stores-products-v3", *argv])
                self.assertEqual(parsed.stores_products_v3_cmd, command_name)
                self.assertTrue(parsed.write_capable)

    @patch("wix_safe_agent_cli.commands.stores_products_v3.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"product": self._current_product()})
        args = SimpleNamespace(product_id="product-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_products_v3.cmd_stores_products_v3_get(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/stores/v3/products/product-1")

    @patch("wix_safe_agent_cli.commands.stores_products_v3.HttpClient")
    def test_get_by_slug_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"product": self._current_product()})
        args = SimpleNamespace(slug="sample-product")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_products_v3.cmd_stores_products_v3_get_by_slug(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v3/products/slug/sample-product")

    @patch("wix_safe_agent_cli.commands.stores_products_v3.HttpClient")
    def test_get_all_products_category_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"categoryId": "all-products"})
        args = SimpleNamespace()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_products_v3.cmd_stores_products_v3_get_all_products_category(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v3/all-products-category")

    @patch("wix_safe_agent_cli.commands.stores_products_v3.HttpClient")
    def test_query_wraps_query_body(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"products": [], "pagingMetadata": {"count": 0}})
        args = SimpleNamespace(query_json='{"filter":{"name":{"$startsWith":"Sam"}}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_products_v3.cmd_stores_products_v3_query(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v3/products/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"name": {"$startsWith": "Sam"}}}})

    @patch("wix_safe_agent_cli.commands.stores_products_v3.HttpClient")
    def test_count_wraps_filter_body(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"count": 1})
        args = SimpleNamespace(filter_json='{"visible":true}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_products_v3.cmd_stores_products_v3_count(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["body"], {"filter": {"visible": True}})

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(product_json='{"name":"Sample Product","slug":"sample-product"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_products_v3.cmd_stores_products_v3_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "stores-products-v3.create")
        self.assertFalse(payload["plan"]["state_capture"]["before_state_available"])

    @patch("wix_safe_agent_cli.commands.stores_products_v3.HttpClient")
    def test_create_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(product_json='{"name":"Sample Product","slug":"sample-product"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_products_v3.cmd_stores_products_v3_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "stores-products-v3.create")
        mock_client.assert_not_called()

    @patch("wix_safe_agent_cli.commands.stores_products_v3.HttpClient")
    def test_update_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(product_id="product-1", product_json='{"revision":3,"name":"Updated"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_products_v3.cmd_stores_products_v3_update(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "stores-products-v3.update")
        mock_client.assert_not_called()

    def test_update_rejects_body_id_mismatch(self) -> None:
        args = SimpleNamespace(product_id="product-1", product_json='{"id":"product-2","revision":3}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_products_v3.cmd_stores_products_v3_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("does not match --product-id", payload["reasons"][0])

    def test_delete_dry_run_requires_irreversible_ack_in_plan(self) -> None:
        args = SimpleNamespace(product_id="product-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_products_v3.cmd_stores_products_v3_delete(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/stores/v3/products/product-1")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    def test_bulk_create_and_update_use_official_paths(self) -> None:
        cases = [
            (
                stores_products_v3.cmd_stores_products_v3_bulk_create,
                SimpleNamespace(products_json='[{"name":"Sample"}]'),
                "/stores/v3/bulk/products/create",
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_update,
                SimpleNamespace(products_json='[{"id":"product-1","revision":3}]'),
                "/stores/v3/bulk/products/update",
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_create_with_inventory,
                SimpleNamespace(products_json='[{"name":"Sample"}]'),
                "/stores/v3/bulk/products-with-inventory/create",
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_update_with_inventory,
                SimpleNamespace(products_json='[{"id":"product-1","revision":3}]'),
                "/stores/v3/bulk/products-with-inventory/update",
            ),
        ]
        for command, args, expected_path in cases:
            with self.subTest(expected_path=expected_path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = command(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["plan"]["request"]["path"], expected_path)

    def test_inventory_single_write_paths(self) -> None:
        cases = [
            (
                stores_products_v3.cmd_stores_products_v3_create_with_inventory,
                SimpleNamespace(product_json='{"name":"Sample"}'),
                "/stores/v3/products-with-inventory",
            ),
            (
                stores_products_v3.cmd_stores_products_v3_update_with_inventory,
                SimpleNamespace(product_id="product-1", product_json='{"revision":3}'),
                "/stores/v3/products-with-inventory/product-1",
            ),
        ]
        for command, args, expected_path in cases:
            with self.subTest(expected_path=expected_path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = command(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["plan"]["request"]["path"], expected_path)

    def test_filter_helper_paths_and_ack_rules(self) -> None:
        cases = [
            (
                stores_products_v3.cmd_stores_products_v3_bulk_add_info_sections,
                "/stores/v3/bulk/products/add-info-sections",
                False,
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_add_info_sections_by_filter,
                "/stores/v3/bulk/products/add-info-sections-by-filter",
                False,
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_add_to_categories_by_filter,
                "/stores/v3/bulk/products/add-to-categories-by-filter",
                False,
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_adjust_variants_by_filter,
                "/stores/v3/bulk/products/adjust-variants-by-filter",
                False,
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_delete_by_filter,
                "/stores/v3/bulk/products/delete-by-filter",
                True,
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_remove_info_sections,
                "/stores/v3/bulk/products/remove-info-sections",
                True,
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_remove_info_sections_by_filter,
                "/stores/v3/bulk/products/remove-info-sections-by-filter",
                True,
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_remove_from_categories_by_filter,
                "/stores/v3/bulk/products/remove-from-categories-by-filter",
                True,
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_update_variants_by_filter,
                "/stores/v3/bulk/products/update-variants-by-filter",
                False,
            ),
            (
                stores_products_v3.cmd_stores_products_v3_bulk_update_by_filter,
                "/stores/v3/bulk/products/update-by-filter",
                False,
            ),
        ]
        for command, expected_path, requires_ack in cases:
            with self.subTest(expected_path=expected_path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = command(SimpleNamespace(request_json='{"filter":{"visible":true}}'), self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["plan"]["request"]["path"], expected_path)
                if requires_ack:
                    self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.stores_products_v3.HttpClient")
    def test_update_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"product": self._current_product()}),
            _DummyResponse({"product": self._current_product()}),
            _DummyResponse({"product": self._current_product(revision=4)}),
            _DummyResponse({"product": self._current_product(revision=4)}),
        ]
        args = SimpleNamespace(product_id="product-1", product_json='{"revision":3,"name":"Updated Product"}')
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            stores_products_v3.cmd_stores_products_v3_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = stores_products_v3.cmd_stores_products_v3_update(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["revision"], 4)
        finally:
            Path(plan_path).unlink()
