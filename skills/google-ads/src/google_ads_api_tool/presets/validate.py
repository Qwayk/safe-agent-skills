from __future__ import annotations

import re
import string
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any


_ALLOWED_PLACEHOLDERS = {"customer_id", "since", "until"}
_REQUIRED_PLACEHOLDERS_DATE_RANGE = {"since", "until"}


def _extract_placeholders(template: str) -> set[str]:
    placeholders: set[str] = set()
    fmt = string.Formatter()
    for literal_text, field_name, format_spec, conversion in fmt.parse(template):  # noqa: B007
        if not field_name:
            continue
        # Field names can include indexing, attribute access, etc. We do not allow that here.
        base = field_name.split("[", 1)[0].split(".", 1)[0].strip()
        if base:
            placeholders.add(base)
    return placeholders


def _is_safe_output_filename(name: str) -> bool:
    s = str(name or "")
    if not s or s.strip() != s:
        return False
    if s.startswith("."):
        return False
    if "/" in s or "\\" in s:
        return False
    if ".." in s:
        return False
    p = PurePosixPath(s)
    if p.name != s:
        return False
    return bool(re.match(r"^[A-Za-z0-9_.-]+$", s))


@dataclass(frozen=True)
class PresetValidationResult:
    ok: bool
    errors: list[str]


def validate_preset_dict(preset: dict[str, Any], *, source: str = "<preset>") -> PresetValidationResult:
    errs: list[str] = []
    if not isinstance(preset, dict):
        return PresetValidationResult(ok=False, errors=[f"{source}: preset must be a JSON object"])

    v = preset.get("preset_schema_version")
    if v != 1:
        errs.append(f"{source}: preset_schema_version must be 1")

    name = preset.get("name")
    if not isinstance(name, str) or not name.strip():
        errs.append(f"{source}: name must be a non-empty string")

    desc = preset.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errs.append(f"{source}: description must be a non-empty string")

    join_map = preset.get("join_map")
    if not isinstance(join_map, dict) or not join_map:
        errs.append(f"{source}: join_map must be a non-empty object")
        join_map = {}

    if isinstance(join_map, dict):
        for jk, jv in join_map.items():
            if not isinstance(jk, str) or not jk.strip():
                errs.append(f"{source}: join_map keys must be non-empty strings")
                continue
            if not isinstance(jv, dict):
                errs.append(f"{source}: join_map[{jk}] must be an object")
                continue
            d = jv.get("description")
            if not isinstance(d, str) or not d.strip():
                errs.append(f"{source}: join_map[{jk}].description must be a non-empty string")
            fields = jv.get("fields")
            if not isinstance(fields, list) or not fields or not all(isinstance(x, str) and x.strip() for x in fields):
                errs.append(f"{source}: join_map[{jk}].fields must be a non-empty list of strings")

    groups = preset.get("query_groups")
    if not isinstance(groups, list) or not groups:
        errs.append(f"{source}: query_groups must be a non-empty list")
        groups = []

    seen_group_ids: set[str] = set()
    seen_outputs: set[str] = set()
    for i, g in enumerate(groups):
        label = f"{source}: query_groups[{i}]"
        if not isinstance(g, dict):
            errs.append(f"{label} must be an object")
            continue

        gid = g.get("group_id")
        if not isinstance(gid, str) or not gid.strip():
            errs.append(f"{label}.group_id must be a non-empty string")
            gid = None
        if isinstance(gid, str):
            if gid in seen_group_ids:
                errs.append(f"{label}.group_id duplicates an earlier group_id: {gid}")
            seen_group_ids.add(gid)

        required = g.get("required")
        if not isinstance(required, bool):
            errs.append(f"{label}.required must be a boolean")

        requires_date_range = g.get("requires_date_range", True)
        if not isinstance(requires_date_range, bool):
            errs.append(f"{label}.requires_date_range must be a boolean if provided")
            requires_date_range = True

        output = g.get("output")
        if not isinstance(output, str) or not _is_safe_output_filename(output) or not output.endswith(".jsonl"):
            errs.append(f"{label}.output must be a safe filename ending with .jsonl")
            output = None
        if isinstance(output, str):
            if output in seen_outputs:
                errs.append(f"{label}.output duplicates an earlier output filename: {output}")
            seen_outputs.add(output)

        join_keys = g.get("join_keys")
        if not isinstance(join_keys, list) or not join_keys or not all(isinstance(x, str) and x.strip() for x in join_keys):
            errs.append(f"{label}.join_keys must be a non-empty list of strings")
            join_keys = []
        for jk in join_keys:
            if isinstance(join_map, dict) and jk not in join_map:
                errs.append(f"{label}.join_keys references missing join key in join_map: {jk}")

        templates = g.get("gaql_templates")
        if not isinstance(templates, dict) or not templates:
            errs.append(f"{label}.gaql_templates must be a non-empty object")
            templates = {}
        if isinstance(templates, dict):
            if "base" not in templates:
                errs.append(f"{label}.gaql_templates must include a 'base' template")
            for tname, t in templates.items():
                if not isinstance(tname, str) or not tname.strip():
                    errs.append(f"{label}.gaql_templates keys must be non-empty strings")
                    continue
                if not isinstance(t, str) or not t.strip():
                    errs.append(f"{label}.gaql_templates[{tname}] must be a non-empty string")
                    continue
                ph = _extract_placeholders(t)
                unknown = sorted([x for x in ph if x not in _ALLOWED_PLACEHOLDERS])
                if unknown:
                    errs.append(f"{label}.gaql_templates[{tname}] contains unknown placeholders: {', '.join(unknown)}")
                if requires_date_range:
                    missing = sorted([x for x in _REQUIRED_PLACEHOLDERS_DATE_RANGE if x not in ph])
                    if missing:
                        errs.append(
                            f"{label}.gaql_templates[{tname}] missing required placeholders: {', '.join(missing)}"
                        )

        mrd = g.get("max_rows_default")
        if mrd is not None:
            try:
                mrd_i = int(mrd)
            except Exception:
                errs.append(f"{label}.max_rows_default must be an integer if provided")
            else:
                if mrd_i <= 0:
                    errs.append(f"{label}.max_rows_default must be > 0 if provided")

    return PresetValidationResult(ok=(len(errs) == 0), errors=errs)
