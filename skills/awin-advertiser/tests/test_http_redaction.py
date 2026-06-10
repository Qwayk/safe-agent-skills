from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from awin_advertiser_safe_agent_cli.cli import main
from awin_advertiser_safe_agent_cli.http import HttpClient


def _response(*, status: int, url: str, body: str) -> requests.Response:
    resp = requests.Response()
    resp.status_code = status
    resp.url = url
    resp._content = body.encode("utf-8")
    resp.headers["content-type"] = "application/json"
    return resp


class TestHttpRedaction(unittest.TestCase):
    def test_verbose_success_redacts_access_token_in_logs(self) -> None:
        client = HttpClient(timeout_s=5.0, verbose=True, user_agent="test-agent")
        client._session.request = Mock(  # type: ignore[method-assign]
            return_value=_response(
                status=200,
                url="https://api.awin.com/advertisers/123/publishers?accessToken=token123",
                body='{"ok":true}',
            )
        )

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            response = client.request(
                "GET",
                "https://api.awin.com/advertisers/123/publishers",
                headers={"Authorization": "Bearer token123"},
                params={"accessToken": "token123"},
            )

        log_text = stderr.getvalue()
        self.assertNotIn("token123", log_text)
        self.assertIn("accessToken=***REDACTED***", log_text)
        self.assertEqual(response.url, "https://api.awin.com/advertisers/123/publishers?accessToken=***REDACTED***")

    def test_http_error_redacts_url_and_provider_body(self) -> None:
        client = HttpClient(timeout_s=5.0, verbose=True, user_agent="test-agent")
        client._session.request = Mock(  # type: ignore[method-assign]
            return_value=_response(
                status=401,
                url="https://api.awin.com/advertisers/123/publishers?accessToken=token123",
                body='{"error":"bad token token123","accessToken":"token123","Authorization":"Bearer token123"}',
            )
        )

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            with self.assertRaises(RuntimeError) as ctx:
                client.request(
                    "GET",
                    "https://api.awin.com/advertisers/123/publishers",
                    headers={"Authorization": "Bearer token123"},
                    params={"accessToken": "token123"},
                )

        error_text = str(ctx.exception)
        log_text = stderr.getvalue()
        self.assertNotIn("token123", error_text)
        self.assertNotIn("token123", log_text)
        self.assertIn("***REDACTED***", error_text)
        self.assertIn("accessToken=***REDACTED***", error_text)
        self.assertIn("Authorization", error_text)

    def test_request_exception_redacts_verbose_and_error_message(self) -> None:
        client = HttpClient(timeout_s=5.0, verbose=True, user_agent="test-agent")
        client._session.request = Mock(  # type: ignore[method-assign]
            side_effect=requests.RequestException(
                "connection failed for https://api.awin.com/x?accessToken=token123 with Authorization: Bearer token123"
            )
        )

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            with self.assertRaises(RuntimeError) as ctx:
                client.request(
                    "GET",
                    "https://api.awin.com/x",
                    headers={"Authorization": "Bearer token123"},
                    params={"accessToken": "token123"},
                )

        error_text = str(ctx.exception)
        self.assertNotIn("token123", error_text)
        self.assertNotIn("token123", stderr.getvalue())
        self.assertIn("accessToken=***REDACTED***", error_text)


class TestCliHttpErrorRedaction(unittest.TestCase):
    @patch.object(requests.Session, "request")
    def test_cli_http_error_redacts_stdout_stderr_and_audit(self, request_mock) -> None:
        request_mock.return_value = _response(
            status=401,
            url="https://api.awin.com/advertisers/123/publishers?accessToken=token123",
            body='{"error":"bad token token123","accessToken":"token123","Authorization":"Bearer token123"}',
        )

        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            log_path = Path(td) / "audit.jsonl"
            env_path.write_text(
                "AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token123\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--log-file",
                        str(log_path),
                        "--verbose",
                        "publishers",
                        "list",
                        "--advertiser-id",
                        "123",
                    ]
                )

            self.assertEqual(rc, 1)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ok"])
            combined = stdout.getvalue() + stderr.getvalue() + log_path.read_text(encoding="utf-8")
            self.assertNotIn("token123", combined)
            self.assertIn("***REDACTED***", combined)
            self.assertIn("accessToken=***REDACTED***", payload["error"])
