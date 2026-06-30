from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import headless_sitemap
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestHeadlessSitemapCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli headless-sitemap list-pages",
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

    def test_parser_exposes_headless_sitemap_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "headless-sitemap",
                "list-pages",
                "--item-type",
                "BLOG_POST",
                "--limit",
                "50",
                "--cursor",
                "next-1",
            ]
        )

        self.assertIs(args.func, headless_sitemap.cmd_headless_sitemap_list_pages)
        self.assertFalse(args.write_capable)
        self.assertEqual(args.item_type, "BLOG_POST")
        self.assertEqual(args.limit, "50")
        self.assertEqual(args.cursor, "next-1")

    @patch("wix_safe_agent_cli.commands.headless_sitemap.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_sitemap.HttpClient")
    def test_list_pages_uses_official_path_and_cursor_params(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "pages": [
                    {
                        "id": "https://example.com/blog/post-1",
                        "shouldBeIncludedInSitemap": True,
                    }
                ],
                "pagingMetadata": {"count": 1, "cursors": {"next": None}},
            }
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_sitemap.cmd_headless_sitemap_list_pages(
                SimpleNamespace(item_type="blog_post", limit="50", cursor="next-1"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "headlessSitemap.listSitemapPages")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/v1/list-sitemap-pages")
        self.assertEqual(
            payload["request"]["params"],
            {"itemType": "BLOG_POST", "paging.limit": 50, "paging.cursor": "next-1"},
        )
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "headless-sitemap")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["url"], "https://www.wixapis.com/v1/list-sitemap-pages")
        self.assertEqual(call.kwargs["params"], {"itemType": "BLOG_POST", "paging.limit": 50, "paging.cursor": "next-1"})
        self.assertIsNone(call.kwargs["json_body"])

    def test_list_pages_rejects_invalid_item_type(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_sitemap.cmd_headless_sitemap_list_pages(
                SimpleNamespace(item_type="BAD_TYPE", limit=None, cursor=None),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--item-type must be one of", payload["error"])

    def test_list_pages_rejects_limit_above_official_maximum(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_sitemap.cmd_headless_sitemap_list_pages(
                SimpleNamespace(item_type="BLOG_POST", limit=201, cursor=None),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--limit must be between 0 and 200", payload["error"])
