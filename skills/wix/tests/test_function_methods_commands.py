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
from wix_safe_agent_cli.commands import function_methods
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestFunctionMethodsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli function-methods",
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

    def test_parser_recognizes_function_methods_inventory_backfilled_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["function-methods", "create", "--function-method-json", '{"functionId":"fn-1","automationId":"auto-1"}'],
            ["function-methods", "delete", "--function-method-id", "method-1"],
            ["function-methods", "query", "--query-json", "{}"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.function_methods.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.function_methods.HttpClient")
    def test_read_and_plans_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"functionMethods": []})

        read_buf = io.StringIO()
        with redirect_stdout(read_buf):
            read_rc = function_methods.cmd_function_methods_query(
                SimpleNamespace(query_json='{"filter":{"functionId":"fn-1"}}'),
                self._ctx(),
            )
        read_payload = json.loads(read_buf.getvalue())
        self.assertEqual(read_rc, 0)
        self.assertEqual(read_payload["request"]["method"], "POST")
        self.assertEqual(read_payload["request"]["path"], "/functions/v1/methods/query")
        self.assertEqual(read_payload["request"]["body"], {"filter": {"functionId": "fn-1"}})

        cases = [
            (
                function_methods.cmd_function_methods_create,
                SimpleNamespace(function_method_json='{"functionId":"fn-1","automationId":"auto-1"}'),
                "functionMethods.createFunctionMethod",
                "POST",
                "/functions/v1/methods",
                False,
            ),
            (
                function_methods.cmd_function_methods_delete,
                SimpleNamespace(function_method_id="method-1"),
                "functionMethods.deleteFunctionMethod",
                "DELETE",
                "/functions/v1/methods/method-1",
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "function-methods")

    @patch("wix_safe_agent_cli.commands.function_methods.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.function_methods.HttpClient")
    def test_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"functionMethod": {"id": "method-1"}})
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "functionMethods.createFunctionMethod",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"functionMethod": {"functionId": "fn-1", "automationId": "auto-1"}},
                },
                "proposed_changes": [{"operation": "create-function-method"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = function_methods.cmd_function_methods_create(
                    SimpleNamespace(function_method_json='{"functionId":"fn-1","automationId":"auto-1"}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["method"], "POST")
        self.assertEqual(payload["receipt"]["request"]["path"], "/functions/v1/methods")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.function_methods.HttpClient")
    def test_create_requires_non_empty_function_method_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = function_methods.cmd_function_methods_create(
                SimpleNamespace(function_method_json="{}"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.function_methods.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.function_methods.HttpClient")
    def test_delete_apply_refuses_without_ack_irreversible(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "functionMethods.deleteFunctionMethod",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"functionMethodId": "method-1"},
                },
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = function_methods.cmd_function_methods_delete(
                    SimpleNamespace(function_method_id="method-1"),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=False),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(payload["plan"]["risk_level"], "high")
        mock_client.return_value.request.assert_not_called()
