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
from wix_safe_agent_cli.commands import bi_event
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


class TestBiEventCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="app-token",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=True,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli bi-event send",
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

    def _args(self, **kwargs) -> SimpleNamespace:
        data = {
            "event_name": "app_setup_finished",
            "event_data_json": None,
        }
        data.update(kwargs)
        return SimpleNamespace(**data)

    def test_parser_recognizes_bi_event_send(self) -> None:
        parser = build_parser()

        parsed = parser.parse_args(["bi-event", "send", "--event-name", "app_setup_finished"])
        self.assertEqual(parsed.bi_event_cmd, "send")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_bi_event_send")

    def test_bi_event_send_dry_run_builds_plan_and_writes_plan_out(self) -> None:
        args = self._args(event_data_json='{"step":"configured"}')
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            plan_path = handle.name

        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = bi_event.cmd_bi_event_send(args, self._ctx(plan_out=plan_path))
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["method"], "bi-event.send")
            self.assertEqual(payload["plan"]["request"]["method"], "POST")
            self.assertEqual(payload["plan"]["request"]["path"], "/apps/v1/bi-event")
            self.assertEqual(
                payload["plan"]["request"]["body"],
                {"eventName": "app_setup_finished", "eventData": {"step": "configured"}},
            )
            self.assertEqual(payload["plan"]["selector"]["event_name"], "app_setup_finished")
            self.assertTrue(Path(plan_path).exists())
            written_plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
            self.assertEqual(written_plan["request"]["body"]["eventName"], "app_setup_finished")
        finally:
            Path(plan_path).unlink(missing_ok=True)

    @patch("wix_safe_agent_cli.commands.bi_event.HttpClient")
    def test_bi_event_send_apply_without_plan_in_is_refused_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        args = self._args()
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bi_event.cmd_bi_event_send(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.bi_event.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.bi_event.HttpClient")
    def test_bi_event_send_apply_with_plan_posts_event(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"accepted": True})

        args = self._args(event_data_json='{"step":"configured"}')
        plan = {
            "method": "bi-event.send",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {
                    "kind": "wix-bi-event",
                    "operation": "send",
                    "event_name": "app_setup_finished",
                    "event_data": {"step": "configured"},
                },
                "before_state": {},
            },
        }
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".json") as handle:
            json.dump(plan, handle)
            plan_path = handle.name

        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = bi_event.cmd_bi_event_send(args, self._ctx(apply=True, yes=True, plan_in=plan_path))
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["method"], "bi-event.send")
            self.assertEqual(mock_client.return_value.request.call_count, 1)
            call = mock_client.return_value.request.call_args.kwargs
            self.assertEqual(call["method"], "POST")
            self.assertEqual(call["url"], "https://www.wixapis.com/apps/v1/bi-event")
            self.assertEqual(call["headers"]["Authorization"], "app-token")
            self.assertEqual(call["json_body"], {"eventName": "app_setup_finished", "eventData": {"step": "configured"}})
        finally:
            Path(plan_path).unlink(missing_ok=True)
