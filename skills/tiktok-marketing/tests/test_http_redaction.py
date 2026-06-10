from __future__ import annotations

import unittest

import requests

from tiktok_marketing_safe_agent_cli.http import HttpClient


class _Response:
    def __init__(self, *, status_code: int, url: str, body: str, headers: dict[str, str] | None = None):
        self.status_code = status_code
        self.headers = headers or {"content-type": "text/plain"}
        self.url = url
        self.body = body.encode("utf-8")
        self.text = body

    def json(self) -> dict[str, object]:
        return {}


class _Session:
    def __init__(
        self,
        response: _Response,
        *,
        should_raise: bool = False,
        raise_message: str = "",
    ):
        self._response = response
        self._should_raise = should_raise
        self._raise_message = raise_message

    def request(self, *_args, **_kwargs) -> _Response:  # noqa: ARG002
        if self._should_raise:
            raise requests.RequestException(self._raise_message)
        return self._response


class TestHttpRedaction(unittest.TestCase):
    def test_http_error_message_sanitizes_secret_query_params(self) -> None:
        client = HttpClient(timeout_s=1, verbose=False, user_agent="test-agent")
        client._session = _Session(
            response=_Response(
                status_code=403,
                url=(
                    "https://business-api.tiktok.com/open_api/v1.3/advertiser/balance/get/"
                    "?app_id=app-123&secret=very-secret-token&advertiser_id=123"
                ),
                body='{"message":"secret=very-secret-token"}',
            )
        )

        with self.assertRaises(RuntimeError) as cm:
            client.request(
                "GET",
                "https://business-api.tiktok.com/open_api/v1.3/advertiser/balance/get/",
                params={"app_id": "app-123", "secret": "very-secret-token", "advertiser_id": "123"},
            )
        error = str(cm.exception)
        self.assertNotIn("very-secret-token", error)
        self.assertIn("secret=***REDACTED***", error)
        self.assertIn("HTTP 403", error)

    def test_request_exception_message_sanitizes_secret_query_params(self) -> None:
        client = HttpClient(timeout_s=1, verbose=False, user_agent="test-agent")
        client._session = _Session(
            response=_Response(status_code=200, url="https://example.invalid", body="{}"),
            should_raise=True,
            raise_message="Request failed for secret=very-secret-token",
        )

        with self.assertRaises(RuntimeError) as cm:
            client.request(
                "GET",
                "https://example.invalid",
                params={"secret": "very-secret-token"},
            )
        error = str(cm.exception)
        self.assertNotIn("very-secret-token", error)
        self.assertIn("secret=***REDACTED***", error)
