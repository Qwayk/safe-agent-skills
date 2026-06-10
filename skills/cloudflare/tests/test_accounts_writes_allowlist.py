from __future__ import annotations

import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from cloudflare_api_tool.cli import main
from cloudflare_api_tool.operation_keys import (
    allowlisted_operation_command_by_method_path,
    allowlisted_operation_command_by_operation_id,
)
from cloudflare_api_tool.openapi_index import load_allowlisted_operation_index
from tests._live_inventory import load_live_inventory_rows


class _DummyResponse:
    def __init__(self, *, status: int, url: str, obj: Any | None, body: bytes | None = None):
        self.status_code = int(status)
        self.url = str(url)
        if body is not None:
            self.content = body
        else:
            self.content = (json.dumps(obj, ensure_ascii=False) if obj is not None else "").encode("utf-8")
        self.headers: dict[str, str] = {}


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


def _first_live_account_write_pair() -> tuple[str, str]:
    rows = load_live_inventory_rows()
    preferred = sorted(
        [
            (str(r.get("method") or "").upper().strip(), str(r.get("path_template") or "").strip())
            for r in rows
            if str(r.get("method") or "").upper().strip() in {"POST", "PUT", "PATCH"}
            and (str(r.get("path_template") or "").strip() == "/accounts" or str(r.get("path_template") or "").strip().startswith("/accounts/"))
            and str(r.get("sensitivity") or "") != "sensitive_write_result"
        ]
    )
    if preferred:
        return preferred[0]
    pairs = sorted(
        {
            (str(r.get("method") or "").upper().strip(), str(r.get("path_template") or "").strip())
            for r in rows
            if str(r.get("method") or "").upper().strip() in {"POST", "PUT", "PATCH", "DELETE"}
            and (str(r.get("path_template") or "").strip() == "/accounts" or str(r.get("path_template") or "").strip().startswith("/accounts/"))
        }
    )
    if not pairs:
        raise AssertionError("live inventory has no /accounts write operations")
    return pairs[0]


class TestAccountsWritesAllowlist(unittest.TestCase):
    def test_accounts_writes_allowlist_covers_all_live_account_write_pairs(self) -> None:
        rows = load_live_inventory_rows()
        expected: set[tuple[str, str]] = set()
        for r in rows:
            method = str(r.get("method") or "").upper().strip()
            path = str(r.get("path_template") or "").strip()
            if method not in {"POST", "PUT", "PATCH", "DELETE"}:
                continue
            if not (path == "/accounts" or path.startswith("/accounts/")):
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
            raise AssertionError(f"missing allowlist for {len(missing)} /accounts write operations: {preview}")

    def test_operations_call_account_write_refuses_apply_without_yes_and_makes_no_http_call(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        method, path_template = _first_live_account_write_pair()

        self.assertIn(method, {"POST", "PUT", "PATCH", "DELETE"})
        self.assertTrue(path_template == "/accounts" or path_template.startswith("/accounts/"))

        names = re.findall(r"\{([^}]+)\}", path_template)
        params: list[str] = []
        for n in names:
            if n == "account_id":
                params.append("account_id=acc1")
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

    def test_operations_call_account_write_refuses_apply_missing_out_and_makes_no_http_call(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        method, path_template = _first_live_account_write_pair()

        names = re.findall(r"\{([^}]+)\}", path_template)
        params: list[str] = []
        for n in names:
            if n == "account_id":
                params.append("account_id=acc1")
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
                        "--yes",
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
            reasons = " ".join([str(x) for x in (payload.get("reasons") or [])])
            self.assertIn("--out", reasons)

    def test_operations_call_delete_account_requires_ack_irreversible_and_makes_no_http_call(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            out_file = root / "out.json"

            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("account-deletion")
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
                        "account_id=acc1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            reasons = " ".join([str(x) for x in (payload.get("reasons") or [])])
            self.assertIn("ack-irreversible", reasons)

    def test_operations_call_account_write_apply_is_file_only_and_receipt_is_redacted(self) -> None:
        sentinel_put = "ACCOUNTS_WRITE_PUT_RESPONSE_SHOULD_NOT_PRINT"
        sentinel_get = "ACCOUNTS_WRITE_VERIFICATION_GET_SHOULD_NOT_PRINT"

        seen: list[tuple[str, str]] = []

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            seen.append((str(method), str(url)))
            if method == "PUT" and str(url).endswith("/accounts/acc1"):
                body = json.dumps({"success": True, "errors": [], "messages": [], "result": {"ok": True, "note": sentinel_put}}, ensure_ascii=False).encode(
                    "utf-8"
                )
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            if method == "GET" and str(url).endswith("/accounts/acc1"):
                body = json.dumps({"success": True, "errors": [], "messages": [], "result": {"ok": True, "note": sentinel_get}}, ensure_ascii=False).encode(
                    "utf-8"
                )
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            out_file = root / "out" / "account_put.json"

            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("accounts-update-account")
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
                        "account_id=acc1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("refused", False))
            self.assertIn("file", payload)
            self.assertNotIn("result", payload)

            self.assertTrue(out_file.exists())
            self.assertIn(sentinel_put, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel_put, buf.getvalue())
            self.assertNotIn(sentinel_put, json.dumps(payload, ensure_ascii=False))
            self.assertNotIn(sentinel_get, buf.getvalue())
            self.assertNotIn(sentinel_get, json.dumps(payload, ensure_ascii=False))

            receipt = payload.get("receipt") or {}
            verification = receipt.get("verification") or {}
            evidence = verification.get("evidence")
            if evidence is not None:
                self.assertIsInstance(evidence, dict)
                self.assertTrue(set(evidence.keys()).issubset({"http_status", "size_bytes", "sha256"}))
                self.assertNotIn(sentinel_get, json.dumps(evidence, ensure_ascii=False))

            self.assertIn(("PUT", "http://example.invalid/client/v4/accounts/acc1"), seen)
            self.assertIn(("GET", "http://example.invalid/client/v4/accounts/acc1"), seen)
