from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cloudflare_api_tool.cli import main
from cloudflare_api_tool.operation_keys import allowlisted_operation_command_by_method_path
from tests._live_inventory import load_live_inventory_rows


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


def _strip_ticks(s: str) -> str:
    t = str(s or "").strip()
    if t.startswith("`") and t.endswith("`") and len(t) >= 2:
        return t[1:-1].strip()
    return t


class TestOperationsCoverageDrift(unittest.TestCase):
    def test_active_live_coverage_ledger_maps_to_operations_commands(self) -> None:
        tool_root = Path(__file__).resolve().parents[1]
        md_path = tool_root / "docs" / "api_coverage_live_official.md"
        text = md_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        header_idx = None
        for i, line in enumerate(lines):
            if line.startswith("| Status |") and "| Method |" in line and "| Path |" in line:
                header_idx = i
                break
        self.assertIsNotNone(header_idx, msg=f"missing coverage table header: {md_path}")
        assert header_idx is not None

        header_cols = _split_md_row(lines[header_idx])
        col_index = {name: idx for idx, name in enumerate(header_cols)}
        self.assertIn("Method", col_index, msg=f"missing Method column: {md_path}")
        self.assertIn("Path", col_index, msg=f"missing Path column: {md_path}")
        self.assertIn("CLI command(s)", col_index, msg=f"missing CLI command(s) column: {md_path}")

        method_i = int(col_index["Method"])
        path_i = int(col_index["Path"])

        seen_pairs: set[tuple[str, str]] = set()
        for line in lines[header_idx + 2 :]:
            if not line.startswith("|"):
                break
            if line.startswith("|---"):
                continue
            cols = _split_md_row(line)
            if len(cols) < len(header_cols):
                continue
            method = str(cols[method_i] or "").strip().upper()
            path = _strip_ticks(str(cols[path_i] or ""))
            if not method or not path:
                continue

            expected = allowlisted_operation_command_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(expected, msg=f"allowlist missing operation for {md_path}: {method} {path}")
            assert expected is not None

            actual_cli = None
            for cell in cols:
                c = str(cell or "").strip()
                if c.startswith("cloudflare-api-tool "):
                    actual_cli = c
                    break
            self.assertIsNotNone(actual_cli, msg=f"missing CLI cell for {md_path}: {method} {path}")
            assert actual_cli is not None
            self.assertEqual(actual_cli, expected.command, msg=f"drift in {md_path}: {method} {path}")
            seen_pairs.add((method, path))

        expected_pairs = {
            (str(row.get("method") or "").upper().strip(), str(row.get("path_template") or "").strip())
            for row in load_live_inventory_rows()
        }
        self.assertEqual(seen_pairs, expected_pairs)

    def test_openapi_bridge_is_not_on_cli(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        with patch("requests.Session.request", new=fake_request):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["openapi", "call", "--operation-id", "zones-get"])
            # Parse error should be a hard error (non-zero) and must not call HTTP.
            self.assertNotEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
