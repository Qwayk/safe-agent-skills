import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from wordpress_api_tool.cli import main as cli_main
from wordpress_api_tool.http import HttpResponse


class TermsCommandsTests(unittest.TestCase):
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

    def test_terms_list_hits_categories_endpoint_with_search(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/categories"), url)
                self.assertEqual(kwargs.get("params"), {"search": "hi", "context": "view", "per_page": "3", "page": "1"})
                body = json.dumps([{"id": 1, "name": "A"}, {"id": 2, "name": "B"}, {"id": 3, "name": "C"}]).encode(
                    "utf-8"
                )
                return HttpResponse(status=200, headers={"x-wp-totalpages": "1", "x-wp-total": "3"}, body=body)

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "terms",
                        "list",
                        "--taxonomy",
                        "categories",
                        "--query",
                        "hi",
                        "--limit",
                        "3",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertEqual(payload.get("count"), 3)
            self.assertFalse(payload.get("truncated"))

    def test_terms_get_hits_tags_endpoint_by_id(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            raw = {"id": 7, "name": "T", "slug": "t", "taxonomy": "post_tag"}

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/tags/7"), url)
                self.assertEqual(kwargs.get("params"), {"context": "view"})
                body = json.dumps(raw).encode("utf-8")
                return HttpResponse(status=200, headers={}, body=body)

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    ["--output", "json", "--env-file", str(env_path), "terms", "get", "--taxonomy", "tags", "--id", "7"]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertEqual(payload.get("id"), 7)
            self.assertIn("raw", payload)

