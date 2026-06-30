from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import loyalty_imports
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestLoyaltyImportsCommands(unittest.TestCase):
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
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli loyalty-imports",
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

    def test_parser_exposes_loyalty_imports_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["loyalty-imports", "get", "--import-id", "imp-1"], "get", False),
            (["loyalty-imports", "query"], "query", False),
            (["loyalty-imports", "create-file-url"], "create-file-url", True),
            (["loyalty-imports", "create", "--import-json", '{"fileUrl":"wixmp://file.csv"}'], "create", True),
            (
                [
                    "loyalty-imports",
                    "execute",
                    "--execute-json",
                    '{"loyaltyImportId":"imp-1","headerMappingInfo":{"headerMappings":[{"columnName":"email","columnIndex":0}]}}',
                ],
                "execute",
                True,
            ),
            (
                ["loyalty-imports", "get-error-file-download-url", "--import-id", "imp-1"],
                "get-error-file-download-url",
                False,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.loyalty_imports_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})

        cases = [
            (
                loyalty_imports.cmd_loyalty_imports_get,
                SimpleNamespace(import_id="imp-1"),
                "GET",
                "/_api/loyalty-imports/v1/loyalty-imports",
                {"loyaltyImportId": "imp-1"},
                None,
            ),
            (
                loyalty_imports.cmd_loyalty_imports_query,
                SimpleNamespace(query_json=None),
                "POST",
                "/_api/loyalty-imports/v1/loyalty-imports/query",
                None,
                {"query": {"sort": [{"fieldName": "createdDate", "order": "DESC"}], "paging": {"limit": 50}}},
            ),
            (
                loyalty_imports.cmd_loyalty_imports_get_error_file_download_url,
                SimpleNamespace(import_id="imp-1"),
                "GET",
                "/_api/loyalty-imports/v1/loyalty-imports/error-file-download-url",
                {"loyaltyImportId": "imp-1"},
                None,
            ),
        ]

        for func, args, http_method, path, params, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], http_method)
                self.assertEqual(payload["request"]["path"], path)
                if params is not None:
                    self.assertEqual(payload["request"]["params"], params)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_create_file_url_is_reviewed_plan_write_without_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = loyalty_imports.cmd_loyalty_imports_create_file_url(SimpleNamespace(), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/loyalty-imports/v1/loyalty-imports/wixmp-upload-url")
        self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_create_and_execute_are_plan_first_and_ack_gated(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                loyalty_imports.cmd_loyalty_imports_create,
                SimpleNamespace(import_json='{"fileUrl":"wixmp://file.csv","fileName":"points.csv","fileSize":1200}'),
                "POST",
                "/_api/loyalty-imports/v1/loyalty-imports",
                "loyalty-imports.create",
            ),
            (
                loyalty_imports.cmd_loyalty_imports_execute,
                SimpleNamespace(
                    execute_json='{"loyaltyImportId":"imp-1","headerMappingInfo":{"headerMappings":[{"columnName":"email","columnIndex":0}]}}'
                ),
                "POST",
                "/_api/loyalty-imports/v1/loyalty-imports/execute",
                "loyalty-imports.execute",
            ),
        ]

        for func, args, http_method, path, method in cases:
            with self.subTest(method=method):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_create_and_execute_validate_required_fields(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (loyalty_imports.cmd_loyalty_imports_create, SimpleNamespace(import_json='{"fileName":"points.csv"}'), "fileUrl"),
            (
                loyalty_imports.cmd_loyalty_imports_execute,
                SimpleNamespace(execute_json='{"loyaltyImportId":"imp-1","headerMappingInfo":{"headerMappings":[]}}'),
                "headerMappingInfo.headerMappings",
            ),
        ]
        for func, args, expected_error in cases:
            with self.subTest(expected_error=expected_error):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
                self.assertIn(expected_error, payload["error"])
                self.assertFalse(mock_client.return_value.request.called)
