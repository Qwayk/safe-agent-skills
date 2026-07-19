from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xero_safe_agent_cli.auth import TokenStore


class TestOAuthTokens(unittest.TestCase):
    def test_status_is_safe_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            status = TokenStore(Path(directory) / "token.json").status()
            self.assertFalse(status["exists"])
            self.assertNotIn("access_token", status)

    def test_token_is_private_and_status_never_returns_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oauth" / "token.json"
            store = TokenStore(path)
            store.write(
                {
                    "access_token": "access-secret",
                    "refresh_token": "refresh-secret",
                    "expires_in": 1800,
                    "scope": "openid accounting.invoices.read",
                }
            )
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            rendered = str(store.status())
            self.assertNotIn("access-secret", rendered)
            self.assertNotIn("refresh-secret", rendered)
            self.assertIn("accounting.invoices.read", rendered)


if __name__ == "__main__":
    unittest.main()
