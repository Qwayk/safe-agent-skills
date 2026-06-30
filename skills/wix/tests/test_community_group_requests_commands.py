from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_group_requests
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityGroupRequestsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli community-group-requests",
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

    def test_parser_exposes_community_group_requests_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["community-group-requests", "list"], "list", False),
            (["community-group-requests", "query", "--query-json", '{"filter":{"status":"PENDING"}}'], "query", False),
            (["community-group-requests", "approve", "--request-json", '{"requestIds":["request-1"]}'], "approve", True),
            (["community-group-requests", "reject", "--request-json", '{"requestIds":["request-1"]}'], "reject", True),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_group_requests_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_list_uses_official_path_and_params(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"groupRequests": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_requests.cmd_community_group_requests_list(
                SimpleNamespace(params_json='{"paging.limit":50}'),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertTrue(
            mock_client.return_value.request.call_args.kwargs["url"].endswith(
                "/_api/social-groups-proxy/group-requests/v2/group-requests"
            )
        )
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], {"paging.limit": 50})

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_query_uses_official_path_and_wraps_query(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"groupRequests": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_requests.cmd_community_group_requests_query(
                SimpleNamespace(query_json='{"filter":{"status":"PENDING"}}'),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "POST")
        self.assertTrue(
            mock_client.return_value.request.call_args.kwargs["url"].endswith(
                "/_api/social-groups-proxy/group-requests/v2/group-requests/query"
            )
        )
        self.assertEqual(
            mock_client.return_value.request.call_args.kwargs["json_body"],
            {"query": {"filter": {"status": "PENDING"}}},
        )

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_approve_is_plan_first_and_requires_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_requests.cmd_community_group_requests_approve(
                SimpleNamespace(request_json='{"requestIds":["request-1"]}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/_api/social-groups-proxy/group-requests/v2/group-requests/approve",
        )
        self.assertIn("approve-community-group-create-requests", payload["plan"]["risk_reasons"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_reject_is_plan_first_and_requires_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_requests.cmd_community_group_requests_reject(
                SimpleNamespace(request_json='{"requestIds":["request-1"]}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/_api/social-groups-proxy/group-requests/v2/group-requests/reject",
        )
        self.assertIn("reject-community-group-create-requests", payload["plan"]["risk_reasons"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_decision_request_json_must_be_non_empty(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_requests.cmd_community_group_requests_approve(
                SimpleNamespace(request_json="{}"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
