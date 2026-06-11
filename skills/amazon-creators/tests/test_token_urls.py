from __future__ import annotations

import unittest

from amazon_creators_api_tool.token_urls import default_token_url, token_endpoints_for_locale


class TestTokenUrls(unittest.TestCase):
    def test_default_token_url_v2_uses_core_endpoint(self) -> None:
        self.assertEqual(
            default_token_url("2.1", "us"),
            "https://creatorsapi.auth.us-east-1.amazoncognito.com/oauth2/token",
        )

    def test_default_token_url_v2_eu_region(self) -> None:
        self.assertEqual(
            default_token_url("2.2", "fr"),
            "https://creatorsapi.auth.eu-south-2.amazoncognito.com/oauth2/token",
        )

    def test_default_token_url_v3_uk(self) -> None:
        self.assertEqual(
            default_token_url("3.2", "uk"),
            "https://api.amazon.co.uk/auth/o2/token",
        )

    def test_default_token_url_unknown_version_falls_back(self) -> None:
        self.assertEqual(
            default_token_url("2", "us"),
            "https://creatorsapi.auth.us-east-1.amazoncognito.com/oauth2/token",
        )

    def test_token_endpoints_for_locale_includes_all_versions(self) -> None:
        eps = token_endpoints_for_locale("fr")
        self.assertEqual(eps["v2.1"], "https://creatorsapi.auth.us-east-1.amazoncognito.com/oauth2/token")
        self.assertEqual(eps["v2.2"], "https://creatorsapi.auth.eu-south-2.amazoncognito.com/oauth2/token")
        self.assertEqual(eps["v3.3"], "https://api.amazon.co.jp/auth/o2/token")
