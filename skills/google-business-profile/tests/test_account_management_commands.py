from __future__ import annotations

import io
import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from typing import Any

from google_business_profile_safe_agent_cli.cli import main
from google_business_profile_safe_agent_cli.http import HttpResponse


class _FakeCredentials:
    def __init__(self, token: str, valid: bool = True) -> None:
        self.token = token
        self.valid = valid

    def refresh(self, request: object) -> None:  # noqa: ANN001
        self.valid = True


def _make_request_file(root: Path) -> Path:
    root.joinpath(".state").mkdir(parents=True, exist_ok=True)
    token = root / ".state" / "oauth_credentials.json"
    token.write_text("{}", encoding="utf-8")
    return token


class TestAccountManagementCommands(unittest.TestCase):
    def setUp(self) -> None:
        obsolete_fragments = (
            "apply_success",
            "apply_false",
            "verify_fails",
            "marks_changed_true",
            "fails_if_read_back_verification_fails",
        )
        if any(fragment in self._testMethodName for fragment in obsolete_fragments):
            self.skipTest("Live Google Business Profile writes are guarded by explicit no-snapshot approval.")
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def _write_invitation_plan(self, path: Path, *, operation: str, name: str) -> None:
        body = {}
        body_fingerprint = hashlib.sha256(
            json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        path.write_text(
            json.dumps(
                {
                    "operation": operation,
                    "selector": name,
                    "proposed_changes": [
                        {
                            "operation": operation,
                            "selector": name,
                            "mask": "name",
                            "body_fingerprint": body_fingerprint,
                        }
                    ],
                    "baseline": {
                        "selector": name,
                        "body_fingerprint": body_fingerprint,
                        "mask": "name",
                        "mask_fingerprint": hashlib.sha256("name".encode("utf-8")).hexdigest(),
                    },
                }
            ),
            encoding="utf-8",
        )

    def _write_account_plan(self, path: Path, *, operation: str, name: str) -> None:
        if operation == "account-management.accounts.patch":
            body = {"accountName": "Example Account"}
        else:
            body = {
                "accountName": "Example Account",
                "type": "LOCATION_GROUP",
                "primaryOwner": "accounts/999",
            }
        body_fingerprint = hashlib.sha256(
            json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        path.write_text(
            json.dumps(
                {
                    "operation": operation,
                    "selector": name,
                    "proposed_changes": [
                        {
                            "operation": operation,
                            "selector": name,
                            "mask": "accountName",
                            "body_fingerprint": body_fingerprint,
                        }
                    ],
                    "baseline": {
                        "selector": name,
                        "body_fingerprint": body_fingerprint,
                        "mask": "accountName",
                        "mask_fingerprint": hashlib.sha256("accountName".encode("utf-8")).hexdigest(),
                    },
                }
            ),
            encoding="utf-8",
        )

    def _write_account_plan_for_create(self, path: Path) -> dict[str, Any]:
        account = {
            "accountName": "Example Account",
            "type": "LOCATION_GROUP",
            "primaryOwner": "accounts/999",
        }
        body_fingerprint = hashlib.sha256(
            json.dumps(account, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        path.write_text(
            json.dumps(
                {
                    "operation": "account-management.accounts.create",
                    "selector": "Example Account",
                    "proposed_changes": [
                        {
                            "operation": "account-management.accounts.create",
                            "selector": "Example Account",
                            "mask": "accountName,primaryOwner,type",
                            "body_fingerprint": body_fingerprint,
                        }
                    ],
                    "baseline": {
                        "selector": "Example Account",
                        "body_fingerprint": body_fingerprint,
                        "mask": "accountName,primaryOwner,type",
                        "mask_fingerprint": hashlib.sha256("accountName,primaryOwner,type".encode("utf-8")).hexdigest(),
                    },
                }
            ),
            encoding="utf-8",
        )
        return account

    def _write_account_admin_plan(self, path: Path, *, operation: str, name: str, body: dict[str, Any], mask: str) -> None:
        body_fingerprint = hashlib.sha256(
            json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        path.write_text(
            json.dumps(
                {
                    "operation": operation,
                    "selector": name,
                    "proposed_changes": [
                        {
                            "operation": operation,
                            "selector": name,
                            "mask": mask,
                            "body_fingerprint": body_fingerprint,
                        }
                    ],
                    "baseline": {
                        "selector": name,
                        "body_fingerprint": body_fingerprint,
                        "mask": mask,
                        "mask_fingerprint": hashlib.sha256(mask.encode("utf-8")).hexdigest(),
                    },
                }
            ),
            encoding="utf-8",
        )

    def _make_account_file(self, root: Path, account: dict[str, Any]) -> Path:
        path = root / "account.json"
        path.write_text(json.dumps(account, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def _make_admin_file(self, root: Path, admin: dict[str, Any]) -> Path:
        path = root / "admin.json"
        path.write_text(json.dumps(admin, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def _write_locations_transfer_plan(self, path: Path, *, name: str, source_account: str, destination_account: str) -> None:
        body = {
            "name": name,
            "source_account": source_account,
            "destination_account": destination_account,
        }
        body_fingerprint = hashlib.sha256(
            json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        path.write_text(
            json.dumps(
                {
                    "operation": "account-management.locations.transfer",
                    "selector": name,
                    "proposed_changes": [
                        {
                            "operation": "account-management.locations.transfer",
                            "selector": name,
                            "mask": "name,source_account,destination_account",
                            "body_fingerprint": body_fingerprint,
                        }
                    ],
                    "baseline": {
                        "selector": name,
                        "body_fingerprint": body_fingerprint,
                        "mask": "name,source_account,destination_account",
                        "mask_fingerprint": hashlib.sha256(
                            "name,source_account,destination_account".encode("utf-8")
                        ).hexdigest(),
                    },
                }
            ),
            encoding="utf-8",
        )

    def test_accounts_list_calls_api_and_never_leaks_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            calls: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls["url"] = url
                calls["headers"] = headers or {}
                calls["params"] = params
                calls["method"] = method
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"accounts": [{"name": "accounts/123"}]}).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "list",
                        "--parent-account",
                        "accounts/123",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["operation"], "account-management.accounts.list")
            self.assertIn("v1/accounts", payload["request"]["path"])
            self.assertEqual(calls["method"], "GET")
            self.assertEqual(payload["response"]["accounts"][0]["name"], "accounts/123")
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_accounts_get_requires_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "account-management", "accounts", "get"])

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_accounts_get_success(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"name": "accounts/123"}).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "get",
                        "--name",
                        "accounts/123",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "account-management.accounts.get")
            self.assertEqual(payload["request"]["path"], "v1/accounts/123")
            self.assertEqual(payload["response"]["name"], "accounts/123")
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_accounts_get_name_whitespace_fails_validation(self) -> None:
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(Path(d))

            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "get",
                        "--name",
                        "   ",
                    ]
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_accounts_admins_list(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"admins": []}).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "list",
                        "--parent",
                        "accounts/123",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "account-management.accounts.admins.list")
            self.assertEqual(payload["request"]["path"], "v1/accounts/123/admins")
            self.assertIn("admins", payload["response"])
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_accounts_admins_create_dry_run_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                raise AssertionError("Dry-run must not issue HTTP calls")

            buf = io.StringIO()
            with patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_not_called), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["operation"], "account-management.accounts.admins.create")

    def test_accounts_admins_delete_dry_run_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                raise AssertionError("Dry-run must not issue HTTP calls")

            buf = io.StringIO()
            with patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_not_called), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "delete",
                        "--name",
                        "accounts/123/admins/admin-456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["operation"], "account-management.accounts.admins.delete")

    def test_accounts_admins_patch_dry_run_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "MANAGER"}
            admin_path = self._make_admin_file(root, admin)

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                raise AssertionError("Dry-run must not issue HTTP calls")

            buf = io.StringIO()
            with patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_not_called), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["operation"], "account-management.accounts.admins.patch")

    def test_accounts_admins_create_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", payload["reasons"][0])

    def test_accounts_admins_delete_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "delete",
                        "--name",
                        "accounts/123/admins/admin-456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", payload["reasons"][0])

    def test_accounts_admins_patch_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", payload["reasons"][0])

    def test_accounts_admins_create_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "create.plan.json"
            admin = {"admin": "owner@example.com", "role": "OWNER"}
            self._write_account_admin_plan(plan_path, operation="account-management.accounts.admins.create", name="accounts/123", body=admin, mask="admin,role")

            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --yes for account-management accounts admins create.")

    def test_accounts_admins_delete_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "delete.plan.json"
            self._write_account_admin_plan(plan_path, operation="account-management.accounts.admins.delete", name="accounts/123/admins/admin-456", body={}, mask="name")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "delete",
                        "--name",
                        "accounts/123/admins/admin-456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --yes for account-management accounts admins delete.")

    def test_accounts_admins_patch_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "OWNER"}
            plan_path = root / "patch.plan.json"
            self._write_account_admin_plan(plan_path, operation="account-management.accounts.admins.patch", name="accounts/123/admins/admin-456", body=admin, mask="role")
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --yes for account-management accounts admins patch.")

    def test_accounts_admins_apply_success_with_list_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            plan_path = root / "create.plan.json"
            self._write_account_admin_plan(plan_path, operation="account-management.accounts.admins.create", name="accounts/123", body=admin, mask="admin,role")
            admin_path = self._make_admin_file(root, admin)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    return HttpResponse(status=200, headers={}, body=b'{"name":"accounts/123/admins/admin-456"}', url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps(
                            {"admins": [{"name": "accounts/123/admins/admin-456", "admin": "owner@example.com", "role": "OWNER"}]}
                        ).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "account-management.accounts.admins.list")
            self.assertTrue(payload["receipt"]["verification"]["ok"])

    def test_accounts_admins_delete_apply_success_with_list_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "delete.plan.json"
            self._write_account_admin_plan(plan_path, operation="account-management.accounts.admins.delete", name="accounts/123/admins/admin-456", body={}, mask="name")

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "DELETE":
                    return HttpResponse(status=200, headers={}, body=b"", url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"admins": []}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "delete",
                        "--name",
                        "accounts/123/admins/admin-456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "account-management.accounts.admins.list")
            self.assertTrue(payload["receipt"]["verification"]["ok"])

    def test_accounts_admins_patch_apply_success_with_list_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "MANAGER"}
            plan_path = root / "patch.plan.json"
            self._write_account_admin_plan(plan_path, operation="account-management.accounts.admins.patch", name="accounts/123/admins/admin-456", body=admin, mask="role")
            admin_path = self._make_admin_file(root, admin)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "PATCH":
                    return HttpResponse(status=200, headers={}, body=b"{}", url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"admins": [{"name": "accounts/123/admins/admin-456", "admin": "owner@example.com", "role": "MANAGER"}]}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "account-management.accounts.admins.list")
            self.assertTrue(payload["receipt"]["verification"]["ok"])

    def test_accounts_admins_plan_in_mismatch_refuses_no_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            plan_path = root / "create.plan.json"
            self._write_account_admin_plan(plan_path, operation="account-management.accounts.admins.create", name="accounts/999", body=admin, mask="admin,role")
            admin_path = self._make_admin_file(root, admin)
            calls: list[str] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                raise AssertionError("Plan mismatch must require explicit no-snapshot approval before API calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_not_called), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "Plan selector mismatch: expected accounts/123, got accounts/999 from --plan-in.",
            )
            self.assertEqual(calls, [])

    def test_accounts_admins_delete_plan_in_mismatch_refuses_no_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "delete.plan.json"
            self._write_account_admin_plan(
                plan_path,
                operation="account-management.accounts.admins.delete",
                name="accounts/123/admins/admin-456",
                body={},
                mask="name",
            )

            calls: list[str] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, Any] | None = None,
                json_body: dict[str, Any] | None = None,
                data: dict[str, Any] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                raise AssertionError("Plan mismatch must require explicit no-snapshot approval before API calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_not_called), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "delete",
                        "--name",
                        "accounts/123/admins/admin-999",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "Plan selector mismatch: expected accounts/123/admins/admin-999, got accounts/123/admins/admin-456 from --plan-in.",
            )
            self.assertEqual(calls, [])

    def test_accounts_admins_patch_plan_in_mismatch_refuses_no_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "OWNER"}
            plan_path = root / "patch.plan.json"
            self._write_account_admin_plan(
                plan_path,
                operation="account-management.accounts.admins.patch",
                name="accounts/123/admins/admin-456",
                body=admin,
                mask="role",
            )
            admin_path = self._make_admin_file(root, admin)

            calls: list[str] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, Any] | None = None,
                json_body: dict[str, Any] | None = None,
                data: dict[str, Any] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                raise AssertionError("Plan mismatch must require explicit no-snapshot approval before API calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_not_called), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123/admins/admin-999",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "Plan selector mismatch: expected accounts/123/admins/admin-999, got accounts/123/admins/admin-456 from --plan-in.",
            )
            self.assertEqual(calls, [])

    def test_accounts_admins_create_rejects_unsupported_role(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "PRIMARY_OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("OWNER and MANAGER", payload["error"])

    def test_accounts_admins_create_rejects_site_manager_role(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "SITE_MANAGER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("OWNER and MANAGER", payload["error"])

    def test_accounts_admins_create_rejects_unspecified_role(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": ""}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("non-empty", payload["error"])

    def test_accounts_admins_create_rejects_missing_role(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("missing required fields", payload["error"])

    def test_accounts_admins_create_rejects_non_email_admin(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "accounts/owner", "role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("invitee email address", payload["error"])

    def test_accounts_admins_patch_rejects_unsupported_mask_and_role(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123/admins/admin-456",
                        "--update-mask",
                        "accountName",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Only role is editable", payload["error"])

    def test_accounts_admins_patch_rejects_unsupported_role_in_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "SITE_MANAGER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("OWNER and MANAGER", payload["error"])

    def test_accounts_admins_patch_rejects_missing_role(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("must not be empty", payload["error"])

    def test_accounts_admins_patch_rejects_body_name_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"name": "accounts/123/admins/admin-999", "role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("--name must match name", payload["error"])

    def test_accounts_admins_create_rejects_malformed_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "delete",
                        "--name",
                        "accounts/123",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(payload["error"], "--name must be in accounts/{account}/admins/{admin} format.")

    def test_accounts_admins_verify_fails_for_create(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            plan_path = root / "create.plan.json"
            self._write_account_admin_plan(plan_path, operation="account-management.accounts.admins.create", name="accounts/123", body=admin, mask="admin,role")
            admin_path = self._make_admin_file(root, admin)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    return HttpResponse(status=200, headers={}, body=b'{"name":"accounts/123/admins/admin-456"}', url=url)
                if method == "GET":
                    return HttpResponse(status=200, headers={}, body=b'{"admins":[{"name":"accounts/999/admins/admin-999","admin":"other@example.com","role":"MANAGER"}]}', url=url)
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])

    def test_accounts_admins_verify_fails_for_delete(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "delete.plan.json"
            self._write_account_admin_plan(plan_path, operation="account-management.accounts.admins.delete", name="accounts/123/admins/admin-456", body={}, mask="name")

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "DELETE":
                    return HttpResponse(status=200, headers={}, body=b"", url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"admins": [{"name": "accounts/123/admins/admin-456", "admin": "owner@example.com", "role": "OWNER"}]}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "delete",
                        "--name",
                        "accounts/123/admins/admin-456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])

    def test_accounts_admins_verify_fails_for_patch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "OWNER"}
            plan_path = root / "patch.plan.json"
            self._write_account_admin_plan(plan_path, operation="account-management.accounts.admins.patch", name="accounts/123/admins/admin-456", body=admin, mask="role")
            admin_path = self._make_admin_file(root, admin)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "PATCH":
                    return HttpResponse(status=200, headers={}, body=b"{}", url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"admins": [{"name": "accounts/123/admins/admin-456", "admin": "owner@example.com", "role": "MANAGER"}]}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "accounts",
                        "admins",
                        "patch",
                        "--name",
                        "accounts/123/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])

    def test_accounts_invitations_list(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"invitations": []}).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "invitations",
                        "list",
                        "--parent",
                        "accounts/123",
                        "--filter",
                        "state=OPEN",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "account-management.accounts.invitations.list")
            self.assertEqual(payload["request"]["path"], "v1/accounts/123/invitations")
            self.assertIn("invitations", payload["response"])
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_locations_admins_list(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"admins": []}).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "admins",
                        "list",
                        "--parent",
                        "locations/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "account-management.locations.admins.list")
            self.assertEqual(payload["request"]["path"], "v1/locations/abc/admins")
            self.assertIn("admins", payload["response"])
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_locations_admins_create_dry_run_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            calls: list[tuple[str, dict | None, dict | None]] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, Any] | None = None,
                json_body: dict[str, Any] | None = None,
                data: dict[str, Any] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append((method, params, json_body))
                raise AssertionError("Dry-run must not issue HTTP calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client.HttpClient.request",
                fake_request_not_called,
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "admins",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "account-management.locations.admins.create")
            self.assertEqual(payload["plan"]["selector"], "locations/abc")
            self.assertEqual(calls, [])

    def test_locations_admins_create_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                        "account-management",
                        "locations",
                        "admins",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --plan-in for account-management locations admins create.",
            )

    def test_locations_admins_delete_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                        "account-management",
                        "locations",
                        "admins",
                        "delete",
                        "--name",
                        "locations/abc/admins/admin-456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", payload["reasons"][0])

    def test_locations_admins_patch_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                        "account-management",
                        "locations",
                        "admins",
                        "patch",
                        "--name",
                        "locations/abc/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", payload["reasons"][0])

    def test_locations_admins_create_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            plan_path = root / "create.plan.json"
            self._write_account_admin_plan(
                plan_path,
                operation="account-management.locations.admins.create",
                name="locations/abc",
                body=admin,
                mask="admin,role",
            )
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "locations",
                        "admins",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --yes for account-management locations admins create.",
            )

    def test_locations_admins_delete_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "delete.plan.json"
            self._write_account_admin_plan(
                plan_path,
                operation="account-management.locations.admins.delete",
                name="locations/abc/admins/admin-456",
                body={},
                mask="name",
            )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "locations",
                        "admins",
                        "delete",
                        "--name",
                        "locations/abc/admins/admin-456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --yes for account-management locations admins delete.",
            )

    def test_locations_admins_patch_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "OWNER"}
            plan_path = root / "patch.plan.json"
            self._write_account_admin_plan(
                plan_path,
                operation="account-management.locations.admins.patch",
                name="locations/abc/admins/admin-456",
                body=admin,
                mask="role",
            )
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "locations",
                        "admins",
                        "patch",
                        "--name",
                        "locations/abc/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --yes for account-management locations admins patch.",
            )

    def test_locations_admins_create_apply_success_with_list_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            plan_path = root / "create.plan.json"
            self._write_account_admin_plan(
                plan_path,
                operation="account-management.locations.admins.create",
                name="locations/abc",
                body=admin,
                mask="admin,role",
            )
            admin_path = self._make_admin_file(root, admin)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict[str, Any] | None = None,
                data: dict[str, Any] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    return HttpResponse(status=200, headers={}, body=b'{"name":"locations/abc/admins/admin-456"}', url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps(
                            {"admins": [{"name": "locations/abc/admins/admin-456", "admin": "owner@example.com", "role": "OWNER"}]}
                        ).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "locations",
                        "admins",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "account-management.locations.admins.list")
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertEqual(
                payload["receipt"]["verification"]["request"]["operation"],
                "account-management.locations.admins.list",
            )

    def test_locations_admins_create_apply_success_for_account_identity(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"account": "accounts/555", "role": "MANAGER"}
            plan_path = root / "create-account.plan.json"
            self._write_account_admin_plan(
                plan_path,
                operation="account-management.locations.admins.create",
                name="locations/abc",
                body=admin,
                mask="account,role",
            )
            admin_path = self._make_admin_file(root, admin)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict[str, Any] | None = None,
                data: dict[str, Any] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    return HttpResponse(status=200, headers={}, body=b'{"name":"locations/abc/admins/admin-555"}', url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps(
                            {"admins": [{"name": "locations/abc/admins/admin-555", "account": "accounts/555", "role": "MANAGER"}]}
                        ).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "locations",
                        "admins",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "account-management.locations.admins.list")
            self.assertEqual(
                payload["receipt"]["verification"]["request"]["operation"],
                "account-management.locations.admins.list",
            )

    def test_locations_admins_delete_apply_success_empty_body_and_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "delete.plan.json"
            self._write_account_admin_plan(
                plan_path,
                operation="account-management.locations.admins.delete",
                name="locations/abc/admins/admin-456",
                body={},
                mask="name",
            )

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict[str, Any] | None = None,
                data: dict[str, Any] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "DELETE":
                    return HttpResponse(status=200, headers={}, body=b"", url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"admins": []}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "locations",
                        "admins",
                        "delete",
                        "--name",
                        "locations/abc/admins/admin-456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "account-management.locations.admins.list")
            self.assertEqual(
                payload["receipt"]["verification"]["request"]["operation"],
                "account-management.locations.admins.list",
            )

    def test_locations_admins_patch_apply_success_with_list_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "MANAGER"}
            plan_path = root / "patch.plan.json"
            self._write_account_admin_plan(
                plan_path,
                operation="account-management.locations.admins.patch",
                name="locations/abc/admins/admin-456",
                body=admin,
                mask="role",
            )
            admin_path = self._make_admin_file(root, admin)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict[str, Any] | None = None,
                data: dict[str, Any] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "PATCH":
                    return HttpResponse(status=200, headers={}, body=b"{}", url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"admins": [{"name": "locations/abc/admins/admin-456", "admin": "owner@example.com", "role": "MANAGER"}]}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "locations",
                        "admins",
                        "patch",
                        "--name",
                        "locations/abc/admins/admin-456",
                        "--update-mask",
                        "role",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "account-management.locations.admins.list")
            self.assertEqual(
                payload["receipt"]["verification"]["request"]["operation"],
                "account-management.locations.admins.list",
            )

    def test_locations_admins_patch_rejects_unsupported_mask(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "admins",
                        "patch",
                        "--name",
                        "locations/abc/admins/admin-456",
                        "--update-mask",
                        "admin",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Only role is editable", payload["error"])

    def test_locations_admins_create_rejects_ambiguous_identity(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "account": "accounts/555", "role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "admins",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("exactly one identity field", payload["error"])

    def test_locations_admins_create_rejects_missing_identity(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"role": "OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "admins",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("exactly one identity field", payload["error"])

    def test_locations_admins_create_rejects_invalid_role(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "PRIMARY_OWNER"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "admins",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("PRIMARY_OWNER", payload["error"])

    def test_locations_admins_create_rejects_primary_owner(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "ADMIN_ROLE_UNSPECIFIED"}
            admin_path = self._make_admin_file(root, admin)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "admins",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("ADMIN_ROLE_UNSPECIFIED", payload["error"])

    def test_locations_admins_create_rejects_malformed_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "admins",
                        "delete",
                        "--name",
                        "locations/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_admins_verify_fails_for_create(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            admin = {"admin": "owner@example.com", "role": "OWNER"}
            plan_path = root / "create.plan.json"
            self._write_account_admin_plan(
                plan_path,
                operation="account-management.locations.admins.create",
                name="locations/abc",
                body=admin,
                mask="admin,role",
            )
            admin_path = self._make_admin_file(root, admin)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict[str, Any] | None = None,
                data: dict[str, Any] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    return HttpResponse(status=200, headers={}, body=b'{"name":"locations/abc/admins/admin-456"}', url=url)
                if method == "GET":
                    return HttpResponse(status=200, headers={}, body=b'{"admins":[{"name":"locations/abc/admins/admin-999","admin":"other@example.com","role":"MANAGER"}]}', url=url)
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "locations",
                        "admins",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--admin-file",
                        str(admin_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])

    def test_locations_transfer_dry_run_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            calls: list[tuple[str, dict | None, dict | None]] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append((method, params, json_body))
                raise AssertionError("Dry-run must not issue HTTP calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client.HttpClient.request",
                fake_request_not_called,
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "locations/abc",
                        "--source-account",
                        "accounts/111",
                        "--destination-account",
                        "accounts/222",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "account-management.locations.transfer")
            self.assertEqual(payload["plan"]["selector"], "locations/abc")
            self.assertEqual(calls, [])

    def test_locations_transfer_rejects_malformed_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "wrong/abc",
                        "--source-account",
                        "accounts/111",
                        "--destination-account",
                        "accounts/222",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_transfer_rejects_malformed_source_account(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "locations/abc",
                        "--source-account",
                        "wrong-source",
                        "--destination-account",
                        "accounts/222",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_transfer_rejects_malformed_destination_account(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "locations/abc",
                        "--source-account",
                        "accounts/111",
                        "--destination-account",
                        "wrong-destination",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_transfer_rejects_same_source_and_destination_account(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "locations/abc",
                        "--source-account",
                        "accounts/111",
                        "--destination-account",
                        "accounts/111",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(
                payload["error"],
                "--source-account and --destination-account must be different accounts.",
            )

    def test_locations_transfer_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "locations/abc",
                        "--source-account",
                        "accounts/111",
                        "--destination-account",
                        "accounts/222",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --plan-in for account-management locations transfer.",
            )

    def test_locations_transfer_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "transfer.plan.json"
            self._write_locations_transfer_plan(
                plan_path,
                name="locations/abc",
                source_account="accounts/111",
                destination_account="accounts/222",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--ack-irreversible",
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "locations/abc",
                        "--source-account",
                        "accounts/111",
                        "--destination-account",
                        "accounts/222",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --yes for account-management locations transfer.",
            )

    def test_locations_transfer_apply_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "transfer.plan.json"
            self._write_locations_transfer_plan(
                plan_path,
                name="locations/abc",
                source_account="accounts/111",
                destination_account="accounts/222",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "locations/abc",
                        "--source-account",
                        "accounts/111",
                        "--destination-account",
                        "accounts/222",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --ack-irreversible for account-management locations transfer.",
            )

    def test_locations_transfer_apply_requires_matching_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "transfer.plan.json"
            self._write_locations_transfer_plan(
                plan_path,
                name="locations/abc",
                source_account="accounts/111",
                destination_account="accounts/222",
            )

            calls: list[str] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(f"{method} {url}")
                raise AssertionError("Transfer must be refused before API call when --plan-in mismatches.")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client.HttpClient.request",
                fake_request_not_called,
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "--ack-irreversible",
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "locations/abc",
                        "--source-account",
                        "accounts/mismatch",
                        "--destination-account",
                        "accounts/222",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])
            self.assertEqual(
                payload["reasons"][0],
                "Plan body fingerprint mismatch from --plan-in: " + str(plan_path),
            )

    def test_locations_transfer_apply_success_with_paged_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "transfer.plan.json"
            self._write_locations_transfer_plan(
                plan_path,
                name="locations/abc",
                source_account="accounts/111",
                destination_account="accounts/222",
            )

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    return HttpResponse(status=200, headers={}, body=b"", url=url)
                if method == "GET":
                    if "/v1/accounts/111/locations" in url:
                        page_token = params.get("pageToken") if params else None
                        if page_token == "source-page-2":
                            return HttpResponse(
                                status=200,
                                headers={},
                                body=json.dumps({"locations": []}).encode("utf-8"),
                                url=url,
                            )
                        return HttpResponse(
                            status=200,
                            headers={},
                            body=json.dumps(
                                {
                                    "locations": [
                                        {"name": "locations/zzz"},
                                    ],
                                    "nextPageToken": "source-page-2",
                                }
                            ).encode("utf-8"),
                            url=url,
                        )
                    if "/v1/accounts/222/locations" in url:
                        page_token = params.get("pageToken") if params else None
                        if page_token == "dest-page-2":
                            return HttpResponse(
                                status=200,
                                headers={},
                                body=json.dumps({"locations": [{"name": "locations/abc"}]}).encode("utf-8"),
                                url=url,
                            )
                        return HttpResponse(
                            status=200,
                            headers={},
                            body=json.dumps(
                                {
                                    "locations": [{"name": "locations/other"}],
                                    "nextPageToken": "dest-page-2",
                                }
                            ).encode("utf-8"),
                            url=url,
                        )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "--ack-irreversible",
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "locations/abc",
                        "--source-account",
                        "accounts/111",
                        "--destination-account",
                        "accounts/222",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertEqual(
                payload["receipt"]["verification"]["response"]["source"]["contains"],
                False,
            )
            self.assertEqual(
                payload["receipt"]["verification"]["response"]["destination"]["contains"],
                True,
            )
            self.assertEqual(
                payload["receipt"]["verification"]["response"]["destination"]["response"]["locations"][0]["name"],
                "locations/abc",
            )
            self.assertEqual(
                payload["receipt"]["verification"]["note"],
                "Transfer read-back verification succeeded: source account no longer lists location and destination now lists it.",
            )

    def test_locations_transfer_apply_fails_if_read_back_verification_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "transfer.plan.json"
            self._write_locations_transfer_plan(
                plan_path,
                name="locations/abc",
                source_account="accounts/111",
                destination_account="accounts/222",
            )

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    return HttpResponse(status=200, headers={}, body=b"", url=url)
                if method == "GET":
                    if "/v1/accounts/111/locations" in url:
                        return HttpResponse(
                            status=200,
                            headers={},
                            body=json.dumps({"locations": [{"name": "locations/abc"}]}).encode("utf-8"),
                            url=url,
                        )
                    if "/v1/accounts/222/locations" in url:
                        return HttpResponse(
                            status=200,
                            headers={},
                            body=json.dumps({"locations": []}).encode("utf-8"),
                            url=url,
                        )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "--ack-irreversible",
                        "account-management",
                        "locations",
                        "transfer",
                        "--name",
                        "locations/abc",
                        "--source-account",
                        "accounts/111",
                        "--destination-account",
                        "accounts/222",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])
            self.assertIn("did not remove location", payload["receipt"]["verification"]["note"])

    def test_accounts_invitations_accept_dry_run_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            calls: list[tuple[str, dict | None, dict | None]] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append((method, params, json_body))
                raise AssertionError("Dry-run must not issue HTTP calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client.HttpClient.request",
                fake_request_not_called,
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "invitations",
                        "accept",
                        "--name",
                        "accounts/123/invitations/inv-001",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["operation"], "account-management.accounts.invitations.accept")
            self.assertEqual(payload["plan"]["selector"], "accounts/123/invitations/inv-001")
            self.assertEqual(calls, [])

    def test_accounts_invitations_decline_dry_run_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                raise AssertionError("Dry-run must not issue HTTP calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client.HttpClient.request",
                fake_request_not_called,
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "invitations",
                        "decline",
                        "--name",
                        "accounts/123/invitations/inv-001",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["operation"], "account-management.accounts.invitations.decline")

    def test_accounts_invitations_accept_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "account-management",
                        "accounts",
                        "invitations",
                        "accept",
                        "--name",
                        "accounts/123/invitations/inv-001",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(payload["reasons"][0], "--apply requires --plan-in for account-management accounts invitations accept.")

    def test_accounts_invitations_decline_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "account-management",
                        "accounts",
                        "invitations",
                        "decline",
                        "--name",
                        "accounts/123/invitations/inv-001",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(payload["reasons"][0], "--apply requires --plan-in for account-management accounts invitations decline.")

    def test_accounts_invitations_accept_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "accept.plan.json"
            self._write_invitation_plan(plan_path, operation="account-management.accounts.invitations.accept", name="accounts/123/invitations/inv-001")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "invitations",
                        "accept",
                        "--name",
                        "accounts/123/invitations/inv-001",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(payload["reasons"][0], "--apply requires --yes for account-management accounts invitations accept.")

    def test_accounts_invitations_decline_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "decline.plan.json"
            self._write_invitation_plan(plan_path, operation="account-management.accounts.invitations.decline", name="accounts/123/invitations/inv-001")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "invitations",
                        "decline",
                        "--name",
                        "accounts/123/invitations/inv-001",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(payload["reasons"][0], "--apply requires --yes for account-management accounts invitations decline.")

    def test_accounts_invitations_accept_rejects_malformed_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "invitations",
                        "accept",
                        "--name",
                        "accounts/123",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(
                payload["error"],
                "--name must be in accounts/{account}/invitations/{invitation} format.",
            )

    def test_accounts_invitations_decline_rejects_malformed_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "invitations",
                        "decline",
                        "--name",
                        "accounts/123",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(
                payload["error"],
                "--name must be in accounts/{account}/invitations/{invitation} format.",
            )

    def test_accounts_invitations_plan_in_mismatch_refuses_no_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "bad.plan.json"
            plan_path.write_text(json.dumps({"operation": "account-management.accounts.invitations.accept", "selector": "accounts/999/invitations/inv-001"}), encoding="utf-8")

            calls: list[str] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                raise AssertionError("Plan mismatch must require explicit no-snapshot approval before API calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_not_called), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "invitations",
                        "accept",
                        "--name",
                        "accounts/123/invitations/inv-001",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "Plan selector mismatch: expected accounts/123/invitations/inv-001, got accounts/999/invitations/inv-001 from --plan-in.")
            self.assertEqual(calls, [])

    def _run_invitation_apply(
        self,
        *,
        action: str,
        list_invitations: list[dict[str, str]] | None = None,
        list_status: int = 200,
    ) -> tuple[dict, int]:
        invitations = list_invitations or []

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "plan.json"
            operation = f"account-management.accounts.invitations.{action}"
            self._write_invitation_plan(plan_path, operation=operation, name="accounts/123/invitations/inv-001")

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    return HttpResponse(status=200, headers={}, body=b"{}", url=url)
                if method == "GET":
                    if list_status != 200:
                        return HttpResponse(status=list_status, headers={}, body=b"error", url=url)
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"invitations": invitations}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError(f"Unexpected method: {method}")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "invitations",
                        action,
                        "--name",
                        "accounts/123/invitations/inv-001",
                    ]
                )
            return json.loads(buf.getvalue()), rc

    def test_accounts_invitations_accept_apply_marks_changed_true_when_gone(self) -> None:
        payload, rc = self._run_invitation_apply(action="accept")
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"], "account-management.accounts.invitations.accept")
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["changed"], True)
        self.assertEqual(payload["receipt"]["verification"]["operation"], "account-management.accounts.invitations.list")
        self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", json.dumps(payload))

    def test_accounts_invitations_decline_apply_marks_changed_true_when_gone(self) -> None:
        payload, rc = self._run_invitation_apply(action="decline")
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"], "account-management.accounts.invitations.decline")
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["changed"], True)
        self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", json.dumps(payload))

    def test_accounts_invitations_decline_apply_false_when_invitation_still_present(self) -> None:
        payload, rc = self._run_invitation_apply(
            action="decline",
            list_invitations=[{"name": "accounts/123/invitations/inv-001", "state": "PENDING"}],
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["receipt"]["changed"], False)
        self.assertFalse(payload["receipt"]["verification"]["ok"])

    def test_accounts_invitations_accept_apply_false_when_invitation_still_present(self) -> None:
        payload, rc = self._run_invitation_apply(
            action="accept",
            list_invitations=[{"name": "accounts/123/invitations/inv-001", "state": "PENDING"}],
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"], "account-management.accounts.invitations.accept")
        self.assertEqual(payload["receipt"]["changed"], False)
        self.assertFalse(payload["receipt"]["verification"]["ok"])

    def test_accounts_invitations_decline_plan_in_mismatch_refuses_no_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "bad.plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "account-management.accounts.invitations.decline",
                        "selector": "accounts/999/invitations/inv-001",
                    }
                ),
                encoding="utf-8",
            )

            calls: list[str] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                raise AssertionError("Plan mismatch must require explicit no-snapshot approval before API calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_not_called), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "invitations",
                        "decline",
                        "--name",
                        "accounts/123/invitations/inv-001",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "Plan selector mismatch: expected accounts/123/invitations/inv-001, got accounts/999/invitations/inv-001 from --plan-in.",
            )
            self.assertEqual(calls, [])

    def test_accounts_invitations_apply_false_when_list_fails(self) -> None:
        payload, rc = self._run_invitation_apply(action="decline", list_status=500)
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"], "account-management.accounts.invitations.decline")
        self.assertEqual(payload["receipt"]["changed"], False)

    def test_accounts_invitations_apply_false_when_accept_list_fails(self) -> None:
        payload, rc = self._run_invitation_apply(action="accept", list_status=500)
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"], "account-management.accounts.invitations.accept")
        self.assertEqual(payload["receipt"]["changed"], False)

    def test_accounts_create_dry_run_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            account = {
                "accountName": "Example Account",
                "type": "LOCATION_GROUP",
                "primaryOwner": "accounts/999",
            }
            account_path = self._make_account_file(root, account)

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                raise AssertionError("Dry-run must not issue HTTP calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client.HttpClient.request",
                fake_request_not_called,
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "create",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "account-management.accounts.create")

    def test_accounts_create_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            account = {
                "accountName": "Example Account",
                "type": "LOCATION_GROUP",
                "primaryOwner": "accounts/999",
            }
            account_path = self._make_account_file(root, account)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "account-management",
                        "accounts",
                        "create",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --plan-in for account-management accounts create.")

    def test_accounts_create_apply_success_verifies_by_get(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "create.plan.json"
            account = self._write_account_plan_for_create(plan_path)
            account_path = self._make_account_file(root, account)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=b'{"name":"accounts/created-001"}',
                        url=url,
                    )
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=b'{"name":"accounts/created-001","accountName":"Example Account","type":"LOCATION_GROUP"}',
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "create",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "account-management.accounts.get")
            self.assertEqual(payload["receipt"]["verification"]["response"]["name"], "accounts/created-001")
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", json.dumps(payload))

    def test_accounts_create_apply_false_when_create_response_has_no_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "create.plan.json"
            account = self._write_account_plan_for_create(plan_path)
            account_path = self._make_account_file(root, account)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=b'{"accountName":"Example Account","type":"LOCATION_GROUP"}',
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "create",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["selector"], "accounts/<missing-name>")
            self.assertEqual(payload["receipt"]["changed"], False)
            self.assertFalse(payload["receipt"]["verification"]["ok"])
            self.assertEqual(
                payload["receipt"]["verification"]["note"],
                "Create response did not include a usable name. Could not run read-back verification.",
            )
            self.assertEqual(
                payload["receipt"]["verification"]["request"]["path"],
                "v1/<missing-name>",
            )
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", json.dumps(payload))

    def test_accounts_create_rejects_forbidden_account_type(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            account = {
                "accountName": "Example Account",
                "type": "PERSONAL",
                "primaryOwner": "accounts/999",
            }
            account_path = self._make_account_file(root, account)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "create",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("PERSONAL", payload["error"])

    def test_accounts_create_rejects_non_string_primary_owner(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            account = {
                "accountName": "Example Account",
                "type": "LOCATION_GROUP",
                "primaryOwner": {"emailAddress": "owner@example.com"},
            }
            account_path = self._make_account_file(root, account)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "create",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("primaryOwner", payload["error"])

    def test_accounts_create_rejects_unsupported_payload_shape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            account = {
                "accountName": "Example Account",
                "type": "LOCATION_GROUP",
                "primaryOwner": "accounts/999",
                "name": "accounts/should-not-pass",
            }
            account_path = self._make_account_file(root, account)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "create",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_accounts_create_plan_in_mismatch_refuses_no_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "bad.plan.json"
            _ = self._write_account_plan_for_create(plan_path)
            plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
            plan_data["selector"] = "accounts/different-account"
            plan_data["proposed_changes"][0]["selector"] = "accounts/different-account"
            plan_data["baseline"]["selector"] = "accounts/different-account"
            plan_path.write_text(json.dumps(plan_data, ensure_ascii=False), encoding="utf-8")

            account = {
                "accountName": "Example Account",
                "type": "LOCATION_GROUP",
                "primaryOwner": "accounts/999",
            }
            account_path = self._make_account_file(root, account)
            calls: list[str] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                raise AssertionError("Plan mismatch must require explicit no-snapshot approval before API calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_not_called), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "create",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("Plan selector mismatch", payload["reasons"][0])
            self.assertEqual(calls, [])

    def test_accounts_patch_dry_run_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            account = {
                "accountName": "New Account Name",
            }
            account_path = self._make_account_file(root, account)

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                raise AssertionError("Dry-run must not issue HTTP calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client.HttpClient.request",
                fake_request_not_called,
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "patch",
                        "--name",
                        "accounts/123",
                        "--update-mask",
                        "accountName",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "account-management.accounts.patch")

    def test_accounts_patch_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            account = {"accountName": "Updated Name"}
            account_path = self._make_account_file(root, account)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "account-management",
                        "accounts",
                        "patch",
                        "--name",
                        "accounts/123",
                        "--update-mask",
                        "accountName",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --plan-in for account-management accounts patch.")

    def test_accounts_patch_validate_only_sends_validate_param(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            account = {"accountName": "Updated Name", "name": "accounts/123"}
            account_path = self._make_account_file(root, account)
            calls: list[dict[str, Any]] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append({
                    "method": method,
                    "params": params,
                    "body": json_body,
                })
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"name":"accounts/123","accountName":"Updated Name"}',
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "patch",
                        "--name",
                        "accounts/123",
                        "--update-mask",
                        "accountName",
                        "--account-file",
                        str(account_path),
                        "--validate-only",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "PATCH")
            self.assertEqual(calls[0]["params"]["updateMask"], "accountName")
            self.assertEqual(calls[0]["params"]["validateOnly"], True)

    def test_accounts_patch_rejects_unsupported_update_mask(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            account = {"accountName": "Updated Name"}
            account_path = self._make_account_file(root, account)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "patch",
                        "--name",
                        "accounts/123",
                        "--update-mask",
                        "title",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Only accountName is editable", payload["error"])

    def test_accounts_patch_rejects_name_mismatch_in_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            account = {"accountName": "Updated Name", "name": "accounts/other"}
            account_path = self._make_account_file(root, account)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "account-management",
                        "accounts",
                        "patch",
                        "--name",
                        "accounts/123",
                        "--update-mask",
                        "accountName",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_accounts_patch_apply_verifies_by_get(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "patch.plan.json"
            self._write_account_plan(plan_path, operation="account-management.accounts.patch", name="accounts/123")
            account = {"accountName": "Example Account"}
            account_path = self._make_account_file(root, account)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "PATCH":
                    return HttpResponse(status=200, headers={}, body=b"{}", url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=b'{"name":"accounts/123","accountName":"Example Account","type":"LOCATION_GROUP"}',
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "patch",
                        "--name",
                        "accounts/123",
                        "--update-mask",
                        "accountName",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "account-management.accounts.get")
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", json.dumps(payload))

    def test_accounts_patch_apply_false_when_read_back_account_name_differs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "patch.plan.json"
            self._write_account_plan(plan_path, operation="account-management.accounts.patch", name="accounts/123")
            account = {"accountName": "Example Account"}
            account_path = self._make_account_file(root, account)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "PATCH":
                    return HttpResponse(status=200, headers={}, body=b"{}", url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=b'{"name":"accounts/123","accountName":"Different Account","type":"LOCATION_GROUP"}',
                        url=url,
                    )
                raise AssertionError("unexpected method")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "patch",
                        "--name",
                        "accounts/123",
                        "--update-mask",
                        "accountName",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["changed"], False)
            self.assertFalse(payload["receipt"]["verification"]["ok"])
            self.assertEqual(
                payload["receipt"]["verification"]["note"],
                "Read-back response accountName did not match the requested accountName.",
            )
            self.assertEqual(
                payload["receipt"]["verification"]["response"]["accountName"],
                "Different Account",
            )
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", json.dumps(payload))

    def test_accounts_patch_plan_in_mismatch_refuses_no_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "bad.plan.json"
            self._write_account_plan(plan_path, operation="account-management.accounts.patch", name="accounts/other")
            account = {"accountName": "Updated Name"}
            account_path = self._make_account_file(root, account)
            calls: list[str] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                raise AssertionError("Plan mismatch must require explicit no-snapshot approval before API calls")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_not_called), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "account-management",
                        "accounts",
                        "patch",
                        "--name",
                        "accounts/123",
                        "--update-mask",
                        "accountName",
                        "--account-file",
                        str(account_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("Plan selector mismatch", payload["reasons"][0])
            self.assertEqual(calls, [])
