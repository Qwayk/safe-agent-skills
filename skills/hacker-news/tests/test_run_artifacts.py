from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from hacker_news_api_tool.cli import main


class TestCommandWiring(unittest.TestCase):
    def _env_file(self, tmpdir: str) -> Path:
        env_path = Path(tmpdir) / ".env"
        env_path.write_text("HACKER_NEWS_API_ROOT=https://status.example.com/v0\n", encoding="utf-8")
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
        _url = str(expected_url)

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
                url = _url
                content = _body.encode("utf-8")
                text = _body

            return _Resp()

        return _fake_request

    def test_items_get(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/v0/item/1234.json",
                status_code=200,
                body='{"id":1234,"type":"story"}',
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(
                        ["--output", "json", "--env-file", str(env_path), "items", "get", "--id", "1234"]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], "/v0/item/1234.json")

    def test_users_get(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/v0/user/alice.json",
                status_code=200,
                body='{"id":"alice","created":100}',
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(
                        ["--output", "json", "--env-file", str(env_path), "users", "get", "--id", "alice"]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], "/v0/user/alice.json")

    def test_stories_top(self) -> None:
        self._assert_story_command("top", "/v0/topstories.json")

    def test_stories_new(self) -> None:
        self._assert_story_command("new", "/v0/newstories.json")

    def test_stories_best(self) -> None:
        self._assert_story_command("best", "/v0/beststories.json")

    def test_stories_ask(self) -> None:
        self._assert_story_command("ask", "/v0/askstories.json")

    def test_stories_show(self) -> None:
        self._assert_story_command("show", "/v0/showstories.json")

    def test_stories_jobs(self) -> None:
        self._assert_story_command("jobs", "/v0/jobstories.json")

    def _assert_story_command(self, story_type: str, endpoint: str) -> None:
        route = "job" if story_type == "jobs" else story_type
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url=f"https://status.example.com/v0/{route}stories.json",
                status_code=200,
                body='[1,2,3]',
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "stories", story_type])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], endpoint)

    def test_maxitem_get(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/v0/maxitem.json",
                status_code=200,
                body='12345',
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "maxitem", "get"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], "/v0/maxitem.json")

    def test_updates_get(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/v0/updates.json",
                status_code=200,
                body='{"items":[],"profiles":[]}',
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "updates", "get"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["endpoint"], "/v0/updates.json")

    def test_auth_check_is_live_read(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/v0/maxitem.json",
                status_code=200,
                body='12345',
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["data"]["auth"]["required"], False)
            self.assertEqual(payload["endpoint"], "/v0/maxitem.json")

    def test_items_null_is_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/v0/item/9999.json",
                status_code=200,
                body="null",
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(
                        ["--output", "json", "--env-file", str(env_path), "items", "get", "--id", "9999"]
                    )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Item '9999' was not found", payload["error"])

    def test_users_null_is_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/v0/user/ghost.json",
                status_code=200,
                body="null",
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(
                        ["--output", "json", "--env-file", str(env_path), "users", "get", "--id", "ghost"]
                    )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("User 'ghost' was not found", payload["error"])

    def test_non_2xx_is_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/v0/maxitem.json",
                status_code=500,
                body="oops",
                content_type="text/plain",
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "maxitem", "get"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ToolError")

    def test_invalid_json_is_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(d)
            fake = self._fake_request_for(
                expected_url="https://status.example.com/v0/maxitem.json",
                status_code=200,
                body="not json",
                content_type="text/plain",
            )
            buf = io.StringIO()
            with patch("requests.Session.request", new=fake):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "maxitem", "get"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ToolError")
