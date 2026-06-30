from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_comments
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityCommentsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli community-comments",
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

    def test_parser_exposes_community_comments_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["community-comments", "create", "--comment-json", '{"comment":{"appId":"app-1"}}'], "create", True),
            (["community-comments", "get", "--comment-id", "comment-1"], "get", False),
            (
                ["community-comments", "update", "--comment-id", "comment-1", "--comment-json", '{"comment":{"revision":"1"}}'],
                "update",
                True,
            ),
            (["community-comments", "delete", "--comment-id", "comment-1"], "delete", True),
            (
                ["community-comments", "moderate-draft-content", "--comment-id", "comment-1"],
                "moderate-draft-content",
                True,
            ),
            (["community-comments", "query"], "query", False),
            (["community-comments", "mark", "--comment-id", "comment-1"], "mark", True),
            (["community-comments", "unmark", "--comment-id", "comment-1"], "unmark", True),
            (["community-comments", "hide", "--comment-id", "comment-1"], "hide", True),
            (["community-comments", "publish", "--comment-id", "comment-1"], "publish", True),
            (["community-comments", "count"], "count", False),
            (["community-comments", "list-by-resource"], "list-by-resource", False),
            (["community-comments", "get-thread", "--comment-id", "comment-1"], "get-thread", False),
            (
                ["community-comments", "bulk-publish", "--request-json", '{"appId":"app-1","filter":{}}'],
                "bulk-publish",
                True,
            ),
            (
                ["community-comments", "bulk-hide", "--request-json", '{"appId":"app-1","filter":{}}'],
                "bulk-hide",
                True,
            ),
            (
                ["community-comments", "bulk-delete", "--request-json", '{"appId":"app-1","filter":{}}'],
                "bulk-delete",
                True,
            ),
            (
                ["community-comments", "bulk-moderate-draft-content", "--request-json", '{"appId":"app-1","filter":{}}'],
                "bulk-moderate-draft-content",
                True,
            ),
            (
                ["community-comments", "bulk-move-by-filter", "--request-json", '{"appId":"app-1","filter":{}}'],
                "bulk-move-by-filter",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_comments_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths_and_bodies(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"comments": []})
        cases = [
            (
                community_comments.cmd_community_comments_get,
                SimpleNamespace(comment_id="comment-1"),
                "GET",
                "/comments/v1/comments/comment-1",
                None,
                None,
            ),
            (
                community_comments.cmd_community_comments_query,
                SimpleNamespace(request_json='{"appId":"app-1","query":{"cursorPaging":{"limit":10}}}'),
                "POST",
                "/comments/v1/comments/query-cursor",
                None,
                {"appId": "app-1", "query": {"cursorPaging": {"limit": 10}}},
            ),
            (
                community_comments.cmd_community_comments_count,
                SimpleNamespace(request_json='{"appId":"app-1","filter":{"status":"PUBLISHED"}}'),
                "POST",
                "/comments/v1/comments/count",
                None,
                {"appId": "app-1", "filter": {"status": "PUBLISHED"}},
            ),
            (
                community_comments.cmd_community_comments_list_by_resource,
                SimpleNamespace(params_json='{"appId":"app-1","resourceId":"res-1"}'),
                "GET",
                "/comments/v1/comments/list-by-resource",
                {"appId": "app-1", "resourceId": "res-1"},
                None,
            ),
            (
                community_comments.cmd_community_comments_get_thread,
                SimpleNamespace(comment_id="comment-1", params_json='{"appId":"app-1"}'),
                "GET",
                "/comments/v1/comments/comment-1/thread",
                {"appId": "app-1"},
                None,
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
                community_comments.cmd_community_comments_create,
                SimpleNamespace(comment_json='{"comment":{"appId":"app-1","content":{"text":"hello"}}}'),
                "POST",
                "/comments/v1/comments",
                False,
            ),
            (
                community_comments.cmd_community_comments_update,
                SimpleNamespace(comment_id="comment-1", comment_json='{"comment":{"revision":"1","content":{"text":"edit"}}}'),
                "PATCH",
                "/comments/v1/comments/comment-1",
                False,
            ),
            (
                community_comments.cmd_community_comments_delete,
                SimpleNamespace(comment_id="comment-1"),
                "DELETE",
                "/comments/v1/comments/comment-1",
                True,
            ),
            (
                community_comments.cmd_community_comments_moderate_draft_content,
                SimpleNamespace(comment_id="comment-1", request_json='{"revision":"1","draftContentAction":"PUBLISH"}'),
                "POST",
                "/comments/v1/comments/comment-1/moderate",
                True,
            ),
            (
                community_comments.cmd_community_comments_mark,
                SimpleNamespace(comment_id="comment-1", request_json="{}"),
                "PUT",
                "/comments/v1/comments/comment-1/mark",
                True,
            ),
            (
                community_comments.cmd_community_comments_unmark,
                SimpleNamespace(comment_id="comment-1", request_json="{}"),
                "PUT",
                "/comments/v1/comments/comment-1/unmark",
                True,
            ),
            (
                community_comments.cmd_community_comments_hide,
                SimpleNamespace(comment_id="comment-1", request_json="{}"),
                "PUT",
                "/comments/v1/comments/comment-1/hide",
                True,
            ),
            (
                community_comments.cmd_community_comments_publish,
                SimpleNamespace(comment_id="comment-1", request_json="{}"),
                "PUT",
                "/comments/v1/comments/comment-1/publish",
                True,
            ),
            (
                community_comments.cmd_community_comments_bulk_publish,
                SimpleNamespace(request_json='{"appId":"app-1","filter":{}}'),
                "POST",
                "/comments/v1/bulk/comments/publish-by-filter",
                True,
            ),
            (
                community_comments.cmd_community_comments_bulk_hide,
                SimpleNamespace(request_json='{"appId":"app-1","filter":{}}'),
                "PUT",
                "/comments/v1/bulk/comments/hide-by-filter",
                True,
            ),
            (
                community_comments.cmd_community_comments_bulk_delete,
                SimpleNamespace(request_json='{"appId":"app-1","filter":{}}'),
                "PUT",
                "/comments/v1/bulk/comments/delete-by-filter",
                True,
            ),
            (
                community_comments.cmd_community_comments_bulk_moderate_draft_content,
                SimpleNamespace(request_json='{"appId":"app-1","filter":{},"draftContentAction":"HIDE"}'),
                "POST",
                "/comments/v1/bulk/comments/moderate-by-filter",
                True,
            ),
            (
                community_comments.cmd_community_comments_bulk_move_by_filter,
                SimpleNamespace(request_json='{"appId":"app-1","filter":{},"destination":{"resourceId":"res-2"}}'),
                "PUT",
                "/comments/v1/bulk/comments/move-by-filter",
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
            rc = community_comments.cmd_community_comments_create(SimpleNamespace(comment_json="{}"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
