from __future__ import annotations

import unittest
from pathlib import Path

from qdrant_cloud_api_tool.operations_v1 import INVENTORY_OPERATION_COUNT, OPERATIONS, OPERATIONS_BY_DOMAIN


class TestOfficialInventory(unittest.TestCase):
    def test_inventory_files_exist_and_counts_match(self) -> None:
        root = Path(__file__).resolve().parents[1]
        rpcs = root / "docs" / "official_rpcs_v1.txt"
        routes = root / "docs" / "official_http_routes_v1.txt"
        cmds = root / "docs" / "official_commands_v1.txt"
        self.assertTrue(rpcs.exists())
        self.assertTrue(routes.exists())
        self.assertTrue(cmds.exists())

        rpcs_lines = [ln for ln in rpcs.read_text(encoding="utf-8").splitlines() if ln.strip()]
        routes_lines = [ln for ln in routes.read_text(encoding="utf-8").splitlines() if ln.strip()]
        cmds_lines = [ln for ln in cmds.read_text(encoding="utf-8").splitlines() if ln.strip()]

        self.assertGreater(len(rpcs_lines), 0)
        self.assertEqual(len(rpcs_lines), len(routes_lines))
        self.assertEqual(len(rpcs_lines), len(cmds_lines))

        self.assertEqual(len(rpcs_lines), INVENTORY_OPERATION_COUNT)
        self.assertEqual(len(OPERATIONS), INVENTORY_OPERATION_COUNT)
        self.assertEqual(sum(len(v) for v in OPERATIONS_BY_DOMAIN.values()), INVENTORY_OPERATION_COUNT)

