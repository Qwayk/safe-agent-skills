from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from statuspage_api_tool.cli import main


class TestAuthAndFlags(unittest.TestCase):
    def test_auth_check_json_no_env_needed(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "auth", "check"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "statuspage-api-tool")
        self.assertFalse(payload["auth"]["required"])

    def test_config_file_can_supply_base_url(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cfg_path = Path(d) / "config.json"
            cfg_path.write_text(json.dumps({"base_url": "https://status.example.com"}), encoding="utf-8")

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
                self.assertEqual(url, "https://status.example.com/api/v2/status.json")

                class _Resp:
                    status_code = 200
                    headers = {"content-type": "application/json"}
                    url = "https://status.example.com/api/v2/status.json"
                    content = b'{"status":{"indicator":"none"}}'
                    text = '{"status":{"indicator":"none"}}'

                return _Resp()

            buf = io.StringIO()
            with patch("requests.Session.request", new=_fake_request):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--config", str(cfg_path), "status", "get"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])

    def test_base_url_flag_works_without_env_file(self) -> None:
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
            self.assertEqual(url, "https://status.example.com/api/v2/status.json")

            class _Resp:
                status_code = 200
                headers = {"content-type": "application/json"}
                url = "https://status.example.com/api/v2/status.json"
                content = b'{"status":{"indicator":"none"}}'
                text = '{"status":{"indicator":"none"}}'

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
                            "--base-url",
                            "https://status.example.com",
                            "status",
                            "get",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])

    def test_log_file_writes_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            log_path = Path(d) / "audit.jsonl"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--log-file", str(log_path), "auth", "check"])
            self.assertEqual(rc, 0)
            rows = log_path.read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(rows), 1)
            first = json.loads(rows[0])
            self.assertIn("event", first)
