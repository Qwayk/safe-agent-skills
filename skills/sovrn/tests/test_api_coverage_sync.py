from __future__ import annotations

import re
import unittest
from pathlib import Path

EXPECTED_COMMANDS = {
    "sovrn-safe-cli commerce campaigns get",
    "sovrn-safe-cli commerce links check",
    "sovrn-safe-cli commerce links bid-check",
    "sovrn-safe-cli commerce reports transactions get",
    "sovrn-safe-cli commerce reports pages get",
    "sovrn-safe-cli commerce reports links get",
    "sovrn-safe-cli commerce reports merchants get",
    "sovrn-safe-cli commerce reports merchants-by-date get",
    "sovrn-safe-cli commerce reports merchandise get",
    "sovrn-safe-cli commerce reports networks get",
    "sovrn-safe-cli commerce reports cuids get",
    "sovrn-safe-cli commerce merchant-groups approved",
    "sovrn-safe-cli commerce merchant-groups delta",
    "sovrn-safe-cli commerce coupons product get",
    "sovrn-safe-cli commerce products recommend",
    "sovrn-safe-cli commerce comparisons prices search",
    "sovrn-safe-cli advertising reports account get",
    "sovrn-safe-cli advertising reports bid get",
    "sovrn-safe-cli advertising reports breakout get",
    "sovrn-safe-cli advertising reports domain-account get",
    "sovrn-safe-cli advertising reports domain-bid get",
    "sovrn-safe-cli advertising reports custom get",
}


class TestApiCoverageSync(unittest.TestCase):
    def test_coverage_ledger_command_set_matches_expected_surface(self) -> None:
        root = Path(__file__).resolve().parents[1]
        coverage_path = root / "docs" / "api_coverage.md"
        text = coverage_path.read_text(encoding="utf-8")

        commands: set[str] = set()
        states: list[str] = []

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            parts = [part.strip() for part in stripped.strip("|").split("|")]
            if len(parts) != 8:
                continue
            command = re.sub(r"`", "", parts[5]).strip()
            state = re.sub(r"`", "", parts[6]).strip()
            if command.startswith("sovrn-safe-cli "):
                commands.add(command)
                states.append(state)

        self.assertEqual(commands, EXPECTED_COMMANDS)
        self.assertEqual(len(commands), 22)
        for state in states:
            self.assertIn(state, {"implemented", "implemented-access-gated"})
