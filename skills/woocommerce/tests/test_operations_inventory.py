from __future__ import annotations

import unittest

from qwayk_woocommerce_safe_agent_cli.catalog import load_operation_catalog


class TestOperationsInventory(unittest.TestCase):
    def test_inventory_has_expected_shape(self) -> None:
        catalog = load_operation_catalog()
        self.assertEqual(len(catalog), 139)
        keys = {spec.key for spec in catalog}
        self.assertEqual(len(keys), len(catalog))
        for required in [
            "index get",
            "coupons create",
            "orders batch",
            "webhooks update",
            "system-status-tools run",
            "data current-currency",
        ]:
            self.assertIn(required, keys)
