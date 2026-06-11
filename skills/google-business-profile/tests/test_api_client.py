from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.api_client import (
    ACCOUNT_MANAGEMENT_HOST,
    BUSINESS_INFORMATION_HOST,
    BUSINESS_CALLS_HOST,
    NOTIFICATIONS_HOST,
    MEDIA_UPLOAD_HOST,
    LEGACY_V49_HOST,
    PERFORMANCE_HOST,
    PLACE_ACTIONS_HOST,
    LODGING_HOST,
    VERIFICATIONS_HOST,
    GoogleBusinessProfileApiClient,
)
from google_business_profile_safe_agent_cli.config import Config
from google_business_profile_safe_agent_cli.http import HttpResponse


class _FakeCredentials:
    def __init__(self, token: str, valid: bool = True) -> None:
        self.token = token
        self.valid = valid
        self.refreshed = False

    def refresh(self, request: object) -> None:  # noqa: ANN001
        self.refreshed = True
        self.valid = True
        self.token = "refreshed-token"


class TestGoogleBusinessProfileApiClient(unittest.TestCase):
    def _build_config(self) -> Config:
        return Config(
            base_url="https://mybusinessbusinessinformation.googleapis.com",
            oauth_client_secrets_file=None,
            oauth_scopes=["https://www.googleapis.com/auth/business.manage"],
            timeout_s=30.0,
        )

    def test_account_management_host_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

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
                request_data["url"] = url
                request_data["headers"] = headers or {}
                request_data["params"] = params
                request_data["body"] = json_body
                request_data["data"] = data
                request_data["method"] = method
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"ok": true}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="original-token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                response, request = client.list_accounts(parent_account="accounts/1")

            self.assertEqual(response["ok"], True)
            self.assertIn(ACCOUNT_MANAGEMENT_HOST, str(request["host"]))
            self.assertIn(ACCOUNT_MANAGEMENT_HOST, str(request_data["url"]))
            self.assertEqual(request_data["headers"]["Authorization"], "Bearer original-token")
            self.assertNotIn("original-token", json.dumps(request))

    def test_create_account_posts_to_account_management_host(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {"accountName": "Test Business", "type": "LOCATION_GROUP", "primaryOwner": "accounts/999"}

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"name":"accounts/created"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.create_account(body=body)

            self.assertEqual(request["method"], "POST")
            self.assertEqual(request["path"], "v1/accounts")
            self.assertEqual((request.get("params") or {}).get("validateOnly"), None)
            self.assertEqual(request["body"], body)
            self.assertEqual(str(request["host"]), ACCOUNT_MANAGEMENT_HOST)

    def test_patch_account_uses_update_mask_and_validate_only(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {"name": "accounts/123", "accountName": "New Name"}

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"name":"accounts/123","accountName":"New Name"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.patch_account(name="accounts/123", update_mask="accountName", body=body, validate_only=True)

            self.assertEqual(request["method"], "PATCH")
            self.assertEqual(request["path"], "v1/accounts/123")
            self.assertEqual((request["params"] or {}).get("updateMask"), "accountName")
            self.assertEqual((request["params"] or {}).get("validateOnly"), True)
            self.assertEqual(request["body"], body)

    def test_create_account_admin_posts_to_parent_admins_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {"admin": "accounts/222", "role": "OWNER"}

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"name":"accounts/123/admins/admin-456"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                response, request = client.create_account_admin(parent="accounts/123", body=body)

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(request_data["url"], str(request.get("host")) + "/v1/accounts/123/admins")
            self.assertEqual(request["path"], "v1/accounts/123/admins")
            self.assertEqual(request["body"], body)
            self.assertEqual(response["name"], "accounts/123/admins/admin-456")

    def test_patch_account_admin_uses_update_mask_and_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {"name": "accounts/123/admins/admin-456", "role": "MANAGER"}

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"name":"accounts/123/admins/admin-456","role":"MANAGER"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.patch_account_admin(
                    name="accounts/123/admins/admin-456",
                    update_mask="role",
                    body=body,
                )

            self.assertEqual(request_data["method"], "PATCH")
            self.assertEqual(request["path"], "v1/accounts/123/admins/admin-456")
            self.assertEqual((request["params"] or {}).get("updateMask"), "role")
            self.assertEqual(request_data["body"], body)

    def test_delete_account_admin_allows_empty_response_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b"",
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                response, request = client.delete_account_admin(name="accounts/123/admins/admin-456")

            self.assertEqual(request_data["method"], "DELETE")
            self.assertEqual(request["path"], "v1/accounts/123/admins/admin-456")
            self.assertEqual(response, {})

    def test_refreshes_credentials_when_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            captured: dict[str, object] = {}
            creds = _FakeCredentials(token="expired-token", valid=False)

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
                captured["url"] = url
                captured["headers"] = headers or {}
                return HttpResponse(status=200, headers={}, body=b'{"ok": true}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=creds,
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.get_account(name="accounts/7")

            self.assertTrue(creds.refreshed)
            self.assertEqual(captured["headers"]["Authorization"], "Bearer refreshed-token")
            self.assertIn(ACCOUNT_MANAGEMENT_HOST, str(request["host"]))

    def test_business_information_host_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

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
                request_data["url"] = url
                request_data["headers"] = headers or {}
                return HttpResponse(status=200, headers={}, body=b'{"ok": true}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="bi-token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.list_categories(
                    region_code="US",
                    language_code="en-US",
                    view="BASIC",
                    filter=None,
                    page_size=None,
                    page_token=None,
                )

            self.assertIn(BUSINESS_INFORMATION_HOST, str(request_data["url"]))
            self.assertIn(BUSINESS_INFORMATION_HOST, str(request["host"]))
            self.assertEqual(request_data["headers"]["Authorization"], "Bearer bi-token")

    def test_patch_location_uses_business_information_update_mask_and_validate_only(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {"title": "Coffee"}

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(status=200, headers={}, body=b'{"ok": true}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.patch_location(
                    name="locations/abc",
                    update_mask="title",
                    body=body,
                    validate_only=True,
                )

            self.assertEqual(request["method"], "PATCH")
            self.assertEqual(request["path"], "v1/locations/abc")
            self.assertEqual((request["params"] or {}).get("updateMask"), "title")
            self.assertEqual((request["params"] or {}).get("validateOnly"), True)
            self.assertEqual(request["body"], body)

    def test_create_location_uses_parent_and_optional_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {"title": "Coffee"}

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                request_data["headers"] = headers or {}
                return HttpResponse(status=200, headers={}, body=b'{"name":"locations/new"}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.create_location(
                    parent="accounts/abc",
                    body=body,
                    validate_only=True,
                    request_id="request-1",
                )

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(request_data["url"], str(BUSINESS_INFORMATION_HOST) + "/v1/accounts/abc/locations")
            self.assertEqual((request_data["params"] or {}).get("validateOnly"), True)
            self.assertEqual((request_data["params"] or {}).get("requestId"), "request-1")
            self.assertEqual(request_data["body"], body)

    def test_update_attributes_uses_attribute_mask(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {
                "name": "locations/abc/attributes",
                "attributes": [
                    {
                        "name": "attributes/takeout",
                        "values": [True],
                    }
                ],
            }

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(status=200, headers={}, body=b'{"ok": true}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.update_attributes(
                    name="locations/abc/attributes",
                    attribute_mask="attributes/takeout",
                    body=body,
                )

            self.assertEqual(request["method"], "PATCH")
            self.assertEqual(request["path"], "v1/locations/abc/attributes")
            self.assertEqual((request["params"] or {}).get("attributeMask"), "attributes/takeout")
            self.assertEqual(request["body"], body)

    def test_delete_location_uses_delete_with_empty_success_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["json_body"] = json_body
                return HttpResponse(status=200, headers={}, body=b"", url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                response, request = client.delete_location(name="locations/abc")

            self.assertEqual(response, {})
            self.assertEqual(request["method"], "DELETE")
            self.assertEqual(request["path"], "v1/locations/abc")
            self.assertIsNone(request_data.get("json_body"))
            self.assertEqual(request_data["url"], str(BUSINESS_INFORMATION_HOST) + "/v1/locations/abc")

    def test_get_notification_setting_uses_notifications_host(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["headers"] = headers or {}
                return HttpResponse(status=200, headers={}, body=b'{"name":"accounts/123/notificationSetting"}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.get_notification_setting(name="accounts/123/notificationSetting")

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request["path"], "v1/accounts/123/notificationSetting")
            self.assertEqual(request["host"], NOTIFICATIONS_HOST)
            self.assertEqual(request_data["url"], str(NOTIFICATIONS_HOST) + "/v1/accounts/123/notificationSetting")

    def test_update_notification_setting_uses_patch_with_mask(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {"name": "accounts/123/notificationSetting", "notificationSettings": []}

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(status=200, headers={}, body=b'{"ok": true}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.update_notification_setting(
                    name="accounts/123/notificationSetting",
                    update_mask="emailNotifications,notificationType",
                    body=body,
                )

            self.assertEqual(request_data["method"], "PATCH")
            self.assertEqual(request["path"], "v1/accounts/123/notificationSetting")
            self.assertEqual((request["params"] or {}).get("updateMask"), "emailNotifications,notificationType")
            self.assertEqual(request["body"], body)
            self.assertEqual(request["host"], NOTIFICATIONS_HOST)

    def test_upload_media_metadata_uses_media_upload_metadata_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {
                "resourceName": "locations/123/media/abc",
                "sourceUrl": "https://example.com/pic.jpg",
            }

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
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                request_data["headers"] = headers or {}
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"resourceName":"locations/123/media/abc"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.upload_media_metadata(
                    resource_name="locations/123/media/abc",
                    body=body,
                )

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(
                request_data["url"],
                str(MEDIA_UPLOAD_HOST) + "/v1/media/locations/123/media/abc",
            )
            self.assertEqual(request["path"], "v1/media/locations/123/media/abc")
            self.assertEqual(request["body"], body)
            self.assertEqual(request["host"], MEDIA_UPLOAD_HOST)

    def test_upload_media_file_uses_upload_path_and_upload_type(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            request_body = {"mode": "file", "size": 4, "content_type": "image/jpeg", "fingerprint": "digest"}

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
                request_data["data"] = data
                request_data["headers"] = headers or {}
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"resourceName":"locations/123/media/abc"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.upload_media_file(
                    resource_name="locations/123/media/abc",
                    data=b"abcd",
                    content_type="image/jpeg",
                    request_body=request_body,
                )

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(request_data["url"], str(MEDIA_UPLOAD_HOST) + "/upload/v1/media/locations/123/media/abc")
            self.assertEqual((request_data["params"] or {}).get("upload_type"), "media")
            self.assertEqual(request_data["headers"].get("Content-Type"), "image/jpeg")
            self.assertEqual(request_data["data"], b"abcd")
            self.assertEqual(request["path"], "upload/v1/media/locations/123/media/abc")
            self.assertEqual(request["body"], request_body)
            self.assertEqual(request["host"], MEDIA_UPLOAD_HOST)

    def test_get_lodging_uses_lodging_host_and_read_mask(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                request_data["headers"] = headers or {}
                return HttpResponse(status=200, headers={}, body=b'{"name":"locations/abc"}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.get_lodging(name="locations/abc/lodging", read_mask="name,websites")

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(LODGING_HOST) + "/v1/locations/abc/lodging")
            self.assertEqual(request["host"], LODGING_HOST)
            self.assertEqual((request["params"] or {}).get("readMask"), "name,websites")

    def test_update_lodging_uses_patch_mask_and_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {"name": "locations/abc", "wifi": True}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(status=200, headers={}, body=b'{"name":"locations/abc"}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.update_lodging(name="locations/abc/lodging", update_mask="wifi", body=body)

            self.assertEqual(request_data["method"], "PATCH")
            self.assertEqual(request_data["url"], str(LODGING_HOST) + "/v1/locations/abc/lodging")
            self.assertEqual((request["params"] or {}).get("updateMask"), "wifi")
            self.assertEqual(request["body"], body)
            self.assertEqual(request["host"], LODGING_HOST)

    def test_get_lodging_google_updated_uses_lodging_host_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(status=200, headers={}, body=b'{"name":"locations/abc"}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.get_lodging_google_updated(name="locations/abc/lodging", read_mask="googleUpdated")

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(LODGING_HOST) + "/v1/locations/abc/lodging:getGoogleUpdated")
            self.assertEqual(request["host"], LODGING_HOST)
            self.assertEqual((request["params"] or {}).get("readMask"), "googleUpdated")

    def test_get_business_calls_settings_uses_business_calls_host_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                request_data["headers"] = headers or {}
                return HttpResponse(status=200, headers={}, body=b'{"name":"locations/abc/businesscallssettings"}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.get_business_calls_settings(
                    name="locations/abc/businesscallssettings",
                )

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(BUSINESS_CALLS_HOST) + "/v1/locations/abc/businesscallssettings")
            self.assertEqual(request["host"], BUSINESS_CALLS_HOST)
            self.assertIsNone(request.get("params"))

    def test_update_business_calls_settings_uses_patch_mask_and_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {"name": "locations/abc/businesscallssettings", "businessCallsEnabled": True}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(status=200, headers={}, body=b'{"name":"locations/abc/businesscallssettings"}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.update_business_calls_settings(
                    name="locations/abc/businesscallssettings",
                    update_mask="businessCallsEnabled",
                    body=body,
                )

            self.assertEqual(request_data["method"], "PATCH")
            self.assertEqual(request_data["url"], str(BUSINESS_CALLS_HOST) + "/v1/locations/abc/businesscallssettings")
            self.assertEqual((request["params"] or {}).get("updateMask"), "businessCallsEnabled")
            self.assertEqual(request["body"], body)
            self.assertEqual(request["host"], BUSINESS_CALLS_HOST)

    def test_list_business_calls_insights_uses_parent_and_optional_paging(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["headers"] = headers or {}
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"businessCallsInsights": []}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.list_business_calls_insights(
                    parent="locations/abc",
                    page_size=20,
                    page_token="page-token",
                    filter="metric=CALLS_ANSWERED",
                )

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(BUSINESS_CALLS_HOST) + "/v1/locations/abc/businesscallsinsights")
            self.assertEqual(request["host"], BUSINESS_CALLS_HOST)
            self.assertEqual((request["params"] or {}).get("pageSize"), 20)
            self.assertEqual((request["params"] or {}).get("pageToken"), "page-token")
            self.assertEqual((request["params"] or {}).get("filter"), "metric=CALLS_ANSWERED")

    def test_fetch_multi_daily_metrics_time_series_uses_performance_host_path_and_query_parts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
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
                    body=(
                        b'{"multiDailyMetricTimeSeries":[{"dailyMetricTimeSeries":[{"dailyMetric":"DAILY_ORDERS",'
                        b'"timeSeries":{"datedValues":[{"date":{"year":2025,"month":1,"day":1},"value":"8"}]}}]}]}'
                    ),
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.fetch_multi_daily_metrics_time_series(
                    location="locations/123",
                    daily_metrics=["DAILY_ORDERS", "DAILY_VIEWS"],
                    daily_range_start_year=2025,
                    daily_range_start_month=1,
                    daily_range_start_day=1,
                    daily_range_end_year=2025,
                    daily_range_end_month=1,
                    daily_range_end_day=31,
                )

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(PERFORMANCE_HOST) + "/v1/locations/123:fetchMultiDailyMetricsTimeSeries")
            self.assertEqual(request["host"], PERFORMANCE_HOST)
            self.assertEqual(request["path"], "v1/locations/123:fetchMultiDailyMetricsTimeSeries")
            self.assertEqual((request["params"] or {}).get("dailyMetrics"), ["DAILY_ORDERS", "DAILY_VIEWS"])
            self.assertEqual((request["params"] or {}).get("dailyRange.startDate.year"), 2025)
            self.assertEqual((request["params"] or {}).get("dailyRange.startDate.month"), 1)
            self.assertEqual((request["params"] or {}).get("dailyRange.startDate.day"), 1)
            self.assertEqual((request["params"] or {}).get("dailyRange.endDate.year"), 2025)
            self.assertEqual((request["params"] or {}).get("dailyRange.endDate.month"), 1)
            self.assertEqual((request["params"] or {}).get("dailyRange.endDate.day"), 31)

    def test_get_daily_metrics_time_series_uses_required_daily_metric_and_dates(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
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
                    body=b'{"timeSeries":{"datedValues":[{"date":{"year":2025,"month":1,"day":1},"value":"8"}]}}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.get_daily_metrics_time_series(
                    name="locations/123",
                    daily_metric="DAILY_ORDERS",
                    daily_range_start_year=2025,
                    daily_range_start_month=1,
                    daily_range_start_day=1,
                    daily_range_end_year=2025,
                    daily_range_end_month=1,
                    daily_range_end_day=31,
                )

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(PERFORMANCE_HOST) + "/v1/locations/123:getDailyMetricsTimeSeries")
            self.assertEqual(request["host"], PERFORMANCE_HOST)
            self.assertEqual(request["path"], "v1/locations/123:getDailyMetricsTimeSeries")
            self.assertEqual((request["params"] or {}).get("dailyMetric"), "DAILY_ORDERS")
            self.assertEqual((request["params"] or {}).get("dailyRange.startDate.year"), 2025)
            self.assertEqual((request["params"] or {}).get("dailyRange.startDate.month"), 1)
            self.assertEqual((request["params"] or {}).get("dailyRange.startDate.day"), 1)
            self.assertEqual((request["params"] or {}).get("dailyRange.endDate.year"), 2025)
            self.assertEqual((request["params"] or {}).get("dailyRange.endDate.month"), 1)
            self.assertEqual((request["params"] or {}).get("dailyRange.endDate.day"), 31)
    def test_list_search_keywords_impressions_monthly_uses_parent_and_month_range(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
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
                    body=b'{"searchKeywordsCounts":[{"searchKeyword":"coffee","insightsValue":{"value":"123"}}]}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.list_search_keywords_impressions_monthly(
                    parent="locations/123",
                    monthly_range_start_year=2025,
                    monthly_range_start_month=1,
                    monthly_range_end_year=2025,
                    monthly_range_end_month=3,
                    page_size=25,
                    page_token="next-page",
                )

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(PERFORMANCE_HOST) + "/v1/locations/123/searchkeywords/impressions/monthly")
            self.assertEqual(request["host"], PERFORMANCE_HOST)
            self.assertEqual(request["path"], "v1/locations/123/searchkeywords/impressions/monthly")
            self.assertEqual((request["params"] or {}).get("monthlyRange.startMonth.year"), 2025)
            self.assertEqual((request["params"] or {}).get("monthlyRange.startMonth.month"), 1)
            self.assertEqual((request["params"] or {}).get("monthlyRange.endMonth.year"), 2025)
            self.assertEqual((request["params"] or {}).get("monthlyRange.endMonth.month"), 3)
            self.assertEqual((request["params"] or {}).get("pageSize"), 25)
            self.assertEqual((request["params"] or {}).get("pageToken"), "next-page")

    def test_start_upload_location_media_posts_empty_body_to_v4_start_upload(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                request_data["json_body"] = json_body
                request_data["body"] = json_body
                request_data["data"] = data
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"mediaItemDataRef":{"resourceName":"media/abc"}}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.start_upload_location_media(parent="accounts/123/locations/456")

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(request_data["url"], str(LEGACY_V49_HOST) + "/v4/accounts/123/locations/456:startUpload")
            self.assertIsNone(request_data.get("json_body"))
            self.assertIsNone(request_data.get("params"))
            self.assertIsNone(request_data.get("data"))
            self.assertEqual(request["path"], "v4/accounts/123/locations/456:startUpload")
            self.assertEqual(request["host"], LEGACY_V49_HOST)

    def test_create_location_media_posts_media_item_json_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            media_item = {
                "mediaFormat": "PHOTO",
                "sourceUrl": "https://example.com/photo.jpg",
            }

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
                    body=b'{"mediaItemDataRef":{"resourceName":"media/abc"}}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.create_location_media(parent="accounts/123/locations/456", media_item=media_item)

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(request_data["url"], str(LEGACY_V49_HOST) + "/v4/accounts/123/locations/456/media")
            self.assertEqual(request_data["params"], None)
            self.assertEqual(request_data["body"], media_item)
            self.assertEqual(request["path"], "v4/accounts/123/locations/456/media")
            self.assertEqual(request["host"], LEGACY_V49_HOST)

    def test_list_legacy_reviews_posts_expected_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                    body=b'{"reviews":[{"name":"accounts/123/locations/456/reviews/abc"}]}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.list_legacy_reviews(
                    parent="accounts/123/locations/456",
                    page_size=25,
                    page_token="next",
                    order_by="rating desc",
                )

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(
                request_data["url"],
                str(LEGACY_V49_HOST) + "/v4/accounts/123/locations/456/reviews",
            )
            self.assertEqual(request["path"], "v4/accounts/123/locations/456/reviews")
            self.assertEqual(request["host"], LEGACY_V49_HOST)
            self.assertEqual((request_data["params"] or {}).get("pageSize"), 25)
            self.assertEqual((request_data["params"] or {}).get("pageToken"), "next")
            self.assertEqual((request_data["params"] or {}).get("orderBy"), "rating desc")

    def test_list_legacy_verifications_posts_expected_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                    body=b'{"verifications":[{"name":"accounts/123/locations/456/verifications/001"}]}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.list_legacy_verifications(
                    parent="accounts/123/locations/456",
                    page_size=10,
                    page_token="next-token",
                )

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(
                request_data["url"],
                str(LEGACY_V49_HOST) + "/v4/accounts/123/locations/456/verifications",
            )
            self.assertEqual(request["path"], "v4/accounts/123/locations/456/verifications")
            self.assertEqual(request["host"], LEGACY_V49_HOST)
            self.assertEqual((request_data["params"] or {}).get("pageSize"), 10)
            self.assertEqual((request_data["params"] or {}).get("pageToken"), "next-token")

    def test_get_legacy_review_posts_get_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                    body=b'{"name":"accounts/123/locations/456/reviews/abc"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.get_legacy_review(name="accounts/123/locations/456/reviews/abc")

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(LEGACY_V49_HOST) + "/v4/accounts/123/locations/456/reviews/abc")
            self.assertEqual(request["path"], "v4/accounts/123/locations/456/reviews/abc")
            self.assertEqual(request["host"], LEGACY_V49_HOST)

    def test_complete_legacy_verification_posts_pin_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                    body=b'{"verification":{"name":"accounts/123/locations/456/verifications/001","state":"COMPLETED"}}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.complete_legacy_verification(
                    name="accounts/123/locations/456/verifications/001",
                    pin="123456",
                )

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(
                request_data["url"],
                str(LEGACY_V49_HOST) + "/v4/accounts/123/locations/456/verifications/001:complete",
            )
            self.assertEqual(request["path"], "v4/accounts/123/locations/456/verifications/001:complete")
            self.assertEqual(request["host"], LEGACY_V49_HOST)
            self.assertEqual(request_data["body"], {"pin": "123456"})

    def test_update_review_reply_puts_comment_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            reply = {"comment": "Thanks for the review"}

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
                    body=b'{"reviewReply":{"comment":"Thanks for the review"}}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.update_review_reply(
                    name="accounts/123/locations/456/reviews/abc",
                    review_reply=reply,
                )

            self.assertEqual(request_data["method"], "PUT")
            self.assertEqual(request_data["url"], str(LEGACY_V49_HOST) + "/v4/accounts/123/locations/456/reviews/abc/reply")
            self.assertEqual(request_data["body"], reply)
            self.assertEqual(request["path"], "v4/accounts/123/locations/456/reviews/abc/reply")
            self.assertEqual(request["host"], LEGACY_V49_HOST)

    def test_delete_review_reply_deletes_reply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                    body=b"",
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                response, request = client.delete_review_reply(name="accounts/123/locations/456/reviews/abc")

            self.assertEqual(response, {})
            self.assertEqual(request_data["method"], "DELETE")
            self.assertEqual(
                request_data["url"],
                str(LEGACY_V49_HOST) + "/v4/accounts/123/locations/456/reviews/abc/reply",
            )
            self.assertEqual(request["path"], "v4/accounts/123/locations/456/reviews/abc/reply")
            self.assertEqual(request["host"], LEGACY_V49_HOST)

    def test_place_action_links_create_uses_parent_and_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {
                "name": "locations/abc/placeActionLinks/old",
                "uri": "https://example.com/click",
                "placeActionType": "DINING_RESERVATION",
            }

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
                    body=b'{"name":"locations/abc/placeActionLinks/new"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.create_place_action_link(parent="locations/abc", body=body)

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(request_data["url"], str(PLACE_ACTIONS_HOST) + "/v1/locations/abc/placeActionLinks")
            self.assertIsNone(request_data["params"])
            self.assertEqual(request_data["body"], body)
            self.assertEqual(request["path"], "v1/locations/abc/placeActionLinks")
            self.assertEqual(request["host"], PLACE_ACTIONS_HOST)

    def test_place_action_links_delete_uses_name_and_allow_empty_response(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                return HttpResponse(status=200, headers={}, body=b"", url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.delete_place_action_link(name="locations/abc/placeActionLinks/xyz")

            self.assertEqual(request_data["method"], "DELETE")
            self.assertEqual(request_data["url"], str(PLACE_ACTIONS_HOST) + "/v1/locations/abc/placeActionLinks/xyz")
            self.assertEqual(request["path"], "v1/locations/abc/placeActionLinks/xyz")
            self.assertEqual(request["host"], PLACE_ACTIONS_HOST)

    def test_place_action_links_get_uses_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"name":"locations/abc/placeActionLinks/xyz","uri":"https://example.com/click"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.get_place_action_link(name="locations/abc/placeActionLinks/xyz")

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(PLACE_ACTIONS_HOST) + "/v1/locations/abc/placeActionLinks/xyz")
            self.assertEqual(request["path"], "v1/locations/abc/placeActionLinks/xyz")
            self.assertEqual(request["host"], PLACE_ACTIONS_HOST)
            self.assertIsNone(request_data["params"])

    def test_place_action_links_list_uses_parent_and_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"placeActionLinks":[]}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.list_place_action_links(
                    parent="locations/abc",
                    page_size=10,
                    page_token="pt",
                    filter="placeActionType=DINING_RESERVATION",
                )

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(PLACE_ACTIONS_HOST) + "/v1/locations/abc/placeActionLinks")
            self.assertEqual((request_data["params"] or {}).get("pageSize"), 10)
            self.assertEqual((request_data["params"] or {}).get("pageToken"), "pt")
            self.assertEqual((request_data["params"] or {}).get("filter"), "placeActionType=DINING_RESERVATION")
            self.assertEqual(request["path"], "v1/locations/abc/placeActionLinks")
            self.assertEqual(request["host"], PLACE_ACTIONS_HOST)

    def test_place_action_links_patch_uses_update_mask(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            body = {
                "name": "locations/abc/placeActionLinks/xyz",
                "uri": "https://example.com/click",
            }

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
                    body=b'{"name":"locations/abc/placeActionLinks/xyz"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.patch_place_action_link(
                    name="locations/abc/placeActionLinks/xyz",
                    update_mask="uri",
                    body=body,
                )

            self.assertEqual(request_data["method"], "PATCH")
            self.assertEqual(request_data["url"], str(PLACE_ACTIONS_HOST) + "/v1/locations/abc/placeActionLinks/xyz")
            self.assertEqual((request_data["params"] or {}).get("updateMask"), "uri")
            self.assertEqual(request_data["body"], body)
            self.assertEqual(request["path"], "v1/locations/abc/placeActionLinks/xyz")
            self.assertEqual(request["host"], PLACE_ACTIONS_HOST)

    def test_place_action_type_metadata_list_uses_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"placeActionTypeMetadata":[]}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.list_place_action_type_metadata(
                    language_code="en-US",
                    page_size=20,
                    page_token="pt",
                    filter="location=locations/abc",
                )

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(PLACE_ACTIONS_HOST) + "/v1/placeActionTypeMetadata")
            self.assertEqual((request_data["params"] or {}).get("languageCode"), "en-US")
            self.assertEqual((request_data["params"] or {}).get("pageSize"), 20)
            self.assertEqual((request_data["params"] or {}).get("pageToken"), "pt")
            self.assertEqual((request_data["params"] or {}).get("filter"), "location=locations/abc")
            self.assertEqual(request["path"], "v1/placeActionTypeMetadata")
            self.assertEqual(request["host"], PLACE_ACTIONS_HOST)

    def test_fetch_verification_options_uses_post_body_and_verifications_host(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

            request_data: dict[str, object] = {}
            context = {"address": {"postalCode": "94107"}}

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
                return HttpResponse(status=200, headers={}, body=b'{}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.fetch_verification_options(
                    location="locations/abc",
                    language_code="en-US",
                    context=context,
                )

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(request_data["url"], str(VERIFICATIONS_HOST) + "/v1/locations/abc:fetchVerificationOptions")
            self.assertEqual(request["host"], VERIFICATIONS_HOST)
            self.assertEqual(
                request_data["body"],
                {
                    "languageCode": "en-US",
                    "context": context,
                },
            )

    def test_get_voice_of_merchant_state_uses_get_and_path_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                return HttpResponse(status=200, headers={}, body=b'{}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.get_voice_of_merchant_state(name="locations/abc")

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(VERIFICATIONS_HOST) + "/v1/locations/abc/VoiceOfMerchantState")
            self.assertEqual(request_data["params"], None)
            self.assertEqual(request_data["body"], None)
            self.assertEqual(request["path"], "v1/locations/abc/VoiceOfMerchantState")
            self.assertEqual(request["host"], VERIFICATIONS_HOST)

    def test_list_verifications_uses_parent_and_paging_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                return HttpResponse(status=200, headers={}, body=b'{"verifications":[]}', url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.list_verifications(
                    parent="locations/abc",
                    page_size=10,
                    page_token="next-page",
                )

            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["url"], str(VERIFICATIONS_HOST) + "/v1/locations/abc/verifications")
            self.assertEqual(request["path"], "v1/locations/abc/verifications")
            self.assertEqual(request["host"], VERIFICATIONS_HOST)
            self.assertEqual((request["params"] or {}).get("pageSize"), 10)
            self.assertEqual((request["params"] or {}).get("pageToken"), "next-page")

    def test_verify_location_posts_expected_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                    body=b'{"verification":{"name":"locations/abc/verifications/001"}}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.verify_location(
                    name="locations/abc",
                    method="ADDRESS",
                    language_code="en-US",
                    mailer_contact="mailer@business.example",
                    phone_number="+12025550199",
                    email_address="owner@example.com",
                    context={"address": {"regionCode": "US"}},
                    token={"tokenString": "abc"},
                    trusted_partner_token="partner-token",
                )

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(request_data["url"], str(VERIFICATIONS_HOST) + "/v1/locations/abc:verify")
            self.assertEqual(request["path"], "v1/locations/abc:verify")
            self.assertEqual(request["host"], VERIFICATIONS_HOST)
            self.assertEqual(
                request_data["body"],
                {
                    "method": "ADDRESS",
                    "languageCode": "en-US",
                    "mailerContact": "mailer@business.example",
                    "phoneNumber": "+12025550199",
                    "emailAddress": "owner@example.com",
                    "context": {"address": {"regionCode": "US"}},
                    "token": {"tokenString": "abc"},
                    "trustedPartnerToken": "partner-token",
                },
            )
            self.assertEqual(request_data["params"], None)

    def test_complete_verification_posts_pin(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                request_data["body"] = json_body
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"verification":{"name":"locations/abc/verifications/001"}}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.complete_verification(
                    name="locations/abc/verifications/001",
                    pin="123456",
                )

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(request_data["url"], str(VERIFICATIONS_HOST) + "/v1/locations/abc/verifications/001:complete")
            self.assertEqual(request["path"], "v1/locations/abc/verifications/001:complete")
            self.assertEqual(request["host"], VERIFICATIONS_HOST)
            self.assertEqual(request_data["body"], {"pin": "123456"})

    def test_generate_verification_token_posts_location_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                    body=b'{"result":"SUCCEEDED"}',
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                _, request = client.generate_verification_token(location_id="123456")

            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(
                request_data["url"],
                str(VERIFICATIONS_HOST) + "/v1/verificationTokens:generate",
            )
            self.assertEqual(request["path"], "v1/verificationTokens:generate")
            self.assertEqual(request["host"], VERIFICATIONS_HOST)
            self.assertIsNone(request.get("params"))
            self.assertEqual(request_data["body"], {"locationId": "123456"})

    def test_accept_account_invitation_posts_empty_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                    body=b"{}",
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                response, request = client.accept_account_invitation(name="accounts/123/invitations/abc")

            self.assertEqual(response, {})
            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(
                request_data["url"],
                str(ACCOUNT_MANAGEMENT_HOST) + "/v1/accounts/123/invitations/abc:accept",
            )
            self.assertEqual(request["path"], "v1/accounts/123/invitations/abc:accept")
            self.assertEqual(request["host"], ACCOUNT_MANAGEMENT_HOST)
            self.assertEqual(request_data["params"], None)
            self.assertEqual(request_data["body"], {})

    def test_accept_account_invitation_allows_true_empty_response_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                return HttpResponse(status=200, headers={}, body=b"", url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                response, request = client.accept_account_invitation(name="accounts/123/invitations/abc")

            self.assertEqual(response, {})
            self.assertEqual(request["path"], "v1/accounts/123/invitations/abc:accept")

    def test_decline_account_invitation_posts_empty_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                    body=b"{}",
                    url=url,
                )

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                response, request = client.decline_account_invitation(name="accounts/123/invitations/abc")

            self.assertEqual(response, {})
            self.assertEqual(request_data["method"], "POST")
            self.assertEqual(
                request_data["url"],
                str(ACCOUNT_MANAGEMENT_HOST) + "/v1/accounts/123/invitations/abc:decline",
            )
            self.assertEqual(request["path"], "v1/accounts/123/invitations/abc:decline")
            self.assertEqual(request["host"], ACCOUNT_MANAGEMENT_HOST)
            self.assertEqual(request_data["params"], None)
            self.assertEqual(request_data["body"], {})

    def test_decline_account_invitation_allows_true_empty_response_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GBP_TIMEOUT_S=30\n", encoding="utf-8")
            token_path = root / ".state" / "oauth_credentials.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text("{}", encoding="utf-8")

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
                return HttpResponse(status=200, headers={}, body=b"", url=url)

            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials(token="token"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                client = GoogleBusinessProfileApiClient(
                    cfg=self._build_config(),
                    env_file=str(env_path),
                    timeout_s=30.0,
                    verbose=False,
                    ack_no_snapshot=True,
                )
                response, request = client.decline_account_invitation(name="accounts/123/invitations/abc")

            self.assertEqual(response, {})
            self.assertEqual(request["path"], "v1/accounts/123/invitations/abc:decline")
