from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from openai_api_tool.audit_log import AuditLogger
from openai_api_tool.commands.auth import cmd_auth_check
from openai_api_tool.output import Output


class TestAuthCheckLive(unittest.TestCase):
    def _cfg(self, **overrides: object) -> SimpleNamespace:
        cfg = SimpleNamespace(
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
            organization_id=None,
            project_id=None,
            timeout_s=30,
        )
        for field, value in overrides.items():
            setattr(cfg, field, value)
        return cfg

    def _ctx(self, *, live: bool, cfg_overrides: dict[str, object] | None = None) -> dict[str, object]:
        cfg = self._cfg(**(cfg_overrides or {}))
        return {
            "cfg": cfg,
            "tool_version": "0.1.0",
            "timeout_s": cfg.timeout_s,
            "verbose": False,
            "live": live,
            "audit": AuditLogger(path=None, enabled=False),
            "out": Output(mode="json"),
        }

    def _args(self) -> SimpleNamespace:
        return SimpleNamespace()

    def test_offline_auth_check_does_not_hit_api(self) -> None:
        ctx = self._ctx(live=False)
        buf = io.StringIO()
        with patch("openai_api_tool.commands.auth.HttpClient.request") as mock_request:
            with redirect_stdout(buf):
                rc = cmd_auth_check(self._args(), ctx)
        self.assertEqual(rc, 0)
        mock_request.assert_not_called()
        self.assertFalse(ctx["out"].last["live_checked"])
        self.assertFalse(ctx["out"].last["live_allowed"])

    def test_live_auth_check_calls_api(self) -> None:
        ctx = self._ctx(live=True)
        response = SimpleNamespace(status=200, headers={"content-type": "application/json"}, body=b"{}", url="https://api.openai.com/v1/models")
        buf = io.StringIO()
        with patch("openai_api_tool.commands.auth.HttpClient.request", return_value=response) as mock_request:
            with redirect_stdout(buf):
                rc = cmd_auth_check(self._args(), ctx)
        self.assertEqual(rc, 0)
        mock_request.assert_called_once()
        payload = ctx["out"].last
        self.assertTrue(payload["live_checked"])
        self.assertTrue(payload["live_ok"])
        self.assertEqual(payload["live_status_code"], 200)
        self.assertTrue(payload["live_allowed"])

    def test_live_auth_check_handles_http_error(self) -> None:
        ctx = self._ctx(live=True)
        error_message = "HTTP 401 Unauthorized\n{\"error\": \"invalid_key\"}"
        buf = io.StringIO()
        with patch("openai_api_tool.commands.auth.HttpClient.request", side_effect=RuntimeError(error_message)):
            with redirect_stdout(buf):
                rc = cmd_auth_check(self._args(), ctx)
        self.assertEqual(rc, 0)
        payload = ctx["out"].last
        self.assertFalse(payload["ok"])
        self.assertFalse(payload["live_ok"])
        self.assertEqual(payload["live_status_code"], 401)
        self.assertEqual(payload["error_type"], "HttpError")
        self.assertIn("HTTP 401", payload["error"])
