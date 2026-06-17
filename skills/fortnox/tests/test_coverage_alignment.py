from __future__ import annotations

import re
import unittest
from pathlib import Path

from fortnox_api_tool.rest_inventory import load_rest_inventory
from fortnox_api_tool.websocket_inventory import load_websocket_inventory


_DOC_STATUS_TO_JSON = {
    "Planned, not shipped": "planned-not-shipped",
    "Partially shipped": "partially-shipped",
    "Shipped": "shipped",
}

_DOC_PROOF_TO_JSON = {
    "Not yet applicable": "not-yet-applicable",
    "Local unit-tested / live-unverified": "local-unit-tested-live-unverified",
}


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _coverage_text() -> str:
    return (_root() / "docs/api_coverage.md").read_text(encoding="utf-8")


def _parse_pipe_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def _extract_total(text: str, label: str) -> int:
    pattern = re.compile(rf"- {re.escape(label)}: `(\d+)`")
    match = pattern.search(text)
    if not match:
        raise AssertionError(f"Missing total line for {label!r} in docs/api_coverage.md")
    return int(match.group(1))


def _extract_last_audited(text: str) -> str:
    match = re.search(r"Last audited \(UTC\): (\d{4}-\d{2}-\d{2})", text)
    if not match:
        raise AssertionError("Missing 'Last audited (UTC)' line in docs/api_coverage.md")
    return match.group(1)


def _parse_rest_family_rows(text: str) -> dict[str, dict[str, str]]:
    section = text.split("## REST family summary", 1)[1].split("## REST per-operation ledger", 1)[0]
    rows: dict[str, dict[str, str]] = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        family_slug, _labels, _ops, planned_cli_prefix, ship_status, notes = _parse_pipe_row(line)[:6]
        rows[family_slug.strip("`")] = {
            "planned_cli_prefix": planned_cli_prefix.strip("`"),
            "ship_status": _DOC_STATUS_TO_JSON[ship_status],
            "notes": notes,
        }
    return rows


def _parse_rest_operation_rows(text: str) -> dict[str, dict[str, str]]:
    section = text.split("## Websocket control commands", 1)[0]
    heading_re = re.compile(r"^### `([^`]+)` \((\d+) operations\)$")
    rows: dict[str, dict[str, str]] = {}
    current_family: str | None = None
    for line in section.splitlines():
        match = heading_re.match(line)
        if match:
            current_family = match.group(1)
            continue
        if current_family and (line.startswith("| Shipped |") or line.startswith("| Planned, not shipped |")):
            status, group_name, http_method, path, operation_id, title, cli_command, proof_status, notes = _parse_pipe_row(line)[:9]
            rows[operation_id.strip("`")] = {
                "family_slug": current_family,
                "group_name": group_name.strip("`"),
                "http_method": http_method.strip("`"),
                "path": path.strip("`"),
                "title": title,
                "cli_command": cli_command.strip("`"),
                "ship_status": _DOC_STATUS_TO_JSON[status],
                "proof_status": _DOC_PROOF_TO_JSON[proof_status],
                "notes": notes,
            }
    return rows


def _parse_websocket_control_rows(text: str) -> dict[str, dict[str, str]]:
    section = text.split("## Websocket control commands", 1)[1].split("## Websocket topics and events", 1)[0]
    rows: dict[str, dict[str, str]] = {}
    for line in section.splitlines():
        if not line.startswith("| "):
            continue
        if line.startswith("| Status ") or line.startswith("|---"):
            continue
        status, official_command, cli_command, notes = _parse_pipe_row(line)[:4]
        rows[official_command.strip("`")] = {
            "cli_command": cli_command.strip("`"),
            "ship_status": _DOC_STATUS_TO_JSON[status],
            "notes": notes,
        }
    return rows


def _parse_websocket_topic_rows(text: str) -> dict[str, dict[str, str]]:
    section = text.split("## Websocket topics and events", 1)[1].split("## Honest gaps still open", 1)[0]
    rows: dict[str, dict[str, str]] = {}
    for line in section.splitlines():
        if not line.startswith("| "):
            continue
        if line.startswith("| Status ") or line.startswith("|---"):
            continue
        status, topic, event_count, cli_command, documented_event_names, notes = _parse_pipe_row(line)[:6]
        rows[topic.strip("`")] = {
            "event_count": event_count,
            "cli_command": cli_command.strip("`"),
            "documented_event_names": documented_event_names.replace("`", ""),
            "ship_status": _DOC_STATUS_TO_JSON[status],
            "notes": notes,
        }
    return rows


class TestCoverageAlignment(unittest.TestCase):
    def test_last_audited_matches_both_inventories(self) -> None:
        text = _coverage_text()
        expected = _extract_last_audited(text)
        self.assertEqual(load_rest_inventory().audited_utc, expected)
        self.assertEqual(load_websocket_inventory().audited_utc, expected)

    def test_rest_coverage_rows_match_inventory(self) -> None:
        text = _coverage_text()
        inventory = load_rest_inventory()

        family_rows = _parse_rest_family_rows(text)
        self.assertEqual(len(family_rows), len(inventory.family_summaries))
        families = {item.family_slug: item for item in inventory.family_summaries}
        self.assertEqual(set(families), set(family_rows))
        for family_slug, row in family_rows.items():
            item = families[family_slug]
            self.assertEqual(item.planned_cli_prefix, row["planned_cli_prefix"])
            self.assertEqual(item.ship_status, row["ship_status"])
            self.assertEqual(item.notes, row["notes"])

        operation_rows = _parse_rest_operation_rows(text)
        self.assertEqual(len(operation_rows), len(inventory.operations))
        operations = {item.operation_id: item for item in inventory.operations}
        self.assertEqual(set(operations), set(operation_rows))
        shipped_count = sum(1 for item in inventory.operations if item.ship_status == "shipped")
        self.assertEqual(shipped_count, _extract_total(text, "Shipped explicit REST commands today"))
        for operation_id, row in operation_rows.items():
            item = operations[operation_id]
            self.assertEqual(item.family_slug, row["family_slug"])
            self.assertEqual(item.group_name, row["group_name"])
            self.assertEqual(item.http_method, row["http_method"])
            self.assertEqual(item.path, row["path"])
            self.assertEqual(item.title, row["title"])
            self.assertEqual(item.cli_command, row["cli_command"])
            self.assertEqual(item.ship_status, row["ship_status"])
            self.assertEqual(item.proof_status, row["proof_status"])
            self.assertEqual(item.notes, row["notes"])

    def test_websocket_coverage_rows_match_inventory(self) -> None:
        text = _coverage_text()
        inventory = load_websocket_inventory()

        control_rows = _parse_websocket_control_rows(text)
        self.assertEqual(len(control_rows), len(inventory.control_commands))
        control_commands = {item.official_command: item for item in inventory.control_commands}
        self.assertEqual(set(control_commands), set(control_rows))
        for official_command, row in control_rows.items():
            item = control_commands[official_command]
            self.assertEqual(item.cli_command, row["cli_command"])
            self.assertEqual(item.ship_status, row["ship_status"])
            self.assertEqual(item.notes, row["notes"])

        topic_rows = _parse_websocket_topic_rows(text)
        self.assertEqual(len(topic_rows), len(inventory.topics))
        topics = {item.topic: item for item in inventory.topics}
        self.assertEqual(set(topics), set(topic_rows))
        shipped_websocket_entries = sum(1 for item in inventory.control_commands if item.ship_status == "shipped")
        shipped_websocket_entries += sum(1 for item in inventory.topics if item.ship_status == "shipped")
        self.assertEqual(
            shipped_websocket_entries,
            _extract_total(text, "Shipped explicit websocket commands today"),
        )
        for topic_name, row in topic_rows.items():
            item = topics[topic_name]
            documented_event_names = ", ".join(event.event for event in item.events)
            self.assertEqual(str(item.event_count), row["event_count"])
            self.assertEqual(item.cli_command, row["cli_command"])
            self.assertEqual(item.ship_status, row["ship_status"])
            self.assertEqual(documented_event_names, row["documented_event_names"])
            self.assertEqual(item.notes, row["notes"])
