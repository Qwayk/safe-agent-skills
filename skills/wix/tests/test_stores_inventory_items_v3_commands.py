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
from wix_safe_agent_cli.commands import stores_inventory_items_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestStoresInventoryItemsV3Commands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli stores-inventory-items-v3",
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
    def _current_inventory_item(*, revision: int = 3) -> dict:
        return {
            "id": "inventory-item-1",
            "revision": revision,
            "variantId": "variant-1",
            "locationId": "location-1",
            "inStock": True,
        }

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_stores_inventory_items_v3_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["stores-inventory-items-v3", "get", "--inventory-item-id", "inventory-item-1"])
        self.assertEqual(get_args.stores_inventory_items_v3_cmd, "get")
        self.assertFalse(get_args.write_capable)

        query_args = parser.parse_args(["stores-inventory-items-v3", "query"])
        self.assertEqual(query_args.stores_inventory_items_v3_cmd, "query")
        self.assertFalse(query_args.write_capable)

        search_args = parser.parse_args(["stores-inventory-items-v3", "search"])
        self.assertEqual(search_args.stores_inventory_items_v3_cmd, "search")
        self.assertFalse(search_args.write_capable)

        create_args = parser.parse_args(
            ["stores-inventory-items-v3", "create", "--inventory-item-json", '{"variantId":"variant-1"}']
        )
        self.assertEqual(create_args.stores_inventory_items_v3_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(
            [
                "stores-inventory-items-v3",
                "update",
                "--inventory-item-id",
                "inventory-item-1",
                "--inventory-item-json",
                '{"revision":3}',
            ]
        )
        self.assertEqual(update_args.stores_inventory_items_v3_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(
            ["stores-inventory-items-v3", "delete", "--inventory-item-id", "inventory-item-1"]
        )
        self.assertEqual(delete_args.stores_inventory_items_v3_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

    @patch("wix_safe_agent_cli.commands.stores_inventory_items_v3.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"inventoryItem": self._current_inventory_item()}
        )
        args = SimpleNamespace(inventory_item_id="inventory-item-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_get(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/stores/v3/inventory-items/inventory-item-1")

    @patch("wix_safe_agent_cli.commands.stores_inventory_items_v3.HttpClient")
    def test_query_wraps_query_body(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"inventoryItems": [], "pagingMetadata": {"count": 0}}
        )
        args = SimpleNamespace(query_json='{"filter":{"locationId":{"$eq":"location-1"}}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_query(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v3/inventory-items/query")
        self.assertEqual(
            payload["request"]["body"],
            {"query": {"filter": {"locationId": {"$eq": "location-1"}}}},
        )

    @patch("wix_safe_agent_cli.commands.stores_inventory_items_v3.HttpClient")
    def test_search_wraps_search_body(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"inventoryItems": []})
        args = SimpleNamespace(search_json='{"filter":{"variantId":{"$eq":"variant-1"}}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_search(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v3/inventory-items/search")
        self.assertEqual(
            payload["request"]["body"],
            {"search": {"filter": {"variantId": {"$eq": "variant-1"}}}},
        )

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(
            inventory_item_json='{"variantId":"variant-1","locationId":"location-1","quantity":10}'
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "stores-inventory-items-v3.create")
        self.assertFalse(payload["plan"]["state_capture"]["before_state_available"])

    def test_update_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(
            inventory_item_id="inventory-item-1",
            inventory_item_json='{"revision":3,"quantity":12}',
        )
        with patch(
            "wix_safe_agent_cli.commands.stores_inventory_items_v3.HttpClient"
        ) as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse(
                {"inventoryItem": self._current_inventory_item()}
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "stores-inventory-items-v3.update")

    def test_delete_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(inventory_item_id="inventory-item-1")
        with patch(
            "wix_safe_agent_cli.commands.stores_inventory_items_v3.HttpClient"
        ) as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse(
                {"inventoryItem": self._current_inventory_item()}
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_delete(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "stores-inventory-items-v3.delete")

    @patch("wix_safe_agent_cli.commands.stores_inventory_items_v3.HttpClient")
    def test_create_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(
            inventory_item_json='{"variantId":"variant-1","locationId":"location-1","quantity":10}'
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_create(
                args,
                self._ctx(apply=True, yes=True),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "stores-inventory-items-v3.create")
        mock_client.assert_not_called()

    @patch("wix_safe_agent_cli.commands.stores_inventory_items_v3.HttpClient")
    def test_update_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(
            inventory_item_id="inventory-item-1",
            inventory_item_json='{"revision":3,"quantity":12}',
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_update(
                args,
                self._ctx(apply=True, yes=True),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "stores-inventory-items-v3.update")
        mock_client.assert_not_called()

    @patch("wix_safe_agent_cli.commands.stores_inventory_items_v3.HttpClient")
    def test_delete_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(inventory_item_id="inventory-item-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_delete(
                args,
                self._ctx(apply=True, yes=True, ack_irreversible=True),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "stores-inventory-items-v3.delete")
        mock_client.assert_not_called()

    def test_update_rejects_body_id_mismatch(self) -> None:
        args = SimpleNamespace(
            inventory_item_id="inventory-item-1",
            inventory_item_json='{"id":"inventory-item-2","revision":3}',
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("does not match --inventory-item-id", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.stores_inventory_items_v3.HttpClient")
    def test_update_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"inventoryItem": self._current_inventory_item()}),
            _DummyResponse({"inventoryItem": self._current_inventory_item()}),
            _DummyResponse({"inventoryItem": self._current_inventory_item(revision=4)}),
            _DummyResponse({"inventoryItem": self._current_inventory_item(revision=4)}),
        ]
        args = SimpleNamespace(
            inventory_item_id="inventory-item-1",
            inventory_item_json='{"revision":3,"quantity":12}',
        )
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            stores_inventory_items_v3.cmd_stores_inventory_items_v3_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_update(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["revision"], 4)
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.stores_inventory_items_v3.HttpClient")
    def test_delete_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"inventoryItem": self._current_inventory_item()}),
            _DummyResponse({"inventoryItem": self._current_inventory_item()}),
            _DummyResponse({}),
            RuntimeError("HTTP 404 for GET https://www.wixapis.com/stores/v3/inventory-items/inventory-item-1\n{}"),
        ]
        args = SimpleNamespace(inventory_item_id="inventory-item-1")
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            stores_inventory_items_v3.cmd_stores_inventory_items_v3_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = stores_inventory_items_v3.cmd_stores_inventory_items_v3_delete(
                    args,
                    self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path),
                )
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["actual_http_status"], 404)
        finally:
            Path(plan_path).unlink()
