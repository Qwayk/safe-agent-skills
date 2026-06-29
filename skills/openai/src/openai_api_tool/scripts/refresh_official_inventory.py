from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path
from typing import Any

import yaml


DOCS_OVERVIEW_URL = "https://developers.openai.com/api/reference/overview"
DOCS_ROOT = "https://developers.openai.com"
OPENAPI_YAML_URL = "https://app.stainless.com/api/spec/documented/openai/openapi.documented.yml"
DOCS_API_REFERENCE = f"{DOCS_ROOT}/api/reference"


_ALLOWED_METHODS = {"get", "post", "put", "patch", "delete", "head"}

_CURL_BETA_RE = re.compile(r"OpenAI-Beta:\s*([^\"\\]+)")


def _utc_date() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def _tool_root() -> Path:
    # .../src/openai_api_tool/scripts/refresh_official_inventory.py -> tool root is 4 levels up
    return Path(__file__).resolve().parents[3]


def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "openai-api-tool-inventory-refresh"})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310
        return r.read().decode("utf-8", errors="ignore")


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _parse_overview_method_links(html: str) -> set[str]:
    links = set(re.findall(r'href="(/api/reference/[^"]+)"', html or ""))
    return {l for l in links if "/methods/" in l}


def _resource_key(value: str) -> str:
    return re.sub(r"[-_]", "", str(value).lower()).rstrip("s")


def _normalize_snake(value: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(value))
    s = re.sub(r"\W+", "_", s)
    return re.sub(r"_+", "_", s).strip("_").lower()


def _extract_doc_method_from_meta_path(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None

    # Keep common simple route slugs and reject long natural language text.
    token = raw.split()[0]
    if not re.fullmatch(r"[a-zA-Z0-9_/-]+", token):
        return None

    method = token.strip("/").lower()
    if not method:
        return None
    if method in _ALLOWED_METHODS:
        return None
    return method.replace("_", "_")


def _extract_doc_method_from_name(value: str, method: str) -> str | None:
    if not value:
        return None
    tokens = [t.lower() for t in re.findall(r"[a-z0-9_\\-]+", str(value))]
    for token in tokens:
        if token in {"create", "generate", "new"}:
            return "create"
        if token in {"list"}:
            return "list"
        if token in {"retrieve", "get", "read"}:
            return "retrieve"
        if token in {"update", "modify", "edit"}:
            return "update"
        if token in {"delete", "remove", "remove-method"}:
            return "delete"
        if token in {"cancel", "abort"}:
            return "cancel"
        if token in {"count", "num"}:
            return "count"
    return None


def _extract_doc_method_from_operation_id(operation_id: str, method: str) -> str | None:
    if not operation_id:
        return None
    tokens = _normalize_snake(operation_id).split("_")
    for token in tokens:
        if token in {"list", "create", "retrieve", "update", "delete", "cancel", "count"}:
            return token
    return None


def _best_doc_method(op_obj: dict[str, Any], method: str) -> str:
    meta = op_obj.get("x-oaiMeta")
    if isinstance(meta, dict):
        for candidate in (meta.get("path"), meta.get("name")):
            slug = _extract_doc_method_from_meta_path(candidate)
            if slug:
                return slug
            slug = _extract_doc_method_from_name(str(candidate or ""), method)
            if slug:
                return slug

    # Preserve request operation semantics.
    fallback = {
        "get": "retrieve",
        "post": "create",
        "put": "update",
        "patch": "update",
        "delete": "delete",
        "head": "get",
    }
    default = fallback.get(method.lower(), method.lower())
    op_id = str(op_obj.get("operationId") or "").strip()
    if op_id:
        found = _extract_doc_method_from_operation_id(op_id, method)
        if found:
            return found
    return default


def _resource_segments_for_path(api_path: str, group: str | None, method_slug: str | None = None) -> list[str]:
    static_segments = [seg for seg in str(api_path).split("/") if seg and "{" not in seg]
    if not static_segments:
        return []

    if method_slug and static_segments[-1].lower().replace("_", "-") == method_slug.lower().replace("_", "-"):
        static_segments = static_segments[:-1]
    if not static_segments:
        return []

    root_index = 0
    if isinstance(group, str):
        g = group.strip()
        if g:
            for idx, seg in enumerate(static_segments):
                if _resource_key(seg) == _resource_key(g):
                    root_index = idx
                    break

    parts: list[str] = [static_segments[root_index]]
    for seg in static_segments[root_index + 1 :]:
        parts.extend(["subresources", seg])
    return parts


def _operation_doc_url(
    *,
    api_path: str,
    method: str,
    op_obj: dict[str, Any],
    overview_method_links: set[str],
) -> str:
    meta = op_obj.get("x-oaiMeta")
    if not isinstance(meta, dict):
        return DOCS_OVERVIEW_URL

    group = str(meta.get("group") or "").strip()
    if not group and not api_path:
        return DOCS_OVERVIEW_URL

    segments = _resource_segments_for_path(api_path, group or None)
    if not segments:
        return DOCS_OVERVIEW_URL

    beta = _extract_beta_from_openapi_op(op_obj)
    method_slug = _best_doc_method(op_obj, method.lower())
    segments = _resource_segments_for_path(api_path, group or None, method_slug)

    if not segments:
        return DOCS_OVERVIEW_URL

    candidates: list[str] = []

    base = f"{DOCS_API_REFERENCE}/resources"
    if beta:
        candidates.append("/".join([f"{base}/beta", *segments, "methods", method_slug]))
    candidates.append("/".join([base, *segments, "methods", method_slug]))
    if segments and segments[0] == "organization":
        candidates.append("/".join([base, "admin", "subresources", *segments, "methods", method_slug]))

    for candidate in candidates:
        rel = candidate.replace(DOCS_ROOT, "", 1)
        if rel in overview_method_links:
            return candidate
    return DOCS_OVERVIEW_URL


def _extract_beta_from_openapi_op(op_obj: dict[str, Any]) -> str | None:
    meta = op_obj.get("x-oaiMeta")
    if not isinstance(meta, dict):
        return None
    examples = meta.get("examples")
    if not isinstance(examples, dict):
        return None
    req = examples.get("request")
    if not isinstance(req, dict):
        return None
    curl = req.get("curl")
    if not isinstance(curl, str):
        return None
    m = _CURL_BETA_RE.search(curl)
    if not m:
        return None
    v = str(m.group(1) or "").strip().strip("'").strip('"')
    return v or None


def _required_path_params(openapi_obj: dict[str, Any], op_obj: dict[str, Any], path_item: dict[str, Any]) -> list[str]:
    required: set[str] = set()

    def scan(params: Any) -> None:
        if not isinstance(params, list):
            return
        for p in params:
            if not isinstance(p, dict):
                continue
            if str(p.get("in") or "") != "path":
                continue
            name = str(p.get("name") or "").strip()
            if not name:
                continue
            if bool(p.get("required")):
                required.add(name)

    scan(path_item.get("parameters"))
    scan(op_obj.get("parameters"))
    return sorted(required)


def _required_body(op_obj: dict[str, Any]) -> bool:
    rb = op_obj.get("requestBody")
    if not isinstance(rb, dict):
        return False
    return bool(rb.get("required"))


def main() -> int:
    ap = argparse.ArgumentParser(prog="refresh_official_inventory")
    ap.add_argument("--date", default=_utc_date(), help="UTC date for snapshot file names (YYYY-MM-DD)")
    ap.add_argument("--out-dir", default="docs", help="Output docs directory (tool-relative)")
    args = ap.parse_args()

    tool_root = _tool_root()
    out_dir = tool_root / str(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    openapi_yaml_text = _fetch_text(OPENAPI_YAML_URL)
    openapi_obj = yaml.safe_load(openapi_yaml_text)
    if not isinstance(openapi_obj, dict):
        raise RuntimeError("OpenAPI YAML did not parse as an object")
    version = str(((openapi_obj.get("info") or {}).get("version") or "")).strip() or "unknown"

    openapi_yml_path = out_dir / f"official_openapi_documented_v{version}_{args.date}.yml"
    _write_text(openapi_yml_path, openapi_yaml_text)
    openapi_sha = _sha256_bytes(openapi_yml_path.read_bytes())

    overview_html = _fetch_text(DOCS_OVERVIEW_URL)
    overview_method_links = _parse_overview_method_links(overview_html)
    if not overview_method_links:
        raise RuntimeError("No /methods/ links found in overview page")

    paths_obj = openapi_obj.get("paths")
    if not isinstance(paths_obj, dict):
        raise RuntimeError("OpenAPI missing paths")

    openapi_ops: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = []
    for path_template, path_item in paths_obj.items():
        if not isinstance(path_item, dict):
            continue
        for method, op_obj in path_item.items():
            method_l = str(method or "").lower()
            if method_l not in _ALLOWED_METHODS:
                continue
            if isinstance(op_obj, dict):
                openapi_ops.append((method_l.upper(), str(path_template), op_obj, path_item))

    openapi_operation_count = len(openapi_ops)
    if openapi_operation_count == 0:
        raise RuntimeError("No method/path operations found in OpenAPI")

    # OpenAPI is the operation boundary now. One row per declared method/path.
    rows: list[dict[str, Any]] = []
    for method, path_template, op_obj, path_item in openapi_ops:
        operation_id = str(op_obj.get("operationId") or "").strip()
        if not operation_id:
            # Fallback: deterministic derived name
            operation_id = (
                method.lower() + "_" + path_template.strip("/").replace("/", "_").replace("{", "").replace("}", "")
            )

        tags_raw = op_obj.get("tags") or []
        tags = sorted([t.strip() for t in tags_raw if isinstance(t, str) and t.strip()])

        required_path = _required_path_params(openapi_obj, op_obj, path_item)
        template_params = sorted(set(re.findall(r"{([a-zA-Z0-9_\\-]+)}", path_template)))
        required_path = sorted(set(required_path) | set(template_params))
        required_body = _required_body(op_obj)
        beta = _extract_beta_from_openapi_op(op_obj)

        doc_url = _operation_doc_url(
            api_path=path_template,
            method=method,
            op_obj=op_obj,
            overview_method_links=overview_method_links,
        )

        rows.append(
            {
                "operation_command": operation_id,
                "method": method,
                "path": path_template,
                "doc_url": doc_url,
                "tags": tags,
                "required_path": required_path,
                "required_body": required_body,
                "beta": beta,
            }
        )

    rows_sorted = sorted(rows, key=lambda r: (r["operation_command"], r["method"], r["path"]))

    lines: list[str] = []
    lines.append("# Pinned official operations list for openai-api-tool")
    lines.append(f"# Source: {DOCS_OVERVIEW_URL}")
    lines.append(f"# OpenAPI snapshot: {openapi_yml_path.name} sha256={openapi_sha}")
    lines.append(f"# Generated (UTC): {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    lines.append("# Fields: operation_command<TAB>METHOD<TAB>PATH<TAB>doc_url<TAB>[tags=..]<TAB>[required_path=..]<TAB>[required_body=0|1]<TAB>[beta=..]")
    for r in rows_sorted:
        tags = ",".join(r["tags"])
        req_path = ",".join(r["required_path"])
        req_body = "1" if bool(r["required_body"]) else "0"
        beta = str(r["beta"] or "").strip()
        extras = [
            f"[tags={tags}]",
            f"[required_path={req_path}]",
            f"[required_body={req_body}]",
        ]
        if beta:
            extras.append(f"[beta={beta}]")
        line = "\t".join([r["operation_command"], r["method"], r["path"], r["doc_url"], *extras])
        lines.append(line)

    ops_path = out_dir / f"official_operations_v1_{args.date}.txt"
    _write_text(ops_path, "\n".join(lines) + "\n")

    print(
        json.dumps(
            {
                "ok": True,
                "openapi_version": version,
                "openapi_snapshot": str(openapi_yml_path),
                "openapi_sha256": openapi_sha,
                "ops_file": str(ops_path),
                "ops_count": len(rows_sorted),
                "openapi_operation_count": openapi_operation_count,
                "ops_count_matches_openapi_count": len(rows_sorted) == openapi_operation_count,
                "unique_method_path_count": len(rows_sorted),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
