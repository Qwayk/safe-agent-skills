from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cloudflare_api_tool.cli import main
from cloudflare_api_tool.operation_keys import allowlisted_operation_command_by_operation_id
from cloudflare_api_tool.openapi_index import is_read_like_non_get_operation, load_allowlisted_operation_index
from tests._live_inventory import load_live_inventory_rows


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


class TestRadarAllAllowlist(unittest.TestCase):
    def test_radar_all_allowlist_is_exact_match_to_live_inventory(self) -> None:
        rows = load_live_inventory_rows()
        expected = {
            (str(r.get("method") or "").upper().strip(), str(r.get("path_template") or "").strip())
            for r in rows
            if str(r.get("path_template") or "").strip().startswith("/radar/")
        }
        self.assertNotIn(("", ""), expected)
        self.assertTrue(all(p.startswith("/radar/") for _, p in expected))
        self.assertNotIn(("GET", "/radar"), expected)

        idx = load_allowlisted_operation_index()
        radar_specs = [s for s in idx.all_specs() if str(s.path_template or "").startswith("/radar/")]
        actual = {(s.method, s.path_template) for s in radar_specs}

        self.assertEqual(expected, actual)

        for s in radar_specs:
            self.assertEqual(s.sensitivity, "sensitive_read", msg=f"unexpected sensitivity for {s.method} {s.path_template}")

    def test_dataset_download_is_write_like_and_not_read_like(self) -> None:
        idx = load_allowlisted_operation_index()
        spec = idx.get_by_method_path(method="POST", path_template="/radar/datasets/download")
        self.assertIsNotNone(spec)
        assert spec is not None

        self.assertEqual(spec.sensitivity, "sensitive_read")
        self.assertFalse(is_read_like_non_get_operation(spec))

    def test_operations_list_hides_radar_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "/radar/",
                        "--limit",
                        "50",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "/radar/",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_call_radar_dataset_download_refuses_apply_without_yes(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("radar-post-reports-dataset-download-url")
            self.assertIsNotNone(cmd)
            assert cmd is not None
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "operations",
                        cmd.area,
                        cmd.op_key,
                        "--out",
                        "out/radar_datasets_download_url.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_radar_dataset_download_refuses_missing_out(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("radar-post-reports-dataset-download-url")
            self.assertIsNotNone(cmd)
            assert cmd is not None
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "operations",
                        cmd.area,
                        cmd.op_key,
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
