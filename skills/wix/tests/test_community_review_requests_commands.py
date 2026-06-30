from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_review_requests
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityReviewRequestsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli community-review-requests",
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

    def test_parser_exposes_community_review_requests_commands(self) -> None:
        parser = build_parser()
        cases = [
            (
                ["community-review-requests", "create", "--review-request-json", '{"reviewRequest":{"namespace":"stores"}}'],
                "create",
                True,
            ),
            (["community-review-requests", "get", "--review-request-id", "request-1"], "get", False),
            (["community-review-requests", "delete", "--review-request-id", "request-1"], "delete", True),
            (["community-review-requests", "query"], "query", False),
            (["community-review-requests", "count"], "count", False),
            (
                ["community-review-requests", "bulk-cancel-by-filter", "--filter-json", '{"filter":{"namespace":"stores"}}'],
                "bulk-cancel-by-filter",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_review_requests_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths_and_bodies(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"reviewRequests": []})
        cases = [
            (
                community_review_requests.cmd_community_review_requests_get,
                SimpleNamespace(review_request_id="request-1"),
                "GET",
                "/reviews/v2/review-requests/request-1",
                None,
            ),
            (
                community_review_requests.cmd_community_review_requests_query,
                SimpleNamespace(request_json='{"query":{"filter":{"namespace":"stores"}}}'),
                "POST",
                "/reviews/v2/review-requests/query",
                {"query": {"filter": {"namespace": "stores"}}},
            ),
            (
                community_review_requests.cmd_community_review_requests_count,
                SimpleNamespace(request_json='{"filter":{"namespace":"stores"}}'),
                "POST",
                "/reviews/v2/review-requests/count",
                {"filter": {"namespace": "stores"}},
            ),
        ]
        for func, args, method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_with_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                community_review_requests.cmd_community_review_requests_create,
                SimpleNamespace(review_request_json='{"reviewRequest":{"namespace":"stores","order":{"id":"order-1"}}}'),
                "POST",
                "/reviews/v2/review-requests",
                False,
            ),
            (
                community_review_requests.cmd_community_review_requests_delete,
                SimpleNamespace(review_request_id="request-1"),
                "DELETE",
                "/reviews/v2/review-requests/request-1",
                True,
            ),
            (
                community_review_requests.cmd_community_review_requests_bulk_cancel_by_filter,
                SimpleNamespace(filter_json='{"filter":{"namespace":"stores"}}'),
                "PUT",
                "/reviews/v2/bulk/review-requests/cancel-by-filter",
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
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_rejects_empty_create_body(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_review_requests.cmd_community_review_requests_create(
                SimpleNamespace(review_request_json="{}"), self._ctx()
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
