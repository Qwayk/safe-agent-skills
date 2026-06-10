from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from qwayk_woocommerce_safe_agent_cli.audit_log import AuditLogger


class TestAuditLog(unittest.TestCase):
    def test_audit_log_includes_context_and_redacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "audit.jsonl"
            audit = AuditLogger(path=str(path), enabled=True)
            audit.bind_context(
                {
                    "tool": "qwayk-woocommerce-safe-agent-cli",
                    "version": "0.1.0",
                    "command": "qwayk-woocommerce-safe-agent-cli coupons create",
                    "apply": False,
                    "yes": False,
                    "env_fingerprint": "https://shop.example.com/wp-json/wc/v3",
                }
            )
            audit.write(
                "test.event",
                {"token": "SECRET", "nested": {"api_key": "KEY", "safe": "ok"}},
            )
            audit.close()

            rows = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(rows), 1)
            payload = json.loads(rows[0])
            self.assertEqual(payload["tool"], "qwayk-woocommerce-safe-agent-cli")
            self.assertEqual(payload["event"], "test.event")
            self.assertEqual(payload["payload"]["token"], "***REDACTED***")
            self.assertEqual(payload["payload"]["nested"]["api_key"], "***REDACTED***")
            self.assertEqual(payload["payload"]["nested"]["safe"], "ok")
