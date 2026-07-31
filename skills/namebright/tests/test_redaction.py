from __future__ import annotations

import unittest

from namebright_safe_cli.redaction import redact_object, redact_string


class TestRedaction(unittest.TestCase):
    def test_recursive_case_insensitive_keys(self) -> None:
        value = {
            "Domain": {"AuthCode": "abc", "verification": "111", "AccountBalance": "100"},
            "contacts": [
                {"Email": "a@ex.com", "LinkAuthCode": "x"},
                {"AuthCode": "y", "Nested": {"LinkAuthCode": "l", "Token": "abc"}},
            ],
            "Meta": {"Token": "secret-token"},
        }
        safe = redact_object(value)
        self.assertEqual(safe["Domain"]["AuthCode"], "***REDACTED***")
        self.assertEqual(safe["Domain"]["verification"], "***REDACTED***")
        self.assertEqual(safe["Domain"]["AccountBalance"], "***REDACTED***")
        self.assertEqual(safe["contacts"][0]["Email"], "a@ex.com")
        self.assertEqual(safe["contacts"][0]["LinkAuthCode"], "***REDACTED***")
        self.assertEqual(safe["contacts"][1]["Nested"]["LinkAuthCode"], "***REDACTED***")
        self.assertEqual(safe["Meta"]["Token"], "***REDACTED***")

    def test_redact_pii_when_enabled(self) -> None:
        payload = {
            "Contact": {
                "Email": "a@ex.com",
                "EmailAddress": "billing@ex.com",
                "FirstName": "Ada",
                "LastName": "Lovelace",
                "Country": "US",
                "Phone": "+1",
                "Address1": "1 Main",
            },
        }
        safe_default = redact_object(payload)
        self.assertEqual(safe_default["Contact"]["Email"], "a@ex.com")

        safe_pii = redact_object(payload, redact_pii=True)
        self.assertEqual(safe_pii["Contact"]["Email"], "***REDACTED***")
        self.assertEqual(safe_pii["Contact"]["EmailAddress"], "***REDACTED***")
        self.assertEqual(safe_pii["Contact"]["FirstName"], "***REDACTED***")
        self.assertEqual(safe_pii["Contact"]["LastName"], "***REDACTED***")
        self.assertEqual(safe_pii["Contact"]["Phone"], "***REDACTED***")
        self.assertEqual(safe_pii["Contact"]["Country"], "***REDACTED***")

    def test_redact_string_values(self) -> None:
        safe = redact_string("Bearer abc", secret_values=("abc",))
        self.assertEqual(safe, "Bearer ***REDACTED***")
