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
from wix_safe_agent_cli.commands import multilingual_translation_contents
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


class TestMultilingualTranslationContentsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli multilingual-translation-contents",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_translation_content_commands(self) -> None:
        parser = build_parser()
        content = '{"schemaId":"schema-1","entityId":"entity-1","locale":"fr-FR","fields":{"title":{"value":"Bonjour"}}}'
        cases = [
            (["multilingual-translation-contents", "create", "--content-json", content], "create", True),
            (["multilingual-translation-contents", "get", "--content-id", "content-1"], "get", False),
            (["multilingual-translation-contents", "update", "--content-json", '{"id":"content-1","schemaId":"schema-1"}'], "update", True),
            (["multilingual-translation-contents", "delete", "--content-id", "content-1"], "delete", True),
            (["multilingual-translation-contents", "query"], "query", False),
            (["multilingual-translation-contents", "search"], "search", False),
            (["multilingual-translation-contents", "bulk-create", "--contents-json", f"[{content}]"], "bulk-create", True),
            (["multilingual-translation-contents", "bulk-delete", "--content-ids-json", '["content-1"]'], "bulk-delete", True),
            (["multilingual-translation-contents", "bulk-update", "--contents-json", '[{"content":{"id":"content-1","schemaId":"schema-1"}}]'], "bulk-update", True),
            (["multilingual-translation-contents", "update-by-key", "--content-json", content], "update-by-key", True),
            (["multilingual-translation-contents", "bulk-update-by-key", "--contents-json", f'[{{"content":{content}}}]'], "bulk-update-by-key", True),
        ]
        for argv, subcommand, write_capable in cases:
            parsed = parser.parse_args(argv)
            self.assertEqual(parsed.multilingual_translation_contents_cmd, subcommand)
            self.assertEqual(parsed.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.multilingual_translation_contents.HttpClient")
    def test_get_uses_official_path_and_site_auth(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"content": {"id": "content-1"}})
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_contents.cmd_multilingual_translation_contents_get(SimpleNamespace(content_id="content-1"), ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/translation-content/v1/contents/content-1")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["headers"]["Authorization"], "site-token")
        self.assertNotIn("wix-account-id", call.kwargs["headers"])

    @patch("wix_safe_agent_cli.commands.multilingual_translation_contents.HttpClient")
    def test_query_and_search_build_read_bodies(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"contents": []})
        query_args = SimpleNamespace(
            query_json='{"query":{}}',
            filter_json='{"schemaId":{"$eq":"schema-1"}}',
            sort_json='[{"fieldName":"id","order":"ASC"}]',
            cursor="cursor-1",
            limit=20,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_contents.cmd_multilingual_translation_contents_query(query_args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/translation-content/v1/contents/query")
        self.assertEqual(payload["request"]["body"]["query"]["filter"], {"schemaId": {"$eq": "schema-1"}})

        search_args = SimpleNamespace(search_json='{"search":{"expression":"bonjour"}}', cursor="cursor-2", limit=10)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_contents.cmd_multilingual_translation_contents_search(search_args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/translation-content/v1/contents/search")
        self.assertEqual(payload["request"]["body"]["search"]["cursorPaging"], {"cursor": "cursor-2", "limit": 10})

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(content_json='{"schemaId":"schema-1","entityId":"entity-1","locale":"fr-FR","fields":{"title":{"value":"Bonjour"}}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_contents.cmd_multilingual_translation_contents_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/translation-content/v1/contents")
        self.assertEqual(payload["plan"]["selector"]["entity_id"], "entity-1")

    def test_update_requires_id_and_schema_id(self) -> None:
        args = SimpleNamespace(content_json='{"id":"content-1"}', force_fields_timestamp_update=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_contents.cmd_multilingual_translation_contents_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("schemaId", payload["error"])

    def test_field_removal_requires_ack_for_apply(self) -> None:
        args = SimpleNamespace(content_json='{"id":"content-1","schemaId":"schema-1","fields":{"title":{}}}', force_fields_timestamp_update="true")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_contents.cmd_multilingual_translation_contents_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("content-field-removal", payload["plan"]["risk_reasons"])
        self.assertIn("apply requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertTrue(payload["plan"]["request"]["body"]["forceFieldsTimestampUpdate"])

    @patch("wix_safe_agent_cli.commands.multilingual_translation_contents.HttpClient")
    def test_bulk_delete_apply_with_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": []})
        args = SimpleNamespace(content_ids_json='["content-1","content-2"]')
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_contents.cmd_multilingual_translation_contents_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/translation-content/v1/bulk/contents/delete"))
        self.assertEqual(call.kwargs["json_body"], {"contentIds": ["content-1", "content-2"]})

    def test_bulk_update_by_key_validates_key_fields_and_options(self) -> None:
        args = SimpleNamespace(
            contents_json='[{"content":{"schemaId":"schema-1","entityId":"entity-1","locale":"fr-FR","fields":{"title":{"value":"Bonjour"}}}}]',
            force_fields_timestamp_update="false",
            return_entity="true",
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_contents.cmd_multilingual_translation_contents_bulk_update_by_key(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        body = payload["plan"]["request"]["body"]
        self.assertEqual(payload["plan"]["request"]["path"], "/translation-content/v1/bulk/contents/update-by-key")
        self.assertFalse(body["forceFieldsTimestampUpdate"])
        self.assertTrue(body["returnEntity"])

    def test_plan_in_mismatch_is_refused(self) -> None:
        args = SimpleNamespace(content_id="content-1")
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(
                {
                    "method": "multilingual-translation-contents.delete",
                    "baseline": {
                        "env_fingerprint": "https://other.example",
                        "selector": {"kind": "wix-multilingual-translation-content", "operation": "delete", "content_id": "content-1"},
                    },
                },
                handle,
            )
            plan_path = handle.name
        try:
            ctx = self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = multilingual_translation_contents.cmd_multilingual_translation_contents_delete(args, ctx)
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
        finally:
            Path(plan_path).unlink()


if __name__ == "__main__":
    unittest.main()
