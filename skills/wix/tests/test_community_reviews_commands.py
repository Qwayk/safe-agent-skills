from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_reviews
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityReviewsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli community-reviews",
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

    def test_parser_exposes_community_reviews_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["community-reviews", "get", "--review-id", "review-1"], "get", False),
            (["community-reviews", "query"], "query", False),
            (["community-reviews", "count"], "count", False),
            (["community-reviews", "create", "--review-json", '{"review":{"namespace":"stores"}}'], "create", True),
            (
                ["community-reviews", "update", "--review-id", "review-1", "--review-json", '{"review":{"revision":"1"}}'],
                "update",
                True,
            ),
            (["community-reviews", "delete", "--review-id", "review-1"], "delete", True),
            (
                ["community-reviews", "bulk-create", "--request-json", '{"reviews":[{"namespace":"stores"}]}'],
                "bulk-create",
                True,
            ),
            (
                ["community-reviews", "bulk-delete", "--filter-json", '{"filter":{"namespace":"stores"}}'],
                "bulk-delete",
                True,
            ),
            (["community-reviews", "remove-reply", "--review-id", "review-1"], "remove-reply", True),
            (
                ["community-reviews", "set-reply", "--review-id", "review-1", "--message", "Thanks"],
                "set-reply",
                True,
            ),
            (
                ["community-reviews", "update-moderation-status", "--review-id", "review-1", "--status", "APPROVED"],
                "update-moderation-status",
                True,
            ),
            (
                ["community-reviews", "bulk-update-moderation-status", "--request-json", '{"filter":{},"status":"REJECTED"}'],
                "bulk-update-moderation-status",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_reviews_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths_and_bodies(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"reviews": []})
        cases = [
            (
                community_reviews.cmd_community_reviews_get,
                SimpleNamespace(review_id="review-1", params_json='{"returnPrivateReviews":true}'),
                "GET",
                "/reviews/v1/reviews/review-1",
                {"returnPrivateReviews": True},
                None,
            ),
            (
                community_reviews.cmd_community_reviews_query,
                SimpleNamespace(request_json='{"query":{"filter":{"namespace":"stores"}}}'),
                "POST",
                "/reviews/v1/reviews/query",
                None,
                {"query": {"filter": {"namespace": "stores"}}},
            ),
            (
                community_reviews.cmd_community_reviews_count,
                SimpleNamespace(request_json='{"filter":{"namespace":"stores"}}'),
                "POST",
                "/reviews/v1/reviews/count",
                None,
                {"filter": {"namespace": "stores"}},
            ),
        ]
        for func, args, method, path, params, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if params is not None:
                    self.assertEqual(payload["request"]["params"], params)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_with_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                community_reviews.cmd_community_reviews_create,
                SimpleNamespace(review_json='{"review":{"namespace":"stores","entityId":"product-1"}}'),
                "POST",
                "/reviews/v1/reviews",
                False,
            ),
            (
                community_reviews.cmd_community_reviews_update,
                SimpleNamespace(review_id="review-1", review_json='{"review":{"revision":"1","content":{"title":"Edit"}}}'),
                "PATCH",
                "/reviews/v1/reviews/review-1",
                False,
            ),
            (
                community_reviews.cmd_community_reviews_delete,
                SimpleNamespace(review_id="review-1"),
                "DELETE",
                "/reviews/v1/reviews/review-1",
                True,
            ),
            (
                community_reviews.cmd_community_reviews_bulk_create,
                SimpleNamespace(request_json='{"reviews":[{"namespace":"stores"}]}'),
                "POST",
                "/reviews/v1/bulk/reviews/create",
                True,
            ),
            (
                community_reviews.cmd_community_reviews_bulk_delete,
                SimpleNamespace(filter_json='{"filter":{"namespace":"stores"}}'),
                "POST",
                "/reviews/v1/bulk/reviews/delete",
                True,
            ),
            (
                community_reviews.cmd_community_reviews_remove_reply,
                SimpleNamespace(review_id="review-1"),
                "DELETE",
                "/reviews/v1/reviews/review-1/reply",
                True,
            ),
            (
                community_reviews.cmd_community_reviews_set_reply,
                SimpleNamespace(review_id="review-1", message="Thanks"),
                "PATCH",
                "/reviews/v1/reviews/review-1/reply",
                False,
            ),
            (
                community_reviews.cmd_community_reviews_update_moderation_status,
                SimpleNamespace(review_id="review-1", status="APPROVED"),
                "PATCH",
                "/reviews/v1/reviews/review-1/moderate",
                True,
            ),
            (
                community_reviews.cmd_community_reviews_bulk_update_moderation_status,
                SimpleNamespace(request_json='{"filter":{"namespace":"stores"},"status":"REJECTED"}'),
                "POST",
                "/reviews/v1/bulk/reviews/moderate",
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
            rc = community_reviews.cmd_community_reviews_create(SimpleNamespace(review_json="{}"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
