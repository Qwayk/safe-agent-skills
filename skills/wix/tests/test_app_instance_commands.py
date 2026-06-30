from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import app_instance
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


class TestAppInstanceParser(unittest.TestCase):
    def test_parser_recognizes_app_instance_get(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["app-instance", "get"])

        self.assertEqual(parsed.app_instance_cmd, "get")
        self.assertFalse(parsed.write_capable)
        self.assertIs(parsed.func, app_instance.cmd_app_instance_get)


class TestAppInstanceCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, verbose: bool = False) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        if cfg_override:
            for key, value in cfg_override.items():
                setattr(cfg, key, value)
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": verbose,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    @patch("wix_safe_agent_cli.commands.app_instance.HttpClient")
    def test_app_instance_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"site": {"id": "site-1", "installedWixApps": ["wix_forms"]}}
        )
        args = SimpleNamespace()
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = app_instance.cmd_app_instance_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/apps/v1/instance")

        http_call = mock_client.return_value.request.call_args
        self.assertEqual(http_call.kwargs["headers"]["Authorization"], "token-abc")
