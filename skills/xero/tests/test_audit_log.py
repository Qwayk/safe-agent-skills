from __future__ import annotations

import json
import unittest

from xero_safe_agent_cli.redaction import redact, safe_error


class TestRedaction(unittest.TestCase):
    def test_xero_secrets_and_sensitive_financial_fields_are_redacted(self) -> None:
        value = {
            "access_token": "access-secret",
            "refresh_token": "refresh-secret",
            "Contact": {"EmailAddress": "person@example.com"},
            "BankAccountNumber": "123456789",
            "InvoiceNumber": "INV-123",
        }
        rendered = json.dumps(redact(value, sensitive=True))
        self.assertNotIn("access-secret", rendered)
        self.assertNotIn("refresh-secret", rendered)
        self.assertNotIn("person@example.com", rendered)
        self.assertNotIn("123456789", rendered)
        self.assertNotIn("INV-123", rendered)

    def test_errors_scrub_bearer_and_basic_credentials(self) -> None:
        rendered = safe_error("Bearer abc.def.ghi Basic Y2xpZW50OnNlY3JldA==")
        self.assertNotIn("abc.def.ghi", rendered)
        self.assertNotIn("Y2xpZW50OnNlY3JldA", rendered)


if __name__ == "__main__":
    unittest.main()
