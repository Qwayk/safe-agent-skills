from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from meta_ads_api_tool.audit_log import AuditLogger


class TestAuditLog(unittest.TestCase):
    def test_audit_log_includes_context_and_redacts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "audit.jsonl"
            audit = AuditLogger(path=str(p), enabled=True)
            audit.bind_context(
                {
                    "tool": "meta-ads-api-tool",
                    "version": "0.0.0",
                    "command": "meta-ads-api-tool auth check",
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
            self.assertEqual(obj["tool"], "meta-ads-api-tool")
            self.assertEqual(obj["event"], "test.event")
            self.assertEqual(obj["payload"]["token"], "***REDACTED***")
            self.assertEqual(obj["payload"]["nested"]["api_key"], "***REDACTED***")
            self.assertEqual(obj["payload"]["nested"]["safe"], "ok")
