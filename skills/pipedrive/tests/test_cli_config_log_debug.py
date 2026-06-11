from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from qwayk_pipedrive_safe_agent_cli.cli import main


class _Response:
    def __init__(self, status: int, body: dict[str, object], url: str = "https://api.test.pipedrive.com/api/v1/users/me") -> None:
        self.status = status
        self.headers = {}
        self.body = json.dumps(body).encode("utf-8")
        self.url = url

    def json(self) -> object:
        return json.loads(self.body.decode("utf-8"))


class _HttpClient:
    last: "_HttpClient | None" = None

    def __init__(self, timeout_s: float, verbose: bool, user_agent: str) -> None:
        _HttpClient.last = self
        self.timeout_s = timeout_s
        self.verbose = verbose
        self.user_agent = user_agent
        self.requests: list[tuple[str, str, dict[str, str], dict[str, Any] | None]] = []
        self._responses: list[_Response] = [_Response(200, {"data": {"id": 12345, "name": "ok"}})]

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: object,
    ) -> _Response:
        self.requests.append((method, url, dict(headers or {}), params))
        if not self._responses:
            return _Response(200, {"data": []})
        return self._responses.pop(0)


class _FailingHttpClient:
    last: "_FailingHttpClient | None" = None

    def __init__(self, timeout_s: float, verbose: bool, user_agent: str) -> None:
        _FailingHttpClient.last = self
        self.timeout_s = timeout_s
        self.verbose = verbose
        self.user_agent = user_agent
        self.token = ""

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: object,
    ) -> _Response:
        self.token = (headers or {}).get("x-api-token", "")
        raise RuntimeError(f"request token blocked: {self.token}")


class TestCliFlagsAndConfig(unittest.TestCase):
    def _write_env(self, root: str, token: str, domain: str = "env-company") -> str:
        env_path = os.path.join(root, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"PIPEDRIVE_API_DOMAIN={domain}\n")
            f.write(f"PIPEDRIVE_API_TOKEN={token}\n")
        return env_path

    def _write_config(self, root: str, values: dict[str, object]) -> str:
        config_path = os.path.join(root, "config.json")
        Path(config_path).write_text(json.dumps(values), encoding="utf-8")
        return config_path

    def test_config_file_values_and_timeout_flag_override(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td, token="env-token")
            config_path = self._write_config(td, {"base_url": "https://configured.example.com/api/v1", "timeout_s": 12})

            buf = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", new=_HttpClient):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "--config",
                            config_path,
                            "--timeout-s",
                            "5",
                            "auth",
                            "check",
                        ]
                    )
            client = _HttpClient.last
            self.assertIsNotNone(client)
            assert client is not None
            self.assertEqual(rc, 0)
            self.assertIsNotNone(client)
            self.assertEqual(client.timeout_s, 5.0)
            method, url, headers, _params = client.requests[0]
            self.assertEqual(method, "GET")
            self.assertEqual(url, "https://configured.example.com/api/v1/users/me")
            self.assertEqual(headers["x-api-token"], "env-token")
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["http"]["status"], 200)

    def test_config_does_not_accept_token_key(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td, token="env-token")
            config_path = self._write_config(td, {"token": "bad-token", "base_url": "https://configured.example.com"})
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "--config", config_path, "auth", "check"])
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("unknown keys", payload["error"])

    def test_debug_prints_redacted_stack_and_log_file_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            token = "very-secret-token"
            env_path = self._write_env(td, token=token)
            log_path = os.path.join(td, "audit.jsonl")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", new=_FailingHttpClient):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "--debug",
                            "--log-file",
                            log_path,
                            "auth",
                            "check",
                        ]
                    )

            self.assertEqual(rc, 1)
            stdout_payload = json.loads(stdout.getvalue())
            self.assertEqual(stdout_payload["error_type"], "RuntimeError")
            self.assertNotIn(token, stdout_payload["error"])
            err_text = stderr.getvalue()
            self.assertIn("Traceback", err_text)
            self.assertNotIn(token, err_text)
            log_rows = [json.loads(line) for line in Path(log_path).read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertGreaterEqual(len(log_rows), 2)
            self.assertFalse(any(token in json.dumps(row) for row in log_rows))
