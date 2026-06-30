from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import site_urls
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict | list) -> None:
        self._payload = payload

    def json(self):
        return self._payload


class TestSiteUrlsCommands(TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
            api_key=None,
            account_id=None,
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        if cfg_override:
            for key, value in cfg_override.items():
                setattr(cfg, key, value)

        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "apply": False,
            "yes": False,
            "verbose": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli site-urls",
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_site_urls_get_editor_urls(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["site-urls", "get-editor-urls"])

        self.assertEqual(parsed.site_urls_cmd, "get-editor-urls")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_site_urls_get_editor_urls")

    def test_parser_recognizes_site_urls_list_published_site_urls(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["site-urls", "list-published-site-urls"])

        self.assertEqual(parsed.site_urls_cmd, "list-published-site-urls")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_site_urls_list_published_site_urls")

    @patch("wix_safe_agent_cli.commands.site_urls.HttpClient")
    def test_site_urls_get_editor_urls_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"editorUrl": "https://editor.wix.com/site-123"})

        args = SimpleNamespace(field_path=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_urls.cmd_site_urls_get_editor_urls(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "site-urls.get-editor-urls")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/editor-urls/v2/editor-urls")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(call.kwargs["url"].endswith("/editor-urls/v2/editor-urls"))
        headers = call.kwargs["headers"]
        self.assertEqual(headers, {"Authorization": "site-app-token"})

    @patch("wix_safe_agent_cli.commands.site_urls.HttpClient")
    def test_site_urls_list_published_site_urls_returns_empty_array_when_unpublished(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse([])

        args = SimpleNamespace()
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_urls.cmd_site_urls_list_published_site_urls(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "site-urls.list-published-site-urls")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/urls-server/v2/published-site-urls")
        self.assertEqual(payload["response"], [])

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(call.kwargs["url"].endswith("/urls-server/v2/published-site-urls"))
        headers = call.kwargs["headers"]
        self.assertEqual(headers, {"Authorization": "site-app-token"})
