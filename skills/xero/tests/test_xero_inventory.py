from __future__ import annotations

import json
import os
import re
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from xero_safe_agent_cli import openapi_inventory

PINNED_COMMIT = "e952d0bda3628facbf7afc5990ad6a0e7e77bd1e"
PINNED_RELEASE = "16.1.0"
CHECKOUT_ENV = "XERO_OPENAPI_CHECKOUT"
CATALOG_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "xero_safe_agent_cli"
    / "generated"
    / "operations.json"
)


def configured_checkout() -> Path | None:
    raw = os.environ.get(CHECKOUT_ENV, "").strip()
    if not raw:
        return None
    checkout = Path(raw).expanduser().resolve()
    if not checkout.is_dir():
        raise AssertionError(f"{CHECKOUT_ENV} is not a directory: {checkout}")
    return checkout


class TestXeroInventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.operations = cls.catalog["operations"]

    def test_clean_checkout_configuration_is_optional_and_portable(self) -> None:
        with patch.dict(os.environ, {CHECKOUT_ENV: ""}):
            self.assertIsNone(configured_checkout())
        self.assertEqual(self.catalog["source"]["commit"], PINNED_COMMIT)

    def test_modified_pinned_spec_is_refused_before_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "xero_accounting.yaml").write_text("modified: true\n", encoding="utf-8")
            with patch.object(openapi_inventory, "_git_commit", return_value=PINNED_COMMIT):
                with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                    openapi_inventory.build_inventory(root)

    def test_pinned_boundary_accounts_for_every_openapi_operation(self) -> None:
        source = self.catalog["source"]
        self.assertEqual(source["commit"], PINNED_COMMIT)
        self.assertEqual(source["release"], PINNED_RELEASE)
        self.assertEqual(source["executable_spec_count"], 12)
        self.assertEqual(source["callback_spec_count"], 1)
        self.assertEqual(source["openapi_operation_count"], 477)
        self.assertEqual(
            source["methods"],
            {"DELETE": 29, "GET": 254, "PATCH": 1, "POST": 121, "PUT": 72},
        )
        self.assertEqual(
            source["operations_by_spec"],
            {
                "accounting": 235,
                "app-store": 4,
                "assets": 6,
                "bank-feeds": 7,
                "files": 18,
                "finance": 8,
                "identity": 2,
                "payroll-au": 32,
                "payroll-au-v2": 9,
                "payroll-nz": 71,
                "payroll-uk": 69,
                "projects": 16,
            },
        )

    def test_fixed_commands_and_manual_supplements_are_deterministic(self) -> None:
        commands = [row["command"] for row in self.operations if row["command"]]
        self.assertEqual(len(commands), 474)
        self.assertEqual(len(commands), len(set(commands)))
        self.assertTrue(all(re.fullmatch(r"[a-z0-9-]+\.[a-z0-9-]+", value) for value in commands))
        self.assertEqual(
            Counter(row["disposition"] for row in self.operations),
            {"command": 474, "superseded_compatibility": 5},
        )
        self.assertEqual(
            {
                row["command"]
                for row in self.operations
                if row.get("source_kind") == "official_docs_manual"
            },
            {
                "einvoicing.get-registration",
                "einvoicing.register-by-business-number",
            },
        )

    def test_superseded_au_compatibility_operations_have_no_commands(self) -> None:
        superseded = {
            row["operation_id"]: row
            for row in self.operations
            if row["disposition"] == "superseded_compatibility"
        }
        self.assertEqual(
            set(superseded),
            {
                "createTimesheet",
                "getLeaveApplications",
                "getTimesheet",
                "getTimesheets",
                "updateTimesheet",
            },
        )
        self.assertTrue(all(row["spec_id"] == "payroll-au" for row in superseded.values()))
        self.assertTrue(all(row["command"] is None for row in superseded.values()))
        self.assertTrue(all(row["superseded_by"] for row in superseded.values()))

    def test_verification_commands_never_cross_api_family(self) -> None:
        by_command = {row["command"]: row for row in self.operations if row.get("command")}
        for row in by_command.values():
            verification_command = row.get("verification_command")
            if verification_command:
                self.assertEqual(
                    row["spec_id"],
                    by_command[verification_command]["spec_id"],
                    f"{row['command']} crosses to {verification_command}",
                )

    def test_access_region_auth_and_callback_classification_is_explicit(self) -> None:
        by_command = {row["command"]: row for row in self.operations if row["command"]}
        self.assertEqual(by_command["payroll-au-v2.get-timesheets"]["region"], "AU")
        self.assertEqual(by_command["payroll-nz.get-employees"]["region"], "NZ")
        self.assertEqual(by_command["payroll-uk.get-employees"]["region"], "UK")
        self.assertEqual(by_command["app-store.get-subscription"]["auth_flow"], "client_credentials")
        self.assertFalse(by_command["app-store.get-subscription"]["tenant_required"])
        self.assertEqual(by_command["app-store.get-subscription"]["region"], "AU,NZ,UK")
        self.assertIn(
            "legacy Xero App Store partner and marketplace billing access in AU, NZ, and UK",
            by_command["app-store.get-subscription"]["access_reason"],
        )
        identity_connections = by_command["identity.get-connections"]
        self.assertEqual(identity_connections["auth_flow"], "client_credentials")
        self.assertEqual(identity_connections["minimum_scopes"], ["app.connections"])
        self.assertFalse(identity_connections["tenant_required"])
        self.assertEqual(
            identity_connections["required_one_of_headers"],
            ["Xero-Tenant-Id", "Xero-User-Id"],
        )
        self.assertEqual(
            by_command["accounting.get-invoices"]["minimum_scopes"],
            ["accounting.invoices.read"],
        )
        self.assertEqual(
            by_command["accounting.create-invoices"]["minimum_scopes"],
            ["accounting.invoices"],
        )
        self.assertTrue(by_command["accounting.get-payment-services"]["access_gated"])
        self.assertTrue(by_command["bank-feeds.create-statements"]["access_gated"])
        self.assertTrue(by_command["assets.get-assets"]["sensitive_output"])
        self.assertTrue(by_command["finance.get-cash-validation"]["sensitive_output"])
        self.assertTrue(by_command["projects.get-project-users"]["sensitive_output"])
        self.assertTrue(by_command["projects.get-time-entries"]["sensitive_output"])
        self.assertTrue(by_command["assets.create-asset"]["extra_approval"])
        self.assertTrue(by_command["assets.create-asset-type"]["extra_approval"])
        self.assertIn("financial", by_command["projects.create-time-entry"]["risk_flags"])
        self.assertTrue(by_command["projects.create-time-entry"]["extra_approval"])
        registration = by_command["einvoicing.register-by-business-number"]
        self.assertEqual(registration["method"], "PUT")
        self.assertIsNone(registration["request"])
        self.assertEqual(registration["region"], "AU,NZ")
        self.assertIn("Standard or Adviser role", registration["access_reason"])
        self.assertEqual(registration["tenant_bound_path_parameters"], ["organisationId"])
        self.assertEqual(
            by_command["accounting.get-organisation-cissettings"][
                "tenant_bound_path_parameters"
            ],
            ["OrganisationID"],
        )
        self.assertEqual(self.catalog["manual_boundaries"]["webhooks"]["disposition"], "callback_only")
        self.assertEqual(
            self.catalog["manual_boundaries"]["practice_manager"]["disposition"],
            "access_gated_docs_only",
        )
        self.assertEqual(
            self.catalog["manual_boundaries"]["xero_hq"]["disposition"],
            "access_gated_docs_only",
        )
        self.assertEqual(
            self.catalog["manual_boundaries"]["xero_tax"]["disposition"],
            "access_gated_docs_only",
        )
        payment_commands = {
            command
            for command, row in by_command.items()
            if "paymentservices" in row["minimum_scopes"]
        }
        self.assertEqual(
            set(self.catalog["manual_boundaries"]["payment_services"]["commands"]),
            payment_commands,
        )
        self.assertEqual(
            self.catalog["manual_boundaries"]["payment_services"]["callable_operations"],
            4,
        )
        self.assertEqual(
            by_command["accounting.get-reports-list"]["minimum_scopes"],
            ["accounting.reports.taxreports.read"],
        )
        self.assertEqual(
            by_command["accounting.get-report-from-id"]["minimum_scopes"],
            ["accounting.reports.taxreports.read"],
        )
        self.assertEqual(by_command["accounting.get-reports-list"]["region"], "AU,NZ")
        self.assertEqual(by_command["accounting.get-report-from-id"]["region"], "AU,NZ")
        report_1099 = by_command["accounting.get-report-ten-ninety-nine"]
        self.assertEqual(report_1099["region"], "US")
        self.assertIn("Adviser", report_1099["access_reason"])
        for command in (
            "accounting.get-reports-list",
            "accounting.get-journals",
            "accounting.get-manual-journals",
        ):
            self.assertIn("reporting permission", by_command[command]["access_reason"])
        self.assertEqual(
            by_command["accounting.get-organisation-cissettings"]["region"], "UK"
        )
        self.assertEqual(
            by_command["accounting.get-contact-cissettings"]["region"], "UK"
        )
        self.assertEqual(
            by_command["finance.get-financial-statement-cashflow"]["excluded_regions"],
            ["US"],
        )
        self.assertIn(
            "closed API", by_command["finance.get-cash-validation"]["access_reason"]
        )
        self.assertIn(
            "10 July 2018",
            by_command["accounting.get-expense-claims"]["access_reason"],
        )
        self.assertIn(
            "10 July 2018", by_command["accounting.get-receipts"]["access_reason"]
        )
        for command in (
            "payroll-au.get-employees",
            "payroll-au-v2.get-timesheets",
            "payroll-nz.get-employees",
            "payroll-uk.get-employees",
        ):
            self.assertTrue(by_command[command]["access_gated"])
            self.assertIn("Payroll Admin", by_command[command]["access_reason"])
        self.assertIn(
            "partner permissions", by_command["payroll-uk.get-employees"]["access_reason"]
        )
        self.assertIn(
            "financial institutions",
            by_command["bank-feeds.get-feed-connections"]["access_reason"],
        )
        self.assertIn(
            "Projects product",
            by_command["projects.get-projects"]["access_reason"],
        )
        for command in (
            "accounting.create-contacts",
            "accounting.create-invoices",
            "accounting.create-credit-notes",
        ):
            self.assertIn("BankAccountAdmin", by_command[command]["access_reason"])
        self.assertIn(
            "29 April 2026", by_command["accounting.get-journals"]["access_reason"]
        )

    def test_all_app_store_commands_carry_the_xass_lifecycle_warning(self) -> None:
        expected = (
            "legacy Xero App Store partner and marketplace billing access in AU, NZ, and UK; "
            "Xero deprecated Xero App Store Subscriptions (XASS) in March 2026, accepted no "
            "new apps after 4 December 2025, and required existing customers to migrate by "
            "1 July 2026; the endpoints remain in the pinned and current API reference only "
            "for legacy transition needs; live entitlement and behavior remain unverified"
        )
        app_store_rows = [row for row in self.operations if row["spec_id"] == "app-store"]
        self.assertEqual(len(app_store_rows), 4)
        self.assertEqual({row["access_reason"] for row in app_store_rows}, {expected})
        self.assertTrue(all(row["scheduled_retirement"] is None for row in app_store_rows))
        coverage = openapi_inventory.render_coverage(self.catalog)
        self.assertEqual(coverage.count(expected), 4)

    def test_generated_catalog_and_coverage_are_repeatable(self) -> None:
        checkout = configured_checkout()
        if checkout is None:
            self.skipTest(
                f"set {CHECKOUT_ENV} to the official Xero-OpenAPI checkout for regeneration proof"
            )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog_path = root / "operations.json"
            coverage_path = root / "api_coverage.md"
            openapi_inventory.write_outputs(
                checkout,
                catalog_path=catalog_path,
                coverage_path=coverage_path,
            )
            generated = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertEqual(generated, self.catalog)
            coverage = coverage_path.read_text(encoding="utf-8")
            self.assertIn("477 callable OpenAPI operations", coverage)
            self.assertIn("474 explicit commands", coverage)
            self.assertEqual(coverage.count("| OpenAPI |"), 477)
            self.assertEqual(coverage.count("| Official docs |"), 2)


if __name__ == "__main__":
    unittest.main()
