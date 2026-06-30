from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import editor_deep_link
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEditorDeepLinkCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
            api_key=None,
            account_id=None,
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    def test_parser_recognizes_editor_deep_link_create(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["editor-deep-link", "create", "--custom-params-json", '{"leadFormId":"abc"}'])

        self.assertEqual(parsed.editor_deep_link_cmd, "create")
        self.assertFalse(parsed.write_capable)
        self.assertIs(parsed.func, editor_deep_link.cmd_editor_deep_link_create)

    @patch("wix_safe_agent_cli.commands.editor_deep_link.HttpClient")
    def test_create_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"url": "https://editor.example/deep-link"})
        args = SimpleNamespace(custom_params_json='{"leadFormId":"abc"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = editor_deep_link.cmd_editor_deep_link_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/apps/v1/post-installation/editor-deep-link")
        self.assertEqual(payload["request"]["body"], {"customParams": {"leadFormId": "abc"}})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertEqual(call.kwargs["json_body"], {"customParams": {"leadFormId": "abc"}})

    @patch("wix_safe_agent_cli.commands.editor_deep_link.HttpClient")
    def test_create_allows_empty_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"url": "https://editor.example/open"})
        args = SimpleNamespace(custom_params_json=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = editor_deep_link.cmd_editor_deep_link_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["body"], {})

    @patch("wix_safe_agent_cli.commands.editor_deep_link.HttpClient")
    def test_create_rejects_non_string_custom_param_value(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(custom_params_json='{"leadFormId":123}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = editor_deep_link.cmd_editor_deep_link_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--custom-params-json values must be strings", payload["error"])
