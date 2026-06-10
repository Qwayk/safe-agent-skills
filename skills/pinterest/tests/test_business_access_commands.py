from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from pinterest_api_tool.commands import business_access as business_access_cmd
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


class TestBusinessAccessCommands(unittest.TestCase):
    def test_business_access_endpoints_build_paths_and_params(self) -> None:
        cases = [
            (business_access_cmd.cmd_business_assets_list, "/businesses/b1/assets", {}),
            (business_access_cmd.cmd_business_members_list, "/businesses/b1/members", {}),
            (business_access_cmd.cmd_business_partners_list, "/businesses/b1/partners", {}),
            (
                business_access_cmd.cmd_business_asset_members_list,
                "/businesses/b1/assets/a1/members",
                {"asset_id": "a1"},
            ),
            (
                business_access_cmd.cmd_business_asset_partners_list,
                "/businesses/b1/assets/a1/partners",
                {"asset_id": "a1"},
            ),
            (
                business_access_cmd.cmd_business_member_assets_list,
                "/businesses/b1/members/m1/assets",
                {"member_id": "m1"},
            ),
            (
                business_access_cmd.cmd_business_partner_assets_list,
                "/businesses/b1/partners/p1/assets",
                {"partner_id": "p1"},
            ),
        ]
        for fn, expected_path, extra in cases:
            http = _FakeHttp([{"items": [{"id": "1"}], "bookmark": None}])
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
                business_id="b1",
                limit=10,
                page_size=20,
                bookmark=None,
                param=["foo=bar"],
                **extra,
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = fn(args, ctx)
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], expected_path)
            self.assertEqual(payload["business_id"], "b1")
            self.assertEqual(payload["params"]["foo"], "bar")

            self.assertEqual(len(http.calls), 1)
            self.assertEqual(http.calls[0]["method"], "GET")
            self.assertIn(expected_path, str(http.calls[0]["url"]))
            params = http.calls[0]["params"] or {}
            self.assertEqual(params["page_size"], 20)
            self.assertEqual(params["foo"], "bar")

