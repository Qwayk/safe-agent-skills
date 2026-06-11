from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator

from ..errors import NotFound, ValidationError


@dataclass(frozen=True)
class AnalyzeArgs:
    pack_dir: Path
    top_n: int
    min_negative_cost_micros: int
    min_negative_clicks: int
    min_negative_impressions: int


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise NotFound(f"File not found: {path}") from None
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid JSON file: {path} ({type(e).__name__})") from None


def _read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            for raw in f:
                s = raw.strip()
                if not s:
                    continue
                obj = json.loads(s)
                if isinstance(obj, dict):
                    yield obj
    except FileNotFoundError:
        raise NotFound(f"File not found: {path}") from None
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid JSONL file: {path} ({type(e).__name__})") from None


def _get(obj: dict[str, Any], *keys: str, default: Any = None) -> Any:  # noqa: ANN401
    cur: Any = obj
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default


def _sum_int(values: Iterable[Any]) -> int:
    total = 0
    for v in values:
        try:
            if v is None:
                continue
            total += int(v)
        except Exception:
            continue
    return total


def _sum_float(values: Iterable[Any]) -> float:
    total = 0.0
    for v in values:
        try:
            if v is None:
                continue
            total += float(v)
        except Exception:
            continue
    return total


def _table_paths_from_manifest(pack_dir: Path, manifest: dict[str, Any]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    tables = manifest.get("tables")
    if not isinstance(tables, list):
        return out
    for t in tables:
        if not isinstance(t, dict):
            continue
        name = str(t.get("name") or "").strip()
        rel = str(t.get("path") or "").strip()
        if not name or not rel:
            continue
        out[name] = (pack_dir / rel).resolve()
    return out


def _data_quality(manifest: dict[str, Any], table_paths: dict[str, Path]) -> dict[str, Any]:
    groups = manifest.get("groups")
    required_failed = False
    truncated_tables: list[str] = []
    if isinstance(groups, list):
        for g in groups:
            if not isinstance(g, dict):
                continue
            if bool(g.get("required")) and str(g.get("status") or "") == "failed":
                required_failed = True

    tables = manifest.get("tables")
    if isinstance(tables, list):
        for t in tables:
            if not isinstance(t, dict):
                continue
            if bool(t.get("truncated")):
                truncated_tables.append(str(t.get("name") or ""))

    known_tables = sorted(table_paths.keys())
    return {
        "required_group_failed": required_failed,
        "truncated_tables": sorted([t for t in truncated_tables if t]),
        "tables_present": known_tables,
    }


def _totals_from_ad_daily_metrics(path: Path) -> dict[str, Any]:
    row_count = 0
    impressions = 0
    clicks = 0
    cost_micros = 0
    conversions = 0.0
    conversions_value = 0.0
    for r in _read_jsonl(path):
        row_count += 1
        impressions += int(_get(r, "metrics", "impressions", default=0) or 0)
        clicks += int(_get(r, "metrics", "clicks", default=0) or 0)
        cost_micros += int(_get(r, "metrics", "cost_micros", default=0) or 0)
        conversions += float(_get(r, "metrics", "conversions", default=0.0) or 0.0)
        conversions_value += float(_get(r, "metrics", "conversions_value", default=0.0) or 0.0)
    totals = {
        "impressions": impressions,
        "clicks": clicks,
        "cost_micros": cost_micros,
        "conversions": conversions,
        "conversions_value": conversions_value,
    }
    c = float(totals["conversions"] or 0.0)
    totals["cpa_micros"] = int(totals["cost_micros"] / c) if c > 0 else None
    return {"row_count": row_count, "totals": totals}


def _waste_and_winners_from_ad_daily_metrics(path: Path, *, top_n: int, min_cost_micros: int) -> dict[str, Any]:
    agg: dict[str, dict[str, Any]] = {}
    for r in _read_jsonl(path):
        ad_rn = str(_get(r, "ad_group_ad", "resource_name", default="") or "").strip()
        if not ad_rn:
            # Fall back to ad id when resource name is missing.
            ad_rn = str(_get(r, "ad_group_ad", "ad", "id", default="") or "").strip()
        if not ad_rn:
            continue
        rec = agg.setdefault(
            ad_rn,
            {
                "ad_group_ad_resource_name": ad_rn,
                "campaign_resource_name": str(_get(r, "campaign", "resource_name", default="") or "").strip() or None,
                "ad_group_resource_name": str(_get(r, "ad_group", "resource_name", default="") or "").strip() or None,
                "impressions": 0,
                "clicks": 0,
                "cost_micros": 0,
                "conversions": 0.0,
                "conversions_value": 0.0,
            },
        )
        rec["impressions"] += int(_get(r, "metrics", "impressions", default=0) or 0)
        rec["clicks"] += int(_get(r, "metrics", "clicks", default=0) or 0)
        rec["cost_micros"] += int(_get(r, "metrics", "cost_micros", default=0) or 0)
        rec["conversions"] += float(_get(r, "metrics", "conversions", default=0.0) or 0.0)
        rec["conversions_value"] += float(_get(r, "metrics", "conversions_value", default=0.0) or 0.0)

    waste: list[dict[str, Any]] = []
    winners: list[dict[str, Any]] = []
    for rec in agg.values():
        cost = int(rec.get("cost_micros") or 0)
        conv = float(rec.get("conversions") or 0.0)
        if cost < min_cost_micros:
            continue
        if conv <= 0.0:
            waste.append(rec)
        else:
            rec = dict(rec)
            rec["cpa_micros"] = int(cost / conv) if conv > 0 else None
            winners.append(rec)

    waste.sort(key=lambda x: (int(x.get("cost_micros") or 0), int(x.get("clicks") or 0)), reverse=True)
    winners.sort(
        key=lambda x: (float(x.get("conversions") or 0.0), -int(x.get("cpa_micros") or 0)),
        reverse=True,
    )
    return {
        "waste_no_conversions": waste[: max(0, int(top_n or 0))],
        "top_winners": winners[: max(0, int(top_n or 0))],
    }


def _keyword_candidates_to_pause(path: Path, *, top_n: int, min_cost_micros: int, min_clicks: int) -> list[dict[str, Any]]:
    agg: dict[str, dict[str, Any]] = {}
    for r in _read_jsonl(path):
        text = str(_get(r, "ad_group_criterion", "keyword", "text", default="") or "").strip()
        match_type = str(_get(r, "ad_group_criterion", "keyword", "match_type", default="") or "").strip()
        if not text:
            continue
        k = f"{text.lower()}::{match_type}"
        rec = agg.setdefault(
            k,
            {
                "keyword_text": text,
                "keyword_match_type": match_type or None,
                "campaign_resource_name": str(_get(r, "campaign", "resource_name", default="") or "").strip() or None,
                "ad_group_resource_name": str(_get(r, "ad_group", "resource_name", default="") or "").strip() or None,
                "impressions": 0,
                "clicks": 0,
                "cost_micros": 0,
                "conversions": 0.0,
                "conversions_value": 0.0,
            },
        )
        rec["impressions"] += int(_get(r, "metrics", "impressions", default=0) or 0)
        rec["clicks"] += int(_get(r, "metrics", "clicks", default=0) or 0)
        rec["cost_micros"] += int(_get(r, "metrics", "cost_micros", default=0) or 0)
        rec["conversions"] += float(_get(r, "metrics", "conversions", default=0.0) or 0.0)
        rec["conversions_value"] += float(_get(r, "metrics", "conversions_value", default=0.0) or 0.0)

    out: list[dict[str, Any]] = []
    for rec in agg.values():
        if float(rec.get("conversions") or 0.0) > 0.0:
            continue
        if int(rec.get("cost_micros") or 0) < min_cost_micros:
            continue
        if int(rec.get("clicks") or 0) < min_clicks:
            continue
        out.append(rec)
    out.sort(key=lambda x: (int(x.get("cost_micros") or 0), int(x.get("clicks") or 0)), reverse=True)
    return out[: max(0, int(top_n or 0))]


def _url_waste_candidates(
    path: Path, *, url_key: tuple[str, ...], top_n: int, min_cost_micros: int
) -> list[dict[str, Any]]:
    agg: dict[str, dict[str, Any]] = {}
    for r in _read_jsonl(path):
        url = str(_get(r, *url_key, default="") or "").strip()
        if not url:
            continue
        rec = agg.setdefault(
            url,
            {
                "url": url,
                "impressions": 0,
                "clicks": 0,
                "cost_micros": 0,
                "conversions": 0.0,
                "conversions_value": 0.0,
            },
        )
        rec["impressions"] += int(_get(r, "metrics", "impressions", default=0) or 0)
        rec["clicks"] += int(_get(r, "metrics", "clicks", default=0) or 0)
        rec["cost_micros"] += int(_get(r, "metrics", "cost_micros", default=0) or 0)
        rec["conversions"] += float(_get(r, "metrics", "conversions", default=0.0) or 0.0)
        rec["conversions_value"] += float(_get(r, "metrics", "conversions_value", default=0.0) or 0.0)

    out: list[dict[str, Any]] = []
    for rec in agg.values():
        if float(rec.get("conversions") or 0.0) > 0.0:
            continue
        if int(rec.get("cost_micros") or 0) < min_cost_micros:
            continue
        out.append(rec)
    out.sort(key=lambda x: (int(x.get("cost_micros") or 0), int(x.get("clicks") or 0)), reverse=True)
    return out[: max(0, int(top_n or 0))]


def _candidate_negative_keywords(
    path: Path,
    *,
    top_n: int,
    min_cost_micros: int,
    min_clicks: int,
    min_impressions: int,
) -> list[dict[str, Any]]:
    agg: dict[str, dict[str, Any]] = {}
    for r in _read_jsonl(path):
        term = str(_get(r, "search_term_view", "search_term", default="") or "").strip()
        if not term:
            continue
        key = term.lower()
        rec = agg.setdefault(
            key,
            {
                "search_term": term,
                "impressions": 0,
                "clicks": 0,
                "cost_micros": 0,
                "conversions": 0.0,
                "conversions_value": 0.0,
            },
        )
        rec["impressions"] += int(_get(r, "metrics", "impressions", default=0) or 0)
        rec["clicks"] += int(_get(r, "metrics", "clicks", default=0) or 0)
        rec["cost_micros"] += int(_get(r, "metrics", "cost_micros", default=0) or 0)
        rec["conversions"] += float(_get(r, "metrics", "conversions", default=0.0) or 0.0)
        rec["conversions_value"] += float(_get(r, "metrics", "conversions_value", default=0.0) or 0.0)

    candidates: list[dict[str, Any]] = []
    for rec in agg.values():
        if float(rec.get("conversions") or 0.0) > 0.0:
            continue
        if int(rec.get("cost_micros") or 0) < min_cost_micros:
            continue
        if int(rec.get("clicks") or 0) < min_clicks:
            continue
        if int(rec.get("impressions") or 0) < min_impressions:
            continue
        candidates.append(rec)

    candidates.sort(key=lambda x: (int(x.get("cost_micros") or 0), int(x.get("clicks") or 0)), reverse=True)
    return candidates[: max(0, int(top_n or 0))]


def run_snapshot_analyze_optimize(a: AnalyzeArgs) -> dict[str, Any]:
    pack_dir = a.pack_dir.expanduser().resolve()
    manifest_path = pack_dir / "manifest.json"
    manifest_obj = _read_json(manifest_path)
    if not isinstance(manifest_obj, dict):
        raise ValidationError("manifest.json must be a JSON object")

    table_paths = _table_paths_from_manifest(pack_dir, manifest_obj)
    quality = _data_quality(manifest_obj, table_paths)

    used_tables: list[str] = []
    missing_tables: list[str] = []

    summary: dict[str, Any] = {
        "preset": manifest_obj.get("preset"),
        "customer_id": manifest_obj.get("customer_id"),
        "since": manifest_obj.get("since"),
        "until": manifest_obj.get("until"),
    }

    recommendations: dict[str, Any] = {}

    if "ad_daily_metrics" in table_paths:
        used_tables.append("ad_daily_metrics")
        summary["ad_daily_metrics"] = _totals_from_ad_daily_metrics(table_paths["ad_daily_metrics"])
        recommendations["ads"] = _waste_and_winners_from_ad_daily_metrics(
            table_paths["ad_daily_metrics"],
            top_n=a.top_n,
            min_cost_micros=a.min_negative_cost_micros,
        )
    else:
        missing_tables.append("ad_daily_metrics")

    if "search_terms_daily" in table_paths:
        used_tables.append("search_terms_daily")
        recommendations["candidate_negative_keywords"] = _candidate_negative_keywords(
            table_paths["search_terms_daily"],
            top_n=a.top_n,
            min_cost_micros=a.min_negative_cost_micros,
            min_clicks=a.min_negative_clicks,
            min_impressions=a.min_negative_impressions,
        )
    else:
        missing_tables.append("search_terms_daily")
        recommendations["candidate_negative_keywords"] = []

    if "keyword_daily_metrics" in table_paths:
        used_tables.append("keyword_daily_metrics")
        recommendations["candidate_keywords_to_pause"] = _keyword_candidates_to_pause(
            table_paths["keyword_daily_metrics"],
            top_n=a.top_n,
            min_cost_micros=a.min_negative_cost_micros,
            min_clicks=a.min_negative_clicks,
        )
    else:
        missing_tables.append("keyword_daily_metrics")
        recommendations["candidate_keywords_to_pause"] = []

    if "landing_pages_daily" in table_paths:
        used_tables.append("landing_pages_daily")
        recommendations["candidate_landing_pages_to_review"] = _url_waste_candidates(
            table_paths["landing_pages_daily"],
            url_key=("landing_page_view", "unexpanded_final_url"),
            top_n=a.top_n,
            min_cost_micros=a.min_negative_cost_micros,
        )
    else:
        missing_tables.append("landing_pages_daily")
        recommendations["candidate_landing_pages_to_review"] = []

    if "placements_daily" in table_paths:
        used_tables.append("placements_daily")
        # Placements table key depends on the GAQL resource. Prefer the preset-defined key.
        recommendations["candidate_placements_to_review"] = _url_waste_candidates(
            table_paths["placements_daily"],
            url_key=("detail_placement_view", "placement"),
            top_n=a.top_n,
            min_cost_micros=a.min_negative_cost_micros,
        )
    else:
        missing_tables.append("placements_daily")
        recommendations["candidate_placements_to_review"] = []

    return {
        "ok": True,
        "pack_dir": str(pack_dir),
        "data_quality": quality,
        "tables_used": sorted(set(used_tables)),
        "tables_missing": sorted(set(missing_tables)),
        "summary": summary,
        "recommendations": recommendations,
        "notes": [
            "This report is best-effort and purely offline (it reads the exported pack).",
            "Review candidate negative keywords carefully; exclude brand and high-intent terms when appropriate.",
        ],
    }
