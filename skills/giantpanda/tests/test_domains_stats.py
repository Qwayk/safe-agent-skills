from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

import requests

from giantpanda_api_tool.cli import main


class TestDomainsStats(unittest.TestCase):
    def _mock_response(self, status: int = 200, payload: object = None) -> object:
        if payload is None:
            payload = {"rows": []}

        def response(*_args, **_kwargs):  # noqa: ANN001
            body = json.dumps(payload).encode("utf-8")
            headers = {"content-type": "application/json"}
            return SimpleNamespace(
                status_code=status,
                content=body,
                url="https://account.giantpanda.com/api/v1/domains/stats/",
                headers=headers,
                text=json.dumps(payload),
            )

        return response

    def test_domains_stats_validates_date_order(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("GIANTPANDA_API_TOKEN=t\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_path,
                        "domains",
                        "stats",
                        "--start-date",
                        "2026-08-10",
                        "--end-date",
                        "2026-08-01",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertIn("start_date must be <=", payload["error"])

    def test_domains_stats_missing_token_is_ready_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("GIANTPANDA_API_TOKEN=your_token_here\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_path,
                        "domains",
                        "stats",
                        "--start-date",
                        "2026-08-01",
                        "--end-date",
                        "2026-08-10",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "AuthenticationError")

    def test_domains_stats_http_failure_error_type_and_no_token_leak(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            token = "sentinel_token_123"
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"GIANTPANDA_API_TOKEN={token}\n")
            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                req.side_effect = requests.RequestException("provider network issue")
                out = io.StringIO()
                with redirect_stdout(out):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "domains",
                            "stats",
                            "--start-date",
                            "2026-08-01",
                            "--end-date",
                            "2026-08-10",
                        ]
                    )
            self.assertEqual(rc, 1)
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["error_type"], "ProviderError")
            self.assertNotIn(token, out.getvalue())

    def test_domains_stats_output_has_status_in_provider_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("GIANTPANDA_API_TOKEN=t\n")

            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                req.side_effect = self._mock_response(payload={"status": "ok"})
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "domains",
                            "stats",
                            "--start-date",
                            "2026-08-01",
                            "--end-date",
                            "2026-08-10",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertFalse("status" in payload)
            self.assertIn("status", payload["provider"])

    def test_domains_stats_verbose_does_not_leak_token(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            token = "sentinel_verbose_123"
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"GIANTPANDA_API_TOKEN={token}\n")

            def response(*_args, **_kwargs):
                body = b"{}"
                return SimpleNamespace(
                    status_code=200,
                    content=body,
                    url="https://account.giantpanda.com/api/v1/domains/stats/",
                    headers={"content-type": "application/json"},
                    text="{}",
                )

            with patch("giantpanda_api_tool.http.requests.Session.request", side_effect=response):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "--verbose",
                            "domains",
                            "stats",
                            "--start-date",
                            "2026-08-01",
                            "--end-date",
                            "2026-08-10",
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertNotIn(token, stderr.getvalue())
            self.assertIn("***REDACTED***", stderr.getvalue())

    def test_domains_stats_calls_fixed_host_with_query(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("GIANTPANDA_API_TOKEN=t\n")

            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                req.side_effect = self._mock_response()
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "domains",
                            "stats",
                            "--start-date",
                            "2026-08-01",
                            "--end-date",
                            "2026-08-10",
                            "--page",
                            "2",
                            "--page-size",
                            "50",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["provider"]["endpoint"], "/api/v1/domains/stats/")
            req.assert_called_once()
            self.assertIn("api/v1/domains/stats/", req.call_args.kwargs["url"])
            self.assertEqual(req.call_args.kwargs["params"]["start_date"], "2026-08-01")
            self.assertEqual(req.call_args.kwargs["params"]["end_date"], "2026-08-10")
            self.assertEqual(req.call_args.kwargs["params"]["page"], 2)
            self.assertEqual(req.call_args.kwargs["params"]["page_size"], 50)
            self.assertEqual(req.call_args.kwargs["headers"]["Authorization"], "Token t")
