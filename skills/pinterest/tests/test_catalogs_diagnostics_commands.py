from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from pinterest_api_tool.commands import catalogs as catalogs_cmd
from pinterest_api_tool.config import Config
from pinterest_api_tool.http import HttpResponse
from pinterest_api_tool.output import Output


class _FakeHttp:
    def __init__(self, responses: list[dict]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def request(self, method: str, url: str, **kwargs):  # noqa: ANN001
        self.calls.append({"method": method, "url": url, "params": kwargs.get("params")})
        if not self._responses:
            raise AssertionError("No more fake responses available")
        data = self._responses.pop(0)
        return HttpResponse(status=200, headers={}, body=json.dumps(data).encode("utf-8"), url=url)


class _Audit:
    def write(self, event: str, payload):  # noqa: ANN001
        _ = event, payload


class TestCatalogsDiagnosticsCommands(unittest.TestCase):
    def _ctx(self, http: _FakeHttp) -> dict:
        return {
            "cfg": Config(
                base_url="https://api.pinterest.com/v5",
                access_token="X",
                app_id=None,
                app_secret=None,
                refresh_token=None,
                timeout_s=30,
            ),
            "http": http,
            "env_file": "/tmp/.env",
            "out": Output(mode="json"),
            "audit": _Audit(),
        }

    def test_catalogs_available_filter_values(self) -> None:
        http = _FakeHttp([{"ok": True}])
        args = SimpleNamespace(ad_account_id="123", param=["foo=bar"])

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = catalogs_cmd.cmd_catalogs_available_filter_values(args, self._ctx(http))
        self.assertEqual(rc, 0)

        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/catalogs/available_filter_values")

        self.assertEqual(len(http.calls), 1)
        self.assertIn("/catalogs/available_filter_values", str(http.calls[0]["url"]))
        params = http.calls[0]["params"] or {}
        self.assertEqual(params["ad_account_id"], "123")
        self.assertEqual(params["foo"], "bar")

    def test_catalogs_product_group_product_counts(self) -> None:
        http = _FakeHttp([{"ok": True}])
        args = SimpleNamespace(ad_account_id="123", product_group_id="pg1", param=["foo=bar"])

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = catalogs_cmd.cmd_catalogs_product_group_product_counts(args, self._ctx(http))
        self.assertEqual(rc, 0)

        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/catalogs/product_groups/pg1/product_counts")

        self.assertEqual(len(http.calls), 1)
        self.assertIn("/catalogs/product_groups/pg1/product_counts", str(http.calls[0]["url"]))
        params = http.calls[0]["params"] or {}
        self.assertEqual(params["ad_account_id"], "123")
        self.assertEqual(params["foo"], "bar")

    def test_catalogs_items_batch_get(self) -> None:
        http = _FakeHttp([{"ok": True}])
        args = SimpleNamespace(ad_account_id="123", batch_id="b1", param=["foo=bar"])

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = catalogs_cmd.cmd_catalogs_items_batch_get(args, self._ctx(http))
        self.assertEqual(rc, 0)

        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/catalogs/items/batch/b1")

        self.assertEqual(len(http.calls), 1)
        self.assertIn("/catalogs/items/batch/b1", str(http.calls[0]["url"]))
        params = http.calls[0]["params"] or {}
        self.assertEqual(params["ad_account_id"], "123")
        self.assertEqual(params["foo"], "bar")

