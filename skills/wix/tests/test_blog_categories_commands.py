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
from wix_safe_agent_cli.commands import blog_categories
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBlogCategoriesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli blog-categories",
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

    @patch("wix_safe_agent_cli.commands.blog_categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_categories.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"categories": []})

        cases = [
            (blog_categories.cmd_blog_categories_get, SimpleNamespace(category_id="cat-1", params_json="{}"), "GET", "/blog/v3/categories/cat-1", {}, None),
            (blog_categories.cmd_blog_categories_query, SimpleNamespace(query_json='{"query":{"paging":{"limit":10}}}'), "POST", "/blog/v3/categories/query", None, {"query": {"paging": {"limit": 10}}}),
            (blog_categories.cmd_blog_categories_list, SimpleNamespace(params_json='{"paging.limit":10}'), "GET", "/blog/v3/categories", {"paging.limit": 10}, None),
            (blog_categories.cmd_blog_categories_get_by_slug, SimpleNamespace(slug="news", params_json="{}"), "GET", "/blog/v3/categories/slugs/news", {}, None),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "blog-categories")

    @patch("wix_safe_agent_cli.commands.blog_categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_categories.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (blog_categories.cmd_blog_categories_create, SimpleNamespace(category_json='{"category":{"label":"News"}}'), "POST", "/blog/v3/categories"),
            (blog_categories.cmd_blog_categories_update, SimpleNamespace(category_id="cat-1", category_json='{"category":{"label":"Updates"}}'), "PATCH", "/blog/v3/categories/cat-1"),
            (blog_categories.cmd_blog_categories_delete, SimpleNamespace(category_id="cat-1"), "DELETE", "/blog/v3/categories/cat-1"),
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

    @patch("wix_safe_agent_cli.commands.blog_categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_categories.HttpClient")
    def test_delete_requires_ack_for_apply(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = blog_categories.cmd_blog_categories_delete(
                SimpleNamespace(category_id="cat-1"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.blog_categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_categories.HttpClient")
    def test_reviewed_plan_apply_sends_request_and_emits_receipt(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"category": {"id": "cat-1"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = str(Path(tmp) / "plan.json")
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = blog_categories.cmd_blog_categories_create(
                    SimpleNamespace(category_json='{"category":{"label":"News"}}'),
                    self._ctx(plan_out=plan_path),
                )
            self.assertEqual(dry_rc, 0)
            self.assertTrue(Path(plan_path).exists())
            mock_client.return_value.request.assert_not_called()

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = blog_categories.cmd_blog_categories_create(
                    SimpleNamespace(category_json='{"category":{"label":"News"}}'),
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
            payload = json.loads(apply_buf.getvalue())
            self.assertEqual(apply_rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["request"]["path"], "/blog/v3/categories")
            self.assertEqual(payload["receipt"]["response"], {"category": {"id": "cat-1"}})

        mock_client.return_value.request.assert_called_once()
        call = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(call["method"], "POST")
        self.assertTrue(str(call["url"]).endswith("/blog/v3/categories"))
        self.assertEqual(call["json_body"], {"category": {"label": "News"}})

    @patch("wix_safe_agent_cli.commands.blog_categories.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_categories.HttpClient")
    def test_query_json_must_be_an_object(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = blog_categories.cmd_blog_categories_query(SimpleNamespace(query_json="[]"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("--query-json must be a JSON object", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_blog_categories_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["blog-categories", "create", "--category-json", "{}"], blog_categories.cmd_blog_categories_create, True),
            (["blog-categories", "get", "--category-id", "cat-1"], blog_categories.cmd_blog_categories_get, False),
            (["blog-categories", "update", "--category-id", "cat-1", "--category-json", "{}"], blog_categories.cmd_blog_categories_update, True),
            (["blog-categories", "delete", "--category-id", "cat-1"], blog_categories.cmd_blog_categories_delete, True),
            (["blog-categories", "query"], blog_categories.cmd_blog_categories_query, False),
            (["blog-categories", "list"], blog_categories.cmd_blog_categories_list, False),
            (["blog-categories", "get-by-slug", "--slug", "news"], blog_categories.cmd_blog_categories_get_by_slug, False),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
