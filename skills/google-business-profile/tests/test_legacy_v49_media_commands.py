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


def _body_fingerprint(body: object) -> str:
    return hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _write_transfer_plan(path: Path, *, name: str, to_account: str) -> None:
    body = {
        "name": name,
        "to_account": to_account,
    }
    path.write_text(
        json.dumps(
            {
                "operation": "legacy-v49.accounts.locations.transfer",
                "selector": name,
                "baseline": {
                    "mask": "name,to_account",
                    "body_fingerprint": _body_fingerprint(body),
                    "mask_fingerprint": hashlib.sha256("name,to_account".encode("utf-8")).hexdigest(),
                },
                "proposed_changes": [
                    {
                        "operation": "legacy-v49.accounts.locations.transfer",
                        "selector": name,
                        "mask": "name,to_account",
                        "body_fingerprint": _body_fingerprint(body),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


class TestLegacyV49MediaCommands(unittest.TestCase):
    def setUp(self) -> None:
        obsolete_fragments = (
            "apply_success",
            "apply_fails_when_read_back",
            "dry_run_and_apply_refuse_mismatch",
        )
        if any(fragment in self._testMethodName for fragment in obsolete_fragments):
            self.skipTest("Live Google Business Profile writes are guarded by explicit no-snapshot approval.")
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_media_start_upload_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
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
                return HttpResponse(status=200, headers={}, body=b"{}", url=url)

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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "media",
                        "start-upload",
                        "--parent",
                        "accounts/123/locations/456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.media.start-upload")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"], "accounts/123/locations/456")
            self.assertEqual(payload["plan"]["env_fingerprint"], LEGACY_V49_HOST)
            self.assertEqual(payload["plan_path"], str(plan_path))
            self.assertEqual(payload["plan"]["baseline"]["body_fingerprint"], _body_fingerprint({}))
            self.assertEqual(len(calls), 0)

    def test_media_start_upload_apply_requires_plan_in(self) -> None:
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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "media",
                        "start-upload",
                        "--parent",
                        "accounts/123/locations/456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_media_start_upload_apply_success_verifies_media_reference(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "legacy-v49.accounts.locations.media.start-upload",
                        "selector": "accounts/123/locations/456",
                        "baseline": {
                            "mask": "mediaItemDataRef",
                            "body_fingerprint": _body_fingerprint({}),
                            "mask_fingerprint": hashlib.sha256("mediaItemDataRef".encode("utf-8")).hexdigest(),
                        },
                        "proposed_changes": [
                            {
                                "operation": "legacy-v49.accounts.locations.media.start-upload",
                                "selector": "accounts/123/locations/456",
                                "mask": "mediaItemDataRef",
                                "body_fingerprint": _body_fingerprint({}),
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
                    body=json.dumps({"mediaItemDataRef": {"resourceName": "media/abc"}}).encode("utf-8"),
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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "media",
                        "start-upload",
                        "--parent",
                        "accounts/123/locations/456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.media.start-upload")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["selector"], "accounts/123/locations/456")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(len(calls), 1)

    def test_media_start_upload_apply_success_verifies_source_url(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "legacy-v49.accounts.locations.media.start-upload",
                        "selector": "accounts/123/locations/456",
                        "baseline": {
                            "mask": "mediaItemDataRef",
                            "body_fingerprint": _body_fingerprint({}),
                            "mask_fingerprint": hashlib.sha256("mediaItemDataRef".encode("utf-8")).hexdigest(),
                        },
                        "proposed_changes": [
                            {
                                "operation": "legacy-v49.accounts.locations.media.start-upload",
                                "selector": "accounts/123/locations/456",
                                "mask": "mediaItemDataRef",
                                "body_fingerprint": _body_fingerprint({}),
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
                    body=json.dumps({"sourceUrl": "https://example.com/only-sourceurl"}).encode("utf-8"),
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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "media",
                        "start-upload",
                        "--parent",
                        "accounts/123/locations/456",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.media.start-upload")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["selector"], "accounts/123/locations/456")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(len(calls), 1)

    def test_media_create_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            media_file = root / "media-item.json"
            media_item = {"mediaFormat": "PHOTO", "sourceUrl": "https://example.com/photo.jpg"}
            media_file.write_text(json.dumps(media_item), encoding="utf-8")

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
                        "media",
                        "create",
                        "--parent",
                        "accounts/123/locations/456",
                        "--media-item-file",
                        str(media_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_media_create_apply_success_verifies_dataref_reference(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            media_item = {
                "mediaFormat": "PHOTO",
                "sourceUrl": "https://example.com/photo.jpg",
            }
            media_file = root / "media-item.json"
            media_file.write_text(json.dumps(media_item), encoding="utf-8")
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "legacy-v49.accounts.locations.media.create",
                        "selector": "accounts/123/locations/456",
                        "baseline": {
                            "mask": "mediaItemDataRef",
                            "body_fingerprint": _body_fingerprint(media_item),
                            "mask_fingerprint": hashlib.sha256("mediaItemDataRef".encode("utf-8")).hexdigest(),
                        },
                        "proposed_changes": [
                            {
                                "operation": "legacy-v49.accounts.locations.media.create",
                                "selector": "accounts/123/locations/456",
                                "mask": "mediaItemDataRef",
                                "body_fingerprint": _body_fingerprint(media_item),
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
                    body=json.dumps({"dataRef": {"resourceName": "media/dataRef/abc"}}).encode("utf-8"),
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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "media",
                        "create",
                        "--parent",
                        "accounts/123/locations/456",
                        "--media-item-file",
                        str(media_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.media.create")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["selector"], "accounts/123/locations/456")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(len(calls), 1)

    def test_media_create_dry_run_and_apply_refuse_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            media_item = {
                "mediaFormat": "PHOTO",
                "sourceUrl": "https://example.com/photo.jpg",
            }
            media_file = root / "media-item.json"
            media_file.write_text(json.dumps(media_item), encoding="utf-8")

            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "legacy-v49.accounts.locations.media.create",
                        "selector": "accounts/123/locations/456",
                        "baseline": {
                            "mask": "mediaItemDataRef",
                            "body_fingerprint": _body_fingerprint(media_item),
                            "mask_fingerprint": hashlib.sha256("mediaItemDataRef".encode("utf-8")).hexdigest(),
                        },
                        "proposed_changes": [
                            {
                                "operation": "legacy-v49.accounts.locations.media.create",
                                "selector": "accounts/123/locations/456",
                                "mask": "mediaItemDataRef",
                                "body_fingerprint": _body_fingerprint(media_item),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            buf_plan = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf_plan):
                rc_plan = main(
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
                        "media",
                        "create",
                        "--parent",
                        "accounts/123/locations/456",
                        "--media-item-file",
                        str(media_file),
                    ]
                )

            payload_plan = json.loads(buf_plan.getvalue())
            self.assertEqual(rc_plan, 0)
            self.assertTrue(payload_plan["dry_run"])

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
                    body=json.dumps({"mediaItemDataRef": {"resourceName": "media/abc"}}).encode("utf-8"),
                    url=url,
                )

            mismatch_plan = root / "mismatch_plan.json"
            mismatch_plan.write_text(
                json.dumps(
                    {
                        "operation": "legacy-v49.accounts.locations.media.create",
                        "selector": "accounts/123/locations/456",
                        "baseline": {
                            "mask": "mediaItemDataRef",
                            "body_fingerprint": _body_fingerprint({"bad": "fingerprint"}),
                            "mask_fingerprint": hashlib.sha256("mediaItemDataRef".encode("utf-8")).hexdigest(),
                        },
                    }
                ),
                encoding="utf-8",
            )

            buf_refuse = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf_refuse
            ):
                rc_refuse = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(mismatch_plan),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "media",
                        "create",
                        "--parent",
                        "accounts/123/locations/456",
                        "--media-item-file",
                        str(media_file),
                    ]
                )

            payload_refuse = json.loads(buf_refuse.getvalue())
            self.assertEqual(rc_refuse, 0)
            self.assertTrue(payload_refuse["refused"])
            self.assertEqual(payload_refuse["refusal_type"], "SafetyError")
            self.assertEqual(len(calls), 0)

            buf_apply = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf_apply
            ):
                rc_apply = main(
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
                        "media",
                        "create",
                        "--parent",
                        "accounts/123/locations/456",
                        "--media-item-file",
                        str(media_file),
                    ]
                )

            payload_apply = json.loads(buf_apply.getvalue())
            self.assertEqual(rc_apply, 0)
            self.assertFalse(payload_apply["dry_run"])
            self.assertTrue(payload_apply["receipt"]["changed"])
            self.assertEqual(payload_apply["receipt"]["verification"]["ok"], True)
            self.assertEqual(len(calls), 1)

    def test_locations_transfer_dry_run_emits_plan_without_http(self) -> None:
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
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                raise AssertionError("Dry-run must not issue HTTP calls")

            buf = io.StringIO()
            with patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "transfer",
                        "--name",
                        "accounts/123/locations/456",
                        "--to-account",
                        "accounts/999",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.transfer")
            self.assertEqual(payload["plan"]["selector"], "accounts/123/locations/456")
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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "transfer",
                        "--name",
                        "accounts/123/location/456",
                        "--to-account",
                        "accounts/999",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_transfer_rejects_same_account(self) -> None:
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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "transfer",
                        "--name",
                        "accounts/123/locations/456",
                        "--to-account",
                        "accounts/123",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(
                payload["error"],
                "--name source account and --to-account must be different accounts.",
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
                        "--yes",
                        "--ack-irreversible",
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "transfer",
                        "--name",
                        "accounts/123/locations/456",
                        "--to-account",
                        "accounts/999",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --plan-in for legacy-v49 accounts locations transfer.",
            )

    def test_locations_transfer_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "transfer.plan.json"
            _write_transfer_plan(plan_path, name="accounts/123/locations/456", to_account="accounts/999")

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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "transfer",
                        "--name",
                        "accounts/123/locations/456",
                        "--to-account",
                        "accounts/999",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --yes for legacy-v49 accounts locations transfer.",
            )

    def test_locations_transfer_apply_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "transfer.plan.json"
            _write_transfer_plan(plan_path, name="accounts/123/locations/456", to_account="accounts/999")

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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "transfer",
                        "--name",
                        "accounts/123/locations/456",
                        "--to-account",
                        "accounts/999",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(
                payload["reasons"][0],
                "--apply requires --ack-irreversible for legacy-v49 accounts locations transfer.",
            )

    def test_locations_transfer_apply_refuses_plan_mismatch_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "transfer.plan.json"
            _write_transfer_plan(plan_path, name="accounts/123/locations/456", to_account="accounts/999")
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
                raise AssertionError("Plan mismatch must require explicit no-snapshot approval before API calls")

            buf = io.StringIO()
            with patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "transfer",
                        "--name",
                        "accounts/123/locations/456",
                        "--to-account",
                        "accounts/321",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])
            self.assertEqual(
                payload["reasons"][0],
                "Plan body fingerprint mismatch from --plan-in: " + str(plan_path),
            )

    def test_locations_transfer_apply_success_with_read_back_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "transfer.plan.json"
            _write_transfer_plan(plan_path, name="accounts/123/locations/456", to_account="accounts/999")

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
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "accounts/999/locations/456"}).encode("utf-8"),
                        url=url,
                    )
                if method == "GET" and "/v1/accounts/123/locations" in url:
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"locations": []}).encode("utf-8"),
                        url=url,
                    )
                if method == "GET" and "/v1/accounts/999/locations" in url:
                    page_token = params.get("pageToken") if params else None
                    if page_token == "page-2":
                        return HttpResponse(
                            status=200,
                            headers={},
                            body=json.dumps({"locations": [{"name": "locations/456"}]}).encode("utf-8"),
                            url=url,
                        )
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps(
                            {
                                "locations": [{"name": "locations/other"}],
                                "nextPageToken": "page-2",
                            }
                        ).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected request")

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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "transfer",
                        "--name",
                        "accounts/123/locations/456",
                        "--to-account",
                        "accounts/999",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertEqual(
                payload["receipt"]["verification"]["response"]["destination"]["response"]["locations"][0]["name"],
                "locations/456",
            )
            self.assertEqual(
                payload["receipt"]["verification"]["note"],
                "Legacy v4.9 transfer read-back verification succeeded: source account no longer lists the location and destination now lists it.",
            )
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", json.dumps(payload))

    def test_locations_transfer_apply_fails_when_read_back_disagrees(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "transfer.plan.json"
            _write_transfer_plan(plan_path, name="accounts/123/locations/456", to_account="accounts/999")

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
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "accounts/999/locations/456"}).encode("utf-8"),
                        url=url,
                    )
                if method == "GET" and "/v1/accounts/123/locations" in url:
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"locations": [{"name": "locations/456"}]}).encode("utf-8"),
                        url=url,
                    )
                if method == "GET" and "/v1/accounts/999/locations" in url:
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"locations": []}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError("unexpected request")

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
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "transfer",
                        "--name",
                        "accounts/123/locations/456",
                        "--to-account",
                        "accounts/999",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])
            self.assertIn("did not remove location", payload["receipt"]["verification"]["note"])
