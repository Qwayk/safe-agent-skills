from __future__ import annotations

from dataclasses import dataclass

from .discovery import (
    DiscoveryDocSpec,
    MethodSpec,
    extract_method_specs,
    load_vendored_discovery_doc,
)


def to_kebab(token: str) -> str:
    # Convert camelCase/PascalCase/snake_case to kebab-case.
    if not token:
        return token
    out: list[str] = []
    prev: str | None = None
    for ch in token:
        if ch == "_":
            out.append("-")
            prev = ch
            continue
        if ch.isupper():
            if out and prev not in {"-", "_"}:
                out.append("-")
            out.append(ch.lower())
            prev = ch
            continue
        out.append(ch)
        prev = ch
    kebab = "".join(out).replace("--", "-").strip("-")
    return kebab


@dataclass(frozen=True)
class SnapshotSpec:
    service_token: str
    version_token: str
    discovery: DiscoveryDocSpec


def snapshots() -> list[SnapshotSpec]:
    return [
        SnapshotSpec(
            service_token="admin",
            version_token="v1alpha",
            discovery=DiscoveryDocSpec(
                expected_name="analyticsadmin",
                expected_version="v1alpha",
                vendor_filename="analyticsadmin_v1alpha_discovery.json",
            ),
        ),
        SnapshotSpec(
            service_token="data",
            version_token="v1beta",
            discovery=DiscoveryDocSpec(
                expected_name="analyticsdata",
                expected_version="v1beta",
                vendor_filename="analyticsdata_v1beta_discovery.json",
            ),
        ),
        SnapshotSpec(
            service_token="data",
            version_token="v1alpha",
            discovery=DiscoveryDocSpec(
                expected_name="analyticsdata",
                expected_version="v1alpha",
                vendor_filename="analyticsdata_v1alpha_discovery.json",
            ),
        ),
    ]


def methods_for_snapshot(spec: SnapshotSpec) -> list[MethodSpec]:
    doc = load_vendored_discovery_doc(spec.discovery)
    return extract_method_specs(doc)


def official_method_ids(spec: SnapshotSpec) -> list[str]:
    return [m.method_id for m in methods_for_snapshot(spec)]


def command_tokens_for_method(spec: SnapshotSpec, method: MethodSpec) -> list[str]:
    # Rule: ga4-api-tool <service> <version> <resource chain> <method>
    chain = [to_kebab(x) for x in method.resource_chain]
    method_token = to_kebab(method.method_name)
    return ["ga4-api-tool", spec.service_token, spec.version_token, *chain, method_token]


def official_commands() -> list[str]:
    cmds: list[str] = []
    for snap in snapshots():
        for m in methods_for_snapshot(snap):
            cmds.append(" ".join(command_tokens_for_method(snap, m)))
    cmds.sort()
    return cmds
