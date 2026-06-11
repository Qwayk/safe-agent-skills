from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cloudflare_api_tool.cli import main


class _DummyResponse:
    def __init__(self, *, status: int, url: str, obj: object | None):
        self.status_code = int(status)
        self.url = str(url)
        self.headers: dict[str, str] = {"Content-Type": "application/json"}
        self.content = (json.dumps(obj, ensure_ascii=False) if obj is not None else "").encode("utf-8")


def _ok(result: object, *, result_info: dict | None = None) -> dict:
    out: dict = {"success": True, "errors": [], "messages": [], "result": result}
    if result_info is not None:
        out["result_info"] = result_info
    return out


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


class TestAccountAccessCommands(unittest.TestCase):
    def test_roles_list_happy_path(self) -> None:
        tc = self

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/roles"):
                params = kwargs.get("params") or {}
                tc.assertEqual(params.get("page"), 1)
                tc.assertEqual(params.get("per_page"), 50)
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj=_ok(
                        [{"id": "r1", "name": "Role 1"}],
                        result_info={"total_pages": 1},
                    ),
                )
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "accounts",
                        "roles",
                        "list",
                        "--account-id",
                        "acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "accounts.roles.list")
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["result"][0]["id"], "r1")

    def test_roles_get_happy_path(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/roles/r1"):
                return _DummyResponse(status=200, url=url, obj=_ok({"id": "r1", "name": "Role 1"}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "accounts",
                        "roles",
                        "get",
                        "--account-id",
                        "acc1",
                        "--role-id",
                        "r1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "accounts.roles.get")
            self.assertEqual(payload["account_id"], "acc1")
            self.assertEqual(payload["role_id"], "r1")
            self.assertEqual(payload["result"]["id"], "r1")

    def test_members_list_dry_run_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "accounts",
                        "members",
                        "list",
                        "--account-id",
                        "acc1",
                        "--out",
                        "members.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

    def test_members_list_apply_writes_file_and_never_prints_emails(self) -> None:
        fake_email = "alice@example.com"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/members"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj=_ok(
                        [
                            {"id": "m1", "email": fake_email, "roles": [{"id": "r1"}], "status": "accepted"},
                        ],
                        result_info={"total_pages": 1},
                    ),
                )
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            out_file = project_dir / "members.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "accounts",
                        "members",
                        "list",
                        "--account-id",
                        "acc1",
                        "--out",
                        "members.json",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn(fake_email, out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertTrue(out_file.exists())
            self.assertIn(fake_email, out_file.read_text(encoding="utf-8"))

    def test_members_get_apply_writes_file_and_never_prints_emails(self) -> None:
        fake_email = "alice@example.com"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/members/m1"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj=_ok(
                        {"id": "m1", "email": fake_email, "roles": [{"id": "r1"}], "status": "accepted"},
                    ),
                )
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            out_file = project_dir / "member.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "accounts",
                        "members",
                        "get",
                        "--account-id",
                        "acc1",
                        "--member-id",
                        "m1",
                        "--out",
                        "member.json",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn(fake_email, out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertTrue(out_file.exists())
            self.assertIn(fake_email, out_file.read_text(encoding="utf-8"))

    def test_members_add_dry_run_redacts_email_in_stdout(self) -> None:
        email = "alice@example.com"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "accounts",
                        "members",
                        "add",
                        "--account-id",
                        "acc1",
                        "--email",
                        email,
                        "--role-id",
                        "r1",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn(email, out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

    def test_members_add_apply_requires_yes_and_never_prints_email(self) -> None:
        email = "alice@example.com"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "accounts",
                        "members",
                        "add",
                        "--account-id",
                        "acc1",
                        "--email",
                        email,
                        "--role-id",
                        "r1",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn(email, out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_members_add_apply_happy_path_never_prints_email(self) -> None:
        email = "alice@example.com"
        tc = self

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/members"):
                body = kwargs.get("json") or {}
                tc.assertEqual(body.get("email"), email)
                tc.assertEqual(body.get("roles"), ["r1"])
                return _DummyResponse(status=200, url=url, obj=_ok({"id": "m1", "email": email}))
            if method == "GET" and str(url).endswith("/accounts/acc1/members/m1"):
                return _DummyResponse(status=200, url=url, obj=_ok({"id": "m1", "email": email, "roles": [{"id": "r1"}], "status": "accepted"}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "--yes",
                        "accounts",
                        "members",
                        "add",
                        "--account-id",
                        "acc1",
                        "--email",
                        email,
                        "--role-id",
                        "r1",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn(email, out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_members_update_apply_requires_yes(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "accounts",
                        "members",
                        "update",
                        "--account-id",
                        "acc1",
                        "--member-id",
                        "m1",
                        "--role-id",
                        "r1",
                        "--status",
                        "accepted",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_members_update_apply_happy_path_never_prints_email(self) -> None:
        fake_email = "alice@example.com"
        tc = self

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/roles/r1"):
                return _DummyResponse(status=200, url=url, obj=_ok({"id": "r1", "name": "Role 1"}))
            if method == "PUT" and str(url).endswith("/accounts/acc1/members/m1"):
                body = kwargs.get("json") or {}
                tc.assertIn("roles", body)
                tc.assertIsInstance(body.get("roles"), list)
                tc.assertEqual(body["roles"][0]["id"], "r1")
                tc.assertEqual(body.get("status"), "accepted")
                return _DummyResponse(status=200, url=url, obj=_ok({"id": "m1"}))
            if method == "GET" and str(url).endswith("/accounts/acc1/members/m1"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj=_ok({"id": "m1", "email": fake_email, "roles": [{"id": "r1"}], "status": "accepted"}),
                )
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "--yes",
                        "accounts",
                        "members",
                        "update",
                        "--account-id",
                        "acc1",
                        "--member-id",
                        "m1",
                        "--role-id",
                        "r1",
                        "--status",
                        "accepted",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn(fake_email, out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_members_remove_apply_requires_yes(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "accounts",
                        "members",
                        "remove",
                        "--account-id",
                        "acc1",
                        "--member-id",
                        "m1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_members_remove_apply_happy_path_verifies_absent_and_never_prints_email(self) -> None:
        fake_email = "alice@example.com"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "DELETE" and str(url).endswith("/accounts/acc1/members/m1"):
                return _DummyResponse(status=200, url=url, obj=_ok({}))
            if method == "GET" and str(url).endswith("/accounts/acc1/members/m1"):
                # Include a fake email in the body to prove stdout doesn't leak it.
                return _DummyResponse(
                    status=404,
                    url=url,
                    obj={"success": False, "errors": [{"message": "not found"}], "messages": [], "result": {"email": fake_email}},
                )
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "--yes",
                        "accounts",
                        "members",
                        "remove",
                        "--account-id",
                        "acc1",
                        "--member-id",
                        "m1",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn(fake_email, out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
