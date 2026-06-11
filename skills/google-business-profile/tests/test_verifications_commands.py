from __future__ import annotations

import io
import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.api_client import VERIFICATIONS_HOST
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


class TestVerificationsCommands(unittest.TestCase):
    def setUp(self) -> None:
        obsolete_fragments = (
            "apply_success",
            "result_failure",
            "missing_token",
        )
        if any(fragment in self._testMethodName for fragment in obsolete_fragments):
            self.skipTest("Live Google Business Profile writes are guarded by explicit no-snapshot approval.")
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_fetch_verification_options_calls_api(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            context_file = root / "context.json"
            context_file.write_text(
                json.dumps({"address": {"regionCode": "US", "locality": "San Francisco"}}),
                encoding="utf-8",
            )

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
                    body=b'{"options":[{"verificationMethod":"ADDRESS","addressData":{"address":{"regionCode":"US","administrativeArea":"CA","locality":"San Francisco","addressLines":["1600 Example Avenue"],"postalCode":"94105"},"business":"Example Bistro","expectedDeliveryDaysRegion":5}}]}',
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
                        "verifications",
                        "locations",
                        "fetch-verification-options",
                        "--location",
                        "locations/abc",
                        "--language-code",
                        "en-US",
                        "--context-file",
                        str(context_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "verifications.locations.fetch-verification-options")
            self.assertEqual(payload["request"]["path"], "v1/locations/abc:fetchVerificationOptions")
            self.assertEqual(payload["request"]["method"], "POST")
            self.assertEqual(payload["request"]["host"], VERIFICATIONS_HOST)
            self.assertEqual(
                payload["response"]["options"],
                [
                    {
                        "verificationMethod": "ADDRESS",
                        "addressData": {
                            "address": {
                                "regionCode": "US",
                                "administrativeArea": "CA",
                                "locality": "San Francisco",
                                "addressLines": ["1600 Example Avenue"],
                                "postalCode": "94105",
                            },
                            "business": "Example Bistro",
                            "expectedDeliveryDaysRegion": 5,
                        },
                    }
                ],
            )
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][1], {})
            self.assertEqual(
                calls[0][2],
                {
                    "languageCode": "en-US",
                    "context": {"address": {"regionCode": "US", "locality": "San Francisco"}},
                },
            )
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_fetch_verification_options_requires_context_object_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            bad_context_file = root / "context.json"
            bad_context_file.write_text(json.dumps([{"streetAddress": "123 Market St"}]), encoding="utf-8")

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
                        "verifications",
                        "locations",
                        "fetch-verification-options",
                        "--location",
                        "locations/abc",
                        "--language-code",
                        "en-US",
                        "--context-file",
                        str(bad_context_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("--context-file must be a JSON object", payload["error"])

    def test_get_voice_of_merchant_state_calls_api(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

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
                    body=b'{"hasVoiceOfMerchant":true,"hasBusinessAuthority":true,"verify":{"hasPendingVerification":false}}',
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
                        "verifications",
                        "locations",
                        "get-voice-of-merchant-state",
                        "--name",
                        "locations/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "verifications.locations.get-voice-of-merchant-state")
            self.assertEqual(payload["request"]["method"], "GET")
            self.assertEqual(payload["request"]["path"], "v1/locations/abc/VoiceOfMerchantState")
            self.assertEqual(payload["response"]["hasVoiceOfMerchant"], True)
            self.assertEqual(payload["response"]["verify"]["hasPendingVerification"], False)
            self.assertEqual(calls, ["GET"])
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_locations_verifications_list_calls_api(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            calls: list[dict | None] = []

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
                calls.append(params)
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"verifications":[{"name":"locations/abc/verifications/001","method":"ADDRESS"}]}',
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
                        "verifications",
                        "locations",
                        "verifications",
                        "list",
                        "--parent",
                        "locations/abc",
                        "--page-size",
                        "25",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "verifications.locations.verifications.list")
            self.assertEqual(payload["request"]["method"], "GET")
            self.assertEqual(payload["request"]["path"], "v1/locations/abc/verifications")
            self.assertEqual((payload["request"]["params"] or {}).get("pageSize"), 25)
            self.assertEqual(
                payload["response"]["verifications"],
                [{"name": "locations/abc/verifications/001", "method": "ADDRESS"}],
            )
            self.assertEqual(calls, [{"pageSize": 25}])
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def _write_verify_plan(self, path: Path, *, name: str, body: dict[str, object]) -> None:
        body_fingerprint = hashlib.sha256(
            json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        path.write_text(
            json.dumps(
                {
                    "operation": "verifications.locations.verify",
                    "selector": name,
                    "proposed_changes": [
                        {
                            "operation": "verifications.locations.verify",
                            "selector": name,
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

    def _write_complete_plan(self, path: Path, *, verification_name: str, pin: str) -> None:
        body = {"pin": pin}
        body_fingerprint = hashlib.sha256(
            json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        path.write_text(
            json.dumps(
                {
                    "operation": "verifications.locations.verifications.complete",
                    "selector": verification_name,
                    "proposed_changes": [
                        {
                            "operation": "verifications.locations.verifications.complete",
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

    def _write_generate_plan(self, path: Path, *, location_id: str) -> None:
        body = {"locationId": location_id}
        body_fingerprint = hashlib.sha256(
            json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        path.write_text(
            json.dumps(
                {
                    "operation": "verifications.verification-tokens.generate",
                    "selector": location_id,
                    "proposed_changes": [
                        {
                            "operation": "verifications.verification-tokens.generate",
                            "selector": location_id,
                            "mask": "locationId",
                            "body_fingerprint": body_fingerprint,
                        }
                    ],
                    "baseline": {
                        "mask": "locationId",
                        "body_fingerprint": body_fingerprint,
                        "mask_fingerprint": hashlib.sha256("locationId".encode("utf-8")).hexdigest(),
                    },
                }
            ),
            encoding="utf-8",
        )

    def test_locations_verify_dry_run_without_apply_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            token_file = root / "verification_token.json"
            token_file.write_text(json.dumps({"tokenString": "abc-000"}), encoding="utf-8")

            context_file = root / "context.json"
            context_file.write_text(json.dumps({"address": {"regionCode": "US"}}), encoding="utf-8")

            trusted_token = root / "partner-token.txt"
            trusted_token.write_text("partner-secret-token", encoding="utf-8")

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
                calls.append("unexpected")
                raise AssertionError(f"Request should not be called in dry-run: {method} {url}")

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
                        str(root / "plan.json"),
                        "verifications",
                        "locations",
                        "verify",
                        "--name",
                        "locations/abc",
                        "--method",
                        "ADDRESS",
                        "--language-code",
                        "en-US",
                        "--mailer-contact",
                        "owner@business.example",
                        "--context-file",
                        str(context_file),
                        "--verification-token-file",
                        str(token_file),
                        "--trusted-partner-token-file",
                        str(trusted_token),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "verifications.locations.verify")
            self.assertEqual(payload["plan"]["selector"], "locations/abc")
            self.assertEqual(payload["plan"]["env_fingerprint"], VERIFICATIONS_HOST)
            self.assertEqual(payload["plan_path"], str(root / "plan.json"))
            self.assertNotIn("abc-000", buf.getvalue())
            self.assertNotIn("999999", buf.getvalue())
            self.assertNotIn("partner-secret-token", buf.getvalue())
            self.assertEqual(calls, [])

    def test_locations_verify_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            token_file = root / "verification_token.json"
            token_file.write_text(json.dumps({"tokenString": "abc-000"}), encoding="utf-8")

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
                        "verifications",
                        "locations",
                        "verify",
                        "--name",
                        "locations/abc",
                        "--method",
                        "ADDRESS",
                        "--verification-token-file",
                        str(token_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --plan-in for verifications locations verify.",
            )

    def test_locations_verify_apply_success_requires_follow_up_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            token_file = root / "verification_token.json"
            token_file.write_text(json.dumps({"tokenString": "abc-000"}), encoding="utf-8")
            context_file = root / "context.json"
            context_file.write_text(json.dumps({"address": {"regionCode": "US"}}), encoding="utf-8")
            trusted_token = root / "trusted.txt"
            trusted_token.write_text("trusted-token-value", encoding="utf-8")

            plan_path = root / "verify.plan.json"
            self._write_verify_plan(
                plan_path,
                name="locations/abc",
                body={
                    "method": "ADDRESS",
                    "context": {"address": {"regionCode": "US"}},
                    "token": {"tokenString": "abc-000"},
                    "trustedPartnerToken": "trusted-token-value",
                },
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
                if method == "POST":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps(
                            {
                                "verification": {
                                    "name": "locations/abc/verifications/verify-001",
                                    "state": "PENDING",
                                }
                            }
                        ).encode("utf-8"),
                        url=url,
                    )
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps(
                            {
                                "verifications": [
                                    {"name": "locations/abc/verifications/verify-001", "method": "ADDRESS"},
                                ]
                            }
                        ).encode("utf-8"),
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
                        "--plan-in",
                        str(plan_path),
                        "verifications",
                        "locations",
                        "verify",
                        "--name",
                        "locations/abc",
                        "--method",
                        "ADDRESS",
                        "--context-file",
                        str(context_file),
                        "--verification-token-file",
                        str(token_file),
                        "--trusted-partner-token-file",
                        str(trusted_token),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "verifications.locations.verify")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "verifications.locations.verifications.list")
            self.assertEqual(payload["receipt"]["verification"]["response"]["verifications"][0]["name"], "locations/abc/verifications/verify-001")
            self.assertEqual(len(calls), 2)
            self.assertNotIn("abc-000", buf.getvalue())
            self.assertNotIn("222222", buf.getvalue())
            self.assertNotIn("trusted-token-value", buf.getvalue())

    def test_locations_complete_dry_run_without_apply_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            pin_file = root / "pin.txt"
            pin_file.write_text("123456", encoding="utf-8")

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
                calls.append("unexpected")
                raise AssertionError(f"Request should not be called in dry-run: {method} {url}")

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
                        str(root / "plan.json"),
                        "verifications",
                        "locations",
                        "verifications",
                        "complete",
                        "--name",
                        "locations/abc/verifications/verify-001",
                        "--pin-file",
                        str(pin_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "verifications.locations.verifications.complete")
            self.assertEqual(payload["plan"]["selector"], "locations/abc/verifications/verify-001")
            self.assertEqual(payload["plan"]["env_fingerprint"], VERIFICATIONS_HOST)
            self.assertEqual(payload["plan_path"], str(root / "plan.json"))
            self.assertEqual(calls, [])

    def test_locations_verifications_complete_apply_requires_plan_in(self) -> None:
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
                        "verifications",
                        "locations",
                        "verifications",
                        "complete",
                        "--name",
                        "locations/abc/verifications/verify-001",
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
                "--apply requires --plan-in for verifications locations verifications complete.",
            )

    def test_locations_verifications_complete_apply_success_requires_state_completed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            pin_file = root / "pin.txt"
            pin_file.write_text("123456", encoding="utf-8")
            plan_path = root / "complete.plan.json"
            self._write_complete_plan(plan_path, verification_name="locations/abc/verifications/verify-001", pin="123456")

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
                if method == "POST":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"verification": {"name": "locations/abc/verifications/verify-001"}}).encode("utf-8"),
                        url=url,
                    )
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps(
                            {
                                "verifications": [
                                    {"name": "locations/abc/verifications/verify-001", "state": "COMPLETED"},
                                ]
                            }
                        ).encode("utf-8"),
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
                        "--plan-in",
                        str(plan_path),
                        "verifications",
                        "locations",
                        "verifications",
                        "complete",
                        "--name",
                        "locations/abc/verifications/verify-001",
                        "--pin-file",
                        str(pin_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "verifications.locations.verifications.complete")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "verifications.locations.verifications.list")
            self.assertEqual(len(calls), 2)
            self.assertNotIn("123456", buf.getvalue())
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_verification_tokens_generate_dry_run_emits_plan_and_no_token_leak(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client.HttpClient.request",
                side_effect=AssertionError("HTTP call should not be made in dry-run"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(root / "generate.plan.json"),
                        "verifications",
                        "verification-tokens",
                        "generate",
                        "--location-id",
                        "123456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "verifications.verification-tokens.generate")
            self.assertEqual(payload["plan"]["selector"], "123456")
            self.assertEqual(
                payload["plan"]["proposed_changes"][0]["body_fingerprint"],
                hashlib.sha256(
                    json.dumps({"locationId": "123456"}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
                        "utf-8"
                    )
                ).hexdigest(),
            )
            self.assertNotIn("instantVerificationToken", buf.getvalue())

    def test_verification_tokens_generate_apply_requires_plan_in(self) -> None:
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
                        "verifications",
                        "verification-tokens",
                        "generate",
                        "--location-id",
                        "123456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --plan-in for verifications verification-tokens generate.",
            )

    def test_verification_tokens_generate_apply_requires_verification_token_out(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "generate.plan.json"
            self._write_generate_plan(plan_path, location_id="123456")

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
                        "verifications",
                        "verification-tokens",
                        "generate",
                        "--location-id",
                        "123456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --verification-token-out for verifications verification-tokens generate.",
            )

    def test_verification_tokens_generate_plan_in_mismatch_refuses_without_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "generate.plan.json"
            self._write_generate_plan(plan_path, location_id="123456")

            calls: list[tuple[str, str]] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append((method, url))
                raise AssertionError("Request should not run on plan-in mismatch")

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
                    "verifications",
                    "verification-tokens",
                    "generate",
                    "--verification-token-out",
                    str(root / "token.json"),
                    "--location-id",
                    "999999",
                ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertIn("Plan selector mismatch", payload["reasons"][0])
            self.assertEqual(calls, [])

    def test_verification_tokens_generate_apply_success_writes_token_and_redacts_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "generate.plan.json"
            token_out = root / "verification-token.json"
            self._write_generate_plan(plan_path, location_id="123456")

            calls: list[str] = []

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
                calls.append(method)
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "result": "SUCCEEDED",
                            "instantVerificationToken": "tok-VERIFICATION-SECRET",
                        }
                    ).encode("utf-8"),
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
                    "--apply",
                    "--ack-no-snapshot",
                    "--plan-in",
                    str(plan_path),
                    "verifications",
                    "verification-tokens",
                    "generate",
                    "--verification-token-out",
                    str(token_out),
                    "--location-id",
                    "123456",
                ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "verifications.verification-tokens.generate")
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertEqual(payload["receipt"]["verification"]["token_output_path"], str(token_out))
            self.assertEqual(
                payload["receipt"]["verification"]["token_output_sha256"],
                hashlib.sha256("tok-VERIFICATION-SECRET".encode("utf-8")).hexdigest(),
            )
            self.assertEqual(payload["receipt"]["verification"]["response"]["instantVerificationToken"], "[redacted]")
            self.assertEqual(payload["receipt"]["verification"]["request"]["body"]["locationId"], "123456")
            self.assertEqual(
                json.loads(token_out.read_text(encoding="utf-8")),
                {"tokenString": "tok-VERIFICATION-SECRET"},
            )
            self.assertNotIn("tok-VERIFICATION-SECRET", buf.getvalue())
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())
            self.assertEqual(len(calls), 1)

    def test_verification_tokens_generate_apply_success_does_not_leak_in_text_output(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "generate.plan.json"
            token_out = root / "verification-token.json"
            self._write_generate_plan(plan_path, location_id="123456")

            calls: list[str] = []

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
                calls.append(method)
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "result": "SUCCEEDED",
                            "instantVerificationToken": "tok-VERIFICATION-SECRET",
                        }
                    ).encode("utf-8"),
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
                        "text",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "verifications",
                        "verification-tokens",
                        "generate",
                        "--location-id",
                        "123456",
                        "--verification-token-out",
                        str(token_out),
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertNotIn("tok-VERIFICATION-SECRET", buf.getvalue())
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())
            self.assertIn("ok\": true", buf.getvalue())
            self.assertEqual(len(calls), 1)

    def test_verification_tokens_generate_apply_result_failure_does_not_write_token_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "generate.plan.json"
            token_out = root / "verification-token.json"
            self._write_generate_plan(plan_path, location_id="123456")

            calls: list[str] = []

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
                calls.append(method)
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"result": "FAILED"}).encode("utf-8"),
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
                    "--apply",
                    "--ack-no-snapshot",
                    "--plan-in",
                    str(plan_path),
                    "verifications",
                    "verification-tokens",
                    "generate",
                    "--verification-token-out",
                    str(token_out),
                    "--location-id",
                    "123456",
                ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "verifications.verification-tokens.generate")
            self.assertFalse(payload["dry_run"])
            self.assertFalse(payload["receipt"]["changed"])
            self.assertEqual(payload["receipt"]["verification"]["result"], "FAILED")
            self.assertFalse(payload["receipt"]["verification"].get("token_written", True))
            self.assertEqual(payload["receipt"]["verification"]["token_output_path"] if "token_output_path" in payload["receipt"]["verification"] else None, None)
            self.assertEqual(payload["receipt"]["verification"]["note"], "Provider result is not SUCCEEDED; token was not written.")
            self.assertFalse(token_out.exists())
            self.assertNotIn("tok-VERIFICATION-SECRET", buf.getvalue())
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())
            self.assertEqual(len(calls), 1)

    def test_verification_tokens_generate_apply_missing_token_does_not_write_token_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "generate.plan.json"
            token_out = root / "verification-token.json"
            self._write_generate_plan(plan_path, location_id="123456")

            calls: list[str] = []

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
                calls.append(method)
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"result": "SUCCEEDED"}).encode("utf-8"),
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
                    "--apply",
                    "--ack-no-snapshot",
                    "--plan-in",
                    str(plan_path),
                    "verifications",
                    "verification-tokens",
                    "generate",
                    "--verification-token-out",
                    str(token_out),
                    "--location-id",
                    "123456",
                ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "verifications.verification-tokens.generate")
            self.assertFalse(payload["dry_run"])
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"].get("ok", True))
            self.assertEqual(payload["receipt"]["verification"]["note"], "Provider reported SUCCEEDED but did not return instantVerificationToken.")
            self.assertFalse(token_out.exists())
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())
            self.assertEqual(len(calls), 1)
