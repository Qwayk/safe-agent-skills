from __future__ import annotations

import argparse
import json
import re
import tarfile
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.request import urlopen


AUDIT_DATE = "2026-05-25"
CLI_NAME = "bluesky-safe-cli"
ATPROTO_TARBALL_URL = "https://codeload.github.com/bluesky-social/atproto/tar.gz/refs/heads/main"
BSKY_DOCS_TARBALL_URL = "https://codeload.github.com/bluesky-social/bsky-docs/tar.gz/refs/heads/main"
API_HOSTS_AND_AUTH_URL = "https://docs.bsky.app/docs/advanced-guides/api-directory"
HTTP_REFERENCE_INDEX_URL = "https://github.com/bluesky-social/bsky-docs/tree/main/docs/api"
LEXICON_INDEX_URL = "https://github.com/bluesky-social/atproto/tree/main/lexicons"


def _tool_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _docs_dir() -> Path:
    return _tool_root() / "docs"


def _download_and_extract_prefix(url: str, prefix: str, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    archive_path = target_dir / "archive.tar.gz"
    with urlopen(url) as response, archive_path.open("wb") as handle:
        handle.write(response.read())
    with tarfile.open(archive_path, "r:gz") as archive:
        members = [member for member in archive.getmembers() if member.name.startswith(prefix)]
        archive.extractall(path=target_dir, members=members)
    return target_dir / prefix


def _read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    frontmatter: dict[str, str] = {}
    for line in text.splitlines()[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"')
    return frontmatter


def _camel_to_kebab(value: str) -> str:
    text = str(value or "")
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", text)
    text = re.sub(r"([A-Za-z])([0-9])", r"\1-\2", text)
    text = re.sub(r"([0-9])([A-Za-z])", r"\1-\2", text)
    text = text.replace("_", "-")
    text = re.sub(r"[^A-Za-z0-9]+", "-", text)
    return text.strip("-").lower()


def _operation_command(lexicon_id: str) -> str:
    return "-".join(_camel_to_kebab(part) for part in lexicon_id.split("."))


def _route_hint(lexicon_id: str) -> str:
    if lexicon_id.startswith("chat.bsky."):
        return "chat"
    if lexicon_id.startswith("tools.ozone."):
        return "ozone"
    if lexicon_id.startswith("com.atproto.label."):
        return "labeler"
    if lexicon_id == "com.atproto.sync.subscribeRepos":
        return "relay"
    if lexicon_id.startswith("app.bsky."):
        return "entryway-or-pds"
    if lexicon_id.startswith("com.atproto."):
        return "entryway-or-pds"
    return "entryway-or-pds"


def _stability(lexicon_id: str, description: str, docs_source: str) -> str:
    lower = description.lower()
    if ".unspecced." in lexicon_id:
        return "unspecced"
    if ".temp." in lexicon_id:
        return "temp"
    if "active development" in lower or "considered unstable" in lower:
        return "active-development"
    if docs_source == "lexicon-only":
        return "lexicon-only"
    return "stable"


def _http_reference_pages(api_root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in sorted(api_root.glob("*.api.mdx")):
        meta = _read_frontmatter(path)
        title = str(meta.get("title") or "").strip()
        if not title or title == "AT Protocol XRPC API":
            continue
        stem = path.name[: -len(".api.mdx")]
        out[title] = f"https://docs.bsky.app/docs/api/{stem}"
    return out


def _build_inventory(lex_root: Path, docs_map: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(lex_root.rglob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        main = (obj.get("defs") or {}).get("main") or {}
        kind = str(main.get("type") or "")
        if kind not in {"query", "procedure", "subscription"}:
            continue

        lexicon_id = str(obj.get("id") or "")
        parts = lexicon_id.split(".")
        namespace = ".".join(parts[:2]) if len(parts) >= 2 else lexicon_id
        group = parts[2] if len(parts) >= 3 else ""
        docs_source = "http-reference" if lexicon_id in docs_map else "lexicon-only"
        description = str(main.get("description") or "")
        row = {
            "lexicon_id": lexicon_id,
            "operation_command": _operation_command(lexicon_id),
            "namespace": namespace,
            "group": group,
            "kind": kind,
            "http_method": {"query": "GET", "procedure": "POST", "subscription": "WS"}[kind],
            "path": f"/xrpc/{lexicon_id}",
            "doc_url": docs_map.get(
                lexicon_id,
                f"https://github.com/bluesky-social/atproto/blob/main/lexicons/{path.relative_to(lex_root).as_posix()}",
            ),
            "docs_source": docs_source,
            "stability": _stability(lexicon_id, description, docs_source),
            "route_hint": _route_hint(lexicon_id),
            "primary_cli": f"{CLI_NAME} api {_operation_command(lexicon_id)}",
            "input_encoding": ((main.get("input") or {}).get("encoding")) or None,
            "description": description,
            "query_params": sorted(((main.get("parameters") or {}).get("properties") or {}).keys()),
            "required_query_params": list((main.get("parameters") or {}).get("required") or []),
            "required_body_fields": list((((main.get("input") or {}).get("schema") or {}).get("required")) or []),
        }
        rows.append(row)

    commands = [str(row["operation_command"]) for row in rows]
    if len(commands) != len(set(commands)):
        counts = Counter(commands)
        duplicates = sorted(command for command, count in counts.items() if count > 1)
        raise RuntimeError(f"Duplicate operation_command values found: {', '.join(duplicates)}")
    return rows


def _render_api_coverage(rows: list[dict[str, Any]]) -> str:
    total = len(rows)
    http_reference = sum(1 for row in rows if row["docs_source"] == "http-reference")
    lexicon_only = total - http_reference
    namespace_counts = Counter(str(row["namespace"]) for row in rows)

    lines = [
        "# API coverage (Bluesky / atproto XRPC surface)",
        "",
        "Purpose:",
        "- Make official Bluesky API coverage measurable.",
        "- Keep every callable official lexicon tied to an explicit CLI subcommand.",
        "- Keep record lexicons honest: they are not fake extra endpoints; they are used through `com.atproto.repo.*` methods.",
        "",
        "## Summary",
        "",
        "- Provider: Bluesky / atproto lexicon APIs",
        "- Product shape: one official XRPC API world, not split products",
        "- Primary auth path: handle or DID plus app password via `com.atproto.server.createSession`, then authenticated calls via the user's PDS",
        "- Public read option: `https://public.api.bsky.app` for public Bluesky AppView reads",
        "- Official HTTP reference pages: 222",
        f"- Official callable lexicons: {total}",
        f"- Lexicon-only rows: {lexicon_only}",
        f"- Last audited (UTC): {AUDIT_DATE}",
        "",
        "Namespace totals:",
    ]
    for namespace in sorted(namespace_counts):
        lines.append(f"- `{namespace}`: {namespace_counts[namespace]}")
    lines.extend(
        [
            "",
            "Stability notes:",
            "- `unspecced` rows are official but intentionally not part of the stable public contract.",
            "- `temp` rows are official temporary lexicons and should be treated as unstable.",
            "- `active-development` rows are official lexicons whose descriptions explicitly warn they are under active development.",
            "",
            "Coverage rule for this tool:",
            f"- Every row below must be reachable as an explicit subcommand under `{CLI_NAME} api <operation_command>`.",
            "- No raw request bridge counts toward coverage.",
            "",
            "## Inventory mapping",
            "",
            "| operation_command | lexicon_id | kind | route_hint | docs_source | stability | primary_cli |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['operation_command']}` | `{row['lexicon_id']}` | `{row['kind']}` | `{row['route_hint']}` | `{row['docs_source']}` | `{row['stability']}` | `{row['primary_cli']}` |"
        )
    return "\n".join(lines) + "\n"


def _render_references(rows: list[dict[str, Any]]) -> str:
    total = len(rows)
    http_reference = sum(1 for row in rows if row["docs_source"] == "http-reference")
    lexicon_only = total - http_reference
    lines = [
        "# References",
        "",
        f"- Provider: Bluesky / atproto lexicon APIs",
        f"- Last verified (UTC): {AUDIT_DATE}",
        "",
        "Official sources used for this tool:",
        f"- {API_HOSTS_AND_AUTH_URL} — reason: official hosts, routing, and auth guide — last verified (UTC): {AUDIT_DATE}",
        f"- {HTTP_REFERENCE_INDEX_URL} — reason: official HTTP reference page inventory for callable XRPC methods — last verified (UTC): {AUDIT_DATE}",
        f"- {LEXICON_INDEX_URL} — reason: canonical official lexicon schemas and callable method definitions — last verified (UTC): {AUDIT_DATE}",
        "",
        "Current inventory snapshot:",
        f"- Callable official lexicons: {total}",
        f"- HTTP reference page coverage: {http_reference}",
        f"- Lexicon-only callable rows: {lexicon_only}",
        "",
        "Important interpretation note:",
        "- Record lexicons like `app.bsky.feed.post` and `app.bsky.graph.follow` are official schemas, but they are not callable XRPC methods. This tool exposes them through official repository methods such as `com.atproto.repo.createRecord`, `putRecord`, and `applyWrites` instead of inventing fake extra endpoint rows.",
    ]
    return "\n".join(lines) + "\n"


def _render_operations_tsv(rows: list[dict[str, Any]]) -> str:
    out = [
        f"# pinned official Bluesky inventory ({AUDIT_DATE})",
        "# operation_command\tlexicon_id\tkind\thttp_method\tpath\tdoc_url\t[namespace=...]\t[group=...]\t[docs_source=...]\t[stability=...]\t[route_hint=...]\t[input_encoding=...]\t[required_query=...]\t[required_body=...]",
    ]
    for row in rows:
        extras = [
            f"[namespace={row['namespace']}]",
            f"[group={row['group']}]",
            f"[docs_source={row['docs_source']}]",
            f"[stability={row['stability']}]",
            f"[route_hint={row['route_hint']}]",
            f"[input_encoding={row['input_encoding'] or ''}]",
            f"[required_query={','.join(row['required_query_params'])}]",
            f"[required_body={','.join(row['required_body_fields'])}]",
        ]
        out.append(
            "\t".join(
                [
                    str(row["operation_command"]),
                    str(row["lexicon_id"]),
                    str(row["kind"]),
                    str(row["http_method"]),
                    str(row["path"]),
                    str(row["doc_url"]),
                    *extras,
                ]
            )
        )
    return "\n".join(out) + "\n"


def refresh_inventory() -> dict[str, Any]:
    docs_dir = _docs_dir()
    docs_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        lex_root = _download_and_extract_prefix(ATPROTO_TARBALL_URL, "atproto-main/lexicons", temp_dir / "atproto")
        docs_api_root = _download_and_extract_prefix(BSKY_DOCS_TARBALL_URL, "bsky-docs-main/docs/api", temp_dir / "bsky-docs")
        docs_map = _http_reference_pages(docs_api_root)
        rows = _build_inventory(lex_root, docs_map)

    rows.sort(key=lambda item: (str(item["lexicon_id"]), str(item["operation_command"])))
    inventory_path = docs_dir / f"official_xrpc_inventory_v1_{AUDIT_DATE}.json"
    operations_path = docs_dir / f"official_operations_v1_{AUDIT_DATE}.tsv"
    api_coverage_path = docs_dir / "api_coverage.md"
    references_path = docs_dir / "references.md"

    inventory_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    operations_path.write_text(_render_operations_tsv(rows), encoding="utf-8")
    api_coverage_path.write_text(_render_api_coverage(rows), encoding="utf-8")
    references_path.write_text(_render_references(rows), encoding="utf-8")

    return {
        "inventory_path": str(inventory_path),
        "operations_path": str(operations_path),
        "api_coverage_path": str(api_coverage_path),
        "references_path": str(references_path),
        "count": len(rows),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh pinned official Bluesky inventory files")
    _ = parser.parse_args(argv)
    result = refresh_inventory()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
