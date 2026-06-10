from __future__ import annotations

from typing import Any
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from threads_api_tool.threads_client import ThreadsAPIClient


class _FakeResponse:
    def __init__(self, url: str, payload: dict[str, Any] | None = None) -> None:
        self.url = url
        self._payload = payload if payload is not None else {"ok": True}
        self.headers = {}
        self.status = 200

    def json(self) -> dict[str, Any]:
        return dict(self._payload)


class TestThreadsClientRequestPaths(TestCase):
    def _mk_cfg(self, **overrides: Any) -> Any:
        base = SimpleNamespace(
            base_url="https://graph.threads.net",
            api_version="v1.0",
            token="token-123",
            app_id="app-id",
            app_secret="app-secret",
            redirect_uri="https://example.invalid/callback",
            default_user_id="default-user",
        )
        base.__dict__.update(overrides)
        return base

    def _capture(self) -> tuple[dict[str, Any], Any]:
        captured: dict[str, Any] = {}

        def fake_request(method: str, url: str, **kwargs: Any) -> _FakeResponse:
            captured["method"] = method
            captured["url"] = url
            captured["params"] = kwargs.get("params")
            captured["data"] = kwargs.get("data")
            captured["json_body"] = kwargs.get("json_body")
            return _FakeResponse(url=url)

        return captured, fake_request

    def test_profiles_get_uses_profile_path_and_fields(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.get_profile(threads_user_id="user-1", fields="id,username")

        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/user-1")
        self.assertEqual(captured["params"], {"fields": "id,username", "access_token": "token-123"})

    def test_posts_list_owned_uses_threads_user_path(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.list_owned_posts(
                threads_user_id="user-1",
                params={"limit": 25, "fields": "id", "reverse": True},
            )

        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/user-1/threads")
        self.assertEqual(captured["params"]["fields"], "id")
        self.assertEqual(captured["params"]["limit"], 25)
        self.assertTrue(captured["params"]["reverse"])
        self.assertEqual(captured["params"]["access_token"], "token-123")

    def test_replies_list_uses_conversation_endpoint(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.list_replies(threads_media_id="media-1", params={"limit": 10, "reverse": True})

        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/media-1/replies")
        self.assertEqual(captured["params"]["reverse"], True)
        self.assertEqual(captured["params"]["limit"], 10)
        self.assertEqual(captured["params"]["access_token"], "token-123")

    def test_mentions_list_uses_mentions_endpoint(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.list_mentions(threads_user_id="user-1", params={"limit": 5})

        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/user-1/mentions")
        self.assertEqual(captured["params"]["limit"], 5)
        self.assertEqual(captured["params"]["access_token"], "token-123")

    def test_insights_media_includes_metric(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.media_insights(
                threads_media_id="media-1",
                params={"metric": "impressions,reach", "since": "2026-01-01"},
            )

        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/media-1/insights")
        self.assertEqual(captured["params"]["metric"], "impressions,reach")
        self.assertEqual(captured["params"]["since"], "2026-01-01")
        self.assertEqual(captured["params"]["access_token"], "token-123")

    def test_search_keyword_uses_q_param(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.search_keyword(
                query="cats",
                params={
                    "search_type": "all",
                    "search_mode": "keyword",
                    "media_type": "photo",
                },
            )

        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/keyword_search")
        self.assertEqual(captured["params"]["q"], "cats")
        self.assertEqual(captured["params"]["search_type"], "all")
        self.assertEqual(captured["params"]["search_mode"], "keyword")
        self.assertEqual(captured["params"]["media_type"], "photo")
        self.assertEqual(captured["params"]["access_token"], "token-123")

    def test_search_topic_tag_uses_q_param(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.search_topic_tag(topic_tag="travel", params={"media_type": "photo"})

        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/keyword_search")
        self.assertEqual(captured["params"]["q"], "travel")
        self.assertEqual(captured["params"]["media_type"], "photo")
        self.assertEqual(captured["params"]["access_token"], "token-123")

    def test_recently_searched_keywords_uses_me_endpoint(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.recently_searched_keywords()

        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/me")
        self.assertEqual(captured["params"], {"fields": "recently_searched_keywords", "access_token": "token-123"})

    def test_locations_search_query_and_coordinates_paths(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.search_locations_query(q="san francisco", params={"fields": "id,name"})

        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/location_search")
        self.assertEqual(captured["params"]["q"], "san francisco")
        self.assertEqual(captured["params"]["fields"], "id,name")
        self.assertEqual(captured["params"]["access_token"], "token-123")

        captured2, fake_request2 = self._capture()
        with patch.object(client._http, "request", side_effect=fake_request2):
            client.search_locations_coordinates(
                latitude=47.6,
                longitude=-122.3,
                radius_km=5.5,
                params={"fields": "id"},
            )

        self.assertEqual(captured2["url"], "https://graph.threads.net/v1.0/location_search")
        self.assertEqual(captured2["params"]["latitude"], 47.6)
        self.assertEqual(captured2["params"]["longitude"], -122.3)
        self.assertEqual(captured2["params"]["radius_km"], 5.5)
        self.assertEqual(captured2["params"]["fields"], "id")
        self.assertEqual(captured2["params"]["access_token"], "token-123")

    def test_oembed_uses_oembed_with_app_access_token(self) -> None:
        captured: dict[str, Any] = {}
        calls: list[tuple[str, str, dict[str, Any] | None]] = []

        def fake_request(method: str, url: str, **kwargs: Any) -> _FakeResponse:
            captured["method"] = method
            captured["url"] = url
            captured["params"] = kwargs.get("params")
            calls.append((method, url, captured["params"]))

            if "oauth/access_token" in url:
                return _FakeResponse(url=url, payload={"access_token": "app-token-1"})
            return _FakeResponse(url=url)

        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.oembed(
                url="https://threads.net/test/post",
                params={"maxwidth": 420, "fields": "html"},
            )

        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/oembed")
        self.assertEqual(captured["params"]["url"], "https://threads.net/test/post")
        self.assertEqual(captured["params"]["maxwidth"], 420)
        self.assertEqual(captured["params"]["fields"], "html")
        self.assertEqual(captured["params"]["access_token"], "app-token-1")

        self.assertGreaterEqual(len(calls), 2)
        first_call = calls[0]
        second_call = calls[1]
        self.assertEqual(first_call[0], "GET")
        self.assertTrue(first_call[1].endswith("/oauth/access_token"))
        self.assertEqual(first_call[2]["client_id"], "app-id")
        self.assertEqual(first_call[2]["client_secret"], "app-secret")
        self.assertEqual(first_call[2]["grant_type"], "client_credentials")
        self.assertEqual(second_call[0], "GET")
        self.assertTrue(second_call[1].endswith("/v1.0/oembed"))

    def test_auth_exchange_and_refresh_endpoints_are_versionless_and_method_correct(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.exchange_auth_code(code="auth-code")

        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["url"], "https://graph.threads.net/oauth/access_token")
        self.assertEqual(captured["data"]["grant_type"], "authorization_code")
        self.assertEqual(captured["data"]["code"], "auth-code")
        self.assertNotIn("access_token", captured["data"])

        captured2, fake_request2 = self._capture()
        with patch.object(client._http, "request", side_effect=fake_request2):
            client.exchange_short_lived_token(short_token="short-token")

        self.assertEqual(captured2["method"], "GET")
        self.assertEqual(captured2["url"], "https://graph.threads.net/access_token")
        self.assertEqual(captured2["params"]["grant_type"], "th_exchange_token")
        self.assertEqual(captured2["params"]["access_token"], "short-token")

        captured3, fake_request3 = self._capture()
        with patch.object(client._http, "request", side_effect=fake_request3):
            client.refresh_long_lived_token(long_token="long-token")

        self.assertEqual(captured3["method"], "GET")
        self.assertEqual(captured3["url"], "https://graph.threads.net/refresh_access_token")
        self.assertEqual(captured3["params"]["grant_type"], "th_refresh_token")
        self.assertEqual(captured3["params"]["access_token"], "long-token")

    def test_manage_reply_uses_hide_api_param(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.manage_reply(threads_reply_id="reply-1", hide=False)

        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/reply-1/manage_reply")
        self.assertEqual(captured["params"]["hide"], "false")

    def test_manage_pending_reply_uses_approve_api_param(self) -> None:
        captured, fake_request = self._capture()
        cfg = self._mk_cfg()
        client = ThreadsAPIClient(cfg=cfg, env_file="/tmp/.env", timeout_s=30.0, verbose=False)
        with patch.object(client._http, "request", side_effect=fake_request):
            client.manage_pending_reply(threads_reply_id="reply-1", approve=True)

        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["url"], "https://graph.threads.net/v1.0/reply-1/manage_pending_reply")
        self.assertEqual(captured["params"]["approve"], "true")
