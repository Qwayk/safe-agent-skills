from __future__ import annotations

import unittest

from namebright_safe_cli.oauth_tokens import TokenCache


class TestOAuthTokens(unittest.TestCase):
    def test_set_and_get_cached_token(self) -> None:
        cache = TokenCache()
        token_payload = {"access_token": "in-memory", "expires_in": 900, "scope": "x"}
        cache.set(token_payload, now=1700000000.0)
        self.assertEqual(cache.get(now=1700000000.0), "in-memory")
        status = cache.status(now=1700000000.0)
        self.assertTrue(status.exists)
        self.assertIn("scope", status.fields)
        self.assertEqual(status.has_refresh_token, None)

    def test_refresh_token_reflected(self) -> None:
        cache = TokenCache()
        token_payload = {"access_token": "token", "expires_in": 900, "refresh_token": "refresh-value"}
        cache.set(token_payload, now=1700000000.0)
        status = cache.status(now=1700000000.0)
        self.assertTrue(status.has_refresh_token)

    def test_cache_expires_with_max_lifetime(self) -> None:
        cache = TokenCache()
        cache.set({"access_token": "token", "expires_in": 999999}, now=1700000000.0)
        self.assertEqual(cache.get(now=1700000000.0), "token")
        self.assertIsNone(cache.get(now=1700001800.0))
        self.assertIsNone(cache.get(now=1700001801.0))

    def test_two_client_instances_do_not_share_state(self) -> None:
        cache_a = TokenCache()
        cache_b = TokenCache()
        cache_a.set({"access_token": "a", "expires_in": 900}, now=1700000000.0)
        self.assertIsNotNone(cache_a.get(now=1700000000.0))
        self.assertIsNone(cache_b.get(now=1700000000.0))

    def test_invalid_payload_rejected(self) -> None:
        cache = TokenCache()
        with self.assertRaises(ValueError):
            cache.set({"not_access_token": "x"}, now=1700000000.0)
