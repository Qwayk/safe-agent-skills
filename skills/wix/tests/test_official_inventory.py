from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path

from wix_safe_agent_cli.cli import build_parser


class TestOfficialInventory(unittest.TestCase):
    @staticmethod
    def _root() -> Path:
        return Path(__file__).resolve().parents[1]

    def _load_inventory(self) -> dict:
        path = self._root() / "docs" / "official_inventory.json"
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _collect_parser_command_paths() -> set[str]:
        parser = build_parser()
        paths: set[str] = set()

        def walk(p: argparse.ArgumentParser, prefix: str) -> None:
            for action in p._actions:
                if not isinstance(action, argparse._SubParsersAction):
                    continue
                for name, choice in action.choices.items():
                    command_path = f"{prefix} {name}".strip()
                    has_children = any(
                        isinstance(child_action, argparse._SubParsersAction) for child_action in choice._actions
                    )
                    if has_children:
                        walk(choice, command_path)
                    else:
                        paths.add(f"wix-safe-agent-cli {command_path}")

        walk(parser, "")
        return paths

    def test_inventory_file_exists_with_complete_status(self) -> None:
        inventory = self._load_inventory()

        self.assertEqual(inventory["tool_name"], "wix-safe-agent-cli")
        self.assertEqual(inventory["completion_status"], "complete")
        self.assertIn("families", inventory)
        self.assertTrue(inventory["families"])

        notes = "\n".join(inventory.get("notes", []))
        self.assertIn("coverage accounting is complete", notes.lower())
        self.assertIn("zero real callable not-yet-implemented rows", notes.lower())

    def test_oauth_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("oauth-2", families)
        family = families["oauth-2"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 4)

        expected_commands = {
            "wix-safe-agent-cli auth token create",
            "wix-safe-agent-cli auth token request",
            "wix-safe-agent-cli auth token refresh",
            "wix-safe-agent-cli auth token inspect",
        }
        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(expected_commands.issubset(inventory_commands))

        for op in operations:
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertIn("implemented", op["flags"])
            self.assertIsNotNone(op.get("http_method"))
            self.assertIsNotNone(op.get("path"))

    def test_bi_event_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bi-event", families)
        family = families["bi-event"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)

        op = operations[0]
        self.assertEqual(op.get("method_id"), "biEvent.send")
        self.assertEqual(op.get("http_method"), "POST")
        self.assertEqual(op.get("path"), "/apps/v1/bi-event")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli bi-event send")
        self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
        self.assertIn("implemented", op["flags"])

    def test_site_plugins_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("site-plugins", families)
        family = families["site-plugins"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)

        op = operations[0]
        self.assertEqual(op.get("method_id"), "sitePlugins.getPlacementStatus")
        self.assertEqual(op.get("http_method"), "GET")
        self.assertEqual(op.get("path"), "/app-plugins/v1/site-plugins/placement-status")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli site-plugins get-placement-status")
        self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
        self.assertIn("implemented", op["flags"])

    def test_market_listing_family_is_present_and_developer_preview(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("market-listing", families)
        family = families["market-listing"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)
        self.assertIn("developer-preview", family.get("default_flags", []))

        op = operations[0]
        self.assertEqual(op.get("method_id"), "marketListing.search")
        self.assertEqual(op.get("http_method"), "POST")
        self.assertEqual(op.get("path"), "/devcenter/app-market-listing/v1/market-listings/search")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli market-listing search")
        self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
        self.assertIn("implemented", op["flags"])

    def test_embedded_scripts_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("embedded-scripts", families)
        family = families["embedded-scripts"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 2)

        by_id = {op.get("method_id"): op for op in operations}

        self.assertEqual(by_id["embeddedScripts.get"].get("http_method"), "GET")
        self.assertEqual(by_id["embeddedScripts.get"].get("path"), "/apps/v1/scripts")
        self.assertEqual(by_id["embeddedScripts.get"].get("planned_command"), "wix-safe-agent-cli embedded-scripts get")
        self.assertIn("implemented", by_id["embeddedScripts.get"]["flags"])

        self.assertEqual(by_id["embeddedScripts.embed"].get("http_method"), "POST")
        self.assertEqual(by_id["embeddedScripts.embed"].get("path"), "/apps/v1/scripts")
        self.assertEqual(
            by_id["embeddedScripts.embed"].get("planned_command"),
            "wix-safe-agent-cli embedded-scripts embed",
        )
        self.assertIn("implemented", by_id["embeddedScripts.embed"]["flags"])

        for op in operations:
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_analytics_semantic_models_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("analytics-semantic-models", families)
        family = families["analytics-semantic-models"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 3)

        by_id = {op.get("method_id"): op for op in operations}

        self.assertEqual(by_id["analyticsSemanticModels.list"].get("http_method"), "GET")
        self.assertEqual(
            by_id["analyticsSemanticModels.list"].get("path"),
            "/analytics/semantic-model/v3/semantic-models",
        )
        self.assertEqual(
            by_id["analyticsSemanticModels.list"].get("planned_command"),
            "wix-safe-agent-cli analytics-semantic-models list",
        )
        self.assertIn("implemented", by_id["analyticsSemanticModels.list"]["flags"])

        self.assertEqual(by_id["analyticsSemanticModels.get"].get("http_method"), "GET")
        self.assertEqual(
            by_id["analyticsSemanticModels.get"].get("path"),
            "/analytics/semantic-model/v3/semantic-models/{semanticModelId}",
        )
        self.assertEqual(
            by_id["analyticsSemanticModels.get"].get("planned_command"),
            "wix-safe-agent-cli analytics-semantic-models get",
        )
        self.assertIn("implemented", by_id["analyticsSemanticModels.get"]["flags"])

        self.assertEqual(by_id["analyticsSemanticModels.query"].get("http_method"), "POST")
        self.assertEqual(
            by_id["analyticsSemanticModels.query"].get("path"),
            "/analytics/semantic-model/v3/semantic-models/query-data",
        )
        self.assertEqual(
            by_id["analyticsSemanticModels.query"].get("planned_command"),
            "wix-safe-agent-cli analytics-semantic-models query",
        )
        self.assertIn("implemented", by_id["analyticsSemanticModels.query"]["flags"])

        for op in operations:
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_analytics_sessions_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("analytics-sessions", families)
        family = families["analytics-sessions"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 4)

        by_id = {op.get("method_id"): op for op in operations}

        self.assertEqual(by_id["analyticsSessions.getListSessionsJobResult"].get("http_method"), "GET")
        self.assertEqual(
            by_id["analyticsSessions.getListSessionsJobResult"].get("path"),
            "/analytics/v1/sessions/list/result",
        )
        self.assertEqual(
            by_id["analyticsSessions.getListSessionsJobResult"].get("planned_command"),
            "wix-safe-agent-cli analytics-sessions get-list-job-result",
        )
        self.assertIn("implemented", by_id["analyticsSessions.getListSessionsJobResult"]["flags"])

        self.assertEqual(by_id["analyticsSessions.listSessionsAsync"].get("http_method"), "POST")
        self.assertEqual(by_id["analyticsSessions.listSessionsAsync"].get("path"), "/analytics/v1/sessions/list/async")
        self.assertIn("reviewed-plan", by_id["analyticsSessions.listSessionsAsync"]["flags"])

        self.assertEqual(
            by_id["analyticsSessions.markRecordingsAsDeleted"].get("path"),
            "/analytics/v1/sessions/recordings-deleted",
        )
        self.assertIn("requires-ack-irreversible", by_id["analyticsSessions.markRecordingsAsDeleted"]["flags"])

        self.assertEqual(
            by_id["analyticsSessions.markSessionAsRecorded"].get("path"),
            "/analytics/v1/sessions/session-recorded",
        )
        self.assertIn("requires-ack-irreversible", by_id["analyticsSessions.markSessionAsRecorded"]["flags"])

        for op in operations:
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_automations_storage_items_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("automation-storage-items", families)
        family = families["automation-storage-items"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 11)
        self.assertIn("implemented", family.get("coverage_status", "implemented"))

        by_id = {op.get("method_id"): op for op in operations}

        expected = {
            "automationStorageItems.create": (
                "POST",
                "/storage-service/v1/storage-items",
                "wix-safe-agent-cli automation-storage-items create",
            ),
            "automationStorageItems.get": (
                "GET",
                "/storage-service/v1/storage-items/{key}",
                "wix-safe-agent-cli automation-storage-items get",
            ),
            "automationStorageItems.query": (
                "POST",
                "/storage-service/v1/storage-items/query",
                "wix-safe-agent-cli automation-storage-items query",
            ),
            "automationStorageItems.bulkUpdateTags": (
                "POST",
                "/storage-service/v1/bulk/storage-items/update-tags",
                "wix-safe-agent-cli automation-storage-items bulk-update-tags",
            ),
            "automationStorageItems.bulkUpdateTagsByFilter": (
                "POST",
                "/storage-service/v1/bulk/storage-items/update-tags-by-filter",
                "wix-safe-agent-cli automation-storage-items bulk-update-tags-by-filter",
            ),
            "automationStorageItems.updateCounterBy": (
                "PATCH",
                "/storage-service/v1/storage-items/{key}/update-counter-by",
                "wix-safe-agent-cli automation-storage-items update-counter-by",
            ),
            "automationStorageItems.updateValue": (
                "PATCH",
                "/storage-service/v1/storage-items/{key}/update-value",
                "wix-safe-agent-cli automation-storage-items update-value",
            ),
        }

        for method_id, (http_method, path, command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), command)
            self.assertIn("implemented", by_id[method_id]["flags"])

        self.assertIn("requires-ack-irreversible", by_id["automationStorageItems.bulkUpdateTagsByFilter"]["flags"])
        for method_id in [
            "automationStorageItems.onCreated",
            "automationStorageItems.onCounterUpdated",
            "automationStorageItems.onValueUpdated",
            "automationStorageItems.onTagsModified",
        ]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_automations_v2_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("automations-v2", families)
        family = families["automations-v2"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)
        self.assertIn("implemented", family.get("coverage_status", "implemented"))

        by_id = {op.get("method_id"): op for op in operations}

        expected = {
            "automationsV2.create": ("POST", "/automations-service/v2/automations", "wix-safe-agent-cli automations-v2 create"),
            "automationsV2.get": ("GET", "/automations-service/v2/automations/{automationId}", "wix-safe-agent-cli automations-v2 get"),
            "automationsV2.update": ("PATCH", "/automations-service/v2/automations/{automation.id}", "wix-safe-agent-cli automations-v2 update"),
            "automationsV2.delete": ("DELETE", "/automations-service/v2/automations/{automationId}", "wix-safe-agent-cli automations-v2 delete"),
            "automationsV2.query": ("POST", "/automations-service/v2/automations/query", "wix-safe-agent-cli automations-v2 query"),
            "automationsV2.validate": ("POST", "/automations-service/v2/automations/validate", "wix-safe-agent-cli automations-v2 validate"),
        }

        for method_id, (http_method, path, command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), command)
            self.assertIn("implemented", by_id[method_id]["flags"])

        for method_id in ["automationsV2.create", "automationsV2.update", "automationsV2.delete"]:
            self.assertIn("requires-ack-irreversible", by_id[method_id]["flags"])
        for method_id in ["automationsV2.onCreated", "automationsV2.onDeleted", "automationsV2.onUpdated"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_async_jobs_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("async-jobs", families)
        family = families["async-jobs"]
        operations = family.get("operations", [])

        by_id = {op.get("method_id"): op for op in operations}
        callable_operations = [op for op in operations if op.get("cli_callable")]
        self.assertEqual(len(callable_operations), 2)

        self.assertEqual(by_id["asyncJobs.get"].get("http_method"), "GET")
        self.assertEqual(by_id["asyncJobs.get"].get("path"), "/async-jobs/v1/async-jobs/{jobId}")
        self.assertEqual(by_id["asyncJobs.get"].get("planned_command"), "wix-safe-agent-cli async-jobs get")
        self.assertIn("implemented", by_id["asyncJobs.get"]["flags"])

        self.assertEqual(by_id["asyncJobs.listItems"].get("http_method"), "GET")
        self.assertEqual(by_id["asyncJobs.listItems"].get("path"), "/async-jobs/v1/async-jobs/{jobId}/items")
        self.assertEqual(
            by_id["asyncJobs.listItems"].get("planned_command"),
            "wix-safe-agent-cli async-jobs list-items",
        )
        self.assertIn("implemented", by_id["asyncJobs.listItems"]["flags"])

        for op in operations:
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_stores_products_v3_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("stores-products-v3", families)
        family = families["stores-products-v3"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 26)

        by_id = {op.get("method_id"): op for op in operations}

        self.assertEqual(by_id["storesProductsV3.get"].get("http_method"), "GET")
        self.assertEqual(by_id["storesProductsV3.get"].get("path"), "/stores/v3/products/{productId}")
        self.assertEqual(
            by_id["storesProductsV3.get"].get("planned_command"),
            "wix-safe-agent-cli stores-products-v3 get",
        )

        self.assertEqual(by_id["storesProductsV3.getBySlug"].get("http_method"), "GET")
        self.assertEqual(by_id["storesProductsV3.getBySlug"].get("path"), "/stores/v3/products/slug/{slug}")
        self.assertEqual(
            by_id["storesProductsV3.getBySlug"].get("planned_command"),
            "wix-safe-agent-cli stores-products-v3 get-by-slug",
        )

        self.assertEqual(by_id["storesProductsV3.getAllProductsCategory"].get("http_method"), "GET")
        self.assertEqual(
            by_id["storesProductsV3.getAllProductsCategory"].get("path"),
            "/stores/v3/all-products-category",
        )
        self.assertEqual(
            by_id["storesProductsV3.getAllProductsCategory"].get("planned_command"),
            "wix-safe-agent-cli stores-products-v3 get-all-products-category",
        )

        self.assertEqual(by_id["storesProductsV3.query"].get("http_method"), "POST")
        self.assertEqual(by_id["storesProductsV3.query"].get("path"), "/stores/v3/products/query")
        self.assertEqual(
            by_id["storesProductsV3.query"].get("planned_command"),
            "wix-safe-agent-cli stores-products-v3 query",
        )

        self.assertEqual(by_id["storesProductsV3.search"].get("http_method"), "POST")
        self.assertEqual(by_id["storesProductsV3.search"].get("path"), "/stores/v3/products/search")
        self.assertEqual(
            by_id["storesProductsV3.search"].get("planned_command"),
            "wix-safe-agent-cli stores-products-v3 search",
        )

        self.assertEqual(by_id["storesProductsV3.count"].get("http_method"), "POST")
        self.assertEqual(by_id["storesProductsV3.count"].get("path"), "/stores/v3/products/count")
        self.assertEqual(
            by_id["storesProductsV3.count"].get("planned_command"),
            "wix-safe-agent-cli stores-products-v3 count",
        )

        self.assertEqual(by_id["storesProductsV3.create"].get("http_method"), "POST")
        self.assertEqual(by_id["storesProductsV3.create"].get("path"), "/stores/v3/products")
        self.assertEqual(
            by_id["storesProductsV3.create"].get("planned_command"),
            "wix-safe-agent-cli stores-products-v3 create",
        )

        self.assertEqual(by_id["storesProductsV3.update"].get("http_method"), "PATCH")
        self.assertEqual(by_id["storesProductsV3.update"].get("path"), "/stores/v3/products/{productId}")
        self.assertEqual(
            by_id["storesProductsV3.update"].get("planned_command"),
            "wix-safe-agent-cli stores-products-v3 update",
        )

        expected_new = {
            "storesProductsV3.delete": ("DELETE", "/stores/v3/products/{productId}", "wix-safe-agent-cli stores-products-v3 delete"),
            "storesProductsV3.bulkCreate": ("POST", "/stores/v3/bulk/products/create", "wix-safe-agent-cli stores-products-v3 bulk-create"),
            "storesProductsV3.bulkDelete": ("POST", "/stores/v3/bulk/products/delete", "wix-safe-agent-cli stores-products-v3 bulk-delete"),
            "storesProductsV3.bulkUpdate": ("POST", "/stores/v3/bulk/products/update", "wix-safe-agent-cli stores-products-v3 bulk-update"),
            "storesProductsV3.createWithInventory": (
                "POST",
                "/stores/v3/products-with-inventory",
                "wix-safe-agent-cli stores-products-v3 create-with-inventory",
            ),
            "storesProductsV3.updateWithInventory": (
                "PATCH",
                "/stores/v3/products-with-inventory/{productId}",
                "wix-safe-agent-cli stores-products-v3 update-with-inventory",
            ),
            "storesProductsV3.bulkCreateWithInventory": (
                "POST",
                "/stores/v3/bulk/products-with-inventory/create",
                "wix-safe-agent-cli stores-products-v3 bulk-create-with-inventory",
            ),
            "storesProductsV3.bulkUpdateWithInventory": (
                "POST",
                "/stores/v3/bulk/products-with-inventory/update",
                "wix-safe-agent-cli stores-products-v3 bulk-update-with-inventory",
            ),
            "storesProductsV3.bulkAddInfoSections": (
                "POST",
                "/stores/v3/bulk/products/add-info-sections",
                "wix-safe-agent-cli stores-products-v3 bulk-add-info-sections",
            ),
            "storesProductsV3.bulkAddInfoSectionsByFilter": (
                "POST",
                "/stores/v3/bulk/products/add-info-sections-by-filter",
                "wix-safe-agent-cli stores-products-v3 bulk-add-info-sections-by-filter",
            ),
            "storesProductsV3.bulkAddProductsToCategoriesByFilter": (
                "POST",
                "/stores/v3/bulk/products/add-to-categories-by-filter",
                "wix-safe-agent-cli stores-products-v3 bulk-add-to-categories-by-filter",
            ),
            "storesProductsV3.bulkAdjustProductVariantsByFilter": (
                "POST",
                "/stores/v3/bulk/products/adjust-variants-by-filter",
                "wix-safe-agent-cli stores-products-v3 bulk-adjust-variants-by-filter",
            ),
            "storesProductsV3.bulkDeleteByFilter": (
                "POST",
                "/stores/v3/bulk/products/delete-by-filter",
                "wix-safe-agent-cli stores-products-v3 bulk-delete-by-filter",
            ),
            "storesProductsV3.bulkRemoveInfoSections": (
                "POST",
                "/stores/v3/bulk/products/remove-info-sections",
                "wix-safe-agent-cli stores-products-v3 bulk-remove-info-sections",
            ),
            "storesProductsV3.bulkRemoveInfoSectionsByFilter": (
                "POST",
                "/stores/v3/bulk/products/remove-info-sections-by-filter",
                "wix-safe-agent-cli stores-products-v3 bulk-remove-info-sections-by-filter",
            ),
            "storesProductsV3.bulkRemoveProductsFromCategoriesByFilter": (
                "POST",
                "/stores/v3/bulk/products/remove-from-categories-by-filter",
                "wix-safe-agent-cli stores-products-v3 bulk-remove-from-categories-by-filter",
            ),
            "storesProductsV3.bulkUpdateProductVariantsByFilter": (
                "POST",
                "/stores/v3/bulk/products/update-variants-by-filter",
                "wix-safe-agent-cli stores-products-v3 bulk-update-variants-by-filter",
            ),
            "storesProductsV3.bulkUpdateByFilter": (
                "POST",
                "/stores/v3/bulk/products/update-by-filter",
                "wix-safe-agent-cli stores-products-v3 bulk-update-by-filter",
            ),
        }
        for method_id, (http_method, path, command) in expected_new.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_read_only_variants_v3_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("read-only-variants-v3", families)
        family = families["read-only-variants-v3"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 2)

        by_id = {op.get("method_id"): op for op in operations}

        self.assertEqual(by_id["readOnlyVariantsV3.query"].get("http_method"), "POST")
        self.assertEqual(by_id["readOnlyVariantsV3.query"].get("path"), "/stores/v3/products/query-variants")
        self.assertEqual(
            by_id["readOnlyVariantsV3.query"].get("planned_command"),
            "wix-safe-agent-cli read-only-variants-v3 query",
        )

        self.assertEqual(by_id["readOnlyVariantsV3.search"].get("http_method"), "POST")
        self.assertEqual(by_id["readOnlyVariantsV3.search"].get("path"), "/stores/v3/products/search-variants")
        self.assertEqual(
            by_id["readOnlyVariantsV3.search"].get("planned_command"),
            "wix-safe-agent-cli read-only-variants-v3 search",
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_brands_v3_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("brands-v3", families)
        family = families["brands-v3"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 10)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "brandsV3.get": ("GET", "/stores/v3/brands/{brandId}", "wix-safe-agent-cli brands-v3 get"),
            "brandsV3.query": ("POST", "/stores/v3/brands/query", "wix-safe-agent-cli brands-v3 query"),
            "brandsV3.create": ("POST", "/stores/v3/brands", "wix-safe-agent-cli brands-v3 create"),
            "brandsV3.update": ("PATCH", "/stores/v3/brands/{brand.id}", "wix-safe-agent-cli brands-v3 update"),
            "brandsV3.delete": ("DELETE", "/stores/v3/brands/{brandId}", "wix-safe-agent-cli brands-v3 delete"),
            "brandsV3.bulkCreate": ("POST", "/stores/v3/bulk/brands/create", "wix-safe-agent-cli brands-v3 bulk-create"),
            "brandsV3.bulkDelete": ("POST", "/stores/v3/bulk/brands/delete", "wix-safe-agent-cli brands-v3 bulk-delete"),
            "brandsV3.bulkUpdate": ("POST", "/stores/v3/bulk/brands/update", "wix-safe-agent-cli brands-v3 bulk-update"),
            "brandsV3.getOrCreate": ("POST", "/stores/v3/brands/get-or-create", "wix-safe-agent-cli brands-v3 get-or-create"),
            "brandsV3.bulkGetOrCreate": ("POST", "/stores/v3/bulk/brands/get-or-create", "wix-safe-agent-cli brands-v3 bulk-get-or-create"),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_ribbons_v3_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("ribbons-v3", families)
        family = families["ribbons-v3"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 10)

        by_id = {op.get("method_id"): op for op in operations}

        expected = {
            "ribbonsV3.get": ("GET", "/stores/v3/ribbons/{ribbonId}", "wix-safe-agent-cli ribbons-v3 get"),
            "ribbonsV3.query": ("POST", "/stores/v3/ribbons/query", "wix-safe-agent-cli ribbons-v3 query"),
            "ribbonsV3.create": ("POST", "/stores/v3/ribbons", "wix-safe-agent-cli ribbons-v3 create"),
            "ribbonsV3.update": ("PATCH", "/stores/v3/ribbons/{ribbon.id}", "wix-safe-agent-cli ribbons-v3 update"),
            "ribbonsV3.delete": ("DELETE", "/stores/v3/ribbons/{ribbonId}", "wix-safe-agent-cli ribbons-v3 delete"),
            "ribbonsV3.bulkCreate": ("POST", "/stores/v3/bulk/ribbons/create", "wix-safe-agent-cli ribbons-v3 bulk-create"),
            "ribbonsV3.bulkDelete": ("POST", "/stores/v3/bulk/ribbons/delete", "wix-safe-agent-cli ribbons-v3 bulk-delete"),
            "ribbonsV3.bulkUpdate": ("POST", "/stores/v3/bulk/ribbons/update", "wix-safe-agent-cli ribbons-v3 bulk-update"),
            "ribbonsV3.getOrCreate": ("POST", "/stores/v3/ribbons/get-or-create", "wix-safe-agent-cli ribbons-v3 get-or-create"),
            "ribbonsV3.bulkGetOrCreate": ("POST", "/stores/v3/bulk/ribbons/get-or-create", "wix-safe-agent-cli ribbons-v3 bulk-get-or-create"),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_stores_info_sections_v3_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("stores-info-sections-v3", families)
        family = families["stores-info-sections-v3"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 10)

        by_id = {op.get("method_id"): op for op in operations}

        expected = {
            "storesInfoSectionsV3.get": ("GET", "/stores/v3/info-sections/{infoSectionId}", "wix-safe-agent-cli stores-info-sections-v3 get"),
            "storesInfoSectionsV3.query": ("POST", "/stores/v3/info-sections/query", "wix-safe-agent-cli stores-info-sections-v3 query"),
            "storesInfoSectionsV3.create": ("POST", "/stores/v3/info-sections", "wix-safe-agent-cli stores-info-sections-v3 create"),
            "storesInfoSectionsV3.update": ("PATCH", "/stores/v3/info-sections/{infoSectionId}", "wix-safe-agent-cli stores-info-sections-v3 update"),
            "storesInfoSectionsV3.delete": ("DELETE", "/stores/v3/info-sections/{infoSectionId}", "wix-safe-agent-cli stores-info-sections-v3 delete"),
            "storesInfoSectionsV3.bulkCreate": ("POST", "/stores/v3/bulk/info-sections/create", "wix-safe-agent-cli stores-info-sections-v3 bulk-create"),
            "storesInfoSectionsV3.bulkDelete": ("POST", "/stores/v3/bulk/info-sections/delete", "wix-safe-agent-cli stores-info-sections-v3 bulk-delete"),
            "storesInfoSectionsV3.bulkUpdate": ("POST", "/stores/v3/bulk/info-sections/update", "wix-safe-agent-cli stores-info-sections-v3 bulk-update"),
            "storesInfoSectionsV3.getOrCreate": ("POST", "/stores/v3/info-sections/get-or-create", "wix-safe-agent-cli stores-info-sections-v3 get-or-create"),
            "storesInfoSectionsV3.bulkGetOrCreate": ("POST", "/stores/v3/bulk/info-sections/get-or-create", "wix-safe-agent-cli stores-info-sections-v3 bulk-get-or-create"),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_customizations_v3_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("customizations-v3", families)
        family = families["customizations-v3"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 11)

        by_id = {op.get("method_id"): op for op in operations}

        expected = {
            "customizationsV3.get": ("GET", "/stores/v3/customizations/{customizationId}", "wix-safe-agent-cli customizations-v3 get"),
            "customizationsV3.query": ("POST", "/stores/v3/customizations/query", "wix-safe-agent-cli customizations-v3 query"),
            "customizationsV3.create": ("POST", "/stores/v3/customizations", "wix-safe-agent-cli customizations-v3 create"),
            "customizationsV3.update": ("PATCH", "/stores/v3/customizations/{customizationId}", "wix-safe-agent-cli customizations-v3 update"),
            "customizationsV3.delete": ("DELETE", "/stores/v3/customizations/{customizationId}", "wix-safe-agent-cli customizations-v3 delete"),
            "customizationsV3.bulkCreate": ("POST", "/stores/v3/bulk/customizations/create", "wix-safe-agent-cli customizations-v3 bulk-create"),
            "customizationsV3.bulkUpdate": ("POST", "/stores/v3/bulk/customizations/update", "wix-safe-agent-cli customizations-v3 bulk-update"),
            "customizationsV3.addChoices": ("POST", "/stores/v3/customizations/{customizationId}/add-choices", "wix-safe-agent-cli customizations-v3 add-choices"),
            "customizationsV3.bulkAddChoices": ("POST", "/stores/v3/bulk/customizations/add-choices", "wix-safe-agent-cli customizations-v3 bulk-add-choices"),
            "customizationsV3.removeChoices": ("POST", "/stores/v3/customizations/{customizationId}/remove-choices", "wix-safe-agent-cli customizations-v3 remove-choices"),
            "customizationsV3.setChoices": ("POST", "/stores/v3/customizations/{customizationId}/set-choices", "wix-safe-agent-cli customizations-v3 set-choices"),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_categories_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("categories", families)
        family = families["categories"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 22)

        by_id = {op.get("method_id"): op for op in operations}

        self.assertEqual(by_id["categories.get"].get("http_method"), "GET")
        self.assertEqual(by_id["categories.get"].get("path"), "/categories/v1/categories/{categoryId}")
        self.assertEqual(by_id["categories.get"].get("planned_command"), "wix-safe-agent-cli categories get")

        self.assertEqual(by_id["categories.query"].get("http_method"), "POST")
        self.assertEqual(by_id["categories.query"].get("path"), "/categories/v1/categories/query")
        self.assertEqual(by_id["categories.query"].get("planned_command"), "wix-safe-agent-cli categories query")

        self.assertEqual(by_id["categories.search"].get("http_method"), "POST")
        self.assertEqual(by_id["categories.search"].get("path"), "/categories/v1/categories/search")
        self.assertEqual(by_id["categories.search"].get("planned_command"), "wix-safe-agent-cli categories search")

        self.assertEqual(by_id["categories.count"].get("http_method"), "POST")
        self.assertEqual(by_id["categories.count"].get("path"), "/categories/v1/categories/count")
        self.assertEqual(by_id["categories.count"].get("planned_command"), "wix-safe-agent-cli categories count")

        self.assertEqual(by_id["categories.listTrees"].get("http_method"), "GET")
        self.assertEqual(by_id["categories.listTrees"].get("path"), "/categories/v1/categories/list-trees")
        self.assertEqual(
            by_id["categories.listTrees"].get("planned_command"),
            "wix-safe-agent-cli categories list-trees",
        )

        self.assertEqual(by_id["categories.getArrangedItems"].get("http_method"), "GET")
        self.assertEqual(
            by_id["categories.getArrangedItems"].get("path"),
            "/categories/v1/categories/{categoryId}/arranged-items",
        )
        self.assertEqual(
            by_id["categories.getArrangedItems"].get("planned_command"),
            "wix-safe-agent-cli categories get-arranged-items",
        )

        self.assertEqual(by_id["categories.listCategoriesForItem"].get("http_method"), "POST")
        self.assertEqual(
            by_id["categories.listCategoriesForItem"].get("path"),
            "/categories/v1/categories/list-categories-for-item",
        )
        self.assertEqual(
            by_id["categories.listCategoriesForItem"].get("planned_command"),
            "wix-safe-agent-cli categories list-categories-for-item",
        )

        self.assertEqual(by_id["categories.listCategoriesForItems"].get("http_method"), "POST")
        self.assertEqual(
            by_id["categories.listCategoriesForItems"].get("path"),
            "/categories/v1/categories/list-categories-for-items",
        )
        self.assertEqual(
            by_id["categories.listCategoriesForItems"].get("planned_command"),
            "wix-safe-agent-cli categories list-categories-for-items",
        )

        self.assertEqual(by_id["categories.listItemsInCategory"].get("http_method"), "POST")
        self.assertEqual(
            by_id["categories.listItemsInCategory"].get("path"),
            "/categories/v1/categories/{categoryId}/list-items",
        )
        self.assertEqual(
            by_id["categories.listItemsInCategory"].get("planned_command"),
            "wix-safe-agent-cli categories list-items-in-category",
        )

        expected_new = {
            "categories.getBySlug": ("GET", "/categories/v1/categories/slug/{slug}", "wix-safe-agent-cli categories get-by-slug"),
            "categories.create": ("POST", "/categories/v1/categories", "wix-safe-agent-cli categories create"),
            "categories.update": ("PATCH", "/categories/v1/categories/{categoryId}", "wix-safe-agent-cli categories update"),
            "categories.delete": ("DELETE", "/categories/v1/categories/{categoryId}", "wix-safe-agent-cli categories delete"),
            "categories.bulkUpdate": ("POST", "/categories/v1/bulk/categories/update", "wix-safe-agent-cli categories bulk-update"),
            "categories.updateVisibility": ("PATCH", "/categories/v1/categories/visibility", "wix-safe-agent-cli categories update-visibility"),
            "categories.bulkShow": ("POST", "/categories/v1/bulk/categories/show", "wix-safe-agent-cli categories bulk-show"),
            "categories.bulkAddItemsToCategory": (
                "POST",
                "/categories/v1/bulk/categories/{categoryId}/add-items",
                "wix-safe-agent-cli categories bulk-add-items-to-category",
            ),
            "categories.bulkAddItemToCategories": (
                "POST",
                "/categories/v1/bulk/categories/add-item",
                "wix-safe-agent-cli categories bulk-add-item-to-categories",
            ),
            "categories.bulkRemoveItemsFromCategory": (
                "POST",
                "/categories/v1/bulk/categories/{categoryId}/remove-items",
                "wix-safe-agent-cli categories bulk-remove-items-from-category",
            ),
            "categories.bulkRemoveItemFromCategories": (
                "POST",
                "/categories/v1/bulk/categories/remove-item",
                "wix-safe-agent-cli categories bulk-remove-item-from-categories",
            ),
            "categories.move": ("POST", "/categories/v1/categories/{categoryId}/move", "wix-safe-agent-cli categories move"),
            "categories.setArrangedItems": (
                "POST",
                "/categories/v1/categories/{categoryId}/set-arranged-items",
                "wix-safe-agent-cli categories set-arranged-items",
            ),
        }
        for method_id, (http_method, path, command) in expected_new.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_stores_inventory_items_v3_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("stores-inventory-items-v3", families)
        family = families["stores-inventory-items-v3"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 6)

        by_id = {op.get("method_id"): op for op in operations}

        self.assertEqual(by_id["storesInventoryItemsV3.get"].get("http_method"), "GET")
        self.assertEqual(
            by_id["storesInventoryItemsV3.get"].get("path"),
            "/stores/v3/inventory-items/{inventoryItemId}",
        )
        self.assertEqual(
            by_id["storesInventoryItemsV3.get"].get("planned_command"),
            "wix-safe-agent-cli stores-inventory-items-v3 get",
        )

        self.assertEqual(by_id["storesInventoryItemsV3.query"].get("http_method"), "POST")
        self.assertEqual(
            by_id["storesInventoryItemsV3.query"].get("path"),
            "/stores/v3/inventory-items/query",
        )
        self.assertEqual(
            by_id["storesInventoryItemsV3.query"].get("planned_command"),
            "wix-safe-agent-cli stores-inventory-items-v3 query",
        )

        self.assertEqual(by_id["storesInventoryItemsV3.search"].get("http_method"), "POST")
        self.assertEqual(
            by_id["storesInventoryItemsV3.search"].get("path"),
            "/stores/v3/inventory-items/search",
        )
        self.assertEqual(
            by_id["storesInventoryItemsV3.search"].get("planned_command"),
            "wix-safe-agent-cli stores-inventory-items-v3 search",
        )

        self.assertEqual(by_id["storesInventoryItemsV3.create"].get("http_method"), "POST")
        self.assertEqual(
            by_id["storesInventoryItemsV3.create"].get("path"),
            "/stores/v3/inventory-items",
        )
        self.assertEqual(
            by_id["storesInventoryItemsV3.create"].get("planned_command"),
            "wix-safe-agent-cli stores-inventory-items-v3 create",
        )

        self.assertEqual(by_id["storesInventoryItemsV3.update"].get("http_method"), "PATCH")
        self.assertEqual(
            by_id["storesInventoryItemsV3.update"].get("path"),
            "/stores/v3/inventory-items/{inventoryItemId}",
        )
        self.assertEqual(
            by_id["storesInventoryItemsV3.update"].get("planned_command"),
            "wix-safe-agent-cli stores-inventory-items-v3 update",
        )

        self.assertEqual(by_id["storesInventoryItemsV3.delete"].get("http_method"), "DELETE")
        self.assertEqual(
            by_id["storesInventoryItemsV3.delete"].get("path"),
            "/stores/v3/inventory-items/{inventoryItemId}",
        )
        self.assertEqual(
            by_id["storesInventoryItemsV3.delete"].get("planned_command"),
            "wix-safe-agent-cli stores-inventory-items-v3 delete",
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_stores_locations_v3_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("stores-locations-v3", families)
        family = families["stores-locations-v3"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 2)

        by_id = {op.get("method_id"): op for op in operations}

        self.assertEqual(by_id["storesLocationsV3.get"].get("http_method"), "GET")
        self.assertEqual(
            by_id["storesLocationsV3.get"].get("path"),
            "/stores/v3/locations/{storesLocationId}",
        )
        self.assertEqual(
            by_id["storesLocationsV3.get"].get("planned_command"),
            "wix-safe-agent-cli stores-locations-v3 get",
        )

        self.assertEqual(by_id["storesLocationsV3.query"].get("http_method"), "POST")
        self.assertEqual(
            by_id["storesLocationsV3.query"].get("path"),
            "/stores/v3/locations/query",
        )
        self.assertEqual(
            by_id["storesLocationsV3.query"].get("planned_command"),
            "wix-safe-agent-cli stores-locations-v3 query",
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_branches_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("branches", families)
        family = families["branches"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 3)

        by_id = {op.get("method_id"): op for op in operations}

        self.assertEqual(by_id["branches.getDefault"].get("http_method"), "GET")
        self.assertEqual(by_id["branches.getDefault"].get("path"), "/branches/v1/branches/default")
        self.assertEqual(
            by_id["branches.getDefault"].get("planned_command"),
            "wix-safe-agent-cli branches get-default",
        )
        self.assertIn("implemented", by_id["branches.getDefault"]["flags"])

        self.assertEqual(by_id["branches.get"].get("http_method"), "GET")
        self.assertEqual(by_id["branches.get"].get("path"), "/branches/v1/branches/{branchId}")
        self.assertEqual(by_id["branches.get"].get("planned_command"), "wix-safe-agent-cli branches get")
        self.assertIn("implemented", by_id["branches.get"]["flags"])

        self.assertEqual(by_id["branches.query"].get("http_method"), "POST")
        self.assertEqual(by_id["branches.query"].get("path"), "/branches/v1/branches/query")
        self.assertEqual(by_id["branches.query"].get("planned_command"), "wix-safe-agent-cli branches query")
        self.assertIn("implemented", by_id["branches.query"]["flags"])

        for op in operations:
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_sender_emails_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("sender-emails", families)
        family = families["sender-emails"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 7)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "senderEmails.list": ("GET", "/sender-emails/v1/sender-emails", "wix-safe-agent-cli sender-emails list"),
            "senderEmails.get": (
                "GET",
                "/sender-emails/v1/sender-emails/{senderEmailId}",
                "wix-safe-agent-cli sender-emails get",
            ),
            "senderEmails.create": ("POST", "/sender-emails/v1/sender-emails", "wix-safe-agent-cli sender-emails create"),
            "senderEmails.delete": (
                "DELETE",
                "/sender-emails/v1/sender-emails/{senderEmailId}",
                "wix-safe-agent-cli sender-emails delete",
            ),
            "senderEmails.getOrCreate": (
                "POST",
                "/sender-emails/v1/sender-emails/get-or-create",
                "wix-safe-agent-cli sender-emails get-or-create",
            ),
            "senderEmails.sendVerificationCode": (
                "POST",
                "/sender-emails/v1/sender-emails/{senderEmailId}/send-verification-code",
                "wix-safe-agent-cli sender-emails send-verification-code",
            ),
            "senderEmails.verify": (
                "POST",
                "/sender-emails/v1/sender-emails/{senderEmailId}/verify",
                "wix-safe-agent-cli sender-emails verify",
            ),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_sender_details_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("sender-details", families)
        family = families["sender-details"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 7)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "senderDetails.list": ("GET", "/sender-details/v1/sender-details", "wix-safe-agent-cli sender-details list"),
            "senderDetails.get": (
                "GET",
                "/sender-details/v1/sender-details/{senderDetailsId}",
                "wix-safe-agent-cli sender-details get",
            ),
            "senderDetails.create": ("POST", "/sender-details/v1/sender-details", "wix-safe-agent-cli sender-details create"),
            "senderDetails.update": (
                "PATCH",
                "/sender-details/v1/sender-details/{senderDetailsId}",
                "wix-safe-agent-cli sender-details update",
            ),
            "senderDetails.delete": (
                "DELETE",
                "/sender-details/v1/sender-details/{senderDetailsId}",
                "wix-safe-agent-cli sender-details delete",
            ),
            "senderDetails.getDefault": (
                "GET",
                "/sender-details/v1/sender-details/default",
                "wix-safe-agent-cli sender-details get-default",
            ),
            "senderDetails.markDefault": (
                "POST",
                "/sender-details/v1/sender-details/{senderDetailsId}/mark-as-default",
                "wix-safe-agent-cli sender-details mark-default",
            ),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_marketing_consent_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("marketing-consent", families)
        family = families["marketing-consent"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "marketingConsent.get": (
                "GET",
                "/marketing-consent/v1/marketing-consent/{marketingConsentId}",
                "wix-safe-agent-cli marketing-consent get",
            ),
            "marketingConsent.query": (
                "POST",
                "/marketing-consent/v1/marketing-consent/query",
                "wix-safe-agent-cli marketing-consent query",
            ),
            "marketingConsent.getByIdentifier": (
                "GET",
                "/marketing-consent/v1/marketing-consent/get-by",
                "wix-safe-agent-cli marketing-consent get-by-identifier",
            ),
            "marketingConsent.create": (
                "POST",
                "/marketing-consent/v1/marketing-consent",
                "wix-safe-agent-cli marketing-consent create",
            ),
            "marketingConsent.update": (
                "PATCH",
                "/marketing-consent/v1/marketing-consent/{marketingConsent.id}",
                "wix-safe-agent-cli marketing-consent update",
            ),
            "marketingConsent.delete": (
                "DELETE",
                "/marketing-consent/v1/marketing-consent/{marketingConsentId}",
                "wix-safe-agent-cli marketing-consent delete",
            ),
            "marketingConsent.upsert": (
                "POST",
                "/marketing-consent/v1/marketing-consent/upsert",
                "wix-safe-agent-cli marketing-consent upsert",
            ),
            "marketingConsent.remove": (
                "POST",
                "/marketing-consent/v1/marketing-consent/remove",
                "wix-safe-agent-cli marketing-consent remove",
            ),
            "marketingConsent.bulkUpsert": (
                "POST",
                "/marketing-consent/v1/bulk/marketing-consent/upsert",
                "wix-safe-agent-cli marketing-consent bulk-upsert",
            ),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_referral_program_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("referral-program", families)
        family = families["referral-program"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 8)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "referralProgram.activateReferralProgram": (
                "PATCH",
                "/_api/referral-programs/v1/program/activate",
                "wix-safe-agent-cli referral-program activate",
            ),
            "referralProgram.generateAISocialMediaPostsSuggestions": (
                "POST",
                "/_api/referral-programs/v1/program/ai-social-media-posts-suggestions",
                "wix-safe-agent-cli referral-program generate-ai-social-media-posts-suggestions",
            ),
            "referralProgram.getAISocialMediaPostsSuggestions": (
                "GET",
                "/_api/referral-programs/v1/program/ai-social-media-posts-suggestions",
                "wix-safe-agent-cli referral-program get-ai-social-media-posts-suggestions",
            ),
            "referralProgram.getReferralProgram": (
                "GET",
                "/_api/referral-programs/v1/program",
                "wix-safe-agent-cli referral-program get",
            ),
            "referralProgram.getReferralProgramPremiumFeatures": (
                "GET",
                "/_api/referral-programs/v1/program/premium-features",
                "wix-safe-agent-cli referral-program get-premium-features",
            ),
            "referralProgram.pauseReferralProgram": (
                "PATCH",
                "/_api/referral-programs/v1/program/pause",
                "wix-safe-agent-cli referral-program pause",
            ),
            "referralProgram.updateReferralProgram": (
                "PATCH",
                "/_api/referral-programs/v1/program",
                "wix-safe-agent-cli referral-program update",
            ),
        }
        self.assertEqual(set(by_id), set(expected) | {"referralProgram.programUpdated"})
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))
        self.assertFalse(by_id["referralProgram.programUpdated"].get("cli_callable"))
        self.assertIn("callback-only", by_id["referralProgram.programUpdated"]["flags"])

    def test_referral_rewards_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("referral-rewards", families)
        family = families["referral-rewards"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 2)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "referralRewards.getReferralReward": (
                "GET",
                "/_api/referral-rewards/v1/referral-rewards/{id}",
                "wix-safe-agent-cli referral-rewards get",
            ),
            "referralRewards.queryReferralRewards": (
                "POST",
                "/_api/referral-rewards/v1/referral-rewards/query",
                "wix-safe-agent-cli referral-rewards query",
            ),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertTrue(by_id[method_id].get("cli_callable"))

    def test_referring_customers_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("referring-customers", families)
        family = families["referring-customers"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 7)
        self.assertEqual(family.get("coverage_status"), "implemented")

        by_id = {op.get("method_id"): op for op in operations}
        expected_callable = {
            "referringCustomers.getReferringCustomer": (
                "GET",
                "/referral-customers/v1/referring-customers/{referringCustomerId}",
                "wix-safe-agent-cli referring-customers get",
            ),
            "referringCustomers.queryReferringCustomers": (
                "POST",
                "/referral-customers/v1/referring-customers/query",
                "wix-safe-agent-cli referring-customers query",
            ),
            "referringCustomers.getReferringCustomerByReferralCode": (
                "GET",
                "/referral-customers/v1/referring-customers/code/{referralCode}",
                "wix-safe-agent-cli referring-customers get-by-referral-code",
            ),
            "referringCustomers.generateReferringCustomerForContact": (
                "POST",
                "/referral-customers/v1/referring-customers",
                "wix-safe-agent-cli referring-customers generate-for-contact",
            ),
            "referringCustomers.deleteReferringCustomer": (
                "DELETE",
                "/referral-customers/v1/referring-customers/{referringCustomerId}",
                "wix-safe-agent-cli referring-customers delete",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_callable.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertTrue(by_id[method_id].get("cli_callable"))

        self.assertIn("plan-first-write", by_id["referringCustomers.generateReferringCustomerForContact"]["flags"])
        self.assertIn("plan-first-write", by_id["referringCustomers.deleteReferringCustomer"]["flags"])
        self.assertIn("ack-irreversible", by_id["referringCustomers.deleteReferringCustomer"]["flags"])
        self.assertIn("revision-query-param", by_id["referringCustomers.deleteReferringCustomer"]["flags"])

        self.assertFalse(by_id["referringCustomers.referringCustomerCreated"].get("cli_callable"))
        self.assertIn("callback-only", by_id["referringCustomers.referringCustomerCreated"]["flags"])
        self.assertFalse(by_id["referringCustomers.referringCustomerDeleted"].get("cli_callable"))
        self.assertIn("callback-only", by_id["referringCustomers.referringCustomerDeleted"]["flags"])

    def test_referred_friends_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("referred-friends", families)
        family = families["referred-friends"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)
        self.assertEqual(family.get("coverage_status"), "implemented")

        by_id = {op.get("method_id"): op for op in operations}
        expected_callable = {
            "referredFriends.getReferredFriend": (
                "GET",
                "/referral_friends/v1/referred-friends/{referredFriendId}",
                "wix-safe-agent-cli referred-friends get",
            ),
            "referredFriends.updateReferredFriend": (
                "PATCH",
                "/referral_friends/v1/referred-friends/{referredFriend.id}",
                "wix-safe-agent-cli referred-friends update",
            ),
            "referredFriends.deleteReferredFriend": (
                "DELETE",
                "/referral_friends/v1/referred-friends/{referredFriendId}",
                "wix-safe-agent-cli referred-friends delete",
            ),
            "referredFriends.queryReferredFriend": (
                "POST",
                "/referral_friends/v1/referred-friends/query",
                "wix-safe-agent-cli referred-friends query",
            ),
            "referredFriends.createReferredFriend": (
                "POST",
                "/referral_friends/v1/referred-friends",
                "wix-safe-agent-cli referred-friends create",
            ),
            "referredFriends.getReferredFriendByContactId": (
                "GET",
                "/referral_friends/v1/referred-friends/contact/{contactId}",
                "wix-safe-agent-cli referred-friends get-by-contact-id",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_callable.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertTrue(by_id[method_id].get("cli_callable"))

        self.assertIn("plan-first-write", by_id["referredFriends.createReferredFriend"]["flags"])
        self.assertIn("plan-first-write", by_id["referredFriends.updateReferredFriend"]["flags"])
        self.assertIn("requires-current-revision", by_id["referredFriends.updateReferredFriend"]["flags"])
        self.assertIn("plan-first-write", by_id["referredFriends.deleteReferredFriend"]["flags"])
        self.assertIn("ack-irreversible", by_id["referredFriends.deleteReferredFriend"]["flags"])
        self.assertIn("revision-query-param", by_id["referredFriends.deleteReferredFriend"]["flags"])

        for method_id in (
            "referredFriends.referredFriendCreated",
            "referredFriends.referredFriendDeleted",
            "referredFriends.referredFriendUpdated",
        ):
            self.assertFalse(by_id[method_id].get("cli_callable"))
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_referral_tracker_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("referral-tracker", families)
        family = families["referral-tracker"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 4)
        self.assertEqual(family.get("coverage_status"), "implemented")

        by_id = {op.get("method_id"): op for op in operations}
        expected_callable = {
            "referralTracker.getReferralEvent": (
                "GET",
                "/_api/referral-tracker/v1/referral-events/{referralEventId}",
                "wix-safe-agent-cli referral-tracker get",
            ),
            "referralTracker.queryReferralEvent": (
                "POST",
                "/_api/referral-tracker/v1/referral-events/query",
                "wix-safe-agent-cli referral-tracker query",
            ),
            "referralTracker.getReferralStatistics": (
                "GET",
                "/_api/referral-tracker/v1/referral-statistics",
                "wix-safe-agent-cli referral-tracker get-statistics",
            ),
        }
        self.assertEqual(set(by_id), set(expected_callable) | {"referralTracker.referralEventCreated"})
        for method_id, (http_method, path, planned_command) in expected_callable.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertTrue(by_id[method_id].get("cli_callable"))

        self.assertFalse(by_id["referralTracker.referralEventCreated"].get("cli_callable"))
        self.assertIn("callback-only", by_id["referralTracker.referralEventCreated"]["flags"])

    def test_sending_domains_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("sending-domains", families)
        family = families["sending-domains"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 3)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "sendingDomains.get": (
                "GET",
                "/sending-domains/v1/sending-domains/{sendingDomainId}",
                "wix-safe-agent-cli sending-domains get",
            ),
            "sendingDomains.query": (
                "POST",
                "/sending-domains/v1/sending-domains/query",
                "wix-safe-agent-cli sending-domains query",
            ),
            "sendingDomains.authenticate": (
                "POST",
                "/sending-domains/v1/sending-domains/{sendingDomainId}/authenticate",
                "wix-safe-agent-cli sending-domains authenticate",
            ),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_email_campaigns_family_tracks_implemented_and_open_methods(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("email-campaigns", families)
        family = families["email-campaigns"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 14)

        by_id = {op.get("method_id"): op for op in operations}
        implemented = {
            "emailCampaigns.get": ("GET", "/email-marketing/v1/campaigns/{campaignId}", "wix-safe-agent-cli email-campaigns get"),
            "emailCampaigns.list": ("GET", "/email-marketing/v1/campaigns", "wix-safe-agent-cli email-campaigns list"),
            "emailCampaigns.getAudience": (
                "POST",
                "/email-marketing/v1/campaigns/{campaignId}/audience",
                "wix-safe-agent-cli email-campaigns get-audience",
            ),
            "emailCampaigns.identifySenderAddress": (
                "POST",
                "/email-marketing/v1/identify-sender-address",
                "wix-safe-agent-cli email-campaigns identify-sender-address",
            ),
            "emailCampaigns.listRecipients": (
                "GET",
                "/email-marketing/v1/campaigns/{campaignId}/statistics/recipients",
                "wix-safe-agent-cli email-campaigns list-recipients",
            ),
            "emailCampaigns.listStatistics": (
                "GET",
                "/email-marketing/v1/campaigns/statistics",
                "wix-safe-agent-cli email-campaigns list-statistics",
            ),
            "emailCampaigns.pauseScheduling": (
                "POST",
                "/email-marketing/v1/campaigns/{campaignId}/pause-scheduling",
                "wix-safe-agent-cli email-campaigns pause-scheduling",
            ),
            "emailCampaigns.publish": (
                "POST",
                "/email-marketing/v1/campaigns/{campaignId}/publish",
                "wix-safe-agent-cli email-campaigns publish",
            ),
            "emailCampaigns.reschedule": (
                "POST",
                "/email-marketing/v1/campaigns/{campaignId}/reschedule",
                "wix-safe-agent-cli email-campaigns reschedule",
            ),
            "emailCampaigns.reuse": (
                "POST",
                "/email-marketing/v1/campaigns/{campaignId}/reuse",
                "wix-safe-agent-cli email-campaigns reuse",
            ),
            "emailCampaigns.sendTest": (
                "POST",
                "/email-marketing/v1/campaigns/{campaignId}/test",
                "wix-safe-agent-cli email-campaigns send-test",
            ),
            "emailCampaigns.delete": (
                "DELETE",
                "/email-marketing/v1/campaigns/{campaignId}",
                "wix-safe-agent-cli email-campaigns delete",
            ),
            "campaignValidation.validateHtmlLinks": (
                "POST",
                "/email-marketing/v1/campaign-validation/validate-html-links",
                "wix-safe-agent-cli campaign-validation validate-html-links",
            ),
            "campaignValidation.validateLink": (
                "POST",
                "/email-marketing/v1/campaign-validation/validate-link",
                "wix-safe-agent-cli campaign-validation validate-link",
            ),
        }

        self.assertEqual(set(by_id), set(implemented))
        for method_id, (http_method, path, planned_command) in implemented.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_editor_deep_link_family_is_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("editor-deep-link", families)
        family = families["editor-deep-link"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)

        op = operations[0]
        self.assertEqual(op.get("method_id"), "editorDeepLink.create")
        self.assertEqual(op.get("http_method"), "POST")
        self.assertEqual(op.get("path"), "/apps/v1/post-installation/editor-deep-link")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli editor-deep-link create")
        self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
        self.assertIn("implemented", op["flags"])

    def test_cms_data_items_family_is_present_and_unique(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("cms-data-items", families)
        family = families["cms-data-items"]
        self.assertIn("operations", family)
        self.assertTrue(family["operations"])

        method_ids = [op["method_id"] for op in family["operations"]]
        self.assertEqual(len(method_ids), len(set(method_ids)), "Method IDs must be unique")

        for op in family["operations"]:
            self.assertTrue(str(op["doc_url"]).startswith("https://dev.wix.com/docs/"))
            self.assertIn("flags", op)
            self.assertTrue(op["flags"])

    def test_cms_data_items_advanced_write_methods_are_marked_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["cms-data-items"]
        operations = {op["method_id"]: op for op in family["operations"]}

        expected = {
            "dataItems.save": "wix-safe-agent-cli data-items save",
            "dataItems.truncate": "wix-safe-agent-cli data-items truncate",
            "dataItems.bulkRemove": "wix-safe-agent-cli data-items bulk-remove",
            "dataItems.bulkSave": "wix-safe-agent-cli data-items bulk-save",
            "dataItems.bulkUpdate": "wix-safe-agent-cli data-items bulk-update",
            "dataItems.bulkInsertReferences": "wix-safe-agent-cli data-items bulk-insert-references",
            "dataItems.bulkRemoveReferences": "wix-safe-agent-cli data-items bulk-remove-references",
        }

        for method_id, planned_command in expected.items():
            self.assertIn(method_id, operations)
            op = operations[method_id]
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertIn("implemented", op.get("flags", []))
            self.assertIsNotNone(op.get("http_method"))
            self.assertIsNotNone(op.get("path"))

    def test_contact_labels_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("contact-labels", families)
        family = families["contact-labels"]
        self.assertIn("operations", family)

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 6)

        expected_commands = {
            "wix-safe-agent-cli contact-labels query",
            "wix-safe-agent-cli contact-labels list",
            "wix-safe-agent-cli contact-labels find-or-create",
            "wix-safe-agent-cli contact-labels get",
            "wix-safe-agent-cli contact-labels update",
            "wix-safe-agent-cli contact-labels delete",
        }

        method_ids = [op.get("method_id") for op in operations]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(
            expected_commands.issubset(inventory_commands),
            msg=(
                "Missing contact labels planned commands in inventory: "
                f"{sorted(expected_commands - inventory_commands)}"
            ),
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertIsNotNone(op["planned_command"])
            self.assertIsNotNone(op["http_method"])
            self.assertIsNotNone(op["path"])

    def test_contact_extended_fields_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("contact-extended-fields", families)
        family = families["contact-extended-fields"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "contactExtendedFields.getExtendedField": (
                "GET",
                "/contacts/v4/extended-fields/{key}",
                "wix-safe-agent-cli contact-extended-fields get",
            ),
            "contactExtendedFields.updateExtendedField": (
                "PATCH",
                "/contacts/v4/extended-fields/{field.key}",
                "wix-safe-agent-cli contact-extended-fields update",
            ),
            "contactExtendedFields.deleteExtendedField": (
                "DELETE",
                "/contacts/v4/extended-fields/{key}",
                "wix-safe-agent-cli contact-extended-fields delete",
            ),
            "contactExtendedFields.queryExtendedFields": (
                "POST",
                "/contacts/v4/extended-fields/query",
                "wix-safe-agent-cli contact-extended-fields query",
            ),
            "contactExtendedFields.listExtendedFields": (
                "GET",
                "/contacts/v4/extended-fields",
                "wix-safe-agent-cli contact-extended-fields list",
            ),
            "contactExtendedFields.findOrCreateExtendedField": (
                "POST",
                "/contacts/v4/extended-fields",
                "wix-safe-agent-cli contact-extended-fields find-or-create",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        self.assertIn("requires-ack-irreversible", by_id["contactExtendedFields.deleteExtendedField"]["flags"])

        for method_id in [
            "contactExtendedFields.extendedFieldCreated",
            "contactExtendedFields.extendedFieldDeleted",
            "contactExtendedFields.extendedFieldUpdated",
        ]:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id].get("flags", []))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertFalse(by_id[method_id].get("cli_callable"))

    def test_contact_notes_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("contact-notes", families)
        family = families["contact-notes"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 8)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "contactNotes.createNote": ("POST", "/crm/notes/v2/notes", "wix-safe-agent-cli contact-notes create"),
            "contactNotes.getNote": ("GET", "/crm/notes/v2/notes/{noteId}", "wix-safe-agent-cli contact-notes get"),
            "contactNotes.updateNote": (
                "PATCH",
                "/crm/notes/v2/notes/{note.id}",
                "wix-safe-agent-cli contact-notes update",
            ),
            "contactNotes.deleteNote": (
                "DELETE",
                "/crm/notes/v2/notes/{noteId}",
                "wix-safe-agent-cli contact-notes delete",
            ),
            "contactNotes.queryNotes": ("POST", "/crm/notes/v2/notes/query", "wix-safe-agent-cli contact-notes query"),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        self.assertIn("requires-ack-irreversible", by_id["contactNotes.deleteNote"]["flags"])

        for method_id in ["contactNotes.noteCreated", "contactNotes.noteDeleted", "contactNotes.noteUpdated"]:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id].get("flags", []))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertFalse(by_id[method_id].get("cli_callable"))

    def test_contact_attachments_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("contact-attachments", families)
        family = families["contact-attachments"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 6)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "contactAttachments.getAttachment": (
                "GET",
                "/contacts/v4/attachments/{contactId}/{attachmentId}",
                "wix-safe-agent-cli contact-attachments get",
            ),
            "contactAttachments.listAttachments": (
                "GET",
                "/contacts/v4/attachments/{contactId}",
                "wix-safe-agent-cli contact-attachments list",
            ),
            "contactAttachments.generateAttachmentUploadUrl": (
                "POST",
                "/contacts/v4/attachments/{contactId}/upload-url",
                "wix-safe-agent-cli contact-attachments generate-upload-url",
            ),
            "contactAttachments.deleteAttachment": (
                "DELETE",
                "/contacts/v4/attachments/{contactId}/{attachmentId}",
                "wix-safe-agent-cli contact-attachments delete",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        self.assertIn("requires-ack-irreversible", by_id["contactAttachments.deleteAttachment"]["flags"])

        for method_id in [
            "contactAttachments.attachmentCreated",
            "contactAttachments.attachmentDeleted",
        ]:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id].get("flags", []))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertFalse(by_id[method_id].get("cli_callable"))

    def test_contacts_v4_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("contacts", families)
        family = families["contacts"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 20)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "contacts.listContacts": ("GET", "/contacts/v4/contacts", "wix-safe-agent-cli contacts list"),
            "contacts.getContact": ("GET", "/contacts/v4/contacts/{id}", "wix-safe-agent-cli contacts get"),
            "contacts.queryContacts": ("POST", "/contacts/v4/contacts/query", "wix-safe-agent-cli contacts query"),
            "contacts.listFacets": ("GET", "/contacts/v4/contacts/facets", "wix-safe-agent-cli contacts list-facets"),
            "contacts.queryFacets": (
                "POST",
                "/contacts/v4/contacts/facets/query",
                "wix-safe-agent-cli contacts query-facets",
            ),
            "contacts.getBulkJob": ("GET", "/contacts/v4/bulk/jobs/{id}", "wix-safe-agent-cli contacts get-bulk-job"),
            "contacts.previewMergeContacts": (
                "POST",
                "/contacts/v4/contacts/{targetContactId}/preview-merge",
                "wix-safe-agent-cli contacts preview-merge",
            ),
            "contacts.createContact": ("POST", "/contacts/v4/contacts", "wix-safe-agent-cli contacts create"),
            "contacts.updateContact": (
                "PATCH",
                "/contacts/v4/contacts/{contactId}",
                "wix-safe-agent-cli contacts update",
            ),
            "contacts.deleteContact": (
                "DELETE",
                "/contacts/v4/contacts/{contactId}",
                "wix-safe-agent-cli contacts delete",
            ),
            "contacts.mergeContacts": (
                "POST",
                "/contacts/v4/contacts/{targetContactId}/merge",
                "wix-safe-agent-cli contacts merge",
            ),
            "contacts.labelContact": (
                "POST",
                "/contacts/v4/contacts/{contactId}/labels",
                "wix-safe-agent-cli contacts label",
            ),
            "contacts.unlabelContact": (
                "DELETE",
                "/contacts/v4/contacts/{contactId}/labels",
                "wix-safe-agent-cli contacts unlabel",
            ),
            "contacts.bulkDeleteContacts": (
                "POST",
                "/contacts/v4/bulk/contacts/delete",
                "wix-safe-agent-cli contacts bulk-delete",
            ),
            "contacts.bulkUpdateContacts": (
                "POST",
                "/contacts/v4/bulk/contacts/update",
                "wix-safe-agent-cli contacts bulk-update",
            ),
            "contacts.bulkLabelAndUnlabelContacts": (
                "POST",
                "/contacts/v4/bulk/contacts/add-remove-labels",
                "wix-safe-agent-cli contacts bulk-label-unlabel",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        for method_id in [
            "contacts.deleteContact",
            "contacts.mergeContacts",
            "contacts.bulkDeleteContacts",
            "contacts.bulkUpdateContacts",
            "contacts.bulkLabelAndUnlabelContacts",
        ]:
            self.assertIn("requires-ack-irreversible", by_id[method_id]["flags"])

        for method_id in [
            "contacts.contactCreated",
            "contacts.contactDeleted",
            "contacts.contactMerged",
            "contacts.contactUpdated",
        ]:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id].get("flags", []))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertFalse(by_id[method_id].get("cli_callable"))

    def test_app_permissions_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("app-permissions", families)
        family = families["app-permissions"]
        self.assertIn("operations", family)

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 3)

        expected_commands = {
            "wix-safe-agent-cli app-permissions list",
            "wix-safe-agent-cli app-permissions create",
            "wix-safe-agent-cli app-permissions delete",
        }

        method_ids = [op.get("method_id") for op in operations]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(
            expected_commands.issubset(inventory_commands),
            msg=(
                "Missing app-permissions planned commands in inventory: "
                f"{sorted(expected_commands - inventory_commands)}"
            ),
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertIsNotNone(op["planned_command"])
            self.assertIsNotNone(op["http_method"])
            self.assertIsNotNone(op["path"])

    def test_app_installation_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("app-installation", families)
        family = families["app-installation"]
        self.assertIn("operations", family)
        self.assertIn("live-unverified", family.get("default_flags", []))

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 7)

        expected_commands = {
            "wix-safe-agent-cli app-installation get-installed",
            "wix-safe-agent-cli app-installation is-permitted",
            "wix-safe-agent-cli app-installation install",
            "wix-safe-agent-cli app-installation install-from-share-url",
            "wix-safe-agent-cli app-installation uninstall",
            "wix-safe-agent-cli app-installation bulk-install",
            "wix-safe-agent-cli app-installation bulk-uninstall",
        }
        expected_methods = {
            "appInstallation.getInstalledApps": ("GET", "/apps-installer-service/v1/app-instances"),
            "appInstallation.isPermittedToInstallApps": (
                "POST",
                "/apps-installer-service/v1/app-instance/is-permitted-to-install",
            ),
            "appInstallation.install": ("POST", "/apps-installer-service/v1/app-instance/install"),
            "appInstallation.installFromShareUrl": (
                "POST",
                "/apps-installer-service/v1/app-share-url/install",
            ),
            "appInstallation.uninstall": ("POST", "/apps-installer-service/v1/app-instance/uninstall"),
            "appInstallation.bulkInstall": ("POST", "/apps-installer-service/v1/bulk/app-instance/install"),
            "appInstallation.bulkUninstall": (
                "POST",
                "/apps-installer-service/v1/bulk/app-instance/uninstall",
            ),
        }

        method_ids = [op.get("method_id") for op in operations]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(
            expected_commands.issubset(inventory_commands),
            msg=(
                "Missing app-installation planned commands in inventory: "
                f"{sorted(expected_commands - inventory_commands)}"
            ),
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertIsNotNone(op.get("http_method"))
            self.assertIsNotNone(op.get("path"))

        for method_id, (http_method, path) in expected_methods.items():
            op = {op.get("method_id"): op for op in operations}[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)

    def test_custom_embeds_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("custom-embeds", families)
        family = families["custom-embeds"]
        self.assertIn("operations", family)
        self.assertIn("live-unverified", family.get("default_flags", []))

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 5)

        expected_commands = {
            "wix-safe-agent-cli custom-embeds list",
            "wix-safe-agent-cli custom-embeds get",
            "wix-safe-agent-cli custom-embeds create",
            "wix-safe-agent-cli custom-embeds update",
            "wix-safe-agent-cli custom-embeds delete",
        }
        expected_methods = {
            "customEmbeds.list": ("GET", "/embeds/v1/custom-embeds"),
            "customEmbeds.get": ("GET", "/embeds/v1/custom-embeds/{customEmbedId}"),
            "customEmbeds.create": ("POST", "/embeds/v1/custom-embeds"),
            "customEmbeds.update": ("PATCH", "/embeds/v1/custom-embeds/{customEmbed.id}"),
            "customEmbeds.delete": ("DELETE", "/embeds/v1/custom-embeds/{customEmbedId}"),
        }

        method_ids = [op.get("method_id") for op in operations]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(
            expected_commands.issubset(inventory_commands),
            msg=(
                "Missing custom-embeds planned commands in inventory: "
                f"{sorted(expected_commands - inventory_commands)}"
            ),
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertIsNotNone(op.get("http_method"))
            self.assertIsNotNone(op.get("path"))

        for method_id, (http_method, path) in expected_methods.items():
            op = {op.get("method_id"): op for op in operations}[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)

    def test_data_extension_schemas_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("cms-data-extension-schemas", families)
        family = families["cms-data-extension-schemas"]
        self.assertIn("live-unverified", family.get("default_flags", []))

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 4)

        expected_commands = {
            "wix-safe-agent-cli data-extension-schemas list",
            "wix-safe-agent-cli data-extension-schemas create",
            "wix-safe-agent-cli data-extension-schemas update",
            "wix-safe-agent-cli data-extension-schemas delete-user-defined-fields",
        }
        expected_methods = {
            "dataExtensionSchemas.list": ("GET", "/schema-service/v1/schemas"),
            "dataExtensionSchemas.create": ("POST", "/schema-service/v1/schemas"),
            "dataExtensionSchemas.update": ("PUT", "/schema-service/v1/schemas"),
            "dataExtensionSchemas.deleteUserDefinedFields": (
                "POST",
                "/schema-service/v1/schemas/delete-user-defined-fields",
            ),
        }

        method_ids = [op.get("method_id") for op in operations]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(
            expected_commands.issubset(inventory_commands),
            msg=(
                "Missing data-extension-schemas planned commands in inventory: "
                f"{sorted(expected_commands - inventory_commands)}"
            ),
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertIsNotNone(op.get("http_method"))
            self.assertIsNotNone(op.get("path"))

        for method_id, (http_method, path) in expected_methods.items():
            op = {op.get("method_id"): op for op in operations}[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)

    def test_secrets_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("secrets", families)
        family = families["secrets"]
        self.assertIn("live-unverified", family.get("default_flags", []))

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 5)

        expected_commands = {
            "wix-safe-agent-cli secrets list",
            "wix-safe-agent-cli secrets get-value",
            "wix-safe-agent-cli secrets create",
            "wix-safe-agent-cli secrets patch",
            "wix-safe-agent-cli secrets delete",
        }
        expected_methods = {
            "secrets.list": ("GET", "/_api/cloud-secrets-vault-server/api/v1/secrets"),
            "secrets.getValue": ("GET", "/_api/cloud-secrets-vault-server/api/v1/secrets/name/{name}"),
            "secrets.create": ("POST", "/_api/cloud-secrets-vault-server/api/v1/secrets"),
            "secrets.patch": ("PATCH", "/_api/cloud-secrets-vault-server/api/v1/secrets/{id}"),
            "secrets.delete": ("DELETE", "/_api/cloud-secrets-vault-server/api/v1/secrets/{id}"),
        }

        method_ids = [op.get("method_id") for op in operations]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(
            expected_commands.issubset(inventory_commands),
            msg=(
                "Missing secrets planned commands in inventory: "
                f"{sorted(expected_commands - inventory_commands)}"
            ),
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertIsNotNone(op.get("http_method"))
            self.assertIsNotNone(op.get("path"))

        for method_id, (http_method, path) in expected_methods.items():
            op = {op.get("method_id"): op for op in operations}[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)

    def test_notifications_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("notifications", families)
        family = families["notifications"]
        self.assertIn("operations", family)

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)

        op = operations[0]
        self.assertEqual(op.get("method_id"), "notifications.notify")
        self.assertEqual(op.get("http_method"), "POST")
        self.assertEqual(op.get("path"), "/notifications/v3/notify")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli notifications notify")
        self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
        self.assertIn("implemented", op["flags"])

    def test_pricing_plans_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("pricing-plans", families)
        family = families["pricing-plans"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 8)

        by_id = {op.get("method_id"): op for op in operations}

        self.assertEqual(by_id["pricingPlans.get"].get("http_method"), "GET")
        self.assertEqual(by_id["pricingPlans.get"].get("path"), "/pricing-plans/v3/plans/{planId}")
        self.assertEqual(by_id["pricingPlans.get"].get("planned_command"), "wix-safe-agent-cli pricing-plans get")
        self.assertIn("implemented", by_id["pricingPlans.get"]["flags"])

        self.assertEqual(by_id["pricingPlans.query"].get("http_method"), "POST")
        self.assertEqual(by_id["pricingPlans.query"].get("path"), "/pricing-plans/v3/plans/query")
        self.assertEqual(by_id["pricingPlans.query"].get("planned_command"), "wix-safe-agent-cli pricing-plans query")
        self.assertIn("implemented", by_id["pricingPlans.query"]["flags"])

        self.assertEqual(by_id["pricingPlans.search"].get("http_method"), "POST")
        self.assertEqual(by_id["pricingPlans.search"].get("path"), "/pricing-plans/v3/plans/search")
        self.assertEqual(by_id["pricingPlans.search"].get("planned_command"), "wix-safe-agent-cli pricing-plans search")
        self.assertIn("implemented", by_id["pricingPlans.search"]["flags"])

        self.assertEqual(by_id["pricingPlans.count"].get("http_method"), "POST")
        self.assertEqual(by_id["pricingPlans.count"].get("path"), "/pricing-plans/v3/plans/count")
        self.assertEqual(by_id["pricingPlans.count"].get("planned_command"), "wix-safe-agent-cli pricing-plans count")
        self.assertIn("implemented", by_id["pricingPlans.count"]["flags"])

        self.assertEqual(by_id["pricingPlans.create"].get("http_method"), "POST")
        self.assertEqual(by_id["pricingPlans.create"].get("path"), "/pricing-plans/v3/plans")
        self.assertEqual(by_id["pricingPlans.create"].get("planned_command"), "wix-safe-agent-cli pricing-plans create")
        self.assertIn("implemented", by_id["pricingPlans.create"]["flags"])

        self.assertEqual(by_id["pricingPlans.update"].get("http_method"), "PATCH")
        self.assertEqual(by_id["pricingPlans.update"].get("path"), "/pricing-plans/v3/plans/{plan.id}")
        self.assertEqual(by_id["pricingPlans.update"].get("planned_command"), "wix-safe-agent-cli pricing-plans update")
        self.assertIn("implemented", by_id["pricingPlans.update"]["flags"])

        self.assertEqual(by_id["pricingPlans.delete"].get("http_method"), "DELETE")
        self.assertEqual(by_id["pricingPlans.delete"].get("path"), "/pricing-plans/v3/plans/{planId}")
        self.assertEqual(by_id["pricingPlans.delete"].get("planned_command"), "wix-safe-agent-cli pricing-plans delete")
        self.assertIn("implemented", by_id["pricingPlans.delete"]["flags"])

        self.assertEqual(by_id["pricingPlans.bulkUpdate"].get("http_method"), "POST")
        self.assertEqual(by_id["pricingPlans.bulkUpdate"].get("path"), "/pricing-plans/v3/plans/bulk/update")
        self.assertEqual(
            by_id["pricingPlans.bulkUpdate"].get("planned_command"),
            "wix-safe-agent-cli pricing-plans bulk-update",
        )
        self.assertIn("implemented", by_id["pricingPlans.bulkUpdate"]["flags"])

    def test_portfolio_projects_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("portfolio-projects", families)
        family = families["portfolio-projects"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 10)

        by_id = {op.get("method_id"): op for op in operations}

        expected = {
            "portfolioProjects.create": ("POST", "/portfolio/v1/projects", "wix-safe-agent-cli portfolio-projects create"),
            "portfolioProjects.get": ("GET", "/portfolio/v1/projects/{projectId}", "wix-safe-agent-cli portfolio-projects get"),
            "portfolioProjects.update": ("PATCH", "/portfolio/v1/projects/{project.id}", "wix-safe-agent-cli portfolio-projects update"),
            "portfolioProjects.delete": ("DELETE", "/portfolio/v1/projects/{projectId}", "wix-safe-agent-cli portfolio-projects delete"),
            "portfolioProjects.query": ("POST", "/portfolio/v1/projects/query", "wix-safe-agent-cli portfolio-projects query"),
            "portfolioProjects.list": ("GET", "/portfolio/v1/projects", "wix-safe-agent-cli portfolio-projects list"),
            "portfolioProjects.bulkUpdate": (
                "PATCH",
                "/portfolio/projects/projects/api/v1/bulk/portfolio/projects/update",
                "wix-safe-agent-cli portfolio-projects bulk-update",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        for method_id in ("portfolioProjects.created", "portfolioProjects.deleted", "portfolioProjects.updated"):
            with self.subTest(method_id=method_id):
                self.assertIsNone(by_id[method_id].get("http_method"))
                self.assertIsNone(by_id[method_id].get("path"))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertIn("callback-only", by_id[method_id]["flags"])
                self.assertFalse(by_id[method_id]["cli_callable"])

    def test_portfolio_project_items_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("portfolio-project-items", families)
        family = families["portfolio-project-items"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 12)

        by_id = {op.get("method_id"): op for op in operations}

        expected = {
            "portfolioProjectItems.create": ("POST", "/portfolio/v1/items", "wix-safe-agent-cli portfolio-project-items create"),
            "portfolioProjectItems.get": ("GET", "/portfolio/v1/items/{itemId}", "wix-safe-agent-cli portfolio-project-items get"),
            "portfolioProjectItems.update": ("PATCH", "/portfolio/v1/items/{item.id}", "wix-safe-agent-cli portfolio-project-items update"),
            "portfolioProjectItems.delete": ("DELETE", "/portfolio/v1/items/{itemId}", "wix-safe-agent-cli portfolio-project-items delete"),
            "portfolioProjectItems.list": ("GET", "/portfolio/v1/projectItems/{projectId}/items", "wix-safe-agent-cli portfolio-project-items list"),
            "portfolioProjectItems.bulkCreate": (
                "POST",
                "/portfolio/project-items/api/v1/bulk/portfolio/items/create",
                "wix-safe-agent-cli portfolio-project-items bulk-create",
            ),
            "portfolioProjectItems.bulkUpdate": (
                "PATCH",
                "/portfolio/project-items/api/v1/bulk/portfolio/items/update",
                "wix-safe-agent-cli portfolio-project-items bulk-update",
            ),
            "portfolioProjectItems.bulkDelete": (
                "DELETE",
                "/portfolio/project-items/api/v1/bulk/portfolio/items/delete",
                "wix-safe-agent-cli portfolio-project-items bulk-delete",
            ),
            "portfolioProjectItems.duplicate": (
                "POST",
                "/portfolio/project-items/api/v1/items/duplicate",
                "wix-safe-agent-cli portfolio-project-items duplicate",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        for method_id in ("portfolioProjectItems.created", "portfolioProjectItems.deleted", "portfolioProjectItems.updated"):
            with self.subTest(method_id=method_id):
                self.assertIsNone(by_id[method_id].get("http_method"))
                self.assertIsNone(by_id[method_id].get("path"))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertIn("callback-only", by_id[method_id]["flags"])
                self.assertFalse(by_id[method_id]["cli_callable"])

    def test_suppliers_hub_products_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("suppliers-hub-products", families)
        family = families["suppliers-hub-products"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 17)
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {op.get("method_id"): op for op in operations}

        expected = {
            "suppliersHubProducts.create": ("POST", "/suppliers-hub/v1/products", "wix-safe-agent-cli suppliers-hub-products create"),
            "suppliersHubProducts.get": ("GET", "/suppliers-hub/v1/products/{productId}", "wix-safe-agent-cli suppliers-hub-products get"),
            "suppliersHubProducts.update": ("PATCH", "/suppliers-hub/v1/products/{product.id}", "wix-safe-agent-cli suppliers-hub-products update"),
            "suppliersHubProducts.delete": ("DELETE", "/suppliers-hub/v1/products/{productId}", "wix-safe-agent-cli suppliers-hub-products delete"),
            "suppliersHubProducts.query": ("POST", "/suppliers-hub/v1/products/query", "wix-safe-agent-cli suppliers-hub-products query"),
            "suppliersHubProducts.search": ("POST", "/suppliers-hub/v1/products/search", "wix-safe-agent-cli suppliers-hub-products search"),
            "suppliersHubProducts.bulkCreate": ("POST", "/suppliers-hub/v1/bulk/products/create", "wix-safe-agent-cli suppliers-hub-products bulk-create"),
            "suppliersHubProducts.bulkDelete": ("POST", "/suppliers-hub/v1/bulk/products/delete", "wix-safe-agent-cli suppliers-hub-products bulk-delete"),
            "suppliersHubProducts.bulkUpdate": ("PATCH", "/suppliers-hub/v1/bulk/products/update", "wix-safe-agent-cli suppliers-hub-products bulk-update"),
            "suppliersHubProducts.bulkAddToStore": (
                "POST",
                "/suppliershub/marketplace-product/v1/bulk/add-products-to-store",
                "wix-safe-agent-cli suppliers-hub-products bulk-add-to-store",
            ),
            "suppliersHubProducts.bulkUpdateTags": ("POST", "/suppliers-hub/v1/bulk/products/update-tags", "wix-safe-agent-cli suppliers-hub-products bulk-update-tags"),
            "suppliersHubProducts.bulkUpdateTagsByFilter": (
                "POST",
                "/suppliers-hub/v1/bulk/products/update-tags-by-filter",
                "wix-safe-agent-cli suppliers-hub-products bulk-update-tags-by-filter",
            ),
            "suppliersHubProducts.queryCategories": ("POST", "/suppliers-hub/v1/categories/query", "wix-safe-agent-cli suppliers-hub-products query-categories"),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        for method_id in (
            "suppliersHubProducts.productCreated",
            "suppliersHubProducts.productDeleted",
            "suppliersHubProducts.productTagsModified",
            "suppliersHubProducts.productUpdated",
        ):
            with self.subTest(method_id=method_id):
                self.assertIsNone(by_id[method_id].get("http_method"))
                self.assertIsNone(by_id[method_id].get("path"))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertIn("callback-only", by_id[method_id]["flags"])
                self.assertFalse(by_id[method_id]["cli_callable"])

    def test_suppliers_hub_suppliers_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("suppliers-hub-suppliers", families)
        family = families["suppliers-hub-suppliers"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 14)
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {op.get("method_id"): op for op in operations}

        expected = {
            "suppliersHubSuppliers.create": ("POST", "/suppliers-hub/v1/suppliers", "wix-safe-agent-cli suppliers-hub-suppliers create"),
            "suppliersHubSuppliers.get": ("GET", "/suppliers-hub/v1/suppliers/{supplierId}", "wix-safe-agent-cli suppliers-hub-suppliers get"),
            "suppliersHubSuppliers.update": ("PATCH", "/suppliers-hub/v1/suppliers/{supplier.id}", "wix-safe-agent-cli suppliers-hub-suppliers update"),
            "suppliersHubSuppliers.delete": ("DELETE", "/suppliers-hub/v1/suppliers/{supplierId}", "wix-safe-agent-cli suppliers-hub-suppliers delete"),
            "suppliersHubSuppliers.query": ("POST", "/suppliers-hub/v1/suppliers/query", "wix-safe-agent-cli suppliers-hub-suppliers query"),
            "suppliersHubSuppliers.bulkCreate": ("POST", "/suppliers-hub/v1/bulk/suppliers/create", "wix-safe-agent-cli suppliers-hub-suppliers bulk-create"),
            "suppliersHubSuppliers.bulkDelete": ("POST", "/suppliers-hub/v1/bulk/suppliers/delete", "wix-safe-agent-cli suppliers-hub-suppliers bulk-delete"),
            "suppliersHubSuppliers.bulkUpdate": ("POST", "/suppliers-hub/v1/bulk/suppliers/update", "wix-safe-agent-cli suppliers-hub-suppliers bulk-update"),
            "suppliersHubSuppliers.bulkUpdateTags": ("POST", "/suppliers-hub/v1/bulk/suppliers/update-tags", "wix-safe-agent-cli suppliers-hub-suppliers bulk-update-tags"),
            "suppliersHubSuppliers.bulkUpdateTagsByFilter": (
                "POST",
                "/suppliers-hub/v1/bulk/suppliers/update-tags-by-filter",
                "wix-safe-agent-cli suppliers-hub-suppliers bulk-update-tags-by-filter",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        for method_id in (
            "suppliersHubSuppliers.supplierCreated",
            "suppliersHubSuppliers.supplierDeleted",
            "suppliersHubSuppliers.supplierTagsModified",
            "suppliersHubSuppliers.supplierUpdated",
        ):
            with self.subTest(method_id=method_id):
                self.assertIsNone(by_id[method_id].get("http_method"))
                self.assertIsNone(by_id[method_id].get("path"))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertIn("callback-only", by_id[method_id]["flags"])
                self.assertFalse(by_id[method_id]["cli_callable"])

    def test_suppliers_hub_marketplace_provider_submissions_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("suppliers-hub-marketplace-provider-submissions", families)
        family = families["suppliers-hub-marketplace-provider-submissions"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)
        self.assertIn("developer-preview", family.get("default_flags", []))

        operation = operations[0]
        self.assertEqual(operation.get("method_id"), "suppliersHubMarketplaceProviderSubmissions.submitGeneratedMockups")
        self.assertEqual(operation.get("http_method"), "POST")
        self.assertEqual(operation.get("path"), "/suppliershub/v2/submit-generated-mockups")
        self.assertEqual(
            operation.get("planned_command"),
            "wix-safe-agent-cli suppliers-hub-marketplace-provider-submissions submit-generated-mockups",
        )
        self.assertIn("implemented", operation["flags"])
        self.assertIn("docs-endpoint-conflict", operation["flags"])
        self.assertTrue(operation["cli_callable"])

    def test_orders_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("orders", families)
        family = families["orders"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 6)

        expected = {
            "orders.search": ("POST", "/ecom/v1/orders/search", "wix-safe-agent-cli orders search"),
            "orders.get": ("GET", "/ecom/v1/orders/{id}", "wix-safe-agent-cli orders get"),
            "orders.create": ("POST", "/ecom/v1/orders", "wix-safe-agent-cli orders create"),
            "orders.update": ("PATCH", "/ecom/v1/orders/{order.id}", "wix-safe-agent-cli orders update"),
            "orders.cancel": ("POST", "/ecom/v1/orders/{id}/cancel", "wix-safe-agent-cli orders cancel"),
            "orders.bulkUpdate": (
                "POST",
                "/ecom/v1/bulk/orders/update",
                "wix-safe-agent-cli orders bulk-update",
            ),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))

        for method_id, (http_method, path, planned_command) in expected.items():
            op = by_id[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_bookings_time_slots_v2_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-time-slots-v2", families)
        family = families["bookings-time-slots-v2"]

        self.assertEqual(
            family.get("source_urls"),
            [
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/introduction",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/introduction",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/list-availability-time-slots",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/get-availability-time-slot",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/list-event-time-slots",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/get-event-time-slot",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/list-multi-service-availability-time-slots",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/get-multi-service-availability-time-slot",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/time-slot-object",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/flow-single-service-booking",
            ],
        )
        self.assertEqual(
            family.get("default_flags"),
            ["official-docs", "live-unverified"],
        )

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 6)

        expected = {
            "bookingsTimeSlotsV2.listAvailability": (
                "POST",
                "/_api/service-availability/v2/time-slots",
                "wix-safe-agent-cli bookings-time-slots-v2 list-availability",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/list-availability-time-slots",
            ),
            "bookingsTimeSlotsV2.getAvailability": (
                "POST",
                "/_api/service-availability/v2/time-slots/get",
                "wix-safe-agent-cli bookings-time-slots-v2 get-availability",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/get-availability-time-slot",
            ),
            "bookingsTimeSlotsV2.listEventTimeSlots": (
                "POST",
                "/_api/service-availability/v2/time-slots/event",
                "wix-safe-agent-cli bookings-time-slots-v2 list-event",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/list-event-time-slots",
            ),
            "bookingsTimeSlotsV2.getEventTimeSlot": (
                "GET",
                "/_api/service-availability/v2/time-slots/event/{eventId}",
                "wix-safe-agent-cli bookings-time-slots-v2 get-event",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/get-event-time-slot",
            ),
            "bookingsTimeSlotsV2.listMultiServiceAvailabilityTimeSlots": (
                "POST",
                "/_api/service-availability/v2/multi-service-time-slots",
                "wix-safe-agent-cli bookings-time-slots-v2 list-multi-service",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/list-multi-service-availability-time-slots",
            ),
            "bookingsTimeSlotsV2.getMultiServiceAvailabilityTimeSlot": (
                "POST",
                "/_api/service-availability/v2/multi-service-time-slots/get",
                "wix-safe-agent-cli bookings-time-slots-v2 get-multi-service",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/time-slots/time-slots-v2/get-multi-service-availability-time-slot",
            ),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))

        for method_id, (http_method, path, planned_command, doc_url) in expected.items():
            op = by_id[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertEqual(op.get("doc_url"), doc_url)
            self.assertIn("implemented", op["flags"])

        self.assertIn("developer-preview", by_id["bookingsTimeSlotsV2.getEventTimeSlot"]["flags"])

    def test_bookings_reader_v2_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-reader-v2", families)
        family = families["bookings-reader-v2"]

        self.assertEqual(
            family.get("source_urls"),
            [
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-reader-v2/introduction",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-reader-v2/query-extended-bookings",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-reader-v2/count-extended-bookings",
            ],
        )
        self.assertEqual(
            family.get("default_flags"),
            ["official-docs", "live-unverified"],
        )

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 2)

        expected = {
            "bookingsReaderV2.queryExtendedBookings": (
                "POST",
                "/_api/bookings-reader/v2/extended-bookings/query",
                "wix-safe-agent-cli bookings-reader-v2 query-extended-bookings",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-reader-v2/query-extended-bookings",
            ),
            "bookingsReaderV2.countExtendedBookings": (
                "POST",
                "/_api/bookings-reader/v2/extended-bookings/count",
                "wix-safe-agent-cli bookings-reader-v2 count-extended-bookings",
                "https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-reader-v2/count-extended-bookings",
            ),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))

        for method_id, (http_method, path, planned_command, doc_url) in expected.items():
            op = by_id[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertEqual(op.get("doc_url"), doc_url)
            self.assertIn("implemented", op["flags"])

    def test_bookings_services_v2_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-services-v2", families)
        family = families["bookings-services-v2"]

        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(
            family.get("default_flags"),
            ["official-docs", "live-unverified"],
        )

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 26)

        expected = {
            "bookingsServicesV2.createService": ("POST", "/_api/bookings/v2/services", "wix-safe-agent-cli bookings-services-v2 create"),
            "bookingsServicesV2.bulkCreateServices": ("POST", "/bookings/v2/bulk/services/create", "wix-safe-agent-cli bookings-services-v2 bulk-create"),
            "bookingsServicesV2.getService": ("GET", "/_api/bookings/v2/services/{serviceId}", "wix-safe-agent-cli bookings-services-v2 get"),
            "bookingsServicesV2.deleteService": ("DELETE", "/_api/bookings/v2/services/{serviceId}", "wix-safe-agent-cli bookings-services-v2 delete"),
            "bookingsServicesV2.updateService": ("PATCH", "/_api/bookings/v2/services/{serviceId}", "wix-safe-agent-cli bookings-services-v2 update"),
            "bookingsServicesV2.bulkUpdateServices": ("POST", "/bookings/v2/bulk/services/update", "wix-safe-agent-cli bookings-services-v2 bulk-update"),
            "bookingsServicesV2.bulkUpdateServicesByFilter": ("POST", "/bookings/v2/bulk/services/update-by-filter", "wix-safe-agent-cli bookings-services-v2 bulk-update-by-filter"),
            "bookingsServicesV2.bulkDeleteServices": ("POST", "/bookings/v2/bulk/services/delete", "wix-safe-agent-cli bookings-services-v2 bulk-delete"),
            "bookingsServicesV2.bulkDeleteServicesByFilter": ("POST", "/bookings/v2/bulk/services/delete-by-filter", "wix-safe-agent-cli bookings-services-v2 bulk-delete-by-filter"),
            "bookingsServicesV2.queryServices": ("POST", "/_api/bookings/v2/services/query", "wix-safe-agent-cli bookings-services-v2 query"),
            "bookingsServicesV2.searchServices": ("POST", "/_api/bookings/v2/services/search", "wix-safe-agent-cli bookings-services-v2 search"),
            "bookingsServicesV2.queryPolicies": ("POST", "/_api/bookings/v2/services/policies/query", "wix-safe-agent-cli bookings-services-v2 query-policies"),
            "bookingsServicesV2.countServices": ("POST", "/_api/bookings/v2/services/count", "wix-safe-agent-cli bookings-services-v2 count"),
            "bookingsServicesV2.queryLocations": ("POST", "/_api/bookings/v2/services/locations/query", "wix-safe-agent-cli bookings-services-v2 query-locations"),
            "bookingsServicesV2.queryCategories": ("POST", "/_api/bookings/v2/services/categories/query", "wix-safe-agent-cli bookings-services-v2 query-categories"),
            "bookingsServicesV2.setServiceLocations": ("POST", "/_api/bookings/v2/services/{serviceId}/locations", "wix-safe-agent-cli bookings-services-v2 set-service-locations"),
            "bookingsServicesV2.enablePricingPlansForService": ("POST", "/_api/bookings/v2/services/{serviceId}/pricing-plans/add", "wix-safe-agent-cli bookings-services-v2 enable-pricing-plans"),
            "bookingsServicesV2.disablePricingPlansForService": ("POST", "/_api/bookings/v2/services/{serviceId}/pricing-plans/remove", "wix-safe-agent-cli bookings-services-v2 disable-pricing-plans"),
            "bookingsServicesV2.setCustomSlug": ("POST", "/_api/bookings/v2/services/{serviceId}/slugs/custom", "wix-safe-agent-cli bookings-services-v2 set-custom-slug"),
            "bookingsServicesV2.validateSlug": ("POST", "/_api/bookings/v2/services/slugs/validate", "wix-safe-agent-cli bookings-services-v2 validate-slug"),
            "bookingsServicesV2.cloneService": ("POST", "/_api/bookings/v2/services/clone", "wix-safe-agent-cli bookings-services-v2 clone"),
            "bookingsServicesV2.createAddOnGroup": ("POST", "/_api/bookings/v2/services/add-on-groups/create", "wix-safe-agent-cli bookings-services-v2 create-add-on-group"),
            "bookingsServicesV2.deleteAddOnGroup": ("POST", "/_api/bookings/v2/services/add-on-groups/delete", "wix-safe-agent-cli bookings-services-v2 delete-add-on-group"),
            "bookingsServicesV2.listAddOnGroupsByServiceId": ("POST", "/_api/bookings/v2/services/add-on-groups/list-add-on-groups-by-service-id", "wix-safe-agent-cli bookings-services-v2 list-add-on-groups-by-service-id"),
            "bookingsServicesV2.setAddOnsForGroup": ("POST", "/_api/bookings/v2/services/add-on-groups/set-add-ons-for-group", "wix-safe-agent-cli bookings-services-v2 set-add-ons-for-group"),
            "bookingsServicesV2.updateAddOnGroup": ("POST", "/_api/bookings/v2/services/add-on-groups/update", "wix-safe-agent-cli bookings-services-v2 update-add-on-group"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))

        for method_id, (http_method, path, planned_command) in expected.items():
            op = by_id[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_bookings_resources_v2_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-resources-v2", families)
        family = families["bookings-resources-v2"]

        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/resources/resources-v2/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(
            family.get("default_flags"),
            ["official-docs", "live-unverified"],
        )

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 10)

        expected = {
            "bookingsResourcesV2.createResource": ("POST", "/bookings/v2/resources", "wix-safe-agent-cli bookings-resources-v2 create"),
            "bookingsResourcesV2.getResource": ("GET", "/bookings/v2/resources/{resourceId}", "wix-safe-agent-cli bookings-resources-v2 get"),
            "bookingsResourcesV2.updateResource": ("PATCH", "/bookings/v2/resources/{resource.id}", "wix-safe-agent-cli bookings-resources-v2 update"),
            "bookingsResourcesV2.deleteResource": ("DELETE", "/bookings/v2/resources/{resourceId}", "wix-safe-agent-cli bookings-resources-v2 delete"),
            "bookingsResourcesV2.queryResources": ("POST", "/bookings/v2/resources/query", "wix-safe-agent-cli bookings-resources-v2 query"),
            "bookingsResourcesV2.searchResources": ("POST", "/bookings/v2/resources/search", "wix-safe-agent-cli bookings-resources-v2 search"),
            "bookingsResourcesV2.countResources": ("POST", "/bookings/v2/resources/count", "wix-safe-agent-cli bookings-resources-v2 count"),
            "bookingsResourcesV2.bulkCreateResources": ("POST", "/bookings/v2/bulk/resources/create", "wix-safe-agent-cli bookings-resources-v2 bulk-create"),
            "bookingsResourcesV2.bulkDeleteResources": ("POST", "/bookings/v2/bulk/resources/delete", "wix-safe-agent-cli bookings-resources-v2 bulk-delete"),
            "bookingsResourcesV2.bulkUpdateResources": ("POST", "/bookings/v2/bulk/resources/update", "wix-safe-agent-cli bookings-resources-v2 bulk-update"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))

        for method_id, (http_method, path, planned_command) in expected.items():
            op = by_id[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_bookings_resource_types_v2_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-resource-types-v2", families)
        family = families["bookings-resource-types-v2"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/resources/resource-types-v2/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 6)
        expected = {
            "bookingsResourceTypesV2.createResourceType": ("POST", "/bookings/v2/resources/resource-types", "wix-safe-agent-cli bookings-resource-types-v2 create"),
            "bookingsResourceTypesV2.getResourceType": ("GET", "/bookings/v2/resources/resource-types/{resourceTypeId}", "wix-safe-agent-cli bookings-resource-types-v2 get"),
            "bookingsResourceTypesV2.updateResourceType": ("PATCH", "/bookings/v2/resources/resource-types/{resourceType.id}", "wix-safe-agent-cli bookings-resource-types-v2 update"),
            "bookingsResourceTypesV2.deleteResourceType": ("DELETE", "/bookings/v2/resources/resource-types/{resourceTypeId}", "wix-safe-agent-cli bookings-resource-types-v2 delete"),
            "bookingsResourceTypesV2.queryResourceTypes": ("POST", "/bookings/v2/resources/resource-types/query", "wix-safe-agent-cli bookings-resource-types-v2 query"),
            "bookingsResourceTypesV2.countResourceTypes": ("POST", "/bookings/v2/resources/resource-types/count", "wix-safe-agent-cli bookings-resource-types-v2 count"),
        }
        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            op = by_id[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertIn("implemented", op["flags"])

    def test_bookings_policies_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-policies", families)
        family = families["bookings-policies"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/policies/booking-policies/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 8)
        expected = {
            "bookingsPolicies.createBookingPolicy": ("POST", "/bookings/v1/booking-policies", "wix-safe-agent-cli bookings-policies create"),
            "bookingsPolicies.getBookingPolicy": ("GET", "/bookings/v1/booking-policies/{bookingPolicyId}", "wix-safe-agent-cli bookings-policies get"),
            "bookingsPolicies.updateBookingPolicy": ("PATCH", "/bookings/v1/booking-policies/{bookingPolicy.id}", "wix-safe-agent-cli bookings-policies update"),
            "bookingsPolicies.deleteBookingPolicy": ("DELETE", "/bookings/v1/booking-policies/{bookingPolicyId}", "wix-safe-agent-cli bookings-policies delete"),
            "bookingsPolicies.queryBookingPolicies": ("POST", "/bookings/v1/booking-policies/query", "wix-safe-agent-cli bookings-policies query"),
            "bookingsPolicies.countBookingPolicies": ("POST", "/bookings/v1/booking-policies/count", "wix-safe-agent-cli bookings-policies count"),
            "bookingsPolicies.getStrictestBookingPolicy": ("POST", "/bookings/v1/booking-policies/strictest", "wix-safe-agent-cli bookings-policies strictest"),
            "bookingsPolicies.setDefaultBookingPolicy": ("POST", "/bookings/v1/booking-policies/{bookingPolicyId}:setDefault", "wix-safe-agent-cli bookings-policies set-default"),
        }
        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            op = by_id[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertIn("implemented", op["flags"])

    def test_bookings_policy_snapshots_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-policy-snapshots", families)
        family = families["bookings-policy-snapshots"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/policies/booking-policy-snapshots/list-policy-snapshots-by-booking-ids",
            family.get("source_urls"),
        )

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        self.assertEqual(set(operations), {"bookingPolicySnapshots.listPolicySnapshotsByBookingIds"})
        snapshot_op = operations["bookingPolicySnapshots.listPolicySnapshotsByBookingIds"]
        self.assertEqual(snapshot_op.get("http_method"), "GET")
        self.assertEqual(snapshot_op.get("path"), "/_api/booking-policy-snapshots/v1/policy-snapshots")
        self.assertEqual(snapshot_op.get("planned_command"), "wix-safe-agent-cli bookings-policy-snapshots list")
        self.assertIn("implemented", snapshot_op["flags"])
        self.assertTrue(snapshot_op.get("cli_callable"))

    def test_bookings_policy_service_plugin_boundary_is_callback_only(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-policy-service-plugin", families)
        family = families["bookings-policy-service-plugin"]
        self.assertIn("service-plugin", family.get("source_kind", []))
        self.assertIn("callback-only", family.get("default_flags", []))
        self.assertIn("service-plugin", family.get("default_flags", []))
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/policies/booking-policy-service-plugin/introduction",
            family.get("source_urls"),
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/policies/booking-policy-service-plugin/sample-flows",
            family.get("source_urls"),
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/policies/booking-policy-service-plugin/list-booking-policies",
            family.get("source_urls"),
        )

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)
        plugin_op = operations[0]
        self.assertEqual(plugin_op.get("method_id"), "bookingPolicyServicePlugin.listBookingPolicies")
        self.assertIsNone(plugin_op.get("http_method"))
        self.assertIsNone(plugin_op.get("path"))
        self.assertIsNone(plugin_op.get("planned_command"))
        self.assertIn("callback-only", plugin_op["flags"])
        self.assertIn("developer-preview", plugin_op["flags"])
        self.assertIn("service-plugin", plugin_op["flags"])
        self.assertFalse(plugin_op.get("cli_callable"))

    def test_bookings_attendance_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-attendance", families)
        family = families["bookings-attendance"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/attendance/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "bookingsAttendance.getAttendance": ("GET", "/bookings/bookings-attendance/{attendanceId}", "wix-safe-agent-cli bookings-attendance get"),
            "bookingsAttendance.queryAttendance": ("POST", "/bookings/bookings-attendance/query", "wix-safe-agent-cli bookings-attendance query"),
            "bookingsAttendance.countAttendances": ("POST", "/bookings/bookings-attendance/count", "wix-safe-agent-cli bookings-attendance count"),
            "bookingsAttendance.setAttendance": ("POST", "/bookings/bookings-attendance/set", "wix-safe-agent-cli bookings-attendance set"),
            "bookingsAttendance.bulkSetAttendance": ("POST", "/bookings/v2/bulk/attendance/set", "wix-safe-agent-cli bookings-attendance bulk-set"),
            "bookingsAttendance.deleteAttendance": ("DELETE", "/bookings/bookings-attendance/{attendanceId}", "wix-safe-agent-cli bookings-attendance delete"),
            "bookingsAttendance.bulkDeleteAttendances": ("POST", "/bookings/v2/bulk/attendance/delete", "wix-safe-agent-cli bookings-attendance bulk-delete"),
        }

        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            op = operations[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(op.get("cli_callable"))
        self.assertIn("developer-preview", operations["bookingsAttendance.countAttendances"]["flags"])
        self.assertIn("member-auth-only", operations["bookingsAttendance.countAttendances"]["flags"])

    def test_bookings_waitlist_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-waitlist", families)
        family = families["bookings-waitlist"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/waitlist/api-overview",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "bookingsWaitlist.listWaitlistedEntities": ("GET", "/bookings/v1/waitlist/list", "wix-safe-agent-cli bookings-waitlist list"),
            "bookingsWaitlist.registerToWaitlist": ("POST", "/bookings/v1/waitlist/register", "wix-safe-agent-cli bookings-waitlist register"),
            "bookingsWaitlist.leaveWaitlist": ("POST", "/bookings/v1/waitlist/leave", "wix-safe-agent-cli bookings-waitlist leave"),
            "bookingsWaitlist.bookFromWaitlist": ("POST", "/bookings/v1/waitlist/enroll", "wix-safe-agent-cli bookings-waitlist book"),
        }

        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            op = operations[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), command)
            self.assertIn("implemented", op["flags"])
            self.assertIn("developer-preview", op["flags"])
            self.assertTrue(op.get("cli_callable"))

    def test_calendar_schedules_v3_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("calendar-schedules-v3", families)
        family = families["calendar-schedules-v3"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-management/calendar/schedules-v3/introduction",
            family.get("source_urls"),
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-management/calendar/wix-bookings-integration",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "calendarSchedulesV3.createSchedule": ("POST", "/calendar/v3/schedules", "wix-safe-agent-cli calendar-schedules-v3 create"),
            "calendarSchedulesV3.getSchedule": ("GET", "/calendar/v3/schedules/{scheduleId}", "wix-safe-agent-cli calendar-schedules-v3 get"),
            "calendarSchedulesV3.updateSchedule": ("PATCH", "/calendar/v3/schedules/{schedule.id}", "wix-safe-agent-cli calendar-schedules-v3 update"),
            "calendarSchedulesV3.querySchedules": ("POST", "/calendar/v3/schedules/query", "wix-safe-agent-cli calendar-schedules-v3 query"),
            "calendarSchedulesV3.cancelSchedule": ("POST", "/calendar/v3/schedules/{scheduleId}/cancel", "wix-safe-agent-cli calendar-schedules-v3 cancel"),
        }
        event_methods = {
            "calendarSchedulesV3.scheduleCreated",
            "calendarSchedulesV3.scheduleUpdated",
            "calendarSchedulesV3.scheduleCancelled",
            "calendarSchedulesV3.scheduleCloned",
        }

        self.assertTrue(set(expected).issubset(operations))
        self.assertTrue(event_methods.issubset(operations))
        for method_id, (http_method, path, command) in expected.items():
            op = operations[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(op.get("cli_callable"))

    def test_calendar_schedule_time_frames_v3_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("calendar-schedule-time-frames-v3", families)
        family = families["calendar-schedule-time-frames-v3"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-management/calendar/schedule-time-frames-v3/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "calendarScheduleTimeFramesV3.getScheduleTimeFrame": (
                "GET",
                "/calendar/v3/schedules/timeframe/{id}",
                "wix-safe-agent-cli calendar-schedule-time-frames-v3 get",
            ),
            "calendarScheduleTimeFramesV3.listScheduleTimeFrames": (
                "GET",
                "/calendar/v3/schedules/timeframe",
                "wix-safe-agent-cli calendar-schedule-time-frames-v3 list",
            ),
        }

        self.assertTrue(set(expected).issubset(operations))
        self.assertIn("calendarScheduleTimeFramesV3.scheduleTimeFrameUpdated", operations)
        self.assertIn("callback-only", operations["calendarScheduleTimeFramesV3.scheduleTimeFrameUpdated"]["flags"])
        for method_id, (http_method, path, command) in expected.items():
            op = operations[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(op.get("cli_callable"))

    def test_calendar_events_v3_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("calendar-events-v3", families)
        family = families["calendar-events-v3"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "calendarEventsV3.createEvent": ("POST", "/calendar/v3/events", "wix-safe-agent-cli calendar-events-v3 create"),
            "calendarEventsV3.getEvent": ("GET", "/calendar/v3/events/{eventId}", "wix-safe-agent-cli calendar-events-v3 get"),
            "calendarEventsV3.updateEvent": ("PATCH", "/calendar/v3/events/{event.id}", "wix-safe-agent-cli calendar-events-v3 update"),
            "calendarEventsV3.queryEvents": ("POST", "/calendar/v3/events/query", "wix-safe-agent-cli calendar-events-v3 query"),
            "calendarEventsV3.listEvents": ("GET", "/calendar/v3/events", "wix-safe-agent-cli calendar-events-v3 list"),
            "calendarEventsV3.bulkCreateEvent": ("POST", "/calendar/v3/bulk/events/create", "wix-safe-agent-cli calendar-events-v3 bulk-create"),
            "calendarEventsV3.bulkUpdateEvent": ("POST", "/calendar/v3/bulk/events/update", "wix-safe-agent-cli calendar-events-v3 bulk-update"),
            "calendarEventsV3.bulkCancelEvent": ("POST", "/calendar/v3/bulk/events/cancel", "wix-safe-agent-cli calendar-events-v3 bulk-cancel"),
            "calendarEventsV3.cancelEvent": ("POST", "/calendar/v3/events/{eventId}/cancel", "wix-safe-agent-cli calendar-events-v3 cancel"),
            "calendarEventsV3.listEventsByContactId": ("GET", "/calendar/v3/events/contactId/{contactId}", "wix-safe-agent-cli calendar-events-v3 list-by-contact"),
            "calendarEventsV3.listEventsByMemberId": ("GET", "/calendar/v3/events/memberId/{memberId}", "wix-safe-agent-cli calendar-events-v3 list-by-member"),
            "calendarEventsV3.restoreEventDefaults": ("POST", "/calendar/v3/events/{eventId}/restore-defaults", "wix-safe-agent-cli calendar-events-v3 restore-defaults"),
            "calendarEventsV3.splitRecurringEvent": ("POST", "/calendar/v3/events/{recurringEventId}/split", "wix-safe-agent-cli calendar-events-v3 split-recurring"),
        }
        callback_methods = {
            "calendarEventsV3.eventCancelled",
            "calendarEventsV3.eventCreated",
            "calendarEventsV3.eventRecurringSplit",
            "calendarEventsV3.eventUpdated",
        }

        self.assertTrue(set(expected).issubset(operations))
        self.assertTrue(callback_methods.issubset(operations))
        for method_id, (http_method, path, command) in expected.items():
            op = operations[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(op.get("cli_callable"))
        for method_id in callback_methods:
            self.assertIn("callback-only", operations[method_id]["flags"])
            self.assertFalse(operations[method_id].get("cli_callable"))
        for method_id in (
            "calendarEventsV3.bulkCancelEvent",
            "calendarEventsV3.cancelEvent",
            "calendarEventsV3.restoreEventDefaults",
            "calendarEventsV3.splitRecurringEvent",
        ):
            self.assertIn("requires-ack-irreversible", operations[method_id]["flags"])

    def test_calendar_event_views_v3_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("calendar-event-views-v3", families)
        family = families["calendar-event-views-v3"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-management/calendar/event-views-v3/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        op = operations["calendarEventViewsV3.getEventsView"]
        self.assertEqual(op.get("http_method"), "GET")
        self.assertEqual(op.get("path"), "/calendar/v3/events/view")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli calendar-event-views-v3 get")
        self.assertIn("implemented", op["flags"])
        self.assertTrue(op.get("cli_callable"))

        for method_id in (
            "calendarEventViewsV3.eventsViewExtended",
            "calendarEventViewsV3.eventsViewProjectionUpdated",
        ):
            self.assertIn(method_id, operations)
            self.assertIn("callback-only", operations[method_id]["flags"])
            self.assertFalse(operations[method_id].get("cli_callable"))

    def test_calendar_participations_v3_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("calendar-participations-v3", families)
        family = families["calendar-participations-v3"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-management/calendar/participations-v3/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "calendarParticipationsV3.createParticipation": (
                "POST",
                "/calendar/v3/participations",
                "wix-safe-agent-cli calendar-participations-v3 create",
            ),
            "calendarParticipationsV3.getParticipation": (
                "GET",
                "/calendar/v3/participations/{participationId}",
                "wix-safe-agent-cli calendar-participations-v3 get",
            ),
            "calendarParticipationsV3.updateParticipation": (
                "PATCH",
                "/calendar/v3/participations/{participation.id}",
                "wix-safe-agent-cli calendar-participations-v3 update",
            ),
            "calendarParticipationsV3.deleteParticipation": (
                "DELETE",
                "/calendar/v3/participations/{participationId}",
                "wix-safe-agent-cli calendar-participations-v3 delete",
            ),
            "calendarParticipationsV3.queryParticipations": (
                "POST",
                "/calendar/v3/participations/query",
                "wix-safe-agent-cli calendar-participations-v3 query",
            ),
        }
        callback_methods = {
            "calendarParticipationsV3.participationCreated",
            "calendarParticipationsV3.participationDeleted",
            "calendarParticipationsV3.participationUpdated",
        }

        self.assertTrue(set(expected).issubset(operations))
        self.assertTrue(callback_methods.issubset(operations))
        for method_id, (http_method, path, command) in expected.items():
            op = operations[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(op.get("cli_callable"))
        self.assertIn("requires-ack-irreversible", operations["calendarParticipationsV3.deleteParticipation"]["flags"])
        for method_id in callback_methods:
            self.assertIn("callback-only", operations[method_id]["flags"])
            self.assertFalse(operations[method_id].get("cli_callable"))

    def test_calendar_skills_default_business_hours_is_docs_only_and_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("calendar-skills-default-business-hours", families)
        family = families["calendar-skills-default-business-hours"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-management/calendar/skills/configure-default-business-hours",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("coverage_status"), "docs-only")
        self.assertIn("docs-only", family.get("default_flags", []))
        self.assertIn("non-callable", family.get("default_flags", []))

        operation = family.get("operations", [])[0]
        self.assertEqual(operation.get("method_id"), "calendarSkills.configureDefaultBusinessHoursDocs")
        self.assertIsNone(operation.get("planned_command"))
        self.assertIsNone(operation.get("http_method"))
        self.assertIsNone(operation.get("path"))
        self.assertIn("docs-only", operation.get("flags", []))
        self.assertFalse(operation.get("cli_callable"))

    def test_captcha_family_is_gated_and_non_callable_for_rest_cli(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("captcha", families)
        family = families["captcha"]
        self.assertEqual(family.get("coverage_status"), "gated")
        self.assertIn("developer-preview", family.get("default_flags", []))
        self.assertIn("rest-headless-not-supported", family.get("default_flags", []))
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-management/captcha/introduction",
            family.get("source_urls"),
        )

        operation = family.get("operations", [])[0]
        self.assertEqual(operation.get("method_id"), "captcha.authorize")
        self.assertEqual(operation.get("http_method"), "POST")
        self.assertEqual(operation.get("path"), "/captcharator/api/v1/authorize")
        self.assertIsNone(operation.get("planned_command"))
        self.assertIn("developer-preview", operation.get("flags", []))
        self.assertIn("rest-headless-not-supported", operation.get("flags", []))
        self.assertFalse(operation.get("cli_callable"))

    def test_cookie_consent_policy_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("cookie-consent-policy", families)
        family = families["cookie-consent-policy"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 18)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "cookieConsentPolicy.getCookieBannerSettings": (
                "GET",
                "/cookie-consent/v1/cookie-banner-settings",
                "wix-safe-agent-cli cookie-consent-policy get-cookie-banner-settings",
            ),
            "cookieConsentPolicy.updateCookieBannerSettings": (
                "POST",
                "/cookie-consent/v1/cookie-banner-settings/update",
                "wix-safe-agent-cli cookie-consent-policy update-cookie-banner-settings",
            ),
            "cookieConsentPolicy.getCmpConfig": (
                "GET",
                "/consent/cmp/v2/cmp-configs",
                "wix-safe-agent-cli cookie-consent-policy get-cmp-config",
            ),
            "cookieConsentPolicy.updateCmpConfig": (
                "PATCH",
                "/consent/cmp/v2/cmp-configs",
                "wix-safe-agent-cli cookie-consent-policy update-cmp-config",
            ),
            "cookieConsentPolicy.deleteConsentConfig": (
                "DELETE",
                "/consent/consent-config/v1/consent-configs/{consentConfigId}",
                "wix-safe-agent-cli cookie-consent-policy delete-consent-config",
            ),
            "cookieConsentPolicy.bulkUpdateConsentConfigTagsByFilter": (
                "POST",
                "/consent/consent-config/v1/bulk/consent-configs/update-tags-by-filter",
                "wix-safe-agent-cli cookie-consent-policy bulk-update-consent-config-tags-by-filter",
            ),
            "cookieConsentPolicy.listAppsAndStorage": (
                "POST",
                "/consent/consent-config/v1/site-apps-and-storage",
                "wix-safe-agent-cli cookie-consent-policy list-apps-and-storage",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(by_id[method_id].get("cli_callable"))

        self.assertIn("requires-ack-irreversible", by_id["cookieConsentPolicy.deleteConsentConfig"]["flags"])
        self.assertIn(
            "requires-ack-irreversible",
            by_id["cookieConsentPolicy.bulkUpdateConsentConfigTagsByFilter"]["flags"],
        )
        self.assertIn("developer-preview", by_id["cookieConsentPolicy.bulkUpdateConsentConfigs"]["flags"])
        self.assertIn("callback-only", by_id["cookieConsentPolicy.consentConfigCreated"]["flags"])
        self.assertFalse(by_id["cookieConsentPolicy.consentConfigCreated"].get("cli_callable"))

    def test_dashboard_favorite_list_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("dashboard-favorite-list", families)
        family = families["dashboard-favorite-list"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "dashboardFavoriteList.createUserFavoriteList": (
                "POST",
                "/dashboard/v1/user-favorite-list",
                "wix-safe-agent-cli dashboard-favorite-list create",
            ),
            "dashboardFavoriteList.updateUserFavoriteList": (
                "PATCH",
                "/dashboard/v1/user-favorite-list/{favoriteList.id}",
                "wix-safe-agent-cli dashboard-favorite-list update",
            ),
            "dashboardFavoriteList.deleteUserFavoriteList": (
                "DELETE",
                "/dashboard/v1/user-favorite-list/{favoriteListId}",
                "wix-safe-agent-cli dashboard-favorite-list delete",
            ),
            "dashboardFavoriteList.addUserFavorite": (
                "POST",
                "/dashboard/v1/user-favorite-list/add-favorite",
                "wix-safe-agent-cli dashboard-favorite-list add-favorite",
            ),
            "dashboardFavoriteList.deleteUserFavorite": (
                "DELETE",
                "/dashboard/v1/user-favorite-list/delete-favorite/{favoriteId}",
                "wix-safe-agent-cli dashboard-favorite-list delete-favorite",
            ),
            "dashboardFavoriteList.getUserFavoriteList": (
                "GET",
                "/dashboard/v1/user-favorite-list",
                "wix-safe-agent-cli dashboard-favorite-list get",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(by_id[method_id].get("cli_callable"))

        self.assertIn("requires-ack-irreversible", by_id["dashboardFavoriteList.deleteUserFavoriteList"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["dashboardFavoriteList.deleteUserFavorite"]["flags"])
        self.assertIn("callback-only", by_id["dashboardFavoriteList.favoriteListCreated"]["flags"])
        self.assertIn("callback-only", by_id["dashboardFavoriteList.favoriteListDeleted"]["flags"])
        self.assertIn("callback-only", by_id["dashboardFavoriteList.favoriteListUpdated"]["flags"])
        self.assertFalse(by_id["dashboardFavoriteList.favoriteListCreated"].get("cli_callable"))

    def test_bookings_external_calendars_v2_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-external-calendars-v2", families)
        family = families["bookings-external-calendars-v2"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "externalCalendarV2.listProviders": ("GET", "/bookings/v2/external-calendars/providers", "wix-safe-agent-cli bookings-external-calendars-v2 list-providers"),
            "externalCalendarV2.connectByCredentials": ("POST", "/bookings/v2/external-calendars/connections:connectByCredentials", "wix-safe-agent-cli bookings-external-calendars-v2 connect-by-credentials"),
            "externalCalendarV2.connectByOAuth": ("POST", "/bookings/v2/external-calendars/connections:connectByOAuth", "wix-safe-agent-cli bookings-external-calendars-v2 connect-by-oauth"),
            "externalCalendarV2.listConnections": ("GET", "/bookings/v2/external-calendars/connections", "wix-safe-agent-cli bookings-external-calendars-v2 list-connections"),
            "externalCalendarV2.getConnection": ("GET", "/bookings/v2/external-calendars/connections/{connectionId}", "wix-safe-agent-cli bookings-external-calendars-v2 get-connection"),
            "externalCalendarV2.updateSyncConfig": ("PATCH", "/bookings/v2/external-calendars/connections/{connectionId}/sync-config", "wix-safe-agent-cli bookings-external-calendars-v2 update-sync-config"),
            "externalCalendarV2.listCalendars": ("GET", "/bookings/v2/external-calendars/connections/{connectionId}/calendars", "wix-safe-agent-cli bookings-external-calendars-v2 list-calendars"),
            "externalCalendarV2.listEvents": ("GET", "/bookings/v2/external-calendars/events", "wix-safe-agent-cli bookings-external-calendars-v2 list-events"),
            "externalCalendarV2.disconnect": ("POST", "/bookings/v2/external-calendars/connections/{connectionId}/disconnect", "wix-safe-agent-cli bookings-external-calendars-v2 disconnect"),
        }

        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            op = operations[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(op.get("cli_callable"))
        self.assertIn("redacts-sensitive-input", operations["externalCalendarV2.connectByCredentials"]["flags"])

    def test_bookings_service_options_v1_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-service-options-v1", families)
        family = families["bookings-service-options-v1"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/service-options-and-variants/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "bookingsServiceOptionsV1.createServiceOptionsAndVariants": ("POST", "/bookings/v1/serviceOptionsAndVariants", "wix-safe-agent-cli bookings-service-options-v1 create"),
            "bookingsServiceOptionsV1.getServiceOptionsAndVariants": ("GET", "/bookings/v1/serviceOptionsAndVariants/{serviceOptionsAndVariantsId}", "wix-safe-agent-cli bookings-service-options-v1 get"),
            "bookingsServiceOptionsV1.updateServiceOptionsAndVariants": ("PATCH", "/bookings/v1/serviceOptionsAndVariants/{serviceOptionsAndVariants.id}", "wix-safe-agent-cli bookings-service-options-v1 update"),
            "bookingsServiceOptionsV1.deleteServiceOptionsAndVariants": ("DELETE", "/bookings/v1/serviceOptionsAndVariants/{serviceOptionsAndVariantsId}", "wix-safe-agent-cli bookings-service-options-v1 delete"),
            "bookingsServiceOptionsV1.queryServiceOptionsAndVariants": ("POST", "/bookings/v1/serviceOptionsAndVariants/query", "wix-safe-agent-cli bookings-service-options-v1 query"),
            "bookingsServiceOptionsV1.cloneServiceOptionsAndVariants": ("POST", "/bookings/v1/serviceOptionsAndVariants/{cloneFromId}/clone", "wix-safe-agent-cli bookings-service-options-v1 clone"),
            "bookingsServiceOptionsV1.getServiceOptionsAndVariantsByServiceId": ("GET", "/bookings/v1/serviceOptionsAndVariants/service_id/{serviceId}", "wix-safe-agent-cli bookings-service-options-v1 get-by-service-id"),
        }
        event_methods = {
            "bookingsServiceOptionsV1.serviceOptionsAndVariantsCreated",
            "bookingsServiceOptionsV1.serviceOptionsAndVariantsDeleted",
            "bookingsServiceOptionsV1.serviceOptionsAndVariantsUpdated",
        }

        self.assertTrue(set(expected).issubset(operations))
        self.assertTrue(event_methods.issubset(operations))
        for method_id, (http_method, path, command) in expected.items():
            op = operations[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(op.get("cli_callable"))
        for method_id in event_methods:
            op = operations[method_id]
            self.assertIsNone(op.get("http_method"))
            self.assertIsNone(op.get("planned_command"))
            self.assertIn("callback-only", op["flags"])
            self.assertFalse(op.get("cli_callable"))

    def test_bookings_validation_service_plugin_boundary_is_callback_only(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-validation-service-plugin", families)
        family = families["bookings-validation-service-plugin"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-validation-service-plugin/introduction",
            family.get("source_urls"),
        )
        self.assertIn("callback-only", family.get("default_flags", []))
        self.assertIn("developer-preview", family.get("default_flags", []))
        self.assertIn("service-plugin", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "bookingsValidationServicePlugin.validateBeforeCreate",
            "bookingsValidationServicePlugin.validateBeforeCancel",
            "bookingsValidationServicePlugin.validateBeforeReschedule",
            "bookingsValidationServicePlugin.validateBeforeCreateMultiService",
            "bookingsValidationServicePlugin.validateBeforeCancelMultiService",
            "bookingsValidationServicePlugin.validateBeforeRescheduleMultiService",
        }

        self.assertEqual(set(operations), expected)
        for op in operations.values():
            self.assertIsNone(op.get("http_method"))
            self.assertIsNone(op.get("path"))
            self.assertIsNone(op.get("planned_command"))
            self.assertIn("callback-only", op["flags"])
            self.assertIn("developer-preview", op["flags"])
            self.assertIn("service-plugin", op["flags"])
            self.assertFalse(op.get("cli_callable"))

    def test_bookings_staff_members_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("bookings-staff-members", families)
        family = families["bookings-staff-members"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/staff-members/introduction",
            family.get("source_urls"),
        )
        self.assertEqual(family.get("default_flags"), ["official-docs", "live-unverified"])

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 15)
        expected = {
            "bookingsStaffMembers.createStaffMember": ("POST", "/bookings/v1/staff-members", "wix-safe-agent-cli bookings-staff-members create"),
            "bookingsStaffMembers.getStaffMember": ("GET", "/bookings/v1/staff-members/{staffMemberId}", "wix-safe-agent-cli bookings-staff-members get"),
            "bookingsStaffMembers.updateStaffMember": ("PATCH", "/bookings/v1/staff-members/{staffMember.id}", "wix-safe-agent-cli bookings-staff-members update"),
            "bookingsStaffMembers.deleteStaffMember": ("DELETE", "/bookings/v1/staff-members/{staffMemberId}", "wix-safe-agent-cli bookings-staff-members delete"),
            "bookingsStaffMembers.queryStaffMembers": ("POST", "/bookings/v1/staff-members/query", "wix-safe-agent-cli bookings-staff-members query"),
            "bookingsStaffMembers.searchStaffMembers": ("POST", "/bookings/v1/staff-members/search", "wix-safe-agent-cli bookings-staff-members search"),
            "bookingsStaffMembers.countStaffMembers": ("POST", "/bookings/v1/staff-members/count", "wix-safe-agent-cli bookings-staff-members count"),
            "bookingsStaffMembers.assignWorkingHoursSchedule": (
                "POST",
                "/bookings/v1/staff-members/{staffMemberId}/assign-working-hours-schedule",
                "wix-safe-agent-cli bookings-staff-members assign-working-hours-schedule",
            ),
            "bookingsStaffMembers.bulkUpdateStaffMemberTags": ("POST", "/bookings/v1/bulk/staff-members/update-tags", "wix-safe-agent-cli bookings-staff-members bulk-update-tags"),
            "bookingsStaffMembers.bulkUpdateStaffMemberTagsByFilter": (
                "POST",
                "/bookings/v1/bulk/staff-members/update-tags-by-filter",
                "wix-safe-agent-cli bookings-staff-members bulk-update-tags-by-filter",
            ),
            "bookingsStaffMembers.connectStaffMemberToUser": (
                "POST",
                "/bookings/v1/staff-members/{staffMemberId}/connect-staff-member-to-user",
                "wix-safe-agent-cli bookings-staff-members connect-to-user",
            ),
            "bookingsStaffMembers.disconnectStaffMemberFromUser": (
                "POST",
                "/bookings/v1/staff-members/{staffMemberId}/disconnect-staff-member-from-user",
                "wix-safe-agent-cli bookings-staff-members disconnect-from-user",
            ),
            "bookingsStaffMembers.getDeletedStaffMember": (
                "GET",
                "/bookings/v2/staff-members/trash-bin/{staffMemberId}",
                "wix-safe-agent-cli bookings-staff-members get-deleted",
            ),
            "bookingsStaffMembers.listDeletedStaffMembers": (
                "GET",
                "/bookings/v2/staff-members/trash-bin",
                "wix-safe-agent-cli bookings-staff-members list-deleted",
            ),
            "bookingsStaffMembers.removeStaffMemberFromTrashBin": (
                "DELETE",
                "/bookings/v2/staff-members/trash-bin/{staffMemberId}",
                "wix-safe-agent-cli bookings-staff-members remove-from-trash",
            ),
        }
        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            op = by_id[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertIn("implemented", op["flags"])

    def test_order_billing_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("order-billing", families)
        family = families["order-billing"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 8)

        expected = {
            "orderBilling.getOrderRefundability": (
                "POST",
                "/ecom/v1/order-billing/get-order-refundability",
                "wix-safe-agent-cli order-billing get-order-refundability",
            ),
            "orderBilling.calculateRefund": (
                "POST",
                "/ecom/v1/order-billing/calculate-refund",
                "wix-safe-agent-cli order-billing calculate-refund",
            ),
            "orderBilling.authorizeChargeWithSavedPaymentMethod": (
                "POST",
                "/ecom/v1/order-billing/authorize-charge-with-saved-payment-method",
                "wix-safe-agent-cli order-billing authorize-charge-with-saved-payment-method",
            ),
            "orderBilling.captureAuthorizedPayments": (
                "POST",
                "/ecom/v1/order-billing/capture-authorized-payments",
                "wix-safe-agent-cli order-billing capture-authorized-payments",
            ),
            "orderBilling.voidAuthorizedPayments": (
                "POST",
                "/ecom/v1/order-billing/void-authorized-payments",
                "wix-safe-agent-cli order-billing void-authorized-payments",
            ),
            "orderBilling.generateReceipts": (
                "POST",
                "/ecom/v1/order-billing/generate-receipts",
                "wix-safe-agent-cli order-billing generate-receipts",
            ),
            "orderBilling.redeemGiftCard": (
                "POST",
                "/ecom/v1/order-billing/redeem-gift-card",
                "wix-safe-agent-cli order-billing redeem-gift-card",
            ),
            "orderBilling.refundPayments": (
                "POST",
                "/ecom/v1/order-billing/refund-payments",
                "wix-safe-agent-cli order-billing refund-payments",
            ),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))

        for method_id, (http_method, path, planned_command) in expected.items():
            op = by_id[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_payments_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("payments", families)
        family = families["payments"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-management/payments/cashier/payments/transaction/transactions-list",
            family["source_urls"],
        )

        op = operations[0]
        self.assertEqual(op.get("method_id"), "payments.transactionsList")
        self.assertEqual(op.get("http_method"), "GET")
        self.assertEqual(op.get("path"), "/payments/v2/transactions")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli payments transactions-list")
        self.assertEqual(
            op.get("doc_url"),
            "https://dev.wix.com/docs/api-reference/business-management/payments/cashier/payments/transaction/transactions-list",
        )
        self.assertIn("implemented", op["flags"])

    def test_gift_cards_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("gift-cards", families)
        family = families["gift-cards"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 7)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "giftCards.create": ("POST", "/gift-cards/v1/gift-cards", "wix-safe-agent-cli gift-cards create"),
            "giftCards.get": ("GET", "/gift-cards/v1/gift-cards/{giftCardId}", "wix-safe-agent-cli gift-cards get"),
            "giftCards.query": ("POST", "/gift-cards/v1/gift-cards/query", "wix-safe-agent-cli gift-cards query"),
            "giftCards.search": ("POST", "/gift-cards/v1/gift-cards/search", "wix-safe-agent-cli gift-cards search"),
            "giftCards.count": ("POST", "/gift-cards/v1/gift-cards/count", "wix-safe-agent-cli gift-cards count"),
            "giftCards.disable": (
                "POST",
                "/gift-cards/v1/gift-cards/{giftCardId}/disable",
                "wix-safe-agent-cli gift-cards disable",
            ),
            "giftCards.sendEmail": (
                "POST",
                "/gift-cards/v1/gift-cards/{giftCardId}/send-email",
                "wix-safe-agent-cli gift-cards send-email",
            ),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertIn("implemented", by_id[method_id]["flags"])
        self.assertIn("developer-preview", by_id["giftCards.count"]["flags"])

    def test_benefit_items_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("benefit-items", families)
        family = families["benefit-items"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 11)

        expected = {
            "benefitItems.get": ("GET", "/benefit-programs/v1/items/{itemId}", "wix-safe-agent-cli benefit-items get"),
            "benefitItems.list": ("GET", "/benefit-programs/v1/items", "wix-safe-agent-cli benefit-items list"),
            "benefitItems.query": (
                "POST",
                "/benefit-programs/v1/items/query",
                "wix-safe-agent-cli benefit-items query",
            ),
            "benefitItems.count": (
                "POST",
                "/benefit-programs/v1/items/count",
                "wix-safe-agent-cli benefit-items count",
            ),
            "benefitItems.create": (
                "POST",
                "/benefit-programs/v1/items",
                "wix-safe-agent-cli benefit-items create",
            ),
            "benefitItems.update": (
                "PATCH",
                "/benefit-programs/v1/items/{item.id}",
                "wix-safe-agent-cli benefit-items update",
            ),
            "benefitItems.delete": (
                "POST",
                "/benefit-programs/v1/items/{itemId}/delete",
                "wix-safe-agent-cli benefit-items delete",
            ),
            "benefitItems.bulkCreate": (
                "POST",
                "/benefit-programs/v1/bulk/items/create",
                "wix-safe-agent-cli benefit-items bulk-create",
            ),
            "benefitItems.bulkDelete": (
                "POST",
                "/benefit-programs/v1/bulk/items/delete",
                "wix-safe-agent-cli benefit-items bulk-delete",
            ),
            "benefitItems.bulkUpdate": (
                "POST",
                "/benefit-programs/v1/bulk/items/update",
                "wix-safe-agent-cli benefit-items bulk-update",
            ),
            "benefitItems.bulkDeleteByFilter": (
                "POST",
                "/benefit-programs/v1/bulk/items/delete-by-filter",
                "wix-safe-agent-cli benefit-items bulk-delete-by-filter",
            ),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertIn("implemented", by_id[method_id]["flags"])

    def test_balances_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("balances", families)
        family = families["balances"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 5)

        expected = {
            "balances.get": ("GET", "/benefit-programs/v1/balances/{poolId}", "wix-safe-agent-cli balances get"),
            "balances.list": ("GET", "/benefit-programs/v1/balances", "wix-safe-agent-cli balances list"),
            "balances.query": (
                "POST",
                "/benefit-programs/v1/balances/query",
                "wix-safe-agent-cli balances query",
            ),
            "balances.change": (
                "POST",
                "/benefit-programs/v1/balances/{poolId}/change",
                "wix-safe-agent-cli balances change",
            ),
            "balances.revertChange": (
                "POST",
                "/benefit-programs/v1/balances/changes/{transactionId}/revert",
                "wix-safe-agent-cli balances revert-change",
            ),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertIn("implemented", by_id[method_id]["flags"])

    def test_coupons_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("coupons", families)
        family = families["coupons"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 7)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "coupons.get": ("GET", "/stores/v2/coupons/{id}", "wix-safe-agent-cli coupons get"),
            "coupons.query": ("POST", "/stores/v2/coupons/query", "wix-safe-agent-cli coupons query"),
            "coupons.create": ("POST", "/stores/v2/coupons", "wix-safe-agent-cli coupons create"),
            "coupons.update": ("PATCH", "/stores/v2/coupons/{id}", "wix-safe-agent-cli coupons update"),
            "coupons.delete": ("DELETE", "/stores/v2/coupons/{id}", "wix-safe-agent-cli coupons delete"),
            "coupons.bulkCreate": (
                "POST",
                "/stores/v2/bulk/coupons/create",
                "wix-safe-agent-cli coupons bulk-create",
            ),
            "coupons.bulkDelete": (
                "POST",
                "/stores/v2/bulk/coupons/delete",
                "wix-safe-agent-cli coupons bulk-delete",
            ),
        }
        self.assertEqual(set(by_id), set(expected))
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(by_id[method_id].get("http_method"), http_method)
            self.assertEqual(by_id[method_id].get("path"), path)
            self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", by_id[method_id]["flags"])
            self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        for op in operations:
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_domain_dns_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("domain-dns", families)
        family = families["domain-dns"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 5)

        expected_commands = {
            "wix-safe-agent-cli domain-dns get-zone",
            "wix-safe-agent-cli domain-dns preview-zone",
            "wix-safe-agent-cli domain-dns create-zone",
            "wix-safe-agent-cli domain-dns update-zone",
            "wix-safe-agent-cli domain-dns delete-zone",
        }
        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(expected_commands.issubset(inventory_commands))

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_donation_campaigns_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("donation-campaigns", families)
        family = families["donation-campaigns"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)

        expected = {
            "donationCampaigns.get": (
                "GET",
                "/donation-campaigns/v2/donation-campaigns/{donationCampaignId}",
                "wix-safe-agent-cli donation-campaigns get",
            ),
            "donationCampaigns.getMetrics": (
                "GET",
                "/donation-campaigns/v2/donation-campaigns/{donationCampaignId}/metrics",
                "wix-safe-agent-cli donation-campaigns get-metrics",
            ),
            "donationCampaigns.query": (
                "POST",
                "/donation-campaigns/v2/donation-campaigns/query",
                "wix-safe-agent-cli donation-campaigns query",
            ),
            "donationCampaigns.create": (
                "POST",
                "/donation-campaigns/v2/donation-campaigns",
                "wix-safe-agent-cli donation-campaigns create",
            ),
            "donationCampaigns.update": (
                "PATCH",
                "/donation-campaigns/v2/donation-campaigns/{donationCampaign.id}",
                "wix-safe-agent-cli donation-campaigns update",
            ),
            "donationCampaigns.bulkCreate": (
                "POST",
                "/donation-campaigns/v2/bulk/donation-campaigns/create",
                "wix-safe-agent-cli donation-campaigns bulk-create",
            ),
            "donationCampaigns.bulkUpdate": (
                "POST",
                "/donation-campaigns/v2/bulk/donation-campaigns/update",
                "wix-safe-agent-cli donation-campaigns bulk-update",
            ),
            "donationCampaigns.bulkUpdateTags": (
                "POST",
                "/donation-campaigns/v2/bulk/donation-campaigns/update-tags",
                "wix-safe-agent-cli donation-campaigns bulk-update-tags",
            ),
            "donationCampaigns.bulkUpdateTagsByFilter": (
                "POST",
                "/donation-campaigns/v2/bulk/donation-campaigns/update-tags-by-filter",
                "wix-safe-agent-cli donation-campaigns bulk-update-tags-by-filter",
            ),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(by_id), set(expected))

        for method_id, (http_method, path, planned_command) in expected.items():
            op = by_id[method_id]
            self.assertEqual(op.get("http_method"), http_method)
            self.assertEqual(op.get("path"), path)
            self.assertEqual(op.get("planned_command"), planned_command)
            self.assertIn("implemented", op["flags"])
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
            self.assertIsNotNone(op.get("http_method"))
            self.assertIsNotNone(op.get("path"))

    def test_dns_propagation_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("dns-propagation", families)
        family = families["dns-propagation"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)

        op = operations[0]
        self.assertEqual(op.get("method_id"), "domains.getDnsPropagation")
        self.assertEqual(op.get("http_method"), "GET")
        self.assertEqual(op.get("path"), "/premium/domains/v1/dns-propagations/{dnsPropagationId}")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli dns-propagation get")
        self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
        self.assertIn("implemented", op["flags"])

    def test_site_search_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("site-search", families)
        family = families["site-search"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)

        op = operations[0]
        self.assertEqual(op.get("method_id"), "siteSearch.search")
        self.assertEqual(op.get("http_method"), "POST")
        self.assertEqual(op.get("path"), "/_api/site-search/v1/search")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli site-search search")
        self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))
        self.assertIn("implemented", op["flags"])

    def test_data_collections_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("cms-data-collections", families)
        family = families["cms-data-collections"]
        self.assertIn("operations", family)

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 12)

        expected_commands = {
            "wix-safe-agent-cli data-collections list",
            "wix-safe-agent-cli data-collections get",
            "wix-safe-agent-cli data-collections create",
            "wix-safe-agent-cli data-collections update",
            "wix-safe-agent-cli data-collections patch",
            "wix-safe-agent-cli data-collections delete",
            "wix-safe-agent-cli data-collections create-field",
            "wix-safe-agent-cli data-collections update-field",
            "wix-safe-agent-cli data-collections patch-field",
            "wix-safe-agent-cli data-collections delete-field",
            "wix-safe-agent-cli data-collections add-plugin",
            "wix-safe-agent-cli data-collections delete-plugin",
        }

        source_urls = set(family.get("source_urls", []))
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/data-collections/introduction",
            source_urls,
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/data-collections/create-data-collection-field",
            source_urls,
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/data-collections/delete-data-collection-plugin",
            source_urls,
        )

        method_ids = [op.get("method_id") for op in operations]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(
            expected_commands.issubset(inventory_commands),
            msg=f"Missing data collections planned commands in inventory: {sorted(expected_commands - inventory_commands)}",
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertIsNotNone(op["planned_command"])
            self.assertIsNotNone(op["http_method"])
            self.assertIsNotNone(op["path"])

    def test_data_permissions_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("cms-data-permissions", families)
        family = families["cms-data-permissions"]
        self.assertIn("operations", family)

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 6)

        expected_commands = {
            "wix-safe-agent-cli data-permissions get",
            "wix-safe-agent-cli data-permissions get-my",
            "wix-safe-agent-cli data-permissions update",
            "wix-safe-agent-cli data-permissions add-special",
            "wix-safe-agent-cli data-permissions update-special",
            "wix-safe-agent-cli data-permissions remove-special",
        }

        source_urls = set(family.get("source_urls", []))
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/data-permissions/introduction",
            source_urls,
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/data-permissions/update-special-permissions",
            source_urls,
        )

        method_ids = [op.get("method_id") for op in operations]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(
            expected_commands.issubset(inventory_commands),
            msg=f"Missing data permissions planned commands in inventory: {sorted(expected_commands - inventory_commands)}",
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertIsNotNone(op["planned_command"])
            self.assertIsNotNone(op["http_method"])
            self.assertIsNotNone(op["path"])

    def test_data_sharing_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("cms-data-sharing", families)
        family = families["cms-data-sharing"]
        self.assertIn("operations", family)

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 8)

        expected = {
            "dataSharing.createPolicy": (
                "POST",
                "/data/v1/data-collection-sharing/policies",
                "wix-safe-agent-cli data-sharing create-policy",
            ),
            "dataSharing.getPolicy": (
                "GET",
                "/data/v1/data-collection-sharing/policies/{dataSharingPolicyId}",
                "wix-safe-agent-cli data-sharing get-policy",
            ),
            "dataSharing.updatePolicy": (
                "POST",
                "/data/v1/data-collection-sharing/policies/{dataSharingPolicy.id}",
                "wix-safe-agent-cli data-sharing update-policy",
            ),
            "dataSharing.deletePolicy": (
                "DELETE",
                "/data/v1/data-collection-sharing/policies/{dataSharingPolicyId}",
                "wix-safe-agent-cli data-sharing delete-policy",
            ),
            "dataSharing.connectToSharedCollection": (
                "POST",
                "/data/v1/data-collection-sharing/connect-to-shared-collection",
                "wix-safe-agent-cli data-sharing connect",
            ),
            "dataSharing.disconnectFromSharedCollection": (
                "POST",
                "/data/v1/data-collection-sharing/disconnect-from-shared-collection",
                "wix-safe-agent-cli data-sharing disconnect",
            ),
            "dataSharing.listPolicies": (
                "GET",
                "/data/v1/data-collection-sharing/policies",
                "wix-safe-agent-cli data-sharing list-policies",
            ),
            "dataSharing.listSharedDataCollections": (
                "GET",
                "/data/v1/data-collection-sharing/shared",
                "wix-safe-agent-cli data-sharing list-shared-collections",
            ),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(set(expected), set(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_events_settings_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-settings", families)
        family = families["events-settings"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 3)

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(by_id["eventsSettings.get"].get("http_method"), "GET")
        self.assertEqual(by_id["eventsSettings.get"].get("path"), "/events/v1/settings")
        self.assertEqual(
            by_id["eventsSettings.get"].get("planned_command"),
            "wix-safe-agent-cli events-settings get",
        )
        self.assertIn("implemented", by_id["eventsSettings.get"]["flags"])

        self.assertEqual(by_id["eventsSettings.update"].get("http_method"), "PATCH")
        self.assertEqual(
            by_id["eventsSettings.update"].get("path"),
            "/events/v1/settings/{eventsSettings.id}",
        )
        self.assertEqual(
            by_id["eventsSettings.update"].get("planned_command"),
            "wix-safe-agent-cli events-settings update",
        )
        self.assertIn("implemented", by_id["eventsSettings.update"]["flags"])
        self.assertIn("developer-preview", by_id["eventsSettings.update"]["flags"])

        self.assertIsNone(by_id["eventsSettings.updated"].get("http_method"))
        self.assertIsNone(by_id["eventsSettings.updated"].get("path"))
        self.assertIsNone(by_id["eventsSettings.updated"].get("planned_command"))
        self.assertIn("callback-only", by_id["eventsSettings.updated"]["flags"])

        for op in operations:
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_portfolio_settings_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("portfolio-settings", families)
        family = families["portfolio-settings"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 3)

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(by_id["portfolioSettings.get"].get("http_method"), "GET")
        self.assertEqual(by_id["portfolioSettings.get"].get("path"), "/portfolio/v1/settings")
        self.assertEqual(
            by_id["portfolioSettings.get"].get("planned_command"),
            "wix-safe-agent-cli portfolio-settings get",
        )
        self.assertIn("implemented", by_id["portfolioSettings.get"]["flags"])
        self.assertTrue(by_id["portfolioSettings.get"].get("cli_callable"))

        self.assertEqual(by_id["portfolioSettings.update"].get("http_method"), "PATCH")
        self.assertEqual(by_id["portfolioSettings.update"].get("path"), "/portfolio/v1/settings")
        self.assertEqual(
            by_id["portfolioSettings.update"].get("planned_command"),
            "wix-safe-agent-cli portfolio-settings update",
        )
        self.assertIn("implemented", by_id["portfolioSettings.update"]["flags"])
        self.assertTrue(by_id["portfolioSettings.update"].get("cli_callable"))

        self.assertIsNone(by_id["portfolioSettings.created"].get("http_method"))
        self.assertIsNone(by_id["portfolioSettings.created"].get("path"))
        self.assertIsNone(by_id["portfolioSettings.created"].get("planned_command"))
        self.assertIn("callback-only", by_id["portfolioSettings.created"]["flags"])
        self.assertFalse(by_id["portfolioSettings.created"].get("cli_callable"))

        for op in operations:
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_portfolio_collections_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("portfolio-collections", families)
        family = families["portfolio-collections"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "portfolioCollections.create": ("POST", "/portfolio/v1/collections", "wix-safe-agent-cli portfolio-collections create"),
            "portfolioCollections.get": ("GET", "/portfolio/v1/collections/{collectionId}", "wix-safe-agent-cli portfolio-collections get"),
            "portfolioCollections.update": ("PATCH", "/portfolio/v1/collections/{collection.id}", "wix-safe-agent-cli portfolio-collections update"),
            "portfolioCollections.delete": ("DELETE", "/portfolio/v1/collections/{collectionId}", "wix-safe-agent-cli portfolio-collections delete"),
            "portfolioCollections.query": ("POST", "/portfolio/v1/collections/query", "wix-safe-agent-cli portfolio-collections query"),
            "portfolioCollections.list": ("GET", "/portfolio/v1/collections", "wix-safe-agent-cli portfolio-collections list"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id].get("cli_callable"))

        self.assertIn("requires-current-revision", by_id["portfolioCollections.update"]["flags"])
        self.assertIn("irreversible", by_id["portfolioCollections.delete"]["flags"])

        for method_id in ("portfolioCollections.created", "portfolioCollections.deleted", "portfolioCollections.updated"):
            with self.subTest(method_id=method_id):
                self.assertIsNone(by_id[method_id].get("http_method"))
                self.assertIsNone(by_id[method_id].get("path"))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertIn("callback-only", by_id[method_id]["flags"])
                self.assertFalse(by_id[method_id].get("cli_callable"))

        for op in operations:
            self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_events_v3_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-v3", families)
        family = families["events-v3"]
        operations = family.get("operations", [])
        expected = {
            "eventsV3.create": ("POST", "/events/v3/events", "wix-safe-agent-cli events-v3 create"),
            "eventsV3.get": ("GET", "/events/v3/events/{eventId}", "wix-safe-agent-cli events-v3 get"),
            "eventsV3.update": ("PATCH", "/events/v3/events/{event.id}", "wix-safe-agent-cli events-v3 update"),
            "eventsV3.delete": ("DELETE", "/events/v3/events/{eventId}", "wix-safe-agent-cli events-v3 delete"),
            "eventsV3.query": ("POST", "/events/v3/events/query", "wix-safe-agent-cli events-v3 query"),
            "eventsV3.bulkCancelByFilter": (
                "POST",
                "/events/v3/bulk/events/cancel-by-filter",
                "wix-safe-agent-cli events-v3 bulk-cancel-by-filter",
            ),
            "eventsV3.bulkDeleteByFilter": (
                "POST",
                "/events/v3/bulk/events/delete-by-filter",
                "wix-safe-agent-cli events-v3 bulk-delete-by-filter",
            ),
            "eventsV3.cancel": ("POST", "/events/v3/events/{eventId}/cancel", "wix-safe-agent-cli events-v3 cancel"),
            "eventsV3.clone": ("POST", "/events/v3/events/{eventId}/clone", "wix-safe-agent-cli events-v3 clone"),
            "eventsV3.countByStatus": ("POST", "/events/v3/events/count-by-status", "wix-safe-agent-cli events-v3 count-by-status"),
            "eventsV3.getBySlug": ("GET", "/events/v3/events/slug/{slug}", "wix-safe-agent-cli events-v3 get-by-slug"),
            "eventsV3.listByCategory": ("GET", "/events/v3/events/category/{categoryId}", "wix-safe-agent-cli events-v3 list-by-category"),
            "eventsV3.publishDraft": ("POST", "/events/v3/events/{eventId}/publish", "wix-safe-agent-cli events-v3 publish-draft"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("callback-only", by_id["eventsV3.eventCallbacks"]["flags"])
        self.assertIn("developer-preview", by_id["eventsV3.listByCategory"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsV3.delete"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsV3.cancel"]["flags"])

    def test_events_ticket_definitions_v3_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-ticket-definitions-v3", families)
        family = families["events-ticket-definitions-v3"]
        operations = family.get("operations", [])
        expected = {
            "eventsTicketDefinitionsV3.create": (
                "POST",
                "/events-ticket-definitions/v3/ticket-definitions",
                "wix-safe-agent-cli events-ticket-definitions-v3 create",
            ),
            "eventsTicketDefinitionsV3.get": (
                "GET",
                "/events-ticket-definitions/v3/ticket-definitions/{ticketDefinitionId}",
                "wix-safe-agent-cli events-ticket-definitions-v3 get",
            ),
            "eventsTicketDefinitionsV3.update": (
                "PATCH",
                "/events-ticket-definitions/v3/ticket-definitions/{ticketDefinition.id}",
                "wix-safe-agent-cli events-ticket-definitions-v3 update",
            ),
            "eventsTicketDefinitionsV3.delete": (
                "DELETE",
                "/events-ticket-definitions/v3/ticket-definitions/{ticketDefinitionId}",
                "wix-safe-agent-cli events-ticket-definitions-v3 delete",
            ),
            "eventsTicketDefinitionsV3.query": (
                "POST",
                "/events-ticket-definitions/v3/ticket-definitions/query",
                "wix-safe-agent-cli events-ticket-definitions-v3 query",
            ),
            "eventsTicketDefinitionsV3.bulkDeleteByFilter": (
                "POST",
                "/events-ticket-definitions/v3/bulk/ticket-definitions/delete-by-filter",
                "wix-safe-agent-cli events-ticket-definitions-v3 bulk-delete-by-filter",
            ),
            "eventsTicketDefinitionsV3.changeCurrency": (
                "POST",
                "/events-ticket-definitions/v3/ticket-definitions/currency",
                "wix-safe-agent-cli events-ticket-definitions-v3 change-currency",
            ),
            "eventsTicketDefinitionsV3.count": (
                "POST",
                "/events-ticket-definitions/v3/ticket-definitions/count",
                "wix-safe-agent-cli events-ticket-definitions-v3 count",
            ),
            "eventsTicketDefinitionsV3.reorder": (
                "POST",
                "/events-ticket-definitions/v3/ticket-definitions/reorder",
                "wix-safe-agent-cli events-ticket-definitions-v3 reorder",
            ),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["eventsTicketDefinitionsV3.delete"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsTicketDefinitionsV3.bulkDeleteByFilter"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsTicketDefinitionsV3.changeCurrency"]["flags"])
        self.assertIn("callback-only", by_id["eventsTicketDefinitionsV3.ticketDefinitionCreated"]["flags"])
        self.assertIn("callback-only", by_id["eventsTicketDefinitionsV3.ticketDefinitionUpdated"]["flags"])

    def test_events_categories_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-categories", families)
        family = families["events-categories"]
        operations = family.get("operations", [])
        expected = {
            "eventsCategories.create": ("POST", "/events/v1/categories", "wix-safe-agent-cli events-categories create"),
            "eventsCategories.bulkCreate": ("POST", "/events/v1/bulk/categories/create", "wix-safe-agent-cli events-categories bulk-create"),
            "eventsCategories.update": ("PATCH", "/events/v1/categories/{category.id}", "wix-safe-agent-cli events-categories update"),
            "eventsCategories.delete": ("DELETE", "/events/v1/categories/{categoryId}", "wix-safe-agent-cli events-categories delete"),
            "eventsCategories.query": ("POST", "/events/v1/categories/query", "wix-safe-agent-cli events-categories query"),
            "eventsCategories.assignEvents": ("POST", "/events/v1/categories/{categoryId}/events", "wix-safe-agent-cli events-categories assign-events"),
            "eventsCategories.unassignEvents": (
                "DELETE",
                "/events/v1/categories/{categoryId}/events?eventId={eventId}",
                "wix-safe-agent-cli events-categories unassign-events",
            ),
            "eventsCategories.bulkAssignEvents": ("POST", "/events/v1/bulk/categories/events", "wix-safe-agent-cli events-categories bulk-assign-events"),
            "eventsCategories.bulkUnassignEvents": (
                "DELETE",
                "/events/v1/bulk/categories/events?categoryId={categoryId}&eventId={eventId}",
                "wix-safe-agent-cli events-categories bulk-unassign-events",
            ),
            "eventsCategories.get": ("GET", "/events/v1/categories/{categoryId}", "wix-safe-agent-cli events-categories get"),
            "eventsCategories.reorderEvents": ("POST", "/events/v1/categories/{categoryId}/reorder", "wix-safe-agent-cli events-categories reorder-events"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["eventsCategories.delete"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsCategories.unassignEvents"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsCategories.bulkUnassignEvents"]["flags"])

    def test_events_schedule_items_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-schedule-items", families)
        family = families["events-schedule-items"]
        operations = family.get("operations", [])
        expected = {
            "eventsScheduleItems.get": ("GET", "/events/v1/schedule/{itemId}", "wix-safe-agent-cli events-schedule-items get"),
            "eventsScheduleItems.query": ("POST", "/events/v1/schedule/query", "wix-safe-agent-cli events-schedule-items query"),
            "eventsScheduleItems.add": ("POST", "/events/v1/schedule/draft", "wix-safe-agent-cli events-schedule-items add"),
            "eventsScheduleItems.createBookmark": (
                "POST",
                "/events/v1/schedule/{itemId}/bookmark",
                "wix-safe-agent-cli events-schedule-items create-bookmark",
            ),
            "eventsScheduleItems.deleteBookmark": (
                "DELETE",
                "/events/v1/schedule/{itemId}/bookmark",
                "wix-safe-agent-cli events-schedule-items delete-bookmark",
            ),
            "eventsScheduleItems.delete": ("DELETE", "/events/v1/schedule/draft/items", "wix-safe-agent-cli events-schedule-items delete"),
            "eventsScheduleItems.discardDraft": ("DELETE", "/events/v1/schedule/draft", "wix-safe-agent-cli events-schedule-items discard-draft"),
            "eventsScheduleItems.listBookmarks": (
                "GET",
                "/events/v1/schedule/bookmarks",
                "wix-safe-agent-cli events-schedule-items list-bookmarks",
            ),
            "eventsScheduleItems.list": ("GET", "/events/v1/schedule", "wix-safe-agent-cli events-schedule-items list"),
            "eventsScheduleItems.publishDraft": ("POST", "/events/v1/schedule/publish", "wix-safe-agent-cli events-schedule-items publish-draft"),
            "eventsScheduleItems.rescheduleDraft": (
                "POST",
                "/events/v1/schedule/draft/reschedule",
                "wix-safe-agent-cli events-schedule-items reschedule-draft",
            ),
            "eventsScheduleItems.update": ("PATCH", "/events/v1/schedule/draft/{itemId}", "wix-safe-agent-cli events-schedule-items update"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["eventsScheduleItems.delete"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsScheduleItems.discardDraft"]["flags"])

    def test_events_policies_v2_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-policies-v2", families)
        family = families["events-policies-v2"]
        operations = family.get("operations", [])
        expected = {
            "eventsPoliciesV2.create": ("POST", "/events-policies/v2/policies", "wix-safe-agent-cli events-policies-v2 create"),
            "eventsPoliciesV2.get": ("GET", "/events-policies/v2/policies/{policyId}", "wix-safe-agent-cli events-policies-v2 get"),
            "eventsPoliciesV2.update": ("PATCH", "/events-policies/v2/policies/{policy.id}", "wix-safe-agent-cli events-policies-v2 update"),
            "eventsPoliciesV2.delete": ("DELETE", "/events-policies/v2/policies/{policyId}", "wix-safe-agent-cli events-policies-v2 delete"),
            "eventsPoliciesV2.query": ("POST", "/events-policies/v2/policies/query", "wix-safe-agent-cli events-policies-v2 query"),
            "eventsPoliciesV2.reorder": ("POST", "/events-policies/v2/policies/reorder", "wix-safe-agent-cli events-policies-v2 reorder"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["eventsPoliciesV2.delete"]["flags"])

    def test_events_staff_members_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-staff-members", families)
        family = families["events-staff-members"]
        operations = family.get("operations", [])
        expected = {
            "eventsStaffMembers.create": ("POST", "/events/v1/staff-members", "wix-safe-agent-cli events-staff-members create"),
            "eventsStaffMembers.get": ("GET", "/events/v1/staff-members/{staffMemberId}", "wix-safe-agent-cli events-staff-members get"),
            "eventsStaffMembers.update": ("PATCH", "/events/v1/staff-members/{staffMember.id}", "wix-safe-agent-cli events-staff-members update"),
            "eventsStaffMembers.delete": ("DELETE", "/events/v1/staff-members/{staffMemberId}", "wix-safe-agent-cli events-staff-members delete"),
            "eventsStaffMembers.query": ("POST", "/events/v1/staff-members/query", "wix-safe-agent-cli events-staff-members query"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["eventsStaffMembers.delete"]["flags"])

    def test_events_guests_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-guests", families)
        family = families["events-guests"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)

        op = operations[0]
        self.assertEqual(op.get("method_id"), "eventsGuests.query")
        self.assertEqual(op.get("http_method"), "POST")
        self.assertEqual(op.get("path"), "/events/v2/guests/query")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli events-guests query")
        self.assertIn("implemented", op["flags"])
        self.assertTrue(str(op.get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_events_rsvps_v2_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-rsvps-v2", families)
        family = families["events-rsvps-v2"]
        operations = family.get("operations", [])
        expected = {
            "eventsRsvpsV2.create": ("POST", "/events/v2/rsvps", "wix-safe-agent-cli events-rsvps-v2 create"),
            "eventsRsvpsV2.get": ("GET", "/events/v2/rsvps/{rsvpId}", "wix-safe-agent-cli events-rsvps-v2 get"),
            "eventsRsvpsV2.update": ("PATCH", "/events/v2/rsvps/{rsvp.id}", "wix-safe-agent-cli events-rsvps-v2 update"),
            "eventsRsvpsV2.delete": ("DELETE", "/events/v2/rsvps/{rsvpId}", "wix-safe-agent-cli events-rsvps-v2 delete"),
            "eventsRsvpsV2.query": ("POST", "/events/v2/rsvps/query", "wix-safe-agent-cli events-rsvps-v2 query"),
            "eventsRsvpsV2.search": ("POST", "/events/v2/rsvps/search", "wix-safe-agent-cli events-rsvps-v2 search"),
            "eventsRsvpsV2.bulkUpdate": ("PATCH", "/events/v2/bulk/rsvps/update", "wix-safe-agent-cli events-rsvps-v2 bulk-update"),
            "eventsRsvpsV2.bulkDeleteByFilter": ("POST", "/events/v2/bulk/rsvps/delete-by-filter", "wix-safe-agent-cli events-rsvps-v2 bulk-delete-by-filter"),
            "eventsRsvpsV2.cancelCheckIn": ("POST", "/events/v2/rsvps/{rsvpId}/cancel-check-in", "wix-safe-agent-cli events-rsvps-v2 cancel-check-in"),
            "eventsRsvpsV2.checkIn": ("POST", "/events/v2/rsvps/{rsvpId}/check-in", "wix-safe-agent-cli events-rsvps-v2 check-in"),
            "eventsRsvpsV2.count": ("POST", "/events/v2/rsvps/count", "wix-safe-agent-cli events-rsvps-v2 count"),
            "eventsRsvpsV2.listSummary": ("GET", "/events/v2/rsvps/summaries", "wix-safe-agent-cli events-rsvps-v2 list-summary"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(len(operations), len(expected))
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["eventsRsvpsV2.delete"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsRsvpsV2.bulkDeleteByFilter"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsRsvpsV2.cancelCheckIn"]["flags"])

    def test_events_ticket_reservations_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-ticket-reservations", families)
        family = families["events-ticket-reservations"]
        operations = family.get("operations", [])
        expected = {
            "eventsTicketReservations.create": ("POST", "/events/v1/ticket-reservations", "wix-safe-agent-cli events-ticket-reservations create"),
            "eventsTicketReservations.get": ("GET", "/events/v1/ticket-reservations/{ticketReservationId}", "wix-safe-agent-cli events-ticket-reservations get"),
            "eventsTicketReservations.delete": ("DELETE", "/events/v1/ticket-reservations/{ticketReservationId}", "wix-safe-agent-cli events-ticket-reservations delete"),
            "eventsTicketReservations.bulkUpdateTags": ("POST", "/events/v1/bulk/ticket-reservations/update-tags", "wix-safe-agent-cli events-ticket-reservations bulk-update-tags"),
            "eventsTicketReservations.bulkUpdateTagsByFilter": ("POST", "/events/v1/bulk/ticket-reservations/update-tags-by-filter", "wix-safe-agent-cli events-ticket-reservations bulk-update-tags-by-filter"),
            "eventsTicketReservations.cancel": ("POST", "/events/v1/ticket-reservations/{ticketReservationId}/cancel", "wix-safe-agent-cli events-ticket-reservations cancel"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(len(operations), len(expected))
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["eventsTicketReservations.delete"]["flags"])
        self.assertIn("developer-preview", by_id["eventsTicketReservations.delete"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsTicketReservations.bulkUpdateTagsByFilter"]["flags"])
        self.assertIn("developer-preview", by_id["eventsTicketReservations.bulkUpdateTagsByFilter"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["eventsTicketReservations.cancel"]["flags"])

    def test_events_tickets_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-tickets", families)
        family = families["events-tickets"]
        operations = family.get("operations", [])
        expected = {
            "eventsTickets.get": ("GET", "/events/v1/tickets/{ticketNumber}", "wix-safe-agent-cli events-tickets get"),
            "eventsTickets.list": ("GET", "/events/v1/tickets", "wix-safe-agent-cli events-tickets list"),
            "eventsTickets.update": ("PATCH", "/events/v1/tickets/{ticketNumber}", "wix-safe-agent-cli events-tickets update"),
            "eventsTickets.bulkUpdate": ("PATCH", "/events/v1/tickets", "wix-safe-agent-cli events-tickets bulk-update"),
            "eventsTickets.checkIn": ("POST", "/events/v1/tickets/check-in", "wix-safe-agent-cli events-tickets check-in"),
            "eventsTickets.deleteCheckIn": ("DELETE", "/events/v1/tickets/check-in", "wix-safe-agent-cli events-tickets delete-check-in"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(len(operations), len(expected) + 1)
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["eventsTickets.deleteCheckIn"]["flags"])
        self.assertIn("callback-only", by_id["eventsTickets.orderUpdated"]["flags"])
        self.assertFalse(by_id["eventsTickets.orderUpdated"]["cli_callable"])

    def test_events_orders_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-orders", families)
        family = families["events-orders"]
        operations = family.get("operations", [])
        expected = {
            "eventsOrders.list": ("GET", "/events/v1/orders", "wix-safe-agent-cli events-orders list"),
            "eventsOrders.get": ("GET", "/events/v1/events/{eventId}/orders/{orderNumber}", "wix-safe-agent-cli events-orders get"),
            "eventsOrders.update": ("PATCH", "/events/v1/events/{eventId}/orders/{orderNumber}", "wix-safe-agent-cli events-orders update"),
            "eventsOrders.bulkUpdate": ("PATCH", "/events/v1/events/{eventId}/orders", "wix-safe-agent-cli events-orders bulk-update"),
            "eventsOrders.confirm": ("POST", "/events/v1/events/{eventId}/orders/confirm", "wix-safe-agent-cli events-orders confirm"),
            "eventsOrders.getSummary": ("GET", "/events/v1/orders/summary", "wix-safe-agent-cli events-orders get-summary"),
            "eventsOrders.getCheckoutOptions": ("GET", "/events/v1/checkout/options", "wix-safe-agent-cli events-orders get-checkout-options"),
            "eventsOrders.listAvailableTickets": ("GET", "/events/v1/checkout/available-tickets", "wix-safe-agent-cli events-orders list-available-tickets"),
            "eventsOrders.queryAvailableTickets": ("POST", "/events/v1/checkout/available-tickets/query", "wix-safe-agent-cli events-orders query-available-tickets"),
            "eventsOrders.createReservation": ("POST", "/events/v1/checkout/reservations", "wix-safe-agent-cli events-orders create-reservation"),
            "eventsOrders.cancelReservation": ("DELETE", "/events/v1/checkout/reservations/{id}", "wix-safe-agent-cli events-orders cancel-reservation"),
            "eventsOrders.checkout": ("POST", "/events/v1/checkout", "wix-safe-agent-cli events-orders checkout"),
            "eventsOrders.updateCheckout": ("PATCH", "/events/v1/checkout/{orderNumber}", "wix-safe-agent-cli events-orders update-checkout"),
            "eventsOrders.getInvoice": ("POST", "/events/v1/checkout/invoices/{reservationId}", "wix-safe-agent-cli events-orders get-invoice"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(len(operations), len(expected) + 7)
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        for method_id in [
            "eventsOrders.confirm",
            "eventsOrders.createReservation",
            "eventsOrders.cancelReservation",
            "eventsOrders.checkout",
        ]:
            self.assertIn("requires-ack-irreversible", by_id[method_id]["flags"])
        self.assertIn("deprecated", by_id["eventsOrders.createReservation"]["flags"])
        self.assertIn("deprecated", by_id["eventsOrders.cancelReservation"]["flags"])
        self.assertIn("callback-only", by_id["eventsOrders.orderPaid"]["flags"])
        self.assertFalse(by_id["eventsOrders.orderPaid"]["cli_callable"])
        self.assertIn("deprecated", by_id["eventsOrders.reservationCreated"]["flags"])
        self.assertFalse(by_id["eventsOrders.reservationCreated"]["cli_callable"])

    def test_events_forms_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("events-forms", families)
        family = families["events-forms"]
        operations = family.get("operations", [])
        expected = {
            "eventsForms.getForm": ("GET", "/events/v1/events/{eventId}/form", "wix-safe-agent-cli events-forms get-form"),
            "eventsForms.discardDraft": ("DELETE", "/events/v1/events/{eventId}/form", "wix-safe-agent-cli events-forms discard-draft"),
            "eventsForms.addControl": ("POST", "/events/v1/events/{eventId}/form/control", "wix-safe-agent-cli events-forms add-control"),
            "eventsForms.updateControl": ("PUT", "/events/v1/events/{eventId}/form/controls/{id}", "wix-safe-agent-cli events-forms update-control"),
            "eventsForms.deleteControl": ("DELETE", "/events/v1/events/{eventId}/form/controls/{id}", "wix-safe-agent-cli events-forms delete-control"),
            "eventsForms.updateMessages": ("PATCH", "/events/v1/events/{eventId}/form/messages", "wix-safe-agent-cli events-forms update-messages"),
            "eventsForms.publishDraft": ("POST", "/events/v1/events/{eventId}/form/publish", "wix-safe-agent-cli events-forms publish-draft"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(len(operations), len(expected) + 1)
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        for method_id in [
            "eventsForms.discardDraft",
            "eventsForms.deleteControl",
            "eventsForms.updateMessages",
            "eventsForms.publishDraft",
        ]:
            self.assertIn("requires-ack-irreversible", by_id[method_id]["flags"])
        self.assertIn("deprecated", by_id["eventsForms.discardDraft"]["flags"])
        self.assertIn("deprecated", by_id["eventsForms.publishDraft"]["flags"])
        self.assertIn("callback-only", by_id["eventsForms.formEventUpdated"]["flags"])
        self.assertFalse(by_id["eventsForms.formEventUpdated"]["cli_callable"])

    def test_restaurants_menus_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("restaurants-menus", families)
        family = families["restaurants-menus"]
        operations = family.get("operations", [])
        expected = {
            "menus.createMenu": ("POST", "/restaurants/menus-menu/v1/menus", "wix-safe-agent-cli restaurants-menus create"),
            "menus.getMenu": ("GET", "/restaurants/menus-menu/v1/menus/{menuId}", "wix-safe-agent-cli restaurants-menus get"),
            "menus.updateMenu": ("PATCH", "/restaurants/menus-menu/v1/menus/{menu.id}", "wix-safe-agent-cli restaurants-menus update"),
            "menus.deleteMenu": ("DELETE", "/restaurants/menus-menu/v1/menus/{menuId}", "wix-safe-agent-cli restaurants-menus delete"),
            "menus.queryMenus": ("POST", "/restaurants/menus-menu/v1/menus/query", "wix-safe-agent-cli restaurants-menus query"),
            "menus.listMenus": ("GET", "/restaurants/menus-menu/v1/menus", "wix-safe-agent-cli restaurants-menus list"),
            "menus.bulkCreateMenus": ("POST", "/restaurants/menus-menu/v1/bulk/menus/create", "wix-safe-agent-cli restaurants-menus bulk-create"),
            "menus.bulkUpdateMenu": ("POST", "/restaurants/menus-menu/v1/bulk/menus/update", "wix-safe-agent-cli restaurants-menus bulk-update"),
            "menus.duplicateMenu": ("POST", "/restaurants/menus-menu/v1/menus/{id}/duplicate", "wix-safe-agent-cli restaurants-menus duplicate"),
            "menus.updateExtendedFields": ("POST", "/restaurants/menus-menu/v1/menus/{id}/updateExtendedFields", "wix-safe-agent-cli restaurants-menus update-extended-fields"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(len(operations), len(expected) + 3)
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["menus.deleteMenu"]["flags"])
        for method_id in ["menus.menuCreated", "menus.menuUpdated", "menus.menuDeleted"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_sections_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("restaurants-sections", families)
        family = families["restaurants-sections"]
        operations = family.get("operations", [])
        expected = {
            "sections.createSection": ("POST", "/restaurants/menus-section/v1/sections", "wix-safe-agent-cli restaurants-sections create"),
            "sections.getSection": ("GET", "/restaurants/menus-section/v1/sections/{sectionId}", "wix-safe-agent-cli restaurants-sections get"),
            "sections.updateSection": ("PATCH", "/restaurants/menus-section/v1/sections/{section.id}", "wix-safe-agent-cli restaurants-sections update"),
            "sections.deleteSection": ("DELETE", "/restaurants/menus-section/v1/sections/{sectionId}", "wix-safe-agent-cli restaurants-sections delete"),
            "sections.querySections": ("POST", "/restaurants/menus-section/v1/sections/query", "wix-safe-agent-cli restaurants-sections query"),
            "sections.listSections": ("GET", "/restaurants/menus-section/v1/sections", "wix-safe-agent-cli restaurants-sections list"),
            "sections.bulkCreateSections": ("POST", "/restaurants/menus-section/v1/bulk/sections/create", "wix-safe-agent-cli restaurants-sections bulk-create"),
            "sections.bulkDeleteSections": ("DELETE", "/restaurants/menus-section/v1/bulk/sections/delete", "wix-safe-agent-cli restaurants-sections bulk-delete"),
            "sections.bulkUpdateSection": ("POST", "/restaurants/menus-section/v1/bulk/sections/update", "wix-safe-agent-cli restaurants-sections bulk-update"),
            "sections.duplicateSection": ("POST", "/restaurants/menus-section/v1/sections/{id}/duplicate", "wix-safe-agent-cli restaurants-sections duplicate"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(len(operations), len(expected) + 3)
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["sections.deleteSection"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["sections.bulkDeleteSections"]["flags"])
        for method_id in ["sections.sectionCreated", "sections.sectionUpdated", "sections.sectionDeleted"]:
            self.assertIsNone(by_id[method_id].get("http_method"))
            self.assertIsNone(by_id[method_id].get("path"))
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_items_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("restaurants-items", families)
        family = families["restaurants-items"]
        operations = family.get("operations", [])
        expected = {
            "items.createItem": ("POST", "/restaurants/menus-item/v1/items", "wix-safe-agent-cli restaurants-items create"),
            "items.getItem": ("GET", "/restaurants/menus-item/v1/items/{itemId}", "wix-safe-agent-cli restaurants-items get"),
            "items.updateItem": ("PATCH", "/restaurants/menus-item/v1/items/{item.id}", "wix-safe-agent-cli restaurants-items update"),
            "items.deleteItem": ("DELETE", "/restaurants/menus-item/v1/items/{itemId}", "wix-safe-agent-cli restaurants-items delete"),
            "items.queryItems": ("POST", "/restaurants/menus-item/v1/items/query", "wix-safe-agent-cli restaurants-items query"),
            "items.listItems": ("GET", "/restaurants/menus-item/v1/items", "wix-safe-agent-cli restaurants-items list"),
            "items.searchItems": ("POST", "/restaurants/menus-item/v1/items/search", "wix-safe-agent-cli restaurants-items search"),
            "items.countItems": ("POST", "/restaurants/menus-item/v1/items/count", "wix-safe-agent-cli restaurants-items count"),
            "items.bulkCreateItems": ("POST", "/restaurants/menus-item/v1/bulk/items/create", "wix-safe-agent-cli restaurants-items bulk-create"),
            "items.bulkDeleteItems": ("DELETE", "/restaurants/menus-item/v1/bulk/items/delete", "wix-safe-agent-cli restaurants-items bulk-delete"),
            "items.bulkUpdateItem": ("POST", "/restaurants/menus-item/v1/bulk/items/update", "wix-safe-agent-cli restaurants-items bulk-update"),
        }

        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(len(operations), len(expected) + 3)
        self.assertTrue(set(expected).issubset(by_id))
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["items.deleteItem"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["items.bulkDeleteItems"]["flags"])
        for method_id in ["items.itemCreated", "items.itemUpdated", "items.itemDeleted"]:
            self.assertIsNone(by_id[method_id].get("http_method"))
            self.assertIsNone(by_id[method_id].get("path"))
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_item_labels_inventory_matches_commands(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-item-labels"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {op["method_id"]: op for op in family["operations"]}
        expected = {
            "itemLabels.createLabel": ("POST", "/restaurants/item-labels/v1/labels", "wix-safe-agent-cli restaurants-item-labels create"),
            "itemLabels.getLabel": ("GET", "/restaurants/item-labels/v1/labels/{labelId}", "wix-safe-agent-cli restaurants-item-labels get"),
            "itemLabels.updateLabel": ("PATCH", "/restaurants/item-labels/v1/labels/{label.id}", "wix-safe-agent-cli restaurants-item-labels update"),
            "itemLabels.deleteLabel": ("DELETE", "/restaurants/item-labels/v1/labels/{labelId}", "wix-safe-agent-cli restaurants-item-labels delete"),
            "itemLabels.queryLabels": ("POST", "/restaurants/item-labels/v1/labels/query", "wix-safe-agent-cli restaurants-item-labels query"),
            "itemLabels.listLabels": ("GET", "/restaurants/item-labels/v1/labels", "wix-safe-agent-cli restaurants-item-labels list"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["itemLabels.deleteLabel"]["flags"])
        for method_id in ["itemLabels.itemLabelCreated", "itemLabels.itemLabelUpdated", "itemLabels.itemLabelDeleted"]:
            self.assertIsNone(by_id[method_id].get("http_method"))
            self.assertIsNone(by_id[method_id].get("path"))
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertIn("developer-preview", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_item_variants_inventory_matches_commands(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-item-variants"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {op["method_id"]: op for op in family["operations"]}
        expected = {
            "itemVariants.createVariant": ("POST", "/restaurants/item-variants/v1/variants", "wix-safe-agent-cli restaurants-item-variants create"),
            "itemVariants.getVariant": ("GET", "/restaurants/item-variants/v1/variants/{variantId}", "wix-safe-agent-cli restaurants-item-variants get"),
            "itemVariants.updateVariant": ("PATCH", "/restaurants/item-variants/v1/variants/{variant.id}", "wix-safe-agent-cli restaurants-item-variants update"),
            "itemVariants.deleteVariant": ("DELETE", "/restaurants/item-variants/v1/variants/{variantId}", "wix-safe-agent-cli restaurants-item-variants delete"),
            "itemVariants.queryVariants": ("POST", "/restaurants/item-variants/v1/variants/query", "wix-safe-agent-cli restaurants-item-variants query"),
            "itemVariants.listVariants": ("GET", "/restaurants/item-variants/v1/variants", "wix-safe-agent-cli restaurants-item-variants list"),
            "itemVariants.countVariants": ("POST", "/restaurants/item-variants/v1/variants/count", "wix-safe-agent-cli restaurants-item-variants count"),
            "itemVariants.bulkCreateVariants": ("POST", "/restaurants/item-variants/v1/bulk/variants/create", "wix-safe-agent-cli restaurants-item-variants bulk-create"),
            "itemVariants.bulkDeleteVariants": ("DELETE", "/restaurants/item-variants/v1/bulk/variants/delete", "wix-safe-agent-cli restaurants-item-variants bulk-delete"),
            "itemVariants.bulkUpdateVariants": ("POST", "/restaurants/item-variants/v1/bulk/variants/update", "wix-safe-agent-cli restaurants-item-variants bulk-update"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["itemVariants.deleteVariant"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["itemVariants.bulkDeleteVariants"]["flags"])
        for method_id in ["itemVariants.itemVariantCreated", "itemVariants.itemVariantUpdated", "itemVariants.itemVariantDeleted"]:
            self.assertIsNone(by_id[method_id].get("http_method"))
            self.assertIsNone(by_id[method_id].get("path"))
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertIn("developer-preview", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_item_modifiers_inventory_matches_commands(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-item-modifiers"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {op["method_id"]: op for op in family["operations"]}
        expected = {
            "itemModifiers.createModifier": ("POST", "/restaurants/item-modifiers/v1/modifiers", "wix-safe-agent-cli restaurants-item-modifiers create"),
            "itemModifiers.getModifier": ("GET", "/restaurants/item-modifiers/v1/modifiers/{modifierId}", "wix-safe-agent-cli restaurants-item-modifiers get"),
            "itemModifiers.updateModifier": ("PATCH", "/restaurants/item-modifiers/v1/modifiers/{modifier.id}", "wix-safe-agent-cli restaurants-item-modifiers update"),
            "itemModifiers.deleteModifier": ("DELETE", "/restaurants/item-modifiers/v1/modifiers/{modifierId}", "wix-safe-agent-cli restaurants-item-modifiers delete"),
            "itemModifiers.queryModifiers": ("POST", "/restaurants/item-modifiers/v1/modifiers/query", "wix-safe-agent-cli restaurants-item-modifiers query"),
            "itemModifiers.listModifiers": ("GET", "/restaurants/item-modifiers/v1/modifiers", "wix-safe-agent-cli restaurants-item-modifiers list"),
            "itemModifiers.countModifiers": ("POST", "/restaurants/item-modifiers/v1/modifiers/count", "wix-safe-agent-cli restaurants-item-modifiers count"),
            "itemModifiers.bulkCreateModifiers": ("POST", "/restaurants/item-modifiers/v1/bulk/modifiers/create", "wix-safe-agent-cli restaurants-item-modifiers bulk-create"),
            "itemModifiers.bulkDeleteModifiers": ("DELETE", "/restaurants/item-modifiers/v1/bulk/modifiers/delete", "wix-safe-agent-cli restaurants-item-modifiers bulk-delete"),
            "itemModifiers.bulkUpdateModifiers": ("POST", "/restaurants/item-modifiers/v1/bulk/modifiers/update", "wix-safe-agent-cli restaurants-item-modifiers bulk-update"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["itemModifiers.deleteModifier"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["itemModifiers.bulkDeleteModifiers"]["flags"])
        for method_id in ["itemModifiers.itemModifierCreated", "itemModifiers.itemModifierUpdated", "itemModifiers.itemModifierDeleted"]:
            self.assertIsNone(by_id[method_id].get("http_method"))
            self.assertIsNone(by_id[method_id].get("path"))
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertIn("developer-preview", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_item_modifier_groups_inventory_matches_commands(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-item-modifier-groups"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {op["method_id"]: op for op in family["operations"]}
        expected = {
            "itemModifierGroups.createModifierGroup": ("POST", "/restaurants/item-modifier-group/v1/modifier-groups", "wix-safe-agent-cli restaurants-item-modifier-groups create"),
            "itemModifierGroups.getModifierGroup": ("GET", "/restaurants/item-modifier-group/v1/modifier-groups/{modifierGroupId}", "wix-safe-agent-cli restaurants-item-modifier-groups get"),
            "itemModifierGroups.updateModifierGroup": ("PATCH", "/restaurants/item-modifier-group/v1/modifier-groups/{modifierGroup.id}", "wix-safe-agent-cli restaurants-item-modifier-groups update"),
            "itemModifierGroups.deleteModifierGroup": ("DELETE", "/restaurants/item-modifier-group/v1/modifier-groups/{modifierGroupId}", "wix-safe-agent-cli restaurants-item-modifier-groups delete"),
            "itemModifierGroups.queryModifierGroups": ("POST", "/restaurants/item-modifier-group/v1/modifier-groups/query", "wix-safe-agent-cli restaurants-item-modifier-groups query"),
            "itemModifierGroups.listModifierGroups": ("GET", "/restaurants/item-modifier-group/v1/modifier-groups", "wix-safe-agent-cli restaurants-item-modifier-groups list"),
            "itemModifierGroups.countModifierGroups": ("POST", "/restaurants/item-modifier-group/v1/modifier-groups/count", "wix-safe-agent-cli restaurants-item-modifier-groups count"),
            "itemModifierGroups.bulkCreateModifierGroups": ("POST", "/restaurants/item-modifier-group/v1/bulk/modifier-groups/create", "wix-safe-agent-cli restaurants-item-modifier-groups bulk-create"),
            "itemModifierGroups.bulkUpdateModifierGroups": ("POST", "/restaurants/item-modifier-group/v1/bulk/modifiers-groups/update", "wix-safe-agent-cli restaurants-item-modifier-groups bulk-update"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-ack-irreversible", by_id["itemModifierGroups.deleteModifierGroup"]["flags"])
        for method_id in [
            "itemModifierGroups.itemModifierGroupCreated",
            "itemModifierGroups.itemModifierGroupUpdated",
            "itemModifierGroups.itemModifierGroupDeleted",
        ]:
            self.assertIsNone(by_id[method_id].get("http_method"))
            self.assertIsNone(by_id[method_id].get("path"))
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertIn("developer-preview", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_online_order_operation_groups_inventory_methods_are_explicit(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-online-order-operation-groups"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertNotIn("partial-family-inventory", family.get("default_flags", []))
        by_id = {operation["method_id"]: operation for operation in family["operations"]}

        expected = {
            "operationGroups.createOperationGroup": ("POST", "/restaurants/v1/operation-groups", "wix-safe-agent-cli restaurants-online-order-operation-groups create"),
            "operationGroups.getOperationGroup": ("GET", "/restaurants/v1/operation-groups/{operationGroupId}", "wix-safe-agent-cli restaurants-online-order-operation-groups get"),
            "operationGroups.updateOperationGroup": ("PATCH", "/restaurants/v1/operation-groups/{operationGroup.id}", "wix-safe-agent-cli restaurants-online-order-operation-groups update"),
            "operationGroups.deleteOperationGroup": ("DELETE", "/restaurants/v1/operation-groups/{operationGroupId}", "wix-safe-agent-cli restaurants-online-order-operation-groups delete"),
            "operationGroups.queryOperationGroups": ("POST", "/restaurants/v1/operation-groups/query", "wix-safe-agent-cli restaurants-online-order-operation-groups query"),
            "operationGroups.bulkCreateOperationGroups": ("POST", "/restaurants/v1/bulk/operation-groups/create", "wix-safe-agent-cli restaurants-online-order-operation-groups bulk-create"),
            "operationGroups.bulkDeleteOperationGroups": ("POST", "/restaurants/v1/bulk/operation-groups/delete", "wix-safe-agent-cli restaurants-online-order-operation-groups bulk-delete"),
            "operationGroups.bulkUpdateOperationGroups": ("POST", "/restaurants/v1/bulk/operation-groups/update", "wix-safe-agent-cli restaurants-online-order-operation-groups bulk-update"),
            "operationGroups.bulkUpdateOperationGroupTags": ("POST", "/restaurants/v1/bulk/operation-groups/update-tags", "wix-safe-agent-cli restaurants-online-order-operation-groups bulk-update-tags"),
            "operationGroups.bulkUpdateOperationGroupTagsByFilter": ("POST", "/restaurants/v1/bulk/operation-groups/update-tags-by-filter", "wix-safe-agent-cli restaurants-online-order-operation-groups bulk-update-tags-by-filter"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        for method_id in [
            "operationGroups.deleteOperationGroup",
            "operationGroups.bulkDeleteOperationGroups",
            "operationGroups.bulkUpdateOperationGroupTagsByFilter",
        ]:
            self.assertIn("requires-ack-irreversible", by_id[method_id]["flags"])
        for method_id in [
            "operationGroups.operationGroupCreated",
            "operationGroups.operationGroupUpdated",
            "operationGroups.operationGroupDeleted",
        ]:
            self.assertIsNone(by_id[method_id].get("http_method"))
            self.assertIsNone(by_id[method_id].get("path"))
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_online_order_operations_inventory_methods_are_explicit(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-online-order-operations"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertNotIn("partial-family-inventory", family.get("default_flags", []))
        by_id = {operation["method_id"]: operation for operation in family["operations"]}

        expected = {
            "operations.getOperation": ("GET", "/restaurants-operations/v1/operations/{operationId}", "wix-safe-agent-cli restaurants-online-order-operations get"),
            "operations.listOperations": ("GET", "/restaurants-operations/v1/operations", "wix-safe-agent-cli restaurants-online-order-operations list"),
            "operations.queryOperation": ("POST", "/restaurants-operations/v1/operations/query", "wix-safe-agent-cli restaurants-online-order-operations query"),
            "operations.calculateFirstAvailableTimeSlotPerFulfillmentType": ("GET", "/restaurants-operations/v1/operations/{operationId}/first-available-time-slot-per-fulfillment-type", "wix-safe-agent-cli restaurants-online-order-operations first-available-time-slot-per-fulfillment-type"),
            "operations.calculateFirstAvailableTimeSlotsPerOperation": ("POST", "/restaurants-operations/v1/operations/first-available-time-slots-per-operations", "wix-safe-agent-cli restaurants-online-order-operations first-available-time-slots-per-operation"),
            "operations.calculateFirstAvailableTimeSlotsPerMenu": ("GET", "/restaurants-operations/v1/operations/{operationId}/first-available-time-slots-per-menus", "wix-safe-agent-cli restaurants-online-order-operations first-available-time-slots-per-menu"),
            "operations.calculateAvailableTimeSlotsForDate": ("GET", "/restaurants-operations/v1/operations/{operationId}/available-time-slots-per-date", "wix-safe-agent-cli restaurants-online-order-operations available-time-slots-for-date"),
            "operations.calculateAvailableDatesInRange": ("GET", "/restaurants-operations/v1/operations/{operationId}/available-dates", "wix-safe-agent-cli restaurants-online-order-operations available-dates-in-range"),
            "operations.validateOperationAddress": ("GET", "/restaurants-operations/v1/operations/{operationId}/validate-address", "wix-safe-agent-cli restaurants-online-order-operations validate-address"),
            "operations.updateOperation": ("PATCH", "/restaurants-operations/v1/operations/{operation.id}", "wix-safe-agent-cli restaurants-online-order-operations update"),
            "operations.deleteOperation": ("DELETE", "/restaurants-operations/v1/operations/{operationId}", "wix-safe-agent-cli restaurants-online-order-operations delete"),
            "operations.bulkUpdateOperationTags": ("POST", "/restaurants-operations/v1/bulk/operations/update-tags", "wix-safe-agent-cli restaurants-online-order-operations bulk-update-tags"),
            "operations.bulkUpdateOperationTagsByFilter": ("POST", "/restaurants-operations/v1/bulk/operations/update-tags-by-filter", "wix-safe-agent-cli restaurants-online-order-operations bulk-update-tags-by-filter"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-current-revision", by_id["operations.updateOperation"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["operations.deleteOperation"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["operations.bulkUpdateOperationTagsByFilter"]["flags"])

    def test_restaurants_online_order_menu_ordering_settings_inventory_methods_are_explicit(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-online-order-menu-ordering-settings"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertNotIn("partial-family-inventory", family.get("default_flags", []))
        by_id = {operation["method_id"]: operation for operation in family["operations"]}

        expected = {
            "menuOrderingSettings.getMenuOrderingSettings": ("GET", "/menu-ordering-settings/v1/menu-ordering-settings/{menuOrderingSettingsId}", "wix-safe-agent-cli restaurants-online-order-menu-ordering-settings get"),
            "menuOrderingSettings.updateMenuOrderingSettings": ("PATCH", "/menu-ordering-settings/v1/menu-ordering-settings/{menuOrderingSettings.id}", "wix-safe-agent-cli restaurants-online-order-menu-ordering-settings update"),
            "menuOrderingSettings.queryMenuOrderingSettings": ("POST", "/menu-ordering-settings/v1/menu-ordering-settings/query", "wix-safe-agent-cli restaurants-online-order-menu-ordering-settings query"),
            "menuOrderingSettings.listMenusAvailabilityStatus": ("GET", "/menu-ordering-settings/v1/menu-ordering-settings/menus-availability-status", "wix-safe-agent-cli restaurants-online-order-menu-ordering-settings list-menus-availability-status"),
            "menuOrderingSettings.bulkUpdateMenuOrderingSettings": ("POST", "/menu-ordering-settings/v1/bulk/menu-ordering-settings/update", "wix-safe-agent-cli restaurants-online-order-menu-ordering-settings bulk-update"),
            "menuOrderingSettings.bulkUpdateMenuOrderingSettingsTags": ("POST", "/menu-ordering-settings/v1/bulk/menu-ordering-settings/update-tags", "wix-safe-agent-cli restaurants-online-order-menu-ordering-settings bulk-update-tags"),
            "menuOrderingSettings.bulkUpdateMenuOrderingSettingsTagsByFilter": ("POST", "/menu-ordering-settings/v1/bulk/menu-ordering-settings/update-tags-by-filter", "wix-safe-agent-cli restaurants-online-order-menu-ordering-settings bulk-update-tags-by-filter"),
            "menuOrderingSettings.updateExtendedFields": ("POST", "/menu-ordering-settings/v1/menu-ordering-settings/{id}/update-extended-fields", "wix-safe-agent-cli restaurants-online-order-menu-ordering-settings update-extended-fields"),
            "menuOrderingSettings.upsertMenuOrderingSettingsByMenuId": ("POST", "/menu-ordering-settings/v1/menu-ordering-settings/upsert/menu-id/{menuOrderingSettings.menuId}", "wix-safe-agent-cli restaurants-online-order-menu-ordering-settings upsert-by-menu-id"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-current-revision", by_id["menuOrderingSettings.updateMenuOrderingSettings"]["flags"])
        self.assertIn("requires-current-revision", by_id["menuOrderingSettings.bulkUpdateMenuOrderingSettings"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["menuOrderingSettings.bulkUpdateMenuOrderingSettingsTagsByFilter"]["flags"])
        for method_id in [
            "menuOrderingSettings.menuOrderingSettingsCreated",
            "menuOrderingSettings.menuOrderingSettingsDeleted",
            "menuOrderingSettings.menuOrderingSettingsUpdated",
        ]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_online_order_fulfillment_methods_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-online-order-fulfillment-methods"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "fulfillmentMethods.listFulfillmentMethods": ("GET", "/fulfillment-methods/v1/fulfillment-methods", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods list"),
            "fulfillmentMethods.createFulfillmentMethod": ("POST", "/fulfillment-methods/v1/fulfillment-methods", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods create"),
            "fulfillmentMethods.bulkCreateFulfillmentMethods": ("POST", "/fulfillment-methods/v1/bulk/fulfillment-methods/create", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods bulk-create"),
            "fulfillmentMethods.getFulfillmentMethod": ("GET", "/fulfillment-methods/v1/fulfillment-methods/{fulfillmentMethodId}", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods get"),
            "fulfillmentMethods.deleteFulfillmentMethod": ("DELETE", "/fulfillment-methods/v1/fulfillment-methods/{fulfillmentMethodId}", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods delete"),
            "fulfillmentMethods.updateFulfillmentMethod": ("PATCH", "/fulfillment-methods/v1/fulfillment-methods/{fulfillmentMethod.id}", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods update"),
            "fulfillmentMethods.queryFulfillmentMethods": ("POST", "/fulfillment-methods/v1/fulfillment-methods/query", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods query"),
            "fulfillmentMethods.listAvailableFulfillmentMethodsForAddress": ("POST", "/fulfillment-methods/v1/fulfillment-methods/available-for-address", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods list-available-for-address"),
            "fulfillmentMethods.getAccumulatedFulfillmentMethodsAvailability": ("GET", "/fulfillment-methods/v1/fulfillment-methods/accumulated-availability", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods get-accumulated-availability"),
            "fulfillmentMethods.getCombinedMethodAvailability": ("GET", "/fulfillment-methods/v1/fulfillment-methods/combined-availability", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods get-combined-availability"),
            "fulfillmentMethods.getAggregatedMethodAvailability": ("POST", "/fulfillment-methods/v1/fulfillment-methods/aggregated-availability", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods get-aggregated-availability"),
            "fulfillmentMethods.bulkUpdateFulfillmentMethodTags": ("POST", "/fulfillment-methods/v1/bulk/fulfillment-methods/update-tags", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods bulk-update-tags"),
            "fulfillmentMethods.bulkUpdateFulfillmentMethodTagsByFilter": ("POST", "/fulfillment-methods/v1/bulk/fulfillment-methods/update-tags-by-filter", "wix-safe-agent-cli restaurants-online-order-fulfillment-methods bulk-update-tags-by-filter"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-current-revision", by_id["fulfillmentMethods.updateFulfillmentMethod"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["fulfillmentMethods.deleteFulfillmentMethod"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["fulfillmentMethods.bulkUpdateFulfillmentMethodTagsByFilter"]["flags"])
        self.assertIn("deprecated", by_id["fulfillmentMethods.getAccumulatedFulfillmentMethodsAvailability"]["flags"])
        self.assertIn("deprecated", by_id["fulfillmentMethods.getCombinedMethodAvailability"]["flags"])
        for method_id in [
            "fulfillmentMethods.fulfillmentMethodCreated",
            "fulfillmentMethods.fulfillmentMethodDeleted",
            "fulfillmentMethods.fulfillmentMethodUpdated",
        ]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_online_order_availability_exceptions_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-online-order-availability-exceptions"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "availabilityExceptions.createAvailabilityException": ("POST", "/restaurants-availability-exceptions/v1/availability-exceptions", "wix-safe-agent-cli restaurants-online-order-availability-exceptions create"),
            "availabilityExceptions.getAvailabilityException": ("GET", "/restaurants-availability-exceptions/v1/availability-exceptions/{availabilityExceptionId}", "wix-safe-agent-cli restaurants-online-order-availability-exceptions get"),
            "availabilityExceptions.deleteAvailabilityException": ("DELETE", "/restaurants-availability-exceptions/v1/availability-exceptions/{availabilityExceptionId}", "wix-safe-agent-cli restaurants-online-order-availability-exceptions delete"),
            "availabilityExceptions.updateAvailabilityException": ("PATCH", "/restaurants-availability-exceptions/v1/availability-exceptions/{availabilityException.id}", "wix-safe-agent-cli restaurants-online-order-availability-exceptions update"),
            "availabilityExceptions.queryAvailabilityExceptions": ("POST", "/restaurants-availability-exceptions/v1/availability-exceptions/query", "wix-safe-agent-cli restaurants-online-order-availability-exceptions query"),
            "availabilityExceptions.bulkCreateAvailabilityExceptions": ("POST", "/restaurants-availability-exceptions/v1/bulk/availability-exceptions/create", "wix-safe-agent-cli restaurants-online-order-availability-exceptions bulk-create"),
            "availabilityExceptions.bulkUpdateAvailabilityExceptions": ("POST", "/restaurants-availability-exceptions/v1/bulk/availability-exceptions/update", "wix-safe-agent-cli restaurants-online-order-availability-exceptions bulk-update"),
            "availabilityExceptions.bulkUpdateAvailabilityExceptionTags": ("POST", "/restaurants-availability-exceptions/v1/bulk/availability-exceptions/update-tags", "wix-safe-agent-cli restaurants-online-order-availability-exceptions bulk-update-tags"),
            "availabilityExceptions.bulkUpdateAvailabilityExceptionTagsByFilter": ("POST", "/restaurants-availability-exceptions/v1/bulk/availability-exceptions/update-tags-by-filter", "wix-safe-agent-cli restaurants-online-order-availability-exceptions bulk-update-tags-by-filter"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-current-revision", by_id["availabilityExceptions.updateAvailabilityException"]["flags"])
        self.assertIn("requires-current-revision", by_id["availabilityExceptions.bulkUpdateAvailabilityExceptions"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["availabilityExceptions.deleteAvailabilityException"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["availabilityExceptions.bulkUpdateAvailabilityExceptionTagsByFilter"]["flags"])
        for method_id in [
            "availabilityExceptions.availabilityExceptionCreated",
            "availabilityExceptions.availabilityExceptionDeleted",
            "availabilityExceptions.availabilityExceptionUpdated",
        ]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_online_order_service_fees_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-online-order-service-fees"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "serviceFees.calculateServiceFees": ("POST", "/service-fees/v1/calculate", "wix-safe-agent-cli restaurants-online-order-service-fees calculate"),
            "serviceFees.listRules": ("GET", "/service-fees/v1/rules", "wix-safe-agent-cli restaurants-online-order-service-fees list"),
            "serviceFees.createRule": ("POST", "/service-fees/v1/rules", "wix-safe-agent-cli restaurants-online-order-service-fees create"),
            "serviceFees.getRule": ("GET", "/service-fees/v1/rules/{ruleId}", "wix-safe-agent-cli restaurants-online-order-service-fees get"),
            "serviceFees.deleteRule": ("DELETE", "/service-fees/v1/rules/{ruleId}", "wix-safe-agent-cli restaurants-online-order-service-fees delete"),
            "serviceFees.updateRule": ("PATCH", "/service-fees/v1/rules/{rule.id}", "wix-safe-agent-cli restaurants-online-order-service-fees update"),
            "serviceFees.queryRules": ("POST", "/service-fees/v1/rules/query", "wix-safe-agent-cli restaurants-online-order-service-fees query"),
            "serviceFees.bulkCreateRules": ("POST", "/service-fees/v1/bulk/rules/create", "wix-safe-agent-cli restaurants-online-order-service-fees bulk-create"),
            "serviceFees.bulkUpdateRules": ("PATCH", "/service-fees/v1/bulk/rules/update", "wix-safe-agent-cli restaurants-online-order-service-fees bulk-update"),
            "serviceFees.bulkDeleteRules": ("DELETE", "/service-fees/v1/bulk/rules/delete", "wix-safe-agent-cli restaurants-online-order-service-fees bulk-delete"),
            "serviceFees.bulkUpdateRuleTags": ("POST", "/service-fees/v1/bulk/rules/update-tags", "wix-safe-agent-cli restaurants-online-order-service-fees bulk-update-tags"),
            "serviceFees.bulkUpdateRuleTagsByFilter": ("POST", "/service-fees/v1/bulk/rules/update-tags-by-filter", "wix-safe-agent-cli restaurants-online-order-service-fees bulk-update-tags-by-filter"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-current-revision", by_id["serviceFees.updateRule"]["flags"])
        self.assertIn("requires-current-revision", by_id["serviceFees.bulkUpdateRules"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["serviceFees.deleteRule"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["serviceFees.bulkDeleteRules"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["serviceFees.bulkUpdateRuleTagsByFilter"]["flags"])
        for method_id in ["serviceFees.ruleCreated", "serviceFees.ruleDeleted", "serviceFees.ruleUpdated"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_online_order_notification_recipients_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-online-order-notification-recipients"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "notificationRecipients.createRecipient": ("POST", "/rest-notification-recipients/v1/recipients", "wix-safe-agent-cli restaurants-online-order-notification-recipients create"),
            "notificationRecipients.getRecipient": ("GET", "/rest-notification-recipients/v1/recipients/{recipientId}", "wix-safe-agent-cli restaurants-online-order-notification-recipients get"),
            "notificationRecipients.deleteRecipient": ("DELETE", "/rest-notification-recipients/v1/recipients/{recipientId}", "wix-safe-agent-cli restaurants-online-order-notification-recipients delete"),
            "notificationRecipients.updateRecipient": ("PATCH", "/rest-notification-recipients/v1/recipients/{recipient.id}", "wix-safe-agent-cli restaurants-online-order-notification-recipients update"),
            "notificationRecipients.queryRecipients": ("POST", "/rest-notification-recipients/v1/recipients/query", "wix-safe-agent-cli restaurants-online-order-notification-recipients query"),
            "notificationRecipients.bulkCreateRecipients": ("POST", "/rest-notification-recipients/v1/bulk/recipients", "wix-safe-agent-cli restaurants-online-order-notification-recipients bulk-create"),
            "notificationRecipients.bulkUpdateRecipients": ("POST", "/rest-notification-recipients/v1/bulk/recipients/update", "wix-safe-agent-cli restaurants-online-order-notification-recipients bulk-update"),
            "notificationRecipients.bulkDeleteRecipients": ("POST", "/rest-notification-recipients/v1/bulk/recipients/delete", "wix-safe-agent-cli restaurants-online-order-notification-recipients bulk-delete"),
            "notificationRecipients.bulkUpdateRecipientTags": ("POST", "/rest-notification-recipients/v1/bulk/recipients/update-tags", "wix-safe-agent-cli restaurants-online-order-notification-recipients bulk-update-tags"),
            "notificationRecipients.bulkUpdateRecipientTagsByFilter": ("POST", "/rest-notification-recipients/v1/bulk/recipients/update-tags-by-filter", "wix-safe-agent-cli restaurants-online-order-notification-recipients bulk-update-tags-by-filter"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-current-revision", by_id["notificationRecipients.updateRecipient"]["flags"])
        self.assertIn("requires-current-revision", by_id["notificationRecipients.bulkUpdateRecipients"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["notificationRecipients.deleteRecipient"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["notificationRecipients.bulkDeleteRecipients"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["notificationRecipients.bulkUpdateRecipientTagsByFilter"]["flags"])
        for method_id in [
            "notificationRecipients.recipientCreated",
            "notificationRecipients.recipientDeleted",
            "notificationRecipients.recipientUpdated",
        ]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_reservations_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-reservations"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "reservations.createReservation": ("POST", "/table-reservations/reservations/v1/reservations", "wix-safe-agent-cli restaurants-reservations create"),
            "reservations.getReservation": ("GET", "/table-reservations/reservations/v1/reservations/{reservationId}", "wix-safe-agent-cli restaurants-reservations get"),
            "reservations.updateReservation": ("PATCH", "/table-reservations/reservations/v1/reservations/{reservation.id}", "wix-safe-agent-cli restaurants-reservations update"),
            "reservations.deleteReservation": ("DELETE", "/table-reservations/reservations/v1/reservations/{reservationId}", "wix-safe-agent-cli restaurants-reservations delete"),
            "reservations.queryReservations": ("POST", "/table-reservations/reservations/v1/reservations/query", "wix-safe-agent-cli restaurants-reservations query"),
            "reservations.listReservations": ("GET", "/table-reservations/reservations/v1/reservations", "wix-safe-agent-cli restaurants-reservations list"),
            "reservations.searchReservations": ("POST", "/table-reservations/reservations/v1/reservations/search", "wix-safe-agent-cli restaurants-reservations search"),
            "reservations.bulkArchiveReservations": ("POST", "/table-reservations/reservations/v1/bulk/reservations/archive", "wix-safe-agent-cli restaurants-reservations bulk-archive"),
            "reservations.bulkUnarchiveReservations": ("POST", "/table-reservations/reservations/v1/bulk/reservations/unarchive", "wix-safe-agent-cli restaurants-reservations bulk-unarchive"),
            "reservations.cancelReservation": ("POST", "/table-reservations/reservations/v1/reservations/{reservationId}/cancel", "wix-safe-agent-cli restaurants-reservations cancel"),
            "reservations.createHeldReservation": ("POST", "/table-reservations/reservations/v1/reservations/hold", "wix-safe-agent-cli restaurants-reservations create-held"),
            "reservations.reserveReservation": ("POST", "/table-reservations/reservations/v1/reservations/{reservationId}/reserve", "wix-safe-agent-cli restaurants-reservations reserve"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-current-revision", by_id["reservations.updateReservation"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["reservations.deleteReservation"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["reservations.cancelReservation"]["flags"])
        for method_id in ["reservations.reservationCreated", "reservations.reservationDeleted", "reservations.reservationUpdated"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_reservation_locations_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-reservation-locations"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "reservationLocations.getReservationLocation": ("GET", "/table-reservations/reservation-locations/v1/reservation-locations/{reservationLocationId}", "wix-safe-agent-cli restaurants-reservation-locations get"),
            "reservationLocations.updateReservationLocation": ("PATCH", "/table-reservations/reservation-locations/v1/reservation-locations/{reservationLocation.id}", "wix-safe-agent-cli restaurants-reservation-locations update"),
            "reservationLocations.queryReservationLocations": ("POST", "/table-reservations/reservation-locations/v1/reservation-locations/query", "wix-safe-agent-cli restaurants-reservation-locations query"),
            "reservationLocations.listReservationLocations": ("GET", "/table-reservations/reservation-locations/v1/reservation-locations", "wix-safe-agent-cli restaurants-reservation-locations list"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-current-revision", by_id["reservationLocations.updateReservationLocation"]["flags"])
        for method_id in ["reservationLocations.reservationLocationCreated", "reservationLocations.reservationLocationUpdated"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_reservation_time_slots_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-reservation-time-slots"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "reservationTimeSlots.checkTimeSlot": ("POST", "/table-reservations/reservations/v1/check-time-slot", "wix-safe-agent-cli restaurants-reservation-time-slots check"),
            "reservationTimeSlots.getScheduledTimeSlots": ("POST", "/table-reservations/reservations/v1/scheduled-time-slots", "wix-safe-agent-cli restaurants-reservation-time-slots get-scheduled"),
            "reservationTimeSlots.getTimeSlots": ("POST", "/table-reservations/reservations/v1/time-slots", "wix-safe-agent-cli restaurants-reservation-time-slots get"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertIn("read-helper", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

    def test_restaurants_reservation_experiences_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["restaurants-reservation-experiences"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "experiences.createExperience": ("POST", "/table-reservations/experiences/v1/experiences", "wix-safe-agent-cli restaurants-reservation-experiences create"),
            "experiences.getExperience": ("GET", "/table-reservations/experiences/v1/experiences/{experienceId}", "wix-safe-agent-cli restaurants-reservation-experiences get"),
            "experiences.updateExperience": ("PATCH", "/table-reservations/experiences/v1/experiences/{experience.id}", "wix-safe-agent-cli restaurants-reservation-experiences update"),
            "experiences.queryExperiences": ("POST", "/table-reservations/experiences/v1/experiences/query", "wix-safe-agent-cli restaurants-reservation-experiences query"),
            "experiences.searchExperiences": ("POST", "/table-reservations/experiences/v1/experiences/search", "wix-safe-agent-cli restaurants-reservation-experiences search"),
            "experiences.bulkUpdateExperienceTags": ("POST", "/table-reservations/experiences/v1/bulk/experiences/update-tags", "wix-safe-agent-cli restaurants-reservation-experiences bulk-update-tags"),
            "experiences.bulkUpdateExperienceTagsByFilter": ("POST", "/table-reservations/experiences/v1/bulk/experiences/update-tags-by-filter", "wix-safe-agent-cli restaurants-reservation-experiences bulk-update-tags-by-filter"),
            "experiences.getExperienceBySlug": ("GET", "/table-reservations/experiences/v1/experiences/slug/{slug}", "wix-safe-agent-cli restaurants-reservation-experiences get-by-slug"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        self.assertIn("requires-current-revision", by_id["experiences.updateExperience"]["flags"])
        self.assertIn("requires-ack-irreversible", by_id["experiences.bulkUpdateExperienceTagsByFilter"]["flags"])
        for method_id in ["experiences.experienceCreated", "experiences.experienceTagsModified", "experiences.experienceUpdated"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_restaurants_remaining_subfamilies_are_normalized_placeholders(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        expected = set()

        self.assertTrue(expected.issubset(families))
        for slug in expected:
            with self.subTest(slug=slug):
                family = families[slug]
                self.assertEqual(family.get("coverage_status"), "not-yet-implemented")
                self.assertIn("partial-family-inventory", family.get("default_flags", []))
                self.assertTrue(str(family.get("source_urls", [""])[0]).startswith("https://dev.wix.com/docs/"))

    def test_blog_posts_stats_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["blog-posts-stats"]
        self.assertEqual(family.get("coverage_status"), "implemented")

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "blogPosts.getPost": ("GET", "/v3/posts/{postId}", "wix-safe-agent-cli blog-posts-stats get"),
            "blogPosts.queryPosts": ("POST", "/v3/posts/query", "wix-safe-agent-cli blog-posts-stats query"),
            "blogPosts.listPosts": ("GET", "/v3/posts", "wix-safe-agent-cli blog-posts-stats list"),
            "blogPosts.getPostBySlug": ("GET", "/v3/posts/slugs/{slug=**}", "wix-safe-agent-cli blog-posts-stats get-by-slug"),
            "blogPosts.getPostMetrics": ("GET", "/v3/posts/{postId}/metrics", "wix-safe-agent-cli blog-posts-stats get-metrics"),
            "blogStats.getTotalPosts": ("GET", "/blog/v2/stats/posts/total", "wix-safe-agent-cli blog-posts-stats get-total"),
            "blogStats.queryPostCount": ("GET", "/blog/v2/stats/post/count", "wix-safe-agent-cli blog-posts-stats query-count"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        for method_id in ["blogPosts.postCreated", "blogPosts.postDeleted", "blogPosts.postLiked", "blogPosts.postUnliked", "blogPosts.postUpdated"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_blog_draft_posts_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["blog-draft-posts"]
        self.assertEqual(family.get("coverage_status"), "implemented")

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "blogDraftPosts.createDraftPost": ("POST", "/blog/v3/draft-posts", "wix-safe-agent-cli blog-draft-posts create"),
            "blogDraftPosts.getDraftPost": ("GET", "/blog/v3/draft-posts/{draftPostId}", "wix-safe-agent-cli blog-draft-posts get"),
            "blogDraftPosts.updateDraftPost": ("PATCH", "/blog/v3/draft-posts/{draftPost.id}", "wix-safe-agent-cli blog-draft-posts update"),
            "blogDraftPosts.deleteDraftPost": ("DELETE", "/blog/v3/draft-posts/{draftPostId}", "wix-safe-agent-cli blog-draft-posts delete"),
            "blogDraftPosts.queryDraftPosts": ("POST", "/blog/v3/draft-posts/query", "wix-safe-agent-cli blog-draft-posts query"),
            "blogDraftPosts.listDraftPosts": ("GET", "/blog/v3/draft-posts", "wix-safe-agent-cli blog-draft-posts list"),
            "blogDraftPosts.bulkCreateDraftPosts": ("POST", "/blog/v3/bulk/draft-posts/create", "wix-safe-agent-cli blog-draft-posts bulk-create"),
            "blogDraftPosts.bulkDeleteDraftPosts": ("DELETE", "/blog/v3/bulk/draft-posts", "wix-safe-agent-cli blog-draft-posts bulk-delete"),
            "blogDraftPosts.bulkUpdateDraftPosts": ("PATCH", "/blog/v3/draft-posts/update", "wix-safe-agent-cli blog-draft-posts bulk-update"),
            "blogDraftPosts.getDeletedDraftPost": ("GET", "/blog/v3/draft-posts/trash-bin/{draftPostId}", "wix-safe-agent-cli blog-draft-posts get-deleted"),
            "blogDraftPosts.listDeletedDraftPosts": ("GET", "/blog/v3/draft-posts/trash-bin", "wix-safe-agent-cli blog-draft-posts list-deleted"),
            "blogDraftPosts.publishDraftPost": ("POST", "/blog/v3/draft-posts/{draftPostId}/publish", "wix-safe-agent-cli blog-draft-posts publish"),
            "blogDraftPosts.removeFromTrashBin": ("DELETE", "/blog/v3/draft-posts/trash-bin/{draftPostId}", "wix-safe-agent-cli blog-draft-posts remove-from-trash-bin"),
            "blogDraftPosts.restoreFromTrashBin": ("POST", "/blog/v3/draft-posts/trash-bin/{draftPostId}/restore", "wix-safe-agent-cli blog-draft-posts restore-from-trash-bin"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        for method_id in ["blogDraftPosts.draftDeleted", "blogDraftPosts.draftPostCreated", "blogDraftPosts.draftPostUpdated"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_blog_categories_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["blog-categories"]
        self.assertEqual(family.get("coverage_status"), "implemented")

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "blogCategories.createCategory": ("POST", "/blog/v3/categories", "wix-safe-agent-cli blog-categories create"),
            "blogCategories.getCategory": ("GET", "/blog/v3/categories/{categoryId}", "wix-safe-agent-cli blog-categories get"),
            "blogCategories.updateCategory": ("PATCH", "/blog/v3/categories/{category.id}", "wix-safe-agent-cli blog-categories update"),
            "blogCategories.deleteCategory": ("DELETE", "/blog/v3/categories/{categoryId}", "wix-safe-agent-cli blog-categories delete"),
            "blogCategories.queryCategories": ("POST", "/blog/v3/categories/query", "wix-safe-agent-cli blog-categories query"),
            "blogCategories.listCategories": ("GET", "/blog/v3/categories", "wix-safe-agent-cli blog-categories list"),
            "blogCategories.getCategoryBySlug": ("GET", "/blog/v3/categories/slugs/{slug=**}", "wix-safe-agent-cli blog-categories get-by-slug"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        for method_id in ["blogCategories.categoryCreated", "blogCategories.categoryDeleted", "blogCategories.categoryUpdated"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_blog_tags_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["blog-tags"]
        self.assertEqual(family.get("coverage_status"), "implemented")

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "blogTags.getTag": ("GET", "/v3/tags/{tagId}", "wix-safe-agent-cli blog-tags get"),
            "blogTags.deleteTag": ("DELETE", "/v3/tags/{tagId}", "wix-safe-agent-cli blog-tags delete"),
            "blogTags.queryTags": ("POST", "/v3/tags/query", "wix-safe-agent-cli blog-tags query"),
            "blogTags.createTag": ("POST", "/v3/tags", "wix-safe-agent-cli blog-tags create"),
            "blogTags.getTagByLabel": ("GET", "/v3/tags/labels/{label=**}", "wix-safe-agent-cli blog-tags get-by-label"),
            "blogTags.getTagBySlug": ("GET", "/v3/tags/slugs/{slug}", "wix-safe-agent-cli blog-tags get-by-slug"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        for method_id in ["blogTags.tagCreated", "blogTags.tagDeleted", "blogTags.tagUpdated"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_blog_likes_inventory_matches_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["blog-likes"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertNotIn("developer-preview", family.get("default_flags", []))

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        expected = {
            "blogLikes.createLike": ("POST", "/blog/v1/likes", "wix-safe-agent-cli blog-likes create"),
            "blogLikes.getLike": ("GET", "/blog/v1/likes/{likeId}", "wix-safe-agent-cli blog-likes get"),
            "blogLikes.deleteLike": ("DELETE", "/blog/v1/likes/{likeId}", "wix-safe-agent-cli blog-likes delete"),
            "blogLikes.queryLikes": ("POST", "/blog/v1/likes/query", "wix-safe-agent-cli blog-likes query"),
            "blogLikes.deleteLikeByFqdnAndEntityId": ("DELETE", "/blog/v1/likes/fqdn/{fqdn}/entity-id/{entityId}", "wix-safe-agent-cli blog-likes delete-by-fqdn-entity-id"),
        }
        for method_id, (http_method, path, command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertNotIn("developer-preview", by_id[method_id]["flags"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        for method_id in ["blogLikes.likeCreated", "blogLikes.likeDeleted"]:
            self.assertIn("callback-only", by_id[method_id]["flags"])
            self.assertIn("developer-preview", by_id[method_id]["flags"])
            self.assertFalse(by_id[method_id]["cli_callable"])

    def test_forum_inventory_is_disabled_and_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        family = families["forum"]
        self.assertEqual(family.get("coverage_status"), "disabled")
        self.assertIn("disabled", family.get("default_flags", []))
        self.assertIn("discontinued", family.get("default_flags", []))

        by_id = {operation["method_id"]: operation for operation in family["operations"]}
        source_urls = set(family.get("source_urls", []))
        for operation in family["operations"]:
            self.assertIn(operation.get("doc_url"), source_urls)

        expected = {
            "forumCategories.getCategory": ("GET", "/forum/v1/categories/{categoryId}"),
            "forumCategories.getCategoryBySlug": ("GET", "/forum/v1/categories/slugs/{slug}"),
            "forumCategories.queryCategories": ("POST", "/forum/v1/categories/query"),
            "forumPosts.getPost": ("GET", "/forum/v1/posts/{postId}"),
            "forumPosts.getPostBySlug": ("GET", "/forum/v1/posts/slugs/{slug}"),
            "forumPosts.queryPosts": ("POST", "/forum/v1/posts/query"),
        }
        for method_id, (http_method, path) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertIn("disabled", by_id[method_id]["flags"])
                self.assertIn("non-callable", by_id[method_id]["flags"])
                self.assertFalse(by_id[method_id]["cli_callable"])
                self.assertTrue(str(by_id[method_id].get("doc_url")).startswith("https://dev.wix.com/docs/"))

        callback_ids = [
            "forumCategories.categoryCreated",
            "forumCategories.categoryDeleted",
            "forumCategories.categoryUpdated",
            "forumPosts.closed",
            "forumPosts.postCreated",
            "forumPosts.postDeleted",
            "forumPosts.liked",
            "forumPosts.moved",
            "forumPosts.opened",
            "forumPosts.pinned",
            "forumPosts.reported",
            "forumPosts.unliked",
            "forumPosts.unpinned",
            "forumPosts.postUpdated",
        ]
        for method_id in callback_ids:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id]["flags"])
                self.assertIn("disabled", by_id[method_id]["flags"])
                self.assertFalse(by_id[method_id]["cli_callable"])

    def test_remaining_blog_subfamilies_are_normalized_placeholders(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        expected: set[str] = set()

        self.assertTrue(expected.issubset(families))
        for slug in expected:
            with self.subTest(slug=slug):
                family = families[slug]
                self.assertEqual(family.get("coverage_status"), "not-yet-implemented")
                self.assertIn("partial-family-inventory", family.get("default_flags", []))
                self.assertTrue(str(family.get("source_urls", [""])[0]).startswith("https://dev.wix.com/docs/"))

    def test_wix_app_collections_reference_family_is_accounted(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("cms-wix-app-collections", families)
        family = families["cms-wix-app-collections"]
        self.assertEqual(family.get("operations"), [])
        self.assertIn("reference-only", family.get("default_flags", []))
        self.assertIn("covered-by-data-collections-and-data-items", family.get("default_flags", []))

        source_urls = set(family.get("source_urls", []))
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/wix-app-collections/introduction",
            source_urls,
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/wix-app-collections/wix-stores-collections",
            source_urls,
        )

    def test_data_folders_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("cms-data-folders", families)
        family = families["cms-data-folders"]
        self.assertIn("operations", family)

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 7)

        expected_commands = {
            "wix-safe-agent-cli data-folders get",
            "wix-safe-agent-cli data-folders create",
            "wix-safe-agent-cli data-folders update",
            "wix-safe-agent-cli data-folders delete",
            "wix-safe-agent-cli data-folders create-collection-reference",
            "wix-safe-agent-cli data-folders get-collection-references",
            "wix-safe-agent-cli data-folders delete-collection-reference",
        }

        method_ids = [op.get("method_id") for op in operations]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(
            expected_commands.issubset(inventory_commands),
            msg=f"Missing data folders planned commands in inventory: {sorted(expected_commands - inventory_commands)}",
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertIsNotNone(op["planned_command"])
            self.assertIsNotNone(op["http_method"])
            self.assertIsNotNone(op["path"])

    def test_data_indexes_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("cms-indexes", families)
        family = families["cms-indexes"]
        self.assertIn("operations", family)

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 3)

        expected_commands = {
            "wix-safe-agent-cli data-indexes list",
            "wix-safe-agent-cli data-indexes create",
            "wix-safe-agent-cli data-indexes drop",
        }

        source_urls = set(family.get("source_urls", []))
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/indexes/introduction",
            source_urls,
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/indexes/list-indexes",
            source_urls,
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/indexes/create-index",
            source_urls,
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/indexes/drop-index",
            source_urls,
        )

        method_ids = [op.get("method_id") for op in operations]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        inventory_commands = {op.get("planned_command") for op in operations}
        self.assertTrue(
            expected_commands.issubset(inventory_commands),
            msg=f"Missing data indexes planned commands in inventory: {sorted(expected_commands - inventory_commands)}",
        )

        for op in operations:
            self.assertIn("implemented", op["flags"])
            self.assertIsNotNone(op["planned_command"])
            self.assertIsNotNone(op["http_method"])
            self.assertIsNotNone(op["path"])

    def test_form_submissions_and_app_instance_families_present(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("app-instance", families)
        self.assertIn("form-submissions", families)

        app_instance_ops = families["app-instance"].get("operations", [])
        self.assertEqual(len(app_instance_ops), 1)
        self.assertEqual(app_instance_ops[0].get("planned_command"), "wix-safe-agent-cli app-instance get")

        form_ops = families["form-submissions"].get("operations", [])
        method_ids = [op["method_id"] for op in form_ops]
        self.assertEqual(len(method_ids), len(set(method_ids)))

        expected_form_commands = {
            "wix-safe-agent-cli form-submissions get-submission",
            "wix-safe-agent-cli form-submissions query-submissions-by-namespace",
            "wix-safe-agent-cli form-submissions count-submissions",
            "wix-safe-agent-cli form-submissions get-media-upload-url",
            "wix-safe-agent-cli form-submissions create-submission",
            "wix-safe-agent-cli form-submissions update-submission",
            "wix-safe-agent-cli form-submissions delete-submission",
            "wix-safe-agent-cli form-submissions confirm-submission",
            "wix-safe-agent-cli form-submissions bulk-mark-submissions-as-seen",
        }

        inventory_form_commands = {op.get("planned_command") for op in form_ops}
        self.assertTrue(
            expected_form_commands.issubset(inventory_form_commands),
            msg=f"Missing form submissions planned commands in inventory: {sorted(expected_form_commands - inventory_form_commands)}",
        )

    def test_chat_settings_family_present_and_callback_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("chat-settings", families)
        family = families["chat-settings"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 8)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "chatSettings.createChatSettings": ("POST", "/forms/ai/v1/chat-settings", "wix-safe-agent-cli chat-settings create"),
            "chatSettings.getChatSettings": (
                "GET",
                "/forms/ai/v1/chat-settings/{chatSettingsId}",
                "wix-safe-agent-cli chat-settings get",
            ),
            "chatSettings.updateChatSettings": (
                "PATCH",
                "/forms/ai/v1/chat-settings/{chatSettings.id}",
                "wix-safe-agent-cli chat-settings update",
            ),
            "chatSettings.deleteChatSettings": (
                "DELETE",
                "/forms/ai/v1/chat-settings/{chatSettingsId}",
                "wix-safe-agent-cli chat-settings delete",
            ),
            "chatSettings.queryChatSettings": (
                "POST",
                "/forms/ai/v1/chat-settings/query",
                "wix-safe-agent-cli chat-settings query",
            ),
        }
        for method_id, (http_method, path, command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                op = by_id[method_id]
                self.assertEqual(op.get("http_method"), http_method)
                self.assertEqual(op.get("path"), path)
                self.assertEqual(op.get("planned_command"), command)
                self.assertIn("implemented", op["flags"])
                self.assertTrue(op.get("cli_callable"))

        for method_id in (
            "chatSettings.chatSettingsCreated",
            "chatSettings.chatSettingsDeleted",
            "chatSettings.chatSettingsUpdated",
        ):
            with self.subTest(method_id=method_id):
                op = by_id[method_id]
                self.assertIsNone(op.get("http_method"))
                self.assertIsNone(op.get("path"))
                self.assertIsNone(op.get("planned_command"))
                self.assertIn("callback-only", op["flags"])
                self.assertFalse(op.get("cli_callable"))

    def test_community_groups_family_present_and_callback_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-groups", families)
        family = families["community-groups"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 12)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityGroups.createGroup": (
                "POST",
                "/social-groups-proxy/groups/v2/groups",
                "wix-safe-agent-cli community-groups create",
            ),
            "communityGroups.getGroup": (
                "GET",
                "/social-groups-proxy/groups/v2/groups/{groupId}",
                "wix-safe-agent-cli community-groups get",
            ),
            "communityGroups.updateGroup": (
                "PATCH",
                "/social-groups-proxy/groups/v2/groups/{group.id}",
                "wix-safe-agent-cli community-groups update",
            ),
            "communityGroups.deleteGroup": (
                "DELETE",
                "/social-groups-proxy/groups/v2/groups/{groupId}",
                "wix-safe-agent-cli community-groups delete",
            ),
            "communityGroups.getGroupBySlug": (
                "GET",
                "/social-groups-proxy/groups/v2/groups/slugs/{slug}",
                "wix-safe-agent-cli community-groups get-by-slug",
            ),
            "communityGroups.listGroups": (
                "GET",
                "/social-groups-proxy/groups/v2/groups",
                "wix-safe-agent-cli community-groups list",
            ),
            "communityGroups.queryGroups": (
                "POST",
                "/social-groups-proxy/groups/v2/groups/query",
                "wix-safe-agent-cli community-groups query",
            ),
        }
        for method_id, (http_method, path, command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                op = by_id[method_id]
                self.assertEqual(op.get("http_method"), http_method)
                self.assertEqual(op.get("path"), path)
                self.assertEqual(op.get("planned_command"), command)
                self.assertIn("implemented", op["flags"])
                self.assertTrue(op.get("cli_callable"))

        self.assertIn("requires-ack-irreversible", by_id["communityGroups.deleteGroup"]["flags"])

        for method_id in (
            "communityGroups.groupCreated",
            "communityGroups.groupDeleted",
            "communityGroups.groupCoverChanged",
            "communityGroups.groupDescriptionChanged",
            "communityGroups.groupUpdated",
        ):
            with self.subTest(method_id=method_id):
                op = by_id[method_id]
                self.assertIsNone(op.get("http_method"))
                self.assertIsNone(op.get("path"))
                self.assertIsNone(op.get("planned_command"))
                self.assertIn("callback-only", op["flags"])
                self.assertFalse(op.get("cli_callable"))

    def test_interactive_form_sessions_family_present_and_streaming_marked(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("interactive-form-sessions", families)
        family = families["interactive-form-sessions"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 5)
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "interactiveFormSessions.createInteractiveFormSession": (
                "POST",
                "/forms/ai/v1/interactive-form-sessions",
                "wix-safe-agent-cli interactive-form-sessions create",
            ),
            "interactiveFormSessions.createInteractiveFormSessionStreamed": (
                "POST",
                "/forms/ai/v1/interactive-form-sessions/create-streamed",
                "wix-safe-agent-cli interactive-form-sessions create-streamed",
            ),
            "interactiveFormSessions.sendUserMessage": (
                "POST",
                "/forms/ai/v1/interactive-form-sessions/{interactiveFormSessionId}/send-user-message",
                "wix-safe-agent-cli interactive-form-sessions send-message",
            ),
            "interactiveFormSessions.sendUserMessageStreamed": (
                "POST",
                "/forms/ai/v1/interactive-form-sessions/{interactiveFormSessionId}/send-user-message-streamed",
                "wix-safe-agent-cli interactive-form-sessions send-message-streamed",
            ),
            "interactiveFormSessions.generateFormSummary": (
                "POST",
                "/forms/ai/v1/interactive-form-sessions/generate-form-summary",
                "wix-safe-agent-cli interactive-form-sessions generate-summary",
            ),
        }
        for method_id, (http_method, path, command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                op = by_id[method_id]
                self.assertEqual(op.get("http_method"), http_method)
                self.assertEqual(op.get("path"), path)
                self.assertEqual(op.get("planned_command"), command)
                self.assertIn("implemented", op["flags"])
                self.assertIn("developer-preview", op["flags"])
                self.assertTrue(op.get("cli_callable"))

        self.assertIn("streaming-response", by_id["interactiveFormSessions.createInteractiveFormSessionStreamed"]["flags"])
        self.assertIn("streaming-response", by_id["interactiveFormSessions.sendUserMessageStreamed"]["flags"])

    def test_intake_forms_families_present_and_paths_match_official_docs(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("intake-forms", families)
        forms_ops = {op.get("method_id"): op for op in families["intake-forms"].get("operations", [])}
        self.assertEqual(len(forms_ops), 6)
        expected_forms = {
            "intakeForms.queryIntakeForms": (
                "POST",
                "/_api/intake-forms/v1/intake-forms/query",
                "wix-safe-agent-cli intake-forms query",
            ),
            "intakeForms.createCustomerSubmissionLink": (
                "GET",
                "/_api/intake-forms/v1/intake-forms/{intakeFormId}/link",
                "wix-safe-agent-cli intake-forms create-customer-submission-link",
            ),
            "intakeForms.archiveIntakeForm": (
                "POST",
                "/_api/intake-forms/v1/intake-forms/{intakeFormId}/archive",
                "wix-safe-agent-cli intake-forms archive",
            ),
            "intakeForms.unarchiveIntakeForm": (
                "POST",
                "/_api/intake-forms/v1/intake-forms/{intakeFormId}/unarchive",
                "wix-safe-agent-cli intake-forms unarchive",
            ),
            "intakeForms.updateIntakeFormExpirationPeriod": (
                "PATCH",
                "/_api/intake-forms/v1/intake-forms/{intakeFormId}",
                "wix-safe-agent-cli intake-forms update-expiration-period",
            ),
            "intakeForms.deleteIntakeForm": (
                "DELETE",
                "/_api/intake-forms/v1/intake-forms/{intakeFormId}",
                "wix-safe-agent-cli intake-forms delete",
            ),
        }
        for method_id, (http_method, path, command) in expected_forms.items():
            with self.subTest(method_id=method_id):
                op = forms_ops[method_id]
                self.assertEqual(op.get("http_method"), http_method)
                self.assertEqual(op.get("path"), path)
                self.assertEqual(op.get("planned_command"), command)
                self.assertIn("implemented", op["flags"])
                self.assertTrue(op.get("cli_callable"))

        self.assertIn("intake-form-submissions", families)
        submission_ops = {op.get("method_id"): op for op in families["intake-form-submissions"].get("operations", [])}
        self.assertEqual(len(submission_ops), 8)
        self.assertEqual(
            submission_ops["intakeFormSubmissions.countSubmissionsByIntakeFormIds"]["path"],
            "/_api/intake-forms/v1/submissions/count",
        )
        self.assertEqual(
            submission_ops["intakeFormSubmissions.queryIntakeFormSubmissions"]["path"],
            "/_api/intake-forms/v1/submissions/query",
        )
        self.assertEqual(
            submission_ops["intakeFormSubmissions.cancelIntakeFormSubmission"]["planned_command"],
            "wix-safe-agent-cli intake-form-submissions cancel",
        )
        self.assertIn("ack-irreversible", forms_ops["intakeForms.deleteIntakeForm"]["flags"])
        self.assertIn("ack-irreversible", submission_ops["intakeFormSubmissions.cancelIntakeFormSubmission"]["flags"])
        self.assertIn("ack-irreversible", submission_ops["intakeFormSubmissions.deleteIntakeFormSubmission"]["flags"])

    def test_community_group_rules_family_present_and_event_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-group-rules", families)
        family = families["community-group-rules"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 3)
        by_id = {op.get("method_id"): op for op in operations}
        self.assertEqual(by_id["communityGroupRules.listRules"]["http_method"], "GET")
        self.assertEqual(by_id["communityGroupRules.listRules"]["path"], "/social-groups/v2/rules/{groupId}")
        self.assertEqual(
            by_id["communityGroupRules.listRules"]["planned_command"],
            "wix-safe-agent-cli community-group-rules list",
        )
        self.assertEqual(by_id["communityGroupRules.createOrReplaceAllRules"]["http_method"], "PUT")
        self.assertEqual(by_id["communityGroupRules.createOrReplaceAllRules"]["path"], "/social-groups/v2/rules/{groupId}")
        self.assertEqual(
            by_id["communityGroupRules.createOrReplaceAllRules"]["planned_command"],
            "wix-safe-agent-cli community-group-rules create-or-replace",
        )
        self.assertIn("ack-irreversible", by_id["communityGroupRules.createOrReplaceAllRules"]["flags"])
        self.assertFalse(by_id["communityGroupRules.groupRulesUpdated"]["cli_callable"])
        self.assertIn("callback-only", by_id["communityGroupRules.groupRulesUpdated"]["flags"])

    def test_community_group_requests_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-group-requests", families)
        family = families["community-group-requests"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 6)
        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityGroupRequests.listGroupRequests": (
                "GET",
                "/_api/social-groups-proxy/group-requests/v2/group-requests",
                "wix-safe-agent-cli community-group-requests list",
            ),
            "communityGroupRequests.queryGroupRequests": (
                "POST",
                "/_api/social-groups-proxy/group-requests/v2/group-requests/query",
                "wix-safe-agent-cli community-group-requests query",
            ),
            "communityGroupRequests.approveGroupRequests": (
                "POST",
                "/_api/social-groups-proxy/group-requests/v2/group-requests/approve",
                "wix-safe-agent-cli community-group-requests approve",
            ),
            "communityGroupRequests.rejectGroupRequests": (
                "POST",
                "/_api/social-groups-proxy/group-requests/v2/group-requests/reject",
                "wix-safe-agent-cli community-group-requests reject",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        self.assertIn("ack-irreversible", by_id["communityGroupRequests.approveGroupRequests"]["flags"])
        self.assertIn("ack-irreversible", by_id["communityGroupRequests.rejectGroupRequests"]["flags"])
        self.assertFalse(by_id["communityGroupRequests.groupRequestApproved"]["cli_callable"])
        self.assertFalse(by_id["communityGroupRequests.groupRequestRejected"]["cli_callable"])
        self.assertIn("callback-only", by_id["communityGroupRequests.groupRequestApproved"]["flags"])
        self.assertIn("callback-only", by_id["communityGroupRequests.groupRequestRejected"]["flags"])

    def test_community_group_members_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-group-members", families)
        family = families["community-group-members"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 8)
        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityGroupMembers.addGroupMembers": (
                "POST",
                "/social-groups-proxy/members/v2/groups/{groupId}/members",
                "wix-safe-agent-cli community-group-members add",
            ),
            "communityGroupMembers.listGroupMembers": (
                "GET",
                "/social-groups-proxy/members/v2/groups/{groupId}/members",
                "wix-safe-agent-cli community-group-members list",
            ),
            "communityGroupMembers.listMemberships": (
                "GET",
                "/social-groups-proxy/members/v2/members/{memberId}/memberships",
                "wix-safe-agent-cli community-group-members list-memberships",
            ),
            "communityGroupMembers.queryGroupMembers": (
                "POST",
                "/social-groups-proxy/members/v2/groups/{groupId}/members/query",
                "wix-safe-agent-cli community-group-members query",
            ),
            "communityGroupMembers.queryMemberships": (
                "POST",
                "/social-groups-proxy/members/v2/members/{memberId}/memberships/query",
                "wix-safe-agent-cli community-group-members query-memberships",
            ),
            "communityGroupMembers.removeGroupMembers": (
                "DELETE",
                "/social-groups-proxy/members/v2/groups/{groupId}/members",
                "wix-safe-agent-cli community-group-members remove",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        self.assertIn("ack-irreversible", by_id["communityGroupMembers.addGroupMembers"]["flags"])
        self.assertIn("ack-irreversible", by_id["communityGroupMembers.removeGroupMembers"]["flags"])
        self.assertFalse(by_id["communityGroupMembers.memberAdded"]["cli_callable"])
        self.assertFalse(by_id["communityGroupMembers.memberRemoved"]["cli_callable"])
        self.assertIn("callback-only", by_id["communityGroupMembers.memberAdded"]["flags"])
        self.assertIn("callback-only", by_id["communityGroupMembers.memberRemoved"]["flags"])

    def test_community_group_roles_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-group-roles", families)
        family = families["community-group-roles"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 4)
        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityGroupRoles.assignRole": (
                "POST",
                "/social-groups-proxy/roles/v2/groups/{groupId}/roles/assign",
                "wix-safe-agent-cli community-group-roles assign",
            ),
            "communityGroupRoles.unassignRole": (
                "POST",
                "/social-groups-proxy/roles/v2/groups/{groupId}/roles/unassign",
                "wix-safe-agent-cli community-group-roles unassign",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
                self.assertIn("ack-irreversible", by_id[method_id]["flags"])
        self.assertFalse(by_id["communityGroupRoles.roleAssignedToGroupMember"]["cli_callable"])
        self.assertFalse(by_id["communityGroupRoles.roleUnassignedFromGroupMember"]["cli_callable"])
        self.assertIn("callback-only", by_id["communityGroupRoles.roleAssignedToGroupMember"]["flags"])
        self.assertIn("callback-only", by_id["communityGroupRoles.roleUnassignedFromGroupMember"]["flags"])

    def test_community_join_requests_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-join-requests", families)
        family = families["community-join-requests"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 6)
        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityJoinRequests.approveJoinGroupRequests": (
                "POST",
                "/social-groups-proxy/join/v2/groups/{groupId}/join-requests/approve",
                "wix-safe-agent-cli community-join-requests approve",
            ),
            "communityJoinRequests.listJoinGroupRequests": (
                "GET",
                "/social-groups-proxy/join/v2/groups/{groupId}/join-requests",
                "wix-safe-agent-cli community-join-requests list",
            ),
            "communityJoinRequests.queryJoinGroupRequests": (
                "POST",
                "/social-groups-proxy/join/v2/groups/{groupId}/join-requests/query",
                "wix-safe-agent-cli community-join-requests query",
            ),
            "communityJoinRequests.rejectJoinGroupRequests": (
                "POST",
                "/social-groups-proxy/join/v2/groups/{groupId}/join-requests/reject",
                "wix-safe-agent-cli community-join-requests reject",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        self.assertIn("ack-irreversible", by_id["communityJoinRequests.approveJoinGroupRequests"]["flags"])
        self.assertIn("ack-irreversible", by_id["communityJoinRequests.rejectJoinGroupRequests"]["flags"])
        self.assertFalse(by_id["communityJoinRequests.joinGroupRequestApproved"]["cli_callable"])
        self.assertFalse(by_id["communityJoinRequests.joinGroupRequestRejected"]["cli_callable"])
        self.assertIn("callback-only", by_id["communityJoinRequests.joinGroupRequestApproved"]["flags"])
        self.assertIn("callback-only", by_id["communityJoinRequests.joinGroupRequestRejected"]["flags"])

    def test_community_membership_questions_family_present(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-membership-questions", families)
        family = families["community-membership-questions"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 3)
        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityMembershipQuestions.createOrReplaceAllMembershipQuestions": (
                "PUT",
                "/social-groups-proxy/questions/v2/membership-questions/{groupId}",
                "wix-safe-agent-cli community-membership-questions create-or-replace",
            ),
            "communityMembershipQuestions.listAnswers": (
                "POST",
                "/social-groups-proxy/questions/v2/membership-questions/{groupId}/answers",
                "wix-safe-agent-cli community-membership-questions list-answers",
            ),
            "communityMembershipQuestions.listMembershipQuestions": (
                "GET",
                "/social-groups-proxy/questions/v2/membership-questions/{groupId}",
                "wix-safe-agent-cli community-membership-questions list",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        self.assertIn(
            "ack-irreversible",
            by_id["communityMembershipQuestions.createOrReplaceAllMembershipQuestions"]["flags"],
        )

    def test_community_comments_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-comments", families)
        family = families["community-comments"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 28)
        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityComments.createComment": ("POST", "/comments/v1/comments", "wix-safe-agent-cli community-comments create"),
            "communityComments.getComment": (
                "GET",
                "/comments/v1/comments/{commentId}",
                "wix-safe-agent-cli community-comments get",
            ),
            "communityComments.updateComment": (
                "PATCH",
                "/comments/v1/comments/{comment.id}",
                "wix-safe-agent-cli community-comments update",
            ),
            "communityComments.deleteComment": (
                "DELETE",
                "/comments/v1/comments/{commentId}",
                "wix-safe-agent-cli community-comments delete",
            ),
            "communityComments.moderateDraftContent": (
                "POST",
                "/comments/v1/comments/{commentId}/moderate",
                "wix-safe-agent-cli community-comments moderate-draft-content",
            ),
            "communityComments.queryComments": (
                "POST",
                "/comments/v1/comments/query-cursor",
                "wix-safe-agent-cli community-comments query",
            ),
            "communityComments.markComment": (
                "PUT",
                "/comments/v1/comments/{commentId}/mark",
                "wix-safe-agent-cli community-comments mark",
            ),
            "communityComments.unmarkComment": (
                "PUT",
                "/comments/v1/comments/{commentId}/unmark",
                "wix-safe-agent-cli community-comments unmark",
            ),
            "communityComments.hideComment": (
                "PUT",
                "/comments/v1/comments/{commentId}/hide",
                "wix-safe-agent-cli community-comments hide",
            ),
            "communityComments.publishComment": (
                "PUT",
                "/comments/v1/comments/{commentId}/publish",
                "wix-safe-agent-cli community-comments publish",
            ),
            "communityComments.countComments": (
                "POST",
                "/comments/v1/comments/count",
                "wix-safe-agent-cli community-comments count",
            ),
            "communityComments.listCommentsByResource": (
                "GET",
                "/comments/v1/comments/list-by-resource",
                "wix-safe-agent-cli community-comments list-by-resource",
            ),
            "communityComments.getCommentThread": (
                "GET",
                "/comments/v1/comments/{commentId}/thread",
                "wix-safe-agent-cli community-comments get-thread",
            ),
            "communityComments.bulkPublishComment": (
                "POST",
                "/comments/v1/bulk/comments/publish-by-filter",
                "wix-safe-agent-cli community-comments bulk-publish",
            ),
            "communityComments.bulkHideComment": (
                "PUT",
                "/comments/v1/bulk/comments/hide-by-filter",
                "wix-safe-agent-cli community-comments bulk-hide",
            ),
            "communityComments.bulkDeleteComment": (
                "PUT",
                "/comments/v1/bulk/comments/delete-by-filter",
                "wix-safe-agent-cli community-comments bulk-delete",
            ),
            "communityComments.bulkModerateDraftContent": (
                "POST",
                "/comments/v1/bulk/comments/moderate-by-filter",
                "wix-safe-agent-cli community-comments bulk-moderate-draft-content",
            ),
            "communityComments.bulkMoveCommentByFilter": (
                "PUT",
                "/comments/v1/bulk/comments/move-by-filter",
                "wix-safe-agent-cli community-comments bulk-move-by-filter",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        for method_id in (
            "communityComments.deleteComment",
            "communityComments.moderateDraftContent",
            "communityComments.markComment",
            "communityComments.unmarkComment",
            "communityComments.hideComment",
            "communityComments.publishComment",
            "communityComments.bulkPublishComment",
            "communityComments.bulkHideComment",
            "communityComments.bulkDeleteComment",
            "communityComments.bulkModerateDraftContent",
            "communityComments.bulkMoveCommentByFilter",
        ):
            self.assertIn("ack-irreversible", by_id[method_id]["flags"])
        for method_id in (
            "communityComments.commentDeleted",
            "communityComments.commentContentChanged",
            "communityComments.commentHidden",
            "communityComments.commentMarked",
            "communityComments.commentMoved",
            "communityComments.commentPublished",
            "communityComments.commentUnmarked",
            "communityComments.commentCreated",
            "communityComments.resourceCommentCountChanged",
            "communityComments.commentUpdated",
        ):
            self.assertFalse(by_id[method_id]["cli_callable"])
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_community_reports_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-reports", families)
        family = families["community-reports"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 12)
        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityReports.createReport": ("POST", "/reports/v2/reports", "wix-safe-agent-cli community-reports create"),
            "communityReports.getReport": ("GET", "/reports/v2/reports/{reportId}", "wix-safe-agent-cli community-reports get"),
            "communityReports.updateReport": (
                "PATCH",
                "/reports/v2/reports/{report.id}",
                "wix-safe-agent-cli community-reports update",
            ),
            "communityReports.deleteReport": (
                "DELETE",
                "/reports/v2/reports/{reportId}",
                "wix-safe-agent-cli community-reports delete",
            ),
            "communityReports.queryReports": (
                "POST",
                "/reports/v2/reports/query",
                "wix-safe-agent-cli community-reports query",
            ),
            "communityReports.bulkDeleteReportsByFilter": (
                "POST",
                "/reports/v2/reports/bulk/delete-by-filter",
                "wix-safe-agent-cli community-reports bulk-delete-by-filter",
            ),
            "communityReports.countReportsByReasonTypes": (
                "POST",
                "/reports/v2/reports/reason-types/count",
                "wix-safe-agent-cli community-reports count-by-reason-types",
            ),
            "communityReports.upsertReport": (
                "POST",
                "/reports/v2/reports/upsert/entity-name/{report.entityName}/entity-id/{report.entityId}",
                "wix-safe-agent-cli community-reports upsert",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        self.assertIn("ack-irreversible", by_id["communityReports.deleteReport"]["flags"])
        self.assertIn("ack-irreversible", by_id["communityReports.bulkDeleteReportsByFilter"]["flags"])
        for method_id in (
            "communityReports.reportCreated",
            "communityReports.reportDeleted",
            "communityReports.entityReportSummaryChanged",
            "communityReports.reportUpdated",
        ):
            self.assertFalse(by_id[method_id]["cli_callable"])
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_community_reviews_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-reviews", families)
        family = families["community-reviews"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 17)
        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityReviews.getReview": (
                "GET",
                "/reviews/v1/reviews/{reviewId}",
                "wix-safe-agent-cli community-reviews get",
            ),
            "communityReviews.deleteReview": (
                "DELETE",
                "/reviews/v1/reviews/{reviewId}",
                "wix-safe-agent-cli community-reviews delete",
            ),
            "communityReviews.createReview": (
                "POST",
                "/reviews/v1/reviews",
                "wix-safe-agent-cli community-reviews create",
            ),
            "communityReviews.bulkCreateReview": (
                "POST",
                "/reviews/v1/bulk/reviews/create",
                "wix-safe-agent-cli community-reviews bulk-create",
            ),
            "communityReviews.updateReview": (
                "PATCH",
                "/reviews/v1/reviews/{review.id}",
                "wix-safe-agent-cli community-reviews update",
            ),
            "communityReviews.bulkDeleteReviews": (
                "POST",
                "/reviews/v1/bulk/reviews/delete",
                "wix-safe-agent-cli community-reviews bulk-delete",
            ),
            "communityReviews.queryReviews": (
                "POST",
                "/reviews/v1/reviews/query",
                "wix-safe-agent-cli community-reviews query",
            ),
            "communityReviews.removeReply": (
                "DELETE",
                "/reviews/v1/reviews/{reviewId}/reply",
                "wix-safe-agent-cli community-reviews remove-reply",
            ),
            "communityReviews.setReply": (
                "PATCH",
                "/reviews/v1/reviews/{reviewId}/reply",
                "wix-safe-agent-cli community-reviews set-reply",
            ),
            "communityReviews.updateModerationStatus": (
                "PATCH",
                "/reviews/v1/reviews/{reviewId}/moderate",
                "wix-safe-agent-cli community-reviews update-moderation-status",
            ),
            "communityReviews.bulkUpdateModerationStatus": (
                "POST",
                "/reviews/v1/bulk/reviews/moderate",
                "wix-safe-agent-cli community-reviews bulk-update-moderation-status",
            ),
            "communityReviews.countReviews": (
                "POST",
                "/reviews/v1/reviews/count",
                "wix-safe-agent-cli community-reviews count",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        for method_id in (
            "communityReviews.deleteReview",
            "communityReviews.bulkCreateReview",
            "communityReviews.bulkDeleteReviews",
            "communityReviews.removeReply",
            "communityReviews.updateModerationStatus",
            "communityReviews.bulkUpdateModerationStatus",
        ):
            self.assertIn("ack-irreversible", by_id[method_id]["flags"])
        for method_id in (
            "communityReviews.reviewCreated",
            "communityReviews.reviewDeleted",
            "communityReviews.reviewModerationStatusChanged",
            "communityReviews.reviewPublished",
            "communityReviews.reviewUpdated",
        ):
            self.assertFalse(by_id[method_id]["cli_callable"])
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_community_review_requests_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-review-requests", families)
        family = families["community-review-requests"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)
        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityReviewRequests.createReviewRequest": (
                "POST",
                "/reviews/v2/review-requests",
                "wix-safe-agent-cli community-review-requests create",
            ),
            "communityReviewRequests.getReviewRequest": (
                "GET",
                "/reviews/v2/review-requests/{reviewRequestId}",
                "wix-safe-agent-cli community-review-requests get",
            ),
            "communityReviewRequests.deleteReviewRequest": (
                "DELETE",
                "/reviews/v2/review-requests/{reviewRequestId}",
                "wix-safe-agent-cli community-review-requests delete",
            ),
            "communityReviewRequests.queryReviewRequests": (
                "POST",
                "/reviews/v2/review-requests/query",
                "wix-safe-agent-cli community-review-requests query",
            ),
            "communityReviewRequests.countReviewRequests": (
                "POST",
                "/reviews/v2/review-requests/count",
                "wix-safe-agent-cli community-review-requests count",
            ),
            "communityReviewRequests.bulkCancelReviewRequestsByFilter": (
                "PUT",
                "/reviews/v2/bulk/review-requests/cancel-by-filter",
                "wix-safe-agent-cli community-review-requests bulk-cancel-by-filter",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        self.assertIn("ack-irreversible", by_id["communityReviewRequests.deleteReviewRequest"]["flags"])
        self.assertIn("ack-irreversible", by_id["communityReviewRequests.bulkCancelReviewRequestsByFilter"]["flags"])
        for method_id in (
            "communityReviewRequests.reviewRequestCreated",
            "communityReviewRequests.reviewRequestDeleted",
            "communityReviewRequests.reviewRequestUpdated",
        ):
            self.assertFalse(by_id[method_id]["cli_callable"])
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_community_moderation_rules_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("community-moderation-rules", families)
        family = families["community-moderation-rules"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)
        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "communityModerationRules.createRule": ("POST", "/moderation/v1/rules", "wix-safe-agent-cli community-moderation-rules create"),
            "communityModerationRules.getRule": ("GET", "/moderation/v1/rules/{ruleId}", "wix-safe-agent-cli community-moderation-rules get"),
            "communityModerationRules.updateRule": (
                "PATCH",
                "/moderation/v1/rules/{rule.id}",
                "wix-safe-agent-cli community-moderation-rules update",
            ),
            "communityModerationRules.deleteRule": (
                "DELETE",
                "/moderation/v1/rules/{ruleId}",
                "wix-safe-agent-cli community-moderation-rules delete",
            ),
            "communityModerationRules.queryRules": (
                "POST",
                "/moderation/v1/rules/query",
                "wix-safe-agent-cli community-moderation-rules query",
            ),
            "communityModerationRules.checkContent": (
                "POST",
                "/moderation/v1/rules/check",
                "wix-safe-agent-cli community-moderation-rules check-content",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        for method_id in (
            "communityModerationRules.createRule",
            "communityModerationRules.updateRule",
            "communityModerationRules.deleteRule",
        ):
            self.assertIn("ack-irreversible", by_id[method_id]["flags"])
        for method_id in (
            "communityModerationRules.ruleCreated",
            "communityModerationRules.ruleDeleted",
            "communityModerationRules.ruleUpdated",
        ):
            self.assertFalse(by_id[method_id]["cli_callable"])
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_inbox_conversations_and_messages_families_present(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("inbox-conversations", families)
        conversations = {op.get("method_id"): op for op in families["inbox-conversations"].get("operations", [])}
        self.assertEqual(len(conversations), 3)
        self.assertEqual(conversations["inboxConversations.getConversation"]["http_method"], "GET")
        self.assertEqual(conversations["inboxConversations.getConversation"]["path"], "/inbox/v2/conversations/{conversationId}")
        self.assertEqual(
            conversations["inboxConversations.getConversation"]["planned_command"],
            "wix-safe-agent-cli inbox-conversations get",
        )
        self.assertEqual(conversations["inboxConversations.getOrCreateConversation"]["http_method"], "POST")
        self.assertEqual(conversations["inboxConversations.getOrCreateConversation"]["path"], "/inbox/v2/conversations")
        self.assertEqual(
            conversations["inboxConversations.getOrCreateConversation"]["planned_command"],
            "wix-safe-agent-cli inbox-conversations get-or-create",
        )
        self.assertFalse(conversations["inboxConversations.conversationsMerged"]["cli_callable"])
        self.assertIn("callback-only", conversations["inboxConversations.conversationsMerged"]["flags"])

        self.assertIn("inbox-messages", families)
        messages = {op.get("method_id"): op for op in families["inbox-messages"].get("operations", [])}
        self.assertEqual(len(messages), 5)
        self.assertEqual(messages["inboxMessages.listMessages"]["http_method"], "GET")
        self.assertEqual(messages["inboxMessages.listMessages"]["path"], "/inbox/v2/messages")
        self.assertEqual(messages["inboxMessages.listMessages"]["planned_command"], "wix-safe-agent-cli inbox-messages list")
        self.assertEqual(messages["inboxMessages.sendMessage"]["http_method"], "POST")
        self.assertEqual(messages["inboxMessages.sendMessage"]["path"], "/inbox/v2/messages")
        self.assertEqual(messages["inboxMessages.sendMessage"]["planned_command"], "wix-safe-agent-cli inbox-messages send")
        self.assertIn("ack-irreversible", messages["inboxMessages.sendMessage"]["flags"])
        for method_id in (
            "inboxMessages.buttonInteracted",
            "inboxMessages.messageSentToBusiness",
            "inboxMessages.messageSentToParticipant",
        ):
            self.assertFalse(messages[method_id]["cli_callable"])
            self.assertIn("callback-only", messages[method_id]["flags"])

    def test_loyalty_program_family_present_and_event_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("loyalty-program", families)
        operations = families["loyalty-program"].get("operations", [])
        self.assertEqual(len(operations), 8)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "loyaltyProgram.getLoyaltyProgram": (
                "GET",
                "/loyalty-programs/v1/program",
                "wix-safe-agent-cli loyalty-program get",
            ),
            "loyaltyProgram.getLoyaltyProgramPremiumFeatures": (
                "GET",
                "/loyalty-programs/v1/program/premium-features",
                "wix-safe-agent-cli loyalty-program premium-features",
            ),
            "loyaltyProgram.updateLoyaltyProgram": (
                "PATCH",
                "/loyalty-programs/v1/program",
                "wix-safe-agent-cli loyalty-program update",
            ),
            "loyaltyProgram.activateLoyaltyProgram": (
                "POST",
                "/loyalty-programs/v1/program/activate",
                "wix-safe-agent-cli loyalty-program activate",
            ),
            "loyaltyProgram.pauseLoyaltyProgram": (
                "POST",
                "/loyalty-programs/v1/program/pause",
                "wix-safe-agent-cli loyalty-program pause",
            ),
            "loyaltyProgram.enablePointsExpiration": (
                "POST",
                "/loyalty-programs/v1/program/points-expiration/enable",
                "wix-safe-agent-cli loyalty-program enable-points-expiration",
            ),
            "loyaltyProgram.disablePointsExpiration": (
                "POST",
                "/loyalty-programs/v1/program/points-expiration/disable",
                "wix-safe-agent-cli loyalty-program disable-points-expiration",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        for method_id in (
            "loyaltyProgram.updateLoyaltyProgram",
            "loyaltyProgram.activateLoyaltyProgram",
            "loyaltyProgram.pauseLoyaltyProgram",
            "loyaltyProgram.enablePointsExpiration",
            "loyaltyProgram.disablePointsExpiration",
        ):
            self.assertIn("ack-irreversible", by_id[method_id]["flags"])
        self.assertFalse(by_id["loyaltyProgram.loyaltyProgramUpdated"]["cli_callable"])
        self.assertIn("callback-only", by_id["loyaltyProgram.loyaltyProgramUpdated"]["flags"])

    def test_loyalty_earning_rules_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("loyalty-earning-rules", families)
        operations = families["loyalty-earning-rules"].get("operations", [])
        self.assertEqual(len(operations), 11)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "loyaltyEarningRules.listEarningRules": (
                "GET",
                "/_api/loyalty-earning-rules/v1/earning-rules/rules",
                "wix-safe-agent-cli loyalty-earning-rules list",
            ),
            "loyaltyEarningRules.getLoyaltyEarningRule": (
                "GET",
                "/_api/loyalty-earning-rules/v1/earning-rules/{id}",
                "wix-safe-agent-cli loyalty-earning-rules get",
            ),
            "loyaltyEarningRules.createLoyaltyEarningRule": (
                "POST",
                "/_api/loyalty-earning-rules/v1/earning-rules",
                "wix-safe-agent-cli loyalty-earning-rules create",
            ),
            "loyaltyEarningRules.updateLoyaltyEarningRule": (
                "PUT",
                "/_api/loyalty-earning-rules/v1/earning-rules/{earningRule.id}",
                "wix-safe-agent-cli loyalty-earning-rules update",
            ),
            "loyaltyEarningRules.deleteLoyaltyEarningRule": (
                "DELETE",
                "/_api/loyalty-earning-rules/v1/earning-rules/{id}?revision={revision}",
                "wix-safe-agent-cli loyalty-earning-rules delete",
            ),
            "loyaltyEarningRules.bulkCreateLoyaltyEarningRules": (
                "POST",
                "/_api/loyalty-earning-rules/v1/bulk/earning-rules/create",
                "wix-safe-agent-cli loyalty-earning-rules bulk-create",
            ),
            "loyaltyEarningRules.createCustomLoyaltyEarningRule": (
                "POST",
                "/_api/loyalty-earning-rules/v1/earning-rules/custom",
                "wix-safe-agent-cli loyalty-earning-rules create-custom",
            ),
            "loyaltyEarningRules.deleteAutomationEarningRule": (
                "DELETE",
                "/_api/loyalty-earning-rules/v1/automation-earning-rules/{id}",
                "wix-safe-agent-cli loyalty-earning-rules delete-automation",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        for method_id in (
            "loyaltyEarningRules.createLoyaltyEarningRule",
            "loyaltyEarningRules.updateLoyaltyEarningRule",
            "loyaltyEarningRules.deleteLoyaltyEarningRule",
            "loyaltyEarningRules.bulkCreateLoyaltyEarningRules",
            "loyaltyEarningRules.createCustomLoyaltyEarningRule",
            "loyaltyEarningRules.deleteAutomationEarningRule",
        ):
            self.assertIn("ack-irreversible", by_id[method_id]["flags"])
        for method_id in (
            "loyaltyEarningRules.loyaltyEarningRuleCreated",
            "loyaltyEarningRules.loyaltyEarningRuleUpdated",
            "loyaltyEarningRules.loyaltyEarningRuleDeleted",
        ):
            self.assertFalse(by_id[method_id]["cli_callable"])
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_loyalty_tiers_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("loyalty-tiers", families)
        operations = families["loyalty-tiers"].get("operations", [])
        self.assertEqual(len(operations), 13)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "loyaltyTiers.listTiers": (
                "GET",
                "/loyalty-tiers/v1/tiers",
                "wix-safe-agent-cli loyalty-tiers list",
            ),
            "loyaltyTiers.getTier": (
                "GET",
                "/loyalty-tiers/v1/tiers/{tierId}",
                "wix-safe-agent-cli loyalty-tiers get",
            ),
            "loyaltyTiers.createTier": (
                "POST",
                "/loyalty-tiers/v1/tiers",
                "wix-safe-agent-cli loyalty-tiers create",
            ),
            "loyaltyTiers.updateTier": (
                "PATCH",
                "/loyalty-tiers/v1/tiers/{tier.id}",
                "wix-safe-agent-cli loyalty-tiers update",
            ),
            "loyaltyTiers.deleteTier": (
                "DELETE",
                "/loyalty-tiers/v1/tiers/{tierId}?revision={revision}",
                "wix-safe-agent-cli loyalty-tiers delete",
            ),
            "loyaltyTiers.bulkCreateTiers": (
                "POST",
                "/loyalty-tiers/v1/bulk/tiers/create",
                "wix-safe-agent-cli loyalty-tiers bulk-create",
            ),
            "loyaltyTiers.getTiersProgram": (
                "GET",
                "/loyalty-tiers/v1/tiers/program",
                "wix-safe-agent-cli loyalty-tiers get-program",
            ),
            "loyaltyTiers.createTiersProgramSettings": (
                "POST",
                "/loyalty-tiers/v1/tiers/program-settings",
                "wix-safe-agent-cli loyalty-tiers create-program-settings",
            ),
            "loyaltyTiers.getTiersProgramSettings": (
                "GET",
                "/loyalty-tiers/v1/tiers/program-settings",
                "wix-safe-agent-cli loyalty-tiers get-program-settings",
            ),
            "loyaltyTiers.updateTiersProgramSettings": (
                "PATCH",
                "/loyalty-tiers/v1/tiers/program-settings",
                "wix-safe-agent-cli loyalty-tiers update-program-settings",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        for method_id in (
            "loyaltyTiers.createTier",
            "loyaltyTiers.updateTier",
            "loyaltyTiers.deleteTier",
            "loyaltyTiers.bulkCreateTiers",
            "loyaltyTiers.getTiersProgram",
            "loyaltyTiers.createTiersProgramSettings",
            "loyaltyTiers.updateTiersProgramSettings",
        ):
            self.assertIn("ack-irreversible", by_id[method_id]["flags"])
        for method_id in (
            "loyaltyTiers.tierCreated",
            "loyaltyTiers.tierUpdated",
            "loyaltyTiers.tierDeleted",
        ):
            self.assertFalse(by_id[method_id]["cli_callable"])
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_loyalty_accounts_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("loyalty-accounts", families)
        operations = families["loyalty-accounts"].get("operations", [])
        self.assertEqual(len(operations), 16)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "loyaltyAccounts.listAccounts": (
                "GET",
                "/loyalty-accounts/v1/accounts",
                "wix-safe-agent-cli loyalty-accounts list",
            ),
            "loyaltyAccounts.getAccount": (
                "GET",
                "/loyalty-accounts/v1/accounts/{id}",
                "wix-safe-agent-cli loyalty-accounts get",
            ),
            "loyaltyAccounts.queryLoyaltyAccounts": (
                "POST",
                "/loyalty-accounts/v1/accounts/query",
                "wix-safe-agent-cli loyalty-accounts query",
            ),
            "loyaltyAccounts.searchAccounts": (
                "POST",
                "/loyalty-accounts/v1/accounts/search",
                "wix-safe-agent-cli loyalty-accounts search",
            ),
            "loyaltyAccounts.countAccounts": (
                "POST",
                "/loyalty-accounts/v1/accounts/count",
                "wix-safe-agent-cli loyalty-accounts count",
            ),
            "loyaltyAccounts.getProgramTotals": (
                "GET",
                "/loyalty-accounts/v1/accounts/program-totals",
                "wix-safe-agent-cli loyalty-accounts get-program-totals",
            ),
            "loyaltyAccounts.getCurrentMemberAccount": (
                "GET",
                "/loyalty-accounts/v1/accounts/my-account",
                "wix-safe-agent-cli loyalty-accounts get-current-member-account",
            ),
            "loyaltyAccounts.getAccountBySecondaryId": (
                "GET",
                "/loyalty-accounts/v1/accounts/fetch-by",
                "wix-safe-agent-cli loyalty-accounts get-by-secondary-id",
            ),
            "loyaltyAccounts.createAccount": (
                "POST",
                "/loyalty-accounts/v1/accounts",
                "wix-safe-agent-cli loyalty-accounts create",
            ),
            "loyaltyAccounts.adjustPoints": (
                "POST",
                "/loyalty-accounts/v1/accounts/{accountId}/adjust-points",
                "wix-safe-agent-cli loyalty-accounts adjust-points",
            ),
            "loyaltyAccounts.bulkAdjustPoints": (
                "POST",
                "/loyalty-accounts/v1/accounts/bulk-adjust",
                "wix-safe-agent-cli loyalty-accounts bulk-adjust-points",
            ),
            "loyaltyAccounts.earnPoints": (
                "POST",
                "/loyalty-accounts/v1/accounts/{accountId}/earn-points",
                "wix-safe-agent-cli loyalty-accounts earn-points",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
        for method_id in (
            "loyaltyAccounts.createAccount",
            "loyaltyAccounts.adjustPoints",
            "loyaltyAccounts.bulkAdjustPoints",
            "loyaltyAccounts.earnPoints",
        ):
            self.assertIn("ack-irreversible", by_id[method_id]["flags"])
        self.assertIn("deprecated", by_id["loyaltyAccounts.listAccounts"]["flags"])
        for method_id in (
            "loyaltyAccounts.loyaltyAccountCreated",
            "loyaltyAccounts.pointsUpdated",
            "loyaltyAccounts.accountRewardAvailabilityUpdated",
            "loyaltyAccounts.loyaltyAccountUpdated",
        ):
            self.assertFalse(by_id[method_id]["cli_callable"])
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_loyalty_rewards_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("loyalty-rewards", families)
        operations = families["loyalty-rewards"].get("operations", [])
        self.assertEqual(len(operations), 10)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "loyaltyRewards.listRewards": (
                "GET",
                "/loyalty-rewards/v1/rewards",
                "wix-safe-agent-cli loyalty-rewards list",
            ),
            "loyaltyRewards.getReward": (
                "GET",
                "/loyalty-rewards/v1/rewards/{id}",
                "wix-safe-agent-cli loyalty-rewards get",
            ),
            "loyaltyRewards.queryRewards": (
                "POST",
                "/loyalty-rewards/v1/rewards/query",
                "wix-safe-agent-cli loyalty-rewards query",
            ),
            "loyaltyRewards.createReward": (
                "POST",
                "/loyalty-rewards/v1/rewards",
                "wix-safe-agent-cli loyalty-rewards create",
            ),
            "loyaltyRewards.bulkCreateRewards": (
                "POST",
                "/loyalty-rewards/v1/bulk/rewards/create",
                "wix-safe-agent-cli loyalty-rewards bulk-create",
            ),
            "loyaltyRewards.updateReward": (
                "PUT",
                "/loyalty-rewards/v1/rewards/{reward.id}",
                "wix-safe-agent-cli loyalty-rewards update",
            ),
            "loyaltyRewards.deleteReward": (
                "DELETE",
                "/loyalty-rewards/v1/rewards/{id}",
                "wix-safe-agent-cli loyalty-rewards delete",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
        for method_id in (
            "loyaltyRewards.createReward",
            "loyaltyRewards.bulkCreateRewards",
            "loyaltyRewards.updateReward",
            "loyaltyRewards.deleteReward",
        ):
            self.assertIn("ack-irreversible", by_id[method_id]["flags"])
        for method_id in (
            "loyaltyRewards.rewardCreated",
            "loyaltyRewards.rewardDeleted",
            "loyaltyRewards.rewardUpdated",
        ):
            self.assertFalse(by_id[method_id]["cli_callable"])
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_loyalty_transactions_family_present_and_read_only(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("loyalty-transactions", families)
        operations = families["loyalty-transactions"].get("operations", [])
        self.assertEqual(len(operations), 2)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "loyaltyTransactions.getLoyaltyTransaction": (
                "GET",
                "/loyalty-transactions/v1/loyalty-transactions/{loyaltyTransactionId}",
                "wix-safe-agent-cli loyalty-transactions get",
            ),
            "loyaltyTransactions.queryLoyaltyTransactions": (
                "POST",
                "/loyalty-transactions/v1/loyalty-transactions/query",
                "wix-safe-agent-cli loyalty-transactions query",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertNotIn("ack-irreversible", by_id[method_id]["flags"])

    def test_loyalty_social_media_family_present_and_callback_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("loyalty-social-media", families)
        operations = families["loyalty-social-media"].get("operations", [])
        self.assertEqual(len(operations), 3)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "loyaltySocialMedia.createFollowedChannel": (
                "POST",
                "/loyalty-social-media/v1/followed-channels",
                "wix-safe-agent-cli loyalty-social-media create",
            ),
            "loyaltySocialMedia.listFollowedChannels": (
                "GET",
                "/loyalty-social-media/v1/followed-channels",
                "wix-safe-agent-cli loyalty-social-media list",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("requires-visitor-or-member-auth", by_id[method_id]["flags"])

        self.assertIn("ack-irreversible", by_id["loyaltySocialMedia.createFollowedChannel"]["flags"])
        self.assertFalse(by_id["loyaltySocialMedia.followedChannelCreated"]["cli_callable"])
        self.assertIn("callback-only", by_id["loyaltySocialMedia.followedChannelCreated"]["flags"])

    def test_loyalty_imports_family_present_and_callback_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("loyalty-imports", families)
        operations = families["loyalty-imports"].get("operations", [])
        self.assertEqual(len(operations), 7)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "loyaltyImports.getLoyaltyImport": (
                "GET",
                "/_api/loyalty-imports/v1/loyalty-imports",
                "wix-safe-agent-cli loyalty-imports get",
            ),
            "loyaltyImports.queryLoyaltyImports": (
                "POST",
                "/_api/loyalty-imports/v1/loyalty-imports/query",
                "wix-safe-agent-cli loyalty-imports query",
            ),
            "loyaltyImports.createLoyaltyImportFileUrl": (
                "POST",
                "/_api/loyalty-imports/v1/loyalty-imports/wixmp-upload-url",
                "wix-safe-agent-cli loyalty-imports create-file-url",
            ),
            "loyaltyImports.createLoyaltyImport": (
                "POST",
                "/_api/loyalty-imports/v1/loyalty-imports",
                "wix-safe-agent-cli loyalty-imports create",
            ),
            "loyaltyImports.executeLoyaltyImport": (
                "POST",
                "/_api/loyalty-imports/v1/loyalty-imports/execute",
                "wix-safe-agent-cli loyalty-imports execute",
            ),
            "loyaltyImports.getErrorFileDownloadUrl": (
                "GET",
                "/_api/loyalty-imports/v1/loyalty-imports/error-file-download-url",
                "wix-safe-agent-cli loyalty-imports get-error-file-download-url",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])

        self.assertIn("plan-first-write", by_id["loyaltyImports.createLoyaltyImportFileUrl"]["flags"])
        self.assertNotIn("ack-irreversible", by_id["loyaltyImports.createLoyaltyImportFileUrl"]["flags"])
        self.assertIn("ack-irreversible", by_id["loyaltyImports.createLoyaltyImport"]["flags"])
        self.assertIn("ack-irreversible", by_id["loyaltyImports.executeLoyaltyImport"]["flags"])
        self.assertFalse(by_id["loyaltyImports.loyaltyImportCreated"]["cli_callable"])
        self.assertIn("callback-only", by_id["loyaltyImports.loyaltyImportCreated"]["flags"])

    def test_loyalty_checkout_discounts_family_present_and_ack_gated(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("loyalty-checkout-discounts", families)
        operations = families["loyalty-checkout-discounts"].get("operations", [])
        self.assertEqual(len(operations), 2)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "loyaltyCheckoutDiscounts.queryLoyaltyCheckoutDiscounts": (
                "POST",
                "/loyalty-checkout-exchange/v1/loyalty-checkout-discounts/query",
                "wix-safe-agent-cli loyalty-checkout-discounts query",
            ),
            "loyaltyCheckoutDiscounts.applyDiscountToCheckout": (
                "POST",
                "/loyalty-checkout-exchange/v1/loyalty-checkout-discount",
                "wix-safe-agent-cli loyalty-checkout-discounts apply",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])

        self.assertIn("ack-irreversible", by_id["loyaltyCheckoutDiscounts.applyDiscountToCheckout"]["flags"])

    def test_loyalty_coupons_family_present_and_events_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("loyalty-coupons", families)
        operations = families["loyalty-coupons"].get("operations", [])
        self.assertEqual(len(operations), 8)

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "loyaltyCoupons.getLoyaltyCoupon": (
                "GET",
                "/loyalty-coupons/v1/coupons/{loyaltyCouponId}",
                "wix-safe-agent-cli loyalty-coupons get",
            ),
            "loyaltyCoupons.queryLoyaltyCoupon": (
                "POST",
                "/loyalty-coupons/v1/coupons/query",
                "wix-safe-agent-cli loyalty-coupons query",
            ),
            "loyaltyCoupons.getCurrentMemberCoupons": (
                "GET",
                "/loyalty-coupons/v1/coupons/my-coupons",
                "wix-safe-agent-cli loyalty-coupons get-current-member",
            ),
            "loyaltyCoupons.redeemCurrentMemberPointsForCoupon": (
                "POST",
                "/loyalty-coupons/v1/coupons/redeem-my-coupon",
                "wix-safe-agent-cli loyalty-coupons redeem-current-member",
            ),
            "loyaltyCoupons.redeemPointsForCoupon": (
                "POST",
                "/loyalty-coupons/v1/coupons",
                "wix-safe-agent-cli loyalty-coupons redeem",
            ),
            "loyaltyCoupons.deleteLoyaltyCoupon": (
                "DELETE",
                "/loyalty-coupons/v1/coupons/{id}",
                "wix-safe-agent-cli loyalty-coupons delete",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id]["http_method"], http_method)
                self.assertEqual(by_id[method_id]["path"], path)
                self.assertEqual(by_id[method_id]["planned_command"], planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])

        for method_id in (
            "loyaltyCoupons.redeemCurrentMemberPointsForCoupon",
            "loyaltyCoupons.redeemPointsForCoupon",
            "loyaltyCoupons.deleteLoyaltyCoupon",
        ):
            self.assertIn("ack-irreversible", by_id[method_id]["flags"])

        for method_id in ("loyaltyCoupons.couponCreated", "loyaltyCoupons.couponDeleted"):
            self.assertFalse(by_id[method_id]["cli_callable"])
            self.assertIn("callback-only", by_id[method_id]["flags"])

    def test_email_subscriptions_family_present_and_callback_event_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("email-subscriptions", families)
        family = families["email-subscriptions"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 5)
        self.assertIn("developer-preview", family.get("default_flags", []))

        by_id = {op.get("method_id"): op for op in operations}
        expected_commands = {
            "emailSubscriptions.queryEmailSubscriptions": (
                "POST",
                "/email-marketing/v1/email-subscriptions/query",
                "wix-safe-agent-cli email-subscriptions query",
            ),
            "emailSubscriptions.upsertEmailSubscription": (
                "POST",
                "/email-marketing/v1/email-subscriptions",
                "wix-safe-agent-cli email-subscriptions upsert",
            ),
            "emailSubscriptions.bulkUpsertEmailSubscription": (
                "POST",
                "/email-marketing/v1/email-subscriptions/bulk",
                "wix-safe-agent-cli email-subscriptions bulk-upsert",
            ),
            "emailSubscriptions.generateUnsubscribeLink": (
                "POST",
                "/email-marketing/v1/email-subscriptions/unsubscribe-link",
                "wix-safe-agent-cli email-subscriptions generate-unsubscribe-link",
            ),
        }
        for method_id, (http_method, path, command) in expected_commands.items():
            with self.subTest(method_id=method_id):
                op = by_id[method_id]
                self.assertEqual(op.get("http_method"), http_method)
                self.assertEqual(op.get("path"), path)
                self.assertEqual(op.get("planned_command"), command)
                self.assertIn("implemented", op["flags"])
                self.assertIn("developer-preview", op["flags"])
                self.assertTrue(op.get("cli_callable"))

        event = by_id["emailSubscriptions.emailSubscriptionChanged"]
        self.assertIsNone(event.get("http_method"))
        self.assertIsNone(event.get("path"))
        self.assertIsNone(event.get("planned_command"))
        self.assertIn("callback-only", event["flags"])
        self.assertFalse(event.get("cli_callable"))

    def test_app_permissions_family_uses_current_official_list_slug(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("app-permissions", families)
        family = families["app-permissions"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/app-management/app-permissions/list-app-permissions",
            family.get("source_urls", []),
        )

        ops = {op["method_id"]: op for op in family.get("operations", [])}
        self.assertEqual(
            ops["apps.getAppPermissions"]["doc_url"],
            "https://dev.wix.com/docs/api-reference/app-management/app-permissions/list-app-permissions",
        )

    def test_notifications_family_uses_current_official_notify_slug(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("notifications", families)
        family = families["notifications"]
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/business-management/notifications/notifications/notify",
            family.get("source_urls", []),
        )

        ops = {op["method_id"]: op for op in family.get("operations", [])}
        self.assertEqual(
            ops["notifications.notify"]["doc_url"],
            "https://dev.wix.com/docs/api-reference/business-management/notifications/notifications/notify",
        )

    def test_wix_skills_media_skills_is_docs_only_and_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("wix-skills-media-skills", families)
        family = families["wix-skills-media-skills"]
        self.assertIn("docs-only", family.get("default_flags", []))
        self.assertIn("non-callable", family.get("default_flags", []))
        operation = family.get("operations", [])[0]
        self.assertEqual(operation.get("method_id"), "wixSkills.mediaSkillsDocs")
        self.assertIsNone(operation.get("planned_command"))
        self.assertIsNone(operation.get("http_method"))
        self.assertIsNone(operation.get("path"))
        self.assertIn("docs-only", operation.get("flags", []))
        self.assertFalse(operation.get("cli_callable"))

    def test_sites_skills_is_docs_only_and_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("sites-skills", families)
        family = families["sites-skills"]
        self.assertEqual(family.get("coverage_status"), "docs-only")
        self.assertIn("docs-only", family.get("default_flags", []))
        self.assertIn("non-callable", family.get("default_flags", []))
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/account-level/sites/skills/query-sites",
            family.get("source_urls", []),
        )
        self.assertIn(
            "https://dev.wix.com/docs/api-reference/account-level/sites/skills/create-site-from-template",
            family.get("source_urls", []),
        )

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        self.assertEqual(set(operations), {"sitesSkills.querySitesRecipe", "sitesSkills.createSiteFromTemplateRecipe"})
        for operation in operations.values():
            self.assertIsNone(operation.get("planned_command"))
            self.assertIsNone(operation.get("http_method"))
            self.assertIsNone(operation.get("path"))
            self.assertIn("docs-only", operation.get("flags", []))
            self.assertIn("non-callable", operation.get("flags", []))
            self.assertFalse(operation.get("cli_callable"))

    def test_domains_skills_is_docs_only_and_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("domains-skills", families)
        family = families["domains-skills"]
        self.assertEqual(family.get("coverage_status"), "docs-only")
        self.assertIn("docs-only", family.get("default_flags", []))
        self.assertIn("non-callable", family.get("default_flags", []))

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)
        operation = operations[0]
        self.assertEqual(operation.get("method_id"), "domainsSkills.domainSearchAndPurchaseRecipe")
        self.assertIsNone(operation.get("planned_command"))
        self.assertIsNone(operation.get("http_method"))
        self.assertIsNone(operation.get("path"))
        self.assertIn("docs-only", operation.get("flags", []))
        self.assertIn("non-callable", operation.get("flags", []))
        self.assertFalse(operation.get("cli_callable"))

    def test_b2b_site_transfer_is_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("b2b-site-transfer", families)
        family = families["b2b-site-transfer"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("account-api-key", family.get("default_flags", []))
        self.assertIn("requires-ack-irreversible", family.get("default_flags", []))

        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)
        operation = operations[0]
        self.assertEqual(operation.get("method_id"), "businessSiteTransfer.transferSite")
        self.assertEqual(operation.get("http_method"), "POST")
        self.assertEqual(operation.get("path"), "/b2b-site-management/v1/transfer-site")
        self.assertEqual(operation.get("planned_command"), "wix-safe-agent-cli b2b-site-transfer transfer")
        self.assertIn("account-api-key", operation.get("flags", []))
        self.assertIn("requires-ack-irreversible", operation.get("flags", []))
        self.assertTrue(operation.get("cli_callable"))

    def test_partner_profiles_are_implemented_with_contact_boundary(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("partner-profiles", families)
        family = families["partner-profiles"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("developer-preview", family.get("default_flags", []))

        operations = {operation.get("method_id"): operation for operation in family.get("operations", [])}
        expected = {
            "partnerProfiles.createPartnerProfile": ("POST", "/partners/profile/v1/partner-profiles", "wix-safe-agent-cli partner-profiles create"),
            "partnerProfiles.updatePartnerProfile": ("PATCH", "/partners/profile/v1/partner-profiles", "wix-safe-agent-cli partner-profiles update"),
            "partnerProfiles.deletePartnerProfile": ("DELETE", "/partners/profile/v1/partner-profiles", "wix-safe-agent-cli partner-profiles delete"),
            "partnerProfiles.getCurrentPartnerProfile": ("GET", "/partners/profile/v1/partner-profiles/current", "wix-safe-agent-cli partner-profiles get-current"),
            "publicPartnerProfiles.getPublicPartnerProfile": ("GET", "/partners/profile/v1/partner-profiles/{partnerId}/public", "wix-safe-agent-cli partner-profiles get-public"),
            "publicPartnerProfiles.findPublicPartnerProfileBySlug": ("GET", "/partners/profile/v1/partner-profiles/slug/{slug}/public", "wix-safe-agent-cli partner-profiles find-public-by-slug"),
        }
        for method_id, (http_method, path, command) in expected.items():
            self.assertIn(method_id, operations)
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))

        contact = operations["partnerProfiles.contactPartner"]
        self.assertIsNone(contact.get("planned_command"))
        self.assertIn("first-party-only", contact.get("flags", []))
        self.assertFalse(contact.get("cli_callable"))

    def test_viewer_cache_and_seo_tags_are_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("viewer-cache-seo-tags", families)
        family = families["viewer-cache-seo-tags"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        operations = {operation.get("method_id"): operation for operation in family.get("operations", [])}
        expected = {
            "viewerCache.invalidateCache": ("POST", "/ssr/v1/invalidate-cache", "wix-safe-agent-cli viewer-cache invalidate"),
            "viewerSeoTags.resolveItemSeoTags": ("GET", "/promote/seo/v1/resolve-item-seo-tags", "wix-safe-agent-cli viewer-seo-tags resolve-item"),
            "viewerSeoTags.resolveStaticPageSeoTags": ("GET", "/promote/seo/v1/resolve-static-page-seo-tags", "wix-safe-agent-cli viewer-seo-tags resolve-static"),
        }
        for method_id, (http_method, path, command) in expected.items():
            self.assertIn(method_id, operations)
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))

    def test_graphql_boundary_is_docs_only_and_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("graphql-boundary", families)
        family = families["graphql-boundary"]
        self.assertEqual(family.get("coverage_status"), "docs-only")
        self.assertIn("no-generic-graphql-bridge", family.get("default_flags", []))
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)
        operation = operations[0]
        self.assertEqual(operation.get("method_id"), "graphql.genericQueryOrMutationEndpoint")
        self.assertIsNone(operation.get("planned_command"))
        self.assertIn("generic-graphql-bridge-forbidden", operation.get("flags", []))
        self.assertFalse(operation.get("cli_callable"))

    def test_async_jobs_generic_runner_boundary_is_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("async-jobs", families)
        operations = {operation.get("method_id"): operation for operation in families["async-jobs"].get("operations", [])}
        self.assertIn("asyncJobs.genericRunnerBoundary", operations)
        boundary = operations["asyncJobs.genericRunnerBoundary"]
        self.assertIsNone(boundary.get("planned_command"))
        self.assertIn("generic-runner-forbidden", boundary.get("flags", []))
        self.assertFalse(boundary.get("cli_callable"))

    def test_resellers_packages_and_product_instances_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("resellers-packages-product-instances", families)
        family = families["resellers-packages-product-instances"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("account-level-api-key", family.get("default_flags", []))
        self.assertIn("plan-first-writes", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "resellers.getPackage": ("GET", "/resellers/v1/packages/{id}", "wix-safe-agent-cli resellers get"),
            "resellers.queryPackages": ("POST", "/resellers/v1/packages/query", "wix-safe-agent-cli resellers query"),
            "resellers.createPackageV2": ("POST", "/resellers/v2/packages", "wix-safe-agent-cli resellers create-package"),
            "resellers.adjustProductInstanceSpecifications": (
                "PATCH",
                "/resellers/v1/packages/product-instances/{instanceId}",
                "wix-safe-agent-cli resellers adjust-product-instance",
            ),
            "resellers.assignProductInstanceToSite": (
                "PATCH",
                "/resellers/v1/packages/product-instances/{instanceId}/{siteId}",
                "wix-safe-agent-cli resellers assign-product-instance",
            ),
            "resellers.unassignProductInstanceFromSite": (
                "PATCH",
                "/resellers/v1/packages/product-instances/{instanceId}/unassign",
                "wix-safe-agent-cli resellers unassign-product-instance",
            ),
            "resellers.updatePackageExternalId": (
                "PATCH",
                "/resellers/v1/packages/update/{packageId}/{externalId}",
                "wix-safe-agent-cli resellers update-package-external-id",
            ),
            "resellers.cancelPackage": ("DELETE", "/resellers/v1/packages/{id}", "wix-safe-agent-cli resellers cancel-package"),
            "resellers.cancelProductInstance": (
                "DELETE",
                "/resellers/v1/packages/product-instances/{instanceId}",
                "wix-safe-agent-cli resellers cancel-product-instance",
            ),
        }
        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))
            self.assertIn("account-level-api-key", operation.get("flags", []))
        self.assertIn("irreversible", operations["resellers.cancelPackage"].get("flags", []))
        self.assertIn("irreversible", operations["resellers.cancelProductInstance"].get("flags", []))

    def test_multilingual_locale_settings_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("multilingual-locale-settings", families)
        family = families["multilingual-locale-settings"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("site-app-auth", family.get("default_flags", []))
        self.assertIn("plan-first-writes", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "multilingualLocaleSettings.getLocaleSettings": (
                "GET",
                "/locale-settings/v2/settings",
                "wix-safe-agent-cli multilingual-locale-settings get",
            ),
            "multilingualLocaleSettings.setMultilingualMode": (
                "POST",
                "/locale-settings/v2/settings/mode",
                "wix-safe-agent-cli multilingual-locale-settings set-mode",
            ),
            "multilingualLocaleSettings.updateLocaleSettings": (
                "PATCH",
                "/locale-settings/v2/settings",
                "wix-safe-agent-cli multilingual-locale-settings update",
            ),
        }
        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))
        self.assertIn(
            "irreversible-when-disabled",
            operations["multilingualLocaleSettings.setMultilingualMode"].get("flags", []),
        )

    def test_multilingual_locales_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("multilingual-locales", families)
        family = families["multilingual-locales"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("site-app-auth", family.get("default_flags", []))
        self.assertIn("plan-first-writes", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "multilingualLocales.createLocale": ("POST", "/locales/v2/locale", "wix-safe-agent-cli multilingual-locales create"),
            "multilingualLocales.getLocale": ("GET", "/locales/v2/locale/{localeId}", "wix-safe-agent-cli multilingual-locales get"),
            "multilingualLocales.updateLocale": ("PATCH", "/locales/v2/locale/{locale.id}", "wix-safe-agent-cli multilingual-locales update"),
            "multilingualLocales.deleteLocale": ("DELETE", "/locales/v2/locale/{localeId}", "wix-safe-agent-cli multilingual-locales delete"),
            "multilingualLocales.queryLocales": ("POST", "/locales/v2/locale/query", "wix-safe-agent-cli multilingual-locales query"),
            "multilingualLocales.bulkCreateLocales": ("POST", "/locales/v2/bulk/locale/create", "wix-safe-agent-cli multilingual-locales bulk-create"),
            "multilingualLocales.bulkDeleteLocales": ("POST", "/locales/v2/bulk/locale/delete", "wix-safe-agent-cli multilingual-locales bulk-delete"),
            "multilingualLocales.bulkUpdateLocales": ("POST", "/locales/v2/bulk/locale/update", "wix-safe-agent-cli multilingual-locales bulk-update"),
            "multilingualLocales.createNewPrimaryLocale": ("POST", "/locales/v2/locale/change-primary", "wix-safe-agent-cli multilingual-locales create-new-primary"),
            "multilingualLocales.getNewPrimaryLocaleStatus": ("GET", "/locales/v2/locale/change-primary", "wix-safe-agent-cli multilingual-locales get-new-primary-status"),
            "multilingualLocales.listSupportedLocales": ("GET", "/locales/v2/locales/supported", "wix-safe-agent-cli multilingual-locales list-supported"),
            "multilingualLocales.setVisitorPrimaryLocale": ("POST", "/locales/v2/locale/set-visitor-primary", "wix-safe-agent-cli multilingual-locales set-visitor-primary"),
        }
        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))
        self.assertIn("irreversible", operations["multilingualLocales.deleteLocale"].get("flags", []))
        self.assertIn("irreversible", operations["multilingualLocales.bulkDeleteLocales"].get("flags", []))
        self.assertIn("irreversible", operations["multilingualLocales.createNewPrimaryLocale"].get("flags", []))

    def test_multilingual_translation_schemas_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("multilingual-translation-schemas", families)
        family = families["multilingual-translation-schemas"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("site-app-auth", family.get("default_flags", []))
        self.assertIn("plan-first-writes", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "translationSchema.createSchema": ("POST", "/translation-schema/v1/schemas", "wix-safe-agent-cli multilingual-translation-schemas create"),
            "translationSchema.getSchema": ("GET", "/translation-schema/v1/schemas/{schemaId}", "wix-safe-agent-cli multilingual-translation-schemas get"),
            "translationSchema.updateSchema": ("PATCH", "/translation-schema/v1/schemas/{schema.id}", "wix-safe-agent-cli multilingual-translation-schemas update"),
            "translationSchema.deleteSchema": ("DELETE", "/translation-schema/v1/schemas/{schemaId}", "wix-safe-agent-cli multilingual-translation-schemas delete"),
            "translationSchema.querySchemas": ("POST", "/translation-schema/v1/schemas/query", "wix-safe-agent-cli multilingual-translation-schemas query"),
            "translationSchema.listSiteSchemas": ("GET", "/translation-schema/v1/schemas/site", "wix-safe-agent-cli multilingual-translation-schemas list-site"),
            "translationSchema.getSchemaByKey": (
                "GET",
                "/translation-schema/v1/schemas/app-id/{key.appId}/entity-type/{key.entityType}/scope/{key.scope}",
                "wix-safe-agent-cli multilingual-translation-schemas get-by-key",
            ),
        }
        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))
        self.assertIn("irreversible", operations["translationSchema.deleteSchema"].get("flags", []))
        self.assertIn("irreversible-when-removing-fields", operations["translationSchema.updateSchema"].get("flags", []))

    def test_multilingual_translation_contents_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("multilingual-translation-contents", families)
        family = families["multilingual-translation-contents"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("site-app-auth", family.get("default_flags", []))
        self.assertIn("plan-first-writes", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "translationContents.createContent": ("POST", "/translation-content/v1/contents", "wix-safe-agent-cli multilingual-translation-contents create"),
            "translationContents.getContent": ("GET", "/translation-content/v1/contents/{contentId}", "wix-safe-agent-cli multilingual-translation-contents get"),
            "translationContents.updateContent": ("PATCH", "/translation-content/v1/contents/{content.id}", "wix-safe-agent-cli multilingual-translation-contents update"),
            "translationContents.deleteContent": ("DELETE", "/translation-content/v1/contents/{contentId}", "wix-safe-agent-cli multilingual-translation-contents delete"),
            "translationContents.queryContents": ("POST", "/translation-content/v1/contents/query", "wix-safe-agent-cli multilingual-translation-contents query"),
            "translationContents.searchContents": ("POST", "/translation-content/v1/contents/search", "wix-safe-agent-cli multilingual-translation-contents search"),
            "translationContents.bulkCreateContent": ("POST", "/translation-content/v1/bulk/contents/create", "wix-safe-agent-cli multilingual-translation-contents bulk-create"),
            "translationContents.bulkDeleteContent": ("POST", "/translation-content/v1/bulk/contents/delete", "wix-safe-agent-cli multilingual-translation-contents bulk-delete"),
            "translationContents.bulkUpdateContent": ("POST", "/translation-content/v1/bulk/contents/update", "wix-safe-agent-cli multilingual-translation-contents bulk-update"),
            "translationContents.bulkUpdateContentByKey": ("POST", "/translation-content/v1/bulk/contents/update-by-key", "wix-safe-agent-cli multilingual-translation-contents bulk-update-by-key"),
            "translationContents.updateContentByKey": ("PATCH", "/translation-content/v1/contents/by-key", "wix-safe-agent-cli multilingual-translation-contents update-by-key"),
        }
        for method_id, (http_method, path, command) in expected.items():
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))
        for method_id in ("translationContents.contentCreated", "translationContents.contentDeleted", "translationContents.contentUpdated"):
            self.assertIn(method_id, operations)
            self.assertFalse(operations[method_id].get("cli_callable"))
            self.assertIn("callback-only", operations[method_id].get("flags", []))
            self.assertIsNone(operations[method_id].get("planned_command"))
        self.assertIn("irreversible", operations["translationContents.deleteContent"].get("flags", []))
        self.assertIn("irreversible", operations["translationContents.bulkDeleteContent"].get("flags", []))
        self.assertIn("irreversible-when-removing-fields", operations["translationContents.updateContent"].get("flags", []))

    def test_multilingual_translation_published_contents_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("multilingual-translation-published-contents", families)
        family = families["multilingual-translation-published-contents"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("read-only", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        query = operations["translationPublishedContents.queryPublishedContent"]
        self.assertEqual(query.get("http_method"), "POST")
        self.assertEqual(query.get("path"), "/translation-published-content/v3/published-contents/query")
        self.assertEqual(query.get("planned_command"), "wix-safe-agent-cli multilingual-translation-published-contents query")
        self.assertTrue(query.get("cli_callable"))
        self.assertIn("required-schema-key-filter", query.get("flags", []))

        for method_id in (
            "translationPublishedContents.publishedContentCreated",
            "translationPublishedContents.publishedContentDeleted",
            "translationPublishedContents.publishedContentUpdated",
        ):
            self.assertIn(method_id, operations)
            self.assertFalse(operations[method_id].get("cli_callable"))
            self.assertIn("callback-only", operations[method_id].get("flags", []))
            self.assertIsNone(operations[method_id].get("planned_command"))

    def test_multilingual_machine_translation_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("multilingual-machine-translation", families)
        family = families["multilingual-machine-translation"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("credit-spend", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "machineTranslation.machineTranslate": (
                "POST",
                "/machine-translation/v3/machine-translate",
                "wix-safe-agent-cli multilingual-machine-translation translate",
            ),
            "machineTranslation.bulkMachineTranslate": (
                "POST",
                "/machine-translation/v3/bulk-machine-translate",
                "wix-safe-agent-cli multilingual-machine-translation bulk-translate",
            ),
        }
        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))
            self.assertIn("credit-spend", operation.get("flags", []))
            self.assertIn("requires-ack-irreversible", operation.get("flags", []))

    def test_multilingual_machine_translation_credit_data_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("multilingual-machine-translation-credit-data", families)
        family = families["multilingual-machine-translation-credit-data"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("read-helper", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "translationCredits.getCreditData": (
                "GET",
                "/translation-credits/v1/credit",
                "wix-safe-agent-cli multilingual-machine-translation-credit-data get",
            ),
            "translationCredits.checkSufficientCredits": (
                "POST",
                "/translation-credits/v1/credit/is-eligible",
                "wix-safe-agent-cli multilingual-machine-translation-credit-data check-sufficient",
            ),
        }
        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))
        self.assertIn("docs-method-mismatch", operations["translationCredits.checkSufficientCredits"].get("flags", []))

    def test_online_programs_programs_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("online-programs-programs", families)
        family = families["online-programs-programs"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("plan-first-writes", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "programs.createProgram": ("POST", "/online-programs/v3/programs", "wix-safe-agent-cli online-programs-programs create"),
            "programs.getProgram": ("GET", "/online-programs/v3/programs/{programId}", "wix-safe-agent-cli online-programs-programs get"),
            "programs.updateProgram": ("PATCH", "/online-programs/v3/programs/{program.id}", "wix-safe-agent-cli online-programs-programs update"),
            "programs.deleteProgram": ("DELETE", "/online-programs/v3/programs/{programId}", "wix-safe-agent-cli online-programs-programs delete"),
            "programs.queryPrograms": ("POST", "/online-programs/v3/programs/query", "wix-safe-agent-cli online-programs-programs query"),
            "programs.searchPrograms": ("POST", "/online-programs/v3/programs/search", "wix-safe-agent-cli online-programs-programs search"),
            "programs.countPrograms": ("POST", "/online-programs/v3/programs/count", "wix-safe-agent-cli online-programs-programs count"),
            "programs.bulkUpdatePrograms": ("POST", "/online-programs/v3/bulk/programs/update", "wix-safe-agent-cli online-programs-programs bulk-update"),
            "programs.archiveProgram": ("POST", "/online-programs/v3/programs/{programId}/archive", "wix-safe-agent-cli online-programs-programs archive"),
            "programs.duplicateProgram": ("POST", "/online-programs/v3/programs/{programId}/duplicate", "wix-safe-agent-cli online-programs-programs duplicate"),
            "programs.endProgram": ("POST", "/online-programs/v3/programs/{programId}/end", "wix-safe-agent-cli online-programs-programs end"),
            "programs.listSamplePrograms": ("GET", "/online-programs/v3/programs/samples", "wix-safe-agent-cli online-programs-programs list-samples"),
            "programs.publishProgram": ("POST", "/online-programs/v3/programs/{programId}/publish", "wix-safe-agent-cli online-programs-programs publish"),
        }
        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))
        self.assertIn("requires-ack-irreversible", operations["programs.deleteProgram"].get("flags", []))
        self.assertIn("requires-revision", operations["programs.updateProgram"].get("flags", []))
        self.assertIn("bulk-max-100", operations["programs.bulkUpdatePrograms"].get("flags", []))

    def test_online_programs_instructor_v2_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("online-programs-instructor-v2", families)
        family = families["online-programs-instructor-v2"]
        self.assertEqual(family.get("coverage_status"), "implemented")
        self.assertIn("plan-first-writes", family.get("default_flags", []))

        operations = {op.get("method_id"): op for op in family.get("operations", [])}
        expected = {
            "instructors.createInstructor": ("POST", "/_api/instructors-service/v2/instructors", "wix-safe-agent-cli online-programs-instructor-v2 create"),
            "instructors.updateInstructor": ("PATCH", "/_api/instructors-service/v2/instructors/{instructor.id}", "wix-safe-agent-cli online-programs-instructor-v2 update"),
            "instructors.queryInstructors": ("POST", "/_api/instructors-service/v2/instructors/query", "wix-safe-agent-cli online-programs-instructor-v2 query"),
            "instructors.assignInstructorToProgram": ("POST", "/_api/instructors-service/v2/instructors/{instructorId}/assign", "wix-safe-agent-cli online-programs-instructor-v2 assign"),
            "instructors.changeProgramInstructors": ("POST", "/_api/instructors-service/v2/assignments", "wix-safe-agent-cli online-programs-instructor-v2 change-program-instructors"),
            "instructors.inviteInstructor": ("POST", "/_api/instructors-service/v2/instructors/invite", "wix-safe-agent-cli online-programs-instructor-v2 invite"),
            "instructors.listInstructors": ("POST", "/_api/instructors-service/v2/instructors/list", "wix-safe-agent-cli online-programs-instructor-v2 list"),
            "instructors.unassignInstructorFromProgram": ("POST", "/_api/instructors-service/v2/instructors/{instructorId}/unassign", "wix-safe-agent-cli online-programs-instructor-v2 unassign"),
        }
        self.assertEqual(set(operations), set(expected))
        for method_id, (http_method, path, command) in expected.items():
            operation = operations[method_id]
            self.assertEqual(operation.get("http_method"), http_method)
            self.assertEqual(operation.get("path"), path)
            self.assertEqual(operation.get("planned_command"), command)
            self.assertTrue(operation.get("cli_callable"))
        self.assertIn("sends-email", operations["instructors.inviteInstructor"].get("flags", []))
        self.assertIn("bulk-max-10", operations["instructors.changeProgramInstructors"].get("flags", []))
        self.assertIn("requires-ack-irreversible", operations["instructors.unassignInstructorFromProgram"].get("flags", []))

    def test_http_functions_is_site_defined_and_non_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("http-functions", families)
        family = families["http-functions"]
        self.assertIn("site-defined", family.get("default_flags", []))
        self.assertIn("generic-bridge-forbidden", family.get("default_flags", []))
        operation = family.get("operations", [])[0]
        self.assertEqual(operation.get("method_id"), "httpFunctions.callHttpFunction")
        self.assertIsNone(operation.get("planned_command"))
        self.assertIsNone(operation.get("http_method"))
        self.assertIsNone(operation.get("path"))
        self.assertIn("site-defined", operation.get("flags", []))
        self.assertFalse(operation.get("cli_callable"))

    def test_rich_content_ricos_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("rich-content-ricos", families)
        family = families["rich-content-ricos"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 3)

        expected = {
            "richContentRicosDocuments.convertFromRicosDocument": (
                "POST",
                "/ricos/v1/ricos-document/convert/from-ricos",
                "wix-safe-agent-cli rich-content-ricos convert-from",
            ),
            "richContentRicosDocuments.convertToRicosDocument": (
                "POST",
                "/ricos/v1/ricos-document/convert/to-ricos",
                "wix-safe-agent-cli rich-content-ricos convert-to",
            ),
            "richContentRicosDocuments.validateDocument": (
                "POST",
                "/ricos/v1/ricos-document/validate",
                "wix-safe-agent-cli rich-content-ricos validate",
            ),
        }
        by_id = {op.get("method_id"): op for op in operations}
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

    def test_pro_gallery_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("pro-gallery", families)
        family = families["pro-gallery"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 12)

        by_id = {op.get("method_id"): op for op in operations}
        expected = {
            "proGallery.createGallery": ("POST", "/progallery/v2/galleries", "wix-safe-agent-cli pro-gallery create-gallery"),
            "proGallery.getGallery": ("GET", "/progallery/v2/galleries/{galleryId}", "wix-safe-agent-cli pro-gallery get-gallery"),
            "proGallery.updateGallery": ("PATCH", "/progallery/v2/galleries/{gallery.id}", "wix-safe-agent-cli pro-gallery update-gallery"),
            "proGallery.deleteGallery": ("DELETE", "/progallery/v2/galleries/{galleryId}", "wix-safe-agent-cli pro-gallery delete-gallery"),
            "proGallery.listGalleries": ("GET", "/progallery/v2/galleries", "wix-safe-agent-cli pro-gallery list-galleries"),
            "proGallery.createGalleryItem": (
                "POST",
                "/progallery/v2/galleries/{galleryId}/items",
                "wix-safe-agent-cli pro-gallery create-gallery-item",
            ),
            "proGallery.getGalleryItem": (
                "GET",
                "/progallery/v2/galleries/{galleryId}/items/{itemId}",
                "wix-safe-agent-cli pro-gallery get-gallery-item",
            ),
            "proGallery.updateGalleryItem": (
                "PATCH",
                "/progallery/v2/galleries/{galleryId}/items/{item.id}",
                "wix-safe-agent-cli pro-gallery update-gallery-item",
            ),
            "proGallery.deleteGalleryItem": (
                "DELETE",
                "/progallery/v2/galleries/{galleryId}/items/{itemId}",
                "wix-safe-agent-cli pro-gallery delete-gallery-item",
            ),
            "proGallery.listGalleryItems": (
                "GET",
                "/progallery/v2/galleries/{galleryId}/items",
                "wix-safe-agent-cli pro-gallery list-gallery-items",
            ),
            "proGallery.bulkDeleteGalleryItems": (
                "POST",
                "/progallery/v2/galleries/{galleryId}/items/delete",
                "wix-safe-agent-cli pro-gallery bulk-delete-gallery-items",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        deprecated = by_id["proGallery.deleteGalleryItemsDeprecated"]
        self.assertIn("deprecated", deprecated.get("flags", []))
        self.assertIsNone(deprecated.get("planned_command"))
        self.assertFalse(deprecated.get("cli_callable"))

    def test_members_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("members", families)
        family = families["members"]
        self.assertEqual(
            family["source_urls"][0],
            "https://dev.wix.com/docs/api-reference/crm/members-contacts/members/member-management/members/introduction",
        )
        by_id = {op["method_id"]: op for op in family.get("operations", [])}
        expected = {
            "members.updateMySlug": ("POST", "/members/v1/members/my/slug", "wix-safe-agent-cli members update-my-slug"),
            "members.updateMemberSlug": ("POST", "/members/v1/members/{id}/slug", "wix-safe-agent-cli members update-member-slug"),
            "members.joinCommunity": ("POST", "/members/v1/members/join-community", "wix-safe-agent-cli members join-community"),
            "members.leaveCommunity": ("POST", "/members/v1/members/leave-community", "wix-safe-agent-cli members leave-community"),
            "members.getMyMember": ("GET", "/members/v1/members/my", "wix-safe-agent-cli members get-my"),
            "members.deleteMyMember": ("DELETE", "/members/v1/members/my", "wix-safe-agent-cli members delete-my"),
            "members.getMember": ("GET", "/members/v1/members/{id}", "wix-safe-agent-cli members get"),
            "members.deleteMember": ("DELETE", "/members/v1/members/{id}", "wix-safe-agent-cli members delete"),
            "members.listMembers": ("GET", "/members/v1/members", "wix-safe-agent-cli members list"),
            "members.createMember": ("POST", "/members/v1/members", "wix-safe-agent-cli members create"),
            "members.queryMembers": ("POST", "/members/v1/members/query", "wix-safe-agent-cli members query"),
            "members.muteMember": ("POST", "/members/v1/members/{id}/mute", "wix-safe-agent-cli members mute"),
            "members.unmuteMember": ("POST", "/members/v1/members/{id}/unmute", "wix-safe-agent-cli members unmute"),
            "members.approveMember": ("POST", "/members/v1/members/{id}/approve", "wix-safe-agent-cli members approve"),
            "members.blockMember": ("POST", "/members/v1/members/{id}/block", "wix-safe-agent-cli members block"),
            "members.disconnectMember": ("POST", "/members/v1/members/{id}/disconnect", "wix-safe-agent-cli members disconnect"),
            "members.bulkDeleteMembers": ("POST", "/members/v1/members/bulk/delete", "wix-safe-agent-cli members bulk-delete"),
            "members.bulkDeleteMembersByFilter": ("POST", "/members/v1/members/bulk/delete-by-filter", "wix-safe-agent-cli members bulk-delete-by-filter"),
            "members.bulkApproveMembers": ("POST", "/members/v1/members/bulk/approve-by-filter", "wix-safe-agent-cli members bulk-approve"),
            "members.bulkBlockMembers": ("POST", "/members/v1/members/bulk/block-by-filter", "wix-safe-agent-cli members bulk-block"),
            "members.updateMember": ("PATCH", "/members/v1/members/{member.id}", "wix-safe-agent-cli members update"),
            "members.deleteMemberPhones": ("DELETE", "/members/v1/members/{id}/phones", "wix-safe-agent-cli members delete-phones"),
            "members.deleteMemberEmails": ("DELETE", "/members/v1/members/{id}/emails", "wix-safe-agent-cli members delete-emails"),
            "members.deleteMemberAddresses": ("DELETE", "/members/v1/members/{id}/addresses", "wix-safe-agent-cli members delete-addresses"),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        for method_id in ["members.memberCreated", "members.memberDeleted", "members.memberUpdated"]:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id].get("flags", []))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertFalse(by_id[method_id].get("cli_callable"))

    def test_activity_counters_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("activity-counters", families)
        family = families["activity-counters"]
        self.assertEqual(
            family["source_urls"][0],
            "https://dev.wix.com/docs/api-reference/crm/members-contacts/members/activity/activity-counters/introduction",
        )
        by_id = {op["method_id"]: op for op in family.get("operations", [])}
        expected = {
            "activityCounters.getActivityCounters": (
                "GET",
                "/members/v1/activity-counters/{memberId}",
                "wix-safe-agent-cli activity-counters get",
            ),
            "activityCounters.queryActivityCounters": (
                "POST",
                "/members/v1/activity-counters/query",
                "wix-safe-agent-cli activity-counters query",
            ),
            "activityCounters.setActivityCounters": (
                "PUT",
                "/members/v1/activity-counters/{memberId}",
                "wix-safe-agent-cli activity-counters set",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        event = by_id["activityCounters.activityCounterUpdated"]
        self.assertIn("callback-only", event.get("flags", []))
        self.assertIsNone(event.get("planned_command"))
        self.assertFalse(event.get("cli_callable"))

    def test_members_legacy_badges_family_present_and_deprecated(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("members-activity-badges-legacy", families)
        family = families["members-activity-badges-legacy"]
        self.assertIn("deprecated", family.get("default_flags", []))
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 13)
        by_id = {op["method_id"]: op for op in operations}
        self.assertEqual(by_id["membersBadgesLegacy.createBadge"].get("path"), "/members/v3/badges")
        self.assertEqual(by_id["membersBadgesLegacy.getBadge"].get("path"), "/members/v3/badges/{id}")
        self.assertEqual(by_id["membersBadgesLegacy.assignBadgeToMembers"].get("path"), "/members/v3/badges/{id}/members")
        self.assertEqual(by_id["membersBadgesLegacy.updateBadgesDisplayOrder"].get("path"), "/members/v3/badges/order")
        for op in operations:
            with self.subTest(method_id=op["method_id"]):
                self.assertIn("deprecated", op.get("flags", []))
                self.assertIsNone(op.get("planned_command"))
                self.assertFalse(op.get("cli_callable"))

    def test_badges_v4_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("badges-v4", families)
        family = families["badges-v4"]
        self.assertEqual(
            family["source_urls"][0],
            "https://dev.wix.com/docs/api-reference/crm/members-contacts/members/activity/badges-v4/introduction",
        )
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 10)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "badgesV4.createBadge": ("POST", "/badges/v4/badges", "wix-safe-agent-cli badges-v4 create"),
            "badgesV4.getBadge": ("GET", "/badges/v4/badges/{badgeId}", "wix-safe-agent-cli badges-v4 get"),
            "badgesV4.updateBadge": ("PATCH", "/badges/v4/badges/{badge.id}", "wix-safe-agent-cli badges-v4 update"),
            "badgesV4.deleteBadge": ("DELETE", "/badges/v4/badges/{badgeId}", "wix-safe-agent-cli badges-v4 delete"),
            "badgesV4.queryBadges": ("POST", "/badges/v4/badges/query", "wix-safe-agent-cli badges-v4 query"),
            "badgesV4.moveBadge": ("POST", "/badges/v4/badges/{badgeId}/move", "wix-safe-agent-cli badges-v4 move"),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        deprecated = by_id["badgesV4.updateBadgesDisplayOrder"]
        self.assertEqual(deprecated.get("path"), "/badges/v4/badges/order")
        self.assertIn("deprecated", deprecated.get("flags", []))
        self.assertIsNone(deprecated.get("planned_command"))
        self.assertFalse(deprecated.get("cli_callable"))

        for method_id in ["badgesV4.badgeCreated", "badgesV4.badgeUpdated", "badgesV4.badgeDeleted"]:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id].get("flags", []))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertFalse(by_id[method_id].get("cli_callable"))

    def test_badge_assignments_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("badge-assignments", families)
        family = families["badge-assignments"]
        self.assertEqual(
            family["source_urls"][0],
            "https://dev.wix.com/docs/api-reference/crm/members-contacts/members/activity/badge-assignments/introduction",
        )
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "badgeAssignments.createBadgeAssignment": (
                "POST",
                "/badges/v4/assignments",
                "wix-safe-agent-cli badge-assignments create",
            ),
            "badgeAssignments.deleteBadgeAssignment": (
                "DELETE",
                "/badges/v4/assignments/{badgeAssignmentId}",
                "wix-safe-agent-cli badge-assignments delete",
            ),
            "badgeAssignments.queryBadgeAssignments": (
                "POST",
                "/badges/v4/assignments/query",
                "wix-safe-agent-cli badge-assignments query",
            ),
            "badgeAssignments.bulkCreateBadgeAssignments": (
                "POST",
                "/badges/v4/bulk/assignments/create",
                "wix-safe-agent-cli badge-assignments bulk-create",
            ),
            "badgeAssignments.bulkDeleteBadgeAssignments": (
                "POST",
                "/badges/v4/bulk/assignments/delete",
                "wix-safe-agent-cli badge-assignments bulk-delete",
            ),
            "badgeAssignments.bulkUpdateBadgeAssignmentTags": (
                "POST",
                "/badges/v4/bulk/assignments/bulk-update-tags",
                "wix-safe-agent-cli badge-assignments bulk-update-tags",
            ),
            "badgeAssignments.bulkUpdateBadgeAssignmentTagsByFilter": (
                "POST",
                "/badges/v4/bulk/assignments/update-tags-by-filter",
                "wix-safe-agent-cli badge-assignments bulk-update-tags-by-filter",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        for method_id in ["badgeAssignments.badgeAssignmentCreated", "badgeAssignments.badgeAssignmentDeleted"]:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id].get("flags", []))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertFalse(by_id[method_id].get("cli_callable"))

    def test_member_reports_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("member-reports", families)
        family = families["member-reports"]
        self.assertEqual(
            family["source_urls"][0],
            "https://dev.wix.com/docs/api-reference/crm/members-contacts/members/activity/member-reports/introduction",
        )
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 5)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "memberReports.deleteMemberReports": (
                "DELETE",
                "/members/v1/member-reports/members/{memberId}",
                "wix-safe-agent-cli member-reports delete",
            ),
            "memberReports.queryMemberReports": (
                "POST",
                "/members/v1/member-reports/query",
                "wix-safe-agent-cli member-reports query",
            ),
            "memberReports.reportMember": (
                "POST",
                "/members/v1/member-reports",
                "wix-safe-agent-cli member-reports report",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        for method_id in ["memberReports.memberReportCreated", "memberReports.memberReportDeleted"]:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id].get("flags", []))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertFalse(by_id[method_id].get("cli_callable"))

    def test_members_followers_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("members-followers", families)
        family = families["members-followers"]
        self.assertEqual(
            family["source_urls"][0],
            "https://dev.wix.com/docs/api-reference/crm/members-contacts/members/activity/members-followers/introduction",
        )
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 10)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "membersFollowers.followMember": (
                "POST",
                "/members/v3/followers/{memberId}",
                "wix-safe-agent-cli members-followers follow",
            ),
            "membersFollowers.listMemberFollowers": (
                "GET",
                "/members/v3/followers/{memberId}",
                "wix-safe-agent-cli members-followers list-followers",
            ),
            "membersFollowers.listMemberFollowing": (
                "GET",
                "/members/v3/followers/{memberId}/following",
                "wix-safe-agent-cli members-followers list-following",
            ),
            "membersFollowers.listMyMemberFollowers": (
                "GET",
                "/members/v3/followers/my",
                "wix-safe-agent-cli members-followers list-my-followers",
            ),
            "membersFollowers.listMyMemberFollowing": (
                "GET",
                "/members/v3/followers/my/following",
                "wix-safe-agent-cli members-followers list-my-following",
            ),
            "membersFollowers.queryMemberConnections": (
                "POST",
                "/members/v3/followers/{memberId}/connections",
                "wix-safe-agent-cli members-followers query-connections",
            ),
            "membersFollowers.queryMyMemberConnections": (
                "POST",
                "/members/v3/followers/my/connections",
                "wix-safe-agent-cli members-followers query-my-connections",
            ),
            "membersFollowers.unfollowMember": (
                "DELETE",
                "/members/v3/followers/{memberId}",
                "wix-safe-agent-cli members-followers unfollow",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        for method_id in ["membersFollowers.memberFollowed", "membersFollowers.followMemberUnfollowed"]:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id].get("flags", []))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertFalse(by_id[method_id].get("cli_callable"))

    def test_user_members_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("user-members", families)
        family = families["user-members"]
        self.assertEqual(
            family["source_urls"][0],
            "https://dev.wix.com/docs/api-reference/crm/members-contacts/members/member-management/user-member/introduction",
        )
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)
        op = operations[0]
        self.assertEqual(op.get("method_id"), "userMembers.queryUserMembers")
        self.assertEqual(op.get("http_method"), "POST")
        self.assertEqual(op.get("path"), "/members/v1/user-members/query")
        self.assertEqual(op.get("planned_command"), "wix-safe-agent-cli user-members query")
        self.assertIn("implemented", op["flags"])
        self.assertTrue(op["cli_callable"])

    def test_member_authentication_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("member-authentication", families)
        family = families["member-authentication"]
        self.assertEqual(
            family["doc_url"],
            "https://dev.wix.com/docs/api-reference/crm/members-contacts/members/member-management/member-authentication/introduction",
        )
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 1)
        op = operations[0]
        self.assertEqual(op.get("method_id"), "memberAuthentication.sendSetPasswordEmail")
        self.assertEqual(op.get("http_method"), "POST")
        self.assertEqual(op.get("path"), "/wix-sm/api/v1/auth/v1/auth/members/send-set-password-email")
        self.assertEqual(
            op.get("planned_command"),
            "wix-safe-agent-cli member-authentication send-set-password-email",
        )
        self.assertIn("implemented", op["flags"])
        self.assertIn("developer-preview", op["flags"])
        self.assertIn("requires-ack-irreversible", op["flags"])

    def test_member_abouts_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("member-abouts", families)
        family = families["member-abouts"]
        self.assertEqual(
            family["source_urls"][0],
            "https://dev.wix.com/docs/api-reference/crm/members-contacts/members/member-management/members-about-v2/introduction",
        )
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 9)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "memberAbouts.createMemberAbout": (
                "POST",
                "/members/v2/abouts",
                "wix-safe-agent-cli member-abouts create",
            ),
            "memberAbouts.getMemberAbout": (
                "GET",
                "/members/v2/abouts/{id}",
                "wix-safe-agent-cli member-abouts get",
            ),
            "memberAbouts.updateMemberAbout": (
                "PATCH",
                "/members/v2/abouts/{memberAbout.id}",
                "wix-safe-agent-cli member-abouts update",
            ),
            "memberAbouts.deleteMemberAbout": (
                "DELETE",
                "/members/v2/abouts/{id}",
                "wix-safe-agent-cli member-abouts delete",
            ),
            "memberAbouts.queryMemberAbouts": (
                "POST",
                "/members/v2/abouts/query",
                "wix-safe-agent-cli member-abouts query",
            ),
            "memberAbouts.getMyMemberAbout": (
                "GET",
                "/members/v2/abouts/my",
                "wix-safe-agent-cli member-abouts get-my",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertTrue(by_id[method_id]["cli_callable"])

        for method_id in [
            "memberAbouts.memberAboutCreated",
            "memberAbouts.memberAboutDeleted",
            "memberAbouts.memberAboutUpdated",
        ]:
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id].get("flags", []))
                self.assertIsNone(by_id[method_id].get("planned_command"))
                self.assertFalse(by_id[method_id].get("cli_callable"))

    def test_member_privacy_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("member-privacy", families)
        family = families["member-privacy"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 4)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "memberPrivacy.getDefaultPrivacyStatus": (
                "GET",
                "/members/v1/default-privacy-status",
                "wix-safe-agent-cli member-privacy get-default",
            ),
            "memberPrivacy.setDefaultPrivacyStatus": (
                "PATCH",
                "/members/v1/default-privacy-status",
                "wix-safe-agent-cli member-privacy set-default",
            ),
            "memberPrivacy.getMemberPrivacySettings": (
                "GET",
                "/members/v1/privacy-settings",
                "wix-safe-agent-cli member-privacy get-settings",
            ),
            "memberPrivacy.setMemberPrivacySettings": (
                "POST",
                "/members/v1/privacy-settings",
                "wix-safe-agent-cli member-privacy set-settings",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])

    def test_member_custom_fields_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("member-custom-fields", families)
        family = families["member-custom-fields"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 7)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "memberCustomFields.createCustomField": (
                "POST",
                "/members/v1/custom-fields",
                "wix-safe-agent-cli member-custom-fields create",
            ),
            "memberCustomFields.updateCustomField": (
                "PATCH",
                "/members/v1/custom-fields/{id}",
                "wix-safe-agent-cli member-custom-fields update",
            ),
            "memberCustomFields.deleteCustomField": (
                "DELETE",
                "/members/v1/custom-fields/{id}",
                "wix-safe-agent-cli member-custom-fields delete",
            ),
            "memberCustomFields.getCustomField": (
                "GET",
                "/members/v1/custom-fields/{id}",
                "wix-safe-agent-cli member-custom-fields get",
            ),
            "memberCustomFields.hideCustomField": (
                "POST",
                "/members/v1/custom-fields/{id}/hide",
                "wix-safe-agent-cli member-custom-fields hide",
            ),
            "memberCustomFields.listCustomFields": (
                "GET",
                "/members/v1/custom-fields",
                "wix-safe-agent-cli member-custom-fields list",
            ),
            "memberCustomFields.updateCustomFieldsOrder": (
                "POST",
                "/members/v1/custom-fields/order",
                "wix-safe-agent-cli member-custom-fields update-order",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])

        self.assertIn("requires-ack-irreversible", by_id["memberCustomFields.deleteCustomField"]["flags"])

    def test_member_custom_field_applications_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("member-custom-field-applications", families)
        family = families["member-custom-field-applications"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 7)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "memberCustomFieldApplications.createCustomFieldApplication": (
                "POST",
                "/members/v1/custom-fields-applications",
                "wix-safe-agent-cli member-custom-field-applications create",
            ),
            "memberCustomFieldApplications.updateCustomFieldApplication": (
                "PATCH",
                "/members/v1/custom-fields-applications/{application.customFieldId}",
                "wix-safe-agent-cli member-custom-field-applications update",
            ),
            "memberCustomFieldApplications.deleteCustomFieldApplication": (
                "DELETE",
                "/members/v1/custom-fields-applications/{customFieldId}",
                "wix-safe-agent-cli member-custom-field-applications delete",
            ),
            "memberCustomFieldApplications.getCustomFieldApplication": (
                "GET",
                "/members/v1/custom-fields-applications/{customFieldId}",
                "wix-safe-agent-cli member-custom-field-applications get",
            ),
            "memberCustomFieldApplications.getCustomFieldApplications": (
                "POST",
                "/members/v1/custom-fields-applications/applications",
                "wix-safe-agent-cli member-custom-field-applications list-applications",
            ),
            "memberCustomFieldApplications.getMembersCustomFieldApplications": (
                "POST",
                "/members/v1/custom-fields-applications/members",
                "wix-safe-agent-cli member-custom-field-applications get-members",
            ),
            "memberCustomFieldApplications.getRolesCustomFieldApplications": (
                "POST",
                "/members/v1/custom-fields-applications/roles",
                "wix-safe-agent-cli member-custom-field-applications get-roles",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])

        self.assertIn(
            "requires-ack-irreversible",
            by_id["memberCustomFieldApplications.deleteCustomFieldApplication"]["flags"],
        )

    def test_member_custom_field_suggestions_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("member-custom-field-suggestions", families)
        family = families["member-custom-field-suggestions"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 2)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "memberCustomFieldSuggestions.queryCustomFieldSuggestions": (
                "POST",
                "/members/v1/custom-field-suggestions/query",
                "wix-safe-agent-cli member-custom-field-suggestions query",
            ),
            "memberCustomFieldSuggestions.listCustomFieldSuggestions": (
                "GET",
                "/members/v1/custom-field-suggestions",
                "wix-safe-agent-cli member-custom-field-suggestions list",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])

        self.assertIn("developer-preview", by_id["memberCustomFieldSuggestions.listCustomFieldSuggestions"]["flags"])

    def test_crm_tasks_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("crm-tasks", families)
        family = families["crm-tasks"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 11)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "crmTasks.createTask": ("POST", "/crm/tasks/v2/tasks", "wix-safe-agent-cli crm-tasks create"),
            "crmTasks.getTask": ("GET", "/crm/tasks/v2/tasks/{taskId}", "wix-safe-agent-cli crm-tasks get"),
            "crmTasks.updateTask": ("PATCH", "/crm/tasks/v2/tasks/{task.id}", "wix-safe-agent-cli crm-tasks update"),
            "crmTasks.deleteTask": ("DELETE", "/crm/tasks/v2/tasks/{taskId}", "wix-safe-agent-cli crm-tasks delete"),
            "crmTasks.queryTasks": ("POST", "/crm/tasks/v2/tasks/query", "wix-safe-agent-cli crm-tasks query"),
            "crmTasks.countTasks": ("POST", "/crm/tasks/v2/tasks/count", "wix-safe-agent-cli crm-tasks count"),
            "crmTasks.moveTaskAfter": ("POST", "/crm/tasks/v2/tasks/{taskId}/move-after", "wix-safe-agent-cli crm-tasks move-after"),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])

        self.assertIn("ack-irreversible", by_id["crmTasks.deleteTask"]["flags"])
        for method_id in ("crmTasks.taskCreated", "crmTasks.taskDeleted", "crmTasks.taskOverdue", "crmTasks.taskUpdated"):
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id]["flags"])
                self.assertFalse(by_id[method_id]["cli_callable"])

    def test_crm_pipelines_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("crm-pipelines", families)
        family = families["crm-pipelines"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 10)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "crmPipelines.createPipeline": ("POST", "/crm/pipelines/v1/pipelines", "wix-safe-agent-cli crm-pipelines create"),
            "crmPipelines.getPipeline": ("GET", "/crm/pipelines/v1/pipelines/{pipelineId}", "wix-safe-agent-cli crm-pipelines get"),
            "crmPipelines.updatePipeline": ("PATCH", "/crm/pipelines/v1/pipelines/{pipeline.id}", "wix-safe-agent-cli crm-pipelines update"),
            "crmPipelines.deletePipeline": ("DELETE", "/crm/pipelines/v1/pipelines/{pipelineId}", "wix-safe-agent-cli crm-pipelines delete"),
            "crmPipelines.queryPipelines": ("POST", "/crm/pipelines/v1/pipelines/query", "wix-safe-agent-cli crm-pipelines query"),
            "crmPipelines.bulkUpdatePipelineTags": (
                "POST",
                "/crm/pipelines/v1/bulk/pipelines/update-tags",
                "wix-safe-agent-cli crm-pipelines bulk-update-tags",
            ),
            "crmPipelines.bulkUpdatePipelineTagsByFilter": (
                "POST",
                "/crm/pipelines/v1/bulk/pipelines/update-tags-by-filter",
                "wix-safe-agent-cli crm-pipelines bulk-update-tags-by-filter",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])

        self.assertIn("ack-irreversible", by_id["crmPipelines.deletePipeline"]["flags"])
        self.assertIn("ack-irreversible", by_id["crmPipelines.bulkUpdatePipelineTagsByFilter"]["flags"])
        for method_id in ("crmPipelines.pipelineCreated", "crmPipelines.pipelineDeleted", "crmPipelines.pipelineUpdated"):
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertFalse(by_id[method_id]["cli_callable"])

    def test_crm_cards_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("crm-cards", families)
        family = families["crm-cards"]
        operations = family.get("operations", [])
        self.assertEqual(len(operations), 17)
        by_id = {op["method_id"]: op for op in operations}
        expected = {
            "crmCards.createCard": ("POST", "/crm/pipelines/v1/cards", "wix-safe-agent-cli crm-cards create"),
            "crmCards.getCard": ("GET", "/crm/pipelines/v1/cards/{cardId}", "wix-safe-agent-cli crm-cards get"),
            "crmCards.updateCard": ("PATCH", "/crm/pipelines/v1/cards/{card.id}", "wix-safe-agent-cli crm-cards update"),
            "crmCards.deleteCard": ("DELETE", "/crm/pipelines/v1/cards/{cardId}", "wix-safe-agent-cli crm-cards delete"),
            "crmCards.queryCards": ("POST", "/crm/pipelines/v1/cards/query", "wix-safe-agent-cli crm-cards query"),
            "crmCards.searchCards": ("POST", "/crm/pipelines/v1/cards/search", "wix-safe-agent-cli crm-cards search"),
            "crmCards.bulkUpdateCardTags": (
                "POST",
                "/crm/pipelines/v1/bulk/cards/update-tags",
                "wix-safe-agent-cli crm-cards bulk-update-tags",
            ),
            "crmCards.bulkUpdateCardTagsByFilter": (
                "POST",
                "/crm/pipelines/v1/bulk/cards/update-tags-by-filter",
                "wix-safe-agent-cli crm-cards bulk-update-tags-by-filter",
            ),
            "crmCards.moveCard": ("PATCH", "/crm/pipelines/v1/cards/move/{cardId}", "wix-safe-agent-cli crm-cards move"),
            "crmCards.searchCardsByStage": (
                "POST",
                "/crm/pipelines/v1/cards/search-by-stage",
                "wix-safe-agent-cli crm-cards search-by-stage",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            with self.subTest(method_id=method_id):
                self.assertEqual(by_id[method_id].get("http_method"), http_method)
                self.assertEqual(by_id[method_id].get("path"), path)
                self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                self.assertIn("implemented", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])

        self.assertIn("ack-irreversible", by_id["crmCards.deleteCard"]["flags"])
        self.assertIn("ack-irreversible", by_id["crmCards.bulkUpdateCardTagsByFilter"]["flags"])
        for method_id in (
            "crmCards.cardAssigned",
            "crmCards.cardCreated",
            "crmCards.cardDeleted",
            "crmCards.cardMoved",
            "crmCards.cardOverdue",
            "crmCards.cardStale",
            "crmCards.cardUpdated",
        ):
            with self.subTest(method_id=method_id):
                self.assertIn("callback-only", by_id[method_id]["flags"])
                self.assertIn("developer-preview", by_id[method_id]["flags"])
                self.assertFalse(by_id[method_id]["cli_callable"])

    def test_ai_site_chat_families_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}
        expected = {
            "ai-site-chat-widget-settings": {
                "aiSiteChatWidgetSettings.getWidgetSettings": (
                    "GET",
                    "/wix-assistant-widget/v1/settings",
                    "wix-safe-agent-cli ai-site-chat-widget-settings get",
                ),
                "aiSiteChatWidgetSettings.setWidgetSettings": (
                    "POST",
                    "/wix-assistant-widget/v1/settings",
                    "wix-safe-agent-cli ai-site-chat-widget-settings set",
                ),
            },
            "ai-site-chat-widget-settings-v2": {
                "aiSiteChatWidgetSettingsV2.getWidgetSettings": (
                    "GET",
                    "/wix-assistant-widget/v2/settings",
                    "wix-safe-agent-cli ai-site-chat-widget-settings-v2 get",
                ),
                "aiSiteChatWidgetSettingsV2.updateWidgetSettings": (
                    "PATCH",
                    "/wix-assistant-widget/v2/settings",
                    "wix-safe-agent-cli ai-site-chat-widget-settings-v2 update",
                ),
            },
            "ai-site-chat-conversations": {
                "aiSiteChatConversations.getConversation": (
                    "GET",
                    "/wix-assistant-widget/v1/conversation",
                    "wix-safe-agent-cli ai-site-chat-conversations get",
                ),
            },
            "ai-site-chat-messages": {
                "aiSiteChatMessages.listMessages": (
                    "GET",
                    "/wix-assistant-widget/v1/messages/list",
                    "wix-safe-agent-cli ai-site-chat-messages list",
                ),
                "aiSiteChatMessages.bulkCreateMessages": (
                    "POST",
                    "/wix-assistant-widget/v1/bulk/messages/create",
                    "wix-safe-agent-cli ai-site-chat-messages bulk-create",
                ),
                "aiSiteChatMessages.bulkGetByInboxMessages": (
                    "GET",
                    "/wix-assistant-widget/v1/messages/get-by-inbox",
                    "wix-safe-agent-cli ai-site-chat-messages bulk-get-by-inbox",
                ),
                "aiSiteChatMessages.mediaAttachmentUploadUrl": (
                    "GET",
                    "/wix-assistant-widget/v1/messages/files/generate-upload-url",
                    "wix-safe-agent-cli ai-site-chat-messages media-upload-url",
                ),
            },
        }
        for slug, methods in expected.items():
            with self.subTest(slug=slug):
                self.assertIn(slug, families)
                family = families[slug]
                by_id = {op["method_id"]: op for op in family.get("operations", [])}
                for method_id, (http_method, path, planned_command) in methods.items():
                    self.assertEqual(by_id[method_id].get("http_method"), http_method)
                    self.assertEqual(by_id[method_id].get("path"), path)
                    self.assertEqual(by_id[method_id].get("planned_command"), planned_command)
                    self.assertIn("implemented", by_id[method_id]["flags"])

        messages = {op["method_id"]: op for op in families["ai-site-chat-messages"]["operations"]}
        self.assertIn("ack-irreversible", messages["aiSiteChatMessages.bulkCreateMessages"]["flags"])

    def test_faq_app_families_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("faq-category-v2", families)
        category = {op["method_id"]: op for op in families["faq-category-v2"]["operations"]}
        category_expected = {
            "faqCategoryV2.createCategory": ("POST", "/faq/v2/categories", "wix-safe-agent-cli faq-category-v2 create"),
            "faqCategoryV2.getCategory": ("GET", "/faq/v2/categories/{categoryId}", "wix-safe-agent-cli faq-category-v2 get"),
            "faqCategoryV2.updateCategory": ("PATCH", "/faq/v2/categories/{category.id}", "wix-safe-agent-cli faq-category-v2 update"),
            "faqCategoryV2.deleteCategory": ("DELETE", "/faq/v2/categories/{categoryId}", "wix-safe-agent-cli faq-category-v2 delete"),
            "faqCategoryV2.queryCategories": ("POST", "/faq/v2/categories/query", "wix-safe-agent-cli faq-category-v2 query"),
            "faqCategoryV2.listCategories": ("GET", "/faq/v2/categories", "wix-safe-agent-cli faq-category-v2 list"),
            "faqCategoryV2.updateExtendedFields": (
                "POST",
                "/faq/v2/categories/{id}/update-extended-fields",
                "wix-safe-agent-cli faq-category-v2 update-extended-fields",
            ),
        }
        for method_id, (http_method, path, planned_command) in category_expected.items():
            self.assertEqual(category[method_id].get("http_method"), http_method)
            self.assertEqual(category[method_id].get("path"), path)
            self.assertEqual(category[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", category[method_id]["flags"])
        self.assertIn("requires-ack-irreversible", category["faqCategoryV2.deleteCategory"]["flags"])

        self.assertIn("faq-question-entry-v2", families)
        question = {op["method_id"]: op for op in families["faq-question-entry-v2"]["operations"]}
        question_expected = {
            "faqQuestionEntryV2.listQuestionEntries": ("GET", "/faq/v2/question-entries", "wix-safe-agent-cli faq-question-entry-v2 list"),
            "faqQuestionEntryV2.createQuestionEntry": ("POST", "/faq/v2/question-entries", "wix-safe-agent-cli faq-question-entry-v2 create"),
            "faqQuestionEntryV2.getQuestionEntry": (
                "GET",
                "/faq/v2/question-entries/{questionEntryId}",
                "wix-safe-agent-cli faq-question-entry-v2 get",
            ),
            "faqQuestionEntryV2.deleteQuestionEntry": (
                "DELETE",
                "/faq/v2/question-entries/{questionEntryId}",
                "wix-safe-agent-cli faq-question-entry-v2 delete",
            ),
            "faqQuestionEntryV2.updateQuestionEntry": (
                "PATCH",
                "/faq/v2/question-entries/{questionEntry.id}",
                "wix-safe-agent-cli faq-question-entry-v2 update",
            ),
            "faqQuestionEntryV2.queryQuestionEntries": (
                "POST",
                "/faq/v2/question-entries/query",
                "wix-safe-agent-cli faq-question-entry-v2 query",
            ),
            "faqQuestionEntryV2.bulkDeleteQuestionEntries": (
                "POST",
                "/faq/question-entry/v2/bulk/question-entries/delete",
                "wix-safe-agent-cli faq-question-entry-v2 bulk-delete",
            ),
            "faqQuestionEntryV2.bulkUpdateQuestionEntry": (
                "POST",
                "/faq/question-entry/v2/bulk/question-entries/update",
                "wix-safe-agent-cli faq-question-entry-v2 bulk-update",
            ),
            "faqQuestionEntryV2.setQuestionEntryLabels": (
                "PATCH",
                "/faq/v2/question-entries/{questionEntryId}/labels",
                "wix-safe-agent-cli faq-question-entry-v2 set-labels",
            ),
            "faqQuestionEntryV2.updateExtendedFields": (
                "POST",
                "/faq/v2/question-entries/{id}/update-extended-fields",
                "wix-safe-agent-cli faq-question-entry-v2 update-extended-fields",
            ),
        }
        for method_id, (http_method, path, planned_command) in question_expected.items():
            self.assertEqual(question[method_id].get("http_method"), http_method)
            self.assertEqual(question[method_id].get("path"), path)
            self.assertEqual(question[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", question[method_id]["flags"])
        self.assertIn("requires-ack-irreversible", question["faqQuestionEntryV2.deleteQuestionEntry"]["flags"])
        self.assertIn("requires-ack-irreversible", question["faqQuestionEntryV2.bulkDeleteQuestionEntries"]["flags"])

        for method_id in (
            "faqCategoryV2.categoryCreated",
            "faqCategoryV2.categoryDeleted",
            "faqCategoryV2.categoryUpdated",
            "faqQuestionEntryV2.questionEntryCreated",
            "faqQuestionEntryV2.questionEntryDeleted",
            "faqQuestionEntryV2.questionEntryUpdated",
        ):
            op = category.get(method_id) or question.get(method_id)
            self.assertIsNotNone(op)
            self.assertIn("callback-only", op["flags"])
            self.assertFalse(op["cli_callable"])

    def test_functions_v1_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("functions-v1", families)
        operations = {op["method_id"]: op for op in families["functions-v1"]["operations"]}
        expected = {
            "functionsV1.createFunction": ("POST", "/functions/v1/functions", "wix-safe-agent-cli functions-v1 create"),
            "functionsV1.getFunction": (
                "GET",
                "/functions/v1/functions/{functionId}",
                "wix-safe-agent-cli functions-v1 get",
            ),
            "functionsV1.updateFunction": (
                "PATCH",
                "/functions/v1/functions/{function.id}",
                "wix-safe-agent-cli functions-v1 update",
            ),
            "functionsV1.deleteFunction": (
                "DELETE",
                "/functions/v1/functions/{functionId}",
                "wix-safe-agent-cli functions-v1 delete",
            ),
            "functionsV1.queryFunctions": (
                "POST",
                "/functions/v1/functions/query",
                "wix-safe-agent-cli functions-v1 query",
            ),
            "functionsV1.bulkUpdateFunctionTags": (
                "POST",
                "/functions/v1/bulk/functions/bulk-update-tags",
                "wix-safe-agent-cli functions-v1 bulk-update-tags",
            ),
            "functionsV1.bulkUpdateFunctionTagsByFilter": (
                "POST",
                "/functions/v1/bulk/functions/update-tags-by-filter",
                "wix-safe-agent-cli functions-v1 bulk-update-tags-by-filter",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
        self.assertIn("requires-ack-irreversible", operations["functionsV1.deleteFunction"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["functionsV1.bulkUpdateFunctionTagsByFilter"]["flags"])

        for method_id in (
            "functionsV1.functionCreated",
            "functionsV1.functionDeleted",
            "functionsV1.functionTagsModified",
            "functionsV1.functionUpdated",
        ):
            op = operations[method_id]
            self.assertIn("callback-only", op["flags"])
            self.assertFalse(op["cli_callable"])

    def test_function_types_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("function-types", families)
        operations = {op["method_id"]: op for op in families["function-types"]["operations"]}
        expected = {
            "functionTypes.getFunctionType": (
                "GET",
                "/functions/v1/types/{appDefId}/{functionTypeId}",
                "wix-safe-agent-cli function-types get",
            ),
            "functionTypes.queryFunctionTypes": (
                "POST",
                "/functions/v1/types/query",
                "wix-safe-agent-cli function-types query",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])

    def test_function_templates_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("function-templates", families)
        operations = {op["method_id"]: op for op in families["function-templates"]["operations"]}
        expected = {
            "functionTemplates.getFunctionTemplate": (
                "GET",
                "/api/functions/v1/templates/{appDefId}/{functionTemplateId}",
                "wix-safe-agent-cli function-templates get",
            ),
            "functionTemplates.queryFunctionTemplates": (
                "POST",
                "/api/functions/v1/templates/query",
                "wix-safe-agent-cli function-templates query",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])

    def test_function_productions_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("function-productions", families)
        operations = {op["method_id"]: op for op in families["function-productions"]["operations"]}
        expected = {
            "functionProductions.createFunctionProduction": (
                "POST",
                "/functions/v1/productions",
                "wix-safe-agent-cli function-productions create",
            ),
            "functionProductions.updateFunctionProduction": (
                "PATCH",
                "/functions/v1/productions/{functionProduction.id}",
                "wix-safe-agent-cli function-productions update",
            ),
            "functionProductions.deleteFunctionProduction": (
                "DELETE",
                "/functions/v1/productions/{functionProductionId}",
                "wix-safe-agent-cli function-productions delete",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertIn("plan-first-write", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("requires-ack-irreversible", operations["functionProductions.deleteFunctionProduction"]["flags"])

    def test_builderless_productions_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("builderless-productions", families)
        operations = {op["method_id"]: op for op in families["builderless-productions"]["operations"]}
        expected = {
            "builderlessProductions.createFunctionBuilderlessProduction": (
                "POST",
                "/functions/v1/function-builderless-productions",
                "wix-safe-agent-cli builderless-productions create",
            ),
            "builderlessProductions.getFunctionBuilderlessProduction": (
                "GET",
                "/functions/v1/function-builderless-productions/{functionId}",
                "wix-safe-agent-cli builderless-productions get",
            ),
            "builderlessProductions.updateFunctionBuilderlessProduction": (
                "PATCH",
                "/functions/v1/function-builderless-productions/{functionBuilderlessProduction.id}",
                "wix-safe-agent-cli builderless-productions update",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("plan-first-write", operations["builderlessProductions.createFunctionBuilderlessProduction"]["flags"])
        self.assertIn("plan-first-write", operations["builderlessProductions.updateFunctionBuilderlessProduction"]["flags"])

    def test_function_methods_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("function-methods", families)
        operations = {op["method_id"]: op for op in families["function-methods"]["operations"]}
        expected = {
            "functionMethods.createFunctionMethod": (
                "POST",
                "/functions/v1/methods",
                "wix-safe-agent-cli function-methods create",
            ),
            "functionMethods.deleteFunctionMethod": (
                "DELETE",
                "/functions/v1/methods/{functionMethodId}",
                "wix-safe-agent-cli function-methods delete",
            ),
            "functionMethods.queryFunctionMethods": (
                "POST",
                "/functions/v1/methods/query",
                "wix-safe-agent-cli function-methods query",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("plan-first-write", operations["functionMethods.createFunctionMethod"]["flags"])
        self.assertIn("plan-first-write", operations["functionMethods.deleteFunctionMethod"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["functionMethods.deleteFunctionMethod"]["flags"])
        self.assertIn("callback-only", operations["functionMethods.functionMethodCreated"]["flags"])
        self.assertIn("callback-only", operations["functionMethods.functionMethodDeleted"]["flags"])

    def test_function_activations_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("function-activations", families)
        operations = {op["method_id"]: op for op in families["function-activations"]["operations"]}
        expected = {
            "functionActivations.upsertFunctionActivation": (
                "POST",
                "/functions/v1/activations/upsert",
                "wix-safe-agent-cli function-activations upsert",
            ),
            "functionActivations.deleteFunctionActivation": (
                "DELETE",
                "/functions/v1/activations/{functionId}",
                "wix-safe-agent-cli function-activations delete",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertIn("plan-first-write", operations[method_id]["flags"])
            self.assertIn("requires-ack-irreversible", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])

    def test_function_spi_configurations_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("function-spi-configurations", families)
        operations = {op["method_id"]: op for op in families["function-spi-configurations"]["operations"]}
        expected = {
            "functionSpiConfigurations.createFunctionSpiConfiguration": (
                "POST",
                "/functions/v1/function-spi-configurations",
                "wix-safe-agent-cli function-spi-configurations create",
            ),
            "functionSpiConfigurations.getFunctionSpiConfiguration": (
                "GET",
                "/functions/v1/function-spi-configurations/{functionSpiConfigurationId}",
                "wix-safe-agent-cli function-spi-configurations get",
            ),
            "functionSpiConfigurations.updateFunctionSpiConfiguration": (
                "PATCH",
                "/functions/v1/function-spi-configurations/{functionSpiConfiguration.id}",
                "wix-safe-agent-cli function-spi-configurations update",
            ),
            "functionSpiConfigurations.deleteFunctionSpiConfiguration": (
                "DELETE",
                "/functions/v1/function-spi-configurations/{functionSpiConfigurationId}",
                "wix-safe-agent-cli function-spi-configurations delete",
            ),
            "functionSpiConfigurations.queryFunctionSpiConfigurations": (
                "POST",
                "/functions/v1/function-spi-configurations/query",
                "wix-safe-agent-cli function-spi-configurations query",
            ),
            "functionSpiConfigurations.validateFunctionSpiConfiguration": (
                "POST",
                "/functions/v1/function-spi-configurations/validate",
                "wix-safe-agent-cli function-spi-configurations validate",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("plan-first-write", operations["functionSpiConfigurations.createFunctionSpiConfiguration"]["flags"])
        self.assertIn("plan-first-write", operations["functionSpiConfigurations.updateFunctionSpiConfiguration"]["flags"])
        self.assertIn("plan-first-write", operations["functionSpiConfigurations.deleteFunctionSpiConfiguration"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["functionSpiConfigurations.deleteFunctionSpiConfiguration"]["flags"])
        self.assertIn("callback-only", operations["functionSpiConfigurations.spiConfigurationCreated"]["flags"])
        self.assertIn("callback-only", operations["functionSpiConfigurations.spiConfigurationDeleted"]["flags"])
        self.assertIn("callback-only", operations["functionSpiConfigurations.spiConfigurationUpdated"]["flags"])

    def test_payment_link_settings_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("payment-link-settings", families)
        operations = {op["method_id"]: op for op in families["payment-link-settings"]["operations"]}
        expected = {
            "paymentLinksSettings.getPaymentLinksSettings": (
                "GET",
                "/payment-links/v1/payment-links-settings",
                "wix-safe-agent-cli payment-link-settings get",
            ),
            "paymentLinksSettings.updatePaymentLinksSettings": (
                "PATCH",
                "/payment-links/v1/payment-links-settings",
                "wix-safe-agent-cli payment-link-settings update",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("plan-first-write", operations["paymentLinksSettings.updatePaymentLinksSettings"]["flags"])

    def test_get_paid_bulk_downloads_are_developer_preview_not_callable(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("get-paid-bulk-downloads", families)
        self.assertEqual(families["get-paid-bulk-downloads"].get("coverage_status"), "developer-preview")
        for operation in families["get-paid-bulk-downloads"]["operations"]:
            if "developer-preview" in operation["flags"]:
                self.assertFalse(operation["cli_callable"])
                self.assertIsNone(operation.get("planned_command"))

    def test_billable_items_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("billable-items", families)
        operations = {op["method_id"]: op for op in families["billable-items"]["operations"]}
        expected = {
            "billableItems.createBillableItem": (
                "POST",
                "/billable-items/v1/billable-items",
                "wix-safe-agent-cli billable-items create",
            ),
            "billableItems.getBillableItem": (
                "GET",
                "/billable-items/v1/billable-items/{billableItemId}",
                "wix-safe-agent-cli billable-items get",
            ),
            "billableItems.updateBillableItem": (
                "PATCH",
                "/billable-items/v1/billable-items/{billableItem.id}",
                "wix-safe-agent-cli billable-items update",
            ),
            "billableItems.deleteBillableItem": (
                "DELETE",
                "/billable-items/v1/billable-items/{billableItemId}",
                "wix-safe-agent-cli billable-items delete",
            ),
            "billableItems.queryBillableItems": (
                "POST",
                "/billable-items/v1/billable-items/query",
                "wix-safe-agent-cli billable-items query",
            ),
            "billableItems.searchBillableItems": (
                "POST",
                "/billable-items/v1/billable-items/search",
                "wix-safe-agent-cli billable-items search",
            ),
            "billableItems.bulkCreateBillableItems": (
                "POST",
                "/billable-items/v1/bulk/billable-items/create",
                "wix-safe-agent-cli billable-items bulk-create",
            ),
            "billableItems.bulkDeleteBillableItems": (
                "POST",
                "/billable-items/v1/bulk/billable-items/delete",
                "wix-safe-agent-cli billable-items bulk-delete",
            ),
            "billableItems.bulkUpdateBillableItems": (
                "POST",
                "/billable-items/v1/bulk/billable-items/update",
                "wix-safe-agent-cli billable-items bulk-update",
            ),
            "billableItems.bulkUpdateBillableItemTags": (
                "POST",
                "/billable-items/v1/bulk/billable-items/update-tags",
                "wix-safe-agent-cli billable-items bulk-update-tags",
            ),
            "billableItems.bulkUpdateBillableItemTagsByFilter": (
                "POST",
                "/billable-items/v1/bulk/billable-items/update-tags-by-filter",
                "wix-safe-agent-cli billable-items bulk-update-tags-by-filter",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("developer-preview", operations["billableItems.createBillableItem"]["flags"])
        self.assertIn("developer-preview", operations["billableItems.searchBillableItems"]["flags"])
        self.assertIn("developer-preview", operations["billableItems.bulkUpdateBillableItems"]["flags"])
        self.assertIn("requires-current-revision", operations["billableItems.updateBillableItem"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["billableItems.deleteBillableItem"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["billableItems.bulkDeleteBillableItems"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["billableItems.bulkUpdateBillableItemTagsByFilter"]["flags"])
        self.assertIn("callback-only", operations["billableItems.billableItemCreated"]["flags"])
        self.assertIn("callback-only", operations["billableItems.billableItemDeleted"]["flags"])
        self.assertIn("callback-only", operations["billableItems.billableItemUpdated"]["flags"])

    def test_payment_links_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("payment-links", families)
        operations = {op["method_id"]: op for op in families["payment-links"]["operations"]}
        expected = {
            "paymentLinks.createPaymentLink": (
                "POST",
                "/payment-links/v1/payment-links",
                "wix-safe-agent-cli payment-links create",
            ),
            "paymentLinks.getPaymentLink": (
                "GET",
                "/payment-links/v1/payment-links/{paymentLinkId}",
                "wix-safe-agent-cli payment-links get",
            ),
            "paymentLinks.deletePaymentLink": (
                "DELETE",
                "/payment-links/v1/payment-links/{paymentLinkId}",
                "wix-safe-agent-cli payment-links delete",
            ),
            "paymentLinks.queryPaymentLinks": (
                "POST",
                "/payment-links/v1/payment-links/query",
                "wix-safe-agent-cli payment-links query",
            ),
            "paymentLinks.searchPaymentLinks": (
                "POST",
                "/payment-links/v1/payment-links/search",
                "wix-safe-agent-cli payment-links search",
            ),
            "paymentLinks.activatePaymentLink": (
                "POST",
                "/payment-links/v1/payment-links/{paymentLinkId}/activate",
                "wix-safe-agent-cli payment-links activate",
            ),
            "paymentLinks.deactivatePaymentLink": (
                "POST",
                "/payment-links/v1/payment-links/{paymentLinkId}/deactivate",
                "wix-safe-agent-cli payment-links deactivate",
            ),
            "paymentLinks.initiatePayment": (
                "POST",
                "/payment-links/v1/payment-links/{paymentLinkId}/initiate-payment",
                "wix-safe-agent-cli payment-links initiate-payment",
            ),
            "paymentLinks.sendPaymentLink": (
                "POST",
                "/payment-links/v1/payment-links/{paymentLinkId}/send",
                "wix-safe-agent-cli payment-links send",
            ),
            "paymentLinks.setNote": (
                "POST",
                "/payment-links/v1/payment-links/{paymentLinkId}/set-note",
                "wix-safe-agent-cli payment-links set-note",
            ),
            "paymentLinks.updateExtendedFields": (
                "POST",
                "/payment-links/v1/payment-links/{id}/update-extended-fields",
                "wix-safe-agent-cli payment-links update-extended-fields",
            ),
            "paymentLinks.bulkUpdatePaymentLinkTags": (
                "POST",
                "/payment-links/v1/payment-links/bulk-update-tags",
                "wix-safe-agent-cli payment-links bulk-update-tags",
            ),
            "paymentLinks.bulkUpdatePaymentLinkTagsByFilter": (
                "POST",
                "/payment-links/v1/bulk/payment-links/update-tags-by-filter",
                "wix-safe-agent-cli payment-links bulk-update-tags-by-filter",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("requires-ack-irreversible", operations["paymentLinks.createPaymentLink"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["paymentLinks.deletePaymentLink"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["paymentLinks.activatePaymentLink"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["paymentLinks.deactivatePaymentLink"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["paymentLinks.sendPaymentLink"]["flags"])
        self.assertIn("async-job", operations["paymentLinks.bulkUpdatePaymentLinkTagsByFilter"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["paymentLinks.bulkUpdatePaymentLinkTagsByFilter"]["flags"])
        self.assertIn("callback-only", operations["paymentLinks.paymentLinkCreated"]["flags"])
        self.assertIn("callback-only", operations["paymentLinks.paymentLinkDeleted"]["flags"])
        self.assertIn("callback-only", operations["paymentLinks.paymentLinkActivated"]["flags"])
        self.assertIn("callback-only", operations["paymentLinks.paymentLinkDeactivated"]["flags"])
        self.assertIn("callback-only", operations["paymentLinks.paymentLinkNoteSet"]["flags"])
        self.assertIn("callback-only", operations["paymentLinks.paymentLinkPaymentInitiated"]["flags"])
        self.assertIn("callback-only", operations["paymentLinks.paymentLinkSent"]["flags"])
        self.assertIn("callback-only", operations["paymentLinks.paymentLinkUpdated"]["flags"])

    def test_payment_link_payments_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("payment-link-payments", families)
        operations = {op["method_id"]: op for op in families["payment-link-payments"]["operations"]}
        expected = {
            "paymentLinkPayments.queryPaymentLinkPayments": (
                "POST",
                "/payment-links/v1/payment-link-payments/query",
                "wix-safe-agent-cli payment-link-payments query",
            ),
            "paymentLinkPayments.searchPaymentLinkPayments": (
                "POST",
                "/payment-links/v1/payment-link-payments/search",
                "wix-safe-agent-cli payment-link-payments search",
            ),
            "paymentLinkPayments.issueReceipt": (
                "POST",
                "/payment-links/v1/payment-link-payments/{paymentLinkPaymentId}/issue-receipt",
                "wix-safe-agent-cli payment-link-payments issue-receipt",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("plan-first-write", operations["paymentLinkPayments.issueReceipt"]["flags"])
        self.assertIn("callback-only", operations["paymentLinkPayments.paymentLinkPaymentCreated"]["flags"])
        self.assertIn("callback-only", operations["paymentLinkPayments.paymentLinkPaymentUpdated"]["flags"])

    def test_receipts_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("receipts", families)
        operations = {op["method_id"]: op for op in families["receipts"]["operations"]}
        expected = {
            "receipts.createReceipt": (
                "POST",
                "/receipts/v1/receipts",
                "wix-safe-agent-cli receipts create",
            ),
            "receipts.getReceipt": (
                "GET",
                "/receipts/v1/receipts/{receiptId}",
                "wix-safe-agent-cli receipts get",
            ),
            "receipts.queryReceipts": (
                "POST",
                "/receipts/v1/receipts/query",
                "wix-safe-agent-cli receipts query",
            ),
            "receipts.getLatestReceiptNumber": (
                "GET",
                "/receipts/v1/receipts/get-latest-number",
                "wix-safe-agent-cli receipts get-latest-number",
            ),
            "receipts.regenerateReceiptDocument": (
                "POST",
                "/receipts/v1/receipts/{receiptId}/regenerate-receipt-document",
                "wix-safe-agent-cli receipts regenerate-document",
            ),
            "receipts.sendReceiptEmail": (
                "POST",
                "/receipts/v1/receipts/{receiptId}/send-email",
                "wix-safe-agent-cli receipts send-email",
            ),
            "receipts.updateExtendedFields": (
                "POST",
                "/receipts/v1/receipts/{id}/update-extended-fields",
                "wix-safe-agent-cli receipts update-extended-fields",
            ),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("requires-ack-irreversible", operations["receipts.createReceipt"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["receipts.sendReceiptEmail"]["flags"])
        self.assertIn("callback-only", operations["receipts.receiptCreated"]["flags"])
        self.assertIn("callback-only", operations["receipts.receiptSent"]["flags"])
        self.assertIn("callback-only", operations["receipts.receiptUpdated"]["flags"])

    def test_receipt_presets_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("receipt-presets", families)
        operations = {op["method_id"]: op for op in families["receipt-presets"]["operations"]}
        expected = {
            "receiptPresets.createReceiptPreset": ("POST", "/receipts/v1/receipt-presets", "wix-safe-agent-cli receipt-presets create"),
            "receiptPresets.getReceiptPreset": ("GET", "/receipts/v1/receipt-presets/{receiptPresetId}", "wix-safe-agent-cli receipt-presets get"),
            "receiptPresets.updateReceiptPreset": ("PATCH", "/receipts/v1/receipt-presets/{receiptPreset.id}", "wix-safe-agent-cli receipt-presets update"),
            "receiptPresets.deleteReceiptPreset": ("DELETE", "/receipts/v1/receipt-presets/{receiptPresetId}", "wix-safe-agent-cli receipt-presets delete"),
            "receiptPresets.listReceiptPresets": ("GET", "/receipts/v1/receipt-presets", "wix-safe-agent-cli receipt-presets list"),
            "receiptPresets.getDefaultReceiptPreset": ("GET", "/receipts/v1/receipt-presets/default", "wix-safe-agent-cli receipt-presets get-default"),
            "receiptPresets.setDefaultReceiptPreset": ("POST", "/receipts/v1/receipt-presets/default/{receiptPresetId}", "wix-safe-agent-cli receipt-presets set-default"),
            "receiptPresets.updateExtendedFields": ("POST", "/receipts/v1/receipt-presets/{id}/update-extended-fields", "wix-safe-agent-cli receipt-presets update-extended-fields"),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("requires-current-revision", operations["receiptPresets.updateReceiptPreset"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["receiptPresets.deleteReceiptPreset"]["flags"])
        self.assertIn("callback-only", operations["receiptPresets.receiptPresetCreated"]["flags"])
        self.assertIn("callback-only", operations["receiptPresets.receiptPresetDeleted"]["flags"])
        self.assertIn("callback-only", operations["receiptPresets.receiptPresetUpdated"]["flags"])

    def test_receipts_settings_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("receipts-settings", families)
        operations = {op["method_id"]: op for op in families["receipts-settings"]["operations"]}
        expected = {
            "receiptsSettings.getReceiptsSettings": ("GET", "/receipts/v1/receipts-settings", "wix-safe-agent-cli receipts-settings get"),
            "receiptsSettings.updateReceiptsSettings": ("PATCH", "/receipts/v1/receipts-settings", "wix-safe-agent-cli receipts-settings update"),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("requires-current-revision", operations["receiptsSettings.updateReceiptsSettings"]["flags"])
        self.assertIn("callback-only", operations["receiptsSettings.receiptsSettingsUpdated"]["flags"])

    def test_headless_oauth_apps_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("headless-oauth-apps", families)
        operations = {op["method_id"]: op for op in families["headless-oauth-apps"]["operations"]}
        expected = {
            "headlessOauthApps.createOAuthApp": ("POST", "/oauth-app/v1/oauth-apps", "wix-safe-agent-cli headless-oauth-apps create"),
            "headlessOauthApps.getOAuthApp": ("GET", "/oauth-app/v1/oauth-apps/{oAuthAppId}", "wix-safe-agent-cli headless-oauth-apps get"),
            "headlessOauthApps.updateOAuthApp": ("PATCH", "/oauth-app/v1/oauth-apps/{oAuthApp.id}", "wix-safe-agent-cli headless-oauth-apps update"),
            "headlessOauthApps.queryOAuthApps": ("POST", "/oauth-app/v1/oauth-apps/query", "wix-safe-agent-cli headless-oauth-apps query"),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("plan-first-write", operations["headlessOauthApps.createOAuthApp"]["flags"])
        self.assertIn("requires-mask-paths", operations["headlessOauthApps.updateOAuthApp"]["flags"])
        self.assertIn("read-helper-post", operations["headlessOauthApps.queryOAuthApps"]["flags"])
        self.assertIn("callback-only", operations["headlessOauthApps.oauthAppCreated"]["flags"])
        self.assertIn("callback-only", operations["headlessOauthApps.oauthAppDeleted"]["flags"])
        self.assertIn("callback-only", operations["headlessOauthApps.oauthAppUpdated"]["flags"])

    def test_headless_authentication_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("headless-authentication", families)
        operations = {op["method_id"]: op for op in families["headless-authentication"]["operations"]}
        expected = {
            "headlessAuthentication.loginV2": ("POST", "/_api/iam/authentication/v2/login", "wix-safe-agent-cli headless-authentication login-v2"),
            "headlessAuthentication.retrieveTokens": ("POST", "/oauth2/token", "wix-safe-agent-cli headless-authentication retrieve-tokens"),
            "headlessAuthentication.registerV2": ("POST", "/_api/iam/authentication/v2/register", "wix-safe-agent-cli headless-authentication register-v2"),
            "headlessAuthentication.changePassword": ("POST", "/_api/iam/authentication/v2/change-password", "wix-safe-agent-cli headless-authentication change-password"),
            "headlessAuthentication.logout": ("GET", "/_api/iam/authentication/v1/logout", "wix-safe-agent-cli headless-authentication logout"),
            "headlessAuthentication.signOn": ("POST", "/_api/iam/authentication/v2/sign-on", "wix-safe-agent-cli headless-authentication sign-on"),
        }
        for method_id, (http_method, path, planned_command) in expected.items():
            self.assertEqual(operations[method_id].get("http_method"), http_method)
            self.assertEqual(operations[method_id].get("path"), path)
            self.assertEqual(operations[method_id].get("planned_command"), planned_command)
            self.assertIn("implemented", operations[method_id]["flags"])
            self.assertIn("sensitive-output-redacted", operations[method_id]["flags"])
            self.assertTrue(operations[method_id]["cli_callable"])
        self.assertIn("oauth-client-request", operations["headlessAuthentication.retrieveTokens"]["flags"])
        self.assertIn("plan-first-write", operations["headlessAuthentication.registerV2"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["headlessAuthentication.changePassword"]["flags"])
        self.assertIn("requires-ack-irreversible", operations["headlessAuthentication.signOn"]["flags"])

    def test_headless_recovery_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("headless-recovery", families)
        operations = {op["method_id"]: op for op in families["headless-recovery"]["operations"]}
        operation = operations["headlessRecovery.sendRecoveryEmail"]
        self.assertEqual(operation.get("http_method"), "POST")
        self.assertEqual(operation.get("path"), "/_api/iam/recovery/v1/send-email")
        self.assertEqual(operation.get("planned_command"), "wix-safe-agent-cli headless-recovery send-recovery-email")
        self.assertIn("implemented", operation["flags"])
        self.assertIn("plan-first-write", operation["flags"])
        self.assertIn("requires-ack-irreversible", operation["flags"])
        self.assertIn("sensitive-output-redacted", operation["flags"])
        self.assertTrue(operation["cli_callable"])

    def test_headless_redirects_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("headless-redirects", families)
        operations = {op["method_id"]: op for op in families["headless-redirects"]["operations"]}
        operation = operations["headlessRedirects.createRedirectSession"]
        self.assertEqual(operation.get("http_method"), "POST")
        self.assertEqual(operation.get("path"), "/_api/redirects-api/v1/redirect-session")
        self.assertEqual(
            operation.get("planned_command"),
            "wix-safe-agent-cli headless-redirects create-redirect-session",
        )
        self.assertIn("implemented", operation["flags"])
        self.assertIn("developer-preview", operation["flags"])
        self.assertIn("plan-first-write", operation["flags"])
        self.assertIn("requires-ack-irreversible", operation["flags"])
        self.assertIn("sensitive-output-redacted", operation["flags"])
        self.assertIn("docs-endpoint-mismatch", operation["flags"])
        self.assertTrue(operation["cli_callable"])
        self.assertIn("callback-only", operations["headlessRedirects.redirectSessionCreated"]["flags"])

    def test_headless_sitemap_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("headless-sitemap", families)
        operations = {op["method_id"]: op for op in families["headless-sitemap"]["operations"]}
        operation = operations["headlessSitemap.listSitemapPages"]
        self.assertEqual(operation.get("http_method"), "GET")
        self.assertEqual(operation.get("path"), "/v1/list-sitemap-pages")
        self.assertEqual(operation.get("planned_command"), "wix-safe-agent-cli headless-sitemap list-pages")
        self.assertIn("implemented", operation["flags"])
        self.assertIn("read-only", operation["flags"])
        self.assertIn("docs-endpoint-mismatch", operation["flags"])
        self.assertTrue(operation["cli_callable"])

    def test_headless_verification_family_present_and_implemented(self) -> None:
        inventory = self._load_inventory()
        families = {family["slug"]: family for family in inventory["families"]}

        self.assertIn("headless-verification", families)
        operations = {op["method_id"]: op for op in families["headless-verification"]["operations"]}
        operation = operations["headlessVerification.verifyDuringAuthentication"]
        self.assertEqual(operation.get("http_method"), "POST")
        self.assertEqual(operation.get("path"), "/_api/iam/verification/v1/auth/verify")
        self.assertEqual(
            operation.get("planned_command"),
            "wix-safe-agent-cli headless-verification verify-during-authentication",
        )
        self.assertIn("implemented", operation["flags"])
        self.assertIn("developer-preview", operation["flags"])
        self.assertIn("plan-first-write", operation["flags"])
        self.assertIn("sensitive-output-redacted", operation["flags"])
        self.assertIn("docs-endpoint-mismatch", operation["flags"])
        self.assertTrue(operation["cli_callable"])

    def test_implemented_inventory_commands_exist_in_parser(self) -> None:
        inventory = self._load_inventory()
        parser_commands = self._collect_parser_command_paths()

        implemented_commands: set[str] = set()
        for family in inventory["families"]:
            for op in family["operations"]:
                if "implemented" in op.get("flags", []):
                    planned_command = op.get("planned_command")
                    self.assertIsNotNone(planned_command, f"Implemented operation missing planned command: {op['method_id']}")
                    implemented_commands.add(str(planned_command))

        missing = sorted(command for command in implemented_commands if command not in parser_commands)
        self.assertEqual(missing, [], f"Implemented inventory commands missing from parser: {missing}")

    def test_callback_only_operations_do_not_claim_cli_commands(self) -> None:
        inventory = self._load_inventory()
        for family in inventory["families"]:
            for op in family["operations"]:
                if "callback-only" in op.get("flags", []):
                    self.assertIsNone(op.get("planned_command"))
                    self.assertIsNone(op.get("http_method"))
                    self.assertIsNone(op.get("path"))

    def test_docs_only_operations_do_not_claim_cli_commands(self) -> None:
        inventory = self._load_inventory()
        for family in inventory["families"]:
            for op in family["operations"]:
                if "docs-only" in op.get("flags", []):
                    self.assertIsNone(op.get("planned_command"))
                    self.assertIsNone(op.get("http_method"))
                    self.assertIsNone(op.get("path"))

    def test_site_defined_operations_do_not_claim_cli_commands(self) -> None:
        inventory = self._load_inventory()
        for family in inventory["families"]:
            for op in family["operations"]:
                if "site-defined" in op.get("flags", []):
                    self.assertIsNone(op.get("planned_command"))
                    self.assertIsNone(op.get("http_method"))
                    self.assertIsNone(op.get("path"))
