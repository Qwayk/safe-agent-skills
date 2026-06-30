from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import data_extension_schemas
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestDataExtensionSchemasCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
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
            "command_str": "wix-safe-agent-cli data-extension-schemas",
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

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_data_extension_schema_subcommands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(
            [
                "data-extension-schemas",
                "list",
                "--fqdn",
                "wix.ecom.*.order",
                "--namespaces-json",
                '["_user_fields"]',
            ]
        )
        self.assertEqual(list_args.data_extension_schemas_cmd, "list")
        self.assertFalse(list_args.write_capable)

        create_args = parser.parse_args(
            [
                "data-extension-schemas",
                "create",
                "--data-extension-schema-json",
                '{"fqdn":"wix.ecom.*.order","namespace":"_user_fields","jsonSchema":{"type":"object"}}',
            ]
        )
        self.assertEqual(create_args.data_extension_schemas_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(
            [
                "data-extension-schemas",
                "update",
                "--data-extension-schema-json",
                '{"id":"schema-1","fqdn":"wix.ecom.*.order","namespace":"_user_fields","revision":"2","jsonSchema":{"type":"object"}}',
            ]
        )
        self.assertEqual(update_args.data_extension_schemas_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(
            [
                "data-extension-schemas",
                "delete-user-defined-fields",
                "--data-extension-schema-id",
                "schema-1",
                "--fqdn",
                "wix.ecom.*.order",
                "--fields-to-delete-json",
                '["size"]',
            ]
        )
        self.assertEqual(delete_args.data_extension_schemas_cmd, "delete-user-defined-fields")
        self.assertTrue(delete_args.write_capable)

    @patch("wix_safe_agent_cli.commands.data_extension_schemas.HttpClient")
    def test_list_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"dataExtensionSchemas": [{"id": "schema-1"}]}
        )
        args = SimpleNamespace(
            fqdn="wix.ecom.*.order",
            namespaces_json='["_user_fields"]',
            fields_json='["ARCHIVED"]',
            extension_points_json='["checkout"]',
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_extension_schemas.cmd_data_extension_schemas_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            payload["request"]["params"],
            {
                "fqdn": "wix.ecom.*.order",
                "namespaces": ["_user_fields"],
                "fields": ["ARCHIVED"],
                "extensionPoints": ["checkout"],
            },
        )
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["headers"], {"Authorization": "site-app-token"})

    @patch("wix_safe_agent_cli.commands.data_extension_schemas.HttpClient")
    def test_create_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataExtensionSchemas": []})
        args = SimpleNamespace(
            data_extension_schema_json=(
                '{"fqdn":"wix.ecom.*.order","namespace":"_user_fields","jsonSchema":{"type":"object"}}'
            )
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_extension_schemas.cmd_data_extension_schemas_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "data-extension-schemas.create")
        self.assertTrue(payload["plan"]["state_capture"]["before_state_available"])

    @patch("wix_safe_agent_cli.commands.data_extension_schemas.HttpClient")
    def test_create_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataExtensionSchemas": []})
        args = SimpleNamespace(
            data_extension_schema_json=(
                '{"fqdn":"wix.ecom.*.order","namespace":"_user_fields","jsonSchema":{"type":"object"}}'
            )
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_extension_schemas.cmd_data_extension_schemas_create(
                args,
                self._ctx(apply=True, yes=True),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.data_extension_schemas.HttpClient")
    def test_create_refuses_duplicate_namespace(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "dataExtensionSchemas": [
                    {
                        "id": "schema-1",
                        "fqdn": "wix.ecom.*.order",
                        "namespace": "_user_fields",
                        "jsonSchema": {"type": "object"},
                    }
                ]
            }
        )
        args = SimpleNamespace(
            data_extension_schema_json=(
                '{"fqdn":"wix.ecom.*.order","namespace":"_user_fields","jsonSchema":{"type":"object"}}'
            )
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_extension_schemas.cmd_data_extension_schemas_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("already exists", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.data_extension_schemas.HttpClient")
    def test_update_refuses_missing_schema_in_readback(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataExtensionSchemas": []})
        args = SimpleNamespace(
            data_extension_schema_json=(
                '{"id":"schema-1","fqdn":"wix.ecom.*.order","namespace":"_user_fields","revision":"2","jsonSchema":{"type":"object"}}'
            )
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_extension_schemas.cmd_data_extension_schemas_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("not found", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_extension_schemas.HttpClient")
    def test_delete_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "dataExtensionSchemas": [
                    {
                        "id": "schema-1",
                        "fqdn": "wix.ecom.*.order",
                        "namespace": "_user_fields",
                        "jsonSchema": {"type": "object", "properties": {"size": {"type": "string"}}},
                    }
                ]
            }
        )
        args = SimpleNamespace(
            data_extension_schema_id="schema-1",
            fqdn="wix.ecom.*.order",
            fields_to_delete_json='["size"]',
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_extension_schemas.cmd_data_extension_schemas_delete_user_defined_fields(
                args,
                self._ctx(apply=True, yes=True, ack_irreversible=True),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    def test_delete_apply_requires_ack_irreversible(self) -> None:
        args = SimpleNamespace(
            data_extension_schema_id="schema-1",
            fqdn="wix.ecom.*.order",
            fields_to_delete_json='["size"]',
        )

        with patch("wix_safe_agent_cli.commands.data_extension_schemas.HttpClient") as dry_client:
            dry_client.return_value.request.return_value = _DummyResponse(
                {
                    "dataExtensionSchemas": [
                        {
                            "id": "schema-1",
                            "fqdn": "wix.ecom.*.order",
                            "namespace": "_user_fields",
                            "jsonSchema": {"type": "object", "properties": {"size": {"type": "string"}}},
                        }
                    ]
                }
            )
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = data_extension_schemas.cmd_data_extension_schemas_delete_user_defined_fields(
                    args,
                    self._ctx(),
                )
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            with patch("wix_safe_agent_cli.commands.data_extension_schemas.HttpClient") as apply_client:
                apply_client.return_value.request.return_value = _DummyResponse(
                    {
                        "dataExtensionSchemas": [
                            {
                                "id": "schema-1",
                                "fqdn": "wix.ecom.*.order",
                                "namespace": "_user_fields",
                                "jsonSchema": {"type": "object", "properties": {"size": {"type": "string"}}},
                            }
                        ]
                    }
                )
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = data_extension_schemas.cmd_data_extension_schemas_delete_user_defined_fields(
                        args,
                        self._ctx(apply=True, yes=True, plan_in=plan_path),
                    )
                payload = json.loads(buf.getvalue())

            self.assertEqual(dry_rc, 0)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["method"], "data-extension-schemas.delete-user-defined-fields")
            self.assertEqual(apply_client.return_value.request.call_count, 1)
        finally:
            tempfile_path = plan_path
            try:
                import os

                os.unlink(tempfile_path)
            except FileNotFoundError:
                pass

    def test_update_apply_uses_plan_in_and_verifies(self) -> None:
        args = SimpleNamespace(
            data_extension_schema_json=(
                '{"id":"schema-1","fqdn":"wix.ecom.*.order","namespace":"_user_fields","revision":"2","jsonSchema":{"type":"object","properties":{"size":{"type":"string"}}}}'
            )
        )
        before_schema = {
            "id": "schema-1",
            "fqdn": "wix.ecom.*.order",
            "namespace": "_user_fields",
            "revision": "1",
            "jsonSchema": {"type": "object"},
        }
        after_schema = {
            "id": "schema-1",
            "fqdn": "wix.ecom.*.order",
            "namespace": "_user_fields",
            "revision": "2",
            "jsonSchema": {"type": "object", "properties": {"size": {"type": "string"}}},
        }

        with patch("wix_safe_agent_cli.commands.data_extension_schemas.HttpClient") as dry_client:
            dry_client.return_value.request.return_value = _DummyResponse(
                {"dataExtensionSchemas": [before_schema]}
            )
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = data_extension_schemas.cmd_data_extension_schemas_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            with patch("wix_safe_agent_cli.commands.data_extension_schemas.HttpClient") as apply_client:
                apply_client.return_value.request.side_effect = [
                    _DummyResponse({"dataExtensionSchemas": [before_schema]}),
                    _DummyResponse({"dataExtensionSchemas": [before_schema]}),
                    _DummyResponse({"dataExtensionSchema": after_schema}),
                    _DummyResponse({"dataExtensionSchemas": [after_schema]}),
                ]
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = data_extension_schemas.cmd_data_extension_schemas_update(
                        args,
                        self._ctx(apply=True, yes=True, plan_in=plan_path),
                    )
                payload = json.loads(buf.getvalue())

            self.assertEqual(dry_rc, 0)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["revision"], "2")
            self.assertEqual(apply_client.return_value.request.call_count, 4)
        finally:
            tempfile_path = plan_path
            try:
                import os

                os.unlink(tempfile_path)
            except FileNotFoundError:
                pass
