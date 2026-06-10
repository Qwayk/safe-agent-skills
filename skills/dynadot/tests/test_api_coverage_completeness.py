from __future__ import annotations

import unittest
from pathlib import Path


class TestApiCoverageCompleteness(unittest.TestCase):
    def test_no_missing_rows_in_coverage_ledger(self) -> None:
        root = Path(__file__).resolve().parents[1]
        md = (root / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        self.assertNotIn("| Missing |", md, "Coverage ledger still contains Missing rows")

