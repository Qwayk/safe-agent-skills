from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from amazon_creators_api_tool.errors import HttpError
from amazon_creators_api_tool.http import HttpClient


class TestHttpClient(unittest.TestCase):
    @patch("amazon_creators_api_tool.http.requests.Session.request")
    def test_non_retryable_error_raises_once(self, mock_request: MagicMock) -> None:
        response = MagicMock()
        response.status_code = 400
        response.url = "https://example"
        response.reason = "Bad Request"
        response.headers = {"x-amzn-requestid": "abc123"}
        response.content = b"bad"
        mock_request.return_value = response

        client = HttpClient(timeout_s=1, verbose=False, user_agent="ua")
        with self.assertRaises(HttpError) as ctx:
            client.request("GET", "https://example.com")
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.url, "https://example")
        self.assertEqual(ctx.exception.reason, "Bad Request")
        self.assertEqual(ctx.exception.request_id, "abc123")
