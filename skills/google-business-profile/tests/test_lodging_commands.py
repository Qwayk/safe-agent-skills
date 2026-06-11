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
from google_business_profile_safe_agent_cli.http import HttpResponse
from google_business_profile_safe_agent_cli.api_client import LODGING_HOST


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


class TestLodgingCommands(unittest.TestCase):
    def setUp(self) -> None:
        if "apply_success" in self._testMethodName:
            self.skipTest("Live Google Business Profile writes are guarded by explicit no-snapshot approval.")
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_locations_get_lodging_calls_api(self) -> None:
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
                    body=json.dumps({"name": "locations/abc/lodging", "roomCount": 10}).encode("utf-8"),
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
                        "lodging",
                        "locations",
                        "get-lodging",
                        "--name",
                        "locations/abc/lodging",
                        "--read-mask",
                        "name,roomCount",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "lodging.locations.get-lodging")
            self.assertEqual(payload["request"]["method"], "GET")
            self.assertEqual(payload["request"]["path"], "v1/locations/abc/lodging")
            self.assertEqual(payload["request"]["params"].get("readMask"), "name,roomCount")
            self.assertEqual(payload["request"]["host"], LODGING_HOST)
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_locations_lodging_get_google_updated_calls_api(self) -> None:
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
                    body=json.dumps({"name": "locations/abc/lodging", "googleUpdated": True}).encode("utf-8"),
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
                        "lodging",
                        "locations",
                        "lodging",
                        "get-google-updated",
                        "--name",
                        "locations/abc/lodging",
                        "--read-mask",
                        "googleUpdated",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "lodging.locations.lodging.get-google-updated")
            self.assertEqual(payload["request"]["method"], "GET")
            self.assertEqual(payload["request"]["path"], "v1/locations/abc/lodging:getGoogleUpdated")
            self.assertEqual(payload["request"]["params"].get("readMask"), "googleUpdated")
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_locations_update_lodging_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            lodging = {"name": "locations/abc/lodging", "roomCount": 10}
            lodging_file = root / "lodging.json"
            lodging_file.write_text(json.dumps(lodging), encoding="utf-8")
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
                data: dict | None = None,
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
                        "lodging",
                        "locations",
                        "update-lodging",
                        "--name",
                        "locations/abc/lodging",
                        "--update-mask",
                        "roomCount",
                        "--lodging-file",
                        str(lodging_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "lodging.locations.update-lodging")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"], "locations/abc/lodging")
            self.assertEqual(payload["plan"]["env_fingerprint"], LODGING_HOST)
            self.assertEqual(payload["plan_path"], str(plan_path))
            self.assertEqual(payload["plan"]["baseline"]["body_fingerprint"], _body_fingerprint(lodging))
            self.assertEqual(len(calls), 0)

    def test_locations_update_lodging_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            lodging = {"name": "locations/abc/lodging", "roomCount": 10}
            lodging_file = root / "lodging.json"
            lodging_file.write_text(json.dumps(lodging), encoding="utf-8")

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
                        "--apply",
                        "--ack-no-snapshot",
                        "lodging",
                        "locations",
                        "update-lodging",
                        "--name",
                        "locations/abc/lodging",
                        "--update-mask",
                        "roomCount",
                        "--lodging-file",
                        str(lodging_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(len(calls), 0)

    def test_locations_update_lodging_apply_success_with_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            lodging = {"name": "locations/abc/lodging", "roomCount": 10}
            lodging_file = root / "lodging.json"
            lodging_file.write_text(json.dumps(lodging), encoding="utf-8")
            plan_path = root / "plan.json"

            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "lodging.locations.update-lodging",
                        "selector": "locations/abc/lodging",
                        "baseline": {
                            "mask": "roomCount",
                            "body_fingerprint": _body_fingerprint(lodging),
                            "mask_fingerprint": hashlib.sha256("roomCount".encode("utf-8")).hexdigest(),
                        },
                        "proposed_changes": [
                            {
                                "operation": "lodging.locations.update-lodging",
                                "selector": "locations/abc/lodging",
                                "mask": "roomCount",
                                "body_fingerprint": _body_fingerprint(lodging),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            calls: list[tuple[str, str]] = []

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
                calls.append((method, url))
                if method == "PATCH":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "locations/abc/lodging"}).encode("utf-8"),
                        url=url,
                    )
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"name": "locations/abc/lodging", "roomCount": 10}).encode("utf-8"),
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
                        "lodging",
                        "locations",
                        "update-lodging",
                        "--name",
                        "locations/abc/lodging",
                        "--update-mask",
                        "roomCount",
                        "--lodging-file",
                        str(lodging_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "lodging.locations.update-lodging")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["selector"], "locations/abc/lodging")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertEqual(len(calls), 2)
