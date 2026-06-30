from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import functions_v1
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestFunctionsV1Commands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli functions-v1",
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

    def test_parser_recognizes_functions_v1_inventory_backfilled_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["functions-v1", "create", "--function-json", '{"functionName":"myFunction"}'],
            ["functions-v1", "get", "--function-id", "fn-1"],
            ["functions-v1", "update", "--function-json", '{"id":"fn-1","revision":"2"}'],
            ["functions-v1", "delete", "--function-id", "fn-1"],
            ["functions-v1", "query", "--query-json", "{}"],
            ["functions-v1", "bulk-update-tags", "--tags-json", '{"functionIds":["fn-1"],"assignTags":["tag"]}'],
            [
                "functions-v1",
                "bulk-update-tags-by-filter",
                "--tags-json",
                '{"filter":{"appId":"app-1"},"assignTags":["tag"]}',
            ],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.functions_v1.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.functions_v1.HttpClient")
    def test_reads_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"function": {"id": "fn-1"}})

        cases = [
            (functions_v1.cmd_functions_v1_get, SimpleNamespace(function_id="fn-1"), "GET", "/functions/v1/functions/fn-1"),
            (
                functions_v1.cmd_functions_v1_query,
                SimpleNamespace(query_json='{"query":{"paging":{"limit":1}}}'),
                "POST",
                "/functions/v1/functions/query",
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
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "functions-v1")

    @patch("wix_safe_agent_cli.commands.functions_v1.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.functions_v1.HttpClient")
    def test_writes_build_plans_and_high_risk_writes_require_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (
                functions_v1.cmd_functions_v1_create,
                SimpleNamespace(function_json='{"functionName":"myFunction"}'),
                "POST",
                "/functions/v1/functions",
                False,
            ),
            (
                functions_v1.cmd_functions_v1_update,
                SimpleNamespace(function_json='{"id":"fn-1","revision":"2","functionName":"myFunction"}'),
                "PATCH",
                "/functions/v1/functions/fn-1",
                False,
            ),
            (
                functions_v1.cmd_functions_v1_delete,
                SimpleNamespace(function_id="fn-1"),
                "DELETE",
                "/functions/v1/functions/fn-1",
                True,
            ),
            (
                functions_v1.cmd_functions_v1_bulk_update_tags,
                SimpleNamespace(tags_json='{"functionIds":["fn-1"],"assignTags":["tag"]}'),
                "POST",
                "/functions/v1/bulk/functions/bulk-update-tags",
                False,
            ),
            (
                functions_v1.cmd_functions_v1_bulk_update_tags_by_filter,
                SimpleNamespace(tags_json='{"filter":{},"assignTags":["tag"]}'),
                "POST",
                "/functions/v1/bulk/functions/update-tags-by-filter",
                True,
            ),
        ]
        for func, args, method, path, requires_ack in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual("apply also requires --ack-irreversible" in payload["plan"]["preconditions"], requires_ack)
        mock_client.return_value.request.assert_not_called()

    def test_update_requires_revision(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = functions_v1.cmd_functions_v1_update(
                SimpleNamespace(function_json='{"id":"fn-1","functionName":"myFunction"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
