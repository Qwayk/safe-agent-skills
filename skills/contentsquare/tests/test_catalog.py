from __future__ import annotations

import unittest

from contentsquare_safe_agent_cli.catalog import ALL_ENDPOINTS, DATA_EXPORT, ENRICHMENT, METRICS, SPEED_ANALYSIS


class CatalogTests(unittest.TestCase):
    def test_expected_official_counts(self) -> None:
        self.assertEqual(len(DATA_EXPORT), 9)
        self.assertEqual(len(METRICS), 59)
        self.assertEqual(len(ENRICHMENT), 1)
        self.assertEqual(len(SPEED_ANALYSIS), 13)
        self.assertEqual(len(ALL_ENDPOINTS), 82)

    def test_no_raw_bridge_command(self) -> None:
        forbidden = {"raw", "request", "call", "anything", "bridge"}
        for spec in ALL_ENDPOINTS:
            self.assertFalse(forbidden.intersection(spec.command), spec)

    def test_command_paths_are_unique(self) -> None:
        commands = [spec.command for spec in ALL_ENDPOINTS]
        self.assertEqual(len(commands), len(set(commands)))


if __name__ == "__main__":
    unittest.main()
