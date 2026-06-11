from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from figma_safe_agent_cli.cli import main
from figma_safe_agent_cli.http import HttpResponse


class TestAuthCheck(unittest.TestCase):
    def test_auth_check_does_not_leak_token(self) -> None:
        token = "super_secret_token_123"
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "FIGMA_BASE_URL=http://example.invalid",
                        "FIGMA_AUTH_MODE=personal",
                        f"FIGMA_ACCESS_TOKEN={token}",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            class FakeHttpClient:
                def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
                    _ = (timeout_s, verbose, user_agent)

                def request(
                    self,
                    method: str,
                    url: str,
                    **kwargs,
                ) -> HttpResponse:
                    _ = kwargs
                    return HttpResponse(
                        status=200,
                        headers={"content-type": "application/json"},
                        body=b'{"id":"user_1"}',
                        url=f"{url}",
                    )

            with patch("figma_safe_agent_cli.commands.auth.HttpClient", FakeHttpClient):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "--output", "json", "auth", "check"])
                    self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())

            self.assertTrue(payload["ok"])
            self.assertEqual(payload["auth_mode"], "personal")
            self.assertEqual(payload["token_source"], "env")
            self.assertIn("oauth_token_json", payload["token_status"])
            self.assertEqual(payload["live_probe"]["ok"], True)
            payload_text = buf.getvalue()
            self.assertNotIn(token, payload_text)

    def test_auth_check_blocks_without_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(["FIGMA_BASE_URL=http://example.invalid", "FIGMA_AUTH_MODE=personal"]) + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--output", "json", "auth", "check"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["token_present"], False)
            self.assertFalse(payload["live_probe"]["attempted"])
            self.assertEqual(payload["live_probe"]["status"], "blocked")
            self.assertIn("no token available", payload["live_probe"]["reason"].lower())

    def test_auth_check_blocks_when_probe_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(["FIGMA_BASE_URL=http://example.invalid", "FIGMA_AUTH_MODE=personal", "FIGMA_ACCESS_TOKEN=bad-token"]) + "\n",
                encoding="utf-8",
            )

            class FakeHttpClient:
                def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
                    _ = (timeout_s, verbose, user_agent)

                def request(
                    self,
                    method: str,
                    url: str,
                    **kwargs,
                ) -> HttpResponse:
                    _ = (method, url, kwargs)
                    return HttpResponse(
                        status=403,
                        headers={"content-type": "application/json"},
                        body=b'{"status":"forbidden"}',
                        url=f"{url}",
                    )

            with patch("figma_safe_agent_cli.commands.auth.HttpClient", FakeHttpClient):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "--output", "json", "auth", "check"])
                    self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertTrue(payload["live_probe"]["attempted"])
            self.assertFalse(payload["live_probe"]["ok"])
            self.assertIn("probe failed with status 403", payload["live_probe"]["reason"])

    def test_auth_check_plan_mode_with_token_keeps_success(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "FIGMA_BASE_URL=http://example.invalid",
                        "FIGMA_AUTH_MODE=plan",
                        "FIGMA_ACCESS_TOKEN=plan-token",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            class BadHttpClient:
                def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
                    _ = (timeout_s, verbose, user_agent)

                def request(
                    self,
                    method: str,
                    url: str,
                    **kwargs,
                ) -> HttpResponse:
                    raise AssertionError(
                        f"did not expect live probe in plan mode: {method} {url} {kwargs}"
                    )

            with patch("figma_safe_agent_cli.commands.auth.HttpClient", BadHttpClient):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "--output", "json", "auth", "check"])
                self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["live_probe"]["attempted"])

    def test_auth_check_skip_live_reports_skipped_probe(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "FIGMA_BASE_URL=http://example.invalid",
                        "FIGMA_AUTH_MODE=personal",
                        "FIGMA_ACCESS_TOKEN=skip-token",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            class BadHttpClient:
                def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
                    _ = (timeout_s, verbose, user_agent)

                def request(
                    self,
                    method: str,
                    url: str,
                    **kwargs,
                ) -> HttpResponse:
                    raise AssertionError(
                        f"did not expect live probe with --skip-live: {method} {url} {kwargs}"
                    )

            with patch("figma_safe_agent_cli.commands.auth.HttpClient", BadHttpClient):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "--output", "json", "auth", "check", "--skip-live"])
                self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["token_present"])
            self.assertFalse(payload["live_probe"]["attempted"])
            self.assertEqual(payload["live_probe"]["reason"], "skipped by --skip-live")
