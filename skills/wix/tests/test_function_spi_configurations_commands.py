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
from wix_safe_agent_cli.commands import function_spi_configurations
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestFunctionSpiConfigurationsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli function-spi-configurations",
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

    def test_parser_recognizes_function_spi_configurations_inventory_backfilled_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["function-spi-configurations", "create", "--spi-configuration-json", '{"functionId":"fn-1"}'],
            ["function-spi-configurations", "get", "--spi-configuration-id", "cfg-1"],
            [
                "function-spi-configurations",
                "update",
                "--spi-configuration-json",
                '{"id":"cfg-1","revision":"1","functionId":"fn-1"}',
            ],
            ["function-spi-configurations", "delete", "--spi-configuration-id", "cfg-1"],
            ["function-spi-configurations", "query", "--query-json", "{}"],
            ["function-spi-configurations", "validate", "--spi-configuration-json", '{"functionId":"fn-1"}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.function_spi_configurations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.function_spi_configurations.HttpClient")
    def test_reads_and_helpers_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"functionSpiConfigurations": []})

        cases = [
            (
                function_spi_configurations.cmd_function_spi_configurations_get,
                SimpleNamespace(spi_configuration_id="cfg-1"),
                "GET",
                "/functions/v1/function-spi-configurations/cfg-1",
                None,
            ),
            (
                function_spi_configurations.cmd_function_spi_configurations_query,
                SimpleNamespace(query_json='{"filter":{"functionId":"fn-1"}}'),
                "POST",
                "/functions/v1/function-spi-configurations/query",
                {"filter": {"functionId": "fn-1"}},
            ),
            (
                function_spi_configurations.cmd_function_spi_configurations_validate,
                SimpleNamespace(spi_configuration_json='{"functionId":"fn-1"}'),
                "POST",
                "/functions/v1/function-spi-configurations/validate",
                {"functionSpiConfiguration": {"functionId": "fn-1"}},
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "function-spi-configurations")

    @patch("wix_safe_agent_cli.commands.function_spi_configurations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.function_spi_configurations.HttpClient")
    def test_writes_emit_reviewed_plans_on_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (
                function_spi_configurations.cmd_function_spi_configurations_create,
                SimpleNamespace(spi_configuration_json='{"functionId":"fn-1"}'),
                "functionSpiConfigurations.createFunctionSpiConfiguration",
                "POST",
                "/functions/v1/function-spi-configurations",
                False,
            ),
            (
                function_spi_configurations.cmd_function_spi_configurations_update,
                SimpleNamespace(spi_configuration_json='{"id":"cfg-1","revision":"1","functionId":"fn-1"}'),
                "functionSpiConfigurations.updateFunctionSpiConfiguration",
                "PATCH",
                "/functions/v1/function-spi-configurations/cfg-1",
                False,
            ),
            (
                function_spi_configurations.cmd_function_spi_configurations_delete,
                SimpleNamespace(spi_configuration_id="cfg-1"),
                "functionSpiConfigurations.deleteFunctionSpiConfiguration",
                "DELETE",
                "/functions/v1/function-spi-configurations/cfg-1",
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

    @patch("wix_safe_agent_cli.commands.function_spi_configurations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.function_spi_configurations.HttpClient")
    def test_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse(
            {"functionSpiConfiguration": {"id": "cfg-1", "revision": "2"}}
        )
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            selector = {"functionSpiConfiguration": {"id": "cfg-1", "revision": "1", "functionId": "fn-1"}}
            plan = {
                "method": "functionSpiConfigurations.updateFunctionSpiConfiguration",
                "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": selector},
                "proposed_changes": [{"operation": "update-function-spi-configuration"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = function_spi_configurations.cmd_function_spi_configurations_update(
                    SimpleNamespace(spi_configuration_json='{"id":"cfg-1","revision":"1","functionId":"fn-1"}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["method"], "PATCH")
        self.assertEqual(payload["receipt"]["request"]["path"], "/functions/v1/function-spi-configurations/cfg-1")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.function_spi_configurations.HttpClient")
    def test_update_requires_revision_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = function_spi_configurations.cmd_function_spi_configurations_update(
                SimpleNamespace(spi_configuration_json='{"id":"cfg-1","functionId":"fn-1"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.function_spi_configurations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.function_spi_configurations.HttpClient")
    def test_delete_apply_refuses_without_ack_irreversible(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "functionSpiConfigurations.deleteFunctionSpiConfiguration",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"functionSpiConfigurationId": "cfg-1"},
                },
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = function_spi_configurations.cmd_function_spi_configurations_delete(
                    SimpleNamespace(spi_configuration_id="cfg-1"),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=False),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()
