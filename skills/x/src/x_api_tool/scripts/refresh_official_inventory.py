from __future__ import annotations

import argparse
import hashlib
import time
from pathlib import Path

from ..openapi_inventory import extract_operations, load_openapi_snapshot, official_operations_lines


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _render_api_coverage_md(*, ops_lines: list[str]) -> str:
    # Columns: operationId, method, path, tags, security, primary_cli
    header = [
        "# API coverage",
        "",
        f"Last audited (UTC): {_utc_now().split('T', 1)[0]}",
        "",
        f"Last refreshed (UTC): `{_utc_now()}`",
        "",
        "This file is generated from the pinned OpenAPI snapshot.",
        "",
        "| operationId | method | path | tags | security | primary_cli |",
        "|---|---|---|---|---|---|",
    ]
    rows: list[str] = []
    for line in ops_lines:
        # Format: METHOD <path> <operationId> [tags=...] [security=...]
        parts = line.split(" ", 2)
        method = parts[0]
        rest = parts[2] if len(parts) > 2 else ""
        path = parts[1]

        operation_id = rest.split(" ", 1)[0].strip()
        tags = ""
        security = ""
        if "[tags=" in line:
            tags = line.split("[tags=", 1)[1].split("]", 1)[0]
        if "[security=" in line:
            security = line.split("[security=", 1)[1].split("]", 1)[0]

        primary_cli = f"x-api-tool api {operation_id}"
        rows.append(
            "| "
            + " | ".join(
                [
                    operation_id,
                    method,
                    path,
                    tags,
                    security,
                    f"`{primary_cli}`",
                ]
            )
            + " |"
        )

    return "\n".join(header + rows) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--snapshot",
        default="docs/official_openapi_x_api_v2.json",
        help="Path to pinned OpenAPI snapshot JSON",
    )
    p.add_argument(
        "--out-operations",
        default="docs/official_operations.txt",
        help="Path to write official operations inventory",
    )
    p.add_argument(
        "--out-coverage",
        default="docs/api_coverage.md",
        help="Path to write api coverage table markdown",
    )
    args = p.parse_args(argv)

    snap_path = Path(str(args.snapshot))
    obj = load_openapi_snapshot(snap_path)
    ops = extract_operations(obj)
    lines = official_operations_lines(ops)
    content = "\n".join(lines) + "\n"
    _write_text(Path(str(args.out_operations)), content)
    _write_text(Path(str(args.out_coverage)), _render_api_coverage_md(ops_lines=lines))

    # Print minimal integrity info (no secrets).
    print(
        "refreshed",
        {"snapshot": str(snap_path), "snapshot_sha256": _sha256(snap_path), "operations": len(lines)},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
