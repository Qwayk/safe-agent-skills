from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import embedded_scripts
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEmbeddedScriptsCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
            api_key=None,
            account_id=None,
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "command_str": "wix-safe-agent-cli embedded-scripts embed",
            "enforce_reviewed_plan": True,
        }

    def test_parser_recognizes_embedded_scripts_get(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["embedded-scripts", "get", "--component-id", "cmp-123"])

        self.assertEqual(parsed.embedded_scripts_cmd, "get")
        self.assertFalse(parsed.write_capable)
        self.assertIs(parsed.func, embedded_scripts.cmd_embedded_scripts_get)

    def test_parser_recognizes_embedded_scripts_embed(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "embedded-scripts",
                "embed",
                "--component-id",
                "cmp-123",
                "--disabled",
                "true",
                "--parameters-json",
                '{"k":"v"}',
            ]
        )

        self.assertEqual(parsed.embedded_scripts_cmd, "embed")
        self.assertTrue(parsed.write_capable)
        self.assertIs(parsed.func, embedded_scripts.cmd_embedded_scripts_embed)

    @patch("wix_safe_agent_cli.commands.embedded_scripts.HttpClient")
    def test_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"script": {"componentId": "cmp-123"}})
        args = SimpleNamespace(component_id="cmp-123")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = embedded_scripts.cmd_embedded_scripts_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/apps/v1/scripts")
        self.assertEqual(payload["request"]["params"], {"componentId": "cmp-123"})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertEqual(call.kwargs["params"], {"componentId": "cmp-123"})

    @patch("wix_safe_agent_cli.commands.embedded_scripts.HttpClient")
    def test_get_omits_component_id_when_not_provided(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"script": {}})
        args = SimpleNamespace(component_id=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = embedded_scripts.cmd_embedded_scripts_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["params"], {})

        call = mock_client.return_value.request.call_args
        self.assertIsNone(call.kwargs["params"])

    @patch("wix_safe_agent_cli.commands.embedded_scripts.HttpClient")
    def test_get_rejects_empty_component_id(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(component_id="  ")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = embedded_scripts.cmd_embedded_scripts_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--component-id cannot be empty", payload["error"])

    @patch("wix_safe_agent_cli.commands.embedded_scripts.HttpClient")
    def test_embed_writes_plan_with_before_state_snapshot(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"script": {"componentId": "cmp-123", "disabled": False}})
        args = SimpleNamespace(component_id="cmp-123", disabled="true", parameters_json='{"k":"v"}')
        ctx = self._ctx()

        with TemporaryDirectory() as tmpdir:
            plan_path = Path(tmpdir) / "plan.json"
            ctx.update({"plan_out": str(plan_path), "plan_in": None, "apply": False, "yes": False, "receipt_out": None})

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = embedded_scripts.cmd_embedded_scripts_embed(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan_out"], str(plan_path))
            self.assertTrue(plan_path.exists())
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(plan["method"], "embedded-scripts.embed")
            self.assertEqual(plan["request"]["method"], "POST")
            self.assertEqual(
                plan["request"]["body"],
                {"componentId": "cmp-123", "disabled": True, "parameters": {"k": "v"}},
            )
            self.assertEqual(plan["baseline"]["before_state"], {"script": {"componentId": "cmp-123", "disabled": False}})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.embedded_scripts.HttpClient")
    def test_embed_direct_apply_without_plan_in_refuses_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"script": {"componentId": "cmp-123", "disabled": False}})
        args = SimpleNamespace(component_id="cmp-123", disabled="false", parameters_json=None)
        ctx = self._ctx()
        ctx.update({"plan_out": None, "plan_in": None, "apply": True, "yes": True, "receipt_out": None})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = embedded_scripts.cmd_embedded_scripts_embed(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self.assertIn("reviewed saved plan", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)
        first_call = mock_client.return_value.request.call_args_list[0]
        self.assertEqual(first_call.kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.embedded_scripts.HttpClient")
    def test_embed_apply_with_plan_in_posts_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"script": {"componentId": "cmp-123", "disabled": False, "parameters": {"k": "old"}}}),
            _DummyResponse({"ok": True}),
            _DummyResponse({"script": {"componentId": "cmp-123", "disabled": True, "parameters": {"k": "v"}}}),
        ]
        args = SimpleNamespace(component_id="cmp-123", disabled="true", parameters_json='{"k":"v"}')
        ctx = self._ctx()

        with TemporaryDirectory() as tmpdir:
            plan_path = Path(tmpdir) / "plan.json"
            plan = {
                "method": "embedded-scripts.embed",
                "baseline": {
                    "env_fingerprint": ctx["cfg"].base_url,
                    "selector": {
                        "kind": "wix-embedded-script",
                        "componentId": "cmp-123",
                        "body_signature": json.dumps(
                            {"componentId": "cmp-123", "disabled": True, "parameters": {"k": "v"}},
                            sort_keys=True,
                        ),
                    },
                    "before_state": {"script": {"componentId": "cmp-123", "disabled": False, "parameters": {"k": "old"}}},
                },
                "selector": {
                    "kind": "wix-embedded-script",
                    "componentId": "cmp-123",
                    "body_signature": json.dumps(
                        {"componentId": "cmp-123", "disabled": True, "parameters": {"k": "v"}},
                        sort_keys=True,
                    ),
                },
                "request": {
                    "method": "POST",
                    "path": "/apps/v1/scripts",
                    "body": {"componentId": "cmp-123", "disabled": True, "parameters": {"k": "v"}},
                },
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            ctx.update({"plan_in": str(plan_path), "plan_out": None, "apply": True, "yes": True, "receipt_out": None})

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = embedded_scripts.cmd_embedded_scripts_embed(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            receipt = payload["receipt"]
            self.assertEqual(receipt["request"]["body"]["componentId"], "cmp-123")
            self.assertEqual(receipt["verification"]["after"]["script"]["parameters"], {"k": "v"})

        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0].kwargs["method"], "GET")
        self.assertEqual(calls[1].kwargs["method"], "POST")
        self.assertEqual(calls[1].kwargs["json_body"], {"componentId": "cmp-123", "disabled": True, "parameters": {"k": "v"}})
        self.assertEqual(calls[2].kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.embedded_scripts.HttpClient")
    def test_embed_rejects_non_string_parameter_values(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(component_id=None, disabled="false", parameters_json='{"k":123}')
        ctx = self._ctx()
        ctx.update({"plan_out": None, "plan_in": None, "apply": False, "yes": False, "receipt_out": None})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = embedded_scripts.cmd_embedded_scripts_embed(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--parameters-json[k] must be a string", payload["error"])
