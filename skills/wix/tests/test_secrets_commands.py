from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import secrets
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestSecretsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli secrets",
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

    def test_parser_recognizes_secrets_subcommands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["secrets", "list"])
        self.assertEqual(list_args.secrets_cmd, "list")
        self.assertFalse(list_args.write_capable)

        get_args = parser.parse_args(["secrets", "get-value", "--name", "API_KEY"])
        self.assertEqual(get_args.secrets_cmd, "get-value")
        self.assertFalse(get_args.write_capable)

        create_args = parser.parse_args(
            [
                "secrets",
                "create",
                "--secret-json",
                '{"name":"API_KEY","value":"super-secret","description":"Primary key"}',
            ]
        )
        self.assertEqual(create_args.secrets_cmd, "create")
        self.assertTrue(create_args.write_capable)

        patch_args = parser.parse_args(
            [
                "secrets",
                "patch",
                "--secret-id",
                "secret-1",
                "--secret-json",
                '{"description":"Updated description"}',
            ]
        )
        self.assertEqual(patch_args.secrets_cmd, "patch")
        self.assertTrue(patch_args.write_capable)

        delete_args = parser.parse_args(["secrets", "delete", "--secret-id", "secret-1"])
        self.assertEqual(delete_args.secrets_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

    @patch("wix_safe_agent_cli.commands.secrets.HttpClient")
    def test_list_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"secrets": [{"id": "secret-1", "name": "API_KEY", "description": "Primary key"}]}
        )
        args = SimpleNamespace()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = secrets.cmd_secrets_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            payload["request"]["path"],
            "/_api/cloud-secrets-vault-server/api/v1/secrets",
        )
        self.assertNotIn("value", payload["response"]["secrets"][0])

    @patch("wix_safe_agent_cli.commands.secrets.HttpClient")
    def test_get_value_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"value": "super-secret"})
        args = SimpleNamespace(name="API_KEY")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = secrets.cmd_secrets_get_value(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            payload["request"]["path"],
            "/_api/cloud-secrets-vault-server/api/v1/secrets/name/API_KEY",
        )
        self.assertEqual(payload["response"]["value"], "super-secret")

    @patch("wix_safe_agent_cli.commands.secrets.HttpClient")
    def test_create_dry_run_plan_redacts_secret_value(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"secrets": []})
        args = SimpleNamespace(
            secret_json='{"name":"API_KEY","value":"super-secret","description":"Primary key"}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = secrets.cmd_secrets_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        serialized_plan = json.dumps(payload["plan"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "secrets.create")
        self.assertEqual(payload["plan"]["request"]["body"]["secret"]["value"], "[redacted]")
        self.assertNotIn("super-secret", serialized_plan)

    @patch("wix_safe_agent_cli.commands.secrets.HttpClient")
    def test_create_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"secrets": []})
        args = SimpleNamespace(
            secret_json='{"name":"API_KEY","value":"super-secret","description":"Primary key"}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = secrets.cmd_secrets_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.secrets.HttpClient")
    def test_create_refuses_duplicate_name(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"secrets": [{"id": "secret-1", "name": "API_KEY"}]}
        )
        args = SimpleNamespace(secret_json='{"name":"API_KEY","value":"super-secret"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = secrets.cmd_secrets_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("already exists", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.secrets.HttpClient")
    def test_patch_dry_run_plan_redacts_secret_value(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"secrets": [{"id": "secret-1", "name": "API_KEY", "description": "Primary key"}]}
        )
        args = SimpleNamespace(
            secret_id="secret-1",
            secret_json='{"description":"Updated description","value":"new-secret"}',
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = secrets.cmd_secrets_patch(args, self._ctx())
        payload = json.loads(buf.getvalue())
        serialized_plan = json.dumps(payload["plan"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["body"]["secret"]["value"], "[redacted]")
        self.assertNotIn("new-secret", serialized_plan)

    @patch("wix_safe_agent_cli.commands.secrets.HttpClient")
    def test_delete_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"secrets": [{"id": "secret-1", "name": "API_KEY"}]}
        )
        args = SimpleNamespace(secret_id="secret-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = secrets.cmd_secrets_delete(
                args,
                self._ctx(apply=True, yes=True, ack_irreversible=True),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    def test_delete_live_apply_requires_ack_irreversible(self) -> None:
        args = SimpleNamespace(secret_id="secret-1")
        current_secret = {"id": "secret-1", "name": "API_KEY", "description": "Primary key"}

        with patch("wix_safe_agent_cli.commands.secrets.HttpClient") as dry_client:
            dry_client.return_value.request.return_value = _DummyResponse({"secrets": [current_secret]})
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = secrets.cmd_secrets_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            with patch("wix_safe_agent_cli.commands.secrets.HttpClient") as apply_client:
                apply_client.return_value.request.return_value = _DummyResponse({"secrets": [current_secret]})
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = secrets.cmd_secrets_delete(
                        args,
                        self._ctx(apply=True, yes=True, plan_in=plan_path),
                    )
                payload = json.loads(buf.getvalue())

            self.assertEqual(dry_rc, 0)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["method"], "secrets.delete")
            self.assertEqual(apply_client.return_value.request.call_count, 1)
        finally:
            os.unlink(plan_path)

    def test_create_apply_verifies_by_metadata_readback(self) -> None:
        args = SimpleNamespace(secret_json='{"name":"API_KEY","value":"super-secret","description":"Primary key"}')
        created_secret = {"id": "secret-1", "name": "API_KEY", "description": "Primary key"}

        with patch("wix_safe_agent_cli.commands.secrets.HttpClient") as dry_client:
            dry_client.return_value.request.return_value = _DummyResponse({"secrets": []})
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = secrets.cmd_secrets_create(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            with patch("wix_safe_agent_cli.commands.secrets.HttpClient") as apply_client:
                apply_client.return_value.request.side_effect = [
                    _DummyResponse({"secrets": []}),
                    _DummyResponse({"secrets": []}),
                    _DummyResponse({"id": "secret-1"}),
                    _DummyResponse({"secrets": [created_secret]}),
                ]
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = secrets.cmd_secrets_create(
                        args,
                        self._ctx(apply=True, yes=True, plan_in=plan_path),
                    )
                payload = json.loads(buf.getvalue())
                serialized_receipt = json.dumps(payload["receipt"])

            self.assertEqual(dry_rc, 0)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["id"], "secret-1")
            self.assertNotIn("super-secret", serialized_receipt)
            self.assertEqual(apply_client.return_value.request.call_count, 4)
        finally:
            os.unlink(plan_path)
