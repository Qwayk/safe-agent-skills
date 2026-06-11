from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

import requests

from awin_publisher_safe_agent_cli.cli import main


def _json_response(method: str, url: str, params: dict[str, Any], payload: object, *, status: int = 200) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps(payload).encode("utf-8")
    response.headers["content-type"] = "application/json"
    response.url = requests.Request(method=method, url=url, params=params).prepare().url or url
    return response


def _bytes_response(method: str, url: str, params: dict[str, Any], body: bytes, *, content_type: str, status: int = 200) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response._content = body
    response.headers["content-type"] = content_type
    response.url = requests.Request(method=method, url=url, params=params).prepare().url or url
    return response


def _write_env(root: str, *lines: str) -> str:
    env_file = os.path.join(root, ".env")
    with open(env_file, "w", encoding="utf-8") as fh:
        for line in lines:
            fh.write(line.rstrip() + "\n")
    return env_file


class TestPublisherSurface(unittest.TestCase):
    def test_offers_list_posts_filters_and_pagination(self) -> None:
        captured: dict[str, Any] = {}

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            def fake_request(method: str, url: str, headers=None, params=None, json=None, **kwargs: Any) -> requests.Response:
                captured["method"] = method
                captured["url"] = url
                captured["headers"] = headers or {}
                captured["params"] = params or {}
                captured["json"] = json or {}
                return _json_response(method, url, params or {}, {"offers": []})

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, "AWIN_API_TOKEN=TOKEN_OFFERS")
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "offers",
                            "list",
                            "--publisher-id",
                            "777",
                            "--advertiser-ids",
                            "11,22",
                            "--exclusive-only",
                            "--membership",
                            "joined",
                            "--region-codes",
                            "gb,us",
                            "--status",
                            "active",
                            "--type",
                            "voucher",
                            "--updated-since",
                            "2026-06-01",
                            "--page",
                            "2",
                            "--page-size",
                            "50",
                        ]
                    )

            out = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(captured["method"], "POST")
            self.assertTrue(captured["url"].endswith("/publisher/777/promotions"))
            self.assertEqual(captured["params"]["accessToken"], "TOKEN_OFFERS")
            self.assertEqual(captured["json"]["filters"]["advertiserIds"], [11, 22])
            self.assertEqual(captured["json"]["filters"]["membership"], "joined")
            self.assertEqual(captured["json"]["filters"]["regionCodes"], ["GB", "US"])
            self.assertEqual(captured["json"]["pagination"]["page"], 2)
            self.assertEqual(captured["json"]["pagination"]["pageSize"], 50)
            self.assertEqual(out["operation"], "offers.list")

    def test_transactions_list_uses_trailing_slash_endpoint(self) -> None:
        captured: dict[str, Any] = {}

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            def fake_request(method: str, url: str, headers=None, params=None, **kwargs: Any) -> requests.Response:
                captured["method"] = method
                captured["url"] = url
                captured["params"] = params or {}
                return _json_response(method, url, params or {}, [{"id": "t1"}])

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, "AWIN_API_TOKEN=TOKEN_TX")
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "transactions",
                            "list",
                            "--publisher-id",
                            "777",
                            "--start-date",
                            "2026-06-01T00:00:00Z",
                            "--end-date",
                            "2026-06-02T00:00:00Z",
                            "--timezone",
                            "UTC",
                            "--advertiser-ids",
                            "55",
                            "--status",
                            "approved",
                            "--show-basket-products",
                        ]
                    )

            out = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(captured["url"].endswith("/publishers/777/transactions/"))
            self.assertEqual(captured["params"]["advertiserId"], "55")
            self.assertEqual(captured["params"]["status"], "approved")
            self.assertEqual(captured["params"]["showBasketProducts"], "true")
            self.assertEqual(out["operation"], "transactions.list")

    def test_transactions_by_ids_uses_non_trailing_slash_endpoint(self) -> None:
        captured: dict[str, Any] = {}

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            def fake_request(method: str, url: str, headers=None, params=None, **kwargs: Any) -> requests.Response:
                captured["url"] = url
                captured["params"] = params or {}
                return _json_response(method, url, params or {}, [{"id": "1"}])

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, "AWIN_API_TOKEN=TOKEN_TX_IDS")
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "transactions",
                            "by-ids",
                            "--publisher-id",
                            "777",
                            "--ids",
                            "100,200",
                        ]
                    )

            out = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(captured["url"].endswith("/publishers/777/transactions"))
            self.assertFalse(captured["url"].endswith("/publishers/777/transactions/"))
            self.assertEqual(captured["params"]["ids"], "100,200")
            self.assertEqual(out["metadata"]["ids"], ["100", "200"])

    def test_transaction_queries_list_uses_singular_publisher_path(self) -> None:
        captured: dict[str, Any] = {}

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            def fake_request(method: str, url: str, headers=None, params=None, **kwargs: Any) -> requests.Response:
                captured["url"] = url
                captured["params"] = params or {}
                return _json_response(method, url, params or {}, {"pageItems": []})

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, "AWIN_API_TOKEN=TOKEN_TQ")
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "transaction-queries",
                            "list",
                            "--publisher-id",
                            "777",
                            "--start-date",
                            "2026-06-01T00:00:00Z",
                            "--end-date",
                            "2026-06-10T00:00:00Z",
                            "--advertiser-ids",
                            "5,6",
                            "--click-refs",
                            "alpha,beta",
                            "--statuses",
                            "pending,declined",
                            "--page-number",
                            "2",
                            "--page-size",
                            "20",
                        ]
                    )

            out = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(captured["url"].endswith("/publisher/777/transactionqueries"))
            self.assertEqual(captured["params"]["advertiserIds"], "5,6")
            self.assertEqual(captured["params"]["clickRefs"], "alpha,beta")
            self.assertEqual(captured["params"]["statuses"], "pending,declined")
            self.assertEqual(out["metadata"]["page_size"], 20)

    def test_reports_commands_send_expected_paths(self) -> None:
        captured_urls: list[str] = []

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            def fake_request(method: str, url: str, headers=None, params=None, **kwargs: Any) -> requests.Response:
                captured_urls.append(url)
                return _json_response(method, url, params or {}, {"body": []})

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, "AWIN_API_TOKEN=TOKEN_REPORTS")
                for argv in (
                    [
                        "reports",
                        "advertiser",
                        "--publisher-id",
                        "777",
                        "--start-date",
                        "2026-06-01",
                        "--end-date",
                        "2026-06-02",
                        "--region",
                        "GB",
                    ],
                    [
                        "reports",
                        "campaign",
                        "--publisher-id",
                        "777",
                        "--start-date",
                        "2026-06-01",
                        "--end-date",
                        "2026-06-02",
                        "--region",
                        "GB",
                        "--advertiser-ids",
                        "9,10",
                        "--campaign",
                        "summer",
                        "--include-numbers-without-campaign",
                        "--interval",
                        "day",
                    ],
                    [
                        "reports",
                        "creative",
                        "--publisher-id",
                        "777",
                        "--start-date",
                        "2026-06-01",
                        "--end-date",
                        "2026-06-02",
                        "--region",
                        "GB",
                    ],
                ):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(["--output", "json", "--env-file", env_file, *argv])
                    self.assertEqual(rc, 0)

            self.assertTrue(captured_urls[0].endswith("/publishers/777/reports/advertiser"))
            self.assertTrue(captured_urls[1].endswith("/publishers/777/reports/campaign"))
            self.assertTrue(captured_urls[2].endswith("/publishers/777/reports/creative"))

    def test_linkbuilder_generate_and_quota(self) -> None:
        captured: list[dict[str, Any]] = []

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            def fake_request(method: str, url: str, headers=None, params=None, json=None, **kwargs: Any) -> requests.Response:
                captured.append({"method": method, "url": url, "params": params or {}, "json": json})
                payload = {"url": "https://www.awin1.com/example"} if "generate" in url else {"limit": "100", "usage": 5}
                return _json_response(method, url, params or {}, payload)

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, "AWIN_API_TOKEN=TOKEN_LINKS")

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "linkbuilder",
                            "generate",
                            "--publisher-id",
                            "777",
                            "--advertiser-id",
                            "55",
                            "--destination-url",
                            "https://example.com/product",
                            "--campaign",
                            "summer",
                            "--clickref",
                            "ref123",
                            "--shorten",
                        ]
                    )
                self.assertEqual(rc, 0)
                out_generate = json.loads(buf.getvalue())

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "linkbuilder",
                            "quota",
                            "--publisher-id",
                            "777",
                        ]
                    )
                self.assertEqual(rc, 0)
                out_quota = json.loads(buf.getvalue())

            self.assertTrue(captured[0]["url"].endswith("/publishers/777/linkbuilder/generate"))
            self.assertEqual(captured[0]["json"]["parameters"]["campaign"], "summer")
            self.assertEqual(captured[0]["json"]["parameters"]["clickref"], "ref123")
            self.assertTrue(captured[0]["json"]["shorten"])
            self.assertTrue(captured[1]["url"].endswith("/publishers/777/linkbuilder/quota"))
            self.assertEqual(out_generate["operation"], "linkbuilder.generate")
            self.assertEqual(out_quota["operation"], "linkbuilder.quota")

    def test_linkbuilder_generate_batch_reads_json_file(self) -> None:
        captured: dict[str, Any] = {}

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            def fake_request(method: str, url: str, headers=None, params=None, json=None, **kwargs: Any) -> requests.Response:
                captured["json"] = json or {}
                return _json_response(method, url, params or {}, {"responses": []})

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, "AWIN_API_TOKEN=TOKEN_BATCH")
                requests_path = Path(td) / "batch.json"
                requests_path.write_text(
                    json.dumps(
                        {
                            "requests": [
                                {"advertiserId": 55, "destinationUrl": "https://example.com/a"},
                                {"advertiserId": 66, "destinationUrl": "https://example.com/b"},
                            ]
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
                            env_file,
                            "linkbuilder",
                            "generate-batch",
                            "--publisher-id",
                            "777",
                            "--requests-file",
                            str(requests_path),
                        ]
                    )

            out = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(len(captured["json"]["requests"]), 2)
            self.assertEqual(out["metadata"]["requests_count"], 2)

    def test_feed_download_commands_write_files(self) -> None:
        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            calls: list[dict[str, Any]] = []

            def fake_request(method: str, url: str, headers=None, params=None, **kwargs: Any) -> requests.Response:
                calls.append({"url": url, "headers": headers or {}, "params": params or {}})
                if "/datafeed/list/" in url:
                    csv_body = b"Advertiser ID,Feed ID,URL\n9,42,https://datafeed.api.productserve.com/datafeed/download/apikey/KEY/fid/42/format/csv/\n"
                    return _bytes_response(method, url, params or {}, csv_body, content_type="text/csv")
                if "/awinfeeds/download/" in url:
                    return _bytes_response(method, url, params or {}, b'{"id":1}\n', content_type="application/x-jsonlines")
                return _bytes_response(method, url, params or {}, b"sku,name\n1,Demo\n", content_type="text/csv")

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(
                    td,
                    "AWIN_API_TOKEN=TOKEN_FEEDS",
                    "AWIN_FEED_API_KEY=FEEDKEY",
                )
                enhanced_out = Path(td) / "enhanced.jsonl"
                legacy_list_out = Path(td) / "legacy-list.csv"
                legacy_feed_out = Path(td) / "legacy-feed.csv"

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "feeds",
                            "enhanced-download",
                            "--publisher-id",
                            "777",
                            "--advertiser-id",
                            "55",
                            "--locale",
                            "en_GB",
                            "--out",
                            str(enhanced_out),
                        ]
                    )
                self.assertEqual(rc, 0)

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "feeds",
                            "legacy-list",
                            "--out",
                            str(legacy_list_out),
                        ]
                    )
                self.assertEqual(rc, 0)

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "feeds",
                            "legacy-download",
                            "--feed-id",
                            "42",
                            "--out",
                            str(legacy_feed_out),
                        ]
                    )
                self.assertEqual(rc, 0)

                self.assertTrue(enhanced_out.exists())
                self.assertTrue(legacy_list_out.exists())
                self.assertTrue(legacy_feed_out.exists())

            self.assertTrue(calls[0]["url"].endswith("/publishers/777/awinfeeds/download/55-retail-en_GB.jsonl"))
            self.assertTrue(calls[1]["url"].endswith("/datafeed/list/apikey/FEEDKEY"))

    def test_proof_of_purchase_create_supports_dry_run_and_apply(self) -> None:
        requests_seen: list[dict[str, Any]] = []

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            def fake_request(method: str, url: str, headers=None, params=None, json=None, **kwargs: Any) -> requests.Response:
                requests_seen.append({"method": method, "url": url, "headers": headers or {}, "json": json or {}})
                return _json_response(method, url, params or {}, {"accepted": True})

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, "AWIN_PROOF_OF_PURCHASE_API_KEY=POPKEY")
                orders_path = Path(td) / "orders.json"
                orders_path.write_text(
                    json.dumps(
                        {
                            "orders": [
                                {
                                    "orderReference": "ORD-1",
                                    "amount": 123.45,
                                    "currency": "EUR",
                                    "transactionTime": 1762859931,
                                }
                            ]
                        }
                    ),
                    encoding="utf-8",
                )
                plan_path = Path(td) / "plan.json"
                receipt_path = Path(td) / "receipt.json"

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "--no-artifacts",
                            "--plan-out",
                            str(plan_path),
                            "proof-of-purchase",
                            "orders",
                            "create",
                            "--publisher-id",
                            "777",
                            "--advertiser-id",
                            "55",
                            "--orders-file",
                            str(orders_path),
                        ]
                    )
                dry_run = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(dry_run["dry_run"])
                self.assertTrue(plan_path.exists())
                self.assertEqual(requests_seen, [])

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "--no-artifacts",
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                            "--receipt-out",
                            str(receipt_path),
                            "proof-of-purchase",
                            "orders",
                            "create",
                            "--publisher-id",
                            "777",
                            "--advertiser-id",
                            "55",
                            "--orders-file",
                            str(orders_path),
                        ]
                    )
                applied = json.loads(buf.getvalue())
                receipt_exists = receipt_path.exists()

            self.assertEqual(rc, 0)
            self.assertFalse(applied["dry_run"])
            self.assertTrue(receipt_exists)
            self.assertEqual(requests_seen[0]["method"], "POST")
            self.assertTrue(requests_seen[0]["url"].endswith("/publishers/777/advertiser/55/orders"))
            self.assertEqual(requests_seen[0]["headers"]["x-api-key"], "POPKEY")
            self.assertEqual(requests_seen[0]["json"]["orders"][0]["orderReference"], "ORD-1")

    def test_proof_of_purchase_apply_refuses_without_plan_in(self) -> None:
        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, "AWIN_PROOF_OF_PURCHASE_API_KEY=POPKEY")
                orders_path = Path(td) / "orders.json"
                orders_path.write_text(
                    json.dumps(
                        {
                            "orders": [
                                {
                                    "orderReference": "ORD-1",
                                    "amount": 123.45,
                                    "currency": "EUR",
                                    "transactionTime": 1762859931,
                                }
                            ]
                        }
                    ),
                    encoding="utf-8",
                )
                receipt_path = Path(td) / "receipt.json"

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "--no-artifacts",
                            "--apply",
                            "--yes",
                            "--receipt-out",
                            str(receipt_path),
                            "proof-of-purchase",
                            "orders",
                            "create",
                            "--publisher-id",
                            "777",
                            "--advertiser-id",
                            "55",
                            "--orders-file",
                            str(orders_path),
                        ]
                    )
                receipt_exists = receipt_path.exists()

            out = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(out["refused"])
            self.assertIn("--plan-in", out["reason"])
            self.assertFalse(receipt_exists)
            mocked_request.assert_not_called()
