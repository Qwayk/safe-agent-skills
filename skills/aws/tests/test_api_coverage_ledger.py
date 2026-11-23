from __future__ import annotations

import unittest
from pathlib import Path

from aws_safe_agent_cli.generated_registry import load_generated_registry


class TestApiCoverageLedger(unittest.TestCase):
    def test_coverage_totals_match_the_packaged_inventory(self) -> None:
        root = Path(__file__).resolve().parents[1]
        coverage = (root / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        summary = load_generated_registry().summary
        self.assertIn(summary.botocore_version, coverage)
        self.assertIn(f"Services: {summary.service_count}", coverage)
        self.assertIn(f"Operations: {summary.operation_count}", coverage)
        for status, count in summary.operation_status_counts.items():
            self.assertIn(f"| `{status}` | {count} |", coverage)
