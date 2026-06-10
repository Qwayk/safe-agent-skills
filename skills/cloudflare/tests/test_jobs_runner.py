from __future__ import annotations

import csv
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
    def __init__(self, *, status: int, url: str, obj: Any | None):
        self.status_code = int(status)
        self.url = str(url)
        self.headers: dict[str, str] = {}
        self.content = (json.dumps(obj, ensure_ascii=False) if obj is not None else "").encode("utf-8")


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


def _ok(obj: Any) -> dict[str, Any]:
    return {"success": True, "errors": [], "messages": [], "result": obj}


class TestJobsRunner(unittest.TestCase):
    def test_jobs_dry_run_does_not_hit_http(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call in dry-run: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            jobs_csv = root / "jobs.csv"
            with open(jobs_csv, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(
                    f,
                    fieldnames=[
                        "operation_id",
                        "method",
                        "path",
                        "path_params_json",
                        "query_json",
                        "body_json_file",
                        "body_bytes_file",
                        "multipart_spec_file",
                        "content_type",
                        "out",
                        "overwrite",
                    ],
                )
                w.writeheader()
                w.writerow(
                    {
                        "operation_id": "worker-script-list-workers",
                        "path_params_json": json.dumps({"account_id": "acc1"}),
                    }
                )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "jobs", "run", "--file", str(jobs_csv)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)

    def test_jobs_dry_run_does_not_require_token(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call in dry-run: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "CLOUDFLARE_API_BASE_URL=http://example.invalid/client/v4",
                        "CLOUDFLARE_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            jobs_csv = root / "jobs.csv"
            jobs_csv.write_text(
                "operation_id,path_params_json\n" + "worker-script-list-workers," + json.dumps({"account_id": "acc1"}) + "\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "jobs", "run", "--file", str(jobs_csv)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

    def test_jobs_dry_run_supports_dns_allowlist(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call in dry-run: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "CLOUDFLARE_API_BASE_URL=http://example.invalid/client/v4",
                        "CLOUDFLARE_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            jobs_csv = root / "jobs.csv"
            jobs_csv.write_text(
                "method,path,path_params_json\n" + "GET,/zones/{zone_id}/dns_records," + json.dumps({"zone_id": "z1"}) + "\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "jobs", "run", "--file", str(jobs_csv)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

    def test_jobs_apply_read_only_executes(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/scripts"):
                return _DummyResponse(status=200, url=url, obj=_ok([{"id": "s1"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            jobs_csv = root / "jobs.csv"
            jobs_csv.write_text(
                "operation_id,path_params_json\n"
                + "worker-script-list-workers,"
                + json.dumps({"account_id": "acc1"})
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--apply", "jobs", "run", "--file", str(jobs_csv)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertIn("receipt", payload)

    def test_jobs_apply_with_write_requires_yes(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call (should require explicit no-snapshot approval before HTTP): {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            jobs_csv = root / "jobs.csv"
            # POST /accounts/{account_id}/access/apps exists in the snapshot (Zero Trust).
            jobs_csv.write_text(
                "method,path,path_params_json,body_json_file\n"
                + "POST,/accounts/{account_id}/access/apps,"
                + json.dumps({"account_id": "acc1"})
                + ",\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--apply", "jobs", "run", "--file", str(jobs_csv)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_jobs_apply_read_like_post_requires_out_but_not_yes(self) -> None:
        sentinel = "KV_VALUE_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/storage/kv/namespaces/ns1/bulk/get"):
                return _DummyResponse(status=200, url=url, obj=_ok({"k": sentinel}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            jobs_csv = root / "jobs.csv"

            # Missing out should require explicit no-snapshot approval before any HTTP.
            with open(jobs_csv, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(
                    f,
                    fieldnames=[
                        "operation_id",
                        "method",
                        "path",
                        "path_params_json",
                        "query_json",
                        "body_json_file",
                        "body_bytes_file",
                        "multipart_spec_file",
                        "content_type",
                        "out",
                        "overwrite",
                    ],
                )
                w.writeheader()
                w.writerow(
                    {
                        "operation_id": "workers-kv-namespace-get-multiple-key-value-pairs",
                        "path_params_json": json.dumps({"account_id": "acc1", "namespace_id": "ns1"}),
                        "out": "",
                    }
                )
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(["--env-file", str(env_path), "--apply", "jobs", "run", "--file", str(jobs_csv)])
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # With out (no --yes) should execute and write file; batch changed stays false.
            out_file = root / "out" / "kv.json"
            with open(jobs_csv, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(
                    f,
                    fieldnames=[
                        "operation_id",
                        "method",
                        "path",
                        "path_params_json",
                        "query_json",
                        "body_json_file",
                        "body_bytes_file",
                        "multipart_spec_file",
                        "content_type",
                        "out",
                        "overwrite",
                    ],
                )
                w.writeheader()
                w.writerow(
                    {
                        "operation_id": "workers-kv-namespace-get-multiple-key-value-pairs",
                        "path_params_json": json.dumps({"account_id": "acc1", "namespace_id": "ns1"}),
                        "out": str(out_file),
                        "overwrite": "true",
                    }
                )
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(["--env-file", str(env_path), "--project-dir", str(root), "--apply", "jobs", "run", "--file", str(jobs_csv)])
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertFalse(payload2["changed"])
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf2.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload2, ensure_ascii=False))

    def test_jobs_refuses_unknown_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            jobs_csv = root / "jobs.csv"
            jobs_csv.write_text(
                "method,path,path_params_json\n"
                + "GET,/not/a/real/path,{}\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "jobs", "run", "--file", str(jobs_csv)])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
