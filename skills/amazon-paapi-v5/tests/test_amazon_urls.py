from __future__ import annotations

import unittest

from amazon_pa_api_tool.amazon_urls import build_affiliate_dp_link, extract_asin_from_url


class TestAmazonUrls(unittest.TestCase):
    def test_extract_asin_dp(self) -> None:
        self.assertEqual(
            extract_asin_from_url("https://www.amazon.com/dp/B000123456/ref=something"),
            "B000123456",
        )

    def test_extract_asin_gp_product(self) -> None:
        self.assertEqual(
            extract_asin_from_url("https://www.amazon.com/gp/product/B000ABCDEF/"),
            "B000ABCDEF",
        )

    def test_extract_amzn_to_refused(self) -> None:
        self.assertIsNone(extract_asin_from_url("https://amzn.to/3xxxxx"))

    def test_build_affiliate_link(self) -> None:
        url = build_affiliate_dp_link(marketplace="www.amazon.com", asin="b000abc123", partner_tag="mytag-20")
        self.assertEqual(url, "https://www.amazon.com/dp/B000ABC123/?tag=mytag-20")

