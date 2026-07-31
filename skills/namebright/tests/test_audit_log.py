from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from namebright_safe_cli.audit_log import AuditLogger


class TestAuditLog(unittest.TestCase):
    def test_audit_log_redacts_sensitive_and_nested_fields(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "audit.jsonl"
            audit = AuditLogger(path=str(p), enabled=True)
            audit.bind_context(
                {
                    "tool": "namebright-safe-cli",
                    "version": "0.1.0",
                    "command": "namebright-safe-cli domains update",
                    "apply": False,
                    "yes": False,
                    "env_fingerprint": "http://example.invalid",
                }
            )
            audit.write(
                "safe.event",
                {
                    "token": "TKN",
                    "authorization": "Bearer xxx",
                    "tokens": "multi",
                    "verificationCode": "1234",
                    "accountBalance": "9.99",
                    "nested": {"clientSecret": "abc", "api_key": "k"},
                    "AuthCode": "auth",
                    "LinkAuthCode": "link",
                    "email": "user@example.com",
                    "safe": "ok",
                },
            )
            audit.close()

            payload = json.loads(p.read_text(encoding="utf-8").strip())
            self.assertEqual(payload["payload"]["token"], "***REDACTED***")
            self.assertEqual(payload["payload"]["authorization"], "***REDACTED***")
            self.assertEqual(payload["payload"]["tokens"], "***REDACTED***")
            self.assertEqual(payload["payload"]["verificationCode"], "***REDACTED***")
            self.assertEqual(payload["payload"]["accountBalance"], "***REDACTED***")
            self.assertEqual(payload["payload"]["nested"]["clientSecret"], "***REDACTED***")
            self.assertEqual(payload["payload"]["nested"]["api_key"], "***REDACTED***")
            self.assertEqual(payload["payload"]["AuthCode"], "***REDACTED***")
            self.assertEqual(payload["payload"]["LinkAuthCode"], "***REDACTED***")
            self.assertEqual(payload["payload"]["email"], "***REDACTED***")
            self.assertEqual(payload["payload"]["safe"], "ok")
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)
            self.assertEqual(p.parent.stat().st_mode & 0o777, 0o700)
