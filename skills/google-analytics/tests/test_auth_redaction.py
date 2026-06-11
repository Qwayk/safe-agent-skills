from __future__ import annotations

import unittest

from ga4_api_tool.auth import auth_summary
from ga4_api_tool.config import Config
from ga4_api_tool.redaction import sanitize


class TestAuthRedaction(unittest.TestCase):
    def test_auth_summary_never_includes_secrets(self) -> None:
        cfg = Config(
            auth_mode="oauth_refresh_token",
            scopes=("scope1",),
            admin_base_url="https://admin.example/",
            data_base_url="https://data.example/",
            timeout_s=30.0,
            oauth_client_id="client-id",
            oauth_client_secret="client-secret-should-not-leak",
            oauth_refresh_token="refresh-token-should-not-leak",
            service_account_json=None,
        )
        summary = auth_summary(cfg)
        text = repr(summary)
        self.assertNotIn("client-secret-should-not-leak", text)
        self.assertNotIn("refresh-token-should-not-leak", text)
        self.assertTrue(summary["has_refresh_token"])

    def test_redaction_catches_ga4_measurement_protocol_secret(self) -> None:
        obj = {
            "secretValue": "shh",
            "authorization": "Bearer abc.def.ghi",
            "nested": {"refreshToken": "rt", "clientSecret": "cs", "ok": "x"},
        }
        safe = sanitize(obj)
        self.assertEqual(safe["secretValue"], "<REDACTED>")
        self.assertEqual(safe["authorization"], "<REDACTED>")
        self.assertEqual(safe["nested"]["refreshToken"], "<REDACTED>")
        self.assertEqual(safe["nested"]["clientSecret"], "<REDACTED>")
        self.assertEqual(safe["nested"]["ok"], "x")

    def test_redaction_does_not_over_redact_tokenish_structures(self) -> None:
        obj = {
            "auth": {"has_refresh_token": None},
            "oauth_token": {"exists": False, "path": ".state/token.json"},
            "refresh_token": "rt",
        }
        safe = sanitize(obj)
        self.assertIsNone(safe["auth"]["has_refresh_token"])
        self.assertIsInstance(safe["oauth_token"], dict)
        self.assertEqual(safe["oauth_token"]["exists"], False)
        self.assertEqual(safe["oauth_token"]["path"], ".state/token.json")
        self.assertEqual(safe["refresh_token"], "<REDACTED>")

        safe2 = sanitize({"oauth_token": "really-a-token"})
        self.assertEqual(safe2["oauth_token"], "<REDACTED>")
