from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from .generated_registry import slugify

SPEC_REPO_URL = "https://github.com/Azure/azure-rest-api-specs"
PINNED_COMMIT = "ada8601c3b75c15f06f21e50f9368d9476229305"
HTTP_METHODS = {"get", "put", "post", "patch", "delete", "head", "options"}
READ_METHODS = {"get", "head", "options"}
READ_OPERATION_PREFIXES = ("check", "get", "list", "query", "read", "validate")
IRREVERSIBLE_METHODS = {"delete"}
IRREVERSIBLE_TOKENS = ("delete", "purge", "remove", "terminate")
SECURITY_TOKENS = (
    "access",
    "authorization",
    "credential",
    "identity",
    "key",
    "lock",
    "permission",
    "policy",
    "role",
    "secret",
    "vault",
)
SPEND_TOKENS = (
    "billing",
    "budget",
    "capacity",
    "cost",
    "quota",
    "reservation",
    "sku",
)
PUBLIC_TOKENS = (
    "dns",
    "firewall",
    "ip",
    "listener",
    "nat",
    "network",
    "public",
    "route",
    "traffic",
)
SENSITIVE_READ_TOKENS = (
    "access token",
    "accesstoken",
    "api key",
    "apikey",
    "connection string",
    "connectionstring",
    "credential",
    "key",
    "listkeys",
    "listsecrets",
    "password",
    "publishingcredentials",
    "sas",
    "secret",
    "token",
)
EXCLUDED_SERVICE_SLUGS = {
    "awsconnector",
    "contosowidgetmanager",
    "devops",
    "github",
    "m365securityandcompliance",
    "powerplatform",
    "widget",
}
EXCLUDED_SERVICE_TOKENS = (
    "awsconnector",
    "contosowidgetmanager",
    "devops",
    "dynamics",
    "github",
    "graph",
    "m365",
    "microsoft365",
    "microsoft-365",
    "office365",
    "office-365",
    "powerplatform",
    "widgetanalytics",
    "widgetmanager",
    "xbox",
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _repo_commit(spec_root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(spec_root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return PINNED_COMMIT


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _candidate_files(spec_root: Path) -> list[Path]:
    out: list[Path] = []
    for path in spec_root.glob("specification/**/*.json"):
        text = path.as_posix()
        if "/examples/" in text or "/common-types/" in text:
            continue
        if "/resource-manager/" not in text and "/data-plane/" not in text:
            continue
        if "/stable/" not in text and "/preview/" not in text and "-preview" not in text:
            continue
        out.append(path)
    return sorted(out, key=lambda p: p.as_posix())


def _plane(path: Path) -> str:
    text = path.as_posix()
    return "management" if "/resource-manager/" in text else "data_plane"


def _lifecycle(path: Path) -> str:
    text = path.as_posix().lower()
    return "preview" if "/preview/" in text or "-preview" in text else "stable"


def _version(path: Path) -> str:
    parts = path.parts
    for index, part in enumerate(parts):
        if part in {"stable", "preview"} and index + 1 < len(parts):
            return parts[index + 1]
    return ""


def _service_from_path(path: Path) -> tuple[str, str | None]:
    parts = path.parts
    service = parts[1] if len(parts) > 2 and parts[0] == "specification" else path.parent.name
    provider = None
    for part in parts:
        if part.startswith("Microsoft."):
            provider = part
            break
    return service, provider


def _is_excluded_product(service: str, provider: str | None, rel_path: str) -> bool:
    service_slug = slugify(service)
    provider_slug = slugify(provider or "")
    text = " ".join([service_slug, provider_slug, rel_path.lower()])
    if service_slug in EXCLUDED_SERVICE_SLUGS:
        return True
    if any(token in text for token in EXCLUDED_SERVICE_TOKENS):
        return True
    return False


def _operation_name(operation_id: str, method: str, path: str) -> str:
    raw = operation_id.strip() or f"{method}_{path.strip('/').replace('/', '_')}"
    return slugify(raw).replace("-", "_")


def _classification(method: str, operation_id: str) -> str:
    lowered = operation_id.lower()
    if method in READ_METHODS:
        return "read"
    if method == "post" and lowered.startswith(READ_OPERATION_PREFIXES):
        return "read"
    return "write"


def _is_sensitive_read(*, method: str, operation_id: str, path: str, service: str, provider: str | None, summary: str) -> bool:
    text = " ".join([method, operation_id, path, service, provider or "", summary]).lower()
    return any(token in text for token in SENSITIVE_READ_TOKENS)


def _risk_categories(*, method: str, operation_id: str, path: str, service: str, provider: str | None, classification: str) -> list[str]:
    text = " ".join([method, operation_id, path, service, provider or ""]).lower()
    risks: set[str] = set()
    if classification == "write":
        risks.update({"write", "no_snapshot"})
        if method in IRREVERSIBLE_METHODS or any(token in text for token in IRREVERSIBLE_TOKENS):
            risks.add("irreversible")
        if any(token in text for token in SECURITY_TOKENS):
            risks.add("identity_security")
        if any(token in text for token in SPEND_TOKENS):
            risks.add("spend_quota")
        if any(token in text for token in PUBLIC_TOKENS):
            risks.add("public_exposure")
    elif classification == "sensitive_read":
        risks.add("sensitive_read")
    return sorted(risks)


def _version_sort_key(value: str) -> tuple[int, ...]:
    nums = [int(item) for item in re.findall(r"\d+", value)]
    return tuple(nums)


def _select_latest_operations(operations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for operation in operations:
        key = (
            str(operation.get("operation_id") or operation.get("operation_name") or ""),
            str(operation.get("http_method") or ""),
            str(operation.get("path") or ""),
        )
        grouped[key].append(operation)

    selected: list[dict[str, Any]] = []
    candidate_count = 0
    for candidates in grouped.values():
        candidate_count += len(candidates)
        stable = [item for item in candidates if item.get("lifecycle") == "stable"]
        pool = stable or candidates
        chosen = sorted(pool, key=lambda item: _version_sort_key(str(item.get("version") or "")))[-1]
        chosen = dict(chosen)
        chosen["version_selection"] = "latest_stable" if stable else "latest_preview_only"
        chosen["candidate_versions_considered"] = len(candidates)
        selected.append(chosen)
    return selected, candidate_count


def build_inventory(spec_root: Path) -> dict[str, Any]:
    spec_root = spec_root.resolve()
    commit = _repo_commit(spec_root)
    service_map: dict[str, dict[str, Any]] = {}
    parse_errors: list[dict[str, str]] = []
    file_count = 0
    operation_count = 0
    duplicate_names = 0

    for path in _candidate_files(spec_root):
        rel = path.relative_to(spec_root).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            parse_errors.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
            continue
        paths = data.get("paths")
        if not isinstance(paths, dict):
            continue
        service, provider = _service_from_path(path.relative_to(spec_root))
        if _is_excluded_product(service, provider, rel):
            continue
        plane = _plane(path)
        lifecycle = _lifecycle(path)
        version = _version(path)
        service_id = slugify(f"{service}-{plane}")
        entry = service_map.setdefault(
            service_id,
            {
                "service_id": service_id,
                "service": service,
                "plane": plane,
                "resource_providers": [],
                "lifecycles": [],
                "versions": [],
                "source_files": [],
                "operations": [],
            },
        )
        if provider and provider not in entry["resource_providers"]:
            entry["resource_providers"].append(provider)
        if lifecycle not in entry["lifecycles"]:
            entry["lifecycles"].append(lifecycle)
        if version and version not in entry["versions"]:
            entry["versions"].append(version)
        entry["source_files"].append(
            {
                "path": rel,
                "sha256": _sha256_file(path),
                "lifecycle": lifecycle,
                "version": version,
                "resource_provider": provider,
            }
        )
        file_count += 1
        seen_operation_names: set[str] = {str(op.get("operation_name") or "") for op in entry["operations"]}
        for api_path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                method_l = str(method).lower()
                if method_l not in HTTP_METHODS or not isinstance(operation, dict):
                    continue
                operation_id = str(operation.get("operationId") or "").strip()
                base_name = _operation_name(operation_id, method_l, str(api_path))
                op_name = base_name
                if op_name in seen_operation_names:
                    duplicate_names += 1
                    op_name = f"{base_name}_{slugify(version or lifecycle)}_{duplicate_names}"
                seen_operation_names.add(op_name)
                summary = str(operation.get("summary") or operation.get("description") or "")[:240]
                classification = _classification(method_l, operation_id)
                if classification == "read" and _is_sensitive_read(
                    method=method_l,
                    operation_id=operation_id,
                    path=str(api_path),
                    service=service,
                    provider=provider,
                    summary=summary,
                ):
                    classification = "sensitive_read"
                risks = _risk_categories(
                    method=method_l,
                    operation_id=operation_id,
                    path=str(api_path),
                    service=service,
                    provider=provider,
                    classification=classification,
                )
                entry["operations"].append(
                    {
                        "operation_name": op_name,
                        "operation_id": operation_id,
                        "http_method": method_l.upper(),
                        "path": str(api_path),
                        "summary": summary,
                        "classification": classification,
                        "risk_categories": risks,
                        "plane": plane,
                        "lifecycle": lifecycle,
                        "version": version,
                        "resource_provider": provider,
                        "source_file": rel,
                        "coverage_status": "implemented",
                        "notes": "Generated from pinned official Azure REST API specs.",
                    }
                )
                operation_count += 1

    selected_candidate_total = 0
    for service in service_map.values():
        selected, candidate_count = _select_latest_operations(service["operations"])
        selected_candidate_total += candidate_count
        service["operations"] = selected

    services = sorted(service_map.values(), key=lambda item: item["service_id"])
    for service in services:
        service["resource_providers"] = sorted(service["resource_providers"])
        service["lifecycles"] = sorted(service["lifecycles"])
        service["versions"] = sorted(service["versions"])
        service["operations"] = sorted(service["operations"], key=lambda item: item["operation_name"])

    return {
        "generated_at_utc": _utc_now(),
        "source": {
            "repository": SPEC_REPO_URL,
            "pinned_commit": commit,
            "expected_commit": PINNED_COMMIT,
            "inventory_strategy": "generated-inventory possible",
            "spec_root": str(spec_root),
        },
        "boundary": {
            "included": [
                "specification/**/resource-manager/**/{stable,preview}/**/*.json",
                "specification/**/data-plane/**/{stable,preview}/**/*.json",
            ],
            "excluded": [
                "specification/**/examples/**",
                "specification/**/common-types/**",
                "Azure sample/test specs such as Contoso WidgetManager and Widget demo specs",
                "Microsoft Graph, Microsoft 365, Microsoft Ads, Azure DevOps, GitHub, Xbox, LinkedIn, Dynamics, Power Platform, and other non-Azure Microsoft products",
            ],
        },
        "summary": {
            "services": len(services),
            "source_files": file_count,
            "operation_candidates": selected_candidate_total,
            "operations": operation_count,
            "selected_operations": sum(len(s["operations"]) for s in services),
            "management_operations": sum(1 for s in services for o in s["operations"] if o["plane"] == "management"),
            "data_plane_operations": sum(1 for s in services for o in s["operations"] if o["plane"] == "data_plane"),
            "stable_operations": sum(1 for s in services for o in s["operations"] if o["lifecycle"] == "stable"),
            "preview_operations": sum(1 for s in services for o in s["operations"] if o["lifecycle"] == "preview"),
            "read_operations": sum(1 for s in services for o in s["operations"] if o["classification"] in {"read", "sensitive_read"}),
            "sensitive_read_operations": sum(1 for s in services for o in s["operations"] if "sensitive_read" in (o.get("risk_categories") or [])),
            "write_operations": sum(1 for s in services for o in s["operations"] if o["classification"] == "write"),
            "duplicate_operation_names_adjusted": duplicate_names,
            "parse_errors": len(parse_errors),
        },
        "parse_errors": parse_errors[:200],
        "services": services,
    }


def write_inventory_docs(inventory: dict[str, Any], *, tool_root: Path) -> None:
    docs = tool_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "official_inventory.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = inventory["summary"]
    rows: list[str] = [
        "# Azure REST API coverage",
        "",
        "This page is the coverage ledger for the Azure safe CLI; check it when you need to know which official Azure operations are represented by generated named commands.",
        "",
        "## Official inventory snapshot",
        "",
        f"- Source repository: `{inventory['source']['repository']}`",
        f"- Pinned commit: `{inventory['source']['pinned_commit']}`",
        f"- Generated at: `{inventory['generated_at_utc']}`",
        f"- Services: `{summary['services']}`",
        f"- Source spec files: `{summary['source_files']}`",
            f"- Operation candidates across versions: `{summary['operation_candidates']}`",
            f"- Selected generated operations: `{summary['selected_operations']}`",
        f"- Management-plane operations: `{summary['management_operations']}`",
        f"- Data-plane operations: `{summary['data_plane_operations']}`",
        f"- Stable operations: `{summary['stable_operations']}`",
        f"- Preview operations: `{summary['preview_operations']}`",
        f"- Read operations: `{summary['read_operations']}`",
        f"- Sensitive read operations with default value redaction: `{summary.get('sensitive_read_operations', 0)}`",
        f"- Write operations: `{summary['write_operations']}`",
        "",
        "## Boundary",
        "",
        "- Included: official Azure REST API specs under `resource-manager` and `data-plane` stable or preview folders.",
        "- Excluded: examples, shared common types, repo plumbing, sample/test specs such as Contoso WidgetManager and Widget demo specs, Microsoft Graph, Microsoft 365, Microsoft Ads, Azure DevOps, GitHub, and other separate Microsoft products.",
        "- Preview APIs are included only because they are official Azure specs; the lifecycle column keeps that visible.",
        "- Secret/token/key/password/credential-like reads stay implemented but are marked `sensitive_read` in `docs/official_inventory.json`; their response values are redacted by default.",
        "",
        "## Generated command coverage",
        "",
        "| Service command | Plane | Lifecycles | Operations | Status | Notes |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for service in inventory["services"]:
        lifecycles = ", ".join(service.get("lifecycles") or [])
        rows.append(
            f"| `{service['service_id']}` | {service['plane']} | {lifecycles} | {len(service.get('operations') or [])} | implemented | Generated named operations from pinned official specs. |"
        )
    rows.extend(
        [
            "",
            "## Operation-level detail",
            "",
            "Operation-level detail lives in `docs/official_inventory.json` so the full ledger stays machine-readable and does not turn this page into a giant table.",
        ]
    )
    (docs / "api_coverage.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Azure REST API inventory docs")
    parser.add_argument("--spec-root", default="/tmp/azure-rest-api-specs-inventory")
    parser.add_argument("--tool-root", default=str(Path(__file__).resolve().parents[2]))
    args = parser.parse_args(argv)
    inventory = build_inventory(Path(args.spec_root))
    write_inventory_docs(inventory, tool_root=Path(args.tool_root))
    print(json.dumps({"ok": True, "summary": inventory["summary"], "pinned_commit": inventory["source"]["pinned_commit"]}, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
