from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from freepik_api_tool.inventory import INVENTORY_FIELDS, append_inventory_row, read_inventory_index


class TestInventory(unittest.TestCase):
    def test_append_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            inv = Path(d) / "inventory.csv"
            append_inventory_row(
                inv,
                {
                    "resource_id": "123",
                    "format": "jpg",
                    "license_url": "https://example.com/license.pdf",
                    "download_url": "https://example.com/file.jpg",
                },
            )
            with inv.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            for field in ("resource_id", "format", "license_url", "download_url"):
                self.assertIn(field, rows[0])
            self.assertEqual(rows[0]["resource_id"], "123")
            self.assertEqual(rows[0]["format"], "jpg")
            self.assertEqual(read_inventory_index(inv)[("123", "jpg")]["license_url"], "https://example.com/license.pdf")
            self.assertEqual(set(rows[0].keys()), set(INVENTORY_FIELDS))
