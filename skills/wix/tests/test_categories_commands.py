from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import categories
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCategoriesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli categories",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_categories_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["categories", "get", "--category-id", "cat-1"])
        self.assertEqual(get_args.categories_cmd, "get")
        self.assertFalse(get_args.write_capable)

        slug_args = parser.parse_args(["categories", "get-by-slug", "--slug", "bottles"])
        self.assertEqual(slug_args.categories_cmd, "get-by-slug")
        self.assertFalse(slug_args.write_capable)

        query_args = parser.parse_args(["categories", "query"])
        self.assertEqual(query_args.categories_cmd, "query")

        search_args = parser.parse_args(["categories", "search"])
        self.assertEqual(search_args.categories_cmd, "search")

        count_args = parser.parse_args(["categories", "count"])
        self.assertEqual(count_args.categories_cmd, "count")

        list_trees_args = parser.parse_args(["categories", "list-trees"])
        self.assertEqual(list_trees_args.categories_cmd, "list-trees")

        arranged_args = parser.parse_args(["categories", "get-arranged-items", "--category-id", "cat-1"])
        self.assertEqual(arranged_args.categories_cmd, "get-arranged-items")

        one_item_args = parser.parse_args(["categories", "list-categories-for-item"])
        self.assertEqual(one_item_args.categories_cmd, "list-categories-for-item")

        many_items_args = parser.parse_args(["categories", "list-categories-for-items"])
        self.assertEqual(many_items_args.categories_cmd, "list-categories-for-items")

        list_items_args = parser.parse_args(["categories", "list-items-in-category", "--category-id", "cat-1"])
        self.assertEqual(list_items_args.categories_cmd, "list-items-in-category")

        write_commands = [
            (["create", "--category-json", '{"name":"Sale"}'], "create"),
            (["update", "--category-id", "cat-1", "--category-json", '{"revision":"1","name":"Sale"}'], "update"),
            (["delete", "--category-id", "cat-1"], "delete"),
            (["bulk-update", "--categories-json", '[{"id":"cat-1","revision":"1"}]'], "bulk-update"),
            (["update-visibility", "--request-json", '{"categoryIds":["cat-1"],"visible":true}'], "update-visibility"),
            (["bulk-show", "--request-json", '{"categoryIds":["cat-1"]}'], "bulk-show"),
            (
                ["bulk-add-items-to-category", "--category-id", "cat-1", "--request-json", '{"itemIds":["item-1"]}'],
                "bulk-add-items-to-category",
            ),
            (
                ["bulk-add-item-to-categories", "--request-json", '{"itemId":"item-1","categoryIds":["cat-1"]}'],
                "bulk-add-item-to-categories",
            ),
            (
                ["bulk-remove-items-from-category", "--category-id", "cat-1", "--request-json", '{"itemIds":["item-1"]}'],
                "bulk-remove-items-from-category",
            ),
            (
                ["bulk-remove-item-from-categories", "--request-json", '{"itemId":"item-1","categoryIds":["cat-1"]}'],
                "bulk-remove-item-from-categories",
            ),
            (["move", "--category-id", "cat-1", "--request-json", '{"afterCategoryId":"cat-0"}'], "move"),
            (
                ["set-arranged-items", "--category-id", "cat-1", "--request-json", '{"items":[{"catalogItemId":"item-1"}]}'],
                "set-arranged-items",
            ),
        ]
        for argv, command_name in write_commands:
            with self.subTest(command_name=command_name):
                parsed = parser.parse_args(["categories", *argv])
                self.assertEqual(parsed.categories_cmd, command_name)
                self.assertTrue(parsed.write_capable)

    @patch("wix_safe_agent_cli.commands.categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.categories.HttpClient")
    def test_get_uses_expected_request_and_auth_family(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"category": {"id": "cat-1"}})
        args = SimpleNamespace(category_id="cat-1", tree_reference_json=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_get(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/categories/v1/categories/cat-1")
        self.assertEqual(payload["request"]["params"]["treeReference.appNamespace"], "@wix/stores")
        self.assertEqual(payload["request"]["params"]["treeReference.treeKey"], "null")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "categories")

    @patch("wix_safe_agent_cli.commands.categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.categories.HttpClient")
    def test_get_by_slug_uses_expected_request(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"category": {"slug": "bottles"}})
        args = SimpleNamespace(slug="bottles", tree_reference_json=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_get_by_slug(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/categories/v1/categories/slug/bottles")
        self.assertEqual(payload["request"]["params"]["treeReference.appNamespace"], "@wix/stores")

    @patch("wix_safe_agent_cli.commands.categories.HttpClient")
    def test_query_wraps_query_body_and_tree_reference(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"categories": []})
        args = SimpleNamespace(query_json='{"filter":{"name":{"$startsWith":"Sale"}}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_query(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/categories/v1/categories/query")
        self.assertEqual(
            payload["request"]["body"],
            {
                "treeReference": {"appNamespace": "@wix/stores", "treeKey": None},
                "query": {"filter": {"name": {"$startsWith": "Sale"}}},
            },
        )

    @patch("wix_safe_agent_cli.commands.categories.HttpClient")
    def test_search_wraps_search_body_and_tree_reference(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"categories": []})
        args = SimpleNamespace(search_json='{"includeHiddenCategories":true}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_search(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["body"]["treeReference"]["appNamespace"], "@wix/stores")
        self.assertEqual(payload["request"]["body"]["search"], {"includeHiddenCategories": True})

    @patch("wix_safe_agent_cli.commands.categories.HttpClient")
    def test_count_wraps_filter_body_and_tree_reference(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"count": 1})
        args = SimpleNamespace(filter_json='{"hidden":{"$eq":false}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_count(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/categories/v1/categories/count")
        self.assertEqual(payload["request"]["body"]["filter"], {"hidden": {"$eq": False}})

    @patch("wix_safe_agent_cli.commands.categories.HttpClient")
    def test_list_trees_uses_tree_reference_params(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"trees": []})
        args = SimpleNamespace(tree_reference_json=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_list_trees(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/categories/v1/categories/list-trees")
        self.assertEqual(payload["request"]["params"]["treeReference.appNamespace"], "@wix/stores")

    @patch("wix_safe_agent_cli.commands.categories.HttpClient")
    def test_get_arranged_items_uses_category_path(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"items": []})
        args = SimpleNamespace(category_id="cat-1", tree_reference_json=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_get_arranged_items(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/categories/v1/categories/cat-1/arranged-items")

    @patch("wix_safe_agent_cli.commands.categories.HttpClient")
    def test_list_categories_for_item_uses_default_tree_reference(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"categories": []})
        args = SimpleNamespace(request_json='{"catalogItemId":"product-1"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_list_categories_for_item(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["body"]["catalogItemId"], "product-1")
        self.assertEqual(payload["request"]["body"]["treeReference"]["appNamespace"], "@wix/stores")

    @patch("wix_safe_agent_cli.commands.categories.HttpClient")
    def test_list_categories_for_items_uses_default_tree_reference(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": []})
        args = SimpleNamespace(request_json='{"catalogItemIds":["product-1","product-2"]}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_list_categories_for_items(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["body"]["catalogItemIds"], ["product-1", "product-2"])
        self.assertEqual(payload["request"]["body"]["treeReference"]["treeKey"], None)

    @patch("wix_safe_agent_cli.commands.categories.HttpClient")
    def test_list_items_in_category_uses_default_tree_reference(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"items": []})
        args = SimpleNamespace(category_id="cat-1", request_json='{"paging":{"limit":10}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_list_items_in_category(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/categories/v1/categories/cat-1/list-items")
        self.assertEqual(payload["request"]["body"]["paging"], {"limit": 10})
        self.assertEqual(payload["request"]["body"]["treeReference"]["appNamespace"], "@wix/stores")

    @patch("wix_safe_agent_cli.commands.categories.resolve_auth_mode")
    def test_create_emits_reviewed_plan_without_live_write(self, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        args = SimpleNamespace(category_json='{"name":"Sale"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "categories.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/categories/v1/categories")
        self.assertEqual(payload["plan"]["request"]["body"]["category"]["name"], "Sale")
        self.assertEqual(payload["plan"]["request"]["body"]["treeReference"]["appNamespace"], "@wix/stores")

    @patch("wix_safe_agent_cli.commands.categories.resolve_auth_mode")
    def test_update_requires_revision_and_body_id_match(self, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        missing_revision = SimpleNamespace(category_id="cat-1", category_json='{"name":"Sale"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_update(missing_revision, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("revision", payload["error"])

        mismatched_id = SimpleNamespace(category_id="cat-1", category_json='{"id":"cat-2","revision":"1"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_update(mismatched_id, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("does not match", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.categories.resolve_auth_mode")
    def test_bulk_update_uses_official_path_and_requires_revisions(self, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        args = SimpleNamespace(categories_json='[{"id":"cat-1","revision":"1","name":"Sale"}]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = categories.cmd_categories_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["plan"]["request"]["path"], "/categories/v1/bulk/categories/update")
        self.assertEqual(payload["plan"]["request"]["body"]["categories"][0]["id"], "cat-1")

    @patch("wix_safe_agent_cli.commands.categories.resolve_auth_mode")
    def test_item_assignment_write_paths(self, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        cases = [
            (
                categories.cmd_categories_update_visibility,
                SimpleNamespace(request_json='{"categoryIds":["cat-1"],"visible":true}'),
                "/categories/v1/categories/visibility",
            ),
            (
                categories.cmd_categories_bulk_show,
                SimpleNamespace(request_json='{"categoryIds":["cat-1"]}'),
                "/categories/v1/bulk/categories/show",
            ),
            (
                categories.cmd_categories_bulk_add_items_to_category,
                SimpleNamespace(category_id="cat-1", request_json='{"itemIds":["item-1"]}'),
                "/categories/v1/bulk/categories/cat-1/add-items",
            ),
            (
                categories.cmd_categories_bulk_add_item_to_categories,
                SimpleNamespace(request_json='{"itemId":"item-1","categoryIds":["cat-1"]}'),
                "/categories/v1/bulk/categories/add-item",
            ),
            (
                categories.cmd_categories_move,
                SimpleNamespace(category_id="cat-1", request_json='{"afterCategoryId":"cat-0"}'),
                "/categories/v1/categories/cat-1/move",
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

    @patch("wix_safe_agent_cli.commands.categories.resolve_auth_mode")
    def test_irreversible_category_writes_require_ack(self, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        cases = [
            (
                categories.cmd_categories_delete,
                SimpleNamespace(category_id="cat-1"),
                "/categories/v1/categories/cat-1",
            ),
            (
                categories.cmd_categories_bulk_remove_items_from_category,
                SimpleNamespace(category_id="cat-1", request_json='{"itemIds":["item-1"]}'),
                "/categories/v1/bulk/categories/cat-1/remove-items",
            ),
            (
                categories.cmd_categories_bulk_remove_item_from_categories,
                SimpleNamespace(request_json='{"itemId":"item-1","categoryIds":["cat-1"]}'),
                "/categories/v1/bulk/categories/remove-item",
            ),
            (
                categories.cmd_categories_set_arranged_items,
                SimpleNamespace(category_id="cat-1", request_json='{"items":[{"catalogItemId":"item-1"}]}'),
                "/categories/v1/categories/cat-1/set-arranged-items",
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
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
