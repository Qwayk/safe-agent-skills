from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import blog_posts_stats
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBlogPostsStatsCommands(unittest.TestCase):
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
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli blog-posts-stats",
        }

    @patch("wix_safe_agent_cli.commands.blog_posts_stats.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_posts_stats.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"posts": []})

        cases = [
            (blog_posts_stats.cmd_blog_posts_stats_get, SimpleNamespace(post_id="post-1", params_json="{}"), "GET", "/v3/posts/post-1", None, None),
            (blog_posts_stats.cmd_blog_posts_stats_query, SimpleNamespace(query_json='{"query":{"paging":{"limit":10}}}'), "POST", "/v3/posts/query", None, {"query": {"paging": {"limit": 10}}}),
            (blog_posts_stats.cmd_blog_posts_stats_list, SimpleNamespace(params_json='{"paging.limit":10}'), "GET", "/v3/posts", {"paging.limit": 10}, None),
            (blog_posts_stats.cmd_blog_posts_stats_get_by_slug, SimpleNamespace(slug="hello-world", params_json="{}"), "GET", "/v3/posts/slugs/hello-world", {}, None),
            (blog_posts_stats.cmd_blog_posts_stats_get_metrics, SimpleNamespace(post_id="post-1", params_json="{}"), "GET", "/v3/posts/post-1/metrics", {}, None),
            (blog_posts_stats.cmd_blog_posts_stats_get_total, SimpleNamespace(params_json="{}"), "GET", "/blog/v2/stats/posts/total", {}, None),
            (blog_posts_stats.cmd_blog_posts_stats_query_count, SimpleNamespace(params_json='{"rangeStart":"2026-01-01","months":3}'), "GET", "/blog/v2/stats/post/count", {"rangeStart": "2026-01-01", "months": 3}, None),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "blog-posts-stats")

    @patch("wix_safe_agent_cli.commands.blog_posts_stats.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_posts_stats.HttpClient")
    def test_query_json_must_be_an_object(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = blog_posts_stats.cmd_blog_posts_stats_query(SimpleNamespace(query_json="[]"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("--query-json must be a JSON object", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_blog_posts_stats_commands_as_reads(self) -> None:
        parser = build_parser()
        cases = [
            (["blog-posts-stats", "get", "--post-id", "post-1"], blog_posts_stats.cmd_blog_posts_stats_get),
            (["blog-posts-stats", "query"], blog_posts_stats.cmd_blog_posts_stats_query),
            (["blog-posts-stats", "list"], blog_posts_stats.cmd_blog_posts_stats_list),
            (["blog-posts-stats", "get-by-slug", "--slug", "hello-world"], blog_posts_stats.cmd_blog_posts_stats_get_by_slug),
            (["blog-posts-stats", "get-metrics", "--post-id", "post-1"], blog_posts_stats.cmd_blog_posts_stats_get_metrics),
            (["blog-posts-stats", "get-total"], blog_posts_stats.cmd_blog_posts_stats_get_total),
            (["blog-posts-stats", "query-count"], blog_posts_stats.cmd_blog_posts_stats_query_count),
        ]
        for argv, func in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertFalse(args.write_capable)
