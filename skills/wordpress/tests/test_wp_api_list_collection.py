import json
import unittest
from unittest.mock import patch

from wordpress_api_tool.http import HttpClient, HttpResponse
from wordpress_api_tool.wp_api import WordPressApi


class ListCollectionTests(unittest.TestCase):
    def _api(self) -> WordPressApi:
        http = HttpClient(timeout_s=1, verbose=False)
        return WordPressApi(base_url="https://example.com/wp-json/wp/v2", http=http, auth_header="Basic x")

    def test_limit_reached_without_totals_reports_truncated(self):
        api = self._api()

        def _request(method, url, **kwargs):
            self.assertEqual(method, "GET")
            self.assertTrue(url.endswith("/wp-json/wp/v2/posts"), url)
            self.assertEqual(kwargs.get("params"), {"per_page": "3", "page": "1"})
            body = json.dumps([{"id": 1}, {"id": 2}, {"id": 3}]).encode("utf-8")
            return HttpResponse(status=200, headers={}, body=body)

        with patch.object(api.http, "request", side_effect=_request):
            page = api.list_collection(
                "/posts",
                params=None,
                context=None,
                limit=3,
                per_page=3,
                max_pages=100,
                retries=0,
            )

        self.assertEqual(len(page["items"]), 3)
        self.assertTrue(page["truncated"])
        self.assertEqual(page["truncated_reason"], "limit")

    def test_limit_reached_on_short_page_without_totals_reports_truncated(self):
        api = self._api()

        def _request(method, url, **kwargs):
            self.assertEqual(method, "GET")
            self.assertTrue(url.endswith("/wp-json/wp/v2/posts"), url)
            self.assertEqual(kwargs.get("params"), {"per_page": "5", "page": "1"})
            body = json.dumps([{"id": 1}, {"id": 2}, {"id": 3}]).encode("utf-8")
            return HttpResponse(status=200, headers={}, body=body)

        with patch.object(api.http, "request", side_effect=_request):
            page = api.list_collection(
                "/posts",
                params=None,
                context=None,
                limit=3,
                per_page=5,
                max_pages=100,
                retries=0,
            )

        self.assertEqual(len(page["items"]), 3)
        self.assertTrue(page["truncated"])
        self.assertEqual(page["truncated_reason"], "limit")

    def test_limit_reached_on_short_page_with_totals_is_not_truncated(self):
        api = self._api()

        def _request(method, url, **kwargs):
            self.assertEqual(method, "GET")
            self.assertTrue(url.endswith("/wp-json/wp/v2/posts"), url)
            self.assertEqual(kwargs.get("params"), {"per_page": "5", "page": "1"})
            body = json.dumps([{"id": 1}, {"id": 2}, {"id": 3}]).encode("utf-8")
            return HttpResponse(
                status=200,
                headers={"x-wp-total": "3", "x-wp-totalpages": "1"},
                body=body,
            )

        with patch.object(api.http, "request", side_effect=_request):
            page = api.list_collection(
                "/posts",
                params=None,
                context=None,
                limit=3,
                per_page=5,
                max_pages=100,
                retries=0,
            )

        self.assertEqual(len(page["items"]), 3)
        self.assertFalse(page["truncated"])
        self.assertIsNone(page["truncated_reason"])
