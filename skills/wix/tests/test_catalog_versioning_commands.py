from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import catalog_versioning
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


class TestCatalogVersioningParser(unittest.TestCase):
    def test_parser_recognizes_catalog_versioning_get(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog-versioning", "get"])
        self.assertEqual(args.catalog_versioning_cmd, "get")
        self.assertFalse(args.write_capable)
        self.assertIs(args.func, catalog_versioning.cmd_catalog_versioning_get)


class TestCatalogVersioningCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    @patch("wix_safe_agent_cli.commands.catalog_versioning.HttpClient")
    def test_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"catalogVersion": "V3"})
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = catalog_versioning.cmd_catalog_versioning_get(SimpleNamespace(), ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "catalog-versioning.get")
        self.assertEqual(payload["request"]["path"], "/stores/v3/provision/version")
