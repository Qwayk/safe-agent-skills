from __future__ import annotations

import unittest
from pathlib import Path

from youtube_api_tool.youtube_discovery import extract_official_method_names, load_official_discovery_doc


class TestDiscoverySnapshot(unittest.TestCase):
    def test_official_methods_txt_matches_snapshot(self) -> None:
        root = Path(__file__).resolve().parents[1]
        methods_txt = root / "docs" / "official_methods.txt"
        self.assertTrue(methods_txt.exists(), "Missing docs/official_methods.txt")
        expected = [line.strip() for line in methods_txt.read_text(encoding="utf-8").splitlines() if line.strip()]

        discovery = load_official_discovery_doc()
        actual = extract_official_method_names(discovery_obj=discovery)

        self.assertEqual(expected, actual)

