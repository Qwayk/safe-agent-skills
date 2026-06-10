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
from cloudflare_api_tool.openapi_index import load_allowlisted_operation_index


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


class TestRadarAttacksAllowlist(unittest.TestCase):
    def test_allowlist_includes_radar_attacks_layer7_and_layer3_summary(self) -> None:
        idx = load_allowlisted_operation_index()

        self.assertIsNotNone(idx.get("radar-get-attacks-layer7-summary"))
        self.assertIsNotNone(idx.get("radar-get-attacks-layer3-summary"))

        spec7 = idx.get_by_method_path(method="GET", path_template="/radar/attacks/layer7/summary/{dimension}")
        self.assertIsNotNone(spec7)
        assert spec7 is not None
        self.assertEqual(spec7.sensitivity, "sensitive_read")

        spec3 = idx.get_by_method_path(method="GET", path_template="/radar/attacks/layer3/summary/{dimension}")
        self.assertIsNotNone(spec3)
        assert spec3 is not None
        self.assertEqual(spec3.sensitivity, "sensitive_read")

    def test_operations_list_hides_radar_attacks_by_default(self) -> None:
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
                        "/radar/attacks/",
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
                        "/radar/attacks/",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_call_radar_attacks_refuses_missing_out_on_apply(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("radar-get-attacks-layer7-summary")
            self.assertIsNotNone(cmd)
            assert cmd is not None
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "operations",
                        cmd.area,
                        cmd.op_key,
                        "--path-param",
                        "dimension=http_method",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
