from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from sovrn_safe_agent_cli.cli import main
from sovrn_safe_agent_cli.http import HttpResponse
from sovrn_safe_agent_cli.sovrn_api import redact_url


class TestLiveCommandWiring(unittest.TestCase):
    def _env_file(self, root: Path, lines: list[str]) -> Path:
        path = root / ".env"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def _fake_response(self, url: str) -> HttpResponse:
        return HttpResponse(
            status=200,
            headers={"content-type": "application/json"},
            body=b'{"result":"ok"}',
            url=url,
        )

    def test_campaigns_uses_secret_header(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(Path(d), ["SOVRN_COMMERCE_SECRET_KEY=secret-123", "SOVRN_TIMEOUT_S=30"])
            response = self._fake_response("https://rest.viglink.com/api/account/campaigns/PRIMARY")
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response) as mock_request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "commerce", "campaigns", "get", "--search", "PRIMARY"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["auth_shape"], "commerce-secret-header")
            self.assertEqual(mock_request.call_args.args[0], "GET")
            self.assertEqual(mock_request.call_args.args[1], "https://rest.viglink.com/api/account/campaigns/PRIMARY")
            self.assertEqual(mock_request.call_args.kwargs["headers"]["Authorization"], "secret secret-123")

    def test_links_check_redacts_site_key_in_output(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(Path(d), ["SOVRN_COMMERCE_SITE_API_KEY=site-key-123", "SOVRN_TIMEOUT_S=30"])
            response = self._fake_response(redact_url("https://api.viglink.com/api/link/?out=https%3A%2F%2Fexample.com&key=site-key-123"))
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response) as mock_request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "commerce", "links", "check", "--url", "https://example.com"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["request"]["params"]["key"], "***REDACTED***")
            self.assertEqual(mock_request.call_args.kwargs["params"]["key"], "site-key-123")

    def test_merchant_groups_approved_builds_filters(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(Path(d), ["SOVRN_COMMERCE_SECRET_KEY=secret-123", "SOVRN_TIMEOUT_S=30"])
            response = self._fake_response("https://viglink.io/merchants/rates/summaries")
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response) as mock_request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "commerce",
                            "merchant-groups",
                            "approved",
                            "--campaign-id",
                            "44",
                            "--name",
                            "Walmart,Target",
                            "--program-type-filter",
                            "CPA",
                        ]
                    )
            self.assertEqual(rc, 0)
            body = mock_request.call_args.kwargs["json_body"]
            self.assertEqual(body["page"], 1)
            self.assertEqual(body["pageSize"], 1000)
            self.assertEqual(body["filters"][0]["type"], "NAME")
            self.assertEqual(body["filters"][0]["values"], ["Walmart", "Target"])
            self.assertEqual(body["filters"][1]["type"], "PROGRAM_TYPE")

    def test_transactions_passes_filter_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(Path(d), ["SOVRN_COMMERCE_SECRET_KEY=secret-123", "SOVRN_TIMEOUT_S=30"])
            response = self._fake_response("https://viglink.io/v1/reports/transactions")
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response) as mock_request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "commerce",
                            "reports",
                            "transactions",
                            "get",
                            "--click-date",
                            "2026-01-01",
                            "--campaign-ids",
                            "1,2",
                            "--merchant-group-ids",
                            "3,4",
                            "--program-type",
                            "CPA",
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertEqual(
                mock_request.call_args.kwargs["params"],
                {
                    "clickDate": "2026-01-01",
                    "campaignIds": "1,2",
                    "merchantGroupIds": "3,4",
                    "programType": "CPA",
                },
            )

    def test_merchant_delta_uses_etag_header(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(Path(d), ["SOVRN_COMMERCE_SECRET_KEY=secret-123", "SOVRN_TIMEOUT_S=30"])
            response = self._fake_response("https://viglink.io/merchants/rates/summaries/delta")
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response) as mock_request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "commerce",
                            "merchant-groups",
                            "delta",
                            "--campaign-id",
                            "44",
                            "--if-none-match",
                            "etag-123",
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertEqual(mock_request.call_args.kwargs["headers"]["If-None-Match"], "etag-123")
            self.assertEqual(mock_request.call_args.kwargs["params"]["campaignId"], 44)

    def test_coupons_mixed_auth_redacts_query_key(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(
                Path(d),
                [
                    "SOVRN_COMMERCE_SECRET_KEY=secret-123",
                    "SOVRN_COMMERCE_SITE_API_KEY=site-key-123",
                    "SOVRN_TIMEOUT_S=30",
                ],
            )
            response = self._fake_response(redact_url("https://viglink.io/coupons/product?api_key=site-key-123&product_url=https%3A%2F%2Fmerchant.example%2Fitem"))
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response) as mock_request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "commerce",
                            "coupons",
                            "product",
                            "get",
                            "--product-url",
                            "https://merchant.example/item",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["auth_shape"], "commerce-secret-header+commerce-site-api-key-query")
            self.assertEqual(payload["request"]["params"]["api_key"], "***REDACTED***")
            self.assertEqual(mock_request.call_args.kwargs["headers"]["Authorization"], "secret secret-123")

    def test_products_recommend_sends_content_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(Path(d), ["SOVRN_COMMERCE_SITE_API_KEY=site-key-123", "SOVRN_TIMEOUT_S=30"])
            response = self._fake_response(redact_url("https://shopping-gallery.prd-commerce.sovrnservices.com/ai-orchestration/products?apiKey=site-key-123&pageUrl=article-123"))
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response) as mock_request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "commerce",
                            "products",
                            "recommend",
                            "--page-url",
                            "article-123",
                            "--content",
                            "gift guide copy",
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertEqual(mock_request.call_args.kwargs["json_body"]["content"], "gift guide copy")
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["request"]["params"]["apiKey"], "***REDACTED***")

    def test_comparisons_path_redaction_hides_site_key(self) -> None:
        redacted = redact_url(
            "https://comparisons.sovrn.com/api/affiliate/v3.5/sites/site-key-123/compare/prices/usd_en/by/accuracy"
        )
        self.assertIn("/sites/***REDACTED***/compare/", redacted)

    def test_advertising_account_uses_header_and_publisher(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(
                Path(d),
                [
                    "SOVRN_ADVERTISING_API_KEY=adv-key-123",
                    "SOVRN_ADVERTISING_PUBLISHER_ID=9988",
                    "SOVRN_TIMEOUT_S=30",
                ],
            )
            response = self._fake_response("https://api.sovrn.com/reporting/advertising/publishers/9988/account")
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response) as mock_request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "advertising",
                            "reports",
                            "account",
                            "get",
                            "--start",
                            "2026-01-01T00:00:00Z",
                            "--end",
                            "2026-01-02T00:00:00Z",
                            "--metrics",
                            "publisherRevenue",
                            "--dimensions",
                            "auction",
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertEqual(mock_request.call_args.kwargs["headers"]["x-api-key"], "adv-key-123")
            self.assertIn("/publishers/9988/account", mock_request.call_args.args[1])

    def test_advertising_custom_and_domain_account_build_unique_paths(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(
                Path(d),
                [
                    "SOVRN_ADVERTISING_API_KEY=adv-key-123",
                    "SOVRN_ADVERTISING_PUBLISHER_ID=9988",
                    "SOVRN_TIMEOUT_S=30",
                ],
            )
            response = self._fake_response("https://api.sovrn.com/reporting/advertising/publishers/9988/")
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response) as mock_request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "advertising",
                            "reports",
                            "custom",
                            "get",
                            "--start",
                            "2026-01-01T00:00:00Z",
                            "--end",
                            "2026-01-02T00:00:00Z",
                            "--metrics",
                            "publisherRevenue",
                            "--dimensions",
                            "domain",
                            "--granularity",
                            "day",
                            "--domain",
                            "example.com",
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertEqual(mock_request.call_args.kwargs["params"]["granularity"], "day")
            self.assertEqual(mock_request.call_args.kwargs["params"]["domain"], "example.com")

            response2 = self._fake_response("https://api.sovrn.com/reporting/advertising/publishers/9988/domains/example.com/account")
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response2) as mock_request2:
                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "advertising",
                            "reports",
                            "domain-account",
                            "get",
                            "--domain-name",
                            "example.com",
                            "--start",
                            "2026-01-01T00:00:00Z",
                            "--end",
                            "2026-01-02T00:00:00Z",
                            "--metrics",
                            "publisherRevenue",
                            "--dimensions",
                            "auction",
                        ]
                    )
            self.assertEqual(rc2, 0)
            self.assertIn("/domains/example.com/account", mock_request2.call_args.args[1])

    def test_auth_check_does_not_print_publisher_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(
                Path(d),
                [
                    "SOVRN_ADVERTISING_API_KEY=adv-key-123",
                    "SOVRN_ADVERTISING_PUBLISHER_ID=9988",
                    "SOVRN_TIMEOUT_S=30",
                ],
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "check"])
            self.assertEqual(rc, 0)
            output = buf.getvalue()
            self.assertNotIn("9988", output)
            payload = json.loads(output)
            self.assertEqual(
                payload["auth_check"]["env_fingerprint"],
                "commerce_secret=0|commerce_site_key=0|advertising_key=1|advertising_publisher=1",
            )

    def test_bid_check_redacts_user_fields_in_output(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env_file(Path(d), ["SOVRN_COMMERCE_SITE_API_KEY=site-key-123", "SOVRN_TIMEOUT_S=30"])
            response = self._fake_response(redact_url("https://api.viglink.com/api/bid?key=site-key-123&out=https%3A%2F%2Fexample.com"))
            with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=response) as mock_request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "commerce",
                            "links",
                            "bid-check",
                            "--url",
                            "https://example.com",
                            "--user-ip",
                            "203.0.113.10",
                            "--user-agent",
                            "Mozilla/5.0",
                            "--referrer-url",
                            "https://publisher.example/article",
                            "--sub-id",
                            "https://publisher.example/subid",
                            "--gdpr-consent",
                            "consent-string",
                            "--ccpa-consent",
                            "1---",
                            "--gpp-consent",
                            "gpp-string",
                            "--cuid",
                            "user-123",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            for key in ("key", "ip", "userAgent", "referrerUrl", "subId", "gdprConsent", "ccpaConsent", "gppConsent", "cuid"):
                self.assertEqual(payload["request"]["params"][key], "***REDACTED***")
            self.assertEqual(mock_request.call_args.kwargs["params"]["ip"], "203.0.113.10")
