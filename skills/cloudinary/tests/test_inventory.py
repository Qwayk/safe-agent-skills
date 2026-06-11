from __future__ import annotations

import unittest

from cloudinary_safe_agent_cli.inventory import load_inventory_json


class TestInventory(unittest.TestCase):
    def test_inventory_counts_match_expected_surface(self) -> None:
        data = load_inventory_json()
        self.assertEqual(data["operation_count"], 175)
        self.assertEqual(
            data["counts_by_area"],
            {
                "admin": 72,
                "analyze": 16,
                "live_streaming": 12,
                "permissions": 21,
                "player_profiles": 4,
                "provisioning": 26,
                "upload": 22,
                "video_config": 2,
            },
        )
