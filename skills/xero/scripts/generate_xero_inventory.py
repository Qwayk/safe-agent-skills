#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from xero_safe_agent_cli.openapi_inventory import write_outputs  # noqa: E402

DEFAULT_CATALOG = TOOL_ROOT / "src/xero_safe_agent_cli/generated/operations.json"
DEFAULT_COVERAGE = TOOL_ROOT / "docs/api_coverage.md"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the pinned Xero operation catalog and coverage ledger."
    )
    parser.add_argument(
        "--spec-root",
        required=True,
        type=Path,
        help="Path to the pinned XeroAPI/Xero-OpenAPI Git checkout.",
    )
    parser.add_argument("--catalog-output", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--coverage-output", type=Path, default=DEFAULT_COVERAGE)
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
        f"Generated {counts['raw_openapi_operations']} pinned OpenAPI rows, "
        f"{counts['manual_operations']} official manual rows, "
        f"{counts['command']} explicit commands, and "
        f"{counts['superseded_compatibility']} superseded compatibility rows."
    )
    print(f"Catalog: {args.catalog_output}")
    print(f"Coverage: {args.coverage_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
