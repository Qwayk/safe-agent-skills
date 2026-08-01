from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from spaceship_safe_agent_cli.audit_log import AuditLogger


class TestAuditLog(unittest.TestCase):
    def test_audit_log_includes_context_and_redacts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "audit.jsonl"
            audit = AuditLogger(path=str(p), enabled=True)
            audit.bind_context(
                {
                    "tool": "qwayk-spaceship-safe-agent-cli",
                    "version": "0.0.0",
                    "command": "qwayk-spaceship-safe-agent-cli domains list",
                    "apply": False,
                    "yes": False,
                    "private_data": True,
                    "env_fingerprint": "http://example.invalid",
                }
            )
            audit.write(
                "test.event",
                {
                    "token": "SECRET",
                    "authCode": "TRANSFER-CODE",
                    "billing": "BILLING-CONTACT-CANARY",
                    "detail": "OPAQUE-PRIVATE-ERROR-CANARY",
                    "nested": {"api_key": "K", "safe": "ok"},
                },
            )
            audit.bind_context({"tool": "qwayk-spaceship-safe-agent-cli", "private_data": False})
            audit.write("nonprivate.error", {"error": "safe diagnostic", "detail": "safe detail"})
            audit.close()

            rows = p.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(rows), 2)
            obj = json.loads(rows[0])
            self.assertEqual(obj["tool"], "qwayk-spaceship-safe-agent-cli")
            self.assertEqual(obj["event"], "test.event")
            self.assertEqual(obj["payload"]["token"], "***REDACTED***")
            self.assertEqual(obj["payload"]["authCode"], "***REDACTED***")
            self.assertEqual(obj["payload"]["billing"], "***REDACTED***")
            self.assertEqual(obj["payload"]["detail"], "***REDACTED***")
            self.assertEqual(obj["payload"]["nested"]["api_key"], "***REDACTED***")
            self.assertEqual(obj["payload"]["nested"]["safe"], "ok")
            nonprivate = json.loads(rows[1])
            self.assertEqual(nonprivate["payload"]["error"], "safe diagnostic")
            self.assertEqual(nonprivate["payload"]["detail"], "safe detail")
