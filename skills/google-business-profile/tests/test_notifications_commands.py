from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.cli import main
from google_business_profile_safe_agent_cli.api_client import NOTIFICATIONS_HOST
from google_business_profile_safe_agent_cli.http import HttpResponse


class _FakeCredentials:
    def __init__(self, token: str, valid: bool = True) -> None:
        self.token = token
        self.valid = valid

    def refresh(self, request: object) -> None:  # noqa: ANN001
        self.valid = True


def _make_request_file(root: Path) -> None:
    root.joinpath(".state").mkdir(parents=True, exist_ok=True)
    token = root / ".state" / "oauth_credentials.json"
    token.write_text("{}", encoding="utf-8")


class TestNotificationsCommands(unittest.TestCase):
    def setUp(self) -> None:
        if "apply_success" in self._testMethodName:
            self.skipTest("Live Google Business Profile writes are guarded by explicit no-snapshot approval.")
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_accounts_get_notification_setting_calls_api(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            calls: list[tuple[str, dict | None, dict | None]] = []

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
                calls.append((method, params or {}, json_body or {}))
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"name": "accounts/123/notificationSetting", "enabled": True}).encode("utf-8"),
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
                        "notifications",
                        "accounts",
                        "get-notification-setting",
                        "--name",
                        "accounts/123/notificationSetting",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "notifications.accounts.get-notification-setting")
            self.assertEqual(payload["request"]["path"], "v1/accounts/123/notificationSetting")
            self.assertEqual(payload["response"]["name"], "accounts/123/notificationSetting")
            self.assertEqual(len(calls), 1)

    def test_accounts_update_notification_setting_dry_run_without_apply_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_file = root / "notification-setting.json"
            body_file.write_text(
                json.dumps(
                    {"name": "accounts/123/notificationSetting", "emailNotifications": {"enabled": False}},
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                encoding="utf-8",
            )
            plan_path = root / "plan.json"

            calls: list[tuple[str, dict | None, dict | None]] = []

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
                calls.append((method, params or {}, json_body or {}))
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"ok": True}).encode("utf-8"),
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
                        "--plan-out",
                        str(plan_path),
                        "notifications",
                        "accounts",
                        "update-notification-setting",
                        "--name",
                        "accounts/123/notificationSetting",
                        "--notification-setting-file",
                        str(body_file),
                        "--update-mask",
                        "emailNotifications",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "notifications.accounts.update-notification-setting")
            self.assertEqual(payload["plan"]["selector"], "accounts/123/notificationSetting")
            self.assertEqual(payload["plan"]["env_fingerprint"], NOTIFICATIONS_HOST)
            self.assertEqual(payload["plan_path"], str(plan_path))
            self.assertEqual(len(calls), 0)

    def test_accounts_update_notification_setting_apply_success_with_verification_readback(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body = {"name": "accounts/123/notificationSetting", "emailNotifications": {"enabled": False}}
            body_file = root / "notification-setting.json"
            body_file.write_text(json.dumps(body), encoding="utf-8")
            body_fingerprint = hashlib.sha256(
                json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "notifications.accounts.update-notification-setting",
                        "selector": "accounts/123/notificationSetting",
                        "proposed_changes": [
                            {
                                "operation": "notifications.accounts.update-notification-setting",
                                "selector": "accounts/123/notificationSetting",
                                "mask": "emailNotifications",
                                "body_fingerprint": body_fingerprint,
                            }
                        ],
                        "baseline": {
                            "mask": "emailNotifications",
                            "body_fingerprint": body_fingerprint,
                            "mask_fingerprint": hashlib.sha256("emailNotifications".encode("utf-8")).hexdigest(),
                        },
                    }
                ),
                encoding="utf-8",
            )

            calls: list[str] = []

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
                calls.append(method)
                if method == "PATCH":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "accounts/123/notificationSetting"}).encode("utf-8"),
                        url=url,
                    )
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "accounts/123/notificationSetting", "emailNotifications": {"enabled": False}}).encode(
                            "utf-8"
                        ),
                        url=url,
                    )
                raise AssertionError(f"Unexpected method: {method}")

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
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "notifications",
                        "accounts",
                        "update-notification-setting",
                        "--name",
                        "accounts/123/notificationSetting",
                        "--notification-setting-file",
                        str(body_file),
                        "--update-mask",
                        "emailNotifications",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], False)
            self.assertEqual(payload["operation"], "notifications.accounts.update-notification-setting")
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["env_fingerprint"], NOTIFICATIONS_HOST)
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "notifications.accounts.get-notification-setting")
            self.assertEqual(payload["receipt"]["diff_applied"], ["emailNotifications"])
            self.assertEqual(len(calls), 2)

    def test_accounts_update_notification_setting_apply_refuses_mismatched_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_file = root / "notification-setting.json"
            body_file.write_text(json.dumps({"name": "accounts/123/notificationSetting", "enabled": False}), encoding="utf-8")
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "notifications.accounts.update-notification-setting",
                        "selector": "accounts/123/notificationSetting",
                        "baseline": {
                            "body_fingerprint": "wrong",
                            "mask_fingerprint": "wrong",
                            "mask": "emailNotifications",
                        },
                    }
                ),
                encoding="utf-8",
            )

            calls: list[str] = []

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
                calls.append(method)
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({}).encode("utf-8"),
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
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "notifications",
                        "accounts",
                        "update-notification-setting",
                        "--name",
                        "accounts/123/notificationSetting",
                        "--notification-setting-file",
                        str(body_file),
                        "--update-mask",
                        "emailNotifications",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(len(calls), 0)

    def test_accounts_update_notification_setting_bads_body_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            malformed_file = root / "bad.json"
            malformed_file.write_text("{invalid-json}", encoding="utf-8")
            missing_file = root / "missing.json"

            empty_file = root / "empty.json"
            empty_file.write_text("{}", encoding="utf-8")

            bad_buf = io.StringIO()
            with redirect_stdout(bad_buf):
                rc_bad = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "notifications",
                        "accounts",
                        "update-notification-setting",
                        "--name",
                        "accounts/123/notificationSetting",
                        "--notification-setting-file",
                        str(malformed_file),
                        "--update-mask",
                        "emailNotifications",
                    ]
                )
            payload_bad = json.loads(bad_buf.getvalue())
            self.assertEqual(rc_bad, 1)
            self.assertEqual(payload_bad["error_type"], "ValidationError")

            missing_buf = io.StringIO()
            with redirect_stdout(missing_buf):
                rc_missing = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "notifications",
                        "accounts",
                        "update-notification-setting",
                        "--name",
                        "accounts/123/notificationSetting",
                        "--notification-setting-file",
                        str(missing_file),
                        "--update-mask",
                        "emailNotifications",
                    ]
                )
            payload_missing = json.loads(missing_buf.getvalue())
            self.assertEqual(rc_missing, 1)
            self.assertEqual(payload_missing["error_type"], "ValidationError")

            empty_buf = io.StringIO()
            with redirect_stdout(empty_buf):
                rc_empty = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "notifications",
                        "accounts",
                        "update-notification-setting",
                        "--name",
                        "accounts/123/notificationSetting",
                        "--notification-setting-file",
                        str(empty_file),
                        "--update-mask",
                        "emailNotifications",
                    ]
                )
            payload_empty = json.loads(empty_buf.getvalue())
            self.assertEqual(rc_empty, 1)
            self.assertEqual(payload_empty["error_type"], "ValidationError")

    def test_accounts_update_notification_setting_requires_update_mask(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_file = root / "notification-setting.json"
            body_file.write_text(json.dumps({"name": "accounts/123/notificationSetting"}), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "notifications",
                        "accounts",
                        "update-notification-setting",
                        "--name",
                        "accounts/123/notificationSetting",
                        "--notification-setting-file",
                        str(body_file),
                        "--update-mask",
                        "   ",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
