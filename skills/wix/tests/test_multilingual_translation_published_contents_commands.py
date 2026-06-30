from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import multilingual_translation_published_contents
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMultilingualTranslationPublishedContentsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-token",
            api_key=None,
            account_id=None,
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
            "command_str": "wix-safe-agent-cli multilingual-translation-published-contents",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_query(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "multilingual-translation-published-contents",
                "query",
                "--filter-json",
                '{"schemaKey.appId":{"$eq":"app-1"},"schemaKey.entityType":{"$eq":"post"},"schemaKey.scope":{"$eq":"SITE"}}',
            ]
        )
        self.assertEqual(parsed.multilingual_translation_published_contents_cmd, "query")
        self.assertFalse(parsed.write_capable)

    def test_query_requires_schema_key_filter_fields(self) -> None:
        args = SimpleNamespace(query_json=None, filter_json='{"schemaKey.appId":{"$eq":"app-1"}}', sort_json=None, cursor=None, limit=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_published_contents.cmd_multilingual_translation_published_contents_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("schemaKey.appId", payload["error"])

    @patch("wix_safe_agent_cli.commands.multilingual_translation_published_contents.HttpClient")
    def test_query_uses_official_path_body_and_site_auth(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"publishedContents": []})
        args = SimpleNamespace(
            query_json='{"query":{}}',
            filter_json='{"schemaKey.appId":{"$eq":"app-1"},"schemaKey.entityType":{"$eq":"post"},"schemaKey.scope":{"$eq":"SITE"}}',
            sort_json='[{"fieldName":"id","order":"ASC"}]',
            cursor="cursor-1",
            limit=20,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_published_contents.cmd_multilingual_translation_published_contents_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/translation-published-content/v3/published-contents/query")
        self.assertEqual(payload["request"]["body"]["query"]["cursorPaging"], {"cursor": "cursor-1", "limit": 20})
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertEqual(call.kwargs["headers"]["Authorization"], "site-token")
        self.assertNotIn("wix-account-id", call.kwargs["headers"])

    @patch("wix_safe_agent_cli.commands.multilingual_translation_published_contents.HttpClient")
    def test_nested_schema_key_filter_is_accepted(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"publishedContents": []})
        args = SimpleNamespace(
            query_json=None,
            filter_json='{"schemaKey":{"appId":{"$eq":"app-1"},"entityType":{"$eq":"post"},"scope":{"$eq":"SITE"}}}',
            sort_json=None,
            cursor=None,
            limit=None,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_published_contents.cmd_multilingual_translation_published_contents_query(args, self._ctx())
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
