from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import interactive_form_sessions
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: bytes | dict, content_type: str = "application/json") -> None:
        if isinstance(payload, dict):
            self.body = json.dumps(payload).encode("utf-8")
        else:
            self.body = payload
        self.headers = {"content-type": content_type}
        self.status = 200
        self.url = "https://www.wixapis.com/test"

    def json(self):
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class TestInteractiveFormSessionsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli interactive-form-sessions",
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

    def test_parser_exposes_interactive_form_sessions_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["interactive-form-sessions", "create", "--session-json", '{"formId":"form-1"}'], "create", True),
            (
                ["interactive-form-sessions", "create-streamed", "--session-json", '{"formId":"form-1"}'],
                "create-streamed",
                True,
            ),
            (
                [
                    "interactive-form-sessions",
                    "send-message",
                    "--session-id",
                    "session-1",
                    "--message-json",
                    '{"input":"hello"}',
                ],
                "send-message",
                True,
            ),
            (
                [
                    "interactive-form-sessions",
                    "send-message-streamed",
                    "--session-id",
                    "session-1",
                    "--message-json",
                    '{"input":"hello"}',
                ],
                "send-message-streamed",
                True,
            ),
            (
                ["interactive-form-sessions", "generate-summary", "--form-json", '{"form":{"name":"Contact"}}'],
                "generate-summary",
                False,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.interactive_form_sessions_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.interactive_form_sessions.HttpClient")
    def test_generate_summary_uses_official_path_as_helper(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"formSummary": "A short summary"})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = interactive_form_sessions.cmd_interactive_form_sessions_generate_summary(
                SimpleNamespace(form_json='{"form":{"name":"Contact"}}'),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "POST")
        self.assertTrue(
            mock_client.return_value.request.call_args.kwargs["url"].endswith(
                "/forms/ai/v1/interactive-form-sessions/generate-form-summary"
            )
        )

    @patch("wix_safe_agent_cli.commands.interactive_form_sessions.HttpClient")
    def test_session_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        write_cases = [
            (
                interactive_form_sessions.cmd_interactive_form_sessions_create,
                SimpleNamespace(session_json='{"formId":"form-1","dryRun":true}'),
                "/forms/ai/v1/interactive-form-sessions",
                {"formId": "form-1"},
                False,
            ),
            (
                interactive_form_sessions.cmd_interactive_form_sessions_create_streamed,
                SimpleNamespace(session_json='{"formId":"form-1","dryRun":true}'),
                "/forms/ai/v1/interactive-form-sessions/create-streamed",
                {"formId": "form-1"},
                True,
            ),
            (
                interactive_form_sessions.cmd_interactive_form_sessions_send_message,
                SimpleNamespace(session_id="session-1", message_json='{"input":"hello"}'),
                "/forms/ai/v1/interactive-form-sessions/session-1/send-user-message",
                {"interactiveFormSessionId": "session-1"},
                False,
            ),
            (
                interactive_form_sessions.cmd_interactive_form_sessions_send_message_streamed,
                SimpleNamespace(session_id="session-1", message_json='{"input":"hello"}'),
                "/forms/ai/v1/interactive-form-sessions/session-1/send-user-message-streamed",
                {"interactiveFormSessionId": "session-1"},
                True,
            ),
        ]
        for func, args, path, selector, streamed in write_cases:
            with self.subTest(path=path):
                mock_client.return_value.request.reset_mock()
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], "POST")
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual(payload["plan"]["selector"], selector)
                self.assertEqual("headers" in payload["plan"]["request"], streamed)
                self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.interactive_form_sessions.HttpClient")
    def test_streamed_apply_can_return_raw_text(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(b"data: {\"chunk\":true}\n\n", "text/event-stream")
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/plan.json")
        plan = {
            "method": "interactive-form-sessions.create-streamed",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {"formId": "form-1"},
            },
        }
        with patch("wix_safe_agent_cli.commands.interactive_form_sessions.read_json_file", return_value=plan):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = interactive_form_sessions.cmd_interactive_form_sessions_create_streamed(
                    SimpleNamespace(session_json='{"formId":"form-1","dryRun":true}'),
                    ctx,
                )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["response"]["rawText"], 'data: {"chunk":true}\n\n')
        self.assertEqual(
            mock_client.return_value.request.call_args.kwargs["headers"]["Accept"],
            "text/event-stream",
        )

    @patch("wix_safe_agent_cli.commands.interactive_form_sessions.HttpClient")
    def test_send_message_validates_input_length(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = interactive_form_sessions.cmd_interactive_form_sessions_send_message(
                SimpleNamespace(session_id="session-1", message_json='{"input":""}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
