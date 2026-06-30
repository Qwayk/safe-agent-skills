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
from wix_safe_agent_cli.commands import billable_items
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBillableItemsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
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
            "command_str": "wix-safe-agent-cli billable-items",
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

    def test_parser_recognizes_billable_items_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["billable-items", "create", "--billable-item-json", '{"name":"Setup","price":"10"}'],
            ["billable-items", "get", "--billable-item-id", "bi-1"],
            ["billable-items", "update", "--billable-item-json", '{"id":"bi-1","revision":"1","name":"Setup"}'],
            ["billable-items", "delete", "--billable-item-id", "bi-1"],
            ["billable-items", "query", "--query-json", "{}"],
            ["billable-items", "search", "--search-json", "{}"],
            ["billable-items", "bulk-create", "--billable-items-json", '{"billableItems":[]}'],
            ["billable-items", "bulk-delete", "--billable-items-json", '{"billableItemIds":["bi-1"]}'],
            ["billable-items", "bulk-update", "--billable-items-json", '{"billableItems":[]}'],
            ["billable-items", "bulk-update-tags", "--tags-json", '{"billableItemIds":["bi-1"]}'],
            ["billable-items", "bulk-update-tags-by-filter", "--tags-json", '{"filter":{}}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.billable_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.billable_items.HttpClient")
    def test_reads_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"billableItems": []})

        cases = [
            (
                billable_items.cmd_billable_items_get,
                SimpleNamespace(billable_item_id="bi-1"),
                "GET",
                "/billable-items/v1/billable-items/bi-1",
                None,
            ),
            (
                billable_items.cmd_billable_items_query,
                SimpleNamespace(query_json='{"filter":{"name":"Setup"}}'),
                "POST",
                "/billable-items/v1/billable-items/query",
                {"filter": {"name": "Setup"}},
            ),
            (
                billable_items.cmd_billable_items_search,
                SimpleNamespace(search_json='{"search":{"expression":"setup"}}'),
                "POST",
                "/billable-items/v1/billable-items/search",
                {"search": {"expression": "setup"}},
            ),
        ]
        for func, args, http_method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], http_method)
                self.assertEqual(payload["request"]["path"], path)
                if body is None:
                    self.assertNotIn("body", payload["request"])
                else:
                    self.assertEqual(payload["request"]["body"], body)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "billable-items")

    @patch("wix_safe_agent_cli.commands.billable_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.billable_items.HttpClient")
    def test_writes_emit_reviewed_plans_on_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (
                billable_items.cmd_billable_items_create,
                SimpleNamespace(billable_item_json='{"name":"Setup","price":"10"}'),
                "billableItems.createBillableItem",
                "POST",
                "/billable-items/v1/billable-items",
                False,
            ),
            (
                billable_items.cmd_billable_items_update,
                SimpleNamespace(billable_item_json='{"id":"bi-1","revision":"1","name":"Setup"}'),
                "billableItems.updateBillableItem",
                "PATCH",
                "/billable-items/v1/billable-items/bi-1",
                False,
            ),
            (
                billable_items.cmd_billable_items_delete,
                SimpleNamespace(billable_item_id="bi-1"),
                "billableItems.deleteBillableItem",
                "DELETE",
                "/billable-items/v1/billable-items/bi-1",
                True,
            ),
            (
                billable_items.cmd_billable_items_bulk_create,
                SimpleNamespace(billable_items_json='{"billableItems":[]}'),
                "billableItems.bulkCreateBillableItems",
                "POST",
                "/billable-items/v1/bulk/billable-items/create",
                False,
            ),
            (
                billable_items.cmd_billable_items_bulk_delete,
                SimpleNamespace(billable_items_json='{"billableItemIds":["bi-1"]}'),
                "billableItems.bulkDeleteBillableItems",
                "POST",
                "/billable-items/v1/bulk/billable-items/delete",
                True,
            ),
            (
                billable_items.cmd_billable_items_bulk_update,
                SimpleNamespace(billable_items_json='{"billableItems":[{"id":"bi-1","revision":"1"}]}'),
                "billableItems.bulkUpdateBillableItems",
                "POST",
                "/billable-items/v1/bulk/billable-items/update",
                False,
            ),
            (
                billable_items.cmd_billable_items_bulk_update_tags,
                SimpleNamespace(tags_json='{"billableItemIds":["bi-1"],"assignTags":["retail"]}'),
                "billableItems.bulkUpdateBillableItemTags",
                "POST",
                "/billable-items/v1/bulk/billable-items/update-tags",
                False,
            ),
            (
                billable_items.cmd_billable_items_bulk_update_tags_by_filter,
                SimpleNamespace(tags_json='{"filter":{},"assignTags":["retail"]}'),
                "billableItems.bulkUpdateBillableItemTagsByFilter",
                "POST",
                "/billable-items/v1/bulk/billable-items/update-tags-by-filter",
                True,
            ),
        ]
        for func, args, method_name, http_method, path, requires_ack in cases:
            with self.subTest(method_name=method_name):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["method"], method_name)
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                if requires_ack:
                    self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                else:
                    self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.billable_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.billable_items.HttpClient")
    def test_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"billableItem": {"id": "bi-1", "revision": "2"}})
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            selector = {"billableItemId": "bi-1", "revision": "1"}
            plan = {
                "method": "billableItems.updateBillableItem",
                "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": selector},
                "proposed_changes": [{"operation": "update-billable-item"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = billable_items.cmd_billable_items_update(
                    SimpleNamespace(billable_item_json='{"id":"bi-1","revision":"1","name":"Setup"}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["method"], "PATCH")
        self.assertEqual(payload["receipt"]["request"]["path"], "/billable-items/v1/billable-items/bi-1")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.billable_items.HttpClient")
    def test_update_requires_revision_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = billable_items.cmd_billable_items_update(
                SimpleNamespace(billable_item_json='{"id":"bi-1","name":"Setup"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.billable_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.billable_items.HttpClient")
    def test_delete_apply_refuses_without_ack_irreversible(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "billableItems.deleteBillableItem",
                "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": {"billableItemId": "bi-1"}},
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = billable_items.cmd_billable_items_delete(
                    SimpleNamespace(billable_item_id="bi-1"),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=False),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()
