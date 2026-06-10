from __future__ import annotations

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

    def test_download_dry_run_makes_no_http_calls(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            with patch("requests.Session.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "photos", "download", "--id", "Dwu85P9SOIk"])
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
                self.assertFalse(payload["plan"]["before_state"]["supported"])
                self.assertTrue(payload["plan"]["recovery"]["rollback_ready"] is False)
                self.assertFalse(payload["plan"]["recovery"]["automatic_rollback"])
                self.assertEqual(payload["plan"]["recovery"]["strategy"], "no_inverse")
                self.assertEqual(payload["plan"]["recovery"]["end_state"], "irreversible_and_clearly_labeled")
                self.assertEqual(payload["plan"]["recovery"]["restore_note"], "Unsplash download tracking cannot be rolled back by this CLI. If the optional file download ran, delete the local destination file manually.")
                req.assert_not_called()

    def test_photos_download_apply_refuses_before_tracking_or_file_write(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            calls: list[dict[str, Any]] = []
            dest_path = os.path.join(td, "photo.jpg")

            def fake_request(self, method: str, url: str, **kwargs):  # noqa: ANN001
                calls.append({"method": method, "url": url, "kwargs": kwargs})
                if url.endswith("/photos/Dwu85P9SOIk/download"):
                    return _FakeResp(
                        status_code=200,
                        url=url,
                        headers={"content-type": "application/json"},
                        content=b'{"url":"https://images.example.invalid/file.jpg"}',
                        text='{"url":"https://images.example.invalid/file.jpg"}',
                    )
                return _FakeResp(
                    status_code=200,
                    url=url,
                    headers={"content-type": "image/jpeg"},
                    content=b"abc",
                    text="",
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
                            "--apply",
                            "photos",
                            "download",
                            "--id",
                            "Dwu85P9SOIk",
                            "--dest",
                            dest_path,
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertFalse(payload["dry_run"])
                self.assertTrue(payload["refused"])
                self.assertIn("before-state", payload["reasons"][0])
                self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
                self.assertEqual(payload["verification_plan"]["status"], "best_effort_after_apply")
            self.assertEqual(calls, [])
            self.assertFalse(Path(dest_path).exists())

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

    def test_download_apply_refuses_before_tracking_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            calls: list[dict[str, Any]] = []

            def fake_request(self, method: str, url: str, **kwargs):  # noqa: ANN001
                calls.append({"method": method, "url": url, "kwargs": kwargs})
                if url.endswith("/photos/Dwu85P9SOIk/download"):
                    return _FakeResp(
                        status_code=200,
                        url=url,
                        headers={"content-type": "application/json"},
                        content=b'{"url":"https://images.example.invalid/file.jpg"}',
                        text='{"url":"https://images.example.invalid/file.jpg"}',
                    )
                raise AssertionError(f"Unexpected URL: {url}")

            with patch("requests.Session.request", new=fake_request):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "--apply",
                            "photos",
                            "download",
                            "--id",
                            "Dwu85P9SOIk",
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertFalse(payload["dry_run"])
                self.assertTrue(payload["refused"])
                self.assertIn("ack-no-snapshot", payload["reasons"][0])
                self.assertEqual(payload["plan"]["before_state"]["provider_write"]["endpoint"], "/photos/Dwu85P9SOIk/download")

            self.assertEqual(calls, [])

    def test_download_apply_with_file_refuses_before_file_write(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            dest_path = os.path.join(td, "photo.jpg")

            def fake_request(self, method: str, url: str, **kwargs):  # noqa: ANN001
                if url.endswith("/photos/Dwu85P9SOIk/download"):
                    return _FakeResp(
                        status_code=200,
                        url=url,
                        headers={"content-type": "application/json"},
                        content=b'{"url":"https://images.example.invalid/file.jpg"}',
                        text='{"url":"https://images.example.invalid/file.jpg"}',
                    )
                if url == "https://images.example.invalid/file.jpg":
                    return _FakeResp(
                        status_code=200,
                        url=url,
                        headers={"content-type": "image/jpeg"},
                        content=b"abc",
                        text="",
                    )
                raise AssertionError(f"Unexpected URL: {url}")

            with patch("requests.Session.request", new=fake_request):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "--apply",
                            "photos",
                            "download",
                            "--id",
                            "Dwu85P9SOIk",
                            "--dest",
                            dest_path,
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertFalse(payload["dry_run"])
                self.assertTrue(payload["refused"])

            self.assertFalse(Path(dest_path).exists())

    def test_download_apply_plan_in_dest_mismatch_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            plan_path = os.path.join(td, "plan.json")
            dest_path = os.path.join(td, "photo.jpg")
            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "baseline": {
                            "env_fingerprint": "https://api.unsplash.com",
                            "photo_id": "Dwu85P9SOIk",
                            "dest": None,
                            "overwrite": False,
                        }
                    },
                    f,
                )

            with patch("requests.Session.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "--apply",
                            "--plan-in",
                            plan_path,
                            "photos",
                            "download",
                            "--id",
                            "Dwu85P9SOIk",
                            "--dest",
                            dest_path,
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["refused"])
                self.assertIn("plan baseline dest does not match", payload["reasons"][0])
                req.assert_not_called()

    def test_download_overwrite_requires_apply_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            dest_path = os.path.join(td, "photo.jpg")

            with patch("requests.Session.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "--apply",
                            "photos",
                            "download",
                            "--id",
                            "Dwu85P9SOIk",
                            "--dest",
                            dest_path,
                            "--overwrite",
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["refused"])
                self.assertIn("--overwrite requires --apply --yes", payload["reasons"][0])
                req.assert_not_called()

    def test_demo_write_plan_and_receipt_include_no_inverse_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = _write_env(td)
            plan_path = os.path.join(td, "plan.json")
            receipt_path = os.path.join(td, "receipt.json")

            with patch("requests.Session.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_path,
                            "--plan-out",
                            plan_path,
                            "demo",
                            "write",
                            "--selector",
                            "demo-resource",
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["recovery"]["strategy"], "no_inverse")
                self.assertEqual(payload["plan"]["recovery"]["end_state"], "irreversible_and_clearly_labeled")
                self.assertFalse(payload["plan"]["recovery"]["rollback_ready"])
                self.assertFalse(payload["plan"]["recovery"]["automatic_rollback"])
                self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
                self.assertTrue(Path(plan_path).exists())
                req.assert_not_called()

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_path,
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--receipt-out",
                        receipt_path,
                        "demo",
                        "write",
                        "--selector",
                        "demo-resource",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["refused"])
            self.assertIn("template-only", payload2["reasons"][0])
            self.assertEqual(payload2["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertFalse(Path(receipt_path).exists())

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
            (["collections", "photos", "--id", "123"], "/collections/123/photos"),
            (["collections", "related", "--id", "123"], "/collections/123/related"),
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

                    def fake_request(self, method: str, url: str, **kwargs):  # noqa: ANN001
                        _ = method
                        _ = kwargs
                        urls.append(url)
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
