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
from wix_safe_agent_cli.commands import blog_draft_posts
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBlogDraftPostsCommands(unittest.TestCase):
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
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli blog-draft-posts",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.blog_draft_posts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_draft_posts.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"draftPosts": []})

        cases = [
            (blog_draft_posts.cmd_blog_draft_posts_get, SimpleNamespace(draft_post_id="draft-1", params_json="{}"), "GET", "/blog/v3/draft-posts/draft-1", {}, None),
            (blog_draft_posts.cmd_blog_draft_posts_query, SimpleNamespace(query_json='{"query":{"paging":{"limit":10}}}'), "POST", "/blog/v3/draft-posts/query", None, {"query": {"paging": {"limit": 10}}}),
            (blog_draft_posts.cmd_blog_draft_posts_list, SimpleNamespace(params_json='{"paging.limit":10}'), "GET", "/blog/v3/draft-posts", {"paging.limit": 10}, None),
            (blog_draft_posts.cmd_blog_draft_posts_get_deleted, SimpleNamespace(draft_post_id="draft-1", params_json="{}"), "GET", "/blog/v3/draft-posts/trash-bin/draft-1", {}, None),
            (blog_draft_posts.cmd_blog_draft_posts_list_deleted, SimpleNamespace(params_json='{"paging.limit":5}'), "GET", "/blog/v3/draft-posts/trash-bin", {"paging.limit": 5}, None),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "blog-draft-posts")

    @patch("wix_safe_agent_cli.commands.blog_draft_posts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_draft_posts.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (blog_draft_posts.cmd_blog_draft_posts_create, SimpleNamespace(draft_post_json='{"draftPost":{"title":"Draft"}}'), "POST", "/blog/v3/draft-posts"),
            (blog_draft_posts.cmd_blog_draft_posts_update, SimpleNamespace(draft_post_id="draft-1", draft_post_json='{"draftPost":{"title":"Updated"}}'), "PATCH", "/blog/v3/draft-posts/draft-1"),
            (blog_draft_posts.cmd_blog_draft_posts_delete, SimpleNamespace(draft_post_id="draft-1", permanent=False), "DELETE", "/blog/v3/draft-posts/draft-1"),
            (blog_draft_posts.cmd_blog_draft_posts_bulk_create, SimpleNamespace(draft_posts_json='{"draftPosts":[{"title":"A"}]}'), "POST", "/blog/v3/bulk/draft-posts/create"),
            (blog_draft_posts.cmd_blog_draft_posts_bulk_update, SimpleNamespace(draft_posts_json='{"draftPosts":[{"id":"draft-1","title":"B"}]}'), "PATCH", "/blog/v3/draft-posts/update"),
            (blog_draft_posts.cmd_blog_draft_posts_bulk_delete, SimpleNamespace(draft_posts_json='{"draftPostIds":["draft-1"]}'), "DELETE", "/blog/v3/bulk/draft-posts"),
            (blog_draft_posts.cmd_blog_draft_posts_publish, SimpleNamespace(draft_post_id="draft-1", publish_json="{}"), "POST", "/blog/v3/draft-posts/draft-1/publish"),
            (blog_draft_posts.cmd_blog_draft_posts_remove_from_trash_bin, SimpleNamespace(draft_post_id="draft-1"), "DELETE", "/blog/v3/draft-posts/trash-bin/draft-1"),
            (blog_draft_posts.cmd_blog_draft_posts_restore_from_trash_bin, SimpleNamespace(draft_post_id="draft-1", restore_json="{}"), "POST", "/blog/v3/draft-posts/trash-bin/draft-1/restore"),
        ]
        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.blog_draft_posts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_draft_posts.HttpClient")
    def test_permanent_delete_plans_permanent_query_param_and_requires_ack_for_apply(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = blog_draft_posts.cmd_blog_draft_posts_delete(
                SimpleNamespace(draft_post_id="draft-1", permanent=True),
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["params"], {"permanent": True})
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.blog_draft_posts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_draft_posts.HttpClient")
    def test_broad_or_irreversible_deletes_require_ack_for_apply(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (blog_draft_posts.cmd_blog_draft_posts_bulk_delete, SimpleNamespace(draft_posts_json='{"draftPostIds":["draft-1"]}')),
            (blog_draft_posts.cmd_blog_draft_posts_remove_from_trash_bin, SimpleNamespace(draft_post_id="draft-1")),
        ]
        for func, args in cases:
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"))
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.blog_draft_posts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_draft_posts.HttpClient")
    def test_reviewed_plan_apply_sends_request_and_emits_receipt(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"draftPost": {"id": "draft-1"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = str(Path(tmp) / "plan.json")
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = blog_draft_posts.cmd_blog_draft_posts_create(
                    SimpleNamespace(draft_post_json='{"draftPost":{"title":"Draft"}}'),
                    self._ctx(plan_out=plan_path),
                )
            self.assertEqual(dry_rc, 0)
            self.assertTrue(Path(plan_path).exists())
            mock_client.return_value.request.assert_not_called()

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = blog_draft_posts.cmd_blog_draft_posts_create(
                    SimpleNamespace(draft_post_json='{"draftPost":{"title":"Draft"}}'),
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
            payload = json.loads(apply_buf.getvalue())
            self.assertEqual(apply_rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["request"]["path"], "/blog/v3/draft-posts")
            self.assertEqual(payload["receipt"]["response"], {"draftPost": {"id": "draft-1"}})

        mock_client.return_value.request.assert_called_once()
        call = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(call["method"], "POST")
        self.assertTrue(str(call["url"]).endswith("/blog/v3/draft-posts"))
        self.assertEqual(call["json_body"], {"draftPost": {"title": "Draft"}})

    @patch("wix_safe_agent_cli.commands.blog_draft_posts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_draft_posts.HttpClient")
    def test_query_json_must_be_an_object(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = blog_draft_posts.cmd_blog_draft_posts_query(SimpleNamespace(query_json="[]"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("--query-json must be a JSON object", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_blog_draft_posts_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["blog-draft-posts", "get", "--draft-post-id", "draft-1"], blog_draft_posts.cmd_blog_draft_posts_get, False),
            (["blog-draft-posts", "query"], blog_draft_posts.cmd_blog_draft_posts_query, False),
            (["blog-draft-posts", "list"], blog_draft_posts.cmd_blog_draft_posts_list, False),
            (["blog-draft-posts", "get-deleted", "--draft-post-id", "draft-1"], blog_draft_posts.cmd_blog_draft_posts_get_deleted, False),
            (["blog-draft-posts", "list-deleted"], blog_draft_posts.cmd_blog_draft_posts_list_deleted, False),
            (["blog-draft-posts", "create", "--draft-post-json", "{}"], blog_draft_posts.cmd_blog_draft_posts_create, True),
            (["blog-draft-posts", "update", "--draft-post-id", "draft-1", "--draft-post-json", "{}"], blog_draft_posts.cmd_blog_draft_posts_update, True),
            (["blog-draft-posts", "delete", "--draft-post-id", "draft-1"], blog_draft_posts.cmd_blog_draft_posts_delete, True),
            (["blog-draft-posts", "delete", "--draft-post-id", "draft-1", "--permanent"], blog_draft_posts.cmd_blog_draft_posts_delete, True),
            (["blog-draft-posts", "bulk-create", "--draft-posts-json", "{}"], blog_draft_posts.cmd_blog_draft_posts_bulk_create, True),
            (["blog-draft-posts", "bulk-update", "--draft-posts-json", "{}"], blog_draft_posts.cmd_blog_draft_posts_bulk_update, True),
            (["blog-draft-posts", "bulk-delete", "--draft-posts-json", "{}"], blog_draft_posts.cmd_blog_draft_posts_bulk_delete, True),
            (["blog-draft-posts", "publish", "--draft-post-id", "draft-1"], blog_draft_posts.cmd_blog_draft_posts_publish, True),
            (["blog-draft-posts", "remove-from-trash-bin", "--draft-post-id", "draft-1"], blog_draft_posts.cmd_blog_draft_posts_remove_from_trash_bin, True),
            (["blog-draft-posts", "restore-from-trash-bin", "--draft-post-id", "draft-1"], blog_draft_posts.cmd_blog_draft_posts_restore_from_trash_bin, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
