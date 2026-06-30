from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import function_templates
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestFunctionTemplatesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli function-templates",
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

    def test_parser_recognizes_function_templates_inventory_backfilled_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["function-templates", "get", "--app-def-id", "app-1", "--function-template-id", "tpl-1"],
            ["function-templates", "query", "--query-json", "{}"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.function_templates.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.function_templates.HttpClient")
    def test_reads_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"functionTemplate": {"id": "tpl-1"}})

        cases = [
            (
                function_templates.cmd_function_templates_get,
                SimpleNamespace(app_def_id="app-1", function_template_id="tpl-1"),
                "GET",
                "/api/functions/v1/templates/app-1/tpl-1",
            ),
            (
                function_templates.cmd_function_templates_query,
                SimpleNamespace(query_json='{"filter":{"appDefId":"app-1","functionExtensionId":"ext-1"}}'),
                "POST",
                "/api/functions/v1/templates/query",
            ),
        ]
        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "function-templates")

    @patch("wix_safe_agent_cli.commands.function_templates.HttpClient")
    def test_invalid_get_ids_are_rejected_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = function_templates.cmd_function_templates_get(
                SimpleNamespace(app_def_id="app-1", function_template_id=" "),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()
