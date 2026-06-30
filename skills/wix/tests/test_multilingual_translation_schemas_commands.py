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
from wix_safe_agent_cli.commands import multilingual_translation_schemas
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


class TestMultilingualTranslationSchemasCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli multilingual-translation-schemas",
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

    def test_parser_recognizes_translation_schema_commands(self) -> None:
        parser = build_parser()
        cases = [
            (
                [
                    "multilingual-translation-schemas",
                    "create",
                    "--schema-json",
                    '{"key":{"entityType":"post","scope":"SITE"},"fields":{"title":{"type":"SHORT_TEXT"}}}',
                ],
                "create",
                True,
            ),
            (["multilingual-translation-schemas", "get", "--schema-id", "schema-1"], "get", False),
            (["multilingual-translation-schemas", "update", "--schema-json", '{"id":"schema-1","revision":"1"}'], "update", True),
            (["multilingual-translation-schemas", "delete", "--schema-id", "schema-1"], "delete", True),
            (["multilingual-translation-schemas", "query"], "query", False),
            (["multilingual-translation-schemas", "list-site"], "list-site", False),
            (
                [
                    "multilingual-translation-schemas",
                    "get-by-key",
                    "--app-id",
                    "app-1",
                    "--entity-type",
                    "post",
                    "--scope",
                    "SITE",
                ],
                "get-by-key",
                False,
            ),
        ]
        for argv, subcommand, write_capable in cases:
            parsed = parser.parse_args(argv)
            self.assertEqual(parsed.multilingual_translation_schemas_cmd, subcommand)
            self.assertEqual(parsed.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.multilingual_translation_schemas.HttpClient")
    def test_get_uses_official_path_and_site_auth(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"schema": {"id": "schema-1"}})
        args = SimpleNamespace(schema_id="schema-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_schemas.cmd_multilingual_translation_schemas_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/translation-schema/v1/schemas/schema-1")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["headers"]["Authorization"], "site-token")
        self.assertNotIn("wix-account-id", call.kwargs["headers"])

    @patch("wix_safe_agent_cli.commands.multilingual_translation_schemas.HttpClient")
    def test_query_builds_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"schemas": []})
        args = SimpleNamespace(
            query_json='{"query":{}}',
            filter_json='{"key.scope":{"$eq":"SITE"}}',
            sort_json='[{"fieldName":"id","order":"ASC"}]',
            cursor="cursor-1",
            limit=20,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_schemas.cmd_multilingual_translation_schemas_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        body = payload["request"]["body"]
        self.assertEqual(body["query"]["filter"], {"key.scope": {"$eq": "SITE"}})
        self.assertEqual(body["query"]["cursorPaging"], {"cursor": "cursor-1", "limit": 20})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"], body)

    def test_create_dry_run_builds_plan(self) -> None:
        schema_json = '{"key":{"entityType":"post","scope":"SITE"},"fields":{"title":{"type":"SHORT_TEXT","displayName":"Title"}}}'
        args = SimpleNamespace(schema_json=schema_json)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_schemas.cmd_multilingual_translation_schemas_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/translation-schema/v1/schemas")
        self.assertEqual(payload["plan"]["request"]["body"]["schema"]["key"]["entityType"], "post")

    def test_update_requires_id_and_revision(self) -> None:
        args = SimpleNamespace(schema_json='{"id":"schema-1"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_schemas.cmd_multilingual_translation_schemas_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("revision", payload["error"])

    def test_update_field_removal_requires_ack_for_apply(self) -> None:
        args = SimpleNamespace(schema_json='{"id":"schema-1","revision":"1","fields":{"title":{}}}')
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_schemas.cmd_multilingual_translation_schemas_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("schema-field-removal", payload["plan"]["risk_reasons"])
        self.assertIn("apply requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.multilingual_translation_schemas.HttpClient")
    def test_delete_apply_with_ack_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        args = SimpleNamespace(schema_id="schema-1")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_schemas.cmd_multilingual_translation_schemas_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "DELETE")
        self.assertTrue(str(call.kwargs["url"]).endswith("/translation-schema/v1/schemas/schema-1"))

    @patch("wix_safe_agent_cli.commands.multilingual_translation_schemas.HttpClient")
    def test_list_site_and_get_by_key_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"schemas": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_schemas.cmd_multilingual_translation_schemas_list_site(
                SimpleNamespace(app_id="app-1", entity_type="post", scope="SITE", cursor="cursor-1", limit=20),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/translation-schema/v1/schemas/site")
        self.assertEqual(
            mock_client.return_value.request.call_args.kwargs["params"],
            {
                "appId": "app-1",
                "entityType": "post",
                "scope": "SITE",
                "paging.cursor": "cursor-1",
                "paging.limit": 20,
            },
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_translation_schemas.cmd_multilingual_translation_schemas_get_by_key(
                SimpleNamespace(app_id="app-1", entity_type="blog post", scope="SITE"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(
            payload["request"]["path"],
            "/translation-schema/v1/schemas/app-id/app-1/entity-type/blog%20post/scope/SITE",
        )

    def test_plan_in_mismatch_is_refused(self) -> None:
        args = SimpleNamespace(schema_id="schema-1")
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(
                {
                    "method": "multilingual-translation-schemas.delete",
                    "baseline": {
                        "env_fingerprint": "https://other.example",
                        "selector": {"kind": "wix-multilingual-translation-schema", "operation": "delete", "schema_id": "schema-1"},
                    },
                },
                handle,
            )
            plan_path = handle.name
        try:
            ctx = self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = multilingual_translation_schemas.cmd_multilingual_translation_schemas_delete(args, ctx)
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
        finally:
            Path(plan_path).unlink()


if __name__ == "__main__":
    unittest.main()
