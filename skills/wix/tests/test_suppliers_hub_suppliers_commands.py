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
from wix_safe_agent_cli.commands import suppliers_hub_suppliers
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestSuppliersHubSuppliersCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli suppliers-hub-suppliers",
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

    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"suppliers": []})

        cases = [
            (suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_get, SimpleNamespace(supplier_id="sup-1"), "GET", "/suppliers-hub/v1/suppliers/sup-1", None),
            (suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_query, SimpleNamespace(query_json='{"query":{"cursorPaging":{"limit":10}}}'), "POST", "/suppliers-hub/v1/suppliers/query", {"query": {"cursorPaging": {"limit": 10}}}),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "suppliers-hub-suppliers")

    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.HttpClient")
    def test_create_dry_run_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        args = SimpleNamespace(supplier_json='{"supplier":{"name":"Supply Co","types":["DROPSHIPPING"]}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "suppliers-hub-suppliers.create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/suppliers-hub/v1/suppliers")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.HttpClient")
    def test_update_dry_run_reads_before_state_and_fills_supplier_id_and_revision(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"supplier": {"id": "sup-1", "revision": "7", "name": "Old"}})
        args = SimpleNamespace(supplier_id="sup-1", supplier_json='{"supplier":{"name":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        body = payload["plan"]["request"]["body"]["supplier"]
        self.assertEqual(payload["plan"]["request"]["method"], "PATCH")
        self.assertEqual(payload["plan"]["request"]["path"], "/suppliers-hub/v1/suppliers/sup-1")
        self.assertEqual(body["id"], "sup-1")
        self.assertEqual(body["revision"], "7")
        self.assertIn("before_state", payload["plan"]["baseline"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.HttpClient")
    def test_update_refuses_mismatched_supplier_id(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"supplier": {"id": "sup-1", "revision": "7"}})
        args = SimpleNamespace(supplier_id="sup-1", supplier_json='{"supplier":{"id":"sup-2","name":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("supplier.id", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.HttpClient")
    def test_update_refuses_mismatched_supplier_revision(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"supplier": {"id": "sup-1", "revision": "7"}})
        args = SimpleNamespace(supplier_id="sup-1", supplier_json='{"supplier":{"id":"sup-1","revision":"6","name":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("supplier.revision", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.HttpClient")
    def test_delete_requires_ack_for_apply(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"supplier": {"id": "sup-1", "revision": "7"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_delete(
                SimpleNamespace(supplier_id="sup-1"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.HttpClient")
    def test_bulk_update_dry_run_reads_before_states_and_fills_revisions(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"supplier": {"id": "sup-1", "revision": "7"}}),
            _DummyResponse({"supplier": {"id": "sup-2", "revision": "9"}}),
        ]
        args = SimpleNamespace(suppliers_json='{"suppliers":[{"supplier":{"id":"sup-1","name":"One"}},{"id":"sup-2","name":"Two"}]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["request"]["method"], "POST")
        self.assertEqual(plan["request"]["path"], "/suppliers-hub/v1/bulk/suppliers/update")
        self.assertEqual(plan["request"]["body"]["suppliers"][0]["supplier"]["revision"], "7")
        self.assertEqual(plan["request"]["body"]["suppliers"][1]["supplier"]["revision"], "9")
        self.assertEqual(plan["selector"]["supplier_ids"], ["sup-1", "sup-2"])
        self.assertEqual(mock_client.return_value.request.call_count, 2)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.HttpClient")
    def test_bulk_delete_requires_ack_and_reads_before_states(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"supplier": {"id": "sup-1", "revision": "7"}}),
            _DummyResponse({"supplier": {"id": "sup-2", "revision": "9"}}),
        ]
        args = SimpleNamespace(supplier_ids_json='{"supplierIds":["sup-1","sup-2"]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_bulk_delete(
                args,
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/suppliers-hub/v1/bulk/suppliers/delete")
        self.assertEqual(payload["plan"]["selector"]["supplier_ids"], ["sup-1", "sup-2"])
        self.assertEqual(mock_client.return_value.request.call_count, 2)

    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.HttpClient")
    def test_bulk_update_tags_by_filter_is_async_plan_first_and_ack_gated(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        args = SimpleNamespace(tags_json='{"filter":{},"assignTags":{"publicTags":{"tagIds":["tag-1"]}}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_bulk_update_tags_by_filter(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/suppliers-hub/v1/bulk/suppliers/update-tags-by-filter")
        self.assertEqual(payload["plan"]["verification_plan"]["type"], "provider-response-plus-async-job")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_suppliers.HttpClient")
    def test_reviewed_update_apply_sends_patch_and_readback(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"supplier": {"id": "sup-1", "revision": "7", "name": "Old"}}),
            _DummyResponse({"supplier": {"id": "sup-1", "revision": "8", "name": "New"}}),
            _DummyResponse({"supplier": {"id": "sup-1", "revision": "8", "name": "New"}}),
        ]
        plan = {
            "method": "suppliers-hub-suppliers.update",
            "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": {"kind": "suppliers-hub-suppliers", "supplier_id": "sup-1"}},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_path = Path(tmpdir) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_update(
                    SimpleNamespace(supplier_id="sup-1", supplier_json='{"supplier":{"name":"New"}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["body"]["supplier"]["revision"], "7")
        self.assertEqual(payload["receipt"]["verification"]["type"], "read-after-write")
        self.assertEqual(mock_client.return_value.request.call_count, 3)

    def test_parser_includes_suppliers_hub_suppliers_commands(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["suppliers-hub-suppliers", "bulk-update-tags-by-filter", "--tags-json", '{"filter":{}}'])
        self.assertTrue(parsed.write_capable)
        self.assertIs(parsed.func, suppliers_hub_suppliers.cmd_suppliers_hub_suppliers_bulk_update_tags_by_filter)
