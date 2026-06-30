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
from wix_safe_agent_cli.commands import builderless_productions
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBuilderlessProductionsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli builderless-productions",
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

    def test_parser_recognizes_builderless_productions_inventory_backfilled_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["builderless-productions", "create", "--builderless-production-json", '{"templateOptions":{}}'],
            ["builderless-productions", "get", "--function-id", "fn-1"],
            ["builderless-productions", "update", "--builderless-production-json", '{"id":"fn-1"}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.builderless_productions.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.builderless_productions.HttpClient")
    def test_reads_and_plans_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"functionBuilderlessProduction": {"id": "fn-1"}})

        read_buf = io.StringIO()
        with redirect_stdout(read_buf):
            read_rc = builderless_productions.cmd_builderless_productions_get(
                SimpleNamespace(function_id="fn-1"),
                self._ctx(),
            )
        read_payload = json.loads(read_buf.getvalue())
        self.assertEqual(read_rc, 0)
        self.assertEqual(read_payload["request"]["method"], "GET")
        self.assertEqual(read_payload["request"]["path"], "/functions/v1/function-builderless-productions/fn-1")

        cases = [
            (
                builderless_productions.cmd_builderless_productions_create,
                SimpleNamespace(builderless_production_json='{"templateOptions":{"functionTemplateId":"tpl-1"}}'),
                "builderlessProductions.createFunctionBuilderlessProduction",
                "POST",
                "/functions/v1/function-builderless-productions",
            ),
            (
                builderless_productions.cmd_builderless_productions_update,
                SimpleNamespace(builderless_production_json='{"id":"fn-1","templateOptions":{}}'),
                "builderlessProductions.updateFunctionBuilderlessProduction",
                "PATCH",
                "/functions/v1/function-builderless-productions/fn-1",
            ),
        ]
        for func, args, method_name, http_method, path in cases:
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "builderless-productions")

    @patch("wix_safe_agent_cli.commands.builderless_productions.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.builderless_productions.HttpClient")
    def test_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"functionBuilderlessProduction": {"id": "fn-1"}})
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "builderlessProductions.updateFunctionBuilderlessProduction",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"functionBuilderlessProduction": {"id": "fn-1", "templateOptions": {}}},
                },
                "proposed_changes": [{"operation": "update-function-builderless-production"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = builderless_productions.cmd_builderless_productions_update(
                    SimpleNamespace(builderless_production_json='{"id":"fn-1","templateOptions":{}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["method"], "PATCH")
        self.assertEqual(payload["receipt"]["request"]["path"], "/functions/v1/function-builderless-productions/fn-1")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.builderless_productions.HttpClient")
    def test_update_requires_builderless_production_id_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = builderless_productions.cmd_builderless_productions_update(
                SimpleNamespace(builderless_production_json='{"templateOptions":{}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()
