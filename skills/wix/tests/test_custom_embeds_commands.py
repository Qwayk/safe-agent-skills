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
from wix_safe_agent_cli.commands import custom_embeds
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCustomEmbedsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli custom-embeds",
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

    def test_parser_recognizes_custom_embeds_subcommands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["custom-embeds", "list", "--limit", "25", "--offset", "5"])
        self.assertEqual(list_args.custom_embeds_cmd, "list")
        self.assertFalse(list_args.write_capable)

        get_args = parser.parse_args(["custom-embeds", "get", "--custom-embed-id", "embed-1"])
        self.assertEqual(get_args.custom_embeds_cmd, "get")
        self.assertFalse(get_args.write_capable)

        create_args = parser.parse_args(
            [
                "custom-embeds",
                "create",
                "--custom-embed-json",
                '{"name":"Header","position":"HEAD","embedData":{"category":"ESSENTIAL","html":"<script></script>"}}',
            ]
        )
        self.assertEqual(create_args.custom_embeds_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(
            [
                "custom-embeds",
                "update",
                "--custom-embed-id",
                "embed-1",
                "--custom-embed-json",
                '{"revision":"1","name":"Updated Header"}',
            ]
        )
        self.assertEqual(update_args.custom_embeds_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(["custom-embeds", "delete", "--custom-embed-id", "embed-1"])
        self.assertEqual(delete_args.custom_embeds_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

    @patch("wix_safe_agent_cli.commands.custom_embeds.HttpClient")
    def test_custom_embeds_list_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"customEmbeds": [{"id": "embed-1"}]})
        args = SimpleNamespace(limit=25, offset=5)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = custom_embeds.cmd_custom_embeds_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["params"], {"paging.limit": 25, "paging.offset": 5})
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["params"], {"paging.limit": 25, "paging.offset": 5})
        self.assertEqual(call.kwargs["headers"], {"Authorization": "site-app-token"})

    @patch("wix_safe_agent_cli.commands.custom_embeds.HttpClient")
    def test_custom_embeds_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"customEmbed": {"id": "embed-1"}})
        args = SimpleNamespace(custom_embed_id="embed-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = custom_embeds.cmd_custom_embeds_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/embeds/v1/custom-embeds/embed-1")

    @patch("wix_safe_agent_cli.commands.custom_embeds.HttpClient")
    def test_custom_embeds_create_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"customEmbeds": []})
        args = SimpleNamespace(
            custom_embed_json='{"name":"Header","position":"HEAD","embedData":{"category":"ESSENTIAL","html":"<script></script>"}}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = custom_embeds.cmd_custom_embeds_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "custom-embeds.create")
        self.assertTrue(payload["plan"]["state_capture"]["before_state_available"])

    @patch("wix_safe_agent_cli.commands.custom_embeds.HttpClient")
    def test_custom_embeds_create_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"customEmbeds": []})
        args = SimpleNamespace(
            custom_embed_json='{"name":"Header","position":"HEAD","embedData":{"category":"ESSENTIAL","html":"<script></script>"}}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = custom_embeds.cmd_custom_embeds_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    def test_custom_embeds_update_requires_revision(self) -> None:
        args = SimpleNamespace(custom_embed_id="embed-1", custom_embed_json='{"name":"Updated Header"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = custom_embeds.cmd_custom_embeds_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("revision", payload["error"])

    def test_custom_embeds_update_apply_uses_plan_in_and_verifies(self) -> None:
        args = SimpleNamespace(
            custom_embed_id="embed-1",
            custom_embed_json='{"revision":"1","name":"New Header","embedData":{"category":"ESSENTIAL","html":"<script>new()</script>"}}',
        )

        with patch("wix_safe_agent_cli.commands.custom_embeds.HttpClient") as dry_client:
            dry_client.return_value.request.return_value = _DummyResponse(
                {
                    "customEmbed": {
                        "id": "embed-1",
                        "revision": "1",
                        "name": "Old Header",
                        "position": "HEAD",
                        "embedData": {"category": "ESSENTIAL", "html": "<script>old()</script>"},
                    }
                }
            )
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = custom_embeds.cmd_custom_embeds_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            with patch("wix_safe_agent_cli.commands.custom_embeds.HttpClient") as apply_client:
                apply_client.return_value.request.side_effect = [
                    _DummyResponse(
                        {
                            "customEmbed": {
                                "id": "embed-1",
                                "revision": "1",
                                "name": "Old Header",
                                "position": "HEAD",
                                "embedData": {"category": "ESSENTIAL", "html": "<script>old()</script>"},
                            }
                        }
                    ),
                    _DummyResponse(
                        {
                            "customEmbed": {
                                "id": "embed-1",
                                "revision": "1",
                                "name": "Old Header",
                                "position": "HEAD",
                                "embedData": {"category": "ESSENTIAL", "html": "<script>old()</script>"},
                            }
                        }
                    ),
                    _DummyResponse(
                        {
                            "customEmbed": {
                                "id": "embed-1",
                                "revision": "2",
                                "name": "New Header",
                                "position": "HEAD",
                                "embedData": {"category": "ESSENTIAL", "html": "<script>new()</script>"},
                            }
                        }
                    ),
                    _DummyResponse(
                        {
                            "customEmbed": {
                                "id": "embed-1",
                                "revision": "2",
                                "name": "New Header",
                                "position": "HEAD",
                                "embedData": {"category": "ESSENTIAL", "html": "<script>new()</script>"},
                            }
                        }
                    ),
                ]
                apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = custom_embeds.cmd_custom_embeds_update(args, apply_ctx)
                payload = json.loads(buf.getvalue())

            self.assertEqual(dry_rc, 0)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["name"], "New Header")
            patch_call = apply_client.return_value.request.call_args_list[2]
            self.assertEqual(patch_call.kwargs["method"], "PATCH")
            self.assertEqual(patch_call.kwargs["json_body"]["customEmbed"]["id"], "embed-1")
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.custom_embeds.HttpClient")
    def test_custom_embeds_delete_requires_ack(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"customEmbed": {"id": "embed-1", "revision": "1", "name": "Header", "position": "HEAD"}}
        )
        args = SimpleNamespace(custom_embed_id="embed-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            custom_embeds.cmd_custom_embeds_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = custom_embeds.cmd_custom_embeds_delete(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path, ack_irreversible=False),
                )
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertFalse(payload.get("refused", False))
        finally:
            Path(plan_path).unlink()

    def test_custom_embeds_delete_apply_verifies_404(self) -> None:
        args = SimpleNamespace(custom_embed_id="embed-1")

        with patch("wix_safe_agent_cli.commands.custom_embeds.HttpClient") as dry_client:
            dry_client.return_value.request.return_value = _DummyResponse(
                {"customEmbed": {"id": "embed-1", "revision": "1", "name": "Header", "position": "HEAD"}}
            )
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                custom_embeds.cmd_custom_embeds_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            with patch("wix_safe_agent_cli.commands.custom_embeds.HttpClient") as apply_client:
                apply_client.return_value.request.side_effect = [
                    _DummyResponse(
                        {"customEmbed": {"id": "embed-1", "revision": "1", "name": "Header", "position": "HEAD"}}
                    ),
                    _DummyResponse(
                        {"customEmbed": {"id": "embed-1", "revision": "1", "name": "Header", "position": "HEAD"}}
                    ),
                    _DummyResponse({}),
                    RuntimeError("HTTP 404 for GET https://www.wixapis.com/embeds/v1/custom-embeds/embed-1\n{}"),
                ]
                apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path, ack_irreversible=True)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = custom_embeds.cmd_custom_embeds_delete(args, apply_ctx)
                payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["actual_http_status"], 404)
        finally:
            Path(plan_path).unlink()
