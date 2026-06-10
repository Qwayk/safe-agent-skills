from __future__ import annotations

import re
import unittest
from pathlib import Path


def _read_official_commands_snapshot(path: Path) -> set[str]:
    cmds_list: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        cmds_list.append(line)

    duplicates = sorted({c for c in cmds_list if cmds_list.count(c) > 1})
    if duplicates:
        raise AssertionError(f"Duplicate commands found in {path.name}: {duplicates}")

    if cmds_list != sorted(cmds_list):
        raise AssertionError(f"{path.name} must be sorted alphabetically (one command per line)")

    return set(cmds_list)


def _extract_ledger_commands(md: str) -> list[str]:
    # Parse only the main ledger table rows: lines like:
    #   | `list_domain` | Implemented | ...
    rows: list[str] = []
    for line in md.splitlines():
        if not line.startswith("| `"):
            continue
        m = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
        if not m:
            continue
        rows.append(m.group(1).strip())
    return rows


class TestApiCoverageOfficialCommands(unittest.TestCase):
    def test_api_coverage_ledger_matches_official_docs(self) -> None:
        root = Path(__file__).resolve().parents[1]
        p = root / "docs" / "api_coverage.md"
        snapshot_path = root / "docs" / "official_commands.txt"
        md = p.read_text(encoding="utf-8")
        official = _read_official_commands_snapshot(snapshot_path)

        # Ensure the "audited vs official docs" field exists so reviewers know this list is intentional.
        self.assertRegex(md, r"Last audited vs official docs \(UTC\):\s*\d{4}-\d{2}-\d{2}")

        cmds = _extract_ledger_commands(md)
        self.assertTrue(cmds, "No command rows found in docs/api_coverage.md")

        duplicates = sorted({c for c in cmds if cmds.count(c) > 1})
        self.assertEqual(duplicates, [], f"Duplicate command rows found in docs/api_coverage.md: {duplicates}")

        ledger_set = set(cmds)
        missing = sorted(official - ledger_set)
        extra = sorted(ledger_set - official)
        self.assertEqual(missing, [], f"Coverage ledger missing official commands: {missing}")
        self.assertEqual(extra, [], f"Coverage ledger has commands not in official list: {extra}")

        self.assertEqual(
            len(cmds),
            len(official),
            "Coverage ledger row count does not match expected official command count",
        )
