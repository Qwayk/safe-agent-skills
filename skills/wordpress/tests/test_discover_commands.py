import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from wordpress_api_tool.cli import main as cli_main
from wordpress_api_tool.http import HttpResponse


class DiscoverCommandsTests(unittest.TestCase):
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

    def test_discover_post_types_hits_types_endpoint_and_outputs_sorted_results(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            raw = {
                "post": {"name": "Posts", "rest_base": "posts", "rest_namespace": "wp/v2", "hierarchical": False},
                "page": {"name": "Pages", "rest_base": "pages", "rest_namespace": "wp/v2", "hierarchical": True},
            }

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/types"), url)
                self.assertEqual(kwargs.get("params"), {"context": "view"})
                body = json.dumps(raw).encode("utf-8")
                return HttpResponse(status=200, headers={}, body=body)

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    ["--output", "json", "--env-file", str(env_path), "discover", "post-types"]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertEqual(payload.get("count"), 2)
            self.assertEqual([r.get("slug") for r in payload.get("results")], ["page", "post"])

    def test_discover_statuses_hits_statuses_endpoint(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            raw = {
                "publish": {"name": "Published", "public": True, "protected": False, "private": False},
                "draft": {"name": "Draft", "public": False, "protected": False, "private": False},
            }

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/statuses"), url)
                self.assertEqual(kwargs.get("params"), {"context": "view"})
                body = json.dumps(raw).encode("utf-8")
                return HttpResponse(status=200, headers={}, body=body)

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    ["--output", "json", "--env-file", str(env_path), "discover", "statuses"]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertEqual(payload.get("count"), 2)

    def test_discover_taxonomies_hits_taxonomies_endpoint_and_can_include_raw(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            raw = {
                "category": {
                    "name": "Categories",
                    "rest_base": "categories",
                    "rest_namespace": "wp/v2",
                    "hierarchical": True,
                    "types": ["post"],
                }
            }

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/taxonomies"), url)
                self.assertEqual(kwargs.get("params"), {"context": "view"})
                body = json.dumps(raw).encode("utf-8")
                return HttpResponse(status=200, headers={}, body=body)

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "discover",
                        "taxonomies",
                        "--include-raw",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertIn("raw", payload)
            self.assertEqual(payload["raw"], raw)

    def test_discover_can_request_edit_context_explicitly(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            raw = {"post": {"name": "Posts", "rest_base": "posts", "rest_namespace": "wp/v2", "hierarchical": False}}

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/types"), url)
                self.assertEqual(kwargs.get("params"), {"context": "edit"})
                body = json.dumps(raw).encode("utf-8")
                return HttpResponse(status=200, headers={}, body=body)

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    ["--output", "json", "--env-file", str(env_path), "discover", "post-types", "--context", "edit"]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
