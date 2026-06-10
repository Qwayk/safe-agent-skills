import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from wordpress_api_tool.cli import main as cli_main
from wordpress_api_tool.http import HttpResponse


class SearchCommandsTests(unittest.TestCase):
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

    def test_search_query_hits_search_endpoint_and_paginates(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/search"), url)

                page = int((kwargs.get("params") or {}).get("page") or "1")
                if page == 1:
                    self.assertEqual(
                        kwargs.get("params"),
                        {"search": "hello", "per_page": "3", "page": "1"},
                    )
                    body = json.dumps([{"id": 1}, {"id": 2}]).encode("utf-8")
                    return HttpResponse(status=200, headers={"x-wp-totalpages": "2", "x-wp-total": "4"}, body=body)
                if page == 2:
                    self.assertEqual(
                        kwargs.get("params"),
                        {"search": "hello", "per_page": "3", "page": "2"},
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
                        "search",
                        "query",
                        "--query",
                        "hello",
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
            self.assertEqual(payload.get("total"), 4)

