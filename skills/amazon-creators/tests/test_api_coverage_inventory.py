from __future__ import annotations

from pathlib import Path
import unittest


EXPECTED_OPERATIONS = {
    "GetBrowseNodes": "amazon-creators-api-tool browse-nodes describe",
    "GetItems": "amazon-creators-api-tool items get",
    "GetVariations": "amazon-creators-api-tool variations get",
    "SearchItems": "amazon-creators-api-tool search",
}

EXPECTED_RESOURCES = {
    "BrowseNodeInfo",
    "BrowseNodes",
    "Images",
    "ItemInfo",
    "OffersV2",
    "ParentAsin",
    "SearchRefinements",
    "VariationSummary",
}


def _parse_operation_rows(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            if in_table:
                break
            continue
        if not in_table:
            if stripped.startswith("| API operation |"):
                in_table = True
            continue
        if stripped.startswith("|---"):
            continue
        if not stripped.startswith("|"):
            break
        inner = stripped.strip("|")
        if "|" not in inner:
            continue
        operation_part, remainder = inner.split("|", 1)
        if "|" not in remainder:
            continue
        command_part, notes_part = remainder.rsplit("|", 1)
        operation = operation_part.strip().strip("`")
        rows[operation] = {
            "API operation": operation,
            "CLI command": command_part.strip(),
            "Key resource/locale flags": notes_part.strip(),
        }
    return rows


def _parse_resource_bullets(path: Path) -> set[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    resources: set[str] = set()
    in_resources = False
    for line in lines:
        stripped = line.strip()
        if stripped == "High-level resource vocabulary (all supported by the `--resource` flag):":
            in_resources = True
            continue
        if not in_resources:
            continue
        if not stripped:
            continue
        if not stripped.startswith("- "):
            break
        resources.add(stripped.removeprefix("- ").strip("`"))
    return resources


class TestApiCoverageInventory(unittest.TestCase):
    def test_issue_scope_inventory_is_fully_locked(self) -> None:
        path = Path("docs/api_coverage.md")
        rows = _parse_operation_rows(path)
        self.assertEqual(
            set(rows),
            set(EXPECTED_OPERATIONS),
            msg="Coverage ledger must stay locked to the four public catalog operations from Issue #404.",
        )
        for operation, command_prefix in EXPECTED_OPERATIONS.items():
            cli_command = rows[operation]["CLI command"]
            self.assertIn(
                command_prefix,
                cli_command,
                msg=f"Coverage row for {operation} must mention {command_prefix}.",
            )

    def test_issue_scope_resource_vocabulary_is_fully_locked(self) -> None:
        path = Path("docs/api_coverage.md")
        resources = _parse_resource_bullets(path)
        self.assertEqual(
            resources,
            EXPECTED_RESOURCES,
            msg="Coverage ledger must list the exact eight high-level resources from Issue #404.",
        )
