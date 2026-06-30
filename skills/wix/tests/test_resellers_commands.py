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
from wix_safe_agent_cli.commands import resellers
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestResellersCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token=None,
            api_key="acct-api-key",
            account_id="acct-001",
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
            "command_str": "wix-safe-agent-cli resellers",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_resellers_commands(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["resellers", "get", "--package-id", "pkg-1"])
        self.assertEqual(read_args.resellers_cmd, "get")
        self.assertFalse(read_args.write_capable)
        self.assertEqual(read_args.func.__name__, "cmd_resellers_get")

        write_args = parser.parse_args(["resellers", "cancel-product-instance", "--instance-id", "inst-1"])
        self.assertEqual(write_args.resellers_cmd, "cancel-product-instance")
        self.assertTrue(write_args.write_capable)
        self.assertEqual(write_args.func.__name__, "cmd_resellers_cancel_product_instance")

    @patch("wix_safe_agent_cli.commands.resellers.HttpClient")
    def test_resellers_get_uses_account_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"package": {"id": "pkg-1"}})

        args = SimpleNamespace(package_id="pkg-1")
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = resellers.cmd_resellers_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "resellers.get")
        self.assertEqual(payload["request"]["path"], "/resellers/v1/packages/pkg-1")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(str(call.kwargs["url"]).endswith("/resellers/v1/packages/pkg-1"))
        self.assertEqual(call.kwargs["headers"]["Authorization"], "acct-api-key")
        self.assertEqual(call.kwargs["headers"]["wix-account-id"], "acct-001")

    @patch("wix_safe_agent_cli.commands.resellers.HttpClient")
    def test_resellers_query_builds_query_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"packages": []})

        args = SimpleNamespace(
            query_json='{"query":{}}',
            filter_json='{"externalId":{"$eq":"ext-1"}}',
            sort_json='{"createdDate":"DESC"}',
            cursor="cursor-1",
            limit=50,
        )
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = resellers.cmd_resellers_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        body = payload["request"]["body"]
        self.assertEqual(body["query"]["filter"], {"externalId": {"$eq": "ext-1"}})
        self.assertEqual(body["query"]["sort"], {"createdDate": "DESC"})
        self.assertEqual(body["query"]["cursorPaging"], {"cursor": "cursor-1", "limit": 50})
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["json_body"], body)
        self.assertEqual(call.kwargs["headers"]["Content-Type"], "application/json")

    def test_create_package_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(body_json='{"externalId":"ext-1","productInstances":[{"catalogProductId":"prod-1"}]}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = resellers.cmd_resellers_create_package(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "resellers.create-package")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/resellers/v2/packages")
        self.assertEqual(payload["plan"]["request"]["body"]["externalId"], "ext-1")
        self.assertIn("reseller-package-create", payload["plan"]["risk_reasons"])

    @patch("wix_safe_agent_cli.commands.resellers.HttpClient")
    def test_assign_product_instance_apply_writes_receipt(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"package": {"id": "pkg-1"}})

        args = SimpleNamespace(instance_id="inst-1", site_id="site-1")
        ctx = self._ctx(apply=True, yes=True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = resellers.cmd_resellers_assign_product_instance(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "resellers.assign-product-instance")
        self.assertEqual(payload["receipt"]["selector"]["instance_id"], "inst-1")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "PATCH")
        self.assertTrue(str(call.kwargs["url"]).endswith("/resellers/v1/packages/product-instances/inst-1/site-1"))
        self.assertEqual(call.kwargs["headers"]["Authorization"], "acct-api-key")
        self.assertEqual(call.kwargs["headers"]["wix-account-id"], "acct-001")

    def test_adjust_product_instance_requires_catalog_or_billing(self) -> None:
        args = SimpleNamespace(instance_id="inst-1", body_json='{"externalId":"not-supported"}')
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = resellers.cmd_resellers_adjust_product_instance(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("catalogProductId or billingInfo", payload["error"])

    def test_cancel_package_requires_ack_for_apply(self) -> None:
        args = SimpleNamespace(package_id="pkg-1")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = resellers.cmd_resellers_cancel_package(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "resellers.cancel-package")
        self.assertNotIn("receipt", payload)
        self.assertIn("irreversible", payload["plan"]["risk_reasons"])

    @patch("wix_safe_agent_cli.commands.resellers.HttpClient")
    def test_cancel_product_instance_apply_with_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})

        args = SimpleNamespace(instance_id="inst-1")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = resellers.cmd_resellers_cancel_product_instance(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "resellers.cancel-product-instance")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "DELETE")
        self.assertTrue(str(call.kwargs["url"]).endswith("/resellers/v1/packages/product-instances/inst-1"))

    def test_plan_in_mismatch_is_refused(self) -> None:
        args = SimpleNamespace(instance_id="inst-1", site_id="site-1")
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(
                {
                    "method": "resellers.assign-product-instance",
                    "baseline": {
                        "env_fingerprint": "https://other.example",
                        "selector": {
                            "kind": "wix-reseller-package",
                            "operation": "assign-product-instance",
                            "instance_id": "inst-1",
                            "site_id": "site-1",
                        },
                    },
                },
                handle,
            )
            plan_path = handle.name

        try:
            ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = resellers.cmd_resellers_assign_product_instance(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("env_fingerprint", payload["reasons"][0])
        finally:
            Path(plan_path).unlink()


if __name__ == "__main__":
    unittest.main()
