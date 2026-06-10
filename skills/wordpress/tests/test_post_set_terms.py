import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from wordpress_api_tool.cli import main as cli_main
from wordpress_api_tool.http import HttpResponse


class PostSetTermsCommandsTests(unittest.TestCase):
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

    def test_dry_run_does_not_post(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                if method == "POST":
                    self.fail(f"Dry-run must not POST: {url}")

                if url.endswith("/wp-json/wp/v2/posts") and kwargs.get("params", {}).get("slug") == "hello":
                    body = json.dumps(
                        [{"id": 10, "slug": "hello", "link": "l", "categories": [2], "tags": []}]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/tags") and kwargs.get("params", {}).get("slug") == "t":
                    body = json.dumps(
                        [{"id": 5, "slug": "t", "name": "Tag T", "taxonomy": "post_tag"}]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/categories") and "include" in (kwargs.get("params") or {}):
                    body = json.dumps(
                        [
                            {"id": 1, "slug": "c1", "name": "Cat 1", "taxonomy": "category"},
                            {"id": 2, "slug": "c2", "name": "Cat 2", "taxonomy": "category"},
                        ]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/tags") and "include" in (kwargs.get("params") or {}):
                    body = json.dumps([{"id": 5, "slug": "t", "name": "Tag T", "taxonomy": "post_tag"}]).encode(
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
                        "set-terms",
                        "--slug",
                        "hello",
                        "--set",
                        "--category-id",
                        "1",
                        "--tag-slug",
                        "t",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertFalse(payload.get("apply"))
            self.assertTrue(payload.get("dry_run"))
            self.assertIn("plan", payload)
            plan = payload.get("plan") or {}
            rollback = plan.get("rollback") or {}
            self.assertTrue(rollback.get("supported"))
            self.assertIn("before_ids", rollback.get("notes") or "")
            self.assertTrue(payload.get("changed"))

    def test_apply_posts_payload_and_verifies_success(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                if url.endswith("/wp-json/wp/v2/posts") and kwargs.get("params", {}).get("slug") == "hello":
                    body = json.dumps(
                        [{"id": 10, "slug": "hello", "link": "l", "categories": [2], "tags": []}]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/tags") and kwargs.get("params", {}).get("slug") == "t":
                    body = json.dumps([{"id": 5, "slug": "t", "name": "Tag T", "taxonomy": "post_tag"}]).encode(
                        "utf-8"
                    )
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/categories") and "include" in (kwargs.get("params") or {}):
                    body = json.dumps(
                        [
                            {"id": 1, "slug": "c1", "name": "Cat 1", "taxonomy": "category"},
                            {"id": 2, "slug": "c2", "name": "Cat 2", "taxonomy": "category"},
                        ]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/tags") and "include" in (kwargs.get("params") or {}):
                    body = json.dumps([{"id": 5, "slug": "t", "name": "Tag T", "taxonomy": "post_tag"}]).encode(
                        "utf-8"
                    )
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/posts/10") and method == "POST":
                    self.assertEqual(kwargs.get("json_body"), {"categories": [1], "tags": [5]})
                    body = json.dumps({"id": 10}).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/posts/10") and method == "GET":
                    self.assertEqual(kwargs.get("params"), {"context": "edit"})
                    body = json.dumps({"id": 10, "categories": [1], "tags": [5]}).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                self.fail(f"Unexpected request: {method} {url} {kwargs}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--env-file",
                        str(env_path),
                        "post",
                        "set-terms",
                        "--slug",
                        "hello",
                        "--set",
                        "--category-id",
                        "1",
                        "--tag-slug",
                        "t",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("apply"))
            self.assertTrue(payload.get("changed"))
            self.assertTrue(payload.get("verified"))
            receipt = payload.get("receipt") or {}
            self.assertIn("rollback_plan", receipt)
            self.assertTrue((receipt.get("verification") or {}).get("ok"))
            self.assertIn("before_ids", receipt.get("rollback_plan") or "")

    def test_apply_verification_failure_sets_verified_false(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                if url.endswith("/wp-json/wp/v2/posts") and kwargs.get("params", {}).get("slug") == "hello":
                    body = json.dumps(
                        [{"id": 10, "slug": "hello", "link": "l", "categories": [2], "tags": []}]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/tags") and kwargs.get("params", {}).get("slug") == "t":
                    body = json.dumps([{"id": 5, "slug": "t", "name": "Tag T", "taxonomy": "post_tag"}]).encode(
                        "utf-8"
                    )
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/categories") and "include" in (kwargs.get("params") or {}):
                    body = json.dumps(
                        [
                            {"id": 1, "slug": "c1", "name": "Cat 1", "taxonomy": "category"},
                            {"id": 2, "slug": "c2", "name": "Cat 2", "taxonomy": "category"},
                        ]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/tags") and "include" in (kwargs.get("params") or {}):
                    body = json.dumps([{"id": 5, "slug": "t", "name": "Tag T", "taxonomy": "post_tag"}]).encode(
                        "utf-8"
                    )
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/posts/10") and method == "POST":
                    body = json.dumps({"id": 10}).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/posts/10") and method == "GET":
                    body = json.dumps({"id": 10, "categories": [999], "tags": [5]}).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                self.fail(f"Unexpected request: {method} {url} {kwargs}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--env-file",
                        str(env_path),
                        "post",
                        "set-terms",
                        "--slug",
                        "hello",
                        "--set",
                        "--category-id",
                        "1",
                        "--tag-slug",
                        "t",
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertEqual(stderr, "")
            self.assertTrue(payload.get("apply"))
            self.assertTrue(payload.get("changed"))
            self.assertFalse(payload.get("verified"))
            receipt = payload.get("receipt") or {}
            self.assertFalse((receipt.get("verification") or {}).get("ok"))

    def test_slug_ambiguity_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                if method == "POST":
                    self.fail(f"Refusal cases must not POST: {url}")

                if url.endswith("/wp-json/wp/v2/posts") and kwargs.get("params", {}).get("slug") == "hello":
                    body = json.dumps(
                        [{"id": 10, "slug": "hello", "link": "l", "categories": [], "tags": []}]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/tags") and kwargs.get("params", {}).get("slug") == "dup":
                    body = json.dumps([{"id": 5}, {"id": 6}]).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                self.fail(f"Unexpected request: {method} {url} {kwargs}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, _stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--env-file",
                        str(env_path),
                        "post",
                        "set-terms",
                        "--slug",
                        "hello",
                        "--set",
                        "--tag-slug",
                        "dup",
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertFalse(payload.get("ok"))
            self.assertIn("Multiple terms found", payload.get("error") or "")

    def test_target_slug_no_results_refuses_without_post_even_with_apply(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                if method == "POST":
                    self.fail(f"Refusal cases must not POST: {url}")

                if url.endswith("/wp-json/wp/v2/posts") and kwargs.get("params", {}).get("slug") == "missing":
                    body = json.dumps([]).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                self.fail(f"Unexpected request: {method} {url} {kwargs}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, _stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--env-file",
                        str(env_path),
                        "post",
                        "set-terms",
                        "--slug",
                        "missing",
                        "--set",
                        "--tag-id",
                        "1",
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertFalse(payload.get("ok"))
            self.assertIn("No posts found", payload.get("error") or "")

    def test_target_slug_multiple_results_refuses_without_post_even_with_apply(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                if method == "POST":
                    self.fail(f"Refusal cases must not POST: {url}")

                if url.endswith("/wp-json/wp/v2/posts") and kwargs.get("params", {}).get("slug") == "dup":
                    body = json.dumps(
                        [
                            {"id": 10, "slug": "dup", "link": "l1", "categories": [], "tags": []},
                            {"id": 11, "slug": "dup", "link": "l2", "categories": [], "tags": []},
                        ]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                self.fail(f"Unexpected request: {method} {url} {kwargs}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, _stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--env-file",
                        str(env_path),
                        "post",
                        "set-terms",
                        "--slug",
                        "dup",
                        "--set",
                        "--tag-id",
                        "1",
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertFalse(payload.get("ok"))
            self.assertIn("Multiple posts found", payload.get("error") or "")

    def test_term_slug_missing_refuses_without_post_even_with_apply(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._env_file(Path(td))

            def _request(method, url, **kwargs):
                if method == "POST":
                    self.fail(f"Refusal cases must not POST: {url}")

                if url.endswith("/wp-json/wp/v2/posts") and kwargs.get("params", {}).get("slug") == "hello":
                    body = json.dumps(
                        [{"id": 10, "slug": "hello", "link": "l", "categories": [], "tags": []}]
                    ).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                if url.endswith("/wp-json/wp/v2/tags") and kwargs.get("params", {}).get("slug") == "missing":
                    body = json.dumps([]).encode("utf-8")
                    return HttpResponse(status=200, headers={}, body=body)

                self.fail(f"Unexpected request: {method} {url} {kwargs}")

            with patch("wordpress_api_tool.http.HttpClient.request", side_effect=_request):
                rc, _stdout, _stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--env-file",
                        str(env_path),
                        "post",
                        "set-terms",
                        "--slug",
                        "hello",
                        "--set",
                        "--tag-slug",
                        "missing",
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertFalse(payload.get("ok"))
            self.assertIn("No term found", payload.get("error") or "")
