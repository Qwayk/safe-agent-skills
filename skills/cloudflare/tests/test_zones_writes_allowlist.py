from __future__ import annotations

import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cloudflare_api_tool.cli import main
from cloudflare_api_tool.operation_keys import (
    allowlisted_operation_command_by_method_path,
    allowlisted_operation_command_by_operation_id,
)
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


def _strip_ticks(s: str) -> str:
    t = str(s or "").strip()
    if t.startswith("`") and t.endswith("`") and len(t) >= 2:
        return t[1:-1].strip()
    return t


def _first_table_row(md_path: Path) -> dict[str, str]:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if line.startswith("| Status |") and "| Method |" in line and "| Path |" in line:
            header_idx = i
            break
    if header_idx is None:
        raise AssertionError(f"Could not find coverage table header in: {md_path}")

    def _split_md_row(row_line: str) -> list[str]:
        s = str(row_line or "").strip()
        if not s.startswith("|"):
            return []
        s = s.strip().strip("|")
        cols: list[str] = []
        cur: list[str] = []
        esc = False
        for ch in s:
            if esc:
                cur.append(ch)
                esc = False
                continue
            if ch == "\\":
                esc = True
                continue
            if ch == "|":
                cols.append("".join(cur).strip())
                cur = []
                continue
            cur.append(ch)
        if esc:
            cur.append("\\")
        cols.append("".join(cur).strip())
        return cols

    header_cols = _split_md_row(lines[header_idx])
    col_index = {name: idx for idx, name in enumerate(header_cols)}
    for required in ["Status", "Method", "Path"]:
        if required not in col_index:
            raise AssertionError(f"Coverage table missing required column {required!r} in: {md_path}")

    for line in lines[header_idx + 2 :]:
        if not line.startswith("|"):
            break
        if line.startswith("|---"):
            continue
        cols = _split_md_row(line)
        if len(cols) != len(header_cols):
            continue
        return {header_cols[j]: cols[j] for j in range(len(header_cols))}

    raise AssertionError(f"Coverage table has no rows in: {md_path}")


def _first_live_zone_write_pair() -> tuple[str, str]:
    rows = load_live_inventory_rows()
    pairs = sorted(
        {
            (str(r.get("method") or "").upper().strip(), str(r.get("path_template") or "").strip())
            for r in rows
            if str(r.get("method") or "").upper().strip() in {"POST", "PUT", "PATCH", "DELETE"}
            and (str(r.get("path_template") or "").strip() == "/zones" or str(r.get("path_template") or "").strip().startswith("/zones/"))
        }
    )
    if not pairs:
        raise AssertionError("live inventory has no /zones write operations")
    return pairs[0]


class TestZonesWritesAllowlist(unittest.TestCase):
    def test_zones_writes_allowlist_covers_all_live_zone_write_pairs(self) -> None:
        rows = load_live_inventory_rows()
        expected: set[tuple[str, str]] = set()
        for r in rows:
            method = str(r.get("method") or "").upper().strip()
            path = str(r.get("path_template") or "").strip()
            if method not in {"POST", "PUT", "PATCH", "DELETE"}:
                continue
            if not (path == "/zones" or path.startswith("/zones/")):
                continue
            expected.add((method, path))

        self.assertGreater(len(expected), 0)

        idx = load_allowlisted_operation_index()
        missing: list[tuple[str, str]] = []
        for method, path in sorted(expected):
            if idx.get_by_method_path(method=method, path_template=path) is None:
                missing.append((method, path))
        if missing:
            preview = ", ".join([f"{m} {p}" for m, p in missing[:10]])
            raise AssertionError(f"missing allowlist for {len(missing)} /zones write operations: {preview}")

    def test_operations_call_zone_write_refuses_apply_without_yes_and_makes_no_http_call(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        method, path_template = _first_live_zone_write_pair()

        self.assertIn(method, {"POST", "PUT", "PATCH", "DELETE"})
        self.assertTrue(path_template == "/zones" or path_template.startswith("/zones/"))

        names = re.findall(r"\{([^}]+)\}", path_template)
        params: list[str] = []
        for n in names:
            if n == "account_id":
                params.append("account_id=acc1")
            elif n in {"zone_id", "zone_identifier"}:
                params.append(f"{n}=z1")
            else:
                params.append(f"{n}=x1")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_method_path(method=method, path_template=path_template)
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

    def test_operations_call_delete_zone_requires_ack_irreversible_and_makes_no_http_call(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("zones-0-delete")
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
                        "zone_id=z1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            reasons = " ".join([str(x) for x in (payload.get("reasons") or [])])
            self.assertIn("ack-irreversible", reasons)
