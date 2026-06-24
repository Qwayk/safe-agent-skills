from __future__ import annotations

import json
import unittest
from pathlib import Path


class TestInventoryGeneration(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.inventory_path = self.root / "docs" / "_generated" / "aws_botocore_inventory.json"
        self.coverage_path = self.root / "docs" / "api_coverage.md"

    def test_inventory_json_exists_and_has_known_counts(self) -> None:
        self.assertTrue(self.inventory_path.exists(), "Missing docs/_generated/aws_botocore_inventory.json")
        payload = json.loads(self.inventory_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["date"], "2026-06-24")
        self.assertEqual(payload["botocore_version"], "1.43.36")
        self.assertEqual(payload["service_count"], 428)
        self.assertEqual(payload["operation_count"], 18727)
        self.assertEqual(payload["paginator_service_count"], 343)
        self.assertEqual(payload["paginator_count"], 3186)
        self.assertEqual(payload["waiter_service_count"], 68)
        self.assertEqual(payload["waiter_count"], 367)
        self.assertEqual(payload["endpoints_model_version"], 3)
        self.assertEqual(payload["partitions_count"], 8)
        self.assertEqual(payload["botocore_data_dir"], "botocore/data from the pinned botocore wheel")
        self.assertEqual(len(payload["services_with_multiple_versions"]), 10)
        self.assertEqual(len(payload["services"]), 428)
        self.assertEqual(payload["summary"]["operation_status_counts"]["generated_named_command"], 18727)
        self.assertIn("security_identity", payload["summary"]["risk_category_counts"])
        self.assertIn("no_snapshot", payload["summary"]["risk_category_counts"])

        self.assertNotIn("/home/", payload["botocore_data_dir"])
        self.assertNotIn("/Users/", payload["botocore_data_dir"])
        self.assertNotIn(".venv", payload["botocore_data_dir"])
        self.assertNotIn("api-tools-for-" + "ai-agents", payload["botocore_data_dir"])

    def test_coverage_markdown_includes_known_counts_and_stays_specific(self) -> None:
        text = self.coverage_path.read_text(encoding="utf-8")

        expected_snippets = [
            "Services: 428",
            "Operations: 18727",
            "Paginator services: 343",
            "Paginators: 3186",
            "Waiter services: 68",
            "Waiters: 367",
            "Endpoints model version: 3",
            "Partitions: 8",
            "Date: 2026-06-24",
            "Generated named commands: 18727",
            "## Safety and risk coverage",
            "## Generated per-operation evidence",
        ]
        for snippet in expected_snippets:
            self.assertIn(snippet, text)

        banned = [
            "raw bridge",
            "call-anything",
            "generic bridge",
        ]
        for snippet in banned:
            self.assertNotIn(snippet, text.lower())
