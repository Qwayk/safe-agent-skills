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
from wix_safe_agent_cli.commands import contact_labels
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestContactLabelsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
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
        cfg_override = overrides.pop("cfg_override", None)
        if isinstance(cfg_override, dict):
            for field, value in cfg_override.items():
                setattr(cfg, field, value)
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli contact-labels",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "apply": False,
            "yes": False,
            "plan_out": None,
            "plan_in": None,
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

    def test_parser_recognizes_contact_labels_subcommands_and_write_flags(self) -> None:
        parser = build_parser()

        query_args = parser.parse_args(["contact-labels", "query", "--query-json", '{"query":{}}'])
        self.assertEqual(query_args.contact_labels_cmd, "query")
        self.assertFalse(query_args.write_capable)

        list_args = parser.parse_args(["contact-labels", "list"])
        self.assertEqual(list_args.contact_labels_cmd, "list")
        self.assertFalse(list_args.write_capable)

        find_or_create_args = parser.parse_args(
            ["contact-labels", "find-or-create", "--label-json", '{"displayName":"VIP"}']
        )
        self.assertEqual(find_or_create_args.contact_labels_cmd, "find-or-create")
        self.assertTrue(find_or_create_args.write_capable)

        get_args = parser.parse_args(["contact-labels", "get", "--key", "label-1"])
        self.assertEqual(get_args.contact_labels_cmd, "get")
        self.assertFalse(get_args.write_capable)

        update_args = parser.parse_args(
            ["contact-labels", "update", "--key", "label-1", "--label-json", '{"displayName":"VIP"}']
        )
        self.assertEqual(update_args.contact_labels_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(["contact-labels", "delete", "--key", "label-1"])
        self.assertEqual(delete_args.contact_labels_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

    @patch("wix_safe_agent_cli.commands.contact_labels.HttpClient")
    def test_contact_labels_query_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"labels": [{"key": "label-1"}]})
        args = SimpleNamespace(query_json='{"query":{"filter":{"displayName":{"$eq":"VIP"}}}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contact_labels.cmd_contact_labels_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "contact-labels.query")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/contacts/v4/labels/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"displayName": {"$eq": "VIP"}}}})
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertEqual(call.kwargs["headers"]["Authorization"], "site-app-token")
        self.assertEqual(call.kwargs["url"], "https://www.wixapis.com/contacts/v4/labels/query")

    @patch("wix_safe_agent_cli.commands.contact_labels.HttpClient")
    def test_contact_labels_list_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"labels": [{"key": "label-1"}]})
        args = SimpleNamespace()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contact_labels.cmd_contact_labels_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "contact-labels.list")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/contacts/v4/labels")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["url"], "https://www.wixapis.com/contacts/v4/labels")

    @patch("wix_safe_agent_cli.commands.contact_labels.HttpClient")
    def test_contact_labels_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"label": {"key": "label-1", "displayName": "VIP"}}
        )
        args = SimpleNamespace(key="label-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contact_labels.cmd_contact_labels_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "contact-labels.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/contacts/v4/labels/label-1")

    @patch("wix_safe_agent_cli.commands.contact_labels.HttpClient")
    def test_contact_labels_find_or_create_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}})
        args = SimpleNamespace(label_json='{"displayName":"VIP"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contact_labels.cmd_contact_labels_find_or_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "contact-labels.find-or-create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/contacts/v4/labels")
        self.assertEqual(payload["plan"]["request"]["body"]["label"]["displayName"], "VIP")

    @patch("wix_safe_agent_cli.commands.contact_labels.HttpClient")
    def test_contact_labels_find_or_create_apply_requires_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}})
        args = SimpleNamespace(label_json='{"displayName":"VIP"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contact_labels.cmd_contact_labels_find_or_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-in", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.contact_labels.HttpClient")
    def test_contact_labels_find_or_create_apply_uses_plan_and_verifies(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}}),
            _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}}),
        ]
        args = SimpleNamespace(label_json='{"displayName":"VIP"}')
        dry_ctx = self._ctx()

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            contact_labels.cmd_contact_labels_find_or_create(args, dry_ctx)
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])

        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path, command_str="wix-safe-agent-cli contact-labels find-or-create --label-json '{\"displayName\":\"VIP\"}'")
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                rc = contact_labels.cmd_contact_labels_find_or_create(args, apply_ctx)
            payload = json.loads(apply_buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["key"], "label-1")
            self.assertEqual(mock_client.return_value.request.call_count, 2)
            first_call = mock_client.return_value.request.call_args_list[0]
            second_call = mock_client.return_value.request.call_args_list[1]
            self.assertEqual(first_call.kwargs["method"], "POST")
            self.assertEqual(first_call.kwargs["url"], "https://www.wixapis.com/contacts/v4/labels")
            self.assertEqual(second_call.kwargs["method"], "GET")
            self.assertEqual(second_call.kwargs["url"], "https://www.wixapis.com/contacts/v4/labels/label-1")
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.contact_labels.HttpClient")
    def test_contact_labels_update_dry_run_and_apply_flow(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(key="label-1", label_json='{"displayName":"New VIP"}')
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}}),
            _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}}),
            _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}}),
            _DummyResponse({"label": {"key": "label-1", "displayName": "New VIP"}}),
            _DummyResponse({"label": {"key": "label-1", "displayName": "New VIP"}}),
        ]

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            contact_labels.cmd_contact_labels_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])

        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path, command_str="wix-safe-agent-cli contact-labels update --key label-1 --label-json '{\"displayName\":\"New VIP\"}'")
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                rc = contact_labels.cmd_contact_labels_update(args, apply_ctx)
            payload = json.loads(apply_buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["method"], "contact-labels.update")
            self.assertEqual(payload["receipt"]["verification"]["after"]["displayName"], "New VIP")
            self.assertEqual(mock_client.return_value.request.call_count, 5)
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.contact_labels.HttpClient")
    def test_contact_labels_delete_requires_irreversible_plan_flags(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}})
        args = SimpleNamespace(key="label-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            contact_labels.cmd_contact_labels_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])

        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                rc = contact_labels.cmd_contact_labels_delete(args, apply_ctx)
            payload = json.loads(apply_buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.contact_labels.HttpClient")
    def test_contact_labels_delete_apply_verifies_absence(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(key="label-1")
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}}),
            _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}}),
            _DummyResponse({"label": {"key": "label-1", "displayName": "VIP"}}),
            _DummyResponse({}),
            RuntimeError("HTTP 404 for GET https://www.wixapis.com/contacts/v4/labels/label-1\n{}"),
        ]

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            contact_labels.cmd_contact_labels_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])

        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path, ack_irreversible=True)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                rc = contact_labels.cmd_contact_labels_delete(args, apply_ctx)
            payload = json.loads(apply_buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["actual_http_status"], 404)
            self.assertEqual(mock_client.return_value.request.call_count, 5)
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.contact_labels.HttpClient")
    def test_contact_labels_auth_uses_app_token_mode(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"labels": []})
        args = SimpleNamespace()

        ctx = self._ctx(
            cfg_override={
                "api_key": "account-key",
                "account_id": "account-id",
            },
            command_str="wix-safe-agent-cli contact-labels list",
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contact_labels.cmd_contact_labels_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["auth_mode"], "app_token")
        headers = mock_client.return_value.request.call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "site-app-token")
        self.assertNotIn("wix-account-id", headers)
