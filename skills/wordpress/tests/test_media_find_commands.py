import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from wordpress_api_tool.cli import main as cli_main
from wordpress_api_tool.http import HttpResponse


class MediaFindCommandsTests(unittest.TestCase):
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

    def test_media_find_hits_media_collection_with_search(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/media"), url)
                self.assertEqual(
                    kwargs.get("params"),
                    {"search": "img", "context": "view", "per_page": "2", "page": "1"},
                )
                body = json.dumps([{"id": 1, "source_url": "https://x/1.jpg"}, {"id": 2, "source_url": "https://x/2.jpg"}]).encode(
                    "utf-8"
                )
                return HttpResponse(status=200, headers={"x-wp-totalpages": "1", "x-wp-total": "2"}, body=body)

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "media",
                        "find",
                        "--query",
                        "img",
                        "--limit",
                        "2",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertEqual(payload.get("count"), 2)

