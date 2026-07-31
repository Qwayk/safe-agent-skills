"""Generate deterministic SAV Domain APIs v1 operation metadata from a pinned Postman doc."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from pprint import pformat
from typing import Any
from urllib.parse import parse_qsl, urlparse

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_PATH = ROOT / "vendor" / "sav_domain_apis_v1.postman_collection.json"
OUTPUT_PATH = ROOT / "src" / "sav_domain_api" / "operations_generated.py"
DOCS_PATH = ROOT / "docs" / "api_coverage.md"

EXPECTED_COLLECTION_SHA256 = "d330b3df8f1b1962fcae295b0dc47b831c15f68d0d90db73c4dcb151968e33fe"
POSTMAN_SOURCE = "https://documenter.gw.postman.com/api/collections/9688716/TzzANHFJ?segregateAuth=true&versionTag=latest"
COMMAND_ORDER = [
    ("get_active_domains_in_account", "domains active", "read"),
    ("get_recent_auction_sales", "sales recent-auction", "read"),
    ("get_recent_premium_sales", "sales recent-premium", "read"),
    ("get_domain_pricing", "pricing list", "read"),
    ("remove_domain_for_sale", "domains remove-from-sale", "write"),
    ("submit_auth_code_for_pending_transfer_in", "domains submit-transfer-code", "write"),
    ("update_domain_auto_renewal", "domains set-auto-renewal", "write"),
    ("update_domain_for_sale_price", "domains set-sale-price", "write"),
    ("update_domain_nameservers", "domains set-nameservers", "write"),
    ("update_domain_privacy", "domains set-privacy", "write"),
    ("update_domain_whois_contacts", "domains set-whois-contacts", "write"),
    ("list_external_domain_for_sale", "domains list-external-sale", "write"),
]
EXPECTED_COUNT = len(COMMAND_ORDER)
TRANSFER_AUTH_CODE_OPERATION = "submit_auth_code_for_pending_transfer_in"
TRANSFER_AUTH_FLAG = "--auth-code-file"


def _cli_flag(operation_id: str, name: str) -> str:
    if operation_id == TRANSFER_AUTH_CODE_OPERATION and name == "auth_code":
        return TRANSFER_AUTH_FLAG
    return f"--{name.replace('_', '-')}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ensure_bytes_match() -> None:
    actual = _sha256(COLLECTION_PATH)
    if actual != EXPECTED_COLLECTION_SHA256:
        raise SystemExit(
            f"Boundary drift: source sha mismatch for {COLLECTION_PATH.name}: "
            f"{actual} != {EXPECTED_COLLECTION_SHA256}"
        )


def _load_collection() -> dict[str, Any]:
    payload = json.loads(COLLECTION_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("Collection root must be a JSON object.")
    return payload


def _iter_collection_items(items: Sequence[Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if isinstance(item.get("item"), list):
            entries.extend(_iter_collection_items(item["item"]))
            continue
        request = item.get("request")
        if not isinstance(request, dict):
            continue
        url = request.get("url")
        raw_url = None
        if isinstance(url, str):
            raw_url = url
        elif isinstance(url, dict):
            raw_url = url.get("raw")
        if not isinstance(raw_url, str):
            continue
        entries.append(
            {
                "name": str(item.get("name") or ""),
                "method": str(request.get("method") or "").upper(),
                "raw_url": raw_url,
            }
        )
    return entries


def _extract_operation_id(raw_url: str) -> str:
    return urlparse(raw_url).path.rsplit("/", 1)[-1]


def _query_params(raw_url: str) -> list[tuple[str, bool]]:
    parsed = urlparse(raw_url)
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    seen: set[str] = set()
    out: list[tuple[str, bool]] = []
    for key, _ in pairs:
        if key in seen:
            continue
        out.append((key, True))
        seen.add(key)
    return out


def _build_inventory() -> list[dict[str, Any]]:
    _ensure_bytes_match()
    collection = _load_collection()
    items = _iter_collection_items(collection.get("item", []))
    get_rows = [item for item in items if item["method"] == "GET"]
    get_rows_by_id = {
        _extract_operation_id(item["raw_url"]): {
            "method": item["method"],
            "raw_url": item["raw_url"],
            "query_params": _query_params(item["raw_url"]),
        }
        for item in get_rows
    }

    if len(get_rows_by_id) != EXPECTED_COUNT:
        raise SystemExit(
            f"Boundary drift: expected {EXPECTED_COUNT} official GET operations in this collection slice, "
            f"got {len(get_rows_by_id)}."
        )

    rows_by_id = {
        operation_id: row
        for operation_id, row in get_rows_by_id.items()
        if operation_id in {row[0] for row in COMMAND_ORDER}
    }

    if len(rows_by_id) != EXPECTED_COUNT:
        observed = sorted(rows_by_id)
        expected = [row[0] for row in COMMAND_ORDER]
        raise SystemExit(
            f"Boundary drift: expected command-boundary GET operations {expected}, got {len(rows_by_id)} "
            f"Observed: {observed}"
            f" expected: {expected}"
        )

    missing = [
        operation_id for operation_id, _, _ in COMMAND_ORDER if operation_id not in rows_by_id
    ]
    if missing:
        raise SystemExit(f"Boundary drift: missing expected operations: {missing}")

    unknown = sorted(set(rows_by_id) - {row[0] for row in COMMAND_ORDER})
    if unknown:
        raise SystemExit(f"Boundary drift: unexpected operations in scope: {unknown}")

    inventory: list[dict[str, Any]] = []
    for operation_id, command_path, kind in COMMAND_ORDER:
        row = rows_by_id[operation_id]
        params = [
            {
                "name": name,
                "cli_flag": _cli_flag(operation_id, name),
                "required": required,
                "source": "query_example",
            }
            for name, required in row["query_params"]
        ]
        inventory.append(
            {
                "command_path": command_path,
                "operation_id": operation_id,
                "http_method": row["method"],
                "endpoint": f"/domains_api_v1/{operation_id}",
                "kind": kind,
                "requires_approval": kind == "write",
                "required_params": params,
            }
        )
    return inventory


def _render_operations_py(operations: list[dict[str, Any]]) -> str:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "command_prefix": "sav",
        "collection_sha256": EXPECTED_COLLECTION_SHA256,
        "collection_url": POSTMAN_SOURCE,
        "operation_count": len(operations),
        "operations": operations,
    }
    return (
        "from __future__ import annotations\n\n"
        "from typing import Final\n\n"
        "# THIS FILE IS GENERATED. DO NOT EDIT BY HAND.\n\n"
        "OPERATIONS: Final = " + pformat(payload, sort_dicts=True, width=120) + "\n"
    )


def _format_param_list(params: list[dict[str, Any]]) -> str:
    if not params:
        return "No required params in example request."
    return ", ".join(param["cli_flag"] for param in params)


def _render_coverage_md(operations: list[dict[str, Any]]) -> str:
    lines = [
        "# SAV Domain APIs v1 — coverage",
        "",
        "## Summary",
        "",
        "- Provider: `api.sav.com`",
        "- API docs source: `https://documenter.getpostman.com/view/9688716/TzzANHFJ`",
        f"- Source collection URL: `{POSTMAN_SOURCE}`",
        f"- Collection SHA-256: `{EXPECTED_COLLECTION_SHA256}`",
        "- Base URL: `https://api.sav.com/domains_api_v1/` (fixed and enforced)",
        "- Total official documented operations in this slice: `12`",
        "- Read operations: `4`",
        "- Write operations: `8`",
        "",
        "## Operation ledger",
        "",
        "| Command | Operation ID | Method | Semantic | Required params |",
        "| --- | --- | --- | --- | --- |",
    ]
    for op in operations:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`sav {op['command_path']}`",
                    f"`{op['operation_id']}`",
                    op["http_method"],
                    op["kind"],
                    f"`{_format_param_list(op['required_params'])}`",
                ]
            )
            + " |"
        )
    lines.append("")
    lines.extend(
        [
            "## Scope",
            "",
            "- The four commands marked `read` are treated as read operations for runtime safety.",
            "- The eight commands marked `write` are still mapped from GET methods in the official docs, but are treated as writes in runtime safety policy.",
            "- No generic path-command bridge is shipped; only the fixed commands listed above are exposed.",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_outputs() -> tuple[str, str]:
    operations = _build_inventory()
    return _render_operations_py(operations), _render_coverage_md(operations)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate SAV v1 fixed command inventory.")
    parser.add_argument(
        "--check", action="store_true", help="Verify outputs are already up to date."
    )
    args = parser.parse_args(argv)

    operations_text, docs_text = generate_outputs()
    if args.check:
        if not OUTPUT_PATH.exists():
            raise SystemExit(f"Missing generated operations file: {OUTPUT_PATH}")
        if not DOCS_PATH.exists():
            raise SystemExit(f"Missing generated coverage file: {DOCS_PATH}")
        if OUTPUT_PATH.read_text(encoding="utf-8") != operations_text:
            raise SystemExit("Generated operations file is stale.")
        if DOCS_PATH.read_text(encoding="utf-8") != docs_text:
            raise SystemExit("Generated coverage doc is stale.")
        print("Generated inventory is current.")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(operations_text, encoding="utf-8")
    DOCS_PATH.write_text(docs_text, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)} and {DOCS_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
