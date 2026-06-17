from __future__ import annotations

import unittest

from fortnox_api_tool.websocket_inventory import (
    load_websocket_inventory,
    official_control_commands,
    topic_names,
)


class TestWebsocketInventory(unittest.TestCase):
    def test_websocket_inventory_totals_match_coverage_lock(self) -> None:
        inventory = load_websocket_inventory()
        self.assertRegex(inventory.audited_utc, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(inventory.stream_url, "wss://ws.fortnox.se/topics-v1")
        self.assertEqual(inventory.control_command_count, 5)
        self.assertEqual(inventory.topic_count, 19)
        self.assertEqual(inventory.event_count, 60)
        self.assertEqual(len(inventory.topics), 19)
        self.assertEqual(sum(topic.event_count for topic in inventory.topics), 60)

    def test_official_control_commands_match_docs(self) -> None:
        self.assertEqual(
            official_control_commands(),
            (
                "add-tenants-v1",
                "remove-tenants-v1",
                "list-tenants-v1",
                "add-topics-v1",
                "subscribe-v1",
            ),
        )

    def test_expected_topics_and_event_details_are_present(self) -> None:
        inventory = load_websocket_inventory()
        self.assertIn("warehouse-stockbalances", topic_names())
        self.assertIn("customers", topic_names())

        warehouse = next(topic for topic in inventory.topics if topic.topic == "warehouse-stockbalances")
        self.assertEqual(warehouse.event_count, 1)
        self.assertEqual(warehouse.events[0].event, "warehouse-stockbalance-changed-v1")

        vouchers = next(topic for topic in inventory.topics if topic.topic == "vouchers")
        self.assertEqual(vouchers.event_count, 3)
        self.assertEqual(vouchers.events[0].additional_payload, "year, series, id")
