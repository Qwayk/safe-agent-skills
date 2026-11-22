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
        expected_timeout: float | None = None,
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
            _ = (headers, params, json, data)
            if expected_timeout is not None:
                self.assertEqual(timeout, expected_timeout)
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
            summary = {
                "status": {"indicator": "major", "description": "Major Outage"},
                "incidents": [{"id": "incident-1", "status": "investigating"}],
                "scheduled_maintenances": [{"id": "maintenance-1", "status": "scheduled"}],
                "components": [{"id": "component-1", "status": "major_outage"}],
            }
            fake = self._fake_request_for(
                expected_url="https://status.example.com/api/v2/summary.json",
                status_code=200,
                body=json.dumps(summary),
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "summary", "get"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], "/api/v2/summary.json")
            self.assertEqual(payload["data"], summary)

    def test_summary_accepts_empty_lists_without_components(self) -> None:
        summary = {"status": {"indicator": "none"}, "incidents": [], "scheduled_maintenances": []}
        fake = self._fake_request_for(
            expected_url="https://status.example.com/api/v2/summary.json",
            status_code=200,
            body=json.dumps(summary),
        )
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, patch.dict("os.environ", {}, clear=True):
            with patch("requests.Session.request", new=fake), redirect_stdout(buf):
                rc = main(["--env-file", str(self._env_file(d)), "summary", "get"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(buf.getvalue())["data"], summary)

    def test_incomplete_replies_are_errors(self) -> None:
        cases = [
            ("status get", "status", "null", "JSON object"),
            ("status get", "status", '{"status":{}}', "status indicator"),
            ("status get", "status", '{"status":{"indicator":" "}}', "status indicator"),
            ("summary get", "summary", '{"status":{"indicator":"none"}}', "incidents"),
            (
                "summary get",
                "summary",
                '{"status":{"indicator":"none"},"incidents":[]}',
                "scheduled_maintenances",
            ),
            ("incidents list", "incidents", '{"incidents":null}', "incidents"),
            ("maintenances list", "scheduled-maintenances", "{}", "scheduled_maintenances"),
        ]
        with tempfile.TemporaryDirectory() as d, patch.dict("os.environ", {}, clear=True):
            env_path = self._env_file(d)
            for command, route, body, detail in cases:
                with self.subTest(command=command, body=body):
                    fake = self._fake_request_for(
                        expected_url=f"https://status.example.com/api/v2/{route}.json",
                        status_code=200,
                        body=body,
                    )
                    buf = io.StringIO()
                    with patch("requests.Session.request", new=fake), redirect_stdout(buf):
                        rc = main(["--env-file", str(env_path), *command.split()])
                    self.assertEqual(rc, 1)
                    payload = json.loads(buf.getvalue())
                    self.assertFalse(payload["ok"])
                    self.assertEqual(payload["error_type"], "ToolError")
                    self.assertIn(detail, payload["error"])

    def test_explicit_flags_override_invalid_settings(self) -> None:
        fake = self._fake_request_for(
            expected_url="https://status.example.com/api/v2/status.json",
            status_code=200,
            body='{"status":{"indicator":"none"}}',
            expected_timeout=5,
        )
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "STATUSPAGE_BASE_URL=old-page\nSTATUSPAGE_TIMEOUT_S=slow\n", encoding="utf-8"
            )
            for variables in ({}, {"STATUSPAGE_BASE_URL": "stale", "STATUSPAGE_TIMEOUT_S": "invalid"}):
                with self.subTest(variables=variables):
                    buf = io.StringIO()
                    with (
                        patch.dict("os.environ", variables, clear=True),
                        patch("requests.Session.request", new=fake),
                        redirect_stdout(buf),
                    ):
                        rc = main([
                            "--env-file", str(env_path), "--base-url", "https://status.example.com",
                            "--timeout-s", "5", "status", "get",
                        ])
                    self.assertEqual(rc, 0)
                    self.assertEqual(json.loads(buf.getvalue())["base_url"], "https://status.example.com")

    def test_invalid_explicit_timeout_stops_before_the_request(self) -> None:
        for timeout in ("0", "-1", "inf", "nan"):
            with self.subTest(timeout=timeout):
                buf = io.StringIO()
                with patch("requests.Session.request") as request, redirect_stdout(buf):
                    rc = main([
                        "--base-url", "https://status.example.com", "--timeout-s", timeout, "status", "get",
                    ])
                self.assertEqual(rc, 1)
                self.assertEqual(json.loads(buf.getvalue())["error_type"], "ValidationError")
                request.assert_not_called()

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
