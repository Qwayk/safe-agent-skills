from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.commands import app_installations
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


class TestAppInstallationsCommands(unittest.TestCase):
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

    @patch("wix_safe_agent_cli.commands.app_installations.HttpClient")
    def test_app_installations_query_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"appInstallations": [], "pagingMetadata": {"cursors": {"next": "cursor-2"}}}
        )
        args = SimpleNamespace(
            query_json=None,
            filter_json='{"status":{"$eq":"INSTALLED"}}',
            sort_json='{"fieldName":"createdDate","order":"DESC"}',
            fields_json='["appId","siteInfo.siteUrl"]',
            cursor="cursor-1",
            limit=10,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = app_installations.cmd_app_installations_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/app/installations/v1/app-installation/query")
        body = payload["request"]["body"]
        self.assertEqual(body["query"]["cursorPaging"]["cursor"], "cursor-1")
        self.assertEqual(body["query"]["cursorPaging"]["limit"], 10)
        self.assertEqual(body["query"]["filter"]["status"]["$eq"], "INSTALLED")

    @patch("wix_safe_agent_cli.commands.app_installations.HttpClient")
    def test_app_installations_search_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"appInstallations": [], "pagingMetadata": {"cursors": {"next": "cursor-2"}}}
        )
        args = SimpleNamespace(
            search="site owner",
            search_json=None,
            fields_json='["siteInfo.siteUrl","review.title"]',
            cursor="cursor-2",
            limit=3,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = app_installations.cmd_app_installations_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/app/installations/v1/app-installation/search")
        body = payload["request"]["body"]
        self.assertEqual(body["search"]["search"]["expression"], "site owner")
        self.assertEqual(body["search"]["cursorPaging"]["cursor"], "cursor-2")
        self.assertEqual(body["search"]["cursorPaging"]["limit"], 3)
