from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import Mock, patch

import requests

from xero_safe_agent_cli.http import HttpClient


def response(status: int, url: str, *, retry_after: str | None = None) -> requests.Response:
    value = requests.Response()
    value.status_code = status
    value.url = url
    value._content = b'{}'
    if retry_after is not None:
        value.headers["Retry-After"] = retry_after
    return value


class TestHttpClient(unittest.TestCase):
    def test_verbose_log_never_includes_query_values(self) -> None:
        client = HttpClient(timeout_s=5, verbose=True, user_agent="test")
        private_url = (
            "https://api.xero.com/api.xro/2.0/Invoices?"
            "where=EmailAddress%3Dprivate%40example.com&token=secret-token"
        )
        client._session.request = Mock(return_value=response(200, private_url))
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            client.request(
                "GET",
                "https://api.xero.com/api.xro/2.0/Invoices",
                params={
                    "where": 'EmailAddress=="private@example.com"',
                    "token": "secret-token",
                },
            )
        rendered = stderr.getvalue()
        self.assertIn("https://api.xero.com/api.xro/2.0/Invoices", rendered)
        self.assertNotIn("private", rendered)
        self.assertNotIn("secret-token", rendered)
        self.assertNotIn("where=", rendered)

    def test_short_retry_after_waits_then_retries(self) -> None:
        client = HttpClient(timeout_s=5, verbose=False, user_agent="test")
        client._session.request = Mock(
            side_effect=[
                response(429, "https://api.xero.com/Invoices", retry_after="0.25"),
                response(200, "https://api.xero.com/Invoices"),
            ]
        )
        with patch("xero_safe_agent_cli.http.time.sleep") as sleep:
            result = client.request(
                "GET",
                "https://api.xero.com/Invoices",
                retries=1,
            )
        self.assertEqual(result.status, 200)
        sleep.assert_called_once_with(0.25)
        self.assertEqual(client._session.request.call_count, 2)

    def test_long_retry_after_returns_429_without_retrying_early(self) -> None:
        client = HttpClient(timeout_s=5, verbose=False, user_agent="test")
        client._session.request = Mock(
            side_effect=[
                response(429, "https://api.xero.com/Invoices", retry_after="120"),
                response(200, "https://api.xero.com/Invoices"),
            ]
        )
        with patch("xero_safe_agent_cli.http.time.sleep") as sleep:
            result = client.request(
                "GET",
                "https://api.xero.com/Invoices",
                retries=1,
            )
        self.assertEqual(result.status, 429)
        sleep.assert_not_called()
        self.assertEqual(client._session.request.call_count, 1)


if __name__ == "__main__":
    unittest.main()
