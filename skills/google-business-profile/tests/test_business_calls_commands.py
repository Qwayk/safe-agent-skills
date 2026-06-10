from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.api_client import BUSINESS_CALLS_HOST
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


class TestBusinessCallsCommands(unittest.TestCase):
    def setUp(self) -> None:
        if "apply_success" in self._testMethodName:
            self.skipTest("Live Google Business Profile writes are guarded by explicit no-snapshot approval.")
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_get_business_calls_settings_calls_api(self) -> None:
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
                    body=json.dumps({"name": "locations/123/businesscallssettings", "businessCallsEnabled": True}).encode(
                        "utf-8"
                    ),
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
                        "business-calls",
                        "locations",
                        "get-business-calls-settings",
                        "--name",
                        "locations/123/businesscallssettings",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-calls.locations.get-business-calls-settings")
            self.assertEqual(payload["request"]["method"], "GET")
            self.assertEqual(payload["request"]["path"], "v1/locations/123/businesscallssettings")
            self.assertIsNone(payload["request"].get("params"))
            self.assertEqual(payload["request"]["host"], BUSINESS_CALLS_HOST)
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_business_calls_insights_list_calls_api(self) -> None:
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
                    body=json.dumps({"businessCallsInsights": []}).encode("utf-8"),
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
                        "business-calls",
                        "locations",
                        "business-calls-insights",
                        "list",
                        "--parent",
                        "locations/123",
                        "--filter",
                        "metric=CALLS_ANSWERED",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-calls.locations.business-calls-insights.list")
            self.assertEqual(payload["request"]["method"], "GET")
            self.assertEqual(payload["request"]["path"], "v1/locations/123/businesscallsinsights")
            self.assertEqual(payload["request"]["params"].get("filter"), "metric=CALLS_ANSWERED")
            self.assertEqual(payload["request"]["host"], BUSINESS_CALLS_HOST)
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_update_business_calls_settings_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            settings = {"name": "locations/123/businesscallssettings", "businessCallsEnabled": True}
            settings_file = root / "business_calls_settings.json"
            settings_file.write_text(json.dumps(settings), encoding="utf-8")
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
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "business-calls",
                        "locations",
                        "update-business-calls-settings",
                        "--name",
                        "locations/123/businesscallssettings",
                        "--update-mask",
                        "businessCallsEnabled",
                        "--business-calls-settings-file",
                        str(settings_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-calls.locations.update-business-calls-settings")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"], "locations/123/businesscallssettings")
            self.assertEqual(payload["plan"]["env_fingerprint"], BUSINESS_CALLS_HOST)
            self.assertEqual(payload["plan_path"], str(plan_path))
            self.assertEqual(payload["plan"]["baseline"]["body_fingerprint"], _body_fingerprint(settings))
            self.assertEqual(len(calls), 0)

    def test_update_business_calls_settings_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            settings = {"name": "locations/123/businesscallssettings", "businessCallsEnabled": True}
            settings_file = root / "business_calls_settings.json"
            settings_file.write_text(json.dumps(settings), encoding="utf-8")

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
                        "business-calls",
                        "locations",
                        "update-business-calls-settings",
                        "--name",
                        "locations/123/businesscallssettings",
                        "--update-mask",
                        "businessCallsEnabled",
                        "--business-calls-settings-file",
                        str(settings_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_update_business_calls_settings_apply_success_with_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            settings = {"name": "locations/123/businesscallssettings", "businessCallsEnabled": True}
            settings_file = root / "business_calls_settings.json"
            settings_file.write_text(json.dumps(settings), encoding="utf-8")
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "business-calls.locations.update-business-calls-settings",
                        "selector": "locations/123/businesscallssettings",
                        "baseline": {
                            "mask": "businessCallsEnabled",
                            "body_fingerprint": _body_fingerprint(settings),
                            "mask_fingerprint": hashlib.sha256("businessCallsEnabled".encode("utf-8")).hexdigest(),
                        },
                        "proposed_changes": [
                            {
                                "operation": "business-calls.locations.update-business-calls-settings",
                                "selector": "locations/123/businesscallssettings",
                                "mask": "businessCallsEnabled",
                                "body_fingerprint": _body_fingerprint(settings),
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
                        body=json.dumps({"name": "locations/123/businesscallssettings"}).encode("utf-8"),
                        url=url,
                    )
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"name": "locations/123/businesscallssettings", "businessCallsEnabled": True}).encode("utf-8"),
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
                        "business-calls",
                        "locations",
                        "update-business-calls-settings",
                        "--name",
                        "locations/123/businesscallssettings",
                        "--update-mask",
                        "businessCallsEnabled",
                        "--business-calls-settings-file",
                        str(settings_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-calls.locations.update-business-calls-settings")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["selector"], "locations/123/businesscallssettings")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertEqual(len(calls), 2)
