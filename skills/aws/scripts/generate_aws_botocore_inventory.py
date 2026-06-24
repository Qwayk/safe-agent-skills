#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import boto3
import botocore
from botocore.exceptions import DataNotFoundError
from botocore.loaders import Loader

DEFAULT_DATE = "2026-06-24"


def _tool_root() -> Path:
    return Path(__file__).resolve().parents[1]


sys.path.insert(0, str(_tool_root() / "src"))

from aws_safe_agent_cli.aws_runtime import _operation_policy  # noqa: E402


def _kebab_from_operation_name(name: str) -> str:
    step1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    step2 = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", step1)
    return step2.replace("_", "-").lower()


def _botocore_data_dir() -> Path:
    return Path(botocore.__path__[0]) / "data"


def _make_loader() -> Loader:
    # Lock discovery to the packaged botocore data that ships with the pinned wheel.
    return Loader(
        extra_search_paths=[str(_botocore_data_dir())],
        include_default_search_paths=False,
        include_default_extras=False,
    )


def _load_operations(loader: Loader, service: str) -> dict[str, object]:
    api_versions = loader.list_api_versions(service, "service-2")
    selected_api_version = loader.determine_latest_version(service, "service-2")
    service_model = loader.load_service_model(service, "service-2", selected_api_version)
    operation_names = sorted(service_model.get("operations", {}).keys())
    operations: list[dict[str, object]] = []
    for operation_name in operation_names:
        policy = _operation_policy(service, operation_name)
        operations.append(
            {
                "operation_name": operation_name,
                "command": _kebab_from_operation_name(operation_name),
                "status": "generated_named_command",
                "mode": policy["mode"],
                "risk_categories": policy["risk_categories"],
                "requires_plan": policy["requires_plan"],
                "requires_ack_no_snapshot": policy["requires_ack_no_snapshot"],
                "requires_ack_irreversible": policy["requires_ack_irreversible"],
            }
        )

    paginator_names: list[str] = []
    try:
        paginator_model = loader.load_service_model(service, "paginators-1")
    except DataNotFoundError:
        paginator_model = None
    if paginator_model:
        paginator_names = sorted(paginator_model.get("pagination", {}).keys())

    waiter_names: list[str] = []
    try:
        waiter_model = loader.load_service_model(service, "waiters-2")
    except DataNotFoundError:
        waiter_model = None
    if waiter_model:
        waiter_names = sorted(waiter_model.get("waiters", {}).keys())

    return {
        "service": service,
        "api_version": selected_api_version,
        "available_api_versions": api_versions,
        "operation_count": len(operation_names),
        "operation_names": operation_names,
        "operations": operations,
        "paginator_count": len(paginator_names),
        "paginator_names": paginator_names,
        "waiter_count": len(waiter_names),
        "waiter_names": waiter_names,
    }


def build_inventory(*, date: str = DEFAULT_DATE) -> dict[str, object]:
    loader = _make_loader()
    endpoints = loader.load_data("endpoints")
    services = sorted(loader.list_available_services("service-2"))

    service_rows = [_load_operations(loader, service) for service in services]
    multi_version_rows = [
        {
            "service": row["service"],
            "available_api_versions": row["available_api_versions"],
            "selected_api_version": row["api_version"],
        }
        for row in service_rows
        if len(row["available_api_versions"]) > 1
    ]
    selected_api_versions = [
        {"service": row["service"], "api_version": row["api_version"]} for row in service_rows
    ]

    paginator_service_count = sum(1 for row in service_rows if row["paginator_count"])
    waiter_service_count = sum(1 for row in service_rows if row["waiter_count"])

    operation_status_counts: Counter[str] = Counter()
    operation_mode_counts: Counter[str] = Counter()
    risk_category_counts: Counter[str] = Counter()
    for row in service_rows:
        for operation in row["operations"]:
            operation_status_counts[str(operation["status"])] += 1
            operation_mode_counts[str(operation["mode"])] += 1
            for category in operation["risk_categories"]:
                risk_category_counts[str(category)] += 1

    exceptions_ledger = [
        {
            "bucket": "console-only-api",
            "official_source": "AWS service API reference or AWS console/help documentation",
            "status": "outside_coverage_not_claimed",
            "note": "Official AWS surfaces outside packaged Botocore were not claimed as covered in this source build.",
        },
        {
            "bucket": "modeled-but-conditional",
            "official_source": "AWS service API reference and packaged botocore service model",
            "status": "covered_by_generated_command_when_access_allows",
            "note": "The operation has a generated named command, but AWS may still refuse it based on region, account state, permissions, resource type, or gated service access.",
        },
        {
            "bucket": "multi-version-service-model",
            "official_source": "botocore/data/<service>/<apiVersion>/service-2.json",
            "status": "selected_latest_packaged_api_version",
            "note": "When Botocore ships multiple service-model apiVersions, the generated inventory records the selected latest packaged version.",
        },
        {
            "bucket": "support-metadata",
            "official_source": "botocore paginators, waiters, endpoint, retry, and sdk-extras models",
            "status": "accounted_as_metadata",
            "note": "Paginator, waiter, endpoint, retry, and SDK metadata are counted separately because they are not standalone AWS operations.",
        },
        {
            "bucket": "legacy-or-separate-guide",
            "official_source": "Official AWS legacy appendix, separate service guide, or migration page",
            "status": "outside_coverage_not_claimed_until_researched",
            "note": "Legacy or separately documented official surfaces outside packaged Botocore need a targeted official-doc review before any full-AWS claim includes them.",
        },
    ]
    summary = {
        "date": date,
        "boto3_version": boto3.__version__,
        "botocore_version": botocore.__version__,
        "service_count": len(service_rows),
        "operation_count": sum(int(row["operation_count"]) for row in service_rows),
        "paginator_service_count": paginator_service_count,
        "paginator_count": sum(int(row["paginator_count"]) for row in service_rows),
        "waiter_service_count": waiter_service_count,
        "waiter_count": sum(int(row["waiter_count"]) for row in service_rows),
        "endpoints_model_version": endpoints.get("version"),
        "partitions_count": len(endpoints.get("partitions", [])),
        "multi_version_service_count": len(multi_version_rows),
        "operation_status_counts": dict(sorted(operation_status_counts.items())),
        "operation_mode_counts": dict(sorted(operation_mode_counts.items())),
        "risk_category_counts": dict(sorted(risk_category_counts.items())),
    }

    inventory = {
        "date": date,
        "boto3_version": boto3.__version__,
        "botocore_version": botocore.__version__,
        "source": "Packaged botocore data only",
        "botocore_data_dir": "botocore/data from the pinned botocore wheel",
        "summary": summary,
        "endpoints_model_version": summary["endpoints_model_version"],
        "partitions_count": summary["partitions_count"],
        "service_count": summary["service_count"],
        "operation_count": summary["operation_count"],
        "paginator_service_count": summary["paginator_service_count"],
        "paginator_count": summary["paginator_count"],
        "waiter_service_count": summary["waiter_service_count"],
        "waiter_count": summary["waiter_count"],
        "services_with_multiple_versions": multi_version_rows,
        "selected_api_versions": selected_api_versions,
        "services": service_rows,
        "exceptions_ledger": exceptions_ledger,
    }
    return inventory


def _render_list_line(label: str, value: object) -> str:
    return f"- {label}: {value}\n"


def _render_service_row(row: dict[str, object]) -> str:
    return (
        "| "
        + str(row["service"])
        + " | "
        + str(row["api_version"])
        + " | "
        + str(row["operation_count"])
        + " | "
        + str(row["paginator_count"])
        + " | "
        + str(row["waiter_count"])
        + " |\n"
    )


def _render_multi_version_row(row: dict[str, object]) -> str:
    versions = ", ".join(str(version) for version in row["available_api_versions"])
    return (
        "| "
        + str(row["service"])
        + " | "
        + versions
        + " | "
        + str(row["selected_api_version"])
        + " |\n"
    )


def render_coverage_markdown(inventory: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append("# API coverage\n")
    lines.append("\n")
    lines.append(
        "This is the exact boundary for the AWS coverage claim. The tool covers the pinned Botocore service models packaged with Boto3/Botocore 1.43.36, and it does not claim official AWS surfaces outside that package unless they are listed here.\n"
    )
    lines.append(
        "Use this page when you need to check whether the command list and the coverage claim really match.\n"
    )
    lines.append("\n")
    lines.append("## Boundary\n")
    lines.append("\n")
    lines.append("- Packaged botocore data only\n")
    lines.append("- No `~/.aws/models` lookup\n")
    lines.append("- No `AWS_DATA_PATH` lookup\n")
    lines.append(f"- Date: {inventory['date']}\n")
    lines.append("\n")
    lines.append("## Inventory summary\n")
    lines.append("\n")
    lines.append(_render_list_line("Services", inventory["service_count"]))
    lines.append(_render_list_line("Operations", inventory["operation_count"]))
    lines.append(
        _render_list_line(
            "Paginator services",
            f"{inventory['paginator_service_count']} / {inventory['service_count']}",
        )
    )
    lines.append(_render_list_line("Paginators", inventory["paginator_count"]))
    lines.append(
        _render_list_line(
            "Waiter services",
            f"{inventory['waiter_service_count']} / {inventory['service_count']}",
        )
    )
    lines.append(_render_list_line("Waiters", inventory["waiter_count"]))
    lines.append(_render_list_line("Endpoints model version", inventory["endpoints_model_version"]))
    lines.append(_render_list_line("Partitions", inventory["partitions_count"]))
    summary = inventory["summary"]
    status_counts = summary["operation_status_counts"]
    lines.append(_render_list_line("Generated named commands", status_counts["generated_named_command"]))
    lines.append(
        _render_list_line(
            "Services with multiple service-model versions",
            len(inventory["services_with_multiple_versions"]),
        )
    )
    lines.append(
        _render_list_line(
            "Full per-operation inventory",
            "`docs/_generated/aws_botocore_inventory.json`",
        )
    )
    lines.append("\n")
    lines.append("## Generated per-operation evidence\n")
    lines.append("\n")
    lines.append(
        "The generated JSON ledger records every operation with `operation_name`, generated command name, status, mode, risk categories, and acknowledgement requirements.\n"
    )
    lines.append("\n")
    lines.append("| Status | Operations |\n")
    lines.append("|---|---:|\n")
    for status, count in status_counts.items():
        lines.append(f"| `{status}` | {count} |\n")
    lines.append("\n")
    lines.append("## Safety and risk coverage\n")
    lines.append("\n")
    lines.append(
        "These counts come from the same generated ledger. They do not replace human review; they prove that every pinned operation received a conservative safety class.\n"
    )
    lines.append("\n")
    lines.append("| Mode | Operations |\n")
    lines.append("|---|---:|\n")
    for mode, count in summary["operation_mode_counts"].items():
        lines.append(f"| `{mode}` | {count} |\n")
    lines.append("\n")
    lines.append("| Risk category | Operations |\n")
    lines.append("|---|---:|\n")
    for category, count in summary["risk_category_counts"].items():
        lines.append(f"| `{category}` | {count} |\n")
    lines.append("\n")
    lines.append("## Services with multiple service-model versions\n")
    lines.append("\n")
    lines.append("| Service | Available apiVersions | Selected apiVersion |\n")
    lines.append("|---|---|---|\n")
    for row in inventory["services_with_multiple_versions"]:
        lines.append(_render_multi_version_row(row))
    lines.append("\n")
    lines.append("## Service inventory\n")
    lines.append("\n")
    lines.append(
        "This table keeps the human coverage page readable. The generated JSON file records every operation name under its service row.\n"
    )
    lines.append("\n")
    lines.append("| Service | apiVersion | Operations | Paginators | Waiters |\n")
    lines.append("|---|---|---:|---:|---:|\n")
    for row in inventory["services"]:
        lines.append(_render_service_row(row))
    lines.append("\n")
    lines.append("## Exceptions ledger\n")
    lines.append("\n")
    lines.append("This ledger keeps the model boundary honest. It does not claim official AWS surfaces outside packaged Botocore until they are researched and added explicitly.\n")
    lines.append("\n")
    lines.append("| Bucket | Official source bucket | Status | Note |\n")
    lines.append("|---|---|---|---|\n")
    for row in inventory["exceptions_ledger"]:
        lines.append(
            "| "
            + str(row["bucket"])
            + " | "
            + str(row["official_source"])
            + " | "
            + str(row["status"])
            + " | "
            + str(row["note"])
            + " |\n"
        )
    return "".join(lines)


def write_outputs(*, inventory: dict[str, object], output: Path, coverage: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    coverage.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    coverage.write_text(render_coverage_markdown(inventory), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the pinned AWS botocore inventory and coverage page.")
    parser.add_argument(
        "--output",
        default=str(_tool_root() / "docs" / "_generated" / "aws_botocore_inventory.json"),
        help="Write the inventory JSON here.",
    )
    parser.add_argument(
        "--coverage",
        default=str(_tool_root() / "docs" / "api_coverage.md"),
        help="Write the rendered coverage markdown here.",
    )
    parser.add_argument(
        "--date",
        default=DEFAULT_DATE,
        help="Date label for the generated files. Default: %(default)s",
    )
    args = parser.parse_args()

    inventory = build_inventory(date=args.date)
    write_outputs(inventory=inventory, output=Path(args.output), coverage=Path(args.coverage))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
