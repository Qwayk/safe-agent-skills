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


class TestDnsCommands(unittest.TestCase):
    def test_dns_records_ensure_refuses_on_ambiguous_match(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and "/zones/z1/dns_records" in str(url):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj=_ok(
                        [
                            {"id": "r1", "type": "A", "name": "www.example.com", "content": "1.1.1.1"},
                            {"id": "r2", "type": "A", "name": "www.example.com", "content": "1.1.1.1"},
                        ]
                    ),
                )
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
                        "dns",
                        "records",
                        "ensure",
                        "--zone-id",
                        "z1",
                        "--name",
                        "www.example.com",
                        "--type",
                        "A",
                        "--content",
                        "1.1.1.1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_dns_records_export_requires_out_on_apply_and_is_file_only(self) -> None:
        zonefile = b"; zonefile example\nwww 60 IN A 1.1.1.1\n"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/zones/z1/dns_records/export"):
                return _DummyResponse(status=200, url=url, obj=None, body=zonefile)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            # Apply without --out should refuse safely.
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(["--env-file", str(env_path), "--apply", "dns", "records", "export", "--zone-id", "z1"])
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # Apply with --out writes file and does not print content.
            out_file = root / "out" / "zone.txt"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "dns",
                        "records",
                        "export",
                        "--zone-id",
                        "z1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertTrue(out_file.exists())
            self.assertNotIn("zonefile", buf2.getvalue())
            self.assertNotIn("www 60", buf2.getvalue())

    def test_dns_records_ensure_write_requires_apply_yes(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and "/zones/z1/dns_records" in str(url):
                return _DummyResponse(status=200, url=url, obj=_ok([]))
            raise AssertionError(f"unexpected call (should require explicit no-snapshot approval before write): {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "dns",
                        "records",
                        "ensure",
                        "--zone-id",
                        "z1",
                        "--name",
                        "www.example.com",
                        "--type",
                        "A",
                        "--content",
                        "1.1.1.1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_secondary_dns_tsig_create_requires_out_ack_yes_and_does_not_leak_secret(self) -> None:
        sentinel = "SUPERSECRET"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/secondary_dns/tsigs"):
                body = json.dumps(_ok({"id": "ts1", "tsig_secret": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_path = root / "tsig_body.json"
            body_path.write_text(json.dumps({"name": "k", "secret": "v"}, sort_keys=True), encoding="utf-8")

            # Missing --out
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "dns",
                        "secondary",
                        "account",
                        "tsigs",
                        "create",
                        "--account-id",
                        "acc1",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            out_file = root / "out" / "tsig.json"

            # Missing --ack-irreversible
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
                        "dns",
                        "secondary",
                        "account",
                        "tsigs",
                        "create",
                        "--account-id",
                        "acc1",
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

            # Missing --yes
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--ack-irreversible",
                        "dns",
                        "secondary",
                        "account",
                        "tsigs",
                        "create",
                        "--account-id",
                        "acc1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertTrue(payload3["refused"])

            # With all confirmations it still requires explicit no-snapshot approval.
            buf4 = io.StringIO()
            with redirect_stdout(buf4):
                rc4 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "dns",
                        "secondary",
                        "account",
                        "tsigs",
                        "create",
                        "--account-id",
                        "acc1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc4, 0)
            payload4 = json.loads(buf4.getvalue())
            self.assertTrue(payload4["ok"])
            self.assertTrue(payload4["refused"])
            self.assertFalse(out_file.exists())
            self.assertNotIn(sentinel, buf4.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload4, ensure_ascii=False))

    def test_secondary_zone_transfer_write_requires_apply_yes(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call (should require explicit no-snapshot approval before write): {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--apply", "dns", "secondary", "zone", "outgoing", "enable", "--zone-id", "z1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
