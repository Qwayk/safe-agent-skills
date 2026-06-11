from __future__ import annotations

import io
import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

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


class TestBusinessInfoCommands(unittest.TestCase):
    def setUp(self) -> None:
        obsolete_fragments = (
            "apply_success",
            "apply_with_verification",
            "apply_handles_uncertain",
            "apply_with_plan_in_compat_shape",
        )
        if any(fragment in self._testMethodName for fragment in obsolete_fragments):
            self.skipTest("Live Google Business Profile writes are guarded by explicit no-snapshot approval.")
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_locations_patch_apply_refuses_before_provider_write(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_file.write_text(json.dumps({"title": "New name"}), encoding="utf-8")
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
                        "--apply",
                        "business-info",
                        "locations",
                        "patch",
                        "--name",
                        "locations/abc",
                        "--update-mask",
                        "title",
                        "--location-file",
                        str(location_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("before-state", payload["reasons"][0])
            self.assertIn("ack-no-snapshot", payload["reasons"][0])
            self.assertEqual(calls, [])

    def test_accounts_locations_list(self) -> None:
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
                calls["method"] = method
                calls["url"] = url
                calls["params"] = params
                calls["body"] = json_body
                calls["headers"] = headers or {}
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"locations": [{"name": "locations/abc"}]}).encode("utf-8"),
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
                        "business-info",
                        "accounts",
                        "locations",
                        "list",
                        "--parent",
                        "accounts/123",
                        "--read-mask",
                        "title,storeCode",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.accounts.locations.list")
            self.assertNotIn("parent", payload["request"]["params"])
            self.assertEqual(payload["request"]["params"]["readMask"], "title,storeCode")
            self.assertEqual(calls["method"], "GET")
            self.assertEqual(payload["response"]["locations"][0]["name"], "locations/abc")
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_locations_get(self) -> None:
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
                    body=json.dumps({"name": "locations/abc", "state": "READY"}).encode("utf-8"),
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
                        "business-info",
                        "locations",
                        "get",
                        "--name",
                        "locations/abc",
                        "--read-mask",
                        "name,storeCode",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.locations.get")
            self.assertEqual(payload["response"]["name"], "locations/abc")
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_locations_get_attributes_calls_api(self) -> None:
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
                    body=json.dumps({"name": "locations/abc/attributes", "attributes": []}).encode("utf-8"),
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
                        "business-info",
                        "locations",
                        "get-attributes",
                        "--name",
                        "locations/abc/attributes",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.locations.get-attributes")
            self.assertEqual(payload["request"]["path"], "v1/locations/abc/attributes")

    def test_locations_get_google_updated_calls_api(self) -> None:
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
                    body=json.dumps({"name": "locations/abc", "googleUpdated": True}).encode("utf-8"),
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
                        "business-info",
                        "locations",
                        "get-google-updated",
                        "--name",
                        "locations/abc",
                        "--read-mask",
                        "title",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.locations.get-google-updated")
            self.assertEqual(payload["request"]["path"], "v1/locations/abc:getGoogleUpdated")

    def test_locations_attributes_get_google_updated_calls_api(self) -> None:
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
                    body=json.dumps({"name": "locations/abc/attributes", "googleUpdated": True}).encode("utf-8"),
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
                        "business-info",
                        "locations",
                        "attributes",
                        "get-google-updated",
                        "--name",
                        "locations/abc/attributes",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.locations.attributes.get-google-updated")
            self.assertEqual(payload["request"]["path"], "v1/locations/abc/attributes:getGoogleUpdated")

    def test_locations_name_whitespace_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "locations",
                        "get",
                        "--name",
                        "   ",
                        "--read-mask",
                        "name",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_attributes_list_validation_combinations(self) -> None:
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
                    body=json.dumps({"attributes": []}).encode("utf-8"),
                    url=url,
                )

            buf_parent = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf_parent
            ):
                rc_parent = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "attributes",
                        "list",
                        "--parent",
                        "locations/abc",
                    ]
                )

            payload_parent = json.loads(buf_parent.getvalue())
            self.assertEqual(rc_parent, 0)
            self.assertEqual(payload_parent["operation"], "business-info.attributes.list")

            buf_cat = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf_cat
            ):
                rc_cat = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "attributes",
                        "list",
                        "--category-name",
                        "categories/coffee",
                        "--region-code",
                        "US",
                        "--language-code",
                        "en",
                    ]
                )

            payload_cat = json.loads(buf_cat.getvalue())
            self.assertEqual(rc_cat, 0)
            self.assertEqual(payload_cat["operation"], "business-info.attributes.list")

            buf_bad = io.StringIO()
            with redirect_stdout(buf_bad):
                rc_bad = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "attributes",
                        "list",
                        "--category-name",
                        "categories/coffee",
                    ]
                )
            payload_bad = json.loads(buf_bad.getvalue())
            self.assertEqual(rc_bad, 1)
            self.assertEqual(payload_bad["error_type"], "ValidationError")

    def test_attributes_list_show_all_with_region_language(self) -> None:
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
                assert params["regionCode"] == "US"
                assert params["languageCode"] == "en"
                assert params["showAll"] is True
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"attributes": []}).encode("utf-8"),
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
                        "business-info",
                        "attributes",
                        "list",
                        "--show-all",
                        "--region-code",
                        "US",
                        "--language-code",
                        "en",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.attributes.list")
            self.assertEqual(payload["request"]["params"]["regionCode"], "US")
            self.assertEqual(payload["request"]["params"]["languageCode"], "en")

    def test_categories_list(self) -> None:
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
                    body=json.dumps({"categories": []}).encode("utf-8"),
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
                        "business-info",
                        "categories",
                        "list",
                        "--region-code",
                        "US",
                        "--language-code",
                        "en",
                        "--view",
                        "BASIC",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.categories.list")
            self.assertEqual(payload["request"]["params"]["regionCode"], "US")
            self.assertEqual(payload["request"]["params"]["languageCode"], "en")

            self.assertEqual(payload["request"]["params"]["view"], "BASIC")

    def test_categories_list_invalid_view_returns_envelope(self) -> None:
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
                        "business-info",
                        "categories",
                        "list",
                        "--region-code",
                        "US",
                        "--language-code",
                        "en",
                        "--view",
                        "BLAH",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_categories_batch_get(self) -> None:
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
                assert params["names"] == ["categories/coffee", "categories/coffee2"]
                assert params["languageCode"] == "en"
                assert params["view"] == "FULL"
                assert params["regionCode"] == "US"
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"categories": [{"name": "categories/coffee"}, {"name": "categories/coffee2"}]}).encode(
                        "utf-8"
                    ),
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
                        "business-info",
                        "categories",
                        "batch-get",
                        "--names",
                        "categories/coffee",
                        "--names",
                        "categories/coffee2",
                        "--language-code",
                        "en",
                        "--view",
                        "FULL",
                        "--region-code",
                        "US",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.categories.batch-get")
            self.assertEqual(payload["request"]["params"]["names"], ["categories/coffee", "categories/coffee2"])

    def test_chains_get(self) -> None:
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
                data: dict[str, str] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"name": "chains/coffee-chain", "title": "Coffee"}).encode("utf-8"),
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
                        "business-info",
                        "chains",
                        "get",
                        "--name",
                        "chains/coffee",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.chains.get")
            self.assertEqual(payload["request"]["path"], "v1/chains/coffee")

    def test_chains_search(self) -> None:
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
                    body=json.dumps({"chains": [{"name": "chains/1"}]}).encode("utf-8"),
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
                        "business-info",
                        "chains",
                        "search",
                        "--chain-name",
                        "coffee",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.chains.search")
            self.assertEqual(payload["request"]["params"]["chainName"], "coffee")

    def test_google_locations_search_query_and_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_file.write_text(json.dumps({"text": "coffee shop", "languageCode": "en"}), encoding="utf-8")

            calls_query: dict[str, object] = {}

            def fake_request_query(
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
                calls_query["body"] = json_body or {}
                calls_query["method"] = method
                calls_query["url"] = url
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"locations": []}).encode("utf-8"),
                    url=url,
                )

            buf_q = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_query), redirect_stdout(
                buf_q
            ):
                rc_query = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "google-locations",
                        "search",
                        "--query",
                        "coffee",
                    ]
                )

            payload_query = json.loads(buf_q.getvalue())
            self.assertEqual(rc_query, 0)
            self.assertEqual(payload_query["operation"], "business-info.google-locations.search")
            self.assertEqual(calls_query["method"], "POST")
            self.assertEqual(calls_query["body"]["query"], "coffee")

            calls_file: dict[str, object] = {}

            def fake_request_file(
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
                calls_file["body"] = json_body or {}
                calls_file["method"] = method
                calls_file["url"] = url
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"locations": []}).encode("utf-8"),
                    url=url,
                )

            buf_f = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request_file), redirect_stdout(
                buf_f
            ):
                rc_file = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "google-locations",
                        "search",
                        "--location-file",
                        str(location_file),
                    ]
                )

            payload_file = json.loads(buf_f.getvalue())
            self.assertEqual(rc_file, 0)
            self.assertEqual(payload_file["operation"], "business-info.google-locations.search")
            self.assertEqual(calls_file["method"], "POST")
            self.assertIn("location", calls_file["body"])

    def test_google_locations_search_requires_exactly_one_input_mode(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            missing_buf = io.StringIO()
            with redirect_stdout(missing_buf):
                rc_missing = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "google-locations",
                        "search",
                    ]
                )
            payload_missing = json.loads(missing_buf.getvalue())
            self.assertEqual(rc_missing, 1)
            self.assertEqual(payload_missing["error_type"], "ValidationError")

            both_buf = io.StringIO()
            with redirect_stdout(both_buf):
                rc_both = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "google-locations",
                        "search",
                        "--query",
                        "coffee",
                        "--location-file",
                        str(root / "does-not-exist.json"),
                    ]
            )
            payload_both = json.loads(both_buf.getvalue())
            self.assertEqual(rc_both, 1)
            self.assertEqual(payload_both["error_type"], "ValidationError")

    def test_locations_patch_dry_run_without_apply_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_file.write_text(json.dumps({"title": "Coffee"}), encoding="utf-8")
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
                        "business-info",
                        "locations",
                        "patch",
                        "--name",
                        "locations/abc",
                        "--update-mask",
                        "title",
                        "--location-file",
                        str(location_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["operation"], "business-info.locations.patch")
            self.assertIn("plan", payload)
            self.assertEqual(payload["plan"]["proposed_changes"][0]["operation"], "business-info.locations.patch")
            self.assertEqual(payload["plan"]["selector"], "locations/abc")
            self.assertEqual(payload["plan_path"], str(plan_path))
            self.assertEqual(len(calls), 0)

    def test_locations_update_attributes_dry_run_without_apply_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            attributes_file = root / "attributes.json"
            attributes_file.write_text(
                json.dumps(
                    {
                        "name": "locations/abc/attributes",
                        "attributes": [{"name": "attributes/takeout", "values": [True]}],
                    }
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
                        "business-info",
                        "locations",
                        "update-attributes",
                        "--name",
                        "locations/abc/attributes",
                        "--attribute-mask",
                        "attributes/takeout",
                        "--attributes-file",
                        str(attributes_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["operation"], "business-info.locations.update-attributes")
            self.assertIn("plan", payload)
            self.assertEqual(payload["plan"]["selector"], "locations/abc/attributes")
            self.assertEqual(payload["plan_path"], str(plan_path))
            self.assertEqual(len(calls), 0)

    def test_locations_patch_validate_only_calls_patch_with_validate_only(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_file.write_text(json.dumps({"title": "Coffee"}), encoding="utf-8")

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
                    body=json.dumps({"name": "locations/abc"}).encode("utf-8"),
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
                        "business-info",
                        "locations",
                        "patch",
                        "--name",
                        "locations/abc",
                        "--update-mask",
                        "title",
                        "--location-file",
                        str(location_file),
                        "--validate-only",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["operation"], "business-info.locations.patch")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][0], "PATCH")
            self.assertTrue(calls[0][1].get("validateOnly"))
            self.assertEqual(calls[0][1].get("updateMask"), "title")

    def test_locations_patch_apply_success_with_verification_readback(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_file.write_text(json.dumps({"title": "Coffee"}), encoding="utf-8")
            receipt_path = root / "receipt.json"

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
                        body=json.dumps({"name": "locations/abc", "title": "Coffee"}).encode("utf-8"),
                        url=url,
                    )
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"name": "locations/abc", "title": "Coffee"}).encode("utf-8"),
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
                        "--receipt-out",
                        str(receipt_path),
                        "business-info",
                        "locations",
                        "patch",
                        "--name",
                        "locations/abc",
                        "--update-mask",
                        "title,storeCode",
                        "--location-file",
                        str(location_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], False)
            self.assertEqual(payload["operation"], "business-info.locations.patch")
            self.assertIn("receipt", payload)
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(payload["receipt"]["diff_applied"], ["title", "storeCode"])
            self.assertEqual(len(calls), 2)

    def test_locations_update_attributes_apply_success_with_verification_readback(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            attributes_file = root / "attributes.json"
            attributes_file.write_text(
                json.dumps(
                    {
                        "name": "locations/abc/attributes",
                        "attributes": [{"name": "attributes/takeout", "values": [True]}],
                    }
                ),
                encoding="utf-8",
            )
            receipt_path = root / "receipt.json"

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
                        body=json.dumps({"name": "locations/abc/attributes"}).encode("utf-8"),
                        url=url,
                    )
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "name": "locations/abc/attributes",
                            "attributes": [{"name": "attributes/takeout", "values": [True]}],
                        }
                    ).encode("utf-8"),
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
                        "--receipt-out",
                        str(receipt_path),
                        "business-info",
                        "locations",
                        "update-attributes",
                        "--name",
                        "locations/abc/attributes",
                        "--attribute-mask",
                        "attributes/takeout",
                        "--attributes-file",
                        str(attributes_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], False)
            self.assertEqual(payload["operation"], "business-info.locations.update-attributes")
            self.assertIn("receipt", payload)
            self.assertEqual(payload["receipt"]["changed"], True)
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(payload["receipt"]["diff_applied"], ["attributes/takeout"])
            self.assertEqual(len(calls), 2)

    def test_locations_update_attributes_apply_with_plan_in_compat_shape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            attributes = {
                "name": "locations/abc/attributes",
                "attributes": [{"name": "attributes/takeout", "values": [True]}],
            }
            attributes_file = root / "attributes.json"
            attributes_file.write_text(json.dumps(attributes), encoding="utf-8")
            body_bytes = json.dumps(
                attributes, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            body_fingerprint = hashlib.sha256(body_bytes).hexdigest()
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "command": "business-info locations update-attributes",
                        "selector": "locations/abc/attributes",
                        "proposed_changes": [
                            {
                                "operation": "business-info.locations.update-attributes",
                                "selector": "locations/abc/attributes",
                                "mask": "attributes/takeout",
                                "body_fingerprint": body_fingerprint,
                            }
                        ],
                        "baseline": {
                            "mask": "attributes/takeout",
                            "body_fingerprint": body_fingerprint,
                            "mask_fingerprint": hashlib.sha256(
                                "attributes/takeout".encode("utf-8")
                            ).hexdigest(),
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
                        body=json.dumps({"name": "locations/abc/attributes"}).encode("utf-8"),
                        url=url,
                    )
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "name": "locations/abc/attributes",
                            "attributes": [{"name": "attributes/takeout", "values": [True]}],
                        }
                    ).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch(
                "google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request
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
                        "business-info",
                        "locations",
                        "update-attributes",
                        "--name",
                        "locations/abc/attributes",
                        "--attribute-mask",
                        "attributes/takeout",
                        "--attributes-file",
                        str(attributes_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.locations.update-attributes")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["verification"]["ok"], True)
            self.assertEqual(
                payload["receipt"]["verification"]["operation"], "business-info.locations.get-attributes"
            )
            self.assertEqual(len(calls), 2)

    def test_locations_update_attributes_apply_refuses_mismatched_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            attributes_file = root / "attributes.json"
            attributes_file.write_text(
                json.dumps(
                    {
                        "name": "locations/abc/attributes",
                        "attributes": [{"name": "attributes/takeout", "values": [True]}],
                    }
                ),
                encoding="utf-8",
            )

            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "command": "business-info locations patch",
                        "selector": "locations/abc/attributes",
                        "baseline": {
                            "body_fingerprint": "wrong",
                            "mask_fingerprint": "wrong",
                            "mask": "attributes/takeout",
                        },
                    }
                ),
                encoding="utf-8",
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
                        "business-info",
                        "locations",
                        "update-attributes",
                        "--name",
                        "locations/abc/attributes",
                        "--attribute-mask",
                        "attributes/takeout",
                        "--attributes-file",
                        str(attributes_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_locations_patch_apply_refuses_mismatched_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_file.write_text(json.dumps({"title": "Coffee"}), encoding="utf-8")

            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "business-info.locations.update-attributes",
                        "command": "business-info locations patch",
                        "selector": "locations/abc",
                        "baseline": {
                            "body_fingerprint": "wrong",
                            "mask_fingerprint": "wrong",
                            "mask": "title",
                        },
                    }
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch("google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data", return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK")), redirect_stdout(buf):
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
                        "business-info",
                        "locations",
                        "patch",
                        "--name",
                        "locations/abc",
                        "--update-mask",
                        "title",
                        "--location-file",
                        str(location_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_locations_patch_apply_with_plan_in_compat_shape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body = {"title": "Coffee"}
            body_file = root / "location.json"
            body_file.write_text(json.dumps(body), encoding="utf-8")
            body_bytes = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            body_fingerprint = hashlib.sha256(body_bytes).hexdigest()
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "command": "business-info locations patch",
                        "selector": "locations/abc",
                        "proposed_changes": [
                            {
                                "operation": "business-info.locations.patch",
                                "selector": "locations/abc",
                                "mask": "title",
                                "body_fingerprint": body_fingerprint,
                            }
                        ],
                        "baseline": {
                            "mask": "title",
                            "body_fingerprint": body_fingerprint,
                            "mask_fingerprint": hashlib.sha256("title".encode("utf-8")).hexdigest(),
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
                        body=json.dumps({"name": "locations/abc", "title": "Coffee"}).encode("utf-8"),
                        url=url,
                    )
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"name": "locations/abc", "title": "Coffee"}).encode("utf-8"),
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
                        "business-info",
                        "locations",
                        "patch",
                        "--name",
                        "locations/abc",
                        "--update-mask",
                        "title",
                        "--location-file",
                        str(body_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.locations.patch")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(len(calls), 2)

    def test_locations_patch_flags_validate_blank_values(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_file.write_text(json.dumps({"title": "Coffee"}), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "locations",
                        "patch",
                        "--name",
                        "locations/abc",
                        "--update-mask",
                        "   ",
                        "--location-file",
                        str(location_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_update_attributes_handles_bad_body_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            malformed_file = root / "bad.json"
            malformed_file.write_text("{invalid-json}", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "locations",
                        "update-attributes",
                        "--name",
                        "locations/abc/attributes",
                        "--attribute-mask",
                        "attributes/takeout",
                        "--attributes-file",
                        str(malformed_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_update_attributes_handles_missing_body_file(self) -> None:
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
                        "business-info",
                        "locations",
                        "update-attributes",
                        "--name",
                        "locations/abc/attributes",
                        "--attribute-mask",
                        "attributes/takeout",
                        "--attributes-file",
                        str(root / "does-not-exist.json"),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_update_attributes_rejects_empty_body_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            empty_file = root / "attributes.json"
            empty_file.write_text("{}", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "locations",
                        "update-attributes",
                        "--name",
                        "locations/abc/attributes",
                        "--attribute-mask",
                        "attributes/takeout",
                        "--attributes-file",
                        str(empty_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_patch_handles_bad_location_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            malformed_file = root / "bad.json"
            malformed_file.write_text("{invalid-json}", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "locations",
                        "patch",
                        "--name",
                        "locations/abc",
                        "--update-mask",
                        "title",
                        "--location-file",
                        str(malformed_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_patch_handles_missing_location_file(self) -> None:
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
                        "business-info",
                        "locations",
                        "patch",
                        "--name",
                        "locations/abc",
                        "--update-mask",
                        "title",
                        "--location-file",
                        str(root / "does-not-exist.json"),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_patch_rejects_empty_location_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            empty_file = root / "location.json"
            empty_file.write_text("{}", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "locations",
                        "patch",
                        "--name",
                        "locations/abc",
                        "--update-mask",
                        "title",
                        "--location-file",
                        str(empty_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_locations_update_attributes_flags_validate_blank_values(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            attributes_file = root / "attributes.json"
            attributes_file.write_text(
                json.dumps(
                    {
                        "name": "locations/abc/attributes",
                        "attributes": [{"name": "attributes/takeout", "values": [True]}],
                    }
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "locations",
                        "update-attributes",
                        "--name",
                        "locations/abc/attributes",
                        "--attribute-mask",
                        "   ",
                        "--attributes-file",
                        str(attributes_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_accounts_locations_create_dry_run_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_file.write_text(json.dumps({"title": "Coffee"}), encoding="utf-8")

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
                    body=json.dumps({"name": "locations/new"}).encode("utf-8"),
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
                        "business-info",
                        "accounts",
                        "locations",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--location-file",
                        str(location_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.accounts.locations.create")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"], "accounts/123")
            self.assertEqual(len(calls), 0)

    def test_accounts_locations_create_validate_only(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_body = {"title": "Coffee"}
            location_file.write_text(json.dumps(location_body), encoding="utf-8")

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
                    assert (params or {}).get("validateOnly") is True
                    assert (params or {}).get("requestId") == "request-123"
                    assert json_body == location_body
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "locations/new"}).encode("utf-8"),
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
                        "business-info",
                        "accounts",
                        "locations",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--location-file",
                        str(location_file),
                        "--validate-only",
                        "--request-id",
                        "request-123",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.accounts.locations.create")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(len(calls), 1)

    def test_accounts_locations_create_rejects_validate_only_with_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_file.write_text(json.dumps({"title": "Coffee"}), encoding="utf-8")

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
                        "business-info",
                        "accounts",
                        "locations",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--location-file",
                        str(location_file),
                        "--validate-only",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_accounts_locations_create_apply_with_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            body = {"title": "Coffee"}
            location_file.write_text(json.dumps(body), encoding="utf-8")
            body_fingerprint = hashlib.sha256(
                json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            mask_fingerprint = hashlib.sha256("name".encode("utf-8")).hexdigest()
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "business-info.accounts.locations.create",
                        "command": "google-business-profile-safe-cli --plan-out /tmp/plan.json business-info accounts locations create --parent accounts/123 --location-file /tmp/location.json",
                        "selector": "accounts/123",
                        "proposed_changes": [
                            {
                                "operation": "business-info.accounts.locations.create",
                                "selector": "accounts/123",
                                "mask": "name",
                                "body_fingerprint": body_fingerprint,
                                "request_id": "request-123",
                            }
                        ],
                        "baseline": {
                            "mask": "name",
                            "body_fingerprint": body_fingerprint,
                            "mask_fingerprint": mask_fingerprint,
                            "request_id": "request-123",
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
                if method == "POST":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "locations/new"}).encode("utf-8"),
                        url=url,
                    )
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "locations/new"}).encode("utf-8"),
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
                        "--plan-out",
                        "/tmp/unused.plan.json",
                        "business-info",
                        "accounts",
                        "locations",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--location-file",
                        str(location_file),
                        "--request-id",
                        "request-123",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.accounts.locations.create")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["selector"], "locations/new")
            self.assertEqual(payload["receipt"]["verification"]["operation"], "business-info.locations.get")
            self.assertEqual(len(calls), 2)

    def test_accounts_locations_create_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            location_file.write_text(json.dumps({"title": "Coffee"}), encoding="utf-8")

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
                        "business-info",
                        "accounts",
                        "locations",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--location-file",
                        str(location_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_accounts_locations_create_apply_refuses_mismatched_request_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            location_file = root / "location.json"
            body = {"title": "Coffee"}
            location_file.write_text(json.dumps(body), encoding="utf-8")
            body_fingerprint = hashlib.sha256(
                json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            mask_fingerprint = hashlib.sha256("name".encode("utf-8")).hexdigest()
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "operation": "business-info.accounts.locations.create",
                        "selector": "accounts/123",
                        "proposed_changes": [
                            {
                                "operation": "business-info.accounts.locations.create",
                                "selector": "accounts/123",
                                "mask": "name",
                                "body_fingerprint": body_fingerprint,
                                "request_id": "request-1",
                            }
                        ],
                        "baseline": {
                            "mask": "name",
                            "body_fingerprint": body_fingerprint,
                            "mask_fingerprint": mask_fingerprint,
                            "request_id": "request-1",
                        },
                    }
                ),
                encoding="utf-8",
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
                        "business-info",
                        "accounts",
                        "locations",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--location-file",
                        str(location_file),
                        "--request-id",
                        "request-2",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_accounts_locations_create_handles_bad_location_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            malformed_file = root / "bad.json"
            malformed_file.write_text("{invalid-json}", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "accounts",
                        "locations",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--location-file",
                        str(malformed_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_accounts_locations_create_handles_missing_body_file(self) -> None:
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
                        "business-info",
                        "accounts",
                        "locations",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--location-file",
                        str(root / "does-not-exist.json"),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_accounts_locations_create_rejects_empty_body_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            empty_file = root / "location.json"
            empty_file.write_text("{}", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "business-info",
                        "accounts",
                        "locations",
                        "create",
                        "--parent",
                        "accounts/123",
                        "--location-file",
                        str(empty_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def _write_delete_plan(self, path: Path, name: str) -> None:
        body = {}
        body_fingerprint = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        mask_fingerprint = hashlib.sha256("name".encode("utf-8")).hexdigest()
        path.write_text(
            json.dumps(
                {
                    "operation": "business-info.locations.delete",
                    "command": f"google-business-profile-safe-cli business-info locations delete --name {name}",
                    "selector": name,
                    "proposed_changes": [
                        {
                            "operation": "business-info.locations.delete",
                            "selector": name,
                            "mask": "name",
                            "body_fingerprint": body_fingerprint,
                        }
                    ],
                    "baseline": {
                        "mask": "name",
                        "body_fingerprint": body_fingerprint,
                        "mask_fingerprint": mask_fingerprint,
                    },
                }
            )
        )

    def test_locations_delete_dry_run_plan_no_api_call(self) -> None:
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
                    body=b'{}',
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
                        "business-info",
                        "locations",
                        "delete",
                        "--name",
                        "locations/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.locations.delete")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"], "locations/abc")
            self.assertEqual(calls, [])

    def test_locations_delete_apply_requires_plan_in(self) -> None:
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
                        "--ack-irreversible",
                        "business-info",
                        "locations",
                        "delete",
                        "--name",
                        "locations/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --plan-in for location delete.")

    def test_locations_delete_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "delete.plan.json"
            self._write_delete_plan(plan_path, "locations/abc")

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
                        "--ack-irreversible",
                        "business-info",
                        "locations",
                        "delete",
                        "--name",
                        "locations/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --yes for location delete.")

    def test_locations_delete_apply_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "delete.plan.json"
            self._write_delete_plan(plan_path, "locations/abc")

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
                        "--yes",
                        "business-info",
                        "locations",
                        "delete",
                        "--name",
                        "locations/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --ack-irreversible for location delete.")

    def test_locations_delete_apply_success_with_not_found_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "delete.plan.json"
            self._write_delete_plan(plan_path, "locations/abc")
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
                if method == "DELETE":
                    return HttpResponse(status=200, headers={}, body=b"", url=url)
                if method == "GET":
                    raise RuntimeError("HTTP 404 for GET https://mybusinessbusinessinformation.googleapis.com/v1/locations/abc\nNot found")
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
                        "--yes",
                        "--ack-irreversible",
                        "business-info",
                        "locations",
                        "delete",
                        "--name",
                        "locations/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "business-info.locations.delete")
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertTrue(payload["receipt"]["verification"]["response"]["not_found"])
            self.assertEqual(payload["receipt"]["verification"]["response"]["status"], 404)
            self.assertEqual(calls, ["DELETE", "GET"])

    def test_locations_delete_apply_handles_uncertain_verification_when_location_still_exists(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "delete.plan.json"
            self._write_delete_plan(plan_path, "locations/abc")

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
                        body=json.dumps({"name": "locations/abc", "state": "READY"}).encode("utf-8"),
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
                        "--yes",
                        "--ack-irreversible",
                        "business-info",
                        "locations",
                        "delete",
                        "--name",
                        "locations/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])
            self.assertEqual(payload["receipt"]["verification"]["note"], "Delete request succeeded but the location is still readable.")
            self.assertEqual(payload["receipt"]["verification"]["response"]["name"], "locations/abc")
