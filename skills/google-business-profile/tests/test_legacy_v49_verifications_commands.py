from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.api_client import LEGACY_V49_HOST
from google_business_profile_safe_agent_cli.cli import main
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


def _write_complete_plan(path: Path, *, verification_name: str, pin: str) -> None:
    body = {"pin": pin}
    body_fingerprint = hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    path.write_text(
        json.dumps(
            {
                "operation": "legacy-v49.accounts.locations.verifications.complete",
                "selector": verification_name,
                "proposed_changes": [
                    {
                        "operation": "legacy-v49.accounts.locations.verifications.complete",
                        "selector": verification_name,
                        "mask": "name",
                        "body_fingerprint": body_fingerprint,
                    }
                ],
                "baseline": {
                    "mask": "name",
                    "body_fingerprint": body_fingerprint,
                    "mask_fingerprint": hashlib.sha256("name".encode("utf-8")).hexdigest(),
                },
            }
        ),
        encoding="utf-8",
    )


class TestLegacyV49VerificationsCommands(unittest.TestCase):
    def setUp(self) -> None:
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_verifications_list_calls_api(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            request_data: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"verifications":[{"name":"accounts/123/locations/456/verifications/001","state":"PENDING"}]}',
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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "verifications",
                        "list",
                        "--parent",
                        "accounts/123/locations/456",
                        "--page-size",
                        "20",
                        "--page-token",
                        "next-page",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.verifications.list")
            self.assertEqual(payload["request"]["method"], "GET")
            self.assertEqual(payload["request"]["host"], LEGACY_V49_HOST)
            self.assertEqual(payload["request"]["path"], "v4/accounts/123/locations/456/verifications")
            self.assertEqual((payload["request"]["params"] or {}).get("pageSize"), 20)
            self.assertEqual((payload["request"]["params"] or {}).get("pageToken"), "next-page")
            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(
                request_data["url"],
                "https://mybusiness.googleapis.com/v4/accounts/123/locations/456/verifications",
            )
            self.assertEqual((request_data["params"] or {}).get("pageSize"), 20)
            self.assertEqual((request_data["params"] or {}).get("pageToken"), "next-page")

    def test_verifications_complete_dry_run_emits_plan_without_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            pin_file = root / "pin.txt"
            pin_file.write_text("123456", encoding="utf-8")
            plan_path = root / "plan.json"

            calls: list[str] = []

            def fake_request_not_called(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(f"{method} {url}")
                raise AssertionError("HTTP should not run during dry-run.")

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
                        "--plan-out",
                        str(plan_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "verifications",
                        "complete",
                        "--name",
                        "accounts/123/locations/456/verifications/001",
                        "--pin-file",
                        str(pin_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.verifications.complete")
            self.assertEqual(payload["plan"]["selector"], "accounts/123/locations/456/verifications/001")
            self.assertEqual(payload["plan"]["env_fingerprint"], LEGACY_V49_HOST)
            self.assertEqual(payload["plan_path"], str(plan_path))
            self.assertEqual(calls, [])
            self.assertNotIn("123456", buf.getvalue())

    def test_verifications_complete_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            pin_file = root / "pin.txt"
            pin_file.write_text("123456", encoding="utf-8")

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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "verifications",
                        "complete",
                        "--name",
                        "accounts/123/locations/456/verifications/001",
                        "--pin-file",
                        str(pin_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --plan-in for legacy-v49 accounts locations verifications complete.",
            )

    def test_verifications_complete_plan_mismatch_makes_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            pin_file = root / "pin.txt"
            pin_file.write_text("123456", encoding="utf-8")
            plan_path = root / "plan.json"
            _write_complete_plan(
                plan_path,
                verification_name="accounts/123/locations/456/verifications/001",
                pin="654321",
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
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(f"{method} {url}")
                raise AssertionError("HTTP should not run on plan mismatch.")

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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "verifications",
                        "complete",
                        "--name",
                        "accounts/123/locations/456/verifications/001",
                        "--pin-file",
                        str(pin_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertIn("Plan body fingerprint mismatch", payload["reasons"][0])
            self.assertEqual(calls, [])

    def test_verifications_complete_apply_success_uses_follow_up_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            pin_file = root / "pin.txt"
            pin_file.write_text("123456", encoding="utf-8")
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"
            _write_complete_plan(
                plan_path,
                verification_name="accounts/123/locations/456/verifications/001",
                pin="123456",
            )

            calls: list[tuple[str, str, dict | None, dict | None]] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append((method, url, params, json_body))
                if method == "POST":
                    body = {
                        "verification": {
                            "name": "accounts/123/locations/456/verifications/001",
                            "state": "PENDING",
                        }
                    }
                else:
                    body = {
                        "verifications": [
                            {
                                "name": "accounts/123/locations/456/verifications/001",
                                "state": "COMPLETED",
                            }
                        ]
                    }
                return HttpResponse(status=200, headers={}, body=json.dumps(body).encode("utf-8"), url=url)

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
                        "--receipt-out",
                        str(receipt_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "verifications",
                        "complete",
                        "--name",
                        "accounts/123/locations/456/verifications/001",
                        "--pin-file",
                        str(pin_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.verifications.complete")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertEqual(
                payload["receipt"]["verification"]["operation"],
                "legacy-v49.accounts.locations.verifications.list",
            )
            self.assertEqual(payload["receipt_path"], str(receipt_path))
            self.assertEqual(calls[0][0], "POST")
            self.assertEqual(
                calls[0][1],
                "https://mybusiness.googleapis.com/v4/accounts/123/locations/456/verifications/001:complete",
            )
            self.assertEqual(calls[0][3], {"pin": "123456"})
            self.assertEqual(calls[1][0], "GET")
            self.assertEqual(
                calls[1][1],
                "https://mybusiness.googleapis.com/v4/accounts/123/locations/456/verifications",
            )
            self.assertNotIn("123456", buf.getvalue())

    def test_verifications_complete_apply_reports_wrong_follow_up_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            pin_file = root / "pin.txt"
            pin_file.write_text("123456", encoding="utf-8")
            plan_path = root / "plan.json"
            _write_complete_plan(
                plan_path,
                verification_name="accounts/123/locations/456/verifications/001",
                pin="123456",
            )

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "POST":
                    body = {
                        "verification": {
                            "name": "accounts/123/locations/456/verifications/001",
                            "state": "PENDING",
                        }
                    }
                else:
                    body = {
                        "verifications": [
                            {
                                "name": "accounts/123/locations/456/verifications/001",
                                "state": "PENDING",
                            }
                        ]
                    }
                return HttpResponse(status=200, headers={}, body=json.dumps(body).encode("utf-8"), url=url)

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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "verifications",
                        "complete",
                        "--name",
                        "accounts/123/locations/456/verifications/001",
                        "--pin-file",
                        str(pin_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])
            self.assertIn("expected COMPLETED", payload["receipt"]["verification"]["note"])
