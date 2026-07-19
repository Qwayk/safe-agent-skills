from __future__ import annotations

import unittest

from xero_safe_agent_cli.registry import load_registry


class TestFixedCatalogBoundary(unittest.TestCase):
    def test_catalog_has_no_generic_request_command(self) -> None:
        commands = set(load_registry().commands)
        self.assertNotIn("raw-request", commands)
        self.assertNotIn("request", commands)
        self.assertNotIn("call", commands)
        self.assertTrue(all("." in command for command in commands))

    def test_catalog_describes_exact_input_contract(self) -> None:
        description = load_registry().describe("accounting.get-invoices")
        self.assertEqual(description["method"], "GET")
        self.assertIn("query", description["input"])
        self.assertIsNone(description["input"]["body"])


if __name__ == "__main__":
    unittest.main()
