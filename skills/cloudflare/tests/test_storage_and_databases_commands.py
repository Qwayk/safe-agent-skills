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


def _ok(obj: Any) -> dict[str, Any]:
    return {"success": True, "errors": [], "messages": [], "result": obj}


class TestStorageAndDatabasesCommands(unittest.TestCase):
    def test_d1_databases_list_calls_expected_endpoint(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/d1/database"):
                return _DummyResponse(status=200, url=url, obj=_ok([{"uuid": "db1"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "d1", "databases", "list", "--account-id", "acc1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "d1.databases.list")
            self.assertEqual(payload["account_id"], "acc1")
            self.assertEqual(payload["count"], 1)

    def test_d1_export_requires_out_and_is_file_only(self) -> None:
        sentinel = "D1_EXPORT_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/d1/database/db1/export"):
                body = json.dumps(_ok({"sql": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(["--env-file", str(env_path), "--apply", "d1", "export", "--account-id", "acc1", "--database-id", "db1"])
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            out_file = root / "out" / "d1_export.json"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "d1",
                        "export",
                        "--account-id",
                        "acc1",
                        "--database-id",
                        "db1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["changed"])
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf2.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload2, ensure_ascii=False))

    def test_d1_query_requires_yes_and_is_file_only(self) -> None:
        sentinel = "D1_QUERY_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/d1/database/db1/query"):
                body = json.dumps(_ok({"rows": [{"v": sentinel}]}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_path = root / "body.json"
            body_path.write_text(json.dumps({"sql": "select 1"}, sort_keys=True), encoding="utf-8")

            out_file = root / "out" / "d1_query.json"

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "d1",
                        "query",
                        "--account-id",
                        "acc1",
                        "--database-id",
                        "db1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "d1",
                        "query",
                        "--account-id",
                        "acc1",
                        "--database-id",
                        "db1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertFalse(out_file.exists())
            self.assertNotIn(sentinel, buf2.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload2, ensure_ascii=False))

    def test_queues_pull_requires_out_and_is_file_only(self) -> None:
        sentinel = "QUEUE_PULL_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/queues/q1/messages/pull"):
                body = json.dumps(_ok({"messages": [{"body": sentinel}]}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(["--env-file", str(env_path), "--apply", "queues", "pull", "--account-id", "acc1", "--queue-id", "q1"])
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            out_file = root / "out" / "queues_pull.json"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "queues",
                        "pull",
                        "--account-id",
                        "acc1",
                        "--queue-id",
                        "q1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["changed"])
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf2.getvalue())

    def test_r2_temp_creds_create_requires_ack_and_yes_and_is_file_only(self) -> None:
        sentinel = "R2_SECRET_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/r2/temp-access-credentials"):
                body = json.dumps(_ok({"secretAccessKey": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            out_file = root / "out" / "temp_creds.json"

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "r2",
                        "temp-creds",
                        "create",
                        "--account-id",
                        "acc1",
                        "--bucket",
                        "b1",
                        "--permission",
                        "read",
                        "--ttl-seconds",
                        "60",
                        "--parent-access-key-id",
                        "p1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--ack-irreversible",
                        "r2",
                        "temp-creds",
                        "create",
                        "--account-id",
                        "acc1",
                        "--bucket",
                        "b1",
                        "--permission",
                        "read",
                        "--ttl-seconds",
                        "60",
                        "--parent-access-key-id",
                        "p1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "r2",
                        "temp-creds",
                        "create",
                        "--account-id",
                        "acc1",
                        "--bucket",
                        "b1",
                        "--permission",
                        "read",
                        "--ttl-seconds",
                        "60",
                        "--parent-access-key-id",
                        "p1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertTrue(payload3["refused"])
            self.assertFalse(out_file.exists())
            self.assertNotIn(sentinel, buf3.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload3, ensure_ascii=False))
