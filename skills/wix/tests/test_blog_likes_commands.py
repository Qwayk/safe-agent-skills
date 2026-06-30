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
from wix_safe_agent_cli.commands import blog_likes
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBlogLikesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli blog-likes",
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

    @patch("wix_safe_agent_cli.commands.blog_likes.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_likes.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"likes": []})

        cases = [
            (blog_likes.cmd_blog_likes_get, SimpleNamespace(like_id="like-1", params_json="{}"), "GET", "/blog/v1/likes/like-1", {}, None),
            (blog_likes.cmd_blog_likes_query, SimpleNamespace(query_json='{"query":{"paging":{"limit":10}}}'), "POST", "/blog/v1/likes/query", None, {"query": {"paging": {"limit": 10}}}),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "blog-likes")

    @patch("wix_safe_agent_cli.commands.blog_likes.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_likes.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (blog_likes.cmd_blog_likes_create, SimpleNamespace(like_json='{"like":{"fqdn":"wix.blog.v3.post","entityId":"post-1"}}'), "POST", "/blog/v1/likes"),
            (blog_likes.cmd_blog_likes_delete, SimpleNamespace(like_id="like-1"), "DELETE", "/blog/v1/likes/like-1"),
            (blog_likes.cmd_blog_likes_delete_by_fqdn_entity_id, SimpleNamespace(fqdn="wix.blog.v3.post", entity_id="post-1"), "DELETE", "/blog/v1/likes/fqdn/wix.blog.v3.post/entity-id/post-1"),
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

    @patch("wix_safe_agent_cli.commands.blog_likes.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_likes.HttpClient")
    def test_delete_commands_require_ack_for_apply(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (blog_likes.cmd_blog_likes_delete, SimpleNamespace(like_id="like-1")),
            (blog_likes.cmd_blog_likes_delete_by_fqdn_entity_id, SimpleNamespace(fqdn="wix.blog.v3.post", entity_id="post-1")),
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

    @patch("wix_safe_agent_cli.commands.blog_likes.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_likes.HttpClient")
    def test_reviewed_plan_apply_sends_request_and_emits_receipt(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"like": {"id": "like-1"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = str(Path(tmp) / "plan.json")
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = blog_likes.cmd_blog_likes_create(
                    SimpleNamespace(like_json='{"like":{"fqdn":"wix.blog.v3.post","entityId":"post-1"}}'),
                    self._ctx(plan_out=plan_path),
                )
            self.assertEqual(dry_rc, 0)
            self.assertTrue(Path(plan_path).exists())
            mock_client.return_value.request.assert_not_called()

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = blog_likes.cmd_blog_likes_create(
                    SimpleNamespace(like_json='{"like":{"fqdn":"wix.blog.v3.post","entityId":"post-1"}}'),
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
            payload = json.loads(apply_buf.getvalue())
            self.assertEqual(apply_rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["request"]["path"], "/blog/v1/likes")
            self.assertEqual(payload["receipt"]["response"], {"like": {"id": "like-1"}})

        mock_client.return_value.request.assert_called_once()
        call = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(call["method"], "POST")
        self.assertTrue(str(call["url"]).endswith("/blog/v1/likes"))
        self.assertEqual(call["json_body"], {"like": {"fqdn": "wix.blog.v3.post", "entityId": "post-1"}})

    @patch("wix_safe_agent_cli.commands.blog_likes.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_likes.HttpClient")
    def test_query_json_must_be_an_object(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = blog_likes.cmd_blog_likes_query(SimpleNamespace(query_json="[]"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("--query-json must be a JSON object", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_blog_likes_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["blog-likes", "get", "--like-id", "like-1"], blog_likes.cmd_blog_likes_get, False),
            (["blog-likes", "delete", "--like-id", "like-1"], blog_likes.cmd_blog_likes_delete, True),
            (["blog-likes", "query"], blog_likes.cmd_blog_likes_query, False),
            (["blog-likes", "create", "--like-json", "{}"], blog_likes.cmd_blog_likes_create, True),
            (["blog-likes", "delete-by-fqdn-entity-id", "--fqdn", "wix.blog.v3.post", "--entity-id", "post-1"], blog_likes.cmd_blog_likes_delete_by_fqdn_entity_id, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
