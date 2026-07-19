from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src"))

try:
    from twilio_safe_agent_cli import openapi_inventory
except ImportError:
    openapi_inventory = None  # type: ignore[assignment]


PINNED_COMMIT = "1a9189c79a73781ddf45afcd0afd1f210742d68c"
_CHECKOUT_VALUE = os.environ.get("TWILIO_OAI_SPEC_ROOT")
CHECKOUT_ROOT = Path(_CHECKOUT_VALUE) if _CHECKOUT_VALUE else None
HAS_SOURCE_CHECKOUT = CHECKOUT_ROOT is not None and CHECKOUT_ROOT.exists()
CHECKED_IN_CATALOG = TOOL_ROOT / "src/twilio_safe_agent_cli/generated/operations.json"


@unittest.skipIf(openapi_inventory is None, "inventory module is not implemented yet")
class TestTwilioInventory(unittest.TestCase):
    catalog: dict[str, object]
    operations: list[dict[str, object]]

    @classmethod
    def setUpClass(cls) -> None:
        if HAS_SOURCE_CHECKOUT:
            cls.catalog = openapi_inventory.build_inventory(CHECKOUT_ROOT)
        else:
            cls.catalog = json.loads(CHECKED_IN_CATALOG.read_text(encoding="utf-8"))
        cls.operations = cls.catalog["operations"]  # type: ignore[assignment]

    def test_pinned_boundary_counts_every_operation(self) -> None:
        source = self.catalog["source"]
        counts = self.catalog["counts"]
        self.assertEqual(source["commit"], PINNED_COMMIT)
        self.assertEqual(source["spec_count"], 61)
        self.assertEqual(source["path_count"], 982)
        self.assertEqual(source["operation_count"], 1_550)
        self.assertEqual(
            source["methods"],
            {"DELETE": 231, "GET": 782, "PATCH": 12, "POST": 507, "PUT": 18},
        )
        self.assertEqual(len(self.operations), 1_550)
        self.assertEqual(
            counts,
            {
                "canonical_duplicate": 9,
                "command": 1_325,
                "developer_preview": 5,
                "legacy_eol": 205,
                "private_or_unavailable": 6,
                "raw_operations": 1_550,
            },
        )
        self.assertTrue(all(row["operation_id"] for row in self.operations))

    def test_command_names_are_fixed_unique_and_deterministic(self) -> None:
        if HAS_SOURCE_CHECKOUT:
            rebuilt = openapi_inventory.build_inventory(CHECKOUT_ROOT)
            self.assertEqual(self.catalog, rebuilt)

        command_rows = [row for row in self.operations if row["disposition"] == "command"]
        commands = [row["command"] for row in command_rows]
        self.assertEqual(len(commands), 1_325)
        self.assertEqual(len(commands), len(set(commands)))
        self.assertTrue(
            all(re.fullmatch(r"[a-z0-9-]+\.[a-z0-9-]+", command) for command in commands)
        )
        for row in command_rows:
            expected = (
                f"{row['spec_id']}."
                f"{openapi_inventory.operation_id_to_kebab(row['operation_id'])}"
            )
            self.assertEqual(row["command"], expected)

    def test_nine_older_or_deprecated_contracts_are_canonical_duplicates(self) -> None:
        expected = {
            "preview.CreateMarketplaceInstalledAddOn": "marketplace-v1.create-installed-add-on",
            "preview.UpdateMarketplaceInstalledAddOn": "marketplace-v1.update-installed-add-on",
            "pricing-v1.ListVoiceCountry": "pricing-v2.list-voice-country",
            "studio-v1.DeleteExecution": "studio-v2.delete-execution",
            "studio-v1.DeleteFlow": "studio-v2.delete-flow",
            "studio-v1.FetchExecutionContext": "studio-v2.fetch-execution-context",
            "studio-v1.FetchExecutionStep": "studio-v2.fetch-execution-step",
            "studio-v1.FetchExecutionStepContext": "studio-v2.fetch-execution-step-context",
            "studio-v1.ListExecutionStep": "studio-v2.list-execution-step",
        }
        actual = {
            f"{row['spec_id']}.{row['operation_id']}": row["duplicate_of"]
            for row in self.operations
            if row["disposition"] == "canonical_duplicate"
        }
        self.assertEqual(actual, expected)
        for row in self.operations:
            if row["disposition"] == "canonical_duplicate":
                self.assertIsNone(row["command"])
                self.assertIn(
                    row["duplicate_of"],
                    {
                        candidate["command"]
                        for candidate in self.operations
                        if candidate["disposition"] == "command"
                    },
                )

    def test_past_eol_families_and_removed_studio_engagement_are_legacy(self) -> None:
        legacy = [row for row in self.operations if row["disposition"] == "legacy_eol"]
        self.assertEqual(
            Counter(row["family"] for row in legacy),
            {"chat": 95, "ip_messaging": 94, "notify": 15, "studio": 1},
        )
        self.assertTrue(all(row["command"] is None for row in legacy))
        self.assertTrue(all(row["duplicate_of"] is None for row in legacy))
        self.assertTrue(all(row["classification"]["legacy_eol"] for row in legacy))

    def test_all_81_schema_gaps_have_audited_manual_dispositions(self) -> None:
        audited = [row for row in self.operations if row.get("manual_contract")]
        self.assertEqual(len(audited), 81)
        self.assertTrue(all(row["manual_contract"]["sources"] for row in audited))
        self.assertTrue(
            all(
                all(
                    source.startswith("https://www.twilio.com/")
                    or source.startswith("https://github.com/twilio/")
                    for source in row["manual_contract"]["sources"]
                )
                for row in audited
            )
        )

        expected_non_commands = {
            "accounts-v1.UpdateMessagingGeopermissions": "private_or_unavailable",
            "assistants-v1.CreateKnowledge": "developer_preview",
            "assistants-v1.UpdateKnowledge": "developer_preview",
            "assistants-v1.CreateTool": "developer_preview",
            "assistants-v1.UpdateTool": "developer_preview",
            "flex-v1.UpdateConfiguration": "private_or_unavailable",
            "flex-v1.CreateInteractionChannelParticipant": "private_or_unavailable",
            "flex-v1.CreateInteractionTransfer": "private_or_unavailable",
            "flex-v1.UpdateInteractionTransfer": "private_or_unavailable",
            "numbers-v1.CreateSigningRequestConfiguration": "private_or_unavailable",
            "numbers-v2.CreateBulkHostedNumberOrder": "developer_preview",
            "studio-v1.CreateEngagement": "legacy_eol",
        }
        actual_non_commands = {
            f"{row['spec_id']}.{row['operation_id']}": row["disposition"]
            for row in audited
            if row["disposition"] not in {"command", "canonical_duplicate"}
        }
        self.assertEqual(actual_non_commands, expected_non_commands)

        preview_duplicates = {
            row["operation_id"]: row["duplicate_of"]
            for row in audited
            if row["spec_id"] == "preview"
        }
        self.assertEqual(
            preview_duplicates,
            {
                "CreateMarketplaceInstalledAddOn": "marketplace-v1.create-installed-add-on",
                "UpdateMarketplaceInstalledAddOn": "marketplace-v1.update-installed-add-on",
            },
        )

    def test_manual_commands_are_fixed_and_priority_gaps_are_callable(self) -> None:
        required_commands = {
            "verify-v2.create-verification",
            "studio-v2.create-flow",
            "studio-v2.create-execution",
            "video-v1.create-room",
            "sync-v1.create-document",
            "sync-v1.update-document",
            "proxy-v1.create-session",
            "events-v1.create-sink",
            "events-v1.create-subscription",
            "iam-organizations.patch-organization-user",
            "numbers-v1.create-porting-webhook-configuration",
            "numbers-v1.create-sender-id-registration",
            "numbers-v2.create-end-user",
            "trusthub-v1.create-end-user",
        }
        command_rows = {
            row["command"]: row for row in self.operations if row["disposition"] == "command"
        }
        self.assertTrue(required_commands.issubset(command_rows), required_commands - command_rows.keys())

        proxy_schema = command_rows["proxy-v1.create-session"]["request"]["schemas"][
            "application/x-www-form-urlencoded"
        ]["resolved_schema"]
        self.assertNotIn("Participants", proxy_schema["properties"])

        sink_schema = command_rows["events-v1.create-sink"]["request"]["schemas"][
            "application/x-www-form-urlencoded"
        ]["resolved_schema"]
        self.assertEqual(sink_schema["properties"]["SinkType"]["enum"], ["kinesis", "webhook", "segment"])

        for row in self.operations:
            if row["disposition"] != "command" or row["method"] == "GET":
                continue
            request = row.get("request")
            if not request:
                continue
            for media_type in request["media_types"]:
                self.assertFalse(
                    openapi_inventory.has_unbounded_request_schema(
                        request["schemas"][media_type]["resolved_schema"]
                    ),
                    f"{row['command']} has an unbounded request schema",
                )
            schemas = [
                request["schemas"][media_type]["resolved_schema"]
                for media_type in request["media_types"]
            ]
            self.assertFalse(all(openapi_inventory.is_empty_object_schema(schema) for schema in schemas))

    def test_priority_manual_commands_have_the_required_risks(self) -> None:
        rows = {row["command"]: row for row in self.operations if row["command"]}
        expected = {
            "verify-v2.create-verification": {"outbound_contact", "spend", "sensitive_data", "write"},
            "studio-v2.create-execution": {
                "outbound_contact",
                "production_change",
                "sensitive_data",
                "spend",
                "write",
            },
            "video-v1.create-room": {"production_change", "sensitive_data", "spend", "write"},
            "sync-v1.create-document": {"sensitive_data", "write"},
            "proxy-v1.create-session": {"production_change", "write"},
            "events-v1.create-sink": {"production_change", "sensitive_data", "write"},
            "numbers-v1.create-sender-id-registration": {
                "identity_or_compliance",
                "sensitive_data",
                "write",
            },
        }
        for command, required in expected.items():
            self.assertTrue(required.issubset(rows[command]["risk_flags"]), command)

        statistics = rows["taskrouter-v1.create-task-queue-bulk-real-time-statistics"]
        self.assertIn("read", statistics["risk_flags"])
        self.assertNotIn("write", statistics["risk_flags"])

    @unittest.skipUnless(HAS_SOURCE_CHECKOUT, "set TWILIO_OAI_SPEC_ROOT for pinned-source hash proof")
    def test_pin_and_every_source_file_hash_match_the_supplied_specs(self) -> None:
        source = self.catalog["source"]
        files = source["spec_files"]
        self.assertEqual(len(files), 61)
        self.assertIsNotNone(CHECKOUT_ROOT)
        spec_dir = openapi_inventory.resolve_spec_dir(CHECKOUT_ROOT)
        for entry in files:
            spec_path = spec_dir / entry["filename"]
            digest = hashlib.sha256(spec_path.read_bytes()).hexdigest()
            self.assertEqual(entry["sha256"], digest)

        hashes_by_filename = {entry["filename"]: entry["sha256"] for entry in files}
        for row in self.operations:
            self.assertEqual(row["source_sha256"], hashes_by_filename[row["source_filename"]])
            self.assertTrue(row["source_pointer"].startswith("#/paths/"))

    def test_resolved_auth_totals_match_the_pin(self) -> None:
        schemes = Counter()
        for row in self.operations:
            requirements = row["security"]["requirements"]
            if not requirements:
                schemes["none"] += 1
                continue
            self.assertEqual(len(requirements), 1)
            names = list(requirements[0])
            self.assertEqual(len(names), 1)
            schemes[names[0]] += 1
            self.assertIn(names[0], row["security"]["schemes"])
        self.assertEqual(
            schemes,
            {
                "accountSid_authToken": 1_490,
                "basic_apikey_or_accountsid": 41,
                "oAuth2ClientCredentials": 11,
                "none": 8,
            },
        )

    def test_operation_contract_metadata_is_preserved(self) -> None:
        configuration = self._row("conversations-v2", "FetchConfiguration")
        self.assertEqual(
            [(item["name"], item["in"]) for item in configuration["parameters"]],
            [("Sid", "path")],
        )

        message = self._row("api-v2010", "CreateMessage")
        self.assertEqual(message["server"], "https://api.twilio.com")
        self.assertEqual(message["method"], "POST")
        self.assertEqual(
            message["path"], "/2010-04-01/Accounts/{AccountSid}/Messages.json"
        )
        self.assertEqual(
            message["request"]["media_types"], ["application/x-www-form-urlencoded"]
        )
        self.assertEqual(message["success_responses"][0]["status"], "201")
        self.assertIn("pathType", message["path_x_twilio"])

        referenced_body = self._row("assistants-v1", "CreateAssistant")
        resolved_schema = referenced_body["request"]["schemas"]["application/json"][
            "resolved_schema"
        ]
        self.assertIn("properties", resolved_schema)
        self.assertIn("name", resolved_schema["properties"])

    def test_reachable_twilio_pii_metadata_is_preserved(self) -> None:
        message = self._row("api-v2010", "CreateMessage")
        response_fields = {
            field["field"]: field["pii"]
            for field in message["pii_fields"]
            if field["location"].startswith("response:201:application/json")
        }
        self.assertEqual(
            response_fields["body"], {"deleteSla": 30, "handling": "standard"}
        )
        self.assertEqual(
            response_fields["from"], {"deleteSla": 120, "handling": "standard"}
        )
        self.assertEqual(
            response_fields["to"], {"deleteSla": 120, "handling": "standard"}
        )

        binding = self._row("chat-v2", "ListBinding")
        identity = [field for field in binding["pii_fields"] if field["field"] == "Identity"]
        self.assertEqual(identity[0]["pii"], {"deleteSla": 30, "handling": "standard"})

    def test_preview_and_access_flags_preserve_audited_dispositions(self) -> None:
        preview_rows = [row for row in self.operations if row["spec_id"] == "preview"]
        self.assertTrue(preview_rows)
        self.assertTrue(all(row["classification"]["preview"] for row in preview_rows))
        self.assertTrue(
            all(row["disposition"] in {"command", "canonical_duplicate"} for row in preview_rows)
        )

        gated_rows = [row for row in self.operations if row["spec_id"] == "iam-organizations"]
        self.assertEqual(len(gated_rows), 13)
        self.assertTrue(all(row["classification"]["access_gated"] for row in gated_rows))
        self.assertTrue(
            all(row["disposition"] in {"command", "private_or_unavailable"} for row in gated_rows)
        )
        self.assertTrue(
            all(
                row["classification"]["live_verification"] == "unverified"
                for row in self.operations
            )
        )

        frontline_rows = [row for row in self.operations if row["family"] == "frontline"]
        self.assertEqual(len(frontline_rows), 2)
        self.assertTrue(all(row["disposition"] == "command" for row in frontline_rows))
        self.assertTrue(all(row["classification"]["access_gated"] for row in frontline_rows))
        self.assertTrue(
            all(
                row["classification"]["scheduled_eol"] == "2026-09-30"
                for row in frontline_rows
            )
        )

    def test_risk_snapshot_and_verification_strategies_are_explicit(self) -> None:
        for row in self.operations:
            self.assertTrue(row["risk_flags"])
            self.assertIn(row["snapshot_strategy"], openapi_inventory.SNAPSHOT_STRATEGIES)
            self.assertIn(row["verification_strategy"], openapi_inventory.VERIFICATION_STRATEGIES)
        create_message = self._row("api-v2010", "CreateMessage")
        self.assertIn("outbound_contact", create_message["risk_flags"])
        self.assertIn("spend", create_message["risk_flags"])
        self.assertEqual(create_message["snapshot_strategy"], "no_snapshot_create")

    def test_twilio_real_world_actions_have_conservative_static_risks(self) -> None:
        by_operation_name = {
            f"{row['spec_id']}.{openapi_inventory.operation_id_to_kebab(row['operation_id'])}": row
            for row in self.operations
        }
        expectations = {
            "conversations-v1.create-conversation-message": {"outbound_contact", "spend"},
            "studio-v2.create-execution": {"outbound_contact", "spend", "production_change"},
            "api-v2010.create-incoming-phone-number": {"spend"},
            "wireless-v1.update-sim": {"spend"},
            "supersim-v1.create-sms-command": {"outbound_contact", "spend"},
            "api-v2010.create-validation-request": {"outbound_contact", "spend"},
            "api-v2010.create-application": {"production_change"},
            "api-v2010.create-sip-credential": {
                "auth_or_permission",
                "production_change",
            },
            "api-v2010.update-call": {"outbound_contact", "spend", "production_change"},
            "api-v2010.update-conference": {
                "outbound_contact",
                "spend",
                "production_change",
            },
            "api-v2010.create-stream": {"outbound_contact", "spend", "production_change"},
            "messaging-v1.create-tollfree-verification": {
                "identity_or_compliance",
                "spend",
            },
            "messaging-v1.create-us-app-to-person": {
                "identity_or_compliance",
                "production_change",
                "spend",
            },
            "trusthub-v1.create-customer-profile": {"identity_or_compliance"},
            "accounts-v1.create-secondary-auth-token": {"auth_or_permission"},
        }
        for command, required in expectations.items():
            risk_flags = set(by_operation_name[command]["risk_flags"])
            self.assertTrue(
                required.issubset(risk_flags),
                f"{command} is missing {required - risk_flags}",
            )

    def test_all_callable_rows_are_audited_across_every_goal_risk_family(self) -> None:
        command_rows = [row for row in self.operations if row["disposition"] == "command"]
        counts = Counter(flag for row in command_rows for flag in row["risk_flags"])
        risk_families = (
            "outbound_contact",
            "spend",
            "bulk",
            "destructive",
            "auth_or_permission",
            "identity_or_compliance",
            "production_change",
        )
        self.assertEqual(
            {name: counts[name] for name in risk_families},
            {
                "outbound_contact": 36,
                "spend": 138,
                "bulk": 6,
                "destructive": 188,
                "auth_or_permission": 137,
                "identity_or_compliance": 128,
                "production_change": 275,
            },
        )
        allowed = set(risk_families) | {"preview", "read", "sensitive_data", "write"}
        self.assertTrue(all(set(row["risk_flags"]).issubset(allowed) for row in command_rows))
        read_through_post = {
            "numbers-v1.create-eligibility",
            "numbers-v1.create-bulk-eligibility",
            "taskrouter-v1.create-task-queue-bulk-real-time-statistics",
        }
        for row in command_rows:
            if row["method"] == "GET" or row["command"] in read_through_post:
                self.assertIn("read", row["risk_flags"], row["command"])
                if row["command"] in read_through_post:
                    self.assertNotIn("write", row["risk_flags"], row["command"])
            else:
                self.assertIn("write", row["risk_flags"], row["command"])

    def test_preview_wireless_writes_keep_the_same_spend_gate_as_wireless_v1(self) -> None:
        by_operation_name = {
            f"{row['spec_id']}.{openapi_inventory.operation_id_to_kebab(row['operation_id'])}": row
            for row in self.operations
        }
        preview_wireless_writes = {
            "preview.create-wireless-command",
            "preview.create-wireless-rate-plan",
            "preview.update-wireless-rate-plan",
            "preview.delete-wireless-rate-plan",
            "preview.update-wireless-sim",
        }
        for operation_name in preview_wireless_writes:
            row = by_operation_name[operation_name]
            self.assertNotEqual(row["method"], "GET")
            self.assertIn("spend", row["risk_flags"], operation_name)

    def test_checked_in_catalog_and_docs_exactly_match_generation(self) -> None:
        catalog_path = TOOL_ROOT / "src/twilio_safe_agent_cli/generated/operations.json"
        coverage_path = TOOL_ROOT / "docs/api_coverage.md"
        checked_in = json.loads(catalog_path.read_text(encoding="utf-8"))
        self.assertEqual(checked_in, self.catalog)
        self.assertEqual(
            coverage_path.read_text(encoding="utf-8"),
            openapi_inventory.render_coverage(self.catalog),
        )

    @unittest.skipUnless(HAS_SOURCE_CHECKOUT, "set TWILIO_OAI_SPEC_ROOT for writer regeneration")
    def test_writer_uses_exact_default_serialization_for_both_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            catalog_path = Path(tmp) / "operations.json"
            coverage_path = Path(tmp) / "api_coverage.md"
            written = openapi_inventory.write_outputs(
                CHECKOUT_ROOT,
                catalog_path=catalog_path,
                coverage_path=coverage_path,
            )
            self.assertEqual(written, self.catalog)
            self.assertEqual(
                catalog_path.read_text(encoding="utf-8"),
                openapi_inventory.serialize_catalog(self.catalog),
            )
            self.assertEqual(
                coverage_path.read_text(encoding="utf-8"),
                openapi_inventory.render_coverage(self.catalog),
            )

    def _row(self, spec_id: str, operation_id: str) -> dict[str, object]:
        matches = [
            row
            for row in self.operations
            if row["spec_id"] == spec_id and row["operation_id"] == operation_id
        ]
        self.assertEqual(len(matches), 1)
        return matches[0]


class TestTwilioInventoryModuleExists(unittest.TestCase):
    def test_inventory_module_exists(self) -> None:
        self.assertIsNotNone(openapi_inventory, "twilio_safe_agent_cli.openapi_inventory is missing")


if __name__ == "__main__":
    unittest.main()
