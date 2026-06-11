from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

from shopify_admin_api_tool.audit_log import AuditLogger
from shopify_admin_api_tool.commands.graphql import cmd_execute_operation
from shopify_admin_api_tool.errors import SafetyError
from shopify_admin_api_tool.official import load_official_manifest
from shopify_admin_api_tool.output import Output


class TestMutationPlanOffline(unittest.TestCase):
    def test_mutation_dry_run_emits_plan_without_network(self) -> None:
        args = SimpleNamespace(
            op_kind="mutation",
            op_kebab="app-uninstall",
            vars=None,
            return_shape_file=None,
            ack_unsafe_return_shape=False,
            allow_version_mismatch=False,
        )
        ctx = {
            "cfg": SimpleNamespace(
                shop_domain="example.myshopify.com",
                admin_access_token="token",
                api_version="2026-01",
                timeout_s=30.0,
            ),
            "timeout_s": 30.0,
            "verbose": False,
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "tool": "shopify-admin-api-tool",
            "tool_version": "0.0.0",
            "command_str": "shopify-admin-api-tool mutation app-uninstall",
            "audit": AuditLogger(path=None, enabled=False),
            "out": Output(mode="json"),
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_execute_operation(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertIn("plan", payload)
        self.assertEqual(payload["plan"]["selector"]["operation"], "appUninstall")

    def test_spend_impacting_mutation_is_high_risk_in_plan(self) -> None:
        manifest = load_official_manifest()
        op = manifest.find("mutation", kebab="app-subscription-create")
        self.assertIsNotNone(op)
        assert op is not None

        def placeholder_value(gql_type: str) -> object:
            t = str(gql_type or "").strip()
            while t.endswith("!"):
                t = t[:-1].strip()
            if t.startswith("[") and t.endswith("]"):
                return []
            if t in {"Boolean"}:
                return True
            if t in {"Int"}:
                return 1
            if t in {"Float", "Decimal"}:
                return 1.0
            if t in {"String", "ID", "DateTime", "URL", "EmailAddress"}:
                return "x"
            return {}

        required_vars = {a.name: placeholder_value(a.gql_type) for a in op.args if a.required}

        with tempfile.TemporaryDirectory() as td:
            vars_path = f"{td}/vars.json"
            with open(vars_path, "w", encoding="utf-8") as f:
                json.dump(required_vars, f, ensure_ascii=False, sort_keys=True)

            args = SimpleNamespace(
                op_kind="mutation",
                op_kebab="app-subscription-create",
                vars=vars_path,
                return_shape_file=None,
                ack_unsafe_return_shape=False,
                allow_version_mismatch=False,
            )
            ctx = {
                "cfg": SimpleNamespace(
                    shop_domain="example.myshopify.com",
                    admin_access_token="token",
                    api_version="2026-01",
                    timeout_s=30.0,
                ),
                "timeout_s": 30.0,
                "verbose": False,
                "apply": False,
                "yes": False,
                "ack_irreversible": False,
                "plan_out": None,
                "plan_in": None,
                "receipt_out": None,
                "tool": "shopify-admin-api-tool",
                "tool_version": "0.0.0",
                "command_str": "shopify-admin-api-tool mutation app-subscription-create",
                "audit": AuditLogger(path=None, enabled=False),
                "out": Output(mode="json"),
            }
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_execute_operation(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            self.assertEqual(plan["selector"]["operation"], "appSubscriptionCreate")
            self.assertEqual(plan["risk_level"], "high")
            self.assertIn("--apply", plan["required_flags"])
            self.assertIn("--yes", plan["required_flags"])
            self.assertIn("--plan-in", plan["required_flags"])

    def test_plan_marks_no_automatic_recovery(self) -> None:
        args = SimpleNamespace(
            op_kind="mutation",
            op_kebab="app-uninstall",
            vars=None,
            return_shape_file=None,
            ack_unsafe_return_shape=False,
            allow_version_mismatch=False,
        )
        ctx = {
            "cfg": SimpleNamespace(
                shop_domain="example.myshopify.com",
                admin_access_token="token",
                api_version="2026-01",
                timeout_s=30.0,
            ),
            "timeout_s": 30.0,
            "verbose": False,
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "tool": "shopify-admin-api-tool",
            "tool_version": "0.0.0",
            "command_str": "shopify-admin-api-tool mutation app-uninstall",
            "audit": AuditLogger(path=None, enabled=False),
            "out": Output(mode="json"),
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_execute_operation(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        plan = payload["plan"]
        self.assertIn("rollback", plan)
        self.assertIn("supported", plan["rollback"])
        self.assertIs(plan["rollback"]["supported"], False)
        notes = str(plan["rollback"].get("notes", ""))
        self.assertIn("does not create backups", notes)
        self.assertIn("does not auto-rollback", notes)
        self.assertIn("before_state", plan)
        self.assertTrue(plan["before_state"]["required"])
        self.assertFalse(plan["before_state"]["supported"])

    def test_mutation_apply_refuses_before_network_without_before_state(self) -> None:
        args = SimpleNamespace(
            op_kind="mutation",
            op_kebab="backup-region-update",
            vars=None,
            return_shape_file=None,
            ack_unsafe_return_shape=False,
            allow_version_mismatch=False,
        )
        ctx = {
            "cfg": SimpleNamespace(
                shop_domain="example.myshopify.com",
                admin_access_token="token",
                api_version="2026-01",
                timeout_s=30.0,
            ),
            "timeout_s": 30.0,
            "verbose": False,
            "apply": True,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "tool": "shopify-admin-api-tool",
            "tool_version": "0.0.0",
            "command_str": "shopify-admin-api-tool --apply mutation backup-region-update",
            "audit": AuditLogger(path=None, enabled=False),
            "out": Output(mode="json"),
        }
        with mock.patch("shopify_admin_api_tool.commands.graphql.ShopifyAdminGraphQLClient") as client_cls:
            with self.assertRaises(SafetyError) as cm:
                cmd_execute_operation(args, ctx)
        client_cls.assert_not_called()
        self.assertIn("before-state", str(cm.exception))
        self.assertIn("ack-no-snapshot", str(cm.exception))
