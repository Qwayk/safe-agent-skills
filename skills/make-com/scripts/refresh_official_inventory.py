from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LLMS_URL = "https://developers.make.com/llms.txt"
REFERENCE_RE = re.compile(r"\((https://developers\.make\.com/api-documentation/api-reference(?:/[^)]+)?\.md)\)")
JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "make-com-safe-inventory/0.1"})
    with urllib.request.urlopen(req, timeout=30) as response:  # noqa: S310
        return response.read().decode("utf-8")


def slugify(value: str, *, fallback: str = "item") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or fallback


def page_slug(url: str) -> str:
    stem = url.removeprefix("https://developers.make.com/api-documentation/api-reference/")
    stem = stem.removesuffix(".md")
    if stem in {"", "api-reference"}:
        return "api-reference"
    return slugify(stem.replace("/", "-"))


def iter_reference_urls(llms_text: str) -> list[str]:
    urls = []
    for url in REFERENCE_RE.findall(llms_text):
        if url.endswith("/api-reference.md"):
            continue
        if url not in urls:
            urls.append(url)
    return urls


def merge_operation(block: dict[str, Any], *, source_url: str) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    family = page_slug(source_url)
    for path, methods in (block.get("paths") or {}).items():
        if not isinstance(methods, dict):
            continue
        for method, spec in methods.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            if not isinstance(spec, dict):
                continue
            summary = str(spec.get("summary") or f"{method.upper()} {path}")
            command_base = slugify(summary, fallback=f"{method}-{path}")
            scopes: list[str] = []
            for security in spec.get("security") or block.get("security") or []:
                if isinstance(security, dict):
                    for values in security.values():
                        if isinstance(values, list):
                            scopes.extend(str(v) for v in values)
            parameters = []
            for param in spec.get("parameters") or []:
                if isinstance(param, dict):
                    parameters.append(
                        {
                            "name": param.get("name"),
                            "in": param.get("in"),
                            "required": bool(param.get("required")),
                            "deprecated": bool(param.get("deprecated")),
                            "description": param.get("description"),
                            "schema": param.get("schema") or {},
                        }
                    )
            request_body = spec.get("requestBody") or {}
            request_body_required = bool(request_body.get("required"))
            destructive = method.lower() == "delete" or any(
                word in summary.lower() for word in ("delete", "remove", "purge", "revoke", "disable")
            )
            operations.append(
                {
                    "operation_key": f"{method.lower()} {path}",
                    "family_slug": family,
                    "family_title": (block.get("tags") or [{}])[0].get("name") if block.get("tags") else family,
                    "command": command_base,
                    "method": method.upper(),
                    "path": path,
                    "summary": summary,
                    "description": spec.get("description") or "",
                    "parameters": parameters,
                    "request_body_required": request_body_required,
                    "has_request_body": bool(request_body),
                    "scopes": sorted(set(scopes)),
                    "source_url": source_url,
                    "no_snapshot": method.lower() != "get",
                    "destructive": destructive,
                }
            )
    return operations


def main() -> int:
    llms = fetch(LLMS_URL)
    urls = iter_reference_urls(llms)
    operations: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for url in urls:
        try:
            text = fetch(url)
        except Exception as e:  # noqa: BLE001
            failures.append({"url": url, "error": str(e)})
            continue
        page_ops = []
        for raw in JSON_BLOCK_RE.findall(text):
            try:
                block = json.loads(raw)
            except json.JSONDecodeError as e:
                failures.append({"url": url, "error": f"json: {e.msg}"})
                continue
            if block.get("openapi") != "3.0.0":
                continue
            page_ops.extend(merge_operation(block, source_url=url))
        seen_commands: dict[str, int] = {}
        for op in page_ops:
            command = str(op["command"])
            count = seen_commands.get(command, 0)
            seen_commands[command] = count + 1
            if count:
                op["command"] = f"{command}-{count + 1}"
        operations.extend(page_ops)
        pages.append({"url": url, "family_slug": page_slug(url), "operation_count": len(page_ops)})
    operations.sort(key=lambda item: (item["family_slug"], item["command"], item["method"], item["path"]))
    inventory = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": {
            "llms_url": LLMS_URL,
            "boundary": "Official Make Developer Hub Make API Reference Markdown pages with embedded OpenAPI 3.0 JSON blocks.",
        },
        "servers": [
            "https://eu1.make.com/api/v2",
            "https://eu2.make.com/api/v2",
            "https://us1.make.com/api/v2",
            "https://us2.make.com/api/v2",
            "https://eu1.make.celonis.com/api/v2",
            "https://us1.make.celonis.com/api/v2",
        ],
        "pages": pages,
        "failures": failures,
        "operations": operations,
    }
    out = ROOT / "docs" / "official_inventory.json"
    out.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    data_dir = ROOT / "src" / "make_com_safe_agent_cli" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "official_inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {out} with {len(operations)} operations from {len(pages)} pages")
    if failures:
        print(f"failures: {len(failures)}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
