import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from wordpress_api_tool.cli import main as cli_main
from wordpress_api_tool.http import HttpResponse


class _StubApi:
    def __init__(self):
        self._media = {
            123: {
                "id": 123,
                "caption": {"raw": "Old caption", "rendered": "Old caption"},
                "alt_text": "",
                "title": {"raw": "", "rendered": ""},
                "source_url": "https://example.com/wp-content/uploads/2026/01/example.jpg",
            }
        }

    def media_by_id(self, media_id: int):
        return dict(self._media[int(media_id)])

    def update_media(self, *, media_id: int, caption, alt_text, title):
        m = self._media[int(media_id)]
        if caption is not None:
            m["caption"] = {"raw": caption, "rendered": caption}
        if alt_text is not None:
            m["alt_text"] = alt_text
        if title is not None:
            m["title"] = {"raw": title, "rendered": title}
        return dict(m)


class V2PlanReceiptExportTests(unittest.TestCase):
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

    def test_media_set_writes_plan_out_in_dry_run(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            plan_out = td_path / "plan.json"

            stub_api = _StubApi()
            with patch("wordpress_api_tool.commands.media.WordPressApi.from_config", return_value=stub_api):
                rc, stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_out),
                        "media",
                        "set",
                        "--id",
                        "123",
                        "--caption",
                        "New caption",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(plan_out.exists())
            self.assertIn("plan", payload)

            plan = json.loads(plan_out.read_text(encoding="utf-8"))
            self.assertEqual(plan.get("tool"), "wordpress-api-tool")
            self.assertEqual(plan.get("env_fingerprint", {}).get("base_url"), "https://example.com")
            self.assertIn("before_state", plan)
            self.assertTrue(Path(plan["before_state"]["path"]).exists())

            serialized = plan_out.read_text(encoding="utf-8")
            self.assertNotIn("fake_user", serialized)
            self.assertNotIn("fake_password", serialized)
            self.assertNotIn("fake_password", stdout)

    def test_media_set_writes_receipt_out_on_apply(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            receipt_out = td_path / "receipt.json"

            stub_api = _StubApi()
            with patch("wordpress_api_tool.commands.media.WordPressApi.from_config", return_value=stub_api):
                rc, stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--receipt-out",
                        str(receipt_out),
                        "media",
                        "set",
                        "--id",
                        "123",
                        "--caption",
                        "New caption",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(receipt_out.exists())
            self.assertIn("receipt", payload)

            receipt = json.loads(receipt_out.read_text(encoding="utf-8"))
            self.assertEqual(receipt.get("tool"), "wordpress-api-tool")
            self.assertIn("changed", receipt)
            self.assertIn("before_state", receipt)
            self.assertIn("rollback_plan", receipt)
            self.assertIn("re-run media set", (receipt.get("rollback_plan") or ""))

    def test_post_set_status_rollback_plan(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)

            def _request(method, url, **kwargs):
                if method == "POST":
                    self.fail(f"Dry-run should not POST: {url}")

                if url.endswith("/wp-json/wp/v2/posts") and kwargs.get("params", {}).get("slug") == "hello":
                    body = json.dumps([{"id": 10, "slug": "hello", "status": "draft", "link": "https://example.com/post/hello"}]).encode(
                        "utf-8"
                    )
                    return HttpResponse(status=200, headers={}, body=body)

                self.fail(f"Unexpected request: {method} {url} {kwargs}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "post",
                        "set-status",
                        "--slug",
                        "hello",
                        "--to",
                        "publish",
                        "--require-current",
                        "draft",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertIn("plan", payload)
            plan = payload.get("plan") or {}
            rollback = plan.get("rollback") or {}
            self.assertTrue(rollback.get("supported"))
            self.assertIn("previous status", (rollback.get("notes") or ""))

    def test_post_set_status_writes_receipt_with_rollback_plan(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)

            def _request(method, url, **kwargs):
                if url.endswith("/wp-json/wp/v2/posts") and kwargs.get("params", {}).get("slug") == "hello":
                    body = json.dumps([{"id": 10, "slug": "hello", "status": "draft", "link": "l"}]).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/posts/10") and method == "POST":
                    body = json.dumps({"id": 10, "status": "publish"}).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/posts/10") and method == "GET":
                    body = json.dumps({"id": 10, "status": "publish", "slug": "hello", "link": "l"}).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                self.fail(f"Unexpected request: {method} {url} {kwargs}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "post",
                        "set-status",
                        "--slug",
                        "hello",
                        "--to",
                        "publish",
                        "--require-current",
                        "draft",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertIn("receipt", payload)
            receipt = payload.get("receipt") or {}
            self.assertIn("rollback_plan", receipt)
            self.assertIn("To revert", (receipt.get("rollback_plan") or ""))

    def test_post_set_status_pages_dry_run_includes_page_before_state(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)

            def _request(method, url, **kwargs):
                if method == "POST":
                    self.fail(f"Dry-run should not POST: {url}")

                if url.endswith("/wp-json/wp/v2/pages") and kwargs.get("params", {}).get("slug") == "about":
                    body = json.dumps(
                        [{"id": 20, "slug": "about", "status": "draft", "link": "https://example.com/page/about"}]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                self.fail(f"Unexpected request: {method} {url} {kwargs}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "post",
                        "set-status",
                        "--post-type",
                        "pages",
                        "--slug",
                        "about",
                        "--to",
                        "publish",
                        "--require-current",
                        "draft",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertIn("plan", payload)
            plan = payload.get("plan") or {}
            self.assertTrue(plan.get("rollback", {}).get("supported"))
            before_state = plan.get("before_state") or {}
            path = before_state.get("path")
            self.assertIsInstance(path, str)
            self.assertTrue(path.endswith("/page.set-status__slug-about.json"))
            self.assertTrue(Path(path).exists())

    def test_post_set_status_pages_receipt_uses_page_before_state(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)

            def _request(method, url, **kwargs):
                if url.endswith("/wp-json/wp/v2/pages") and kwargs.get("params", {}).get("slug") == "about":
                    body = json.dumps([{"id": 20, "slug": "about", "status": "draft", "link": "https://example.com/page/about"}]).encode(
                        "utf-8"
                    )
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/pages/20") and method == "POST":
                    body = json.dumps({"id": 20, "status": "publish"}).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/pages/20") and method == "GET":
                    body = json.dumps({"id": 20, "slug": "about", "status": "publish", "link": "https://example.com/page/about"}).encode(
                        "utf-8"
                    )
                    return HttpResponse(status=200, headers={}, body=body)

                self.fail(f"Unexpected request: {method} {url} {kwargs}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "post",
                        "set-status",
                        "--post-type",
                        "pages",
                        "--slug",
                        "about",
                        "--to",
                        "publish",
                        "--require-current",
                        "draft",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertIn("receipt", payload)
            receipt = payload.get("receipt") or {}
            before_state = receipt.get("before_state") or {}
            path = before_state.get("path")
            self.assertIsInstance(path, str)
            self.assertTrue(path.endswith("/page.set-status__slug-about.json"))
            self.assertTrue(Path(path).exists())
            self.assertIn("To revert", (receipt.get("rollback_plan") or ""))
