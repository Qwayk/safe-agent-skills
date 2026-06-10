from __future__ import annotations

import json
import unittest
from unittest import mock

from instagram_api_tool.config import Config
from instagram_api_tool.errors import ToolError
from instagram_api_tool.http import HttpResponse
from instagram_api_tool.instagram_client import InstagramAPIClient


def _cfg() -> Config:
    return Config(
        base_url="https://graph.instagram.com",
        auth_api_base_url="https://api.instagram.com",
        auth_web_base_url="https://www.instagram.com",
        graph_version="v25.0",
        app_id="123456789012345",
        app_secret="SECRET_VALUE",
        redirect_uri="https://localhost.example.com/oauth/callback",
        ig_user_id=None,
        token=None,
        timeout_s=30.0,
    )


class TestInstagramClient(unittest.TestCase):
    def test_exchange_auth_code_uses_post_form(self) -> None:
        client = InstagramAPIClient(
            _cfg(),
            env_file=".env",
            timeout_s=30.0,
            verbose=False,
        )
        response = HttpResponse(
            status=200,
            headers={"content-type": "application/json"},
            body=json.dumps({"access_token": "TOKEN", "user_id": "17841400000000000"}).encode("utf-8"),
            url="https://api.instagram.com/oauth/access_token",
        )

        with mock.patch.object(client._http, "request", return_value=response) as request_mock:
            payload = client.exchange_auth_code(code="AUTH_CODE")

        self.assertEqual(payload["user_id"], "17841400000000000")
        request_mock.assert_called_once()
        _, url = request_mock.call_args.args
        self.assertEqual(request_mock.call_args.args[0], "POST")
        self.assertEqual(url, "https://api.instagram.com/oauth/access_token")
        self.assertIsNone(request_mock.call_args.kwargs["params"])
        self.assertEqual(
            request_mock.call_args.kwargs["data"],
            {
                "client_id": "123456789012345",
                "client_secret": "SECRET_VALUE",
                "grant_type": "authorization_code",
                "redirect_uri": "https://localhost.example.com/oauth/callback",
                "code": "AUTH_CODE",
            },
        )

    def test_auth_request_redacts_secret_values_in_errors(self) -> None:
        client = InstagramAPIClient(
            _cfg(),
            env_file=".env",
            timeout_s=30.0,
            verbose=False,
        )

        with mock.patch.object(
            client._http,
            "request",
            side_effect=RuntimeError(
                "Request failed for POST "
                "https://api.instagram.com/oauth/access_token?client_secret=SECRET_VALUE&code=AUTH_CODE"
            ),
        ):
            with self.assertRaises(ToolError) as cm:
                client.exchange_auth_code(code="AUTH_CODE")

        message = str(cm.exception)
        self.assertIn("***REDACTED***", message)
        self.assertNotIn("SECRET_VALUE", message)
        self.assertNotIn("AUTH_CODE", message)

    def test_auth_error_payload_is_treated_as_failure(self) -> None:
        client = InstagramAPIClient(
            _cfg(),
            env_file=".env",
            timeout_s=30.0,
            verbose=False,
        )
        response = HttpResponse(
            status=200,
            headers={"content-type": "application/json"},
            body=json.dumps({"error_type": "OAuthException", "error_message": "Bad code"}).encode("utf-8"),
            url="https://api.instagram.com/oauth/access_token",
        )

        with mock.patch.object(client._http, "request", return_value=response):
            with self.assertRaises(ToolError) as cm:
                client.exchange_auth_code(code="AUTH_CODE")

        self.assertIn("Instagram API error", str(cm.exception))
