from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from google_ads_api_tool.commands.helpers import _load_items
from google_ads_api_tool.errors import ValidationError


class TestHelperCsvInput(unittest.TestCase):
    def test_load_items_reads_csv_rows(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "items.csv"
            path.write_text("resource_name,text\ncustomers/123/campaigns/1,repair\n", encoding="utf-8")
            rows = _load_items(str(path))
        self.assertEqual(
            rows,
            [{"resource_name": "customers/123/campaigns/1", "text": "repair"}],
        )

    def test_load_items_rejects_csv_without_header(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "items.csv"
            path.write_text("", encoding="utf-8")
            with self.assertRaises(ValidationError):
                _load_items(str(path))


if __name__ == "__main__":
    unittest.main()
