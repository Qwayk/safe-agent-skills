from __future__ import annotations

import unittest
from pathlib import Path

from qwayk_woocommerce_safe_agent_cli.catalog import load_operation_catalog


class TestApiCoverageAlignment(unittest.TestCase):
    def test_doc_rows_match_catalog(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "api_coverage.md").read_text(encoding="utf-8").splitlines()
        doc_rows = set()
        for line in text:
            if not line.startswith("| "):
                continue
            columns = [part.strip() for part in line.strip().strip("|").split("|")]
            if len(columns) < 3 or columns[0] == "Method":
                continue
            method = columns[0]
            path = columns[1].strip("`")
            command = columns[2].strip("`")
            doc_rows.add((method, path, command))

        catalog_rows = {(spec.method, spec.path, spec.key) for spec in load_operation_catalog()}
        self.assertEqual(doc_rows, catalog_rows)
