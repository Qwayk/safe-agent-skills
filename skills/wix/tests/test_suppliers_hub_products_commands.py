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
from wix_safe_agent_cli.commands import suppliers_hub_products
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestSuppliersHubProductsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli suppliers-hub-products",
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

    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"products": []})

        cases = [
            (suppliers_hub_products.cmd_suppliers_hub_products_get, SimpleNamespace(product_id="prod-1"), "GET", "/suppliers-hub/v1/products/prod-1", None),
            (suppliers_hub_products.cmd_suppliers_hub_products_query, SimpleNamespace(query_json='{"query":{"cursorPaging":{"limit":10}}}'), "POST", "/suppliers-hub/v1/products/query", {"query": {"cursorPaging": {"limit": 10}}}),
            (suppliers_hub_products.cmd_suppliers_hub_products_search, SimpleNamespace(search_json='{"search":{"search":{"expression":"shirt"}}}'), "POST", "/suppliers-hub/v1/products/search", {"search": {"search": {"expression": "shirt"}}}),
            (suppliers_hub_products.cmd_suppliers_hub_products_query_categories, SimpleNamespace(query_json='{"namespace":"WHOLESALE_NAMESPACE","query":{}}'), "POST", "/suppliers-hub/v1/categories/query", {"namespace": "WHOLESALE_NAMESPACE", "query": {}}),
        ]
        for func, args, method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "suppliers-hub-products")

    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.HttpClient")
    def test_create_dry_run_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        args = SimpleNamespace(product_json='{"product":{"name":"T-shirt","types":["DROPSHIPPING"]}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_products.cmd_suppliers_hub_products_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "suppliers-hub-products.create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/suppliers-hub/v1/products")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.HttpClient")
    def test_update_dry_run_reads_before_state_and_fills_product_id(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"product": {"id": "prod-1", "name": "Old"}})
        args = SimpleNamespace(product_id="prod-1", product_json='{"product":{"name":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_products.cmd_suppliers_hub_products_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["request"]["method"], "PATCH")
        self.assertEqual(plan["request"]["path"], "/suppliers-hub/v1/products/prod-1")
        self.assertEqual(plan["request"]["body"]["product"]["id"], "prod-1")
        self.assertIn("before_state", plan["baseline"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.HttpClient")
    def test_update_refuses_mismatched_product_id(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"product": {"id": "prod-1"}})
        args = SimpleNamespace(product_id="prod-1", product_json='{"product":{"id":"prod-2","name":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_products.cmd_suppliers_hub_products_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("product.id", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.HttpClient")
    def test_delete_requires_ack_for_apply(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"product": {"id": "prod-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_products.cmd_suppliers_hub_products_delete(
                SimpleNamespace(product_id="prod-1"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.HttpClient")
    def test_bulk_update_dry_run_reads_before_states_and_fills_ids(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"product": {"id": "prod-1"}}),
            _DummyResponse({"product": {"id": "prod-2"}}),
        ]
        args = SimpleNamespace(products_json='{"products":[{"product":{"id":"prod-1","name":"One"}},{"id":"prod-2","name":"Two"}]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_products.cmd_suppliers_hub_products_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["request"]["method"], "PATCH")
        self.assertEqual(plan["request"]["path"], "/suppliers-hub/v1/bulk/products/update")
        self.assertEqual(plan["request"]["body"]["products"][0]["product"]["id"], "prod-1")
        self.assertEqual(plan["request"]["body"]["products"][1]["product"]["id"], "prod-2")
        self.assertEqual(plan["selector"]["product_ids"], ["prod-1", "prod-2"])
        self.assertEqual(mock_client.return_value.request.call_count, 2)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.HttpClient")
    def test_bulk_delete_requires_ack_and_reads_before_states(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"product": {"id": "prod-1"}}),
            _DummyResponse({"product": {"id": "prod-2"}}),
        ]
        args = SimpleNamespace(product_ids_json='{"productIds":["prod-1","prod-2"]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_products.cmd_suppliers_hub_products_bulk_delete(
                args,
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/suppliers-hub/v1/bulk/products/delete")
        self.assertEqual(payload["plan"]["selector"]["product_ids"], ["prod-1", "prod-2"])
        self.assertEqual(mock_client.return_value.request.call_count, 2)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.HttpClient")
    def test_bulk_add_to_store_uses_official_endpoint_line(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        args = SimpleNamespace(add_json='{"productReferences":[{"productId":"prod-1","visibleInStore":true}]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_products.cmd_suppliers_hub_products_bulk_add_to_store(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/suppliershub/marketplace-product/v1/bulk/add-products-to-store",
        )
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.HttpClient")
    def test_bulk_update_tags_by_filter_is_async_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        args = SimpleNamespace(tags_json='{"filter":{},"assignTags":{"publicTags":{"tagIds":["tag-1"]}}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_products.cmd_suppliers_hub_products_bulk_update_tags_by_filter(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/suppliers-hub/v1/bulk/products/update-tags-by-filter")
        self.assertEqual(payload["plan"]["verification_plan"]["type"], "provider-response-plus-async-job")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_products.HttpClient")
    def test_reviewed_update_apply_sends_patch_and_readback(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"product": {"id": "prod-1", "name": "Old"}}),
            _DummyResponse({"product": {"id": "prod-1", "name": "New"}}),
            _DummyResponse({"product": {"id": "prod-1", "name": "New"}}),
        ]
        plan = {
            "method": "suppliers-hub-products.update",
            "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": {"kind": "suppliers-hub-products", "product_id": "prod-1"}},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_path = Path(tmpdir) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = suppliers_hub_products.cmd_suppliers_hub_products_update(
                    SimpleNamespace(product_id="prod-1", product_json='{"product":{"name":"New"}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["verification"]["type"], "read-after-write")
        self.assertEqual(mock_client.return_value.request.call_count, 3)

    def test_parser_includes_suppliers_hub_products_commands(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["suppliers-hub-products", "bulk-update-tags-by-filter", "--tags-json", '{"filter":{}}'])
        self.assertTrue(parsed.write_capable)
        self.assertIs(parsed.func, suppliers_hub_products.cmd_suppliers_hub_products_bulk_update_tags_by_filter)
