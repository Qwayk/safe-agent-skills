from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestDocsProofAlignment(unittest.TestCase):
    def test_api_coverage_and_proof_counts_match(self) -> None:
        root = Path(__file__).resolve().parents[1]
        coverage = (root / "docs/api_coverage.md").read_text(encoding="utf-8")
        proof = (root / "docs/proof.md").read_text(encoding="utf-8")

        match = re.search(r"Total explicit commands: (\d+)", coverage)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "62")

        self.assertIn("62", proof)
        self.assertIn("Partner API 2024.11.0", proof)
        self.assertIn("docs/specs/zapier_partner_api.yaml", proof)
