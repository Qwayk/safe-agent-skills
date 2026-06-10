from __future__ import annotations

import argparse
import hashlib
import html
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

USER_AGENT = "linux:qwayk-reddit-safe-agent-cli:v0.1.0 (by /u/qwaykbot)"
SOURCE_URL = "https://www.reddit.com/dev/api/"
DEFAULT_DATE = "2026-05-22"


def _tool_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _docs_dir() -> Path:
    return _tool_root() / "docs"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip()).strip("-").lower()
    return slug or "operation"


def _normalize_text(value: str) -> str:
    text = html.unescape(value).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def _normalize_path_text(value: str) -> str:
    text = _normalize_text(value)
    text = text.replace("→", "")
    text = text.replace(" ", "")
    return text


def _required_path_params(path: str) -> list[str]:
    required: list[str] = []
    inside_optional = 0
    i = 0
    while i < len(path):
        char = path[i]
        if char == "[":
            inside_optional += 1
            i += 1
            continue
        if char == "]":
            inside_optional = max(0, inside_optional - 1)
            i += 1
            continue
        if inside_optional != 0:
            i += 1
            continue

        if char == "{":
            end = path.find("}", i + 1)
            if end != -1:
                name = path[i + 1 : end].strip()
                if name and name not in required:
                    required.append(name)
                i = end + 1
                continue
        elif char == ":":
            j = i + 1
            while j < len(path) and (path[j].isalnum() or path[j] in "_-"):
                j += 1
            name = path[i + 1 : j].strip()
            if name and name not in required:
                required.append(name)
            i = j
            continue
        i += 1
    return required


class RedditApiHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.operations: list[dict[str, str]] = []
        self._current_section: str = ""
        self._capture_section_text = False
        self._section_text_parts: list[str] = []
        self._section_depth = 0
        self._endpoint: dict[str, Any] | None = None
        self._endpoint_div_depth = 0
        self._inside_h3 = False
        self._inside_method = False
        self._inside_scope_badge = False
        self._ignore_h3_depth = 0
        self._placeholder_depth = 0
        self._inside_variants = False
        self._variant: dict[str, Any] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: (v or "") for k, v in attrs}
        classes = set(attr_map.get("class", "").split())

        if tag == "h2" and attr_map.get("id", "").startswith("section_"):
            self._capture_section_text = True
            self._section_text_parts = []
            self._section_depth = 1
            return
        if self._capture_section_text and tag != "h2":
            self._section_depth += 1

        if tag == "div" and "endpoint" in classes and attr_map.get("id"):
            self._endpoint = {
                "anchor_id": attr_map["id"],
                "section": self._current_section,
                "method": "",
                "path_parts": [],
                "scope": "",
                "variants": [],
            }
            self._endpoint_div_depth = 1
            self._inside_h3 = False
            self._inside_method = False
            self._inside_scope_badge = False
            self._ignore_h3_depth = 0
            self._placeholder_depth = 0
            self._inside_variants = False
            self._variant = None
            return
        if self._endpoint is not None and tag == "div":
            self._endpoint_div_depth += 1

        if self._endpoint is None:
            return

        if tag == "h3":
            self._inside_h3 = True
            self._inside_method = False
            self._inside_scope_badge = False
            self._ignore_h3_depth = 0
            self._placeholder_depth = 0
            return

        if self._inside_h3 and tag == "span":
            if "method" in classes:
                self._inside_method = True
            elif "oauth-scope-list" in classes or "api-badge" in classes or "rss-support" in classes:
                self._ignore_h3_depth += 1
                if "oauth-scope" in classes:
                    self._inside_scope_badge = True
            return

        if self._inside_h3 and tag == "a":
            self._ignore_h3_depth += 1
            return

        if self._inside_h3 and tag == "em" and "placeholder" in classes:
            self._placeholder_depth += 1
            return

        if tag == "ul" and "uri-variants" in classes:
            self._inside_variants = True
            return

        if self._inside_variants and tag == "li" and attr_map.get("id"):
            self._variant = {"anchor_id": attr_map["id"], "path_parts": []}
            return

        if self._variant is not None and tag == "em" and "placeholder" in classes:
            self._placeholder_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._capture_section_text:
            if tag == "h2":
                self._section_depth -= 1
                if self._section_depth <= 0:
                    self._current_section = _normalize_text("".join(self._section_text_parts))
                    self._capture_section_text = False
                return
            self._section_depth = max(0, self._section_depth - 1)

        if self._endpoint is None:
            return

        if self._variant is not None and tag == "li":
            path_parts = self._variant.get("path_parts")
            if not isinstance(path_parts, list):
                self._variant = None
                return
            path = _normalize_path_text("".join(str(item) for item in path_parts))
            if path:
                variants = self._endpoint.get("variants") if self._endpoint else None
                if isinstance(variants, list):
                    variants.append(
                        {
                            "anchor_id": str(self._variant.get("anchor_id") or ""),
                            "path": path,
                        }
                    )
            self._variant = None
            return

        if tag == "ul" and self._inside_variants:
            self._inside_variants = False
            return

        if self._inside_h3 and tag == "h3":
            self._inside_h3 = False
            return

        if self._inside_h3 and tag == "span":
            if self._inside_scope_badge:
                self._inside_scope_badge = False
                if self._ignore_h3_depth > 0:
                    self._ignore_h3_depth -= 1
            elif self._inside_method:
                self._inside_method = False
            elif self._ignore_h3_depth > 0:
                self._ignore_h3_depth -= 1
            return

        if self._inside_h3 and tag == "a" and self._ignore_h3_depth > 0:
            self._ignore_h3_depth -= 1
            return

        if tag == "em" and self._placeholder_depth > 0:
            self._placeholder_depth -= 1
            return

        if tag == "div":
            self._endpoint_div_depth -= 1
            if self._endpoint_div_depth <= 0:
                self._finalize_endpoint()
                self._endpoint = None

    def handle_data(self, data: str) -> None:
        if self._capture_section_text:
            self._section_text_parts.append(data)
            return

        if self._endpoint is None:
            return

        if self._variant is not None:
            target = self._variant.get("path_parts")
            if not isinstance(target, list):
                return
            if self._placeholder_depth > 0:
                target.append("{" + _normalize_text(data) + "}")
            else:
                target.append(data)
            return

        if not self._inside_h3:
            return

        if self._inside_method:
            self._endpoint["method"] = _normalize_text(str(self._endpoint.get("method") or "") + data)
            return

        if self._inside_scope_badge:
            self._endpoint["scope"] = _normalize_text(str(self._endpoint.get("scope") or "") + data)
            return

        if self._ignore_h3_depth > 0:
            return

        raw_path_parts = self._endpoint.get("path_parts")
        path_parts = raw_path_parts if isinstance(raw_path_parts, list) else []
        if self._placeholder_depth > 0:
            path_parts.append("{" + _normalize_text(data) + "}")
        else:
            path_parts.append(data)

    def _finalize_endpoint(self) -> None:
        assert self._endpoint is not None
        method = _normalize_text(str(self._endpoint.get("method") or "")).upper()
        raw_path = self._endpoint.get("path_parts")
        path = _normalize_path_text("".join(str(item) for item in raw_path) if isinstance(raw_path, list) else "")
        scope = _normalize_text(str(self._endpoint.get("scope") or "")).lower() or "unknown"
        section = _normalize_text(str(self._endpoint.get("section") or "misc")).lower()
        anchor_id = str(self._endpoint.get("anchor_id") or "")
        variants = self._endpoint.get("variants") or []
        records: list[dict[str, str]] = []

        if isinstance(variants, list) and variants:
            for variant in variants:
                if not isinstance(variant, dict):
                    continue
                variant_anchor = str(variant.get("anchor_id") or "").strip()
                variant_path = str(variant.get("path") or "").strip()
                if not variant_anchor or not variant_path:
                    continue
                records.append(
                    {
                        "anchor_id": variant_anchor,
                        "method": method,
                        "path": variant_path,
                        "section": section,
                        "scope": scope,
                    }
                )
        elif anchor_id and method and path:
            records.append(
                {
                    "anchor_id": anchor_id,
                    "method": method,
                    "path": path,
                    "section": section,
                    "scope": scope,
                }
            )

        for record in records:
            path_value = record["path"]
            required_path = _required_path_params(path_value)
            self.operations.append(
                {
                    "operation_command": _slugify(record["anchor_id"]),
                    "method": record["method"],
                    "path": path_value,
                    "doc_url": urljoin(SOURCE_URL, "#" + record["anchor_id"]),
                    "section": record["section"],
                    "oauth_scope": record["scope"],
                    "required_path": ",".join(required_path),
                }
            )


def fetch_official_api_html() -> str:
    response = requests.get(
        SOURCE_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=60,
    )
    response.raise_for_status()
    return response.text


def parse_operations_from_html(html_text: str) -> list[dict[str, str]]:
    parser = RedditApiHtmlParser()
    parser.feed(html_text)
    seen: set[tuple[str, str]] = set()
    operations: list[dict[str, str]] = []
    for record in parser.operations:
        key = (record["method"], record["path"])
        if key in seen:
            continue
        seen.add(key)
        operations.append(record)
    return operations


def build_operations_tsv(snapshot_name: str, snapshot_sha256: str, operations: list[dict[str, str]]) -> str:
    lines = [
        "# Reddit docs snapshot: " + snapshot_name + " sha256=" + snapshot_sha256,
        "# Source: " + SOURCE_URL,
        "# Fields: operation_command<TAB>METHOD<TAB>PATH<TAB>doc_url<TAB>[section=..]<TAB>[scope=..]<TAB>[required_path=..]",
    ]
    for record in operations:
        extras = [
            f"[section={record['section']}]",
            f"[scope={record['oauth_scope']}]",
        ]
        if record["required_path"]:
            extras.append(f"[required_path={record['required_path']}]")
        line = "\t".join(
            [
                record["operation_command"],
                record["method"],
                record["path"],
                record["doc_url"],
                *extras,
            ]
        )
        lines.append(line)
    return "\n".join(lines) + "\n"


def build_api_coverage_md(operations: list[dict[str, str]], audited_date: str) -> str:
    lines = [
        "# API coverage (Reddit Data API)",
        "",
        "Purpose:",
        "- Make official Reddit REST coverage measurable.",
        "- Keep `api <operation>` commands tied to a pinned official docs snapshot.",
        "",
        "## Summary",
        "",
        "- Provider: Reddit Data API (`/dev/api`)",
        "- Base URL (default): `https://oauth.reddit.com`",
        "- Auth: OAuth 2.0 bearer token for a registered Reddit app",
        "- Pinned docs snapshot: `docs/official_api_docs_" + audited_date + ".html`",
        "- Total operations in snapshot: **" + str(len(operations)) + "**",
        "- Last audited (UTC): " + audited_date,
        "",
        "## Inventory mapping",
        "",
        "Definition of coverage for this tool:",
        "- Every row below must be available as an explicit CLI subcommand under `qwayk-reddit-safe-agent-cli api <operation_command>`.",
        "- No raw request bridge counts toward coverage.",
        "",
        "| operation_command | METHOD | PATH | section | oauth_scope | primary_cli |",
        "|---|---:|---|---|---|---|",
    ]
    for record in operations:
        lines.append(
            "| `"
            + record["operation_command"]
            + "` | `"
            + record["method"]
            + "` | `"
            + record["path"]
            + "` | `"
            + record["section"]
            + "` | `"
            + record["oauth_scope"]
            + "` | `qwayk-reddit-safe-agent-cli api "
            + record["operation_command"]
            + "` |"
        )
    lines.extend(
        [
            "",
            "## Known gaps",
            "",
            "- None in the pinned inventory file. Runtime support still needs live access approval and OAuth setup.",
            "",
            "## Notes",
            "",
            "- Optional subreddit prefixes are shown in square brackets, for example `[/r/{subreddit}]/new`.",
            "- Deprecated or policy-limited endpoints stay in scope if they are still listed in the official docs snapshot.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh pinned Reddit API inventory from the official docs page.")
    parser.add_argument("--date", default=DEFAULT_DATE, help="UTC date label for snapshot files (default: %(default)s)")
    args = parser.parse_args()

    docs_dir = _docs_dir()
    docs_dir.mkdir(parents=True, exist_ok=True)

    html_text = fetch_official_api_html()
    operations = parse_operations_from_html(html_text)
    if not operations:
        raise RuntimeError("Did not parse any Reddit API operations from the official docs page")

    snapshot_name = f"official_api_docs_{args.date}.html"
    snapshot_path = docs_dir / snapshot_name
    snapshot_path.write_text(html_text, encoding="utf-8")
    snapshot_sha256 = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()

    tsv_path = docs_dir / f"official_operations_v1_{args.date}.txt"
    tsv_path.write_text(build_operations_tsv(snapshot_name, snapshot_sha256, operations), encoding="utf-8")

    coverage_path = docs_dir / "api_coverage.md"
    coverage_path.write_text(build_api_coverage_md(operations, audited_date=args.date), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
