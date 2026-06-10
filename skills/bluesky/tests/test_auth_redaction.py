from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr

import requests

from bluesky_safe_agent_cli.http import HttpClient


class _FakeResponse:
    def __init__(self, *, status_code: int, url: str, headers: dict[str, str] | None, body: str) -> None:
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}
        self.content = body.encode("utf-8")

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


class TestAuthRedaction(unittest.TestCase):
    def test_auth_http_error_response_does_not_leak_app_password_or_tokens(self) -> None:
        access = "ACCESS.JWT.LEAK.123"
        refresh = "REFRESH.JWT.LEAK.456"
        app_password = "APP_PASSWORD_LEAK"
        client = HttpClient(timeout_s=1.0, verbose=True, user_agent="bluesky-safe-cli-test")

        secret_body = json.dumps(
            {
                "error": "InvalidToken",
                "accessJwt": access,
                "refreshJwt": refresh,
                "password": app_password,
                "message": "Auth failed",
            },
        )
        response = _FakeResponse(
            status_code=401,
            url=f"https://auth.example.invalid/xrpc/com.atproto.server.refreshSession?accessJwt={access}",
            headers={"content-type": "application/json"},
            body=secret_body,
        )

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            client._session.request = lambda **_: response  # type: ignore[method-assign]
            with self.assertRaises(RuntimeError) as cm:
                client.request(
                    "POST",
                    "https://auth.example.invalid/xrpc/com.atproto.server.refreshSession",
                    headers={"Authorization": f"Bearer {refresh}", "Content-Type": "application/json"},
                    params={"accessJwt": access},
                    json_body={"identifier": "alice.bsky.social", "password": app_password},
                )

        msg = str(cm.exception)
        self.assertIn("HTTP 401", msg)
        self.assertNotIn(access, msg)
        self.assertNotIn(refresh, msg)
        self.assertNotIn(app_password, msg)
        self.assertNotIn("BEARER", msg.upper())
        log = stderr.getvalue()
        self.assertNotIn(access, log)
        self.assertNotIn(refresh, log)
        self.assertNotIn(app_password, log)

    def test_auth_request_exception_message_does_not_leak_secret(self) -> None:
        refresh = "REFRESH.JWT.LEAK.REQUEST"
        app_password = "APP_PASSWORD_LEAK_REQ"
        client = HttpClient(timeout_s=1.0, verbose=True, user_agent="bluesky-safe-cli-test")

        def _raise(**_kwargs):  # noqa: ANN001
            raise requests.RequestException(f"boom Bearer {refresh} password={app_password}")

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            client._session.request = _raise  # type: ignore[method-assign]
            with self.assertRaises(RuntimeError) as cm:
                client.request(
                    "POST",
                    "https://auth.example.invalid/xrpc/com.atproto.server.createSession",
                    json_body={"identifier": "alice.bsky.social", "password": app_password},
                )

        msg = str(cm.exception)
        self.assertNotIn(refresh, msg)
        self.assertNotIn(app_password, msg)
        log = stderr.getvalue()
        self.assertNotIn(refresh, log)
        self.assertNotIn(app_password, log)
