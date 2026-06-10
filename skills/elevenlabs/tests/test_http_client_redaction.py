from __future__ import annotations

import unittest
from unittest.mock import patch

from elevenlabs_api_tool.http import HttpClient


class _DummyResponse:
    def __init__(self, *, status_code: int, url: str, content: bytes):
        self.status_code = status_code
        self.url = url
        self.headers = {"content-type": "text/plain"}
        self.content = content

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


class TestHttpClientRedaction(unittest.TestCase):
    def test_http_error_message_redacts_secrets(self) -> None:
        api_key = "secret-token"
        response = _DummyResponse(
            status_code=401,
            url="https://api.elevenlabs.io/v1/user",
            content=b"Unauthorized: key=secret-token",
        )
        with patch("elevenlabs_api_tool.http.requests.Session.request", return_value=response):
            client = HttpClient(
                timeout_s=1.0,
                verbose=False,
                user_agent="elevenlabs-api-tool/test",
                secrets=(api_key,),
            )
            with self.assertRaises(RuntimeError) as cm:
                client.request("GET", "https://api.elevenlabs.io/v1/user")
            message = str(cm.exception)
            self.assertNotIn(api_key, message)
            self.assertIn("[REDACTED]", message)
