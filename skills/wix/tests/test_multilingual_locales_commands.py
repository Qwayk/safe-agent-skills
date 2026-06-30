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
from wix_safe_agent_cli.commands import multilingual_locales
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


class TestMultilingualLocalesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli multilingual-locales",
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

    def test_parser_recognizes_locales_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["multilingual-locales", "create", "--locale-json", '{"languageCode":"fr"}'], "create", True),
            (["multilingual-locales", "get", "--locale-id", "fr-FR"], "get", False),
            (["multilingual-locales", "update", "--locale-json", '{"id":"fr-FR","revision":"1"}'], "update", True),
            (["multilingual-locales", "delete", "--locale-id", "fr-FR"], "delete", True),
            (["multilingual-locales", "query"], "query", False),
            (["multilingual-locales", "bulk-create", "--locales-json", '[{"languageCode":"fr"}]'], "bulk-create", True),
            (["multilingual-locales", "bulk-delete", "--locale-ids-json", '["fr-FR"]'], "bulk-delete", True),
            (["multilingual-locales", "bulk-update", "--locales-json", '[{"locale":{"id":"fr-FR","revision":"1"}}]'], "bulk-update", True),
            (["multilingual-locales", "create-new-primary", "--primary-locale-json", '{"languageCode":"en"}'], "create-new-primary", True),
            (["multilingual-locales", "get-new-primary-status", "--token", "token-1"], "get-new-primary-status", False),
            (["multilingual-locales", "list-supported"], "list-supported", False),
            (["multilingual-locales", "set-visitor-primary", "--locale-id", "fr-FR"], "set-visitor-primary", True),
        ]
        for argv, subcommand, write_capable in cases:
            parsed = parser.parse_args(argv)
            self.assertEqual(parsed.multilingual_locales_cmd, subcommand)
            self.assertEqual(parsed.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.multilingual_locales.HttpClient")
    def test_get_uses_official_path_and_site_auth(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"locale": {"id": "fr-FR"}})
        args = SimpleNamespace(locale_id="fr-FR")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locales.cmd_multilingual_locales_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/locales/v2/locale/fr-FR")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["headers"]["Authorization"], "site-token")
        self.assertNotIn("wix-account-id", call.kwargs["headers"])

    @patch("wix_safe_agent_cli.commands.multilingual_locales.HttpClient")
    def test_query_builds_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"locales": []})
        args = SimpleNamespace(
            query_json='{"query":{}}',
            filter_json='{"visibility":{"$eq":"VISIBLE"}}',
            sort_json='[{"fieldName":"id","order":"ASC"}]',
            cursor="cursor-1",
            limit=20,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locales.cmd_multilingual_locales_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        body = payload["request"]["body"]
        self.assertEqual(body["query"]["filter"], {"visibility": {"$eq": "VISIBLE"}})
        self.assertEqual(body["query"]["cursorPaging"], {"cursor": "cursor-1", "limit": 20})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"], body)

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(locale_json='{"languageCode":"fr","regionCode":"FR","visibility":"HIDDEN"}')
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locales.cmd_multilingual_locales_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/locales/v2/locale")
        self.assertEqual(payload["plan"]["request"]["body"]["locale"]["languageCode"], "fr")

    def test_update_requires_id_and_revision(self) -> None:
        args = SimpleNamespace(locale_json='{"id":"fr-FR"}')
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locales.cmd_multilingual_locales_update(args, ctx)
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("revision", payload["error"])

    def test_delete_requires_ack_for_apply(self) -> None:
        args = SimpleNamespace(locale_id="fr-FR")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locales.cmd_multilingual_locales_delete(args, ctx)
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("irreversible", payload["plan"]["risk_reasons"])
        self.assertIn("apply requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.multilingual_locales.HttpClient")
    def test_bulk_delete_apply_with_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": [], "bulkActionMetadata": {}})
        args = SimpleNamespace(locale_ids_json='["fr-FR","es-ES"]')
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locales.cmd_multilingual_locales_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/locales/v2/bulk/locale/delete"))
        self.assertEqual(call.kwargs["json_body"], {"localeIds": ["fr-FR", "es-ES"]})

    @patch("wix_safe_agent_cli.commands.multilingual_locales.HttpClient")
    def test_create_new_primary_requires_ack_and_returns_token(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"token": "token-1"})
        args = SimpleNamespace(primary_locale_json='{"languageCode":"en","regionCode":"US"}')
        no_ack_ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locales.cmd_multilingual_locales_create_new_primary(args, no_ack_ctx)
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])

        ack_ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locales.cmd_multilingual_locales_create_new_primary(args, ack_ctx)
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["receipt"]["response"]["token"], "token-1")

    @patch("wix_safe_agent_cli.commands.multilingual_locales.HttpClient")
    def test_status_and_supported_locale_reads_use_query_params(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": "yes"})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locales.cmd_multilingual_locales_get_new_primary_status(SimpleNamespace(token="token-1"), self._ctx())
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], {"token": "token-1"})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locales.cmd_multilingual_locales_list_supported(
                SimpleNamespace(language_code="fr", include_all_locales="true", include_region_options="false"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(
            mock_client.return_value.request.call_args.kwargs["params"],
            {"includeAllLocales": True, "includeRegionOptions": False, "languageCode": "fr"},
        )

    def test_plan_in_mismatch_is_refused(self) -> None:
        args = SimpleNamespace(locale_id="fr-FR")
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(
                {
                    "method": "multilingual-locales.delete",
                    "baseline": {
                        "env_fingerprint": "https://other.example",
                        "selector": {"kind": "wix-multilingual-locale", "operation": "delete", "locale_id": "fr-FR"},
                    },
                },
                handle,
            )
            plan_path = handle.name
        try:
            ctx = self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = multilingual_locales.cmd_multilingual_locales_delete(args, ctx)
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
        finally:
            Path(plan_path).unlink()


if __name__ == "__main__":
    unittest.main()
