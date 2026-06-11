from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class CreativeAnatomyWriteResult:
    row_count: int
    warnings: list[str]


def _get(d: dict[str, Any], *path: str) -> Any:
    cur: Any = d
    for k in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def _as_str_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        out: list[str] = []
        for x in v:
            if isinstance(x, str) and x.strip():
                out.append(x)
        return out
    return []


def _extract_text_assets(items: Any) -> list[str]:
    if not isinstance(items, list):
        return []
    out: list[str] = []
    for it in items:
        if isinstance(it, dict):
            t = it.get("text")
            if isinstance(t, str) and t.strip():
                out.append(t)
    return out


def _extract_creative_fields(ad: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    headlines: list[str] = []
    descriptions: list[str] = []
    final_urls: list[str] = _as_str_list(ad.get("final_urls"))

    rsa = ad.get("responsive_search_ad")
    if isinstance(rsa, dict):
        headlines += _extract_text_assets(rsa.get("headlines"))
        descriptions += _extract_text_assets(rsa.get("descriptions"))

    eta = ad.get("expanded_text_ad")
    if isinstance(eta, dict):
        for k in ["headline_part1", "headline_part2", "headline_part3"]:
            v = eta.get(k)
            if isinstance(v, str) and v.strip():
                headlines.append(v)
        for k in ["description", "description2"]:
            v = eta.get(k)
            if isinstance(v, str) and v.strip():
                descriptions.append(v)

    rda = ad.get("responsive_display_ad")
    if isinstance(rda, dict):
        headlines += _extract_text_assets(rda.get("headlines"))
        descriptions += _extract_text_assets(rda.get("descriptions"))
        lh = rda.get("long_headline")
        if isinstance(lh, dict):
            t = lh.get("text")
            if isinstance(t, str) and t.strip():
                headlines.append(t)

    return headlines, descriptions, final_urls


def _build_asset_refs(*, headlines: list[str], descriptions: list[str], final_urls: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for h in headlines:
        if isinstance(h, str) and h.strip():
            out.append({"kind": "headline", "text": h})
    for d in descriptions:
        if isinstance(d, str) and d.strip():
            out.append({"kind": "description", "text": d})
    for u in final_urls:
        if isinstance(u, str) and u.strip():
            out.append({"kind": "final_url", "url": u})
    return out


def iter_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield i, obj


def _asset_text(asset: dict[str, Any]) -> str | None:
    ta = asset.get("text_asset")
    if isinstance(ta, dict):
        t = ta.get("text")
        if isinstance(t, str) and t.strip():
            return t.strip()
    return None


def _asset_image_url(asset: dict[str, Any]) -> str | None:
    ia = asset.get("image_asset")
    if not isinstance(ia, dict):
        return None
    fs = ia.get("full_size")
    if not isinstance(fs, dict):
        return None
    u = fs.get("url")
    if isinstance(u, str) and u.strip():
        return u.strip()
    return None


def _asset_youtube_id(asset: dict[str, Any]) -> str | None:
    ya = asset.get("youtube_video_asset")
    if isinstance(ya, dict):
        vid = ya.get("youtube_video_id")
        if isinstance(vid, str) and vid.strip():
            return vid.strip()
    return None


def _load_assets_by_resource_name(tables_dir: Path) -> dict[str, dict[str, Any]]:
    src = tables_dir / "assets.jsonl"
    if not src.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for _, row in iter_jsonl(src):
        a = row.get("asset")
        if not isinstance(a, dict):
            continue
        rn = a.get("resource_name")
        if not isinstance(rn, str) or not rn.strip():
            continue
        out[rn.strip()] = a
    return out


def _load_asset_group_assets(tables_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """
    Map asset_group.resource_name -> list of asset references.
    """
    src = tables_dir / "asset_group_assets.jsonl"
    if not src.exists():
        return {}
    out: dict[str, list[dict[str, Any]]] = {}
    for _, row in iter_jsonl(src):
        ag = row.get("asset_group")
        if not isinstance(ag, dict):
            continue
        ag_rn = ag.get("resource_name")
        if not isinstance(ag_rn, str) or not ag_rn.strip():
            continue
        asset = row.get("asset")
        if not isinstance(asset, dict):
            continue
        asset_rn = asset.get("resource_name")
        if not isinstance(asset_rn, str) or not asset_rn.strip():
            continue
        aga = row.get("asset_group_asset")
        field_type = None
        if isinstance(aga, dict):
            ft = aga.get("field_type")
            if isinstance(ft, str) and ft.strip():
                field_type = ft.strip()
        out.setdefault(ag_rn.strip(), []).append(
            {"asset_resource_name": asset_rn.strip(), "field_type": field_type}
        )
    return out


def write_creative_anatomy_table(*, pack_dir: Path) -> CreativeAnatomyWriteResult:
    warnings: list[str] = []
    tables_dir = pack_dir / "tables"
    src = tables_dir / "ad_group_ads.jsonl"
    asset_groups_src = tables_dir / "asset_groups.jsonl"
    out_path = tables_dir / "creative_anatomy.jsonl"

    assets_by_rn = _load_assets_by_resource_name(tables_dir)
    asset_group_assets = _load_asset_group_assets(tables_dir)

    if not src.exists() and not asset_groups_src.exists():
        tables_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text("", encoding="utf-8")
        return CreativeAnatomyWriteResult(
            row_count=0, warnings=["Missing source tables: tables/ad_group_ads.jsonl and tables/asset_groups.jsonl"]
        )

    row_count = 0
    wrote_any_ad_rows = False
    wrote_any_asset_group_rows = False
    with out_path.open("w", encoding="utf-8") as out:
        if src.exists():
            for line_no, row in iter_jsonl(src):
                ag = row.get("ad_group_ad")
                if not isinstance(ag, dict):
                    continue
                ad = ag.get("ad")
                if not isinstance(ad, dict):
                    continue

                customer_id = _get(row, "customer", "id")
                campaign_id = _get(row, "campaign", "id")
                campaign_rn = _get(row, "campaign", "resource_name")
                ad_group_id = _get(row, "ad_group", "id")
                ad_group_rn = _get(row, "ad_group", "resource_name")
                ag_rn = ag.get("resource_name")
                ad_id = _get(ag, "ad", "id")

                ad_type = ad.get("type")
                headlines, descriptions, final_urls = _extract_creative_fields(ad)
                asset_refs = _build_asset_refs(headlines=headlines, descriptions=descriptions, final_urls=final_urls)

                creative_id = None
                if isinstance(ag_rn, str) and ag_rn.strip():
                    creative_id = ag_rn
                elif isinstance(ad_id, (int, str)) and str(ad_id).strip():
                    creative_id = str(ad_id)

                if not creative_id:
                    continue

                out_row: dict[str, Any] = {
                    "creative_id": creative_id,
                    "customer": {"id": str(customer_id)} if customer_id is not None else {},
                    "campaign": {
                        "id": str(campaign_id) if campaign_id is not None else None,
                        "resource_name": str(campaign_rn) if campaign_rn is not None else None,
                    },
                    "ad_group": {
                        "id": str(ad_group_id) if ad_group_id is not None else None,
                        "resource_name": str(ad_group_rn) if ad_group_rn is not None else None,
                    },
                    "ad_group_ad": {
                        "resource_name": str(ag_rn) if ag_rn is not None else None,
                        "ad": {
                            "id": str(ad_id) if ad_id is not None else None,
                            "type": str(ad_type) if ad_type is not None else None,
                        },
                    },
                    "headlines": headlines,
                    "descriptions": descriptions,
                    "final_urls": final_urls,
                    "asset_group": {},
                    "asset_refs": asset_refs,
                    "source_refs": [
                        {
                            "table": "ad_group_ads",
                            "line": line_no,
                            "ad_group_ad_resource_name": str(ag_rn) if ag_rn is not None else None,
                            "ad_id": str(ad_id) if ad_id is not None else None,
                        }
                    ],
                }
                out.write(json.dumps(out_row, ensure_ascii=False) + "\n")
                row_count += 1
                wrote_any_ad_rows = True

        if asset_groups_src.exists():
            for line_no, row in iter_jsonl(asset_groups_src):
                ag = row.get("asset_group")
                if not isinstance(ag, dict):
                    continue

                customer_id = _get(row, "customer", "id")
                campaign_id = _get(row, "campaign", "id")
                campaign_rn = _get(row, "campaign", "resource_name")
                asset_group_id = ag.get("id")
                asset_group_rn = ag.get("resource_name")

                creative_id = None
                if isinstance(asset_group_rn, str) and asset_group_rn.strip():
                    creative_id = asset_group_rn
                elif isinstance(asset_group_id, (int, str)) and str(asset_group_id).strip():
                    creative_id = f"asset_group:{asset_group_id}"

                if not creative_id:
                    continue

                refs: list[dict[str, Any]] = []
                for ref in asset_group_assets.get(str(asset_group_rn or "").strip(), []):
                    arn = str(ref.get("asset_resource_name") or "").strip()
                    if not arn:
                        continue
                    asset = assets_by_rn.get(arn, {})
                    a_type = asset.get("type") if isinstance(asset, dict) else None
                    refs.append(
                        {
                            "kind": "asset",
                            "asset_resource_name": arn,
                            "asset_type": str(a_type) if a_type is not None else None,
                            "field_type": ref.get("field_type"),
                            "text": _asset_text(asset) if isinstance(asset, dict) else None,
                            "image_url": _asset_image_url(asset) if isinstance(asset, dict) else None,
                            "youtube_video_id": _asset_youtube_id(asset) if isinstance(asset, dict) else None,
                        }
                    )

                out_row = {
                    "creative_id": str(creative_id),
                    "customer": {"id": str(customer_id)} if customer_id is not None else {},
                    "campaign": {
                        "id": str(campaign_id) if campaign_id is not None else None,
                        "resource_name": str(campaign_rn) if campaign_rn is not None else None,
                    },
                    "ad_group": {},
                    "ad_group_ad": {"ad": {}},
                    "asset_group": {
                        "id": str(asset_group_id) if asset_group_id is not None else None,
                        "resource_name": str(asset_group_rn) if asset_group_rn is not None else None,
                    },
                    "headlines": [],
                    "descriptions": [],
                    "final_urls": [],
                    "asset_refs": refs,
                    "source_refs": [
                        {
                            "table": "asset_groups",
                            "line": line_no,
                            "asset_group_resource_name": str(asset_group_rn) if asset_group_rn is not None else None,
                            "asset_group_id": str(asset_group_id) if asset_group_id is not None else None,
                        }
                    ],
                }
                out.write(json.dumps(out_row, ensure_ascii=False) + "\n")
                row_count += 1
                wrote_any_asset_group_rows = True

    if row_count == 0:
        warnings.append("creative_anatomy produced 0 rows (no parseable ad_group_ads or asset_groups rows)")
    else:
        if src.exists() and not wrote_any_ad_rows:
            warnings.append("creative_anatomy produced 0 ad rows (no parseable ad_group_ads rows)")
        if asset_groups_src.exists() and not wrote_any_asset_group_rows:
            warnings.append("creative_anatomy produced 0 asset-group rows (no parseable asset_groups rows)")

    return CreativeAnatomyWriteResult(row_count=row_count, warnings=warnings)
