from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cloudflare_api_tool.cli import main
from cloudflare_api_tool.operation_keys import allowlisted_operation_command_by_method_path
from cloudflare_api_tool.openapi_index import load_allowlisted_operation_index
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


class TestPhase27TopLevelAllowlist(unittest.TestCase):
    def test_allowlist_matches_full_live_inventory_method_path_pairs(self) -> None:
        rows = load_live_inventory_rows()
        expected = {(str(r.get("method") or "").upper().strip(), str(r.get("path_template") or "").strip()) for r in rows}
        expected.discard(("", ""))
        self.assertGreater(len(expected), 0)

        idx = load_allowlisted_operation_index()
        actual = {(s.method, s.path_template) for s in idx.all_specs()}

        self.assertEqual(expected, actual)

    def test_allowlist_covers_user_live_inventory_subset(self) -> None:
        rows = load_live_inventory_rows()
        expected = {
            (str(r.get("method") or "").upper().strip(), str(r.get("path_template") or "").strip())
            for r in rows
            if str(r.get("path_template") or "").strip().startswith("/user")
        }
        expected.discard(("", ""))
        self.assertGreater(len(expected), 0)

        idx = load_allowlisted_operation_index()
        for method, path in sorted(expected):
            self.assertIsNotNone(idx.get_by_method_path(method=method, path_template=path), msg=f"missing allowlist: {method} {path}")

    def test_allowlist_covers_organizations_live_inventory_subset(self) -> None:
        rows = load_live_inventory_rows()
        expected = {
            (str(r.get("method") or "").upper().strip(), str(r.get("path_template") or "").strip())
            for r in rows
            if str(r.get("path_template") or "").strip().startswith("/organizations/")
        }
        expected.discard(("", ""))
        self.assertGreater(len(expected), 0)

        idx = load_allowlisted_operation_index()
        for method, path in sorted(expected):
            self.assertIsNotNone(idx.get_by_method_path(method=method, path_template=path), msg=f"missing allowlist: {method} {path}")

    def test_allowlist_covers_system_misc_live_inventory_subset(self) -> None:
        rows = load_live_inventory_rows()
        expected = {
            (str(r.get("method") or "").upper().strip(), str(r.get("path_template") or "").strip())
            for r in rows
            if str(r.get("path_template") or "").strip().startswith(("/memberships", "/tenants", "/system", "/certificates", "/destinations"))
            or str(r.get("path_template") or "").strip() in {"/accounts", "/zones", "/ips", "/live", "/ready"}
        }
        expected.discard(("", ""))
        self.assertGreater(len(expected), 0)

        idx = load_allowlisted_operation_index()
        for method, path in sorted(expected):
            self.assertIsNotNone(idx.get_by_method_path(method=method, path_template=path), msg=f"missing allowlist: {method} {path}")

    def test_operations_list_hides_user_endpoints_by_default(self) -> None:
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
                        "/user/tokens",
                        "--method",
                        "GET",
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
                        "/user/tokens",
                        "--method",
                        "GET",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_call_delete_membership_requires_ack_irreversible(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_method_path(method="DELETE", path_template="/memberships/{membership_id}")
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
                        "--path-param",
                        "membership_id=m1",
                        "--out",
                        str(root / "out.json"),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
