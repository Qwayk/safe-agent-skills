from __future__ import annotations

import json
import unittest

from pinterest_api_tool.api import PinterestApi
from pinterest_api_tool.http import HttpResponse


class _FakeHttp:
    def __init__(self, responses: list[dict]) -> None:
        self._responses = list(responses)
        self.calls: list[dict] = []

    def request(self, method: str, url: str, **kwargs):  # noqa: ANN001
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        if not self._responses:
            raise AssertionError("No more fake responses available")
        data = self._responses.pop(0)
        return HttpResponse(status=200, headers={}, body=json.dumps(data).encode("utf-8"), url=url)


class TestPagination(unittest.TestCase):
    def test_list_all_pages_until_bookmark_empty(self) -> None:
        http = _FakeHttp(
            [
                {"items": [{"id": "1"}, {"id": "2"}], "bookmark": "b1"},
                {"items": [{"id": "3"}], "bookmark": None},
            ]
        )
        api = PinterestApi(base_url="https://api.pinterest.com/v5", http=http, access_token="X")
        items, bookmark, pages = api.list_all("/pins", params={}, limit=100, page_size=100, bookmark=None)

        self.assertEqual([x["id"] for x in items], ["1", "2", "3"])
        self.assertIsNone(bookmark)
        self.assertEqual(pages, 2)

        self.assertEqual(len(http.calls), 2)
        self.assertEqual(http.calls[0]["method"], "GET")
        self.assertIn("/pins", http.calls[0]["url"])
        params0 = http.calls[0]["kwargs"].get("params") or {}
        self.assertEqual(params0["page_size"], 100)
        self.assertNotIn("bookmark", params0)

        params1 = http.calls[1]["kwargs"].get("params") or {}
        self.assertEqual(params1["bookmark"], "b1")

    def test_list_all_respects_limit(self) -> None:
        http = _FakeHttp(
            [
                {"items": [{"id": "1"}, {"id": "2"}], "bookmark": "b1"},
                {"items": [{"id": "3"}], "bookmark": "b2"},
            ]
        )
        api = PinterestApi(base_url="https://api.pinterest.com/v5", http=http, access_token="X")
        items, bookmark, pages = api.list_all("/pins", params={}, limit=2, page_size=100, bookmark=None)
        self.assertEqual([x["id"] for x in items], ["1", "2"])
        self.assertEqual(bookmark, "b1")
        self.assertEqual(pages, 1)
