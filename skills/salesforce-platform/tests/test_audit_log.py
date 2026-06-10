from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests import bootstrap  # noqa: F401

from salesforce_platform_safe_agent_cli.audit_log import AuditLogger


class TestAuditLog(unittest.TestCase):
    def test_audit_log_includes_context_and_redacts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "audit.jsonl"
            audit = AuditLogger(path=str(p), enabled=True)
            audit.bind_context(
                {
                    "tool": "qwayk-salesforce-platform-safe-agent-cli",
                    "version": "0.0.0",
                    "command": "qwayk-salesforce-platform-safe-agent-cli versions list",
                    "apply": True,
                    "yes": False,
                    "env_fingerprint": "https://example.my.salesforce.com",
                }
            )
            audit.write(
                "test.event",
                {"token": "SECRET", "nested": {"api_key": "K", "safe": "ok"}},
            )
            audit.close()

            rows = p.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(rows), 1)
            obj = json.loads(rows[0])
            self.assertEqual(obj["tool"], "qwayk-salesforce-platform-safe-agent-cli")
            self.assertEqual(obj["event"], "test.event")
            self.assertEqual(obj["payload"]["token"], "***REDACTED***")
            self.assertEqual(obj["payload"]["nested"]["api_key"], "***REDACTED***")
            self.assertEqual(obj["payload"]["nested"]["safe"], "ok")
