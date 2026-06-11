from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cloudflare_api_tool.cli import main


class _DummyResponse:
    def __init__(self, *, status: int, url: str, body: bytes, headers: dict[str, str] | None = None):
        self.status_code = int(status)
        self.url = str(url)
        self.headers = dict(headers or {})
        self.content = body

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


def _write_env(root: Path, *, token: str = "T") -> Path:
    p = root / ".env"
    p.write_text(
        "\n".join(
            [
                "CLOUDFLARE_API_BASE_URL=http://example.invalid/client/v4",
                f"CLOUDFLARE_API_TOKEN={token}",
                "CLOUDFLARE_TIMEOUT_S=30",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return p


class TestLoadBalancersCommands(unittest.TestCase):
    def test_load_balancers_monitors_list_is_dry_run_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "load-balancers", "monitors", "list", "--account-id", "acct1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

    def test_load_balancers_monitors_list_apply_missing_out_refuses_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "load-balancers",
                        "monitors",
                        "list",
                        "--account-id",
                        "acct1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_load_balancers_monitors_create_apply_missing_yes_refuses_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"

            body_path = root / "body.json"
            body_path.write_text('{"description":"example"}\n', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "load-balancers",
                        "monitors",
                        "create",
                        "--account-id",
                        "acct1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        "out.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_load_balancers_monitors_preview_apply_requires_out_but_not_yes_and_changed_false(self) -> None:
        secret_bytes = b'{"preview":"SECRET_PREVIEW_SHOULD_NOT_PRINT"}\n'

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"

            # Missing --out refuses safely (no API calls).
            def fake_request_never(self, method, url, **kwargs):  # noqa: ANN001
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request_never):
                buf1 = io.StringIO()
                with redirect_stdout(buf1):
                    rc1 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "load-balancers",
                            "monitors",
                            "preview",
                            "--account-id",
                            "acct1",
                            "--monitor-id",
                            "m1",
                        ]
                    )
                self.assertEqual(rc1, 0)
                payload1 = json.loads(buf1.getvalue())
                self.assertTrue(payload1["ok"])
                self.assertTrue(payload1["refused"])

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                if method == "POST" and str(url).endswith("/accounts/acct1/load_balancers/monitors/m1/preview"):
                    return _DummyResponse(status=200, url=url, body=secret_bytes)
                raise AssertionError(f"unexpected call: {method} {url}")

            # With --out succeeds without --yes and reports changed=false.
            with patch("requests.Session.request", new=fake_request):
                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "load-balancers",
                            "monitors",
                            "preview",
                            "--account-id",
                            "acct1",
                            "--monitor-id",
                            "m1",
                            "--out",
                            "preview.json",
                        ]
                    )
                self.assertEqual(rc2, 0)
                out_text = buf2.getvalue()
                self.assertNotIn("SECRET_PREVIEW_SHOULD_NOT_PRINT", out_text)
                payload2 = json.loads(out_text)
                self.assertTrue(payload2["ok"])
                self.assertFalse(payload2.get("changed"), "load-balancers monitors preview should be read-like (changed=false)")
                out_path = project_dir / "preview.json"
                self.assertTrue(out_path.exists())
                self.assertEqual(out_path.read_bytes(), secret_bytes)

    def test_load_balancers_regions_list_apply_requires_out_and_calls_get(self) -> None:
        secret_bytes = b'{"regions":["SECRET_REGION_SHOULD_NOT_PRINT"]}\n'

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"

            def fake_request_never(self, method, url, **kwargs):  # noqa: ANN001
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request_never):
                buf1 = io.StringIO()
                with redirect_stdout(buf1):
                    rc1 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "load-balancers",
                            "regions",
                            "list",
                            "--account-id",
                            "acct1",
                        ]
                    )
                self.assertEqual(rc1, 0)
                payload1 = json.loads(buf1.getvalue())
                self.assertTrue(payload1["ok"])
                self.assertTrue(payload1["refused"])

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                if method == "GET" and str(url).endswith("/accounts/acct1/load_balancers/regions"):
                    return _DummyResponse(status=200, url=url, body=secret_bytes)
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request):
                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "load-balancers",
                            "regions",
                            "list",
                            "--account-id",
                            "acct1",
                            "--out",
                            "regions.json",
                        ]
                    )
                self.assertEqual(rc2, 0)
                out_text = buf2.getvalue()
                self.assertNotIn("SECRET_REGION_SHOULD_NOT_PRINT", out_text)
                payload2 = json.loads(out_text)
                self.assertTrue(payload2["ok"])
                self.assertFalse(payload2.get("changed"), "load-balancers regions list should be read-like (changed=false)")
                out_path = project_dir / "regions.json"
                self.assertTrue(out_path.exists())
                self.assertEqual(out_path.read_bytes(), secret_bytes)

    def test_load_balancers_search_apply_requires_out_and_calls_get(self) -> None:
        secret_bytes = b'{"results":["SECRET_SEARCH_RESULT_SHOULD_NOT_PRINT"]}\n'

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"

            def fake_request_never(self, method, url, **kwargs):  # noqa: ANN001
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request_never):
                buf1 = io.StringIO()
                with redirect_stdout(buf1):
                    rc1 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "load-balancers",
                            "search",
                            "--account-id",
                            "acct1",
                            "--query",
                            "name=example",
                        ]
                    )
                self.assertEqual(rc1, 0)
                payload1 = json.loads(buf1.getvalue())
                self.assertTrue(payload1["ok"])
                self.assertTrue(payload1["refused"])

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                if (
                    method == "GET"
                    and str(url).endswith("/accounts/acct1/load_balancers/search")
                    and kwargs.get("params") == {"name": "example"}
                ):
                    return _DummyResponse(status=200, url=url, body=secret_bytes)
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request):
                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "load-balancers",
                            "search",
                            "--account-id",
                            "acct1",
                            "--query",
                            "name=example",
                            "--out",
                            "search.json",
                        ]
                    )
                self.assertEqual(rc2, 0)
                out_text = buf2.getvalue()
                self.assertNotIn("SECRET_SEARCH_RESULT_SHOULD_NOT_PRINT", out_text)
                payload2 = json.loads(out_text)
                self.assertTrue(payload2["ok"])
                self.assertFalse(payload2.get("changed"), "load-balancers search should be read-like (changed=false)")
                out_path = project_dir / "search.json"
                self.assertTrue(out_path.exists())
                self.assertEqual(out_path.read_bytes(), secret_bytes)

    def test_load_balancers_preview_result_get_apply_requires_out_and_calls_get(self) -> None:
        secret_bytes = b'{"preview":"SECRET_PREVIEW_RESULT_SHOULD_NOT_PRINT"}\n'

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"

            def fake_request_never(self, method, url, **kwargs):  # noqa: ANN001
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request_never):
                buf1 = io.StringIO()
                with redirect_stdout(buf1):
                    rc1 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "load-balancers",
                            "preview-result",
                            "get",
                            "--account-id",
                            "acct1",
                            "--preview-id",
                            "p1",
                        ]
                    )
                self.assertEqual(rc1, 0)
                payload1 = json.loads(buf1.getvalue())
                self.assertTrue(payload1["ok"])
                self.assertTrue(payload1["refused"])

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                if method == "GET" and str(url).endswith("/accounts/acct1/load_balancers/preview/p1"):
                    return _DummyResponse(status=200, url=url, body=secret_bytes)
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request):
                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "load-balancers",
                            "preview-result",
                            "get",
                            "--account-id",
                            "acct1",
                            "--preview-id",
                            "p1",
                            "--out",
                            "preview_result.json",
                        ]
                    )
                self.assertEqual(rc2, 0)
                out_text = buf2.getvalue()
                self.assertNotIn("SECRET_PREVIEW_RESULT_SHOULD_NOT_PRINT", out_text)
                payload2 = json.loads(out_text)
                self.assertTrue(payload2["ok"])
                self.assertFalse(payload2.get("changed"), "load-balancers preview-result get should be read-like (changed=false)")
                out_path = project_dir / "preview_result.json"
                self.assertTrue(out_path.exists())
                self.assertEqual(out_path.read_bytes(), secret_bytes)

    def test_load_balancers_pools_patch_all_apply_missing_yes_refuses_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"

            body_path = root / "body.json"
            body_path.write_text('{"pools":[{"id":"p1"}]}\n', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "load-balancers",
                        "pools",
                        "patch-all",
                        "--account-id",
                        "acct1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        "patch_all.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
