from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from requests import Response

from hacker_news_api_tool.cli import main


def _maxitem_response() -> Response:
    response = Response()
    response.status_code = 200
    response.headers["Content-Type"] = "application/json"
    response._content = b"12345"
    return response


class TestAuthAndFlags(unittest.TestCase):
    def test_auth_check_json_no_env_needed(self) -> None:
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / "missing.env"
            with patch.dict(os.environ, clear=True), patch(
                "requests.Session.request", return_value=_maxitem_response()
            ) as request, redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])
            self.assertFalse(env_path.exists())
        self.assertEqual(rc, 0)
        self.assertEqual(request.call_args.kwargs["url"], "https://hacker-news.firebaseio.com/v0/maxitem.json")
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "hacker-news-api-tool")
        self.assertFalse(payload["data"]["auth"]["required"])
        self.assertEqual(payload["endpoint"], "/v0/maxitem.json")

    def test_config_file_can_supply_api_root(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cfg_path = Path(d) / "config.json"
            cfg_path.write_text(json.dumps({"api_root": "https://status.example.com/v0"}), encoding="utf-8")

            def _fake_request(  # type: ignore[no-untyped-def]
                _session,
                *,
                method,
                url,
                headers=None,
                params=None,
                json=None,
                data=None,
                timeout=None,
            ):
                _ = (headers, params, json, data, timeout)
                self.assertEqual(method, "GET")
                self.assertEqual(url, "https://status.example.com/v0/maxitem.json")

                class _Resp:
                    status_code = 200
                    headers = {"content-type": "application/json"}
                    url = "https://status.example.com/v0/maxitem.json"
                    content = b"12345"
                    text = "12345"

                return _Resp()

            buf = io.StringIO()
            with patch("requests.Session.request", new=_fake_request):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--config", str(cfg_path), "maxitem", "get"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], "/v0/maxitem.json")

    def test_api_root_flag_works_without_env_file(self) -> None:
        def _fake_request(  # type: ignore[no-untyped-def]
            _session,
            *,
            method,
            url,
            headers=None,
            params=None,
            json=None,
            data=None,
            timeout=None,
        ):
            _ = (headers, params, json, data, timeout)
            self.assertEqual(method, "GET")
            self.assertEqual(url, "https://status.example.com/v0/maxitem.json")

            class _Resp:
                status_code = 200
                headers = {"content-type": "application/json"}
                url = "https://status.example.com/v0/maxitem.json"
                content = b"12345"
                text = "12345"

            return _Resp()

        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / "does-not-exist.env"
            buf = io.StringIO()
            with patch("requests.Session.request", new=_fake_request):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--api-root",
                            "https://status.example.com/v0",
                            "maxitem",
                            "get",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])

    def test_api_root_flag_overrides_file_and_shell_settings(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("HACKER_NEWS_API_ROOT=https://file.example/v0\n", encoding="utf-8")
            for settings in ({}, {"HACKER_NEWS_API_ROOT": "https://shell.example/v0"}):
                with self.subTest(settings=settings), patch.dict(os.environ, settings, clear=True), patch(
                    "requests.Session.request", return_value=_maxitem_response()
                ) as request, redirect_stdout(io.StringIO()):
                    rc = main([
                        "--env-file", str(env_path), "--api-root", "https://flag.example/v0/",
                        "maxitem", "get",
                    ])
                    self.assertEqual(rc, 0)
                    self.assertEqual(request.call_args.kwargs["url"], "https://flag.example/v0/maxitem.json")

    def test_onboarding_command_can_create_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            example_path = Path(d) / ".env.example"
            example_path.write_text(
                "HACKER_NEWS_API_ROOT=https://hacker-news.firebaseio.com/v0\nHACKER_NEWS_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["env_created"])
            self.assertTrue(env_path.exists())

    def test_log_file_writes_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            log_path = Path(d) / "audit.jsonl"
            buf = io.StringIO()
            with patch("requests.Session.request", return_value=_maxitem_response()), redirect_stdout(buf):
                rc = main(["--output", "json", "--log-file", str(log_path), "auth", "check"])
            self.assertEqual(rc, 0)
            rows = log_path.read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(rows), 1)
            first = json.loads(rows[0])
            self.assertIn("event", first)
