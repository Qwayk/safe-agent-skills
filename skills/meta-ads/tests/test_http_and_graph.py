from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import requests

from meta_ads_api_tool.cli import main
from meta_ads_api_tool.config import Config
from meta_ads_api_tool.graph import GraphClient
from meta_ads_api_tool.http import HttpClient


def _resp(*, url: str, status: int, obj: dict) -> requests.Response:
    r = requests.Response()
    r.status_code = status
    r._content = json.dumps(obj).encode("utf-8")  # type: ignore[attr-defined]
    r.url = url
    r.headers = {}
    return r


class TestHttpAndGraph(unittest.TestCase):
    def test_get_only_refuses_post(self) -> None:
        http = HttpClient(timeout_s=1.0, verbose=False, user_agent="x")
        with self.assertRaises(Exception) as cm:
            http.request("POST", "https://example.invalid")
        self.assertIn("Refusing non-GET", str(cm.exception))

    def test_verbose_logging_redacts_access_token(self) -> None:
        http = HttpClient(timeout_s=1.0, verbose=True, user_agent="x")
        http._session.request = mock.Mock(  # type: ignore[attr-defined]
            return_value=_resp(
                url="https://graph.facebook.com/v24.0/me?access_token=SECRET",
                status=200,
                obj={"ok": True},
            )
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            _ = http.request("GET", "https://graph.facebook.com/v24.0/me?access_token=SECRET")
        txt = buf.getvalue()
        self.assertNotIn("SECRET", txt)
        self.assertIn("***REDACTED***", txt)

    def test_verbose_logging_redacts_access_token_on_request_exception(self) -> None:
        http = HttpClient(timeout_s=1.0, verbose=True, user_agent="x")
        http._session.request = mock.Mock(  # type: ignore[attr-defined]
            side_effect=requests.RequestException(
                "boom https://graph.facebook.com/v24.0/me?access_token=SECRET"
            )
        )
        buf = io.StringIO()
        with redirect_stderr(buf), self.assertRaises(RuntimeError) as cm:
            _ = http.request("GET", "https://graph.facebook.com/v24.0/me?access_token=SECRET")
        txt = buf.getvalue()
        self.assertNotIn("SECRET", txt)
        self.assertIn("***REDACTED***", txt)
        self.assertNotIn("SECRET", str(cm.exception))
        self.assertIn("***REDACTED***", str(cm.exception))

    def test_pagination_merges_pages(self) -> None:
        cfg = Config(
            base_url="https://graph.facebook.com",
            api_version="v24.0",
            access_token="SECRET",
            ad_account_id=None,
            timeout_s=1.0,
            max_retries=0,
        )
        http = HttpClient(timeout_s=1.0, verbose=False, user_agent="x")

        first_url = "https://graph.facebook.com/v24.0/act_1/campaigns"
        next_url = "https://graph.facebook.com/v24.0/act_1/campaigns?after=abc&access_token=SECRET"

        http._session.request = mock.Mock(  # type: ignore[attr-defined]
            side_effect=[
                _resp(
                    url=first_url,
                    status=200,
                    obj={"data": [{"id": "1"}, {"id": "2"}], "paging": {"next": next_url}},
                ),
                _resp(url=next_url, status=200, obj={"data": [{"id": "3"}], "paging": {}}),
            ]
        )

        graph = GraphClient(cfg=cfg, http=http)
        res = graph.list_edge(object_id="act_1", edge="campaigns", params={"limit": "2"}, max_pages=10, max_items=0)
        self.assertEqual([x["id"] for x in res.data], ["1", "2", "3"])
        self.assertEqual(res.raw_pages, 2)

    def test_paging_urls_are_redacted_before_returning(self) -> None:
        cfg = Config(
            base_url="https://graph.facebook.com",
            api_version="v24.0",
            access_token="SECRET",
            ad_account_id=None,
            timeout_s=1.0,
            max_retries=0,
        )
        http = HttpClient(timeout_s=1.0, verbose=False, user_agent="x")

        first_url = "https://graph.facebook.com/v24.0/act_1/campaigns"
        next_url = "https://graph.facebook.com/v24.0/act_1/campaigns?after=abc&access_token=SECRET"

        http._session.request = mock.Mock(  # type: ignore[attr-defined]
            return_value=_resp(
                url=first_url,
                status=200,
                obj={"data": [{"id": "1"}], "paging": {"next": next_url}},
            )
        )

        graph = GraphClient(cfg=cfg, http=http)
        res = graph.list_edge(object_id="act_1", edge="campaigns", params={"limit": "2"}, max_pages=1, max_items=0)
        self.assertIsInstance(res.paging, dict)
        assert res.paging is not None
        self.assertNotIn("SECRET", json.dumps(res.paging))
        self.assertIn("***REDACTED***", json.dumps(res.paging))

    def test_pagination_falls_back_to_after_cursor(self) -> None:
        cfg = Config(
            base_url="https://graph.facebook.com",
            api_version="v24.0",
            access_token="SECRET",
            ad_account_id=None,
            timeout_s=1.0,
            max_retries=0,
        )
        http = HttpClient(timeout_s=1.0, verbose=False, user_agent="x")

        first_url = "https://graph.facebook.com/v24.0/act_1/campaigns"
        second_url = "https://graph.facebook.com/v24.0/act_1/campaigns?after=abc"

        http._session.request = mock.Mock(  # type: ignore[attr-defined]
            side_effect=[
                _resp(
                    url=first_url,
                    status=200,
                    obj={"data": [{"id": "1"}], "paging": {"cursors": {"after": "abc"}}},
                ),
                _resp(url=second_url, status=200, obj={"data": [{"id": "2"}], "paging": {}}),
            ]
        )

        graph = GraphClient(cfg=cfg, http=http)
        res = graph.list_edge(object_id="act_1", edge="campaigns", params={"limit": "2"}, max_pages=10, max_items=0)
        self.assertEqual([x["id"] for x in res.data], ["1", "2"])
        self.assertEqual(res.raw_pages, 2)

        self.assertGreaterEqual(http._session.request.call_count, 2)  # type: ignore[attr-defined]
        second_call = http._session.request.mock_calls[1]  # type: ignore[attr-defined]
        params = second_call.kwargs.get("params") or {}
        self.assertEqual(params.get("after"), "abc")
        self.assertEqual(params.get("limit"), "2")
        self.assertEqual(params.get("access_token"), "SECRET")

    def test_remote_api_error_is_clean_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "META_ADS_BASE_URL=https://graph.facebook.com",
                        "META_ADS_API_VERSION=v24.0",
                        "META_ADS_ACCESS_TOKEN=SECRET",
                        "META_ADS_TIMEOUT_S=1",
                        "META_ADS_MAX_RETRIES=0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            bad_url = "https://graph.facebook.com/v24.0/me?fields=id,name"

            with mock.patch.object(HttpClient, "__init__", return_value=None), mock.patch.object(  # type: ignore[misc]
                HttpClient,
                "request",
                side_effect=lambda method, url, **kwargs: (  # type: ignore[no-untyped-def]
                    # Fake HttpClient.request returning an object with json/url/headers/status/body.
                    # Reuse GraphClient via main() to validate the error is surfaced cleanly.
                    type(
                        "R",
                        (),
                        {
                            "status": 400,
                            "headers": {},
                            "body": json.dumps({"error": {"message": "Bad token", "type": "OAuthException", "code": 190}}).encode(
                                "utf-8"
                            ),
                            "url": bad_url,
                            "json": lambda self: json.loads(self.body.decode("utf-8")),  # type: ignore[no-untyped-def]
                        },
                    )()
                ),
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])
                self.assertEqual(rc, 1)
                payload = json.loads(buf.getvalue())
                self.assertFalse(payload["ok"])
                self.assertEqual(payload["error_type"], "RemoteApiError")
