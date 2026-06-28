from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestAzureInventory(unittest.TestCase):
    def test_inventory_is_pinned_and_generated_from_official_boundary(self) -> None:
        data = json.loads((ROOT / "docs" / "official_inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(data["source"]["repository"], "https://github.com/Azure/azure-rest-api-specs")
        self.assertEqual(data["source"]["pinned_commit"], "ada8601c3b75c15f06f21e50f9368d9476229305")
        self.assertEqual(data["source"]["inventory_strategy"], "generated-inventory possible")
        self.assertGreaterEqual(data["summary"]["services"], 300)
        self.assertGreaterEqual(data["summary"]["selected_operations"], 25000)
        self.assertIn("Microsoft Graph", " ".join(data["boundary"]["excluded"]))

    def test_operations_are_explicit_and_latest_selected(self) -> None:
        data = json.loads((ROOT / "docs" / "official_inventory.json").read_text(encoding="utf-8"))
        services = {service["service_id"]: service for service in data["services"]}
        self.assertIn("compute-management", services)
        compute_ops = services["compute-management"]["operations"]
        self.assertTrue(any(op["operation_name"] for op in compute_ops))
        self.assertTrue(all(op["coverage_status"] == "implemented" for op in compute_ops[:50]))
        self.assertTrue(all(op["version_selection"] in {"latest_stable", "latest_preview_only"} for op in compute_ops[:50]))

    def test_non_azure_microsoft_product_boundaries_are_excluded(self) -> None:
        data = json.loads((ROOT / "docs" / "official_inventory.json").read_text(encoding="utf-8"))
        service_ids = [str(service["service_id"]).lower() for service in data["services"]]
        excluded_fragments = (
            "awsconnector",
            "devops",
            "dynamics",
            "github",
            "m365",
            "microsoft365",
            "office365",
            "powerplatform",
            "xbox",
        )
        for fragment in excluded_fragments:
            self.assertFalse(any(fragment in service_id for service_id in service_ids), fragment)

    def test_sample_widget_specs_are_excluded_from_customer_boundary(self) -> None:
        data = json.loads((ROOT / "docs" / "official_inventory.json").read_text(encoding="utf-8"))
        service_ids = [str(service["service_id"]).lower() for service in data["services"]]
        for fragment in ("contoso", "widgetmanager", "widget-data-plane", "widget-management"):
            self.assertFalse(any(fragment in service_id for service_id in service_ids), fragment)
        excluded_text = " ".join(data["boundary"]["excluded"]).lower()
        self.assertIn("contoso widgetmanager", excluded_text)

    def test_secret_like_reads_are_classified(self) -> None:
        data = json.loads((ROOT / "docs" / "official_inventory.json").read_text(encoding="utf-8"))
        sensitive_reads = [
            op
            for service in data["services"]
            for op in service["operations"]
            if op["classification"] == "sensitive_read" and "sensitive_read" in op.get("risk_categories", [])
        ]
        self.assertGreaterEqual(data["summary"]["sensitive_read_operations"], 100)
        self.assertGreaterEqual(len(sensitive_reads), 100)
        self.assertTrue(any("token" in op["operation_name"] or "secret" in op["operation_name"] or "key" in op["operation_name"] for op in sensitive_reads))


if __name__ == "__main__":
    unittest.main()
