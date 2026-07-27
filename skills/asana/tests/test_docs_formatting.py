from __future__ import annotations

import unittest
from pathlib import Path

from asana_safe_agent_cli.inventory import operations


class TestCoverageAlignment(unittest.TestCase):
    def test_every_operation_has_one_coverage_row(self) -> None:
        root = Path(__file__).resolve().parents[1]
        coverage = (root / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        for operation in operations():
            self.assertEqual(coverage.count(f"`{operation['operation_id']}`"), 1)

    def test_coverage_has_no_unimplemented_rows(self) -> None:
        statuses = {operation["status"] for operation in operations()}
        self.assertEqual(
            statuses,
            {
                "implemented_live_unverified",
                "implemented_access_gated_live_unverified",
                "implemented_developer_preview_live_unverified",
                "implemented_deprecated_live_unverified",
                "intentionally_excluded",
            },
        )


if __name__ == "__main__":
    unittest.main()
