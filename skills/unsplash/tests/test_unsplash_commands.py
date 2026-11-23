from __future__ import annotations

import hashlib
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import patch

import requests

from unsplash_api_tool.cli import main


@dataclass
class _FakeResp:
    status_code: int
    url: str
    headers: dict[str, str]
    content: bytes
    text: str = ""

    def iter_content(self, chunk_size: int = 1024) -> list[bytes]:
        _ = chunk_size
        return [self.content]


def _write_env(dir_path: str, *, access_key: str = "TESTKEY") -> str:
    env_path = os.path.join(dir_path, ".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("UNSPLASH_API_BASE_URL=https://api.unsplash.com\n")
        f.write(f"UNSPLASH_ACCESS_KEY={access_key}\n")
        f.write("UNSPLASH_TIMEOUT_S=1\n")
    return env_path


class TestUnsplashCommands(unittest.TestCase):
    def test_json_mode_parse_errors_emit_single_object(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            with patch("requests.Session.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "photos", "get"])
                self.assertEqual(rc, 1)
                raw = buf.getvalue().strip()
                payload = json.loads(raw)
                self.assertFalse(payload["ok"])
                self.assertEqual(payload["error_type"], "ValidationError")
                req.assert_not_called()

    def test_json_mode_missing_command_emits_single_object(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            with patch("requests.Session.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path])
                self.assertEqual(rc, 1)
                raw = buf.getvalue().strip()
                payload = json.loads(raw)
                self.assertFalse(payload["ok"])
                self.assertEqual(payload["error_type"], "ValidationError")
                req.assert_not_called()

    def test_per_page_cap_invalid_refuses_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            with patch("requests.Session.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "photos", "list", "--per-page", "31"])
                self.assertEqual(rc, 1)
                payload = json.loads(buf.getvalue())
                self.assertFalse(payload["ok"])
                self.assertEqual(payload["error_type"], "ValidationError")
                req.assert_not_called()

    def test_export_photos_list_refuses_without_yes_for_multi_page(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            out_path = os.path.join(td, "export.json")
            with patch("requests.Session.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "export",
                            "photos-list",
                            "--out",
                            out_path,
                            "--max-pages",
                            "2",
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["refused"])
                self.assertIn("--yes", payload["reasons"][0])
                self.assertFalse(Path(out_path).exists())
                req.assert_not_called()

    def test_export_photos_list_writes_file_and_paginates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            out_path = os.path.join(td, "export.json")
            calls: list[dict[str, Any]] = []
            test_self = self

            def fake_request(self, method: str, url: str, **kwargs):  # noqa: ANN001
                calls.append({"method": method, "url": url, "kwargs": kwargs})
                params = kwargs.get("params") or {}
                page = int(params.get("page"))
                per_page = int(params.get("per_page"))
                test_self.assertEqual(per_page, 10)
                payload = [{"id": f"p{page}-1"}, {"id": f"p{page}-2"}]
                blob = json.dumps(payload).encode("utf-8")
                return _FakeResp(
                    status_code=200,
                    url=url,
                    headers={"content-type": "application/json"},
                    content=blob,
                    text=blob.decode("utf-8"),
                )

            with patch("requests.Session.request", new=fake_request):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "--yes",
                            "export",
                            "photos-list",
                            "--out",
                            out_path,
                            "--start-page",
                            "2",
                            "--max-pages",
                            "2",
                            "--per-page",
                            "10",
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["wrote"])
                self.assertEqual(payload["pages_fetched"], 2)
                self.assertEqual(payload["items_written"], 4)

            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0]["kwargs"]["params"]["page"], 2)
            self.assertEqual(calls[1]["kwargs"]["params"]["page"], 3)

            export_obj = json.loads(Path(out_path).read_text(encoding="utf-8"))
            self.assertEqual(export_obj["endpoint"], "GET /photos")
            self.assertEqual(len(export_obj["pages"]), 2)
            self.assertEqual(len(export_obj["items"]), 4)
    def test_photos_list_builds_headers_and_url(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            calls: list[dict[str, Any]] = []

            def fake_request(self, method: str, url: str, **kwargs):  # noqa: ANN001
                calls.append({"method": method, "url": url, "kwargs": kwargs})
                return _FakeResp(
                    status_code=200,
                    url=url,
                    headers={"content-type": "application/json"},
                    content=b"[]",
                    text="[]",
                )

            with patch("requests.Session.request", new=fake_request):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "photos", "list", "--per-page", "1"])
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["endpoint"], "GET /photos")

            self.assertEqual(len(calls), 1)
            call = calls[0]
            self.assertEqual(call["method"], "GET")
            self.assertTrue(call["url"].startswith("https://api.unsplash.com/photos"))
            headers = call["kwargs"]["headers"]
            self.assertEqual(headers["Accept-Version"], "v1")
            self.assertTrue(headers["Authorization"].startswith("Client-ID "))

    def test_auth_key_set_writes_state_immediately(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            auth_file = os.path.join(td, "auth.json")
            with open(auth_file, "w", encoding="utf-8") as f:
                f.write('{"access_key":"LIVEKEY","note":"from_import"}')

            with patch("requests.Session.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "auth",
                            "key",
                            "set",
                            "--file",
                            auth_file,
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                st = Path(payload["stored_to"])
                self.assertTrue(st.exists())
                stored = json.loads(st.read_text(encoding="utf-8"))
                self.assertEqual(stored["access_key"], "LIVEKEY")
                self.assertIn("note", stored)
                req.assert_not_called()

    def test_collection_export_accepts_an_id_with_letters(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            env = _write_env(folder)
            target = Path(folder) / "photos.json"
            url = "https://api.unsplash.com/collections/nvYdtNLrrRQ/photos"
            response = _FakeResp(status_code=200, url=url, headers={}, content=b"[]")
            out = io.StringIO()
            with redirect_stdout(out), patch("requests.Session.request", return_value=response) as request:
                rc = main(["--env-file", env, "export", "collections-photos", "--id", "nvYdtNLrrRQ", "--out", str(target)])
            self.assertEqual(rc, 0, out.getvalue())
            self.assertEqual(request.call_args.kwargs["url"], url)
            self.assertTrue(target.is_file())

    def test_search_users_hits_expected_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            calls: list[str] = []

            def fake_request(self, method: str, url: str, **kwargs):  # noqa: ANN001
                calls.append(url)
                return _FakeResp(
                    status_code=200,
                    url=url,
                    headers={"content-type": "application/json"},
                    content=b'{"total":0,"results":[]}',
                    text='{"total":0,"results":[]}',
                )

            with patch("requests.Session.request", new=fake_request):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "search", "users", "--query", "example_user"])
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["endpoint"], "GET /search/users")

            self.assertEqual(len(calls), 1)
            self.assertTrue(calls[0].startswith("https://api.unsplash.com/search/users"))

    def test_various_read_commands_hit_expected_paths(self) -> None:
        cases = [
            (["photos", "random"], "/photos/random"),
            (["photos", "search", "--query", "coffee"], "/search/photos"),
            (["photos", "stats", "--id", "Dwu85P9SOIk"], "/photos/Dwu85P9SOIk/statistics"),
            (["collections", "list"], "/collections"),
            (["collections", "get", "--id", "123"], "/collections/123"),
            (["collections", "get", "--id", "nvYdtNLrrRQ"], "/collections/nvYdtNLrrRQ"),
            (["collections", "photos", "--id", "nvYdtNLrrRQ"], "/collections/nvYdtNLrrRQ/photos"),
            (["collections", "related", "--id", "nvYdtNLrrRQ"], "/collections/nvYdtNLrrRQ/related"),
            (["topics", "list"], "/topics"),
            (["topics", "get", "--id", "nature"], "/topics/nature"),
            (["topics", "photos", "--id", "nature"], "/topics/nature/photos"),
            (["users", "get", "--username", "example_user"], "/users/example_user"),
            (["users", "photos", "--username", "example_user"], "/users/example_user/photos"),
            (["users", "likes", "--username", "example_user"], "/users/example_user/likes"),
            (["users", "collections", "--username", "example_user"], "/users/example_user/collections"),
            (["users", "statistics", "--username", "example_user"], "/users/example_user/statistics"),
            (["search", "photos", "--query", "tea"], "/search/photos"),
            (["search", "collections", "--query", "tea"], "/search/collections"),
            (["stats", "total"], "/stats/total"),
            (["stats", "month"], "/stats/month"),
        ]
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            for argv, expected_path in cases:
                with self.subTest(argv=argv):
                    urls: list[str] = []

                    def fake_request(self, method: str, url: str, *, calls=urls, **kwargs):  # noqa: ANN001
                        _ = method
                        _ = kwargs
                        calls.append(url)
                        return _FakeResp(
                            status_code=200,
                            url=url,
                            headers={"content-type": "application/json"},
                            content=b"{}",
                            text="{}",
                        )

                    with patch("requests.Session.request", new=fake_request):
                        buf = io.StringIO()
                        with redirect_stdout(buf):
                            rc = main(["--output", "json", "--env-file", env_path, *argv])
                        self.assertEqual(rc, 0)
                        self.assertEqual(len(urls), 1)
                        self.assertIn(expected_path, urls[0])


class TestReviewedDownload(unittest.TestCase):
    photo_id = "Dwu85P9SOIk"
    photo_detail = f"https://api.unsplash.com/photos/{photo_id}"
    tracking_url = f"{photo_detail}/download?ixid=original%2Fcontext&ref=search"
    image_url = "https://images.unsplash.com/example?ixid=original%2Fcontext"
    photo_bytes = b"\xff\xd8\xffexample"

    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.env = _write_env(folder.name)
        self.plan = self.root / "plan.json"
        self.receipt = self.root / "receipt.json"
        self.photo_path = self.root / "images" / "photo.jpg"
        self.tracking_reply: int | str = 200
        self.image_interrupted = False
        self.include_image_link = True
        self.calls = []
        patcher = patch.object(requests.Session, "request", side_effect=self.provider)
        patcher.start()
        self.addCleanup(patcher.stop)

    def provider(self, *, method, url, **kwargs):
        self.calls.append((url, kwargs))
        self.assertEqual(method, "GET")
        reply = requests.Response()
        reply.url = url
        reply.status_code = 200
        reply._content_consumed = True
        if url == self.photo_detail:
            reply._content = json.dumps({
                "id": self.photo_id, "urls": {"full": self.image_url} if self.include_image_link else {},
                "links": {"download_location": self.tracking_url, "html": "https://unsplash.com/photos/example"},
                "user": {"name": "Example", "links": {"html": "https://unsplash.com/@example"}},
            }).encode()
        elif url == self.tracking_url:
            self.assertFalse(kwargs["allow_redirects"])
            self.assertEqual(kwargs["headers"]["Authorization"], "Client-ID TESTKEY")
            if self.tracking_reply == "timeout":
                raise requests.Timeout("No reply")
            reply.status_code = int(self.tracking_reply)
            reply._content = b'{"url":"https://images.unsplash.com/another-url"}'
        elif url == self.image_url:
            self.assertIsNone(kwargs.get("headers"))
            reply._content = self.photo_bytes
            if self.image_interrupted:
                def interrupted(**kwargs):
                    yield b"partial"
                    raise requests.ConnectionError("Transfer stopped")
                reply.iter_content = interrupted
        else:
            self.fail(f"Unexpected URL {url}")
        return reply

    def cli(self, flags, args):
        self.calls.clear()
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            rc = main(["--no-artifacts", "--env-file", self.env, *flags, *args])
        return rc, json.loads(stdout.getvalue())

    def command(self, *args):
        return ["photos", "download", "--id", self.photo_id, *args]

    def preview(self, args):
        rc, result = self.cli(["--plan-out", str(self.plan)], args)
        self.assertEqual(rc, 0, result)
        self.assertEqual(result["tracking_status"], "not_sent")
        self.assertEqual([url for url, _ in self.calls], [self.photo_detail])
        self.assertEqual(result["plan"]["before_state"]["status"], "no_snapshot_available")
        self.assertEqual(result["plan"]["recovery"]["strategy"], "no_inverse")
        self.assertNotIn("TESTKEY", self.plan.read_text())
        return result

    def apply(self, args, *extra):
        return self.cli(
            ["--apply", "--ack-no-snapshot", "--plan-in", str(self.plan), "--receipt-out", str(self.receipt), *extra],
            args,
        )

    def test_saved_plan_uses_exact_tracking_url_and_preserves_credit(self):
        command = self.command("--dest", str(self.photo_path))
        self.preview(command)
        rc, result = self.apply(command)
        self.assertEqual(rc, 0, result)
        self.assertEqual([url for url, _ in self.calls], [self.tracking_url, self.image_url])
        self.assertEqual(result["tracking_status"], "recorded")
        saved = json.loads(self.receipt.read_text())
        self.assertEqual(saved["photo"]["urls"]["full"], self.image_url)
        self.assertEqual(saved["photo"]["photographer"]["profile_url"], "https://unsplash.com/@example")
        self.assertTrue(saved["no_snapshot_approval"]["acknowledged"])
        self.assertEqual(saved["file"]["sha256"], hashlib.sha256(self.photo_bytes).hexdigest())
        self.assertEqual(self.photo_path.read_bytes(), self.photo_bytes)

    def test_tracking_without_a_destination_needs_no_file_transfer(self):
        self.include_image_link = False
        command = self.command()
        self.preview(command)
        rc, result = self.apply(command)
        self.assertEqual(rc, 0, result)
        self.assertEqual([url for url, _ in self.calls], [self.tracking_url])
        self.assertIsNone(result["receipt"]["file"])

    def test_missing_plan_or_no_snapshot_approval_refuses_before_tracking(self):
        command = self.command()
        rc, result = self.cli(["--apply", "--ack-no-snapshot"], command)
        self.assertEqual(rc, 1)
        self.assertTrue(result["refused"])
        self.assertFalse(self.calls)
        self.preview(command)
        rc, result = self.cli(["--apply", "--plan-in", str(self.plan)], command)
        self.assertEqual(rc, 1)
        self.assertEqual(result["plan"]["before_state"]["status"], "no_snapshot_available")
        self.assertFalse(result["ok"])
        self.assertTrue(result["refused"])
        self.assertFalse(self.calls)
        self.assertFalse(self.receipt.exists())

    def test_changed_target_connection_or_old_plan_refuses_before_tracking(self):
        command = self.command()
        self.preview(command)
        rc, result = self.apply(self.command("--dest", str(self.photo_path)))
        self.assertEqual(rc, 1)
        self.assertTrue(result["refused"])
        self.assertFalse(self.calls)
        rc, result = self.apply(["photos", "download", "--id", "another"])
        self.assertEqual(rc, 1)
        self.assertTrue(result["refused"])
        self.assertFalse(self.calls)
        Path(self.env).write_text("UNSPLASH_ACCESS_KEY=OTHERKEY\n")
        rc, result = self.apply(command)
        self.assertEqual(rc, 1)
        self.assertTrue(result["refused"])
        self.assertFalse(self.calls)
        self.plan.write_text('{"baseline":{"photo_id":"Dwu85P9SOIk"}}')
        self.assertEqual(self.apply(command)[0], 1)
        self.assertFalse(self.calls)

    def test_existing_target_stops_before_tracking(self):
        command = self.command("--dest", str(self.photo_path))
        self.preview(command)
        self.photo_path.parent.mkdir()
        self.photo_path.write_bytes(b"original")
        rc, result = self.apply(command)
        self.assertEqual(rc, 1)
        self.assertTrue(result["refused"])
        self.assertFalse(self.calls)
        self.assertEqual(self.photo_path.read_bytes(), b"original")

    def test_overwrite_can_be_previewed_and_interruption_keeps_the_old_photo(self):
        self.photo_path.parent.mkdir()
        self.photo_path.write_bytes(b"original")
        command = self.command("--dest", str(self.photo_path), "--overwrite")
        self.preview(command)
        self.assertEqual(self.apply(command)[0], 1)
        self.assertFalse(self.calls)

        self.image_interrupted = True
        rc, result = self.apply(command, "--yes")
        self.assertEqual(rc, 1, result)
        self.assertEqual(result["tracking_status"], "recorded")
        self.assertIsNone(result["receipt"]["file"])
        self.assertEqual(self.photo_path.read_bytes(), b"original")
        self.assertEqual(list(self.photo_path.parent.iterdir()), [self.photo_path])
        self.assertEqual([url for url, _ in self.calls], [self.tracking_url, self.image_url])

    def test_approved_overwrite_replaces_file_after_transfer(self):
        self.photo_path.parent.mkdir()
        self.photo_path.write_bytes(b"original")
        command = self.command("--dest", str(self.photo_path), "--overwrite")
        self.preview(command)
        rc, result = self.apply(command, "--yes")
        self.assertEqual(rc, 0, result)
        self.assertEqual(self.photo_path.read_bytes(), self.photo_bytes)

    def test_lost_tracking_reply_never_repeats_and_preserves_the_receipt(self):
        command = self.command("--dest", str(self.photo_path))
        self.preview(command)
        for failure, expected in (("timeout", "unknown"), (503, "unknown"), (403, "failed")):
            with self.subTest(failure=failure):
                self.tracking_reply = failure
                rc, result = self.apply(command)
                self.assertEqual(rc, 1)
                self.assertEqual(result["tracking_status"], expected)
                self.assertEqual([url for url, _ in self.calls], [self.tracking_url])
                self.assertFalse(self.photo_path.exists())
                self.assertEqual(json.loads(self.receipt.read_text())["tracking_status"], expected)
