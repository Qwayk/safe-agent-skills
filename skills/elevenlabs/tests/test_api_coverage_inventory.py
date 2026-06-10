from __future__ import annotations

from pathlib import Path
import unittest

from elevenlabs_api_tool.operations import INVENTORY


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
        row = dict(zip(headers, segments))
        rows[row["Endpoint"]] = row
    return rows


def _value_for(row: dict[str, str], header: str) -> str | None:
    target = header.strip().lower()
    for key, value in row.items():
        if key.strip().lower() == target:
            return value
    return None


class TestApiCoverageInventory(unittest.TestCase):
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
