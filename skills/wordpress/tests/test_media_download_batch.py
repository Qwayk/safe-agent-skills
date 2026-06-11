import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from wordpress_api_tool.cli import main as cli_main
from wordpress_api_tool.http import HttpResponse


class MediaDownloadBatchCommandsTests(unittest.TestCase):
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

    def test_dry_run_does_not_write_or_download(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            out_dir = td_path / "out"
            input_path = td_path / "items.json"
            input_path.write_text(
                json.dumps([{"url": "https://example.test/a.jpg", "filename": "a.jpg"}]),
                encoding="utf-8",
            )

            with patch("wordpress_api_tool.http.HttpClient.download_to_file") as dl:
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "media",
                        "download-batch",
                        "--file",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertTrue(payload.get("dry_run"))
            self.assertFalse(out_dir.exists())
            dl.assert_not_called()

    def test_apply_requires_yes(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            input_path = td_path / "items.json"
            input_path.write_text(json.dumps([{"url": "https://example.test/a.jpg"}]), encoding="utf-8")
            out_dir = td_path / "out"

            rc, _stdout, stderr, payload = self._run(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "media",
                    "download-batch",
                    "--file",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                ]
            )

            self.assertEqual(rc, 1)
            self.assertEqual(stderr, "")
            self.assertFalse(payload.get("ok"))
            self.assertIn("both --apply and --yes", payload.get("error") or "")

    def test_apply_writes_file_and_verifies_size(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            out_dir = td_path / "out"
            input_path = td_path / "items.json"
            input_path.write_text(
                json.dumps([{"url": "https://example.test/a.jpg", "filename": "a.jpg"}]),
                encoding="utf-8",
            )

            def _fake_download(_self, url, *, out_path, headers=None, chunk_size=0):  # noqa: ANN001
                self.assertEqual(url, "https://example.test/a.jpg")
                Path(out_path).write_bytes(b"abc")
                return {"bytes": 3, "sha256": "fake", "content_type": "image/jpeg"}

            with patch("wordpress_api_tool.http.HttpClient.download_to_file", new=_fake_download):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "media",
                        "download-batch",
                        "--file",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertIs(payload.get("receipt", {}).get("changed"), True)
            self.assertTrue(out_dir.exists())
            self.assertTrue((out_dir / "a.jpg").exists())
            self.assertEqual(os.path.getsize(out_dir / "a.jpg"), 3)

    def test_partial_success_then_error_has_changed_true(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            out_dir = td_path / "out"
            input_path = td_path / "items.json"
            input_path.write_text(
                json.dumps(
                    [
                        {"url": "https://example.test/a.jpg", "filename": "a.jpg"},
                        {"url": "https://example.test/b.jpg", "filename": "b.jpg"},
                    ]
                ),
                encoding="utf-8",
            )

            call_count = 0

            def _fake_download(_self, url, *, out_path, headers=None, chunk_size=0):  # noqa: ANN001
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    self.assertEqual(url, "https://example.test/a.jpg")
                    Path(out_path).write_bytes(b"abc")
                    return {"bytes": 3, "sha256": "fake", "content_type": "image/jpeg"}
                self.assertEqual(url, "https://example.test/b.jpg")
                raise RuntimeError("boom")

            with patch("wordpress_api_tool.http.HttpClient.download_to_file", new=_fake_download):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "media",
                        "download-batch",
                        "--file",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertEqual(stderr, "")
            self.assertFalse(payload.get("ok"))
            self.assertIs(payload.get("receipt", {}).get("changed"), True)
            self.assertTrue((out_dir / "a.jpg").exists())
            self.assertFalse((out_dir / "b.jpg").exists())

    def test_refuses_path_traversal_filename(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            out_dir = td_path / "out"
            input_path = td_path / "items.json"
            input_path.write_text(
                json.dumps([{"url": "https://example.test/a.jpg", "filename": "../evil.jpg"}]),
                encoding="utf-8",
            )

            with patch("wordpress_api_tool.http.HttpClient.download_to_file") as dl:
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "media",
                        "download-batch",
                        "--file",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertEqual(stderr, "")
            self.assertFalse(payload.get("ok"))
            dl.assert_not_called()
            self.assertFalse(out_dir.exists())

    def test_skip_existing(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            out_dir = td_path / "out"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "a.jpg").write_bytes(b"already")
            input_path = td_path / "items.json"
            input_path.write_text(
                json.dumps([{"url": "https://example.test/a.jpg", "filename": "a.jpg"}]),
                encoding="utf-8",
            )

            with patch("wordpress_api_tool.http.HttpClient.download_to_file") as dl:
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "media",
                        "download-batch",
                        "--file",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                        "--skip-existing",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertIs(payload.get("receipt", {}).get("changed"), False)
            self.assertEqual(payload.get("results")[0].get("action"), "skip")
            dl.assert_not_called()

    def test_id_resolves_url_and_downloads(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            out_dir = td_path / "out"
            input_path = td_path / "items.json"
            input_path.write_text(json.dumps([{"id": 12, "filename": "a.jpg"}]), encoding="utf-8")

            def _request(method, url, **kwargs):  # noqa: ANN001
                self.assertEqual(method, "GET")
                self.assertTrue(url.endswith("/wp-json/wp/v2/media/12"), url)
                self.assertEqual(kwargs.get("params"), {"context": "edit"})
                body = json.dumps({"id": 12, "source_url": "https://example.test/a.jpg"}).encode("utf-8")
                return HttpResponse(status=200, headers={}, body=body)

            def _fake_download(_self, url, *, out_path, headers=None, chunk_size=0):  # noqa: ANN001
                self.assertEqual(url, "https://example.test/a.jpg")
                Path(out_path).write_bytes(b"abc")
                return {"bytes": 3, "sha256": "fake", "content_type": "image/jpeg"}

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request), patch(
                "wordpress_api_tool.http.HttpClient.download_to_file",
                new=_fake_download,
            ):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "media",
                        "download-batch",
                        "--file",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("ok"))
            self.assertTrue((out_dir / "a.jpg").exists())
