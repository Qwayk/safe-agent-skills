from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from pinterest_api_tool.commands import conversions as conversions_cmd
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


class TestConversionsCommands(unittest.TestCase):
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

    def test_conversions_tags_list_builds_path_and_params(self) -> None:
        http = _FakeHttp([{"items": [{"id": "t1"}], "bookmark": None}])
        args = SimpleNamespace(ad_account_id="123", limit=10, page_size=7, bookmark="b0", param=["foo=bar"])

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = conversions_cmd.cmd_conversions_tags_list(args, self._ctx(http))
        self.assertEqual(rc, 0)

        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/ad_accounts/123/conversion_tags")
        self.assertEqual(payload["params"]["foo"], "bar")
        self.assertEqual(payload["count"], 1)

        self.assertEqual(len(http.calls), 1)
        self.assertIn("/ad_accounts/123/conversion_tags", str(http.calls[0]["url"]))
        params = http.calls[0]["params"] or {}
        self.assertEqual(params["page_size"], 7)
        self.assertEqual(params["bookmark"], "b0")
        self.assertEqual(params["foo"], "bar")

    def test_conversions_tags_get_builds_path_and_params(self) -> None:
        http = _FakeHttp([{"id": "t1"}])
        args = SimpleNamespace(ad_account_id="123", id="t1", param=["foo=bar"])

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = conversions_cmd.cmd_conversions_tags_get(args, self._ctx(http))
        self.assertEqual(rc, 0)

        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/ad_accounts/123/conversion_tags/t1")

        self.assertEqual(len(http.calls), 1)
        self.assertIn("/ad_accounts/123/conversion_tags/t1", str(http.calls[0]["url"]))
        params = http.calls[0]["params"] or {}
        self.assertEqual(params["foo"], "bar")

    def test_conversions_simple_get_endpoints_build_paths(self) -> None:
        cases = [
            (conversions_cmd.cmd_conversions_page_visit, "/ad_accounts/123/conversion_tags/page_visit"),
            (conversions_cmd.cmd_conversions_ocpm_eligible, "/ad_accounts/123/conversion_tags/ocpm_eligible"),
            (conversions_cmd.cmd_conversions_eqs, "/ad_accounts/123/conversion_eqs"),
        ]
        for fn, expected_path in cases:
            http = _FakeHttp([{"ok": True}])
            args = SimpleNamespace(ad_account_id="123", param=["foo=bar"])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = fn(args, self._ctx(http))
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], expected_path)

            self.assertEqual(len(http.calls), 1)
            self.assertIn(expected_path, str(http.calls[0]["url"]))
            params = http.calls[0]["params"] or {}
            self.assertEqual(params["foo"], "bar")

