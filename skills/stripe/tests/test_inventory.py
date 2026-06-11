from __future__ import annotations

import unittest

from stripe_api_tool.inventory import canonical_operation_ids, validate_inventories


class TestInventory(unittest.TestCase):
    def test_canonical_operations_non_empty(self) -> None:
        ops = canonical_operation_ids()
        self.assertIsInstance(ops, list)
        self.assertGreater(len(ops), 0)
        self.assertEqual(ops, sorted(ops))

    def test_validate_inventories_ok(self) -> None:
        v = validate_inventories()
        self.assertTrue(v.ok)
        self.assertGreater(v.operation_count, 0)
        self.assertEqual(v.command_count, v.operation_count)
        self.assertFalse(v.mismatch)
        self.assertFalse(v.commands_mismatch)
