from __future__ import annotations

import unittest
from pathlib import Path

from fortnox_api_tool.rest_inventory import load_rest_inventory


class TestDocsConsistency(unittest.TestCase):
    def _root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def _read(self, relative: str) -> str:
        return (self._root() / relative).read_text(encoding="utf-8")

    def test_public_coverage_keeps_current_rest_count(self) -> None:
        coverage = self._read("docs/api_coverage.md")
        inventory = load_rest_inventory()

        self.assertEqual(inventory.operation_count, 377)
        self.assertIn("Official REST operations accounted for: `377`", coverage)
        self.assertIn("Shipped explicit REST commands today: `377`", coverage)

    def test_action_like_get_docs_match_shipped_coverage(self) -> None:
        command_reference = self._read("docs/command_reference.md")
        coverage = self._read("docs/api_coverage.md")

        stale = "Action-like GET endpoints such as email, e-print, preview, print, and reminder flows stay unshipped"
        self.assertNotIn(stale, command_reference)
        self.assertNotIn(stale, coverage)

        self.assertIn("Delivery-triggering invoice, offer, and order GET flows are shipped", command_reference)
        for command in (
            "invoices preview",
            "invoices print",
            "invoices send-an-invoice-as-email",
            "offers send-given-offer-as-email",
            "orders send-given-order-as-email",
        ):
            with self.subTest(command=command):
                self.assertIn(command, command_reference)
                self.assertIn("shipped", coverage.lower())
