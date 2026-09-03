from __future__ import annotations

import json
import unittest
from pathlib import Path

from elevenlabs_api_tool.inventory_generator import _schema_fields
from elevenlabs_api_tool.operations import INVENTORY, InventoryEntry, _default_sample_args


def _parse_coverage_rows(path: Path) -> dict[str, dict[str, str]]:
    data = path.read_text(encoding="utf-8").splitlines()
    rows: dict[str, dict[str, str]] = {}
    headers: list[str] = []
    in_table = False
    for line in data:
        stripped = line.strip()
        if not stripped:
            if in_table:
                break
            continue
        if not in_table:
            if stripped.startswith("| Endpoint") and "CLI command" in stripped:
                headers = [seg.strip() for seg in stripped.strip("|").split("|")]
                in_table = True
            continue
        if stripped.startswith("|---"):
            continue
        if not stripped.startswith("|"):
            break
        segments = [seg.strip() for seg in stripped.strip("|").split("|")]
        if len(segments) != len(headers):
            continue
        row = dict(zip(headers, segments, strict=True))
        rows[row["Endpoint"]] = row
    return rows


def _value_for(row: dict[str, str], header: str) -> str | None:
    target = header.strip().lower()
    for key, value in row.items():
        if key.strip().lower() == target:
            return value
    return None


class TestApiCoverageInventory(unittest.TestCase):
    def test_schema_field_traversal_preserves_composed_array_hierarchy(self) -> None:
        schemas = {
            "Nested": {
                "properties": {
                    "mode": {"type": "string"},
                    "items": {"type": "array", "items": {"$ref": "#/components/schemas/Item"}},
                }
            },
            "Item": {"properties": {"value": {"type": "string"}}},
        }
        schema = {
            "allOf": [
                {"properties": {"config": {"anyOf": [{"$ref": "#/components/schemas/Nested"}]}}}
            ]
        }
        self.assertEqual(
            {
                "config",
                "config.mode",
                "config.items",
                "config.items.value",
            },
            _schema_fields(schema, schemas),
        )

    def test_pinned_schema_includes_current_twilio_amd_contract(self) -> None:
        spec = json.loads(Path("openapi.json").read_text(encoding="utf-8"))
        schemas = spec["components"]["schemas"]
        self.assertIn("TelephonyCallConfig-Input", schemas)
        self.assertIn("TelephonyCallConfig-Output", schemas)
        self.assertIn("TwilioMachineDetectionConfig", schemas)
        self.assertIn("TwilioMachineDetectionMode", schemas)
        self.assertIn("twilio_machine_detection", json.dumps(spec))
        self.assertIn("answering_machine_detection", schemas["WebhookEventType"]["enum"])

    def test_generic_contract_exposes_twilio_amd_request_fields(self) -> None:
        entry = next(e for e in INVENTORY if e.name == "handle_twilio_outbound_call")
        self.assertIn("telephony_call_config", entry.request_body_fields)
        self.assertIn("telephony_call_config.ringing_timeout_secs", entry.request_body_fields)
        self.assertIn("telephony_call_config.twilio_machine_detection", entry.request_body_fields)
        self.assertIn("telephony_call_config.twilio_machine_detection.mode", entry.request_body_fields)
        self.assertNotIn("mode", entry.request_body_fields)
        self.assertNotIn("ringing_timeout_secs", entry.request_body_fields)
        self.assertNotIn("answering_machine_detection", entry.webhook_events)

    def test_webhook_events_are_scoped_to_webhook_settings_requests(self) -> None:
        populated = [e for e in INVENTORY if e.webhook_events]
        self.assertEqual(
            {
                "create_agent_route",
                "run_agent_test_suite_route",
                "resubmit_tests_route",
                "update_settings_route",
            },
            {e.name for e in populated},
        )
        for entry in populated:
            self.assertIn("answering_machine_detection", entry.webhook_events)

    def test_openapi_inventory_counts_and_command_uniqueness(self) -> None:
        http = [e for e in INVENTORY if e.method in {"GET", "POST", "PUT", "PATCH", "DELETE"}]
        self.assertEqual(388, len(http))
        self.assertEqual(367, sum(e.status == "Implemented" for e in http))
        self.assertEqual(21, sum(e.status == "Deprecated" for e in http))
        commands = [e.cli_command for e in INVENTORY if e.cli_command]
        self.assertEqual(len(commands), len(set(commands)))
        self.assertFalse([e for e in INVENTORY if e.status == "Deprecated" and e.cli_command])

    def test_current_multi_context_websocket_rows_are_explicit_and_safe(self) -> None:
        rows = {e.name: e for e in INVENTORY if e.method == "WEBSOCKET"}
        self.assertEqual(7, len(rows))
        expected = {
            "tts_multi_stream_input_wss": (
                "wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/multi-stream-input",
                "tts multi-stream-input websocket",
            ),
            "dialogue_multi_stream_input_wss": (
                "wss://api.elevenlabs.io/v1/text-to-dialogue/multi-stream-input",
                "dialogue multi-stream-input websocket",
            ),
        }
        for name, (path, command) in expected.items():
            self.assertIn(name, rows)
            self.assertEqual(path, rows[name].path)
            self.assertEqual(command, rows[name].cli_command)
            self.assertEqual(("write", "spend_money", "binary_output"), tuple(rows[name].safety))

    def test_inventory_matches_coverage_table(self) -> None:
        path = Path("docs/api_coverage.md")
        rows = _parse_coverage_rows(path)
        for entry in INVENTORY:
            key = f"{entry.method.upper()} {entry.path}"
            self.assertIn(
                key,
                rows,
                msg=f"Coverage table must include row for {key} ({entry.name})",
            )
            row = rows[key]
            status_value = _value_for(row, "Status")
            self.assertEqual(
                entry.status,
                status_value,
                msg=f"Status column for {key} must match inventory status",
            )
            notes_value = _value_for(row, "Notes")
            self.assertIn(
                entry.doc_url,
                notes_value or "",
                msg=f"Notes column for {key} must reference {entry.doc_url}",
            )
            if entry.cli_command and entry.status.lower().startswith("impl"):
                cli_value = _value_for(row, "CLI command(s)")
                self.assertIn(
                    entry.cli_command,
                    cli_value or "",
                    msg=f"CLI column for {key} must mention {entry.cli_command}",
                )

    def test_inventory_has_no_planned_entries_and_docs_only_method(self) -> None:
        planned = [
            entry.name
            for entry in INVENTORY
            if entry.status.lower() == "planned"
        ]
        self.assertFalse(
            planned,
            msg=(
                "The inventory must not declare any Planned rows; "
                f"found: {planned}"
            ),
        )
        for entry in INVENTORY:
            if entry.method.upper() == "DOC":
                self.assertEqual(
                    entry.status,
                    "Docs-only",
                    msg=(
                        "Documentation entries must stay marked as Docs-only; "
                        f"{entry.name} currently says {entry.status}"
                    ),
                )

    def test_default_sample_args_for_sensitive_output_get_operations_include_out(self) -> None:
        entry = InventoryEntry(
            name="sensitive_read",
            section="Test",
            description="Sensitive read path",
            method="GET",
            path="/v1/sensitive",
            status="Implemented",
            doc_url="https://example.test",
            safety=("read", "sensitive_output"),
            cli_command="sensitive read",
        )

        sample_args = _default_sample_args(entry)

        self.assertIn(
            "--out",
            sample_args,
            msg=(
                "GET/read operations marked sensitive_output must include --out "
                "for file-only sample output."
            ),
        )
