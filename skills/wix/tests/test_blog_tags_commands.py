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
from wix_safe_agent_cli.commands import blog_tags
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBlogTagsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli blog-tags",
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

    @patch("wix_safe_agent_cli.commands.blog_tags.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_tags.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"tags": []})

        cases = [
            (blog_tags.cmd_blog_tags_get, SimpleNamespace(tag_id="tag-1", params_json="{}"), "GET", "/v3/tags/tag-1", {}, None),
            (blog_tags.cmd_blog_tags_query, SimpleNamespace(query_json='{"query":{"paging":{"limit":10}}}'), "POST", "/v3/tags/query", None, {"query": {"paging": {"limit": 10}}}),
            (blog_tags.cmd_blog_tags_get_by_label, SimpleNamespace(label="dessert/icecream", params_json="{}"), "GET", "/v3/tags/labels/dessert/icecream", {}, None),
            (blog_tags.cmd_blog_tags_get_by_slug, SimpleNamespace(slug="featured", params_json="{}"), "GET", "/v3/tags/slugs/featured", {}, None),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "blog-tags")

    @patch("wix_safe_agent_cli.commands.blog_tags.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_tags.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (blog_tags.cmd_blog_tags_create, SimpleNamespace(tag_json='{"tag":{"label":"Featured"}}'), "POST", "/v3/tags"),
            (blog_tags.cmd_blog_tags_delete, SimpleNamespace(tag_id="tag-1"), "DELETE", "/v3/tags/tag-1"),
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

    @patch("wix_safe_agent_cli.commands.blog_tags.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_tags.HttpClient")
    def test_delete_requires_ack_for_apply(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = blog_tags.cmd_blog_tags_delete(
                SimpleNamespace(tag_id="tag-1"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.blog_tags.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_tags.HttpClient")
    def test_reviewed_plan_apply_sends_request_and_emits_receipt(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"tag": {"id": "tag-1"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = str(Path(tmp) / "plan.json")
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = blog_tags.cmd_blog_tags_create(
                    SimpleNamespace(tag_json='{"tag":{"label":"Featured"}}'),
                    self._ctx(plan_out=plan_path),
                )
            self.assertEqual(dry_rc, 0)
            self.assertTrue(Path(plan_path).exists())
            mock_client.return_value.request.assert_not_called()

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = blog_tags.cmd_blog_tags_create(
                    SimpleNamespace(tag_json='{"tag":{"label":"Featured"}}'),
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
            payload = json.loads(apply_buf.getvalue())
            self.assertEqual(apply_rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["request"]["path"], "/v3/tags")
            self.assertEqual(payload["receipt"]["response"], {"tag": {"id": "tag-1"}})

        mock_client.return_value.request.assert_called_once()
        call = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(call["method"], "POST")
        self.assertTrue(str(call["url"]).endswith("/v3/tags"))
        self.assertEqual(call["json_body"], {"tag": {"label": "Featured"}})

    @patch("wix_safe_agent_cli.commands.blog_tags.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.blog_tags.HttpClient")
    def test_query_json_must_be_an_object(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = blog_tags.cmd_blog_tags_query(SimpleNamespace(query_json="[]"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("--query-json must be a JSON object", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_blog_tags_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["blog-tags", "get", "--tag-id", "tag-1"], blog_tags.cmd_blog_tags_get, False),
            (["blog-tags", "delete", "--tag-id", "tag-1"], blog_tags.cmd_blog_tags_delete, True),
            (["blog-tags", "query"], blog_tags.cmd_blog_tags_query, False),
            (["blog-tags", "create", "--tag-json", "{}"], blog_tags.cmd_blog_tags_create, True),
            (["blog-tags", "get-by-label", "--label", "dessert/icecream"], blog_tags.cmd_blog_tags_get_by_label, False),
            (["blog-tags", "get-by-slug", "--slug", "featured"], blog_tags.cmd_blog_tags_get_by_slug, False),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
