from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from statuspage_api_tool.cli import main


class TestCommandWiring(unittest.TestCase):
    def _env_file(self, tmpdir: str) -> Path:
        env_path = Path(tmpdir) / ".env"
        env_path.write_text("STATUSPAGE_BASE_URL=https://status.example.com\n", encoding="utf-8")
        return env_path

    def _fake_request_for(
        self,
        *,
        expected_url: str,
        status_code: int,
        body: str,
        content_type: str = "application/json",
    ):
        _status_code = int(status_code)
        _body = str(body)
        _content_type = str(content_type)

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
            self.assertEqual(url, expected_url)

            class _Resp:
                status_code = _status_code
                headers = {"content-type": _content_type}
                url = expected_url
                content = _body.encode("utf-8")
                text = _body

            return _Resp()

        return _fake_request

    def test_status_get(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/api/v2/status.json",
                status_code=200,
                body='{"status":{"indicator":"none","description":"All Systems Operational"}}',
            )

            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "status", "get"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], "/api/v2/status.json")

    def test_summary_get(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/api/v2/summary.json",
                status_code=200,
                body='{"status":{"indicator":"minor","description":"Minor Service Issues"}}',
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "summary", "get"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], "/api/v2/summary.json")

    def test_incidents_list(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/api/v2/incidents.json",
                status_code=200,
                body='{"incidents":[]}',
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "incidents", "list"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], "/api/v2/incidents.json")

    def test_maintenances_list(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/api/v2/scheduled-maintenances.json",
                status_code=200,
                body='{"scheduled_maintenances":[]}',
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "maintenances", "list"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], "/api/v2/scheduled-maintenances.json")

    def test_non_2xx_is_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/api/v2/status.json",
                status_code=500,
                body="oops",
                content_type="text/plain",
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "status", "get"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ToolError")

    def test_invalid_json_is_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/api/v2/status.json",
                status_code=200,
                body="not json",
                content_type="text/plain",
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "status", "get"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ToolError")
