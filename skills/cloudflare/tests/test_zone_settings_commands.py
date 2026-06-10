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


def _json_envelope(result: Any) -> bytes:
    return json.dumps({"success": True, "errors": [], "messages": [], "result": result, "result_info": {}}, ensure_ascii=False).encode(
        "utf-8"
    )


class TestZoneSettingsCommands(unittest.TestCase):
    def test_unknown_setting_path_is_rejected_and_makes_no_http_calls(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "zones",
                        "settings",
                        "setting-get",
                        "--zone-id",
                        "z1",
                        "--setting-path",
                        "not-a-real-setting",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(calls, [])

    def test_zones_settings_patch_dry_run_emits_plan_and_makes_no_http_calls(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_path = root / "body.json"
            body_path.write_text(json.dumps({"example": True}, sort_keys=True), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "zones",
                        "settings",
                        "patch",
                        "--zone-id",
                        "z1",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["command"], "zones.settings.patch")
            self.assertIn("plan", payload)
            self.assertEqual(calls, [])

    def test_zones_settings_patch_apply_without_yes_refuses_and_makes_no_http_calls(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_path = root / "body.json"
            body_path.write_text(json.dumps({"example": True}, sort_keys=True), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "zones",
                        "settings",
                        "patch",
                        "--zone-id",
                        "z1",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])

    def test_zones_settings_setting_patch_apply_patches_then_reads_back(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url)})
            if method == "PATCH" and str(url).endswith("/zones/z1/settings/aegis"):
                return _DummyResponse(status=200, url=url, body=_json_envelope({"id": "aegis", "value": "on"}))
            if method == "GET" and str(url).endswith("/zones/z1/settings/aegis"):
                return _DummyResponse(status=200, url=url, body=_json_envelope({"id": "aegis", "value": "on"}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_path = root / "body.json"
            body_path.write_text(json.dumps({"value": "on"}, sort_keys=True), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "zones",
                        "settings",
                        "setting-patch",
                        "--zone-id",
                        "z1",
                        "--setting-path",
                        "aegis",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])
