from __future__ import annotations

import unittest

from fortnox_api_tool.rest_inventory import (
    find_operation,
    load_rest_inventory,
    load_rest_operations,
    operation_ids,
    planned_cli_commands,
)


class TestRestInventory(unittest.TestCase):
    def test_rest_inventory_totals_match_coverage_lock(self) -> None:
        inventory = load_rest_inventory()
        self.assertRegex(inventory.audited_utc, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(inventory.rendered_family_count, 81)
        self.assertEqual(inventory.unique_family_slug_count, 79)
        self.assertEqual(inventory.operation_count, 377)
        self.assertEqual(len(inventory.operations), 377)
        self.assertEqual(sum(item.operation_count for item in inventory.group_summaries), 377)

    def test_planned_cli_commands_are_unique(self) -> None:
        commands = planned_cli_commands()
        self.assertEqual(len(commands), 377)
        self.assertEqual(len(commands), len(set(commands)))

    def test_operation_ids_are_unique(self) -> None:
        ids = operation_ids()
        self.assertEqual(len(ids), 377)
        self.assertEqual(len(ids), len(set(ids)))

    def test_expected_sample_operations_are_present(self) -> None:
        invoice_list = find_operation("InvoiceController_doIndex")
        self.assertIsNotNone(invoice_list)
        self.assertEqual(invoice_list.http_method, "GET")
        self.assertEqual(invoice_list.path, "/3/invoices")
        self.assertEqual(invoice_list.cli_command, "fortnox-api-tool invoices list")

        stockbalance = find_operation("getStockBalance")
        self.assertIsNotNone(stockbalance)
        self.assertEqual(stockbalance.family_slug, "stock-status")
        self.assertEqual(stockbalance.cli_command, "fortnox-api-tool stock-status get-stock-balance")

        supplier_invoice_credit = find_operation("SupplierInvoiceController_doUpdateAndCredit")
        self.assertIsNotNone(supplier_invoice_credit)
        self.assertEqual(
            supplier_invoice_credit.cli_command,
            "fortnox-api-tool supplier-invoices credit",
        )

        article_url_connection_get = find_operation("ItemUrlConnectionController_doShow")
        self.assertIsNotNone(article_url_connection_get)
        self.assertEqual(article_url_connection_get.path, "/3/articleurlconnections/{id}")
        self.assertEqual(article_url_connection_get.cli_command, "fortnox-api-tool article-url-connections get")

    def test_articles_family_keeps_both_official_rendered_tags(self) -> None:
        operations = [item for item in load_rest_operations() if item.family_slug == "articles"]
        self.assertEqual(len(operations), 6)
        self.assertTrue(
            any(item.path == "/3/articles" for item in operations),
            "Expected the Fortnox master-data Articles endpoints to be present.",
        )
        self.assertTrue(
            any(item.path == "/api/time/articles-v1" for item in operations),
            "Expected the time-reporting Articles endpoint to be merged into the same CLI family.",
        )
