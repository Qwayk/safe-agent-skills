from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from awin_advertiser_safe_agent_cli.audit_log import AuditLogger


class TestAuditLog(unittest.TestCase):
    def test_audit_log_includes_context_and_redacts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "audit.jsonl"
            audit = AuditLogger(path=str(p), enabled=True)
            audit.bind_context(
                {
                    "tool": "awin-advertiser-safe-cli",
                    "version": "0.1.1",
                    "command": "awin-advertiser-safe-cli auth check",
                    "apply": False,
                    "yes": False,
                    "env_fingerprint": "https://api.awin.com",
                }
            )
            audit.write(
                "auth.check",
                {
                    "token": "SECRET",
                    "nested": {"api_key": "K", "safe": "ok"},
                    "error": "HTTP 401 for https://api.awin.com/x?accessToken=SECRET Authorization: Bearer SECRET",
                },
            )
            audit.close()

            rows = p.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(rows), 1)
            obj = json.loads(rows[0])
            self.assertEqual(obj["tool"], "awin-advertiser-safe-cli")
            self.assertEqual(obj["event"], "auth.check")
            self.assertEqual(obj["payload"]["token"], "***REDACTED***")
            self.assertEqual(obj["payload"]["nested"]["api_key"], "***REDACTED***")
            self.assertEqual(obj["payload"]["nested"]["safe"], "ok")
            self.assertNotIn("SECRET", obj["payload"]["error"])
            self.assertIn("accessToken=***REDACTED***", obj["payload"]["error"])
