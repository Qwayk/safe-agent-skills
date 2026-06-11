from __future__ import annotations

import unittest
from pathlib import Path


class TestApiCoverageDoc(unittest.TestCase):
    def test_api_coverage_doc_mentions_all_official_methods(self) -> None:
        root = Path(__file__).resolve().parents[1]
        methods_txt = root / "docs" / "official_methods.txt"
        api_coverage_md = root / "docs" / "api_coverage.md"

        self.assertTrue(methods_txt.exists(), "Missing docs/official_methods.txt")
        self.assertTrue(api_coverage_md.exists(), "Missing docs/api_coverage.md")

        official = [line.strip() for line in methods_txt.read_text(encoding="utf-8").splitlines() if line.strip()]
        text = api_coverage_md.read_text(encoding="utf-8")

        start = text.find("## Method-by-method mapping (pinned discovery snapshot)")
        self.assertNotEqual(start, -1, "docs/api_coverage.md missing method-by-method mapping section")
        end = text.find("\n## ", start + 1)
        self.assertNotEqual(end, -1, "docs/api_coverage.md missing a section after method-by-method mapping")

        mapping = text[start:end]
        missing = [m for m in official if f"`{m}`" not in mapping]
        self.assertEqual(missing, [], f"docs/api_coverage.md missing methods: {missing}")

