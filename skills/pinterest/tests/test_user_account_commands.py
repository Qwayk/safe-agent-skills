from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from pinterest_api_tool.commands import user_account as user_account_cmd
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


class TestUserAccountCommands(unittest.TestCase):
    def test_user_account_get(self) -> None:
        http = _FakeHttp([{"id": "u1"}])
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
        args = SimpleNamespace()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = user_account_cmd.cmd_user_account_get(args, ctx)
        self.assertEqual(rc, 0)

        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/user_account")

        self.assertEqual(len(http.calls), 1)
        self.assertEqual(http.calls[0]["method"], "GET")
        self.assertIn("/user_account", str(http.calls[0]["url"]))

    def test_user_account_list_endpoints_build_paths_and_params(self) -> None:
        cases = [
            (user_account_cmd.cmd_user_account_businesses_list, "/user_account/businesses"),
            (user_account_cmd.cmd_user_account_followers_list, "/user_account/followers"),
            (user_account_cmd.cmd_user_account_following_list, "/user_account/following"),
            (user_account_cmd.cmd_user_account_following_boards_list, "/user_account/following/boards"),
            (user_account_cmd.cmd_user_account_websites_list, "/user_account/websites"),
        ]
        for fn, expected_path in cases:
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
            args = SimpleNamespace(limit=10, page_size=7, bookmark="b0", param=["foo=bar"])
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = fn(args, ctx)
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], expected_path)
            self.assertEqual(payload["params"]["foo"], "bar")
            self.assertEqual(payload["count"], 1)

            self.assertEqual(len(http.calls), 1)
            self.assertEqual(http.calls[0]["method"], "GET")
            self.assertIn(expected_path, str(http.calls[0]["url"]))
            params = http.calls[0]["params"] or {}
            self.assertEqual(params["page_size"], 7)
            self.assertEqual(params["bookmark"], "b0")
            self.assertEqual(params["foo"], "bar")

    def test_user_account_websites_verification(self) -> None:
        http = _FakeHttp([{"ok": True}])
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
        args = SimpleNamespace()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = user_account_cmd.cmd_user_account_websites_verification(args, ctx)
        self.assertEqual(rc, 0)

        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/user_account/websites/verification")

        self.assertEqual(len(http.calls), 1)
        self.assertEqual(http.calls[0]["method"], "GET")
        self.assertIn("/user_account/websites/verification", str(http.calls[0]["url"]))

