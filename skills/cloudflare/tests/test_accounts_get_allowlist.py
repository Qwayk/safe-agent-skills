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


class TestAccountsGetAllowlist(unittest.TestCase):
    def test_accounts_get_allowlist_is_exact_match_to_live_inventory(self) -> None:
        rows = load_live_inventory_rows()
        expected = {
            (str(r.get("method") or "").upper().strip(), str(r.get("path_template") or "").strip())
            for r in rows
            if str(r.get("method") or "").upper().strip() == "GET"
            and str(r.get("path_template") or "").strip().startswith("/accounts/")
        }
        self.assertNotIn(("", ""), expected)
        self.assertTrue(all(m == "GET" for m, _ in expected))
        self.assertTrue(all(p.startswith("/accounts/") for _, p in expected))
        self.assertNotIn(("GET", "/accounts"), expected)

        idx = load_allowlisted_operation_index()
        account_get_specs = [s for s in idx.all_specs() if (s.method == "GET") and str(s.path_template or "").startswith("/accounts/")]
        actual = {(s.method, s.path_template) for s in account_get_specs}

        self.assertEqual(expected, actual)

        accounts_get_area_specs = [s for s in account_get_specs if s.area == "accounts_get"]
        self.assertGreater(len(accounts_get_area_specs), 0, msg="expected at least one Accounts GET operation to come from accounts_get ledger")
        for s in accounts_get_area_specs:
            self.assertEqual(s.sensitivity, "sensitive_read", msg=f"unexpected sensitivity for {s.method} {s.path_template}")

    def test_operations_list_hides_accounts_get_area_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            idx = load_allowlisted_operation_index()
            pick = max((s for s in idx.all_specs() if s.area == "accounts_get"), key=lambda s: len(s.path_template), default=None)
            self.assertIsNotNone(pick, msg="expected at least one spec in accounts_get area")
            assert pick is not None

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        pick.path_template,
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
                        pick.path_template,
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

    def test_operations_call_accounts_get_refuses_apply_missing_out(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            idx = load_allowlisted_operation_index()
            pick = max((s for s in idx.all_specs() if s.area == "accounts_get"), key=lambda s: len(s.path_template), default=None)
            self.assertIsNotNone(pick, msg="expected at least one spec in accounts_get area")
            assert pick is not None

            import re

            names = re.findall(r"\{([^}]+)\}", pick.path_template)
            params: list[str] = []
            for n in names:
                if n == "account_id":
                    params.append("account_id=acc1")
                elif n == "zone_id":
                    params.append("zone_id=z1")
                else:
                    params.append(f"{n}=x1")

            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_method_path(method=pick.method, path_template=pick.path_template)
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
                        *[x for kv in params for x in ["--path-param", kv]],
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
