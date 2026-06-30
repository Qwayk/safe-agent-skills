from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import branches
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


class TestBranchesParser(unittest.TestCase):
    def test_parser_recognizes_branches_commands(self) -> None:
        parser = build_parser()

        default_args = parser.parse_args(["branches", "get-default"])
        self.assertEqual(default_args.branches_cmd, "get-default")
        self.assertFalse(default_args.write_capable)
        self.assertIs(default_args.func, branches.cmd_branches_get_default)

        get_args = parser.parse_args(["branches", "get", "--branch-id", "branch-1"])
        self.assertEqual(get_args.branches_cmd, "get")
        self.assertFalse(get_args.write_capable)
        self.assertIs(get_args.func, branches.cmd_branches_get)

        query_args = parser.parse_args(["branches", "query", "--query-json", '{"query":{}}'])
        self.assertEqual(query_args.branches_cmd, "query")
        self.assertFalse(query_args.write_capable)
        self.assertIs(query_args.func, branches.cmd_branches_query)


class TestBranchesCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    @patch("wix_safe_agent_cli.commands.branches.HttpClient")
    def test_get_default_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"branch": {"id": "default"}})
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = branches.cmd_branches_get_default(SimpleNamespace(), ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "branches.get-default")
        self.assertEqual(payload["request"]["path"], "/branches/v1/branches/default")

    @patch("wix_safe_agent_cli.commands.branches.HttpClient")
    def test_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"branch": {"id": "branch-1"}})
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = branches.cmd_branches_get(SimpleNamespace(branch_id="branch-1"), ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "branches.get")
        self.assertEqual(payload["request"]["path"], "/branches/v1/branches/branch-1")

    @patch("wix_safe_agent_cli.commands.branches.HttpClient")
    def test_query_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"branches": []})
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = branches.cmd_branches_query(SimpleNamespace(query_json='{"query":{}}'), ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "branches.query")
        self.assertEqual(payload["request"]["path"], "/branches/v1/branches/query")
        self.assertEqual(payload["request"]["body"], {"query": {}})

    @patch("wix_safe_agent_cli.commands.branches.HttpClient")
    def test_get_rejects_empty_branch_id_and_query_rejects_non_object(self, mock_client: unittest.mock.MagicMock) -> None:
        ctx = self._ctx()

        get_buf = io.StringIO()
        with redirect_stdout(get_buf):
            get_rc = branches.cmd_branches_get(SimpleNamespace(branch_id=" "), ctx)
        get_payload = json.loads(get_buf.getvalue())
        self.assertEqual(get_rc, 1)
        self.assertFalse(get_payload["ok"])
        self.assertIn("branch-id", get_payload["error"])

        query_buf = io.StringIO()
        with redirect_stdout(query_buf):
            query_rc = branches.cmd_branches_query(SimpleNamespace(query_json="[]"), ctx)
        query_payload = json.loads(query_buf.getvalue())
        self.assertEqual(query_rc, 1)
        self.assertFalse(query_payload["ok"])
        self.assertIn("JSON object", query_payload["error"])

        self.assertEqual(mock_client.return_value.request.call_count, 0)
