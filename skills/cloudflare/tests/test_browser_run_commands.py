from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from cloudflare_api_tool.cli import main


class _DummyResponse:
    def __init__(self, *, status: int, url: str, obj: Any | None = None, raw: bytes | None = None):
        self.status_code = int(status)
        self.url = str(url)
        self.headers: dict[str, str] = {}
        if raw is not None:
            self.content = raw
        else:
            self.content = json.dumps(obj, ensure_ascii=False).encode("utf-8")

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


class TestBrowserRunCommands(unittest.TestCase):
    def test_crawl_rejects_non_positive_depth(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "browser-run",
                        "crawl",
                        "--url",
                        "https://example.com/",
                        "--depth",
                        "0",
                        "--out",
                        "./crawl.json",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("--depth must be >= 1", payload["error"])

    def test_markdown_builds_body_from_flags(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(
                {
                    "method": method,
                    "url": str(url),
                    "params": kwargs.get("params"),
                    "json": kwargs.get("json"),
                }
            )
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": {"markdown": "# Example"}},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            out_path = root / "markdown.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "browser-run",
                        "markdown",
                        "--account-id",
                        "acc1",
                        "--url",
                        "https://example.com/",
                        "--cache-ttl",
                        "120",
                        "--goto-wait-until",
                        "networkidle0",
                        "--goto-timeout-ms",
                        "9000",
                        "--wait-for-selector",
                        "main",
                        "--wait-for-selector-visible",
                        "--wait-for-selector-timeout-ms",
                        "3000",
                        "--out",
                        "./markdown.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(calls[0]["method"], "POST")
            self.assertEqual(calls[0]["url"], "http://example.invalid/client/v4/accounts/acc1/browser-rendering/markdown")
            self.assertEqual(calls[0]["params"]["cacheTTL"], "120")
            self.assertEqual(calls[0]["json"]["url"], "https://example.com/")
            self.assertEqual(calls[0]["json"]["gotoOptions"]["waitUntil"], "networkidle0")
            self.assertEqual(calls[0]["json"]["gotoOptions"]["timeout"], 9000)
            self.assertEqual(calls[0]["json"]["waitForSelector"]["selector"], "main")
            self.assertTrue(calls[0]["json"]["waitForSelector"]["visible"])
            self.assertEqual(calls[0]["json"]["waitForSelector"]["timeout"], 3000)
            self.assertTrue(out_path.exists())

    def test_markdown_uses_default_account_when_omitted(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": {"markdown": "# Example"}},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            sink = io.StringIO()
            with redirect_stdout(sink):
                _ = main(["--env-file", str(env_path), "accounts", "set-default", "--account-id", "acc_default"])
            with redirect_stdout(io.StringIO()):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "browser-run",
                        "markdown",
                        "--url",
                        "https://example.com/",
                        "--out",
                        "./markdown.json",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertIn("/accounts/acc_default/browser-rendering/markdown", calls[0])

    def test_scrape_builds_elements_and_render_options(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"json": kwargs.get("json"), "url": str(url)})
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": [{"selector": "h1"}]},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            with redirect_stdout(io.StringIO()):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "browser-run",
                        "scrape",
                        "--account-id",
                        "acc1",
                        "--url",
                        "https://example.com/",
                        "--selector",
                        "h1",
                        "--selector",
                        "a",
                        "--reject-resource-type",
                        "image",
                        "--viewport-width",
                        "1280",
                        "--viewport-height",
                        "720",
                        "--out",
                        "./scrape.json",
                    ]
                )
            self.assertEqual(rc, 0)
            body = calls[0]["json"]
            self.assertEqual(calls[0]["url"], "http://example.invalid/client/v4/accounts/acc1/browser-rendering/scrape")
            self.assertEqual(body["elements"], [{"selector": "h1"}, {"selector": "a"}])
            self.assertEqual(body["rejectResourceTypes"], ["image"])
            self.assertEqual(body["viewport"], {"width": 1280, "height": 720})

    def test_screenshot_builds_binary_request_body(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"json": kwargs.get("json"), "url": str(url)})
            return _DummyResponse(status=200, url=url, raw=b"PNGDATA")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            screenshot_file = root / "shot.bin"
            with redirect_stdout(io.StringIO()):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "browser-run",
                        "screenshot",
                        "--account-id",
                        "acc1",
                        "--url",
                        "https://example.com/",
                        "--full-page",
                        "--omit-background",
                        "--image-type",
                        "jpeg",
                        "--out",
                        "./shot.bin",
                    ]
                )
            self.assertEqual(rc, 0)
            body = calls[0]["json"]
            self.assertEqual(calls[0]["url"], "http://example.invalid/client/v4/accounts/acc1/browser-rendering/screenshot")
            self.assertTrue(body["fullPage"])
            self.assertTrue(body["omitBackground"])
            self.assertEqual(body["type"], "jpeg")
            self.assertEqual(screenshot_file.read_bytes(), b"PNGDATA")

    def test_crawl_and_crawl_result_map_expected_fields(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(
                {
                    "method": method,
                    "url": str(url),
                    "params": kwargs.get("params"),
                    "json": kwargs.get("json"),
                }
            )
            if method == "POST":
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={"success": True, "errors": [], "messages": [], "result": {"jobId": "job_123"}},
                )
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": {"status": "completed"}},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            with redirect_stdout(io.StringIO()):
                rc_crawl = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "browser-run",
                        "crawl",
                        "--account-id",
                        "acc1",
                        "--url",
                        "https://example.com/",
                        "--depth",
                        "2",
                        "--limit",
                        "10",
                        "--source",
                        "links",
                        "--format",
                        "markdown",
                        "--format",
                        "json",
                        "--include-pattern",
                        "example.com/docs/*",
                        "--exclude-pattern",
                        "example.com/private/*",
                        "--include-subdomains",
                        "--no-render",
                        "--out",
                        "./crawl.json",
                    ]
                )
                rc_result = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "browser-run",
                        "crawl-result",
                        "--account-id",
                        "acc1",
                        "--job-id",
                        "job_123",
                        "--status",
                        "completed",
                        "--limit",
                        "5",
                        "--cursor",
                        "cur_1",
                        "--out",
                        "./crawl_result.json",
                    ]
                )
            self.assertEqual(rc_crawl, 0)
            self.assertEqual(rc_result, 0)
            crawl_call = calls[0]
            result_call = calls[1]
            self.assertEqual(crawl_call["url"], "http://example.invalid/client/v4/accounts/acc1/browser-rendering/crawl")
            self.assertEqual(crawl_call["json"]["depth"], 2)
            self.assertEqual(crawl_call["json"]["limit"], 10)
            self.assertEqual(crawl_call["json"]["source"], "links")
            self.assertEqual(crawl_call["json"]["formats"], ["markdown", "json"])
            self.assertEqual(crawl_call["json"]["includePatterns"], ["example.com/docs/*"])
            self.assertEqual(crawl_call["json"]["excludePatterns"], ["example.com/private/*"])
            self.assertTrue(crawl_call["json"]["includeSubdomains"])
            self.assertFalse(crawl_call["json"]["render"])
            self.assertEqual(
                result_call["url"],
                "http://example.invalid/client/v4/accounts/acc1/browser-rendering/crawl/job_123",
            )
            self.assertEqual(result_call["method"], "GET")
            self.assertEqual(result_call["params"]["status"], "completed")
            self.assertEqual(result_call["params"]["limit"], "5")
            self.assertEqual(result_call["params"]["cursor"], "cur_1")
