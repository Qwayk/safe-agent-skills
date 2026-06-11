from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sovrn_safe_agent_cli.audit_log import AuditLogger


class TestAuditRedaction(unittest.TestCase):
    def test_sensitive_bid_check_values_are_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            log_path = Path(d) / "audit.jsonl"
            logger = AuditLogger(path=str(log_path), enabled=True)
            logger.bind_context({"env_fingerprint": "commerce_secret=0|commerce_site_key=1|advertising_key=0|advertising_publisher=0"})
            logger.write(
                "commerce.links.bid_check",
                {
                    "params": {
                        "ip": "203.0.113.10",
                        "userAgent": "Mozilla/5.0",
                        "gdprConsent": "consent-string",
                        "cuid": "user-123",
                    }
                },
            )
            logger.close()
            text = log_path.read_text(encoding="utf-8")
            self.assertNotIn("203.0.113.10", text)
            self.assertNotIn("Mozilla/5.0", text)
            self.assertNotIn("consent-string", text)
            self.assertNotIn("user-123", text)
            self.assertIn("***REDACTED***", text)
