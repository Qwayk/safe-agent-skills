import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from wordpress_api_tool.cli import main as cli_main
from wordpress_api_tool.http import HttpResponse


class UsersCommandsTests(unittest.TestCase):
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

    def test_users_list_hits_users_endpoint_with_search(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/users"), url)
                self.assertEqual(kwargs.get("params"), {"search": "ann", "context": "view", "per_page": "2", "page": "1"})
                body = json.dumps([{"id": 1, "name": "Ann"}, {"id": 2, "name": "Anne"}]).encode("utf-8")
                return HttpResponse(status=200, headers={"x-wp-totalpages": "1", "x-wp-total": "2"}, body=body)

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "users",
                        "list",
                        "--query",
                        "ann",
                        "--limit",
                        "2",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertEqual(payload.get("count"), 2)

    def test_users_get_hits_users_endpoint_by_id(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            raw = {"id": 5, "name": "U", "slug": "u"}

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/users/5"), url)
                self.assertEqual(kwargs.get("params"), {"context": "view"})
                body = json.dumps(raw).encode("utf-8")
                return HttpResponse(status=200, headers={}, body=body)

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    ["--output", "json", "--env-file", str(env_path), "users", "get", "--id", "5"]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertEqual(payload.get("id"), 5)
            self.assertIn("raw", payload)

