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


class TestCatalogsReportingCommands(unittest.TestCase):
    def test_product_group_products_list_builds_path_and_params(self) -> None:
        http = _FakeHttp([{"items": [{"id": "p1"}], "bookmark": None}])
        ctx = {
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
        args = SimpleNamespace(
            ad_account_id="123",
            product_group_id="pg1",
            limit=10,
            page_size=100,
            bookmark=None,
            param=["foo=bar"],
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = catalogs_cmd.cmd_catalogs_product_group_products_list(args, ctx)
        self.assertEqual(rc, 0)

        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["product_group_id"], "pg1")
        self.assertEqual(payload["count"], 1)

        self.assertEqual(len(http.calls), 1)
        self.assertIn("/catalogs/product_groups/pg1/products", str(http.calls[0]["url"]))
        params = http.calls[0]["params"] or {}
        self.assertEqual(params["ad_account_id"], "123")
        self.assertEqual(params["foo"], "bar")
        self.assertEqual(params["page_size"], 100)

    def test_item_issues_list_builds_path_and_params(self) -> None:
        http = _FakeHttp([{"items": [{"id": "i1"}], "bookmark": None}])
        ctx = {
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
        args = SimpleNamespace(
            processing_result_id="pr1",
            ad_account_id="123",
            limit=10,
            page_size=100,
            bookmark=None,
            param=None,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = catalogs_cmd.cmd_catalogs_processing_result_item_issues_list(args, ctx)
        self.assertEqual(rc, 0)

        self.assertEqual(len(http.calls), 1)
        self.assertIn("/catalogs/processing_results/pr1/item_issues", str(http.calls[0]["url"]))
        params = http.calls[0]["params"] or {}
        self.assertEqual(params["ad_account_id"], "123")
        self.assertEqual(params["page_size"], 100)

    def test_reports_list_and_stats_paths(self) -> None:
        http = _FakeHttp(
            [
                {"items": [{"id": "r1"}], "bookmark": None},  # reports list
                {"stats": {}},  # reports stats
            ]
        )
        ctx = {
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
        list_args = SimpleNamespace(
            ad_account_id="123",
            limit=10,
            page_size=100,
            bookmark=None,
            param=None,
        )
        stats_args = SimpleNamespace(ad_account_id="123", param=["foo=bar"])

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc0 = catalogs_cmd.cmd_catalogs_reports_list(list_args, ctx)
        self.assertEqual(rc0, 0)
        payload0 = json.loads(buf.getvalue())
        self.assertTrue(payload0["ok"])
        self.assertEqual(payload0["count"], 1)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc1 = catalogs_cmd.cmd_catalogs_reports_stats(stats_args, ctx)
        self.assertEqual(rc1, 0)

        self.assertEqual(len(http.calls), 2)
        self.assertIn("/catalogs/reports", str(http.calls[0]["url"]))
        params0 = http.calls[0]["params"] or {}
        self.assertEqual(params0["ad_account_id"], "123")
        self.assertEqual(params0["page_size"], 100)

        self.assertIn("/catalogs/reports/stats", str(http.calls[1]["url"]))
        params1 = http.calls[1]["params"] or {}
        self.assertEqual(params1["ad_account_id"], "123")
        self.assertEqual(params1["foo"], "bar")

