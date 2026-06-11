from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from qwayk_pipedrive_safe_agent_cli.cli import main


class _Response:
    def __init__(self, status: int, body: dict[str, object], headers: dict[str, str] | None = None, url: str = "https://api.test.pipedrive.com/api/v1/users/me") -> None:
        self.status = status
        self.headers = headers or {}
        self.body = json.dumps(body).encode("utf-8")
        self.url = url

    def json(self) -> object:
        return json.loads(self.body.decode("utf-8"))


class _HttpClient:
    def __init__(self, responses: list[_Response]) -> None:
        self._responses = list(responses)
        self.requests: list[tuple[str, str, dict[str, str] | None, dict[str, str] | None]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, object] | None = None,
        **kwargs: object,
    ) -> _Response:
        self.requests.append((method, url, headers or {}, params or {}))
        return self._responses.pop(0)


class _RaiseTokenErrorClient:
    def __init__(self, token: str) -> None:
        self.token = token
        self.requests: list[tuple[str, str, dict[str, str] | None, dict[str, str] | None]] = []

    def request(self, method: str, url: str, *, headers: dict[str, str] | None = None, params: dict[str, str] | None = None, **kwargs: object) -> _Response:
        self.requests.append((method, url, headers or {}, params or {}))
        raise RuntimeError(f"token blocked: {headers.get('x-api-token')}")


class TestAuthCheck(unittest.TestCase):
    def _build_env(self, td: str, token: str = "token-abc") -> str:
        env_path = os.path.join(td, "env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("PIPEDRIVE_API_DOMAIN=test-company\n")
            f.write(f"PIPEDRIVE_API_TOKEN={token}\n")
        return env_path

    def test_auth_check_uses_x_api_token(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._build_env(td)
            client = _HttpClient([_Response(200, {"data": {"id": 42}})])

            buf = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", return_value=client):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "auth", "check"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["operation"], "GET /api/v1/users/me")
            self.assertEqual(client.requests[0][0], "GET")
            self.assertEqual(client.requests[0][2].get("x-api-token"), "token-abc")

    def test_auth_check_error_does_not_leak_token(self) -> None:
        token = "very-secret-token"
        with tempfile.TemporaryDirectory() as td:
            env_path = self._build_env(td, token=token)
            client = _RaiseTokenErrorClient(token)

            buf = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", return_value=client):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "auth", "check"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "RuntimeError")
            self.assertNotIn(token, payload["error"])
