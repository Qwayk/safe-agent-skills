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
from wix_safe_agent_cli.commands import tags
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestTagsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli tags",
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

    def test_parser_recognizes_tags_subcommands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["tags", "list", "--fqdn", "wix.ecom.v1.order"])
        self.assertEqual(list_args.tags_cmd, "list")
        self.assertFalse(list_args.write_capable)

        get_args = parser.parse_args(["tags", "get", "--tag-id", "tag-1"])
        self.assertEqual(get_args.tags_cmd, "get")
        self.assertFalse(get_args.write_capable)

        create_args = parser.parse_args(["tags", "create", "--tag-json", '{"fqdn":"wix.ecom.v1.order","name":"VIP"}'])
        self.assertEqual(create_args.tags_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(["tags", "update", "--tag-id", "tag-1", "--tag-json", '{"revision":"1","name":"VIP"}'])
        self.assertEqual(update_args.tags_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(["tags", "delete", "--tag-id", "tag-1"])
        self.assertEqual(delete_args.tags_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

    @patch("wix_safe_agent_cli.commands.tags.HttpClient")
    def test_tags_list_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"tags": [{"id": "tag-1"}]})
        args = SimpleNamespace(fqdn="wix.ecom.v1.order")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = tags.cmd_tags_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["params"], {"fqdn": "wix.ecom.v1.order"})
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["params"], {"fqdn": "wix.ecom.v1.order"})
        self.assertEqual(call.kwargs["headers"], {"Authorization": "site-app-token"})

    @patch("wix_safe_agent_cli.commands.tags.HttpClient")
    def test_tags_create_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"tags": []})
        args = SimpleNamespace(tag_json='{"fqdn":"wix.ecom.v1.order","name":"VIP"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = tags.cmd_tags_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "tags.create")
        self.assertTrue(payload["plan"]["state_capture"]["before_state_available"])

    @patch("wix_safe_agent_cli.commands.tags.HttpClient")
    def test_tags_create_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"tags": []})
        args = SimpleNamespace(tag_json='{"fqdn":"wix.ecom.v1.order","name":"VIP"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = tags.cmd_tags_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.tags.HttpClient")
    def test_tags_create_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"tags": []}),
            _DummyResponse({"tags": []}),
            _DummyResponse({"tags": []}),
            _DummyResponse({"tag": {"id": "tag-1", "name": "VIP", "fqdn": "wix.ecom.v1.order"}}),
            _DummyResponse({"tag": {"id": "tag-1", "name": "VIP", "fqdn": "wix.ecom.v1.order"}}),
        ]
        args = SimpleNamespace(tag_json='{"fqdn":"wix.ecom.v1.order","name":"VIP"}')
        dry_ctx = self._ctx()

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = tags.cmd_tags_create(args, dry_ctx)
        dry_payload = json.loads(dry_buf.getvalue())
        plan_path = self._write_plan(dry_payload["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = tags.cmd_tags_create(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(dry_rc, 0)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["id"], "tag-1")
            self.assertTrue(payload["receipt"]["state_capture"]["before_state_available"])
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.tags.HttpClient")
    def test_tags_update_apply_uses_plan_in(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"tag": {"id": "tag-1", "name": "Old", "fqdn": "wix.ecom.v1.order", "revision": "1"}}),
            _DummyResponse({"tag": {"id": "tag-1", "name": "Old", "fqdn": "wix.ecom.v1.order", "revision": "1"}}),
            _DummyResponse({"tag": {"id": "tag-1", "name": "Old", "fqdn": "wix.ecom.v1.order", "revision": "1"}}),
            _DummyResponse({"tag": {"id": "tag-1", "name": "New", "fqdn": "wix.ecom.v1.order", "revision": "2"}}),
            _DummyResponse({"tag": {"id": "tag-1", "name": "New", "fqdn": "wix.ecom.v1.order", "revision": "2"}}),
        ]
        args = SimpleNamespace(tag_id="tag-1", tag_json='{"revision":"1","name":"New"}')

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            tags.cmd_tags_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = tags.cmd_tags_update(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["name"], "New")
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.tags.HttpClient")
    def test_tags_delete_requires_ack_and_plan_in(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"tag": {"id": "tag-1", "name": "VIP", "fqdn": "wix.ecom.v1.order"}})
        args = SimpleNamespace(tag_id="tag-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            tags.cmd_tags_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = tags.cmd_tags_delete(args, self._ctx(apply=True, yes=True, plan_in=plan_path, ack_irreversible=False))
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertFalse(payload.get("refused", False))
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.tags.HttpClient")
    def test_tags_delete_apply_verifies_404(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"tag": {"id": "tag-1", "name": "VIP", "fqdn": "wix.ecom.v1.order"}}),
            _DummyResponse({"tag": {"id": "tag-1", "name": "VIP", "fqdn": "wix.ecom.v1.order"}}),
            _DummyResponse({"tag": {"id": "tag-1", "name": "VIP", "fqdn": "wix.ecom.v1.order"}}),
            _DummyResponse({}),
            RuntimeError("HTTP 404 for GET https://www.wixapis.com/tags/v1/tags/tag-1\n{}"),
        ]
        args = SimpleNamespace(tag_id="tag-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            tags.cmd_tags_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path, ack_irreversible=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = tags.cmd_tags_delete(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["actual_http_status"], 404)
        finally:
            Path(plan_path).unlink()
