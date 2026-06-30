from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import rich_content_ricos
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRichContentRicosCommands(unittest.TestCase):
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
        }

    @patch("wix_safe_agent_cli.commands.rich_content_ricos.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.rich_content_ricos.HttpClient")
    def test_rich_content_ricos_helpers_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})

        cases = [
            (
                rich_content_ricos.cmd_rich_content_ricos_convert_from,
                SimpleNamespace(convert_json='{"document":{"nodes":[]},"targetFormat":"MARKDOWN"}'),
                "rich-content-ricos.convert-from",
                "/ricos/v1/ricos-document/convert/from-ricos",
            ),
            (
                rich_content_ricos.cmd_rich_content_ricos_convert_to,
                SimpleNamespace(convert_json='{"markdown":"# Hello","options":{"plugins":["HEADING"]}}'),
                "rich-content-ricos.convert-to",
                "/ricos/v1/ricos-document/convert/to-ricos",
            ),
            (
                rich_content_ricos.cmd_rich_content_ricos_validate,
                SimpleNamespace(validate_json='{"document":{"nodes":[]},"plugins":["TEXT_COLOR"],"fixDocument":true}'),
                "rich-content-ricos.validate",
                "/ricos/v1/ricos-document/validate",
            ),
        ]
        for func, args, method, path in cases:
            with self.subTest(method=method):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())

                self.assertEqual(rc, 0)
                self.assertEqual(payload["method"], method)
                self.assertEqual(payload["request"]["method"], "POST")
                self.assertEqual(payload["request"]["path"], path)
                self.assertEqual(payload["auth_mode"], "access_token")

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "rich-content-ricos")

    def test_invalid_json_is_rejected(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = rich_content_ricos.cmd_rich_content_ricos_validate(SimpleNamespace(validate_json="[]"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("JSON object", payload["error"])

    def test_parser_includes_rich_content_ricos_commands(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["rich-content-ricos", "validate", "--validate-json", '{"document":{"nodes":[]}}'])
        self.assertFalse(parsed.write_capable)
        self.assertIs(parsed.func, rich_content_ricos.cmd_rich_content_ricos_validate)
