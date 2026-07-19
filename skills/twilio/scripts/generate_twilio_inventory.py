#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from twilio_safe_agent_cli.openapi_inventory import write_outputs  # noqa: E402

DEFAULT_CATALOG = TOOL_ROOT / "src/twilio_safe_agent_cli/generated/operations.json"
DEFAULT_COVERAGE = TOOL_ROOT / "docs/api_coverage.md"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the pinned Twilio operation catalog and coverage page."
    )
    parser.add_argument(
        "--spec-root",
        required=True,
        type=Path,
        help="Path to the twilio-oai checkout or its spec/json directory.",
    )
    parser.add_argument(
        "--catalog-output",
        type=Path,
        default=DEFAULT_CATALOG,
        help=f"Catalog destination (default: {DEFAULT_CATALOG})",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=DEFAULT_COVERAGE,
        help=f"Coverage destination (default: {DEFAULT_COVERAGE})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    catalog = write_outputs(
        args.spec_root,
        catalog_path=args.catalog_output,
        coverage_path=args.coverage_output,
    )
    counts = catalog["counts"]
    print(
        "Generated "
        f"{counts['raw_operations']} operations: "
        f"{counts['command']} commands, "
        f"{counts['legacy_eol']} legacy EOL, and "
        f"{counts['canonical_duplicate']} canonical duplicates, with "
        f"{counts['developer_preview']} developer-preview and "
        f"{counts['private_or_unavailable']} private-or-unavailable non-commands."
    )
    print(f"Catalog: {args.catalog_output}")
    print(f"Coverage: {args.coverage_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
