from __future__ import annotations

import unittest
from unittest import mock

import requests

from stripe_api_tool.http import HttpClient


def _resp(*, status: int = 200, url: str = "https://api.stripe.com/v1/account") -> requests.Response:
    r = requests.Response()
    r.status_code = status
    r.url = url
    r._content = b'{"ok":true}'  # noqa: SLF001
    r.headers = {}
    return r


class TestHttpRetry(unittest.TestCase):
    @mock.patch("stripe_api_tool.http.time.sleep", return_value=None)
    def test_retries_transient_request_exception_then_succeeds(self, sleep: mock.Mock) -> None:
        client = HttpClient(timeout_s=1.0, verbose=False, user_agent="stripe-api-tool-tests")
        exc = requests.exceptions.ConnectionError("boom")
        ok = _resp(status=200)

        with mock.patch.object(client._session, "request", side_effect=[exc, ok]) as req:  # noqa: SLF001
            out = client.request("GET", "https://api.stripe.com/v1/account", retries=1)

        self.assertEqual(out.status, 200)
        self.assertEqual(req.call_count, 2)
        sleep.assert_called_once_with(2)

    @mock.patch("stripe_api_tool.http.time.sleep", return_value=None)
    def test_stops_after_retry_budget_for_request_exception(self, sleep: mock.Mock) -> None:
        client = HttpClient(timeout_s=1.0, verbose=False, user_agent="stripe-api-tool-tests")
        exc = requests.exceptions.Timeout("timeout")

        with mock.patch.object(client._session, "request", side_effect=[exc, exc]) as req:  # noqa: SLF001
            with self.assertRaises(RuntimeError) as ctx:
                client.request("GET", "https://api.stripe.com/v1/account", retries=1)

        self.assertIn("Timeout", str(ctx.exception))
        self.assertEqual(req.call_count, 2)
        sleep.assert_called_once_with(2)

