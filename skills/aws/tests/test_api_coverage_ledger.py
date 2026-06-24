from __future__ import annotations

import unittest
from pathlib import Path


class TestApiCoverageLedger(unittest.TestCase):
    def test_coverage_doc_has_boundary_summary_and_ledger(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "api_coverage.md").read_text(encoding="utf-8")

        self.assertIn("## Boundary", text)
        self.assertIn("## Inventory summary", text)
        self.assertIn("## Generated per-operation evidence", text)
        self.assertIn("## Safety and risk coverage", text)
        self.assertIn("## Exceptions ledger", text)
        self.assertIn("Packaged botocore data only", text)
        self.assertIn("official aws surfaces outside packaged botocore were not claimed", text.lower())
        self.assertIn("generated_named_command", text)
        self.assertNotIn("catch-all", text.lower())
        self.assertNotIn("raw bridge", text.lower())
        self.assertNotIn("call-anything", text.lower())
