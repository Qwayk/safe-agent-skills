from __future__ import annotations

import unittest

from sovrn_safe_agent_cli.cli import build_parser


class TestCliSurface(unittest.TestCase):
    def test_all_coverage_commands_parse(self) -> None:
        parser = build_parser()
        cases = [
            ["commerce", "campaigns", "get", "--search", "PRIMARY"],
            ["commerce", "links", "check", "--url", "https://example.com/product"],
            ["commerce", "links", "bid-check", "--url", "https://example.com/product", "--user-ip", "203.0.113.10", "--user-agent", "Mozilla/5.0"],
            ["commerce", "reports", "transactions", "get"],
            ["commerce", "reports", "pages", "get", "--click-date-start", "2026-01-01", "--click-date-end", "2026-01-02"],
            ["commerce", "reports", "links", "get", "--click-date-start", "2026-01-01", "--click-date-end", "2026-01-02"],
            ["commerce", "reports", "merchants", "get", "--click-date-start", "2026-01-01", "--click-date-end", "2026-01-02"],
            ["commerce", "reports", "merchants-by-date", "get", "--click-date-start", "2026-01-01", "--click-date-end", "2026-01-02"],
            ["commerce", "reports", "merchandise", "get", "--click-date-start", "2026-01-01", "--click-date-end", "2026-01-02"],
            ["commerce", "reports", "networks", "get", "--click-date-start", "2026-01-01", "--click-date-end", "2026-01-02"],
            ["commerce", "reports", "cuids", "get", "--click-date-start", "2026-01-01", "--click-date-end", "2026-01-02"],
            ["commerce", "merchant-groups", "approved", "--campaign-id", "1"],
            ["commerce", "merchant-groups", "delta", "--campaign-id", "1", "--since", "2026-01-01T00:00:00Z"],
            ["commerce", "coupons", "product", "get", "--product-url", "https://merchant.example/item"],
            ["commerce", "products", "recommend", "--page-url", "article-123", "--content", "gift guide copy"],
            ["commerce", "comparisons", "prices", "search", "--market", "usd_en", "--plainlink", "https://merchant.example/item"],
            ["advertising", "reports", "account", "get", "--start", "2026-01-01T00:00:00Z", "--end", "2026-01-02T00:00:00Z", "--metrics", "publisherRevenue", "--dimensions", "auction"],
            ["advertising", "reports", "bid", "get", "--start", "2026-01-01T00:00:00Z", "--end", "2026-01-02T00:00:00Z", "--metrics", "publisherRevenue", "--dimensions", "advertiser"],
            ["advertising", "reports", "breakout", "get", "--start", "2026-01-01T00:00:00Z", "--end", "2026-01-02T00:00:00Z", "--metrics", "publisherRevenue"],
            ["advertising", "reports", "domain-account", "get", "--domain-name", "example.com", "--start", "2026-01-01T00:00:00Z", "--end", "2026-01-02T00:00:00Z", "--metrics", "publisherRevenue", "--dimensions", "auction"],
            ["advertising", "reports", "domain-bid", "get", "--domain-name", "example.com", "--start", "2026-01-01T00:00:00Z", "--end", "2026-01-02T00:00:00Z", "--metrics", "publisherRevenue", "--dimensions", "advertiser"],
            ["advertising", "reports", "custom", "get", "--start", "2026-01-01T00:00:00Z", "--end", "2026-01-02T00:00:00Z", "--metrics", "publisherRevenue", "--dimensions", "domain", "--granularity", "day"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(hasattr(args, "func"))
