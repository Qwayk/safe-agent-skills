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


def _parse_overview_method_links(html: str) -> list[str]:
    links = set(re.findall(r'href="(/api/reference/[^"]+)"', html))
    method_links = sorted([l for l in links if "/methods/" in l])
    return method_links


_API_URL_RE = re.compile(r"https://api\.openai\.com/v1[^\s\"\\]+", re.IGNORECASE)
_CURL_X_RE = re.compile(r"\s-X\s+(GET|POST|PUT|PATCH|DELETE|HEAD)\b", re.IGNORECASE)
_CURL_HAS_DATA_RE = re.compile(r"\s(-d|--data\b|--data-raw\b|-F\b)", re.IGNORECASE)
_CURL_BETA_RE = re.compile(r"OpenAI-Beta:\s*([^\"\\]+)")


def _infer_doc_operation_from_doc_page(html: str) -> tuple[str, str, str | None, bool]:
    # The API reference pages are syntax-highlighted; strip HTML tags to make regex matching stable.
    plain = re.sub(r"<[^>]+>", "", html or "")

    # Find the first mention of an OpenAI API URL (most method pages include one in the curl example).
    m = _API_URL_RE.search(plain)
    if not m:
        raise RuntimeError("Could not find curl example with https://api.openai.com/v1/... in doc page")
    url = str(m.group(0) or "").strip().strip('"').strip("'")
    if "/v1" not in url:
        raise RuntimeError(f"Unexpected curl URL (missing /v1): {url}")
    path = url.split("/v1", 1)[1] or ""
    if not path.startswith("/"):
        path = "/" + path
    path = path.split("?", 1)[0]

    # Heuristic: infer method from the nearest curl block around the URL.
    start = max(0, m.start() - 2000)
    end = min(len(plain), m.end() + 2000)
    around = plain[start:end]

    # Infer method from -X; otherwise: POST if data/form is present, else GET.
    mx = _CURL_X_RE.search(around)
    has_data = bool(_CURL_HAS_DATA_RE.search(around))
    if mx:
        method = str(mx.group(1) or "").upper()
    else:
        method = "POST" if has_data else "GET"

    beta = None
    bm = _CURL_BETA_RE.search(around)
    if bm:
        beta = str(bm.group(1) or "").strip().strip("'").strip('"') or None

    return method, path, beta, has_data


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


def _openapi_ops_index(openapi_obj: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    paths = openapi_obj.get("paths")
    if not isinstance(paths, dict):
        raise RuntimeError("OpenAPI missing paths")

    idx: dict[tuple[str, str], dict[str, Any]] = {}
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, op in path_item.items():
            ml = str(method or "").lower()
            if ml not in {"get", "post", "put", "patch", "delete", "head"}:
                continue
            if not isinstance(op, dict):
                continue
            key = (ml.upper(), str(path))
            idx[key] = op
    return idx


def _path_template_matches(concrete: str, template: str) -> bool:
    if concrete == template:
        return True
    parts = [p for p in str(template).split("/") if p != ""]
    pat_parts: list[str] = []
    for seg in parts:
        if seg.startswith("{") and seg.endswith("}") and len(seg) >= 3:
            pat_parts.append(r"[^/]+")
        else:
            pat_parts.append(re.escape(seg))
    pat = "^/" + "/".join(pat_parts) + "$"
    return re.match(pat, str(concrete)) is not None


def _count_template_params(template: str) -> int:
    return len(re.findall(r"{[a-zA-Z0-9_\\-]+}", template))


def _match_openapi_operation(
    *,
    method: str,
    concrete_path: str,
    openapi_obj: dict[str, Any],
    openapi_idx: dict[tuple[str, str], dict[str, Any]],
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """
    Returns: (path_template, path_item_obj, op_obj)
    """
    paths_obj = openapi_obj.get("paths")
    if not isinstance(paths_obj, dict):
        raise RuntimeError("OpenAPI missing paths")

    # Exact match first.
    direct = openapi_idx.get((method, concrete_path))
    if direct is not None:
        path_item = paths_obj.get(concrete_path)
        if isinstance(path_item, dict):
            return concrete_path, path_item, direct
        return concrete_path, {}, direct

    # Match doc example paths (with concrete ids) against OpenAPI templates.
    candidates: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    for path_template, path_item in paths_obj.items():
        if not isinstance(path_item, dict):
            continue
        op_obj = path_item.get(method.lower())
        if not isinstance(op_obj, dict):
            continue
        if _path_template_matches(concrete_path, str(path_template)):
            candidates.append((str(path_template), path_item, op_obj))

    if not candidates:
        raise RuntimeError(f"No OpenAPI operation matches {method} {concrete_path}")

    # Pick the most specific: fewer params, then longer literal (more stable), then stable sort.
    candidates_sorted = sorted(
        candidates,
        key=lambda c: (
            _count_template_params(c[0]),
            -len(c[0]),
            c[0],
        ),
    )
    return candidates_sorted[0]


def _is_probably_id_segment(seg: str) -> bool:
    s = str(seg or "").strip()
    if not s or len(s) < 6:
        return False
    if any(ch.isdigit() for ch in s) and ("_" in s or "-" in s):
        return True
    # Common OpenAI id-ish prefixes seen in docs.
    for prefix in (
        "file-",
        "asst_",
        "thread_",
        "run_",
        "msg_",
        "proj_",
        "org_",
        "batch_",
        "ftjob_",
        "vs_",
        "eval_",
        "evalrun_",
        "cksess_",
        "cons_",
    ):
        if s.startswith(prefix) and any(ch.isdigit() for ch in s):
            return True
    return False


def _split_path(path: str) -> list[str]:
    return [p for p in str(path or "").split("/") if p != ""]


def _template_prefix_matches(concrete_path: str, template_path: str) -> bool:
    c = _split_path(concrete_path)
    t = _split_path(template_path)
    if len(t) > len(c):
        return False
    for i, tseg in enumerate(t):
        cseg = c[i]
        if tseg.startswith("{") and tseg.endswith("}") and len(tseg) >= 3:
            continue
        if tseg != cseg:
            return False
    return True


def _synthesize_missing_openapi_operation(
    *,
    method: str,
    concrete_path: str,
    openapi_obj: dict[str, Any],
    beta_from_doc: str | None,
    has_data: bool,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    paths_obj = openapi_obj.get("paths")
    if not isinstance(paths_obj, dict):
        raise RuntimeError("OpenAPI missing paths")

    best_template: str | None = None
    best_item: dict[str, Any] | None = None
    for tpl, item in paths_obj.items():
        if not isinstance(item, dict):
            continue
        tpl_s = str(tpl)
        if not _template_prefix_matches(concrete_path, tpl_s):
            continue
        # Longest prefix wins; tie-breaker prefers fewer params.
        if best_template is None:
            best_template, best_item = tpl_s, item
            continue
        if len(_split_path(tpl_s)) > len(_split_path(best_template)):
            best_template, best_item = tpl_s, item
            continue
        if len(_split_path(tpl_s)) == len(_split_path(best_template)):
            if _count_template_params(tpl_s) < _count_template_params(best_template):
                best_template, best_item = tpl_s, item

    csegs = _split_path(concrete_path)

    if best_template and best_item is not None:
        tsegs = _split_path(best_template)
        remainder = csegs[len(tsegs) :]
        synthesized_remainder: list[str] = []
        id_idx = 1
        for seg in remainder:
            if _is_probably_id_segment(seg):
                synthesized_remainder.append("{id" + str(id_idx) + "}")
                id_idx += 1
            else:
                synthesized_remainder.append(seg)
        new_template = "/" + "/".join(tsegs + synthesized_remainder)

        # Use a best-effort op object for tags and parameter requirements.
        op_obj = best_item.get(str(method).lower())
        if not isinstance(op_obj, dict):
            op_obj = {}
            for k in ("get", "post", "put", "patch", "delete", "head"):
                cand = best_item.get(k)
                if isinstance(cand, dict):
                    op_obj = cand
                    break
        # This operation is not in the OpenAPI snapshot; avoid reusing operationIds from the prefix op.
        if isinstance(op_obj, dict) and "operationId" in op_obj:
            op_obj = dict(op_obj)
            op_obj.pop("operationId", None)

        # If the doc indicates a beta header but OpenAPI doesn't, keep it for later.
        if beta_from_doc and not _extract_beta_from_openapi_op(op_obj):
            # Do not mutate the OpenAPI snapshot object; copy and attach a minimal x-oaiMeta curl snippet.
            op_obj = dict(op_obj)
            op_obj.setdefault("x-oaiMeta", {"examples": {"request": {"curl": f'-H \"OpenAI-Beta: {beta_from_doc}\"'}}})

        # If doc shows request data but OpenAPI doesn't mark required_body, attach best-effort.
        if has_data and not _required_body(op_obj):
            op_obj = dict(op_obj)
            op_obj.setdefault("requestBody", {"required": False})

        return new_template, best_item, op_obj

    # No prefix match: generalize the full concrete path by replacing id-like segments.
    out: list[str] = []
    id_idx = 1
    for seg in csegs:
        if _is_probably_id_segment(seg):
            out.append("{id" + str(id_idx) + "}")
            id_idx += 1
        else:
            out.append(seg)
    new_template = "/" + "/".join(out)
    op_obj: dict[str, Any] = {}
    if beta_from_doc:
        op_obj["x-oaiMeta"] = {"examples": {"request": {"curl": f'-H \"OpenAI-Beta: {beta_from_doc}\"'}}}
    return new_template, {}, op_obj


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
    method_links = _parse_overview_method_links(overview_html)
    if not method_links:
        raise RuntimeError("No /methods/ links found in overview page")

    openapi_idx = _openapi_ops_index(openapi_obj)

    seen_keys: set[tuple[str, str]] = set()
    rows: list[dict[str, Any]] = []
    for rel in method_links:
        url = DOCS_ROOT + rel
        page_html = _fetch_text(url)
        try:
            method, concrete_path, beta_from_doc, has_data = _infer_doc_operation_from_doc_page(page_html)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"Failed to infer method/path from doc page: {url}: {type(e).__name__}: {e}") from None

        match = None
        try:
            match = _match_openapi_operation(
                method=method,
                concrete_path=concrete_path,
                openapi_obj=openapi_obj,
                openapi_idx=openapi_idx,
            )
        except Exception:
            match = None

        if match:
            path_template, path_item, op_obj = match
        else:
            # Some navigation method pages are not present in the OpenAPI snapshot. Synthesize a template
            # path using the closest matching OpenAPI prefix to keep path params stable when possible.
            path_template, path_item, op_obj = _synthesize_missing_openapi_operation(
                method=method,
                concrete_path=concrete_path,
                openapi_obj=openapi_obj,
                beta_from_doc=beta_from_doc,
                has_data=has_data,
            )

        key = (method, path_template)
        if key in seen_keys:
            continue
        seen_keys.add(key)

        operation_id = str((op_obj or {}).get("operationId") or "").strip()
        if not operation_id:
            # Fallback: deterministic derived name
            derived = method.lower() + "_" + path_template.strip("/").replace("/", "_").replace("{", "").replace("}", "")
            operation_id = derived

        tags_raw = (op_obj or {}).get("tags") or []
        tags = sorted([t.strip() for t in tags_raw if isinstance(t, str) and t.strip()])

        required_path = _required_path_params(openapi_obj, op_obj or {}, path_item or {})
        template_params = sorted(set(re.findall(r"{([a-zA-Z0-9_\\-]+)}", path_template)))
        required_path = sorted(set(required_path) | set(template_params))
        required_body = _required_body(op_obj or {}) or bool(has_data and method in {"POST", "PUT", "PATCH"})
        beta = _extract_beta_from_openapi_op(op_obj or {}) or beta_from_doc

        rows.append(
            {
                "operation_command": operation_id,
                "method": method,
                "path": path_template,
                "doc_url": url,
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
                "unique_method_path_count": len(seen_keys),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
