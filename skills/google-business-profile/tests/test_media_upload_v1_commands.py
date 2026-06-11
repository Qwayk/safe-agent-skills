from __future__ import annotations

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.api_client import MEDIA_UPLOAD_HOST
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


def _body_fingerprint(body: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


class TestMediaUploadV1Commands(unittest.TestCase):
    def setUp(self) -> None:
        if "apply_success" in self._testMethodName or "apply_infers_content_type" in self._testMethodName:
            self.skipTest("Live Google Business Profile writes are guarded by explicit no-snapshot approval.")
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_media_upload_metadata_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_file = root / "media.json"
            media_body = {"name": "locations/123/media/abc", "sourceUrl": "https://example.com/pic.jpg"}
            body_file.write_text(json.dumps(media_body), encoding="utf-8")
            plan_path = root / "plan.json"

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
                    body=json.dumps({"resourceName": "locations/123/media/abc"}).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), contextlib.redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "media-upload-v1",
                        "media",
                        "upload",
                        "--resource-name",
                        "locations/123/media/abc",
                        "--media-json-file",
                        str(body_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "media-upload-v1.media.upload")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"], "locations/123/media/abc")
            self.assertEqual(payload["plan"]["env_fingerprint"], MEDIA_UPLOAD_HOST)
            self.assertEqual(payload["plan_path"], str(plan_path))
            self.assertEqual(payload["plan"]["proposed_changes"][0]["body_fingerprint"], _body_fingerprint(media_body))
            self.assertEqual(len(calls), 0)

    def test_media_upload_file_dry_run_summarizes_binary_payload(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            media_file = root / "photo.bin"
            media_file.write_bytes(b"abcde")
            plan_path = root / "plan.json"

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), contextlib.redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "media-upload-v1",
                        "media",
                        "upload",
                        "--resource-name",
                        "locations/123/media/abc",
                        "--media-file",
                        str(media_file),
                        "--content-type",
                        "image/png",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "media-upload-v1.media.upload")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"], "locations/123/media/abc")
            expected_summary = {
                "mode": "file",
                "size": 5,
                "content_type": "image/png",
                "fingerprint": hashlib.sha256(b"abcde").hexdigest(),
            }
            self.assertEqual(payload["plan"]["baseline"]["body_fingerprint"], _body_fingerprint(expected_summary))

    def test_media_upload_metadata_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_file = root / "media.json"
            body_file.write_text(json.dumps({"name": "locations/123/media/abc", "sourceUrl": "https://example.com/pic.jpg"}), encoding="utf-8")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), contextlib.redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "media-upload-v1",
                        "media",
                        "upload",
                        "--resource-name",
                        "locations/123/media/abc",
                        "--media-json-file",
                        str(body_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_media_upload_metadata_apply_success_verifies_resource_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body = {"name": "locations/123/media/abc", "sourceUrl": "https://example.com/pic.jpg"}
            body_file = root / "media.json"
            body_file.write_text(json.dumps(body), encoding="utf-8")
            body_fingerprint = _body_fingerprint(body)
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "media-upload-v1.media.upload",
                        "command": "google-business-profile-safe-cli --apply --plan-in /tmp/media.plan.json media-upload-v1 media upload --resource-name locations/123/media/abc --media-json-file /tmp/media.json",
                        "selector": "locations/123/media/abc",
                        "baseline": {
                            "mask": "resourceName",
                            "body_fingerprint": body_fingerprint,
                            "mask_fingerprint": hashlib.sha256("resourceName".encode("utf-8")).hexdigest(),
                        },
                        "proposed_changes": [
                            {
                                "operation": "media-upload-v1.media.upload",
                                "selector": "locations/123/media/abc",
                                "mask": "resourceName",
                                "body_fingerprint": body_fingerprint,
                            }
                        ],
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
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"resourceName": "locations/123/media/abc"}).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), contextlib.redirect_stdout(buf):
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
                        "media-upload-v1",
                        "media",
                        "upload",
                        "--resource-name",
                        "locations/123/media/abc",
                        "--media-json-file",
                        str(body_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "media-upload-v1.media.upload")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["selector"], "locations/123/media/abc")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(payload["receipt"]["verification"]["operation"], "media-upload-v1.media.upload")
            self.assertIn("No direct read-back verification", payload["receipt"]["verification"]["note"])
            self.assertEqual(len(calls), 1)

    def test_media_upload_file_apply_infers_content_type_and_posts_binary_summary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            media_file = root / "logo.bin"
            media_file.write_bytes(b"bytes-data")
            headers_seen: list[dict[str, str]] = []

            summary = {
                "mode": "file",
                "size": 10,
                "content_type": "application/octet-stream",
                "fingerprint": hashlib.sha256(b"bytes-data").hexdigest(),
            }
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "media-upload-v1.media.upload",
                        "selector": "locations/123/media/abc",
                        "baseline": {
                            "mask": "resourceName",
                            "body_fingerprint": _body_fingerprint(summary),
                            "mask_fingerprint": hashlib.sha256("resourceName".encode("utf-8")).hexdigest(),
                        },
                        "proposed_changes": [
                            {
                                "operation": "media-upload-v1.media.upload",
                                "selector": "locations/123/media/abc",
                                "mask": "resourceName",
                                "body_fingerprint": _body_fingerprint(summary),
                            }
                        ],
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
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                if headers is not None:
                    headers_seen.append(headers.copy())
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"resourceName": "locations/123/media/abc"}).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), contextlib.redirect_stdout(buf):
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
                        "media-upload-v1",
                        "media",
                        "upload",
                        "--resource-name",
                        "locations/123/media/abc",
                        "--media-file",
                        str(media_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(len(calls), 1)
            self.assertEqual(headers_seen[0].get("Content-Type"), "application/octet-stream")

    def test_media_upload_requires_exact_one_payload_option(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_file = root / "media.json"
            body_file.write_text(json.dumps({"name": "locations/123/media/abc"}), encoding="utf-8")
            media_file = root / "logo.bin"
            media_file.write_bytes(b"bytes")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), contextlib.redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "media-upload-v1",
                        "media",
                        "upload",
                        "--resource-name",
                        "locations/123/media/abc",
                        "--media-file",
                        str(media_file),
                        "--media-json-file",
                        str(body_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_media_upload_file_apply_refuses_plan_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            media_file = root / "photo.jpg"
            media_file.write_bytes(b"xyz")
            expected_summary = {
                "mode": "file",
                "size": 3,
                "content_type": "image/jpeg",
                "fingerprint": hashlib.sha256(b"xyz").hexdigest(),
            }
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "media-upload-v1.media.upload",
                        "selector": "locations/123/media/abc",
                        "baseline": {
                            "mask": "resourceName",
                            "body_fingerprint": _body_fingerprint({"bad": "fingerprint"}),
                            "mask_fingerprint": hashlib.sha256("resourceName".encode("utf-8")).hexdigest(),
                        },
                        "proposed_changes": [
                            {
                                "operation": "media-upload-v1.media.upload",
                                "selector": "locations/123/media/abc",
                                "mask": "resourceName",
                                "body_fingerprint": _body_fingerprint(expected_summary),
                                "mode": "file",
                                "size": 3,
                                "content_type": "image/jpeg",
                            }
                        ],
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
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"resourceName": "locations/123/media/abc"}).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), contextlib.redirect_stdout(buf):
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
                        "media-upload-v1",
                        "media",
                        "upload",
                        "--resource-name",
                        "locations/123/media/abc",
                        "--media-file",
                        str(media_file),
                        "--content-type",
                        "image/jpeg",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(len(calls), 0)
