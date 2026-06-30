from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import form_schemas
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


class TestFormSchemasCommands(unittest.TestCase):
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
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli form-schemas",
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

    def test_parser_exposes_form_schema_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["form-schemas", "list"], "list", False),
            (["form-schemas", "get", "--form-id", "form-1"], "get", False),
            (["form-schemas", "query", "--query-json", '{"filter":{"namespace":{"$eq":"ns"}}}'], "query", False),
            (["form-schemas", "count", "--filter-json", '{"namespace":{"$eq":"ns"}}'], "count", False),
            (["form-schemas", "get-deleted", "--form-id", "form-1"], "get-deleted", False),
            (["form-schemas", "list-deleted"], "list-deleted", False),
            (["form-schemas", "query-deleted", "--query-json", '{"filter":{"namespace":{"$eq":"ns"}}}'], "query-deleted", False),
            (["form-schemas", "count-deleted", "--filter-json", '{"namespace":{"$eq":"ns"}}'], "count-deleted", False),
            (["form-schemas", "list-providers-configs"], "list-providers-configs", False),
            (["form-schemas", "get-summary", "--form-id", "form-1"], "get-summary", False),
            (["form-schemas", "create", "--form-json", '{"form":{"namespace":"ns"}}'], "create", True),
            (["form-schemas", "bulk-create", "--bulk-json", '{"forms":[]}'], "bulk-create", True),
            (["form-schemas", "update", "--form-json", '{"form":{"id":"form-1"}}'], "update", True),
            (["form-schemas", "clone", "--form-id", "form-1"], "clone", True),
            (["form-schemas", "bulk-clone", "--bulk-json", '{"formIds":["form-1"]}'], "bulk-clone", True),
            (["form-schemas", "delete", "--form-id", "form-1"], "delete", True),
            (["form-schemas", "bulk-delete", "--bulk-json", '{"formIds":["form-1"]}'], "bulk-delete", True),
            (["form-schemas", "restore", "--form-id", "form-1"], "restore", True),
            (["form-schemas", "remove-from-trash", "--form-id", "form-1"], "remove-from-trash", True),
            (
                ["form-schemas", "bulk-remove-deleted-field", "--bulk-json", '{"formId":"form-1","fieldIds":["field-1"]}'],
                "bulk-remove-deleted-field",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.form_schemas_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.form_schemas.HttpClient")
    def test_form_schema_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        read_cases = [
            (form_schemas.cmd_form_schemas_list, SimpleNamespace(namespace="ns", limit=5, offset=1), "GET", "/form-schema-service/v4/forms"),
            (form_schemas.cmd_form_schemas_get, SimpleNamespace(form_id="form-1"), "GET", "/form-schema-service/v4/forms/form-1"),
            (
                form_schemas.cmd_form_schemas_get_deleted,
                SimpleNamespace(form_id="form-1"),
                "GET",
                "/form-schema-service/v4/forms/trash-bin/form-1",
            ),
            (
                form_schemas.cmd_form_schemas_list_deleted,
                SimpleNamespace(namespace=None, limit=None, offset=None),
                "GET",
                "/form-schema-service/v4/forms/trash-bin",
            ),
            (
                form_schemas.cmd_form_schemas_list_providers_configs,
                SimpleNamespace(),
                "GET",
                "/form-schema-service/v4/forms/providers-config",
            ),
            (
                form_schemas.cmd_form_schemas_get_summary,
                SimpleNamespace(form_id="form-1"),
                "GET",
                "/form-schema-service/v4/forms/form-1/summary",
            ),
            (
                form_schemas.cmd_form_schemas_query,
                SimpleNamespace(query_json='{"filter":{"namespace":{"$eq":"ns"}}}'),
                "POST",
                "/form-schema-service/v4/forms/query",
            ),
            (
                form_schemas.cmd_form_schemas_count,
                SimpleNamespace(filter_json='{"namespace":{"$eq":"ns"}}'),
                "POST",
                "/form-schema-service/v4/forms/count-by-filter",
            ),
            (
                form_schemas.cmd_form_schemas_query_deleted,
                SimpleNamespace(query_json='{"filter":{"namespace":{"$eq":"ns"}}}'),
                "POST",
                "/form-schema-service/v4/forms/trash-bin/query",
            ),
            (
                form_schemas.cmd_form_schemas_count_deleted,
                SimpleNamespace(filter_json='{"namespace":{"$eq":"ns"}}'),
                "POST",
                "/form-schema-service/v4/deleted-forms/count",
            ),
        ]
        for func, args, http_method, path in read_cases:
            with self.subTest(path=path):
                mock_client.return_value.request.reset_mock()
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                self.assertEqual(rc, 0)
                self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], http_method)
                self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith(path))

    @patch("wix_safe_agent_cli.commands.form_schemas.HttpClient")
    def test_form_schema_writes_are_plan_first_with_expected_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        write_cases = [
            (form_schemas.cmd_form_schemas_create, SimpleNamespace(form_json='{"form":{"namespace":"ns"}}'), "POST", "/form-schema-service/v4/forms", False),
            (form_schemas.cmd_form_schemas_bulk_create, SimpleNamespace(bulk_json='{"forms":[{"namespace":"ns"}]}'), "POST", "/form-schema-service/v4/bulk/forms/create", False),
            (form_schemas.cmd_form_schemas_update, SimpleNamespace(form_json='{"form":{"id":"form-1"}}'), "PATCH", "/form-schema-service/v4/forms/form-1", False),
            (form_schemas.cmd_form_schemas_clone, SimpleNamespace(form_id="form-1", clone_json="{}"), "POST", "/form-schema-service/v4/forms/form-1/clone", False),
            (form_schemas.cmd_form_schemas_bulk_clone, SimpleNamespace(bulk_json='{"formIds":["form-1"]}'), "POST", "/form-schema-service/v4/bulk/forms/clone", False),
            (form_schemas.cmd_form_schemas_delete, SimpleNamespace(form_id="form-1"), "DELETE", "/form-schema-service/v4/forms/form-1", True),
            (form_schemas.cmd_form_schemas_bulk_delete, SimpleNamespace(bulk_json='{"formIds":["form-1"]}'), "POST", "/form-schema-service/v4/bulk/forms/delete", True),
            (form_schemas.cmd_form_schemas_restore, SimpleNamespace(form_id="form-1"), "POST", "/form-schema-service/v4/forms/trash-bin/form-1/restore", False),
            (form_schemas.cmd_form_schemas_remove_from_trash, SimpleNamespace(form_id="form-1"), "DELETE", "/form-schema-service/v4/forms/trash-bin/form-1", True),
            (
                form_schemas.cmd_form_schemas_bulk_remove_deleted_field,
                SimpleNamespace(bulk_json='{"formId":"form-1","fieldIds":["field-1"]}'),
                "POST",
                "/form-schema-service/v4/forms/fields/delete",
                True,
            ),
        ]
        for func, args, http_method, path, requires_ack in write_cases:
            with self.subTest(path=path):
                mock_client.return_value.request.reset_mock()
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                preconditions = payload["plan"]["preconditions"]
                self.assertEqual("apply also requires --ack-irreversible" in preconditions, requires_ack)
                self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.form_schemas.HttpClient")
    def test_form_schema_update_requires_form_id(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_schemas.cmd_form_schemas_update(SimpleNamespace(form_json='{"form":{"namespace":"ns"}}'), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
