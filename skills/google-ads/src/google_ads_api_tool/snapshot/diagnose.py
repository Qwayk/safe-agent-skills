from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from .analyze import (
    _candidate_negative_keywords,
    _data_quality,
    _get,
    _keyword_candidates_to_pause,
    _read_json,
    _read_jsonl,
    _table_paths_from_manifest,
    _totals_from_ad_daily_metrics,
    _url_waste_candidates,
)


MIN_IMPRESSIONS_FOR_PRESSURE = 50
HIGH_LOST_IMPRESSION_SHARE = 0.20
LOW_SEARCH_IMPRESSION_SHARE = 0.20
LOW_QUALITY_SCORE = 5
MIN_QUALITY_SIGNAL_IMPRESSIONS = 5
HIGH_CONFIDENCE_QUALITY_IMPRESSIONS = 10
HIGH_CONFIDENCE_QUALITY_CLICKS = 2
HIGH_CONFIDENCE_QUALITY_COST_MICROS = 5_000_000
LOW_OPTIMIZATION_SCORE = 0.80
TRACKING_RISK_MIN_CLICKS = 15
TRACKING_RISK_MIN_COST_MICROS = 10_000_000
TOP_CANDIDATE_FINDINGS = 10
NEGATIVE_MIN_COST_MICROS = 5_000_000
NEGATIVE_MIN_CLICKS = 3
NEGATIVE_MIN_IMPRESSIONS = 100
POOR_RSA_STRENGTH = {"POOR", "AVERAGE"}
LOW_RSA_ASSET_LABELS = {"LOW"}
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
GOOGLE_ADS_DOCS_ROUTE = "google_ads_docs"
BOOKS_OR_HUMAN_ROUTE = "books_or_human"
PLAN_FIRST_CATEGORIES = {
    "rank_pressure",
    "quality_score_issue",
    "rsa_issue",
    "search_term_cleanup",
    "keyword_pause_candidate",
    "landing_page_review",
    "placement_review",
}
CATEGORY_DOC_QUERIES = {
    "budget_pressure": [
        "What does lost impression share due to budget mean in Google Ads Search?"
    ],
    "rank_pressure": [
        "What does lost impression share due to rank mean in Google Ads Search and what fixes it?"
    ],
    "mixed_pressure": [
        "How do I interpret budget and rank lost impression share together in Google Ads Search?"
    ],
    "low_volume_or_targeting_limited": [
        "Why do Google Ads Search campaigns get low impressions even when budget and rank loss stay low?"
    ],
    "quality_score_issue": [
        "What are the Quality Score components in Google Ads Search and how do I improve them?"
    ],
    "rsa_issue": [
        "What is ad strength in responsive search ads and how should I improve it?"
    ],
    "search_term_cleanup": [
        "How should I use the search terms report to add negative keywords in Google Ads?"
    ],
    "keyword_pause_candidate": [],
    "landing_page_review": [
        "What landing-page factors affect Google Ads Search quality and post-click experience?"
    ],
    "placement_review": [
        "How should I review placements that spend without conversions in Google Ads?"
    ],
    "tracking_risk": [
        "How do primary conversion actions and conversion tracking work in Google Ads?"
    ],
    "recommendation_review": [
        "What is Google Ads optimization score and when should I trust recommendations?",
        "How do Google Ads recommendations and auto-apply work?"
    ],
}
CATEGORY_SUPPORT_ROUTE = {
    "keyword_pause_candidate": BOOKS_OR_HUMAN_ROUTE,
}


@dataclass(frozen=True)
class DiagnoseArgs:
    pack_dir: Path


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _get_any(obj: dict[str, Any], *paths: tuple[str, ...], default: Any = None) -> Any:
    for path in paths:
        value = _get(obj, *path, default=None)
        if value is not None:
            return value
    return default


def _resource_tail(resource_name: str | None) -> str | None:
    value = str(resource_name or "").strip()
    if not value or "/" not in value:
        return value or None
    return value.rsplit("/", 1)[-1] or None


def _entity_ref(
    *,
    entity_type: str,
    resource_name: str | None = None,
    entity_id: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    return {
        "type": entity_type,
        "resource_name": resource_name,
        "id": entity_id or _resource_tail(resource_name),
        "name": name,
    }


def _finding(
    *,
    finding_id: str,
    level: str,
    category: str,
    scope: str,
    entity_refs: list[dict[str, Any]],
    evidence: dict[str, Any],
    explanation: str,
    recommended_next_step: str,
    requires_human_review: bool,
) -> dict[str, Any]:
    return {
        "id": finding_id,
        "level": level,
        "category": category,
        "scope": scope,
        "support_route": CATEGORY_SUPPORT_ROUTE.get(category, GOOGLE_ADS_DOCS_ROUTE),
        "entity_refs": entity_refs,
        "evidence": evidence,
        "explanation": explanation,
        "recommended_next_step": recommended_next_step,
        "recommended_doc_queries": list(CATEGORY_DOC_QUERIES.get(category, [])),
        "requires_human_review": requires_human_review,
    }


def _campaign_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        campaign = row.get("campaign")
        if not isinstance(campaign, dict):
            continue
        resource_name = str(campaign.get("resource_name") or "").strip()
        if not resource_name:
            continue
        index[resource_name] = campaign
    return index


def _ad_group_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        ad_group = row.get("ad_group")
        if not isinstance(ad_group, dict):
            continue
        resource_name = str(ad_group.get("resource_name") or "").strip()
        if not resource_name:
            continue
        index[resource_name] = ad_group
    return index


def _ad_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        ad_group_ad = row.get("ad_group_ad")
        if not isinstance(ad_group_ad, dict):
            continue
        resource_name = str(ad_group_ad.get("resource_name") or "").strip()
        if not resource_name:
            continue
        index[resource_name] = row
    return index


def _aggregate_ad_metrics(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        ad_group_ad_rn = str(_get(row, "ad_group_ad", "resource_name", default="") or "").strip()
        if not ad_group_ad_rn:
            continue
        rec = index.setdefault(
            ad_group_ad_rn,
            {
                "impressions": 0,
                "clicks": 0,
                "cost_micros": 0,
                "conversions": 0.0,
                "conversions_value": 0.0,
            },
        )
        rec["impressions"] += _to_int(_get(row, "metrics", "impressions", default=0))
        rec["clicks"] += _to_int(_get(row, "metrics", "clicks", default=0))
        rec["cost_micros"] += _to_int(_get(row, "metrics", "cost_micros", default=0))
        rec["conversions"] += _to_float(_get(row, "metrics", "conversions", default=0.0))
        rec["conversions_value"] += _to_float(_get(row, "metrics", "conversions_value", default=0.0))
    return index


def _merged_ad_rows(
    *,
    ad_group_ads_rows: list[dict[str, Any]],
    ad_daily_metrics_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    ad_metrics_index = _aggregate_ad_metrics(ad_daily_metrics_rows)
    merged_rows: list[dict[str, Any]] = []
    for row in ad_group_ads_rows:
        ad_group_ad_rn = str(_get(row, "ad_group_ad", "resource_name", default="") or "").strip()
        merged = dict(row)
        merged["metrics"] = dict(ad_metrics_index.get(ad_group_ad_rn) or {})
        merged_rows.append(merged)
    return merged_rows


def _weighted_avg(sum_value: float, weight: int) -> float | None:
    if weight <= 0:
        return None
    return sum_value / float(weight)


def _load_rows(table_paths: dict[str, Path], table_name: str) -> list[dict[str, Any]]:
    path = table_paths.get(table_name)
    if path is None:
        return []
    return list(_read_jsonl(path))


def _has_quality_signal(*, impressions: int, clicks: int, cost_micros: int) -> bool:
    return (
        impressions >= MIN_QUALITY_SIGNAL_IMPRESSIONS
        or clicks > 0
        or cost_micros >= NEGATIVE_MIN_COST_MICROS
    )


def _has_high_confidence_quality_signal(*, impressions: int, clicks: int, cost_micros: int) -> bool:
    has_volume_signal = impressions >= HIGH_CONFIDENCE_QUALITY_IMPRESSIONS
    has_click_signal = clicks >= HIGH_CONFIDENCE_QUALITY_CLICKS
    has_spend_signal = cost_micros >= HIGH_CONFIDENCE_QUALITY_COST_MICROS
    return has_click_signal or (has_volume_signal and (clicks > 0 or has_spend_signal))


def _pressure_findings(
    *,
    table_paths: dict[str, Path],
    campaign_index: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    path = table_paths.get("campaign_pressure_daily")
    if path is None:
        return []

    aggregate: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(path):
        campaign_rn = str(_get(row, "campaign", "resource_name", default="") or "").strip()
        if not campaign_rn:
            continue
        impressions = _to_int(_get(row, "metrics", "impressions", default=0))
        weight = max(impressions, 1)
        rec = aggregate.setdefault(
            campaign_rn,
            {
                "campaign_resource_name": campaign_rn,
                "campaign_id": str(_get(row, "campaign", "id", default="") or "").strip() or None,
                "impressions": 0,
                "clicks": 0,
                "cost_micros": 0,
                "conversions": 0.0,
                "conversions_value": 0.0,
                "search_impression_share_sum": 0.0,
                "search_impression_share_weight": 0,
                "search_budget_lost_impression_share_sum": 0.0,
                "search_budget_lost_impression_share_weight": 0,
                "search_rank_lost_impression_share_sum": 0.0,
                "search_rank_lost_impression_share_weight": 0,
                "search_exact_match_impression_share_sum": 0.0,
                "search_exact_match_impression_share_weight": 0,
                "search_top_impression_share_sum": 0.0,
                "search_top_impression_share_weight": 0,
                "search_absolute_top_impression_share_sum": 0.0,
                "search_absolute_top_impression_share_weight": 0,
            },
        )
        rec["impressions"] += impressions
        rec["clicks"] += _to_int(_get(row, "metrics", "clicks", default=0))
        rec["cost_micros"] += _to_int(_get(row, "metrics", "cost_micros", default=0))
        rec["conversions"] += _to_float(_get(row, "metrics", "conversions", default=0.0))
        rec["conversions_value"] += _to_float(_get(row, "metrics", "conversions_value", default=0.0))
        for metric in (
            "search_impression_share",
            "search_budget_lost_impression_share",
            "search_rank_lost_impression_share",
            "search_exact_match_impression_share",
            "search_top_impression_share",
            "search_absolute_top_impression_share",
        ):
            value = _get(row, "metrics", metric, default=None)
            if value is None or value == "":
                continue
            rec[f"{metric}_sum"] += _to_float(value) * float(weight)
            rec[f"{metric}_weight"] += weight

    findings: list[dict[str, Any]] = []
    for campaign_rn, rec in sorted(aggregate.items()):
        search_impression_share = _weighted_avg(
            rec["search_impression_share_sum"],
            rec["search_impression_share_weight"],
        )
        budget_lost = _weighted_avg(
            rec["search_budget_lost_impression_share_sum"],
            rec["search_budget_lost_impression_share_weight"],
        )
        rank_lost = _weighted_avg(
            rec["search_rank_lost_impression_share_sum"],
            rec["search_rank_lost_impression_share_weight"],
        )
        if search_impression_share is None and budget_lost is None and rank_lost is None:
            continue

        category: str | None = None
        level = "medium"
        next_step = "Review the campaign state, search terms, and targeting before planning any live changes."
        requires_human_review = False

        budget_lost_value = budget_lost or 0.0
        rank_lost_value = rank_lost or 0.0
        search_is_value = search_impression_share or 0.0
        impressions = int(rec["impressions"])

        if budget_lost_value >= HIGH_LOST_IMPRESSION_SHARE and rank_lost_value >= HIGH_LOST_IMPRESSION_SHARE:
            category = "mixed_pressure"
            level = "high"
            next_step = "Build a no-apply plan that separates budget pressure from rank pressure before changing spend, bids, or targeting."
            requires_human_review = True
        elif budget_lost_value >= HIGH_LOST_IMPRESSION_SHARE and rank_lost_value < HIGH_LOST_IMPRESSION_SHARE:
            category = "budget_pressure"
            level = "high"
            next_step = "Build a budget review plan first. Confirm the campaign is actually limited by budget before raising spend."
            requires_human_review = True
        elif rank_lost_value >= HIGH_LOST_IMPRESSION_SHARE and budget_lost_value < HIGH_LOST_IMPRESSION_SHARE:
            category = "rank_pressure"
            level = "high"
            next_step = "Review keyword quality, RSA strength, and landing-page fit before planning any bid or ad changes."
        elif impressions < MIN_IMPRESSIONS_FOR_PRESSURE and budget_lost_value < HIGH_LOST_IMPRESSION_SHARE and rank_lost_value < HIGH_LOST_IMPRESSION_SHARE:
            category = "low_volume_or_targeting_limited"
            level = "medium"
            next_step = "Review search demand, geo coverage, schedule, and targeting before assuming the campaign needs more budget or bids."
        elif (
            search_is_value <= LOW_SEARCH_IMPRESSION_SHARE
            and budget_lost_value < HIGH_LOST_IMPRESSION_SHARE
            and rank_lost_value < HIGH_LOST_IMPRESSION_SHARE
        ):
            category = "low_volume_or_targeting_limited"
            level = "medium"
            next_step = "Review search demand, targeting limits, and keyword coverage before changing budgets or bids."

        if category is None:
            continue

        campaign_meta = campaign_index.get(campaign_rn) or {}
        campaign_name = str(campaign_meta.get("name") or "").strip() or None
        campaign_id = str(campaign_meta.get("id") or rec["campaign_id"] or "").strip() or None
        explanation = (
            f"Campaign delivery looks {category.replace('_', ' ')} over the exported date range. "
            f"Impressions={impressions}, search_impression_share={search_is_value:.4f}, "
            f"search_budget_lost_impression_share={budget_lost_value:.4f}, "
            f"search_rank_lost_impression_share={rank_lost_value:.4f}."
        )
        findings.append(
            _finding(
                finding_id=f"{category}:{campaign_id or _resource_tail(campaign_rn) or campaign_rn}",
                level=level,
                category=category,
                scope="campaign",
                entity_refs=[
                    _entity_ref(
                        entity_type="campaign",
                        resource_name=campaign_rn,
                        entity_id=campaign_id,
                        name=campaign_name,
                    )
                ],
                evidence={
                    "impressions": impressions,
                    "clicks": int(rec["clicks"]),
                    "cost_micros": int(rec["cost_micros"]),
                    "conversions": round(float(rec["conversions"]), 6),
                    "conversions_value": round(float(rec["conversions_value"]), 6),
                    "search_impression_share": search_impression_share,
                    "search_budget_lost_impression_share": budget_lost,
                    "search_rank_lost_impression_share": rank_lost,
                    "search_exact_match_impression_share": _weighted_avg(
                        rec["search_exact_match_impression_share_sum"],
                        rec["search_exact_match_impression_share_weight"],
                    ),
                    "search_top_impression_share": _weighted_avg(
                        rec["search_top_impression_share_sum"],
                        rec["search_top_impression_share_weight"],
                    ),
                    "search_absolute_top_impression_share": _weighted_avg(
                        rec["search_absolute_top_impression_share_sum"],
                        rec["search_absolute_top_impression_share_weight"],
                    ),
                },
                explanation=explanation,
                recommended_next_step=next_step,
                requires_human_review=requires_human_review,
            )
        )
    return findings


def _quality_findings(table_paths: dict[str, Path]) -> list[dict[str, Any]]:
    path = table_paths.get("keyword_quality_snapshot")
    if path is None:
        return []

    ranked_rows: list[tuple[int, int, int, int, int, dict[str, Any], list[str], int | None]] = []
    for row in _read_jsonl(path):
        quality_score_raw = _get(row, "ad_group_criterion", "quality_info", "quality_score", default=None)
        quality_score = None if quality_score_raw in {None, ""} else _to_int(quality_score_raw)
        weak_components: list[str] = []
        component_map = {
            "predicted_ctr": _get(row, "ad_group_criterion", "quality_info", "search_predicted_ctr", default=None),
            "creative_quality": _get(row, "ad_group_criterion", "quality_info", "creative_quality_score", default=None),
            "post_click_quality": _get(row, "ad_group_criterion", "quality_info", "post_click_quality_score", default=None),
        }
        for label, value in component_map.items():
            if str(value or "").strip() == "BELOW_AVERAGE":
                weak_components.append(label)
        if quality_score is None and not weak_components:
            continue
        if quality_score is not None and quality_score > LOW_QUALITY_SCORE and not weak_components:
            continue
        impressions = _to_int(_get(row, "metrics", "impressions", default=0))
        clicks = _to_int(_get(row, "metrics", "clicks", default=0))
        cost_micros = _to_int(_get(row, "metrics", "cost_micros", default=0))
        if not _has_quality_signal(impressions=impressions, clicks=clicks, cost_micros=cost_micros):
            continue
        evidence_rank = 0 if _has_high_confidence_quality_signal(impressions=impressions, clicks=clicks, cost_micros=cost_micros) else 1
        sort_penalty = quality_score if quality_score is not None else 10
        ranked_rows.append((evidence_rank, sort_penalty, -clicks, -impressions, -cost_micros, row, weak_components, quality_score))

    ranked_rows.sort(key=lambda item: item[:5])
    findings: list[dict[str, Any]] = []
    for evidence_rank, _, _, _, _, row, weak_components, quality_score in ranked_rows[:TOP_CANDIDATE_FINDINGS]:
        keyword_text = str(_get(row, "ad_group_criterion", "keyword", "text", default="") or "").strip() or None
        match_type = str(_get(row, "ad_group_criterion", "keyword", "match_type", default="") or "").strip() or None
        campaign_rn = str(_get(row, "campaign", "resource_name", default="") or "").strip() or None
        ad_group_rn = str(_get(row, "ad_group", "resource_name", default="") or "").strip() or None
        impressions = _to_int(_get(row, "metrics", "impressions", default=0))
        clicks = _to_int(_get(row, "metrics", "clicks", default=0))
        cost_micros = _to_int(_get(row, "metrics", "cost_micros", default=0))
        evidence = {
            "quality_score": quality_score,
            "search_predicted_ctr": _get(row, "ad_group_criterion", "quality_info", "search_predicted_ctr", default=None),
            "creative_quality_score": _get(row, "ad_group_criterion", "quality_info", "creative_quality_score", default=None),
            "post_click_quality_score": _get(row, "ad_group_criterion", "quality_info", "post_click_quality_score", default=None),
            "primary_status": _get(row, "ad_group_criterion", "primary_status", default=None),
            "primary_status_reasons": _get(row, "ad_group_criterion", "primary_status_reasons", default=None),
            "system_serving_status": _get(row, "ad_group_criterion", "system_serving_status", default=None),
            "evidence_strength": "high_confidence" if evidence_rank == 0 else "early_signal",
            "impressions": impressions,
            "clicks": clicks,
            "cost_micros": cost_micros,
            "conversions": round(_to_float(_get(row, "metrics", "conversions", default=0.0)), 6),
        }
        if evidence_rank == 0 and quality_score is not None and quality_score <= 3:
            level = "high"
        elif evidence_rank == 0 and len(weak_components) >= 2:
            level = "high"
        else:
            level = "medium"
        parts: list[str] = []
        if quality_score is not None:
            parts.append(f"quality score {quality_score}")
        if weak_components:
            parts.append("weak components: " + ", ".join(weak_components))
        explanation = (
            f"Keyword quality looks weak for {keyword_text or 'this keyword'}"
            f"{f' ({match_type})' if match_type else ''}: " + "; ".join(parts) + "."
        )
        findings.append(
            _finding(
                finding_id=f"quality_score_issue:{_resource_tail(str(_get(row, 'ad_group_criterion', 'resource_name', default='') or '')) or keyword_text or 'keyword'}",
                level=level,
                category="quality_score_issue",
                scope="keyword",
                entity_refs=[
                    _entity_ref(
                        entity_type="campaign",
                        resource_name=campaign_rn,
                        name=str(_get(row, "campaign", "name", default="") or "").strip() or None,
                    ),
                    _entity_ref(
                        entity_type="ad_group",
                        resource_name=ad_group_rn,
                        name=str(_get(row, "ad_group", "name", default="") or "").strip() or None,
                    ),
                    _entity_ref(
                        entity_type="keyword",
                        resource_name=str(_get(row, "ad_group_criterion", "resource_name", default="") or "").strip() or None,
                        name=(f"{keyword_text} [{match_type}]" if keyword_text and match_type else keyword_text),
                    ),
                ],
                evidence=evidence,
                explanation=explanation,
                recommended_next_step="Review search intent alignment, RSA relevance, and landing-page promise before planning any keyword or ad changes.",
                requires_human_review=False,
            )
        )
    return findings


def _rsa_findings(
    *,
    table_paths: dict[str, Path],
    ad_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not ad_rows:
        return []

    low_asset_counts: dict[str, int] = {}
    if "rsa_asset_performance" in table_paths:
        for row in _read_jsonl(table_paths["rsa_asset_performance"]):
            ad_group_ad_rn = str(_get(row, "ad_group_ad", "resource_name", default="") or "").strip()
            label = str(
                _get(row, "ad_group_ad_asset_view", "performance_label", default="") or ""
            ).strip()
            if not ad_group_ad_rn or label not in LOW_RSA_ASSET_LABELS:
                continue
            low_asset_counts[ad_group_ad_rn] = low_asset_counts.get(ad_group_ad_rn, 0) + 1

    ranked: list[tuple[int, int, dict[str, Any], int]] = []
    for row in ad_rows:
        ad_group_ad_rn = str(_get(row, "ad_group_ad", "resource_name", default="") or "").strip()
        ad_type = str(
            _get_any(
                row,
                ("ad_group_ad", "ad", "type"),
                ("ad_group_ad", "ad", "type_"),
                default="",
            )
            or ""
        ).strip()
        if ad_type and ad_type != "RESPONSIVE_SEARCH_AD":
            continue
        ad_strength = str(_get(row, "ad_group_ad", "ad_strength", default="") or "").strip()
        low_count = low_asset_counts.get(ad_group_ad_rn, 0)
        if ad_strength not in POOR_RSA_STRENGTH and low_count < 2:
            continue
        impressions = _to_int(_get(row, "metrics", "impressions", default=0))
        rank = 0 if ad_strength == "POOR" else 1
        ranked.append((rank, -impressions, row, low_count))

    ranked.sort(key=lambda item: (item[0], item[1]))
    findings: list[dict[str, Any]] = []
    for _, _, row, low_count in ranked[:TOP_CANDIDATE_FINDINGS]:
        ad_group_ad_rn = str(_get(row, "ad_group_ad", "resource_name", default="") or "").strip() or None
        ad_strength = str(_get(row, "ad_group_ad", "ad_strength", default="") or "").strip() or None
        policy_approval = _get(row, "ad_group_ad", "policy_summary", "approval_status", default=None)
        policy_review = _get(row, "ad_group_ad", "policy_summary", "review_status", default=None)
        ad_id = str(_get(row, "ad_group_ad", "ad", "id", default="") or "").strip() or None
        ad_name = f"ad {ad_id}" if ad_id else None
        details = [f"ad strength {ad_strength or 'unknown'}"]
        if low_count:
            details.append(f"{low_count} LOW RSA asset labels")
        explanation = (
            f"Responsive Search Ad quality looks weak for {ad_name or 'this ad'}: "
            + "; ".join(details)
            + "."
        )
        findings.append(
            _finding(
                finding_id=f"rsa_issue:{ad_id or _resource_tail(ad_group_ad_rn or '') or 'ad'}",
                level="high" if ad_strength == "POOR" else "medium",
                category="rsa_issue",
                scope="ad",
                entity_refs=[
                    _entity_ref(
                        entity_type="campaign",
                        resource_name=str(_get(row, "campaign", "resource_name", default="") or "").strip() or None,
                        name=str(_get(row, "campaign", "name", default="") or "").strip() or None,
                    ),
                    _entity_ref(
                        entity_type="ad_group",
                        resource_name=str(_get(row, "ad_group", "resource_name", default="") or "").strip() or None,
                        name=str(_get(row, "ad_group", "name", default="") or "").strip() or None,
                    ),
                    _entity_ref(
                        entity_type="ad",
                        resource_name=ad_group_ad_rn,
                        entity_id=ad_id,
                        name=ad_name,
                    ),
                ],
                evidence={
                    "ad_strength": ad_strength,
                    "low_asset_label_count": low_count,
                    "approval_status": policy_approval,
                    "review_status": policy_review,
                    "impressions": _to_int(_get(row, "metrics", "impressions", default=0)),
                    "clicks": _to_int(_get(row, "metrics", "clicks", default=0)),
                    "cost_micros": _to_int(_get(row, "metrics", "cost_micros", default=0)),
                    "conversions": round(_to_float(_get(row, "metrics", "conversions", default=0.0)), 6),
                },
                explanation=explanation,
                recommended_next_step="Review RSA headline and description coverage before planning any live ad edits. Do not auto-apply recommendation changes.",
                requires_human_review=False,
            )
        )
    return findings


def _candidate_findings(
    *,
    category: str,
    scope: str,
    rows: list[dict[str, Any]],
    next_step: str,
    requires_human_review: bool,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for idx, row in enumerate(rows[:TOP_CANDIDATE_FINDINGS], start=1):
        level = "high" if _to_int(row.get("cost_micros")) >= 20_000_000 else "medium"
        entity_name = None
        entity_type = scope
        if category == "search_term_cleanup":
            entity_name = str(row.get("search_term") or "").strip() or None
        elif category == "keyword_pause_candidate":
            text = str(row.get("keyword_text") or "").strip()
            match_type = str(row.get("keyword_match_type") or "").strip()
            entity_name = f"{text} [{match_type}]" if text and match_type else (text or None)
        else:
            entity_name = str(row.get("url") or "").strip() or None
        explanation = (
            f"{entity_name or scope} spent {_to_int(row.get('cost_micros'))} micros with "
            f"{_to_int(row.get('clicks'))} clicks, {_to_int(row.get('impressions'))} impressions, "
            f"and {_to_float(row.get('conversions')):.6f} conversions."
        )
        findings.append(
            _finding(
                finding_id=f"{category}:{idx}:{entity_name or scope}",
                level=level,
                category=category,
                scope=scope,
                entity_refs=[
                    _entity_ref(
                        entity_type=entity_type,
                        resource_name=str(
                            row.get("campaign_resource_name")
                            or row.get("ad_group_resource_name")
                            or row.get("url")
                            or entity_name
                            or ""
                        ).strip()
                        or None,
                        name=entity_name,
                    )
                ],
                evidence={
                    "impressions": _to_int(row.get("impressions")),
                    "clicks": _to_int(row.get("clicks")),
                    "cost_micros": _to_int(row.get("cost_micros")),
                    "conversions": round(_to_float(row.get("conversions")), 6),
                    "conversions_value": round(_to_float(row.get("conversions_value")), 6),
                },
                explanation=explanation,
                recommended_next_step=next_step,
                requires_human_review=requires_human_review,
            )
        )
    return findings


def _tracking_risk_findings(
    *,
    table_paths: dict[str, Path],
    conversion_actions_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    path = table_paths.get("ad_daily_metrics")
    if path is None:
        return []

    totals = _totals_from_ad_daily_metrics(path).get("totals") or {}
    clicks = _to_int(totals.get("clicks"))
    cost_micros = _to_int(totals.get("cost_micros"))
    conversions = _to_float(totals.get("conversions"))
    has_enough_activity = clicks >= TRACKING_RISK_MIN_CLICKS or cost_micros >= TRACKING_RISK_MIN_COST_MICROS
    if not has_enough_activity or conversions > 0:
        return []

    primary_actions = 0
    for row in conversion_actions_rows:
        conversion_action = row.get("conversion_action")
        if not isinstance(conversion_action, dict):
            continue
        if str(conversion_action.get("status") or "").strip() != "ENABLED":
            continue
        if not bool(conversion_action.get("primary_for_goal")):
            continue
        if not bool(conversion_action.get("include_in_conversions_metric")):
            continue
        primary_actions += 1

    if primary_actions > 0:
        return []

    return [
        _finding(
            finding_id="tracking_risk:account",
            level="critical",
            category="tracking_risk",
            scope="account",
            entity_refs=[_entity_ref(entity_type="account")],
            evidence={
                "clicks": clicks,
                "cost_micros": cost_micros,
                "conversions": round(conversions, 6),
                "active_primary_conversion_actions": primary_actions,
            },
            explanation=(
                "The pack shows meaningful spend or clicks with zero conversions, and the exported conversion-action setup "
                "does not show an enabled primary conversion action counted in the conversions metric."
            ),
            recommended_next_step="Review conversion actions and primary-goal setup before trusting zero-conversion performance reads.",
            requires_human_review=False,
        )
    ]


def _recommendation_review_findings(
    *,
    recommendations_rows: list[dict[str, Any]],
    customer_overview_rows: list[dict[str, Any]],
    campaign_inventory_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    active_rows = [
        row
        for row in recommendations_rows
        if not bool(_get(row, "recommendation", "dismissed", default=False))
    ]
    if not active_rows:
        return []

    recommendation_types = Counter(
        str(_get_any(row, ("recommendation", "type"), ("recommendation", "type_"), default="UNKNOWN") or "UNKNOWN")
        for row in active_rows
    )
    customer = customer_overview_rows[0]["customer"] if customer_overview_rows and isinstance(customer_overview_rows[0].get("customer"), dict) else {}
    customer_optimization_score = _to_float(customer.get("optimization_score"), default=-1.0)
    low_score_campaigns = []
    for row in campaign_inventory_rows:
        campaign = row.get("campaign")
        if not isinstance(campaign, dict):
            continue
        score = _to_float(campaign.get("optimization_score"), default=-1.0)
        if score >= 0.0 and score < LOW_OPTIMIZATION_SCORE:
            low_score_campaigns.append(
                {
                    "campaign_name": campaign.get("name"),
                    "campaign_resource_name": campaign.get("resource_name"),
                    "optimization_score": score,
                }
            )

    level = "high" if customer_optimization_score >= 0.0 and customer_optimization_score < LOW_OPTIMIZATION_SCORE else "medium"
    return [
        _finding(
            finding_id="recommendation_review:account",
            level=level,
            category="recommendation_review",
            scope="account",
            entity_refs=[
                _entity_ref(
                    entity_type="account",
                    resource_name=str(customer.get("resource_name") or "").strip() or None,
                    entity_id=str(customer.get("id") or "").strip() or None,
                    name=str(customer.get("descriptive_name") or "").strip() or None,
                )
            ],
            evidence={
                "customer_optimization_score": customer.get("optimization_score"),
                "customer_optimization_score_weight": customer.get("optimization_score_weight"),
                "recommendation_count": len(active_rows),
                "recommendation_type_counts": dict(sorted(recommendation_types.items())),
                "campaigns_below_optimization_score_threshold": low_score_campaigns,
            },
            explanation=(
                "The pack includes active Google Ads recommendations. Review them as evidence only; do not auto-apply them. "
                f"Active recommendation count={len(active_rows)}."
            ),
            recommended_next_step="Review recommendation types and optimization-score context, then build a no-apply plan for anything worth testing.",
            requires_human_review=True,
        )
    ]


def _sort_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER.get(str(item.get("level") or "low"), 99),
            str(item.get("category") or ""),
            str(item.get("id") or ""),
        ),
    )


def _build_actions(findings: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    actions = {
        "read_only_next_steps": [],
        "plan_first_write_candidates": [],
        "human_review_required": [],
    }
    for finding in findings:
        action = {
            "finding_id": finding.get("id"),
            "level": finding.get("level"),
            "category": finding.get("category"),
            "scope": finding.get("scope"),
            "recommended_next_step": finding.get("recommended_next_step"),
        }
        if bool(finding.get("requires_human_review")):
            actions["human_review_required"].append(action)
        elif str(finding.get("category") or "") in PLAN_FIRST_CATEGORIES:
            actions["plan_first_write_candidates"].append(action)
        else:
            actions["read_only_next_steps"].append(action)
    return actions


def run_snapshot_analyze_diagnose(a: DiagnoseArgs) -> dict[str, Any]:
    pack_dir = a.pack_dir.expanduser().resolve()
    manifest_path = pack_dir / "manifest.json"
    manifest_obj = _read_json(manifest_path)
    if not isinstance(manifest_obj, dict):
        raise ValidationError("manifest.json must be a JSON object")

    table_paths = _table_paths_from_manifest(pack_dir, manifest_obj)
    data_quality = _data_quality(manifest_obj, table_paths)

    expected_tables = {
        "customer_overview",
        "campaign_inventory",
        "campaign_settings",
        "campaign_budgets",
        "campaign_pressure_daily",
        "ad_group_inventory",
        "ad_group_ads",
        "ad_daily_metrics",
        "keyword_daily_metrics",
        "keyword_quality_snapshot",
        "search_terms_daily",
        "conversion_actions",
        "recommendations",
        "rsa_asset_performance",
        "landing_pages_daily",
        "placements_daily",
        "ad_daily_metrics_by_device",
        "ad_daily_metrics_by_network",
        "ad_daily_metrics_by_hour",
        "ad_daily_conversions_by_action",
    }
    tables_used = sorted(expected_tables & set(table_paths))
    tables_missing = sorted(expected_tables - set(table_paths))

    campaign_inventory_rows = _load_rows(table_paths, "campaign_inventory")
    ad_group_inventory_rows = _load_rows(table_paths, "ad_group_inventory")
    ad_group_ads_rows = _load_rows(table_paths, "ad_group_ads")
    ad_daily_metrics_rows = _load_rows(table_paths, "ad_daily_metrics")
    customer_overview_rows = _load_rows(table_paths, "customer_overview")
    conversion_actions_rows = _load_rows(table_paths, "conversion_actions")
    recommendations_rows = _load_rows(table_paths, "recommendations")

    campaign_index = _campaign_index(campaign_inventory_rows)
    ad_group_index = _ad_group_index(ad_group_inventory_rows)
    merged_ad_rows = _merged_ad_rows(
        ad_group_ads_rows=ad_group_ads_rows,
        ad_daily_metrics_rows=ad_daily_metrics_rows,
    )
    ad_index = _ad_index(merged_ad_rows)
    _ = ad_group_index

    findings: list[dict[str, Any]] = []
    findings.extend(_pressure_findings(table_paths=table_paths, campaign_index=campaign_index))
    findings.extend(_quality_findings(table_paths))
    findings.extend(_rsa_findings(table_paths=table_paths, ad_rows=list(ad_index.values())))

    if "search_terms_daily" in table_paths:
        findings.extend(
            _candidate_findings(
                category="search_term_cleanup",
                scope="search_term",
                rows=_candidate_negative_keywords(
                    table_paths["search_terms_daily"],
                    top_n=TOP_CANDIDATE_FINDINGS,
                    min_cost_micros=NEGATIVE_MIN_COST_MICROS,
                    min_clicks=NEGATIVE_MIN_CLICKS,
                    min_impressions=NEGATIVE_MIN_IMPRESSIONS,
                ),
                next_step="Review this search term as a negative-keyword candidate before blocking it live.",
                requires_human_review=True,
            )
        )

    if "keyword_daily_metrics" in table_paths:
        findings.extend(
            _candidate_findings(
                category="keyword_pause_candidate",
                scope="keyword",
                rows=_keyword_candidates_to_pause(
                    table_paths["keyword_daily_metrics"],
                    top_n=TOP_CANDIDATE_FINDINGS,
                    min_cost_micros=NEGATIVE_MIN_COST_MICROS,
                    min_clicks=NEGATIVE_MIN_CLICKS,
                ),
                next_step="Review this keyword as a pause candidate before making any live changes.",
                requires_human_review=True,
            )
        )

    if "landing_pages_daily" in table_paths:
        findings.extend(
            _candidate_findings(
                category="landing_page_review",
                scope="landing_page",
                rows=_url_waste_candidates(
                    table_paths["landing_pages_daily"],
                    url_key=("landing_page_view", "unexpanded_final_url"),
                    top_n=TOP_CANDIDATE_FINDINGS,
                    min_cost_micros=NEGATIVE_MIN_COST_MICROS,
                ),
                next_step="Review whether this landing page matches the keyword promise and conversion goal before editing traffic or copy.",
                requires_human_review=False,
            )
        )

    if "placements_daily" in table_paths:
        findings.extend(
            _candidate_findings(
                category="placement_review",
                scope="placement",
                rows=_url_waste_candidates(
                    table_paths["placements_daily"],
                    url_key=("detail_placement_view", "placement"),
                    top_n=TOP_CANDIDATE_FINDINGS,
                    min_cost_micros=NEGATIVE_MIN_COST_MICROS,
                ),
                next_step="Review whether this placement should stay live before excluding it.",
                requires_human_review=True,
            )
        )

    findings.extend(
        _tracking_risk_findings(
            table_paths=table_paths,
            conversion_actions_rows=conversion_actions_rows,
        )
    )
    findings.extend(
        _recommendation_review_findings(
            recommendations_rows=recommendations_rows,
            customer_overview_rows=customer_overview_rows,
            campaign_inventory_rows=campaign_inventory_rows,
        )
    )

    findings = _sort_findings(findings)
    actions = _build_actions(findings)
    level_counts = Counter(str(item.get("level") or "low") for item in findings)
    category_counts = Counter(str(item.get("category") or "unknown") for item in findings)

    notes = [
        "This diagnose report is offline-only and reads only the exported pack.",
        "Recommendation findings are review-only. Do not auto-apply Google Ads recommendations from this output.",
    ]
    if not findings:
        notes.append("No diagnosis heuristics crossed the built-in thresholds on the exported data.")
    if tables_missing:
        notes.append(
            "Some finding families were skipped because these tables were missing: " + ", ".join(tables_missing) + "."
        )

    return {
        "ok": True,
        "pack_dir": str(pack_dir),
        "summary": {
            "preset": manifest_obj.get("preset"),
            "customer_id": manifest_obj.get("customer_id"),
            "since": manifest_obj.get("since"),
            "until": manifest_obj.get("until"),
            "findings_total": len(findings),
            "findings_by_level": dict(sorted(level_counts.items())),
            "findings_by_category": dict(sorted(category_counts.items())),
        },
        "data_quality": data_quality,
        "tables_used": tables_used,
        "tables_missing": tables_missing,
        "findings": findings,
        "actions": actions,
        "notes": notes,
    }
