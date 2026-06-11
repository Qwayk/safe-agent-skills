from __future__ import annotations

import unittest
from unittest.mock import patch

from requests import Response

from sovrn_safe_agent_cli.errors import HttpError
from sovrn_safe_agent_cli.http import HttpClient


class TestHttpErrorHints(unittest.TestCase):
    def test_rate_limit_error_includes_retry_hint(self) -> None:
        client = HttpClient(timeout_s=30, verbose=False, user_agent="test/0.0.0")
        response = Response()
        response.status_code = 429
        response._content = b'{"error":"rate limited"}'
        response.headers["Retry-After"] = "60"
        response.url = "https://api.viglink.com/api/link/?key=site-key-123"

        with patch.object(client._session, "request", return_value=response):
            with self.assertRaises(HttpError) as cm:
                client.request("GET", "https://api.viglink.com/api/link/", params={"key": "site-key-123"})

        message = str(cm.exception)
        self.assertIn("HTTP 429", message)
        self.assertIn("Retry hint: wait 60 second(s) before retrying.", message)
        self.assertNotIn("site-key-123", message)
