#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RpcDef:
    package: str
    service: str
    method: str
    http_bindings: tuple[tuple[str, str], ...]  # (VERB, PATH)

    @property
    def rpc(self) -> str:
        return f"{self.package}.{self.service}.{self.method}"


_RE_LINE_COMMENT = re.compile(r"//.*?$", flags=re.MULTILINE)
_RE_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", flags=re.DOTALL)


def _strip_comments(text: str) -> str:
    text = _RE_BLOCK_COMMENT.sub("", text)
    text = _RE_LINE_COMMENT.sub("", text)
    return text


def _find_matching_brace(text: str, open_idx: int) -> int:
    if open_idx < 0 or open_idx >= len(text) or text[open_idx] != "{":
        raise ValueError("open_idx must point to '{'")
    depth = 0
    in_str = False
    escape = False
    for i in range(open_idx, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_str = False
            continue
        else:
            if ch == '"':
                in_str = True
                continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("Unmatched '{'")


def _parse_package(text: str, *, file: Path) -> str:
    m = re.search(r"\bpackage\s+([a-zA-Z0-9_.]+)\s*;", text)
    if not m:
        raise RuntimeError(f"Missing package in {file}")
    return m.group(1).strip()


def _iter_service_blocks(text: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in re.finditer(r"\bservice\s+([A-Za-z0-9_]+)\s*\{", text):
        name = m.group(1)
        open_idx = m.end() - 1
        close_idx = _find_matching_brace(text, open_idx)
        body = text[open_idx + 1 : close_idx]
        out.append((name, body))
    return out


def _iter_rpc_blocks(service_body: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in re.finditer(r"\brpc\s+([A-Za-z0-9_]+)\s*\(", service_body):
        method = m.group(1)
        after = service_body[m.end() :]
        brace_pos = after.find("{")
        semi_pos = after.find(";")
        if semi_pos != -1 and (brace_pos == -1 or semi_pos < brace_pos):
            out.append((method, ""))
            continue
        if brace_pos == -1:
            continue
        open_idx = m.end() + brace_pos
        close_idx = _find_matching_brace(service_body, open_idx)
        body = service_body[open_idx + 1 : close_idx]
        out.append((method, body))
    return out


def _parse_http_bindings(rpc_body: str, *, file: Path, rpc: str) -> tuple[tuple[str, str], ...]:
    m = re.search(r"option\s*\(google\.api\.http\)\s*=\s*\{", rpc_body)
    if not m:
        raise RuntimeError(f"Missing google.api.http option for {rpc} in {file}")
    open_idx = m.end() - 1
    close_idx = _find_matching_brace(rpc_body, open_idx)
    block = rpc_body[open_idx + 1 : close_idx]

    bindings: list[tuple[str, str]] = []
    for verb, path in re.findall(
        r"\b(get|put|post|delete|patch|head|options)\s*:\s*\"([^\"]+)\"",
        block,
        flags=re.IGNORECASE,
    ):
        bindings.append((verb.upper(), path))

    for kind, path in re.findall(
        r"\bcustom\s*\{[^}]*?\bkind\s*:\s*\"([^\"]+)\"[^}]*?\bpath\s*:\s*\"([^\"]+)\"[^}]*?\}",
        block,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        bindings.append((kind.upper(), path))

    if not bindings:
        raise RuntimeError(f"No HTTP bindings parsed for {rpc} in {file}")
    return tuple(bindings)


def _extract_path_params(path: str) -> tuple[tuple[str, str], ...]:
    """
    Return path template variables as (template_name, cli_arg_name).

    Example:
      "/api/.../{account_id}" -> ("account_id", "account_id")
      "/api/.../{account.id}" -> ("account.id", "account_id")
    """
    template_vars: list[str] = []
    for m in re.finditer(r"\{([^}=]+)(=[^}]*)?\}", path):
        template_vars.append(m.group(1).strip())

    # Keep stable order and uniqueness.
    seen_tpl: set[str] = set()
    unique_tpl: list[str] = []
    for v in template_vars:
        if v and v not in seen_tpl:
            seen_tpl.add(v)
            unique_tpl.append(v)

    out: list[tuple[str, str]] = []
    used_args: set[str] = set()
    for tpl in unique_tpl:
        base = re.sub(r"[^A-Za-z0-9_]+", "_", tpl).strip("_").lower() or "param"
        arg = base
        i = 2
        while arg in used_args:
            arg = f"{base}_{i}"
            i += 1
        used_args.add(arg)
        out.append((tpl, arg))

    return tuple(out)


def _kebab(s: str) -> str:
    out = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    out = re.sub(r"[^a-zA-Z0-9]+", "-", out).strip("-")
    return out.lower()


def _domain_from_package(pkg: str) -> str:
    parts = [p for p in pkg.split(".") if p]
    if parts[:2] == ["qdrant", "cloud"]:
        parts = parts[2:]
    if not parts:
        return "cloud"
    return "-".join([_kebab(p) for p in parts])


def _build_command_names(rpcs: list[RpcDef]) -> dict[str, str]:
    candidates: dict[str, list[RpcDef]] = {}
    for r in rpcs:
        key = f"{_domain_from_package(r.package)}::{_kebab(r.method)}"
        candidates.setdefault(key, []).append(r)

    out: dict[str, str] = {}
    for key, defs in candidates.items():
        _domain, rpc_kebab = key.split("::", 1)
        if len(defs) == 1:
            out[defs[0].rpc] = rpc_kebab
            continue
        # collision: include service name
        for d in defs:
            out[d.rpc] = f"{_kebab(d.service)}-{rpc_kebab}"

    per_domain: dict[str, set[str]] = {}
    for rpc, cmd in out.items():
        pkg = rpc.rsplit(".", 2)[0]
        dom = _domain_from_package(pkg)
        per_domain.setdefault(dom, set())
        if cmd in per_domain[dom]:
            raise RuntimeError(f"Duplicate command name within domain '{dom}': {cmd}")
        per_domain[dom].add(cmd)

    return out


def load_rpcs(proto_root: Path) -> list[RpcDef]:
    protos = sorted(proto_root.rglob("*.proto"))
    if not protos:
        raise RuntimeError(f"No .proto files found under {proto_root}")

    out: list[RpcDef] = []
    for f in protos:
        text = _strip_comments(f.read_text(encoding="utf-8"))
        pkg = _parse_package(text, file=f)
        for service, svc_body in _iter_service_blocks(text):
            for method, rpc_body in _iter_rpc_blocks(svc_body):
                if not rpc_body.strip():
                    raise RuntimeError(f"RPC missing body/options: {pkg}.{service}.{method} in {f}")
                bindings = _parse_http_bindings(rpc_body, file=f, rpc=f"{pkg}.{service}.{method}")
                out.append(RpcDef(package=pkg, service=service, method=method, http_bindings=bindings))
    return out


def _render_operations_py(rows: list[dict[str, object]], *, version_tag: str) -> str:
    lines: list[str] = []
    lines.append("from __future__ import annotations\n\n")
    lines.append("import dataclasses\n\n\n")
    lines.append("@dataclasses.dataclass(frozen=True)\n")
    lines.append("class Operation:\n")
    lines.append("    rpc: str\n")
    lines.append("    domain: str\n")
    lines.append("    service: str\n")
    lines.append("    method: str\n")
    lines.append("    http_verb: str\n")
    lines.append("    http_path: str\n")
    lines.append("    path_params: tuple[tuple[str, str], ...]\n")
    lines.append("    command_name: str\n\n\n")
    lines.append(f"INVENTORY_VERSION = {version_tag!r}\n")
    lines.append(f"INVENTORY_OPERATION_COUNT = {len(rows)}\n\n")

    lines.append("OPERATIONS: tuple[Operation, ...] = (\n")
    for r in rows:
        raw_pp = r.get("path_params")
        if isinstance(raw_pp, list):
            pp = tuple(tuple(p) for p in raw_pp)  # type: ignore[arg-type]
        else:
            pp = ()
        lines.append(
            "    Operation("
            f"rpc={r['rpc']!r}, domain={r['domain']!r}, service={r['service']!r}, method={r['method']!r}, "
            f"http_verb={r['http_verb']!r}, http_path={r['http_path']!r}, "
            f"path_params={pp!r}, command_name={r['command_name']!r}"
            "),\n"
        )
    lines.append(")\n\n")

    lines.append("OPERATIONS_BY_DOMAIN: dict[str, list[Operation]] = {}\n")
    lines.append("OPERATIONS_BY_RPC: dict[str, Operation] = {}\n")
    lines.append("for op in OPERATIONS:\n")
    lines.append("    OPERATIONS_BY_RPC[op.rpc] = op\n")
    lines.append("    OPERATIONS_BY_DOMAIN.setdefault(op.domain, []).append(op)\n")
    lines.append("for dom in OPERATIONS_BY_DOMAIN:\n")
    lines.append("    OPERATIONS_BY_DOMAIN[dom] = sorted(OPERATIONS_BY_DOMAIN[dom], key=lambda o: o.rpc)\n\n\n")

    lines.append("def find_operation_by_rpc(rpc: str) -> Operation:\n")
    lines.append("    op = OPERATIONS_BY_RPC.get(str(rpc))\n")
    lines.append("    if not op:\n")
    lines.append("        raise KeyError(f\"Unknown RPC: {rpc}\")\n")
    lines.append("    return op\n\n\n")

    lines.append("def find_verification_read_op(op: Operation) -> Operation | None:\n")
    lines.append("    # Deterministic best-effort: same path template, GET.\n")
    lines.append("    for cand in OPERATIONS:\n")
    lines.append("        if cand.http_verb.upper() == 'GET' and cand.http_path == op.http_path and cand.path_params == op.path_params:\n")
    lines.append("            return cand\n")
    lines.append("    return None\n")
    return "".join(lines)


def _render_api_coverage_md(rows: list[dict[str, object]]) -> str:
    from datetime import UTC, datetime

    audited_utc = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = []
    lines.append("# API coverage\n")
    lines.append("\n")
    lines.append(f"Last audited (UTC): {audited_utc}\n")
    lines.append("\n")
    lines.append(
        "100% coverage definition: every RPC listed in `docs/official_rpcs_v1.txt` has a first-class CLI command.\n"
    )
    lines.append("\n")
    lines.append(f"Coverage count: **{len(rows)} RPCs**.\n")
    lines.append("\n")
    lines.append("## Mapping (RPC → CLI)\n")
    lines.append("\n")
    lines.append("Format: `domain command` ← `HTTP_VERB PATH` ← `RPC`\n")
    lines.append("\n")
    for r in rows:
        lines.append(
            f"- `{r['domain']} {r['command_name']}` ← `{r['http_verb']} {r['http_path']}` ← `{r['rpc']}`\n"
        )
    return "".join(lines)


def write_inventory(*, tool_root: Path, rpcs: list[RpcDef], version_tag: str) -> None:
    docs = tool_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)

    commands_by_rpc = _build_command_names(rpcs)

    rpcs_path = docs / f"official_rpcs_{version_tag}.txt"
    routes_path = docs / f"official_http_routes_{version_tag}.txt"
    cmds_path = docs / f"official_commands_{version_tag}.txt"

    rpcs_lines = [r.rpc for r in rpcs]
    routes_lines: list[str] = []
    for r in rpcs:
        for verb, path in r.http_bindings:
            routes_lines.append(f"{verb} {path} {r.rpc}")

    cmd_lines: list[str] = []
    for r in rpcs:
        dom = _domain_from_package(r.package)
        cmd_lines.append(f"{dom} {commands_by_rpc[r.rpc]}")

    rpcs_path.write_text("\n".join(rpcs_lines) + "\n", encoding="utf-8")
    routes_path.write_text("\n".join(routes_lines) + "\n", encoding="utf-8")
    cmds_path.write_text("\n".join(cmd_lines) + "\n", encoding="utf-8")

    rows: list[dict[str, object]] = []
    for r in rpcs:
        verb, path = r.http_bindings[0]
        dom = _domain_from_package(r.package)
        rows.append(
            {
                "rpc": r.rpc,
                "domain": dom,
                "service": r.service,
                "method": r.method,
                "http_verb": verb,
                "http_path": path,
                "path_params": list(_extract_path_params(path)),
                "command_name": commands_by_rpc[r.rpc],
            }
        )

    rows_sorted = sorted(rows, key=lambda x: (str(x["domain"]), str(x["rpc"])))

    ops_py = tool_root / "src" / "qdrant_cloud_api_tool" / f"operations_{version_tag}.py"
    ops_py.write_text(_render_operations_py(rows_sorted, version_tag=version_tag), encoding="utf-8")

    coverage_path = docs / "api_coverage.md"
    coverage_path.write_text(_render_api_coverage_md(rows_sorted), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--tool-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Tool root (default: this tool folder)",
    )
    ap.add_argument(
        "--vendor-proto-root",
        default=None,
        help="Vendored proto root (folder that contains the proto/ tree). Defaults to vendor/qdrant-cloud-public-api/<commit>/",
    )
    ap.add_argument("--version-tag", default="v1", help="Inventory version tag (default: v1)")
    args = ap.parse_args()

    tool_root = Path(args.tool_root).resolve()
    if args.vendor_proto_root:
        vendor_root = Path(args.vendor_proto_root).resolve()
    else:
        vend_parent = tool_root / "vendor" / "qdrant-cloud-public-api"
        commits = sorted([p for p in vend_parent.iterdir() if p.is_dir()])
        if not commits:
            raise RuntimeError(f"No vendored protos found under {vend_parent}")
        vendor_root = commits[-1]

    proto_root = vendor_root / "proto"
    rpcs = load_rpcs(proto_root)
    write_inventory(tool_root=tool_root, rpcs=rpcs, version_tag=str(args.version_tag))
    print(f"ok: rpcs={len(rpcs)} vendor={vendor_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
