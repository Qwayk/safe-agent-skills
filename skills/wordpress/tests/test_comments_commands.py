import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from wordpress_api_tool.cli import main as cli_main
from wordpress_api_tool.http import HttpResponse


class CommentsCommandsTests(unittest.TestCase):
    def _run(self, argv):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = int(cli_main(list(argv)))
        stdout = out.getvalue()
        stderr = err.getvalue()
        payload = json.loads(stdout)
        return rc, stdout, stderr, payload

    def _env_file(self, td_path: Path) -> Path:
        env_path = td_path / ".env"
        env_path.write_text(
            "\n".join(
                [
                    "WP_BASE_URL=https://example.com",
                    "WP_USERNAME=fake_user",
                    "WP_APP_PASSWORD=fake_password",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return env_path

    def test_comments_list_hits_comments_endpoint_and_paginates(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            calls = []

            def _request(method, url, **kwargs):
                calls.append((method, url, kwargs.get("params")))
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/comments"), url)

                page = int((kwargs.get("params") or {}).get("page") or "1")
                if page == 1:
                    self.assertEqual(
                        kwargs.get("params"),
                        {"post": "10", "context": "view", "per_page": "3", "page": "1"},
                    )
                    body = json.dumps([{"id": 1}, {"id": 2}]).encode("utf-8")
                    return HttpResponse(status=200, headers={"x-wp-totalpages": "2", "x-wp-total": "4"}, body=body)
                if page == 2:
                    self.assertEqual(
                        kwargs.get("params"),
                        {"post": "10", "context": "view", "per_page": "3", "page": "2"},
                    )
                    body = json.dumps([{"id": 3}, {"id": 4}]).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)
                raise AssertionError(f"Unexpected page={page}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "comments",
                        "list",
                        "--post-id",
                        "10",
                        "--limit",
                        "3",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertEqual(payload.get("count"), 3)
            self.assertTrue(payload.get("truncated"))
            self.assertEqual(payload.get("truncated_reason"), "limit")
            self.assertEqual(payload.get("pages_fetched"), 2)
            self.assertEqual(payload.get("total"), 4)
            self.assertEqual(payload.get("total_pages"), 2)
            self.assertEqual(len(calls), 2)

    def test_comments_get_hits_comment_by_id_endpoint(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            raw = {"id": 123, "post": 10, "content": {"rendered": "<p>Hi</p>"}}

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/comments/123"), url)
                self.assertEqual(kwargs.get("params"), {"context": "view"})
                body = json.dumps(raw).encode("utf-8")
                return HttpResponse(status=200, headers={}, body=body)

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    ["--output", "json", "--env-file", str(env_path), "comments", "get", "--id", "123"]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertEqual(payload.get("id"), 123)
            self.assertIn("raw", payload)

