from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..api import PinterestApi, build_analytics_params, resolve_access_token


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _api(ctx: dict[str, Any]) -> PinterestApi:
    cfg = ctx["cfg"]
    return PinterestApi(
        base_url=cfg.base_url,
        http=ctx["http"],
        access_token=resolve_access_token(
            env_file=ctx["env_file"],
            env_access_token=cfg.access_token,
            env_refresh_token=cfg.refresh_token,
            app_id=cfg.app_id,
            app_secret=cfg.app_secret,
            base_url=cfg.base_url,
            http=ctx["http"],
        ),
    )


def cmd_audit_snapshot(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    out_dir = Path(str(args.out_dir)).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    ad_account_id = getattr(args, "ad_account_id", None)
    include_ads = bool(getattr(args, "include_ads", False))
    include_catalogs = bool(getattr(args, "include_catalogs", False))
    include_user_account = bool(getattr(args, "include_user_account", False))
    include_business_access = bool(getattr(args, "include_business_access", False))
    include_resources = bool(getattr(args, "include_resources", False))
    include_conversions = bool(getattr(args, "include_conversions", False))
    business_id = getattr(args, "business_id", None)
    export_limit = int(getattr(args, "export_limit", 50000))
    export_page_size = int(getattr(args, "export_page_size", 100))

    started_at_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    meta = {
        "tool": "pinterest-api-tool",
        "started_at_utc": started_at_utc,
        "base_url": ctx["cfg"].base_url,
    }
    _write_json(out_dir / "meta.json", meta)

    fatal_errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    files: dict[str, str] = {"meta": str(out_dir / "meta.json")}

    def export_list(
        *,
        stage: str,
        key: str,
        path: str,
        params: dict[str, Any] | None,
        record_file: bool = True,
    ) -> list[dict[str, Any]] | None:
        try:
            items, bookmark, pages = api.list_all(
                path,
                params=params or {},
                limit=export_limit,
                page_size=export_page_size,
                bookmark=None,
            )
            payload = {
                "ok": True,
                "count": len(items),
                "pages": pages,
                "bookmark": bookmark,
                "items": items,
                "params": params or {},
            }
            p = out_dir / key
            _write_json(p, payload)
            if record_file:
                files[stage] = str(p)
            return items
        except Exception as e:  # noqa: BLE001
            warnings.append({"stage": stage, "error": str(e)})
            return None

    def export_get(
        *,
        stage: str,
        key: str,
        path: str,
        params: dict[str, Any] | None,
        record_file: bool = True,
    ) -> dict[str, Any] | None:
        try:
            data = api.get(path, params=params or None)
            payload = {"ok": True, "params": params or {}, "data": data}
            p = out_dir / key
            _write_json(p, payload)
            if record_file:
                files[stage] = str(p)
            return payload
        except Exception as e:  # noqa: BLE001
            warnings.append({"stage": stage, "error": str(e)})
            return None

    boards_items: list[dict[str, Any]] = []
    sections_by_board: dict[str, Any] = {}

    # Boards
    try:
        boards_params: dict[str, Any] = {}
        if ad_account_id:
            boards_params["ad_account_id"] = str(ad_account_id).strip()
        boards, boards_bookmark, boards_pages = api.list_all(
            "/boards",
            params=boards_params,
            limit=int(args.boards_limit),
            page_size=int(args.page_size),
            bookmark=None,
        )
        boards_items = [b for b in boards if isinstance(b, dict)]
        boards_payload = {
            "ok": True,
            "count": len(boards),
            "pages": boards_pages,
            "bookmark": boards_bookmark,
            "items": boards,
        }
        p = out_dir / "boards.json"
        _write_json(p, boards_payload)
        files["boards"] = str(p)
    except Exception as e:  # noqa: BLE001
        fatal_errors.append({"stage": "boards", "error": str(e)})

    # Board sections (best-effort; continue on per-board errors)
    try:
        for b in boards_items:
            board_id = str(b.get("id") or "").strip()
            if not board_id:
                continue
            try:
                sec_params: dict[str, Any] = {}
                if ad_account_id:
                    sec_params["ad_account_id"] = str(ad_account_id).strip()
                secs, sec_bookmark, sec_pages = api.list_all(
                    f"/boards/{board_id}/sections",
                    params=sec_params,
                    limit=10000,
                    page_size=int(args.page_size),
                    bookmark=None,
                )
                sections_by_board[board_id] = {
                    "ok": True,
                    "count": len(secs),
                    "pages": sec_pages,
                    "bookmark": sec_bookmark,
                    "items": secs,
                }
            except Exception as e:  # noqa: BLE001
                sections_by_board[board_id] = {"ok": False, "error": str(e)}

        p = out_dir / "board_sections_by_board.json"
        _write_json(p, {"ok": True, "boards": sections_by_board})
        files["board_sections_by_board"] = str(p)
    except Exception as e:  # noqa: BLE001
        warnings.append({"stage": "board_sections_by_board", "error": str(e)})

    # Boards summary (derived; no extra API calls)
    try:
        summary_items: list[dict[str, Any]] = []
        for b in boards_items:
            bid = str(b.get("id") or "").strip()
            if not bid:
                continue
            sec = sections_by_board.get(bid) or {}
            section_count = None
            if isinstance(sec, dict) and sec.get("ok") is True:
                section_count = sec.get("count")
            summary_items.append(
                {
                    "id": bid,
                    "name": b.get("name"),
                    "privacy": b.get("privacy"),
                    "section_count": section_count,
                }
            )
        summary_items.sort(key=lambda x: (-(x["section_count"] or 0), (x.get("name") or "")))
        p = out_dir / "boards_summary.json"
        _write_json(p, {"ok": True, "count": len(summary_items), "items": summary_items})
        files["boards_summary"] = str(p)
    except Exception as e:  # noqa: BLE001
        warnings.append({"stage": "boards_summary", "error": str(e)})

    # Pins
    try:
        pins_params: dict[str, Any] = {}
        if ad_account_id:
            pins_params["ad_account_id"] = str(ad_account_id).strip()
        pins, pins_bookmark, pins_pages = api.list_all(
            "/pins",
            params=pins_params,
            limit=int(args.pins_limit),
            page_size=int(args.page_size),
            bookmark=None,
        )
        pins_payload = {
            "ok": True,
            "count": len(pins),
            "pages": pins_pages,
            "bookmark": pins_bookmark,
            "items": pins,
        }
        p = out_dir / "pins.json"
        _write_json(p, pins_payload)
        files["pins"] = str(p)
    except Exception as e:  # noqa: BLE001
        fatal_errors.append({"stage": "pins", "error": str(e)})

    # Analytics (optional; common to fail if scopes/tier missing)
    if not bool(args.skip_analytics):
        analytics_default_metrics = ["IMPRESSION"]
        for name, path in [
            ("analytics_user", "/user_account/analytics"),
            ("analytics_top_pins", "/user_account/analytics/top_pins"),
            ("analytics_top_video_pins", "/user_account/analytics/top_video_pins"),
        ]:
            try:
                params = build_analytics_params(
                    start_date=None,
                    end_date=None,
                    metrics=None,
                    extra_params=None,
                    default_days=90,
                    default_metrics=analytics_default_metrics,
                )
                if path.endswith("/top_pins") or path.endswith("/top_video_pins"):
                    params["sort_by"] = "IMPRESSION"
                if ad_account_id:
                    params["ad_account_id"] = str(ad_account_id).strip()
                data = api.get(path, params=params)
                p = out_dir / f"{name}.json"
                _write_json(p, {"ok": True, "params": params, "data": data})
                files[name] = str(p)
            except Exception as e:  # noqa: BLE001
                warnings.append({"stage": name, "error": str(e)})

    # User account discovery (optional; warning-only)
    if include_user_account:
        export_list(
            stage="user_account_businesses",
            key="user_account/businesses.json",
            path="/user_account/businesses",
            params={},
        )
        export_list(
            stage="user_account_followers",
            key="user_account/followers.json",
            path="/user_account/followers",
            params={},
        )
        export_list(
            stage="user_account_following",
            key="user_account/following.json",
            path="/user_account/following",
            params={},
        )
        export_list(
            stage="user_account_following_boards",
            key="user_account/following_boards.json",
            path="/user_account/following/boards",
            params={},
        )
        export_list(
            stage="user_account_websites",
            key="user_account/websites.json",
            path="/user_account/websites",
            params={},
        )
        export_get(
            stage="user_account_websites_verification",
            key="user_account/websites_verification.json",
            path="/user_account/websites/verification",
            params={},
        )

    # Business Access exports (optional; warning-only)
    if include_business_access:
        if not business_id or not str(business_id).strip():
            warnings.append(
                {
                    "stage": "business_access",
                    "error": "--include-business-access requires --business-id (skipping business exports; do not guess a business)",
                }
            )
        else:
            bid = str(business_id).strip()
            assets = export_list(
                stage="business_access_assets",
                key="business/assets.json",
                path=f"/businesses/{bid}/assets",
                params={},
            ) or []
            members = export_list(
                stage="business_access_members",
                key="business/members.json",
                path=f"/businesses/{bid}/members",
                params={},
            ) or []
            partners = export_list(
                stage="business_access_partners",
                key="business/partners.json",
                path=f"/businesses/{bid}/partners",
                params={},
            ) or []

            asset_members_dir = out_dir / "business" / "asset_members"
            asset_partners_dir = out_dir / "business" / "asset_partners"
            member_assets_dir = out_dir / "business" / "member_assets"
            partner_assets_dir = out_dir / "business" / "partner_assets"
            files["business_asset_members_dir"] = str(asset_members_dir)
            files["business_asset_partners_dir"] = str(asset_partners_dir)
            files["business_member_assets_dir"] = str(member_assets_dir)
            files["business_partner_assets_dir"] = str(partner_assets_dir)

            for asset in assets:
                asset_id = str((asset or {}).get("asset_id") or (asset or {}).get("id") or "").strip()
                if not asset_id:
                    continue
                export_list(
                    stage=f"business_access_asset_members_{asset_id}",
                    key=f"business/asset_members/{asset_id}.json",
                    path=f"/businesses/{bid}/assets/{asset_id}/members",
                    params={},
                    record_file=False,
                )
                export_list(
                    stage=f"business_access_asset_partners_{asset_id}",
                    key=f"business/asset_partners/{asset_id}.json",
                    path=f"/businesses/{bid}/assets/{asset_id}/partners",
                    params={},
                    record_file=False,
                )

            for member in members:
                member_id = str((member or {}).get("member_id") or (member or {}).get("id") or "").strip()
                if not member_id:
                    continue
                export_list(
                    stage=f"business_access_member_assets_{member_id}",
                    key=f"business/member_assets/{member_id}.json",
                    path=f"/businesses/{bid}/members/{member_id}/assets",
                    params={},
                    record_file=False,
                )

            for partner in partners:
                partner_id = str((partner or {}).get("partner_id") or (partner or {}).get("id") or "").strip()
                if not partner_id:
                    continue
                export_list(
                    stage=f"business_access_partner_assets_{partner_id}",
                    key=f"business/partner_assets/{partner_id}.json",
                    path=f"/businesses/{bid}/partners/{partner_id}/assets",
                    params={},
                    record_file=False,
                )

    # Resources / lookup exports (optional; warning-only)
    if include_resources:
        export_get(
            stage="resources_ad_account_countries",
            key="resources/ad_account_countries.json",
            path="/resources/ad_account_countries",
            params={},
        )
        export_get(
            stage="resources_delivery_metrics",
            key="resources/delivery_metrics.json",
            path="/resources/delivery_metrics",
            params={},
        )
        export_get(
            stage="resources_metrics_ready_state",
            key="resources/metrics_ready_state.json",
            path="/resources/metrics_ready_state",
            params={},
        )

    # Conversions exports (optional; warning-only)
    if include_conversions:
        if not ad_account_id or not str(ad_account_id).strip():
            warnings.append(
                {
                    "stage": "conversions",
                    "error": "--include-conversions requires --ad-account-id (skipping conversion exports; do not guess an account)",
                }
            )
        else:
            aid = str(ad_account_id).strip()
            export_list(
                stage="conversions_tags",
                key="conversions/tags.json",
                path=f"/ad_accounts/{aid}/conversion_tags",
                params={},
            )
            export_get(
                stage="conversions_page_visit",
                key="conversions/page_visit.json",
                path=f"/ad_accounts/{aid}/conversion_tags/page_visit",
                params={},
            )
            export_get(
                stage="conversions_ocpm_eligible",
                key="conversions/ocpm_eligible.json",
                path=f"/ad_accounts/{aid}/conversion_tags/ocpm_eligible",
                params={},
            )
            export_get(
                stage="conversions_eqs",
                key="conversions/eqs.json",
                path=f"/ad_accounts/{aid}/conversion_eqs",
                params={},
            )

    # Ads exports (optional; warning-only)
    if include_ads:
        if not ad_account_id or not str(ad_account_id).strip():
            warnings.append(
                {
                    "stage": "ads",
                    "error": "--include-ads requires --ad-account-id (skipping ads exports; do not guess an account)",
                }
            )
        else:
            aid = str(ad_account_id).strip()
            export_list(stage="ads_ad_accounts", key="ads/ad_accounts.json", path="/ad_accounts", params={})
            export_list(
                stage="ads_campaigns",
                key="ads/campaigns.json",
                path=f"/ad_accounts/{aid}/campaigns",
                params={},
            )
            export_list(
                stage="ads_ad_groups",
                key="ads/ad_groups.json",
                path=f"/ad_accounts/{aid}/ad_groups",
                params={},
            )
            export_list(
                stage="ads_ads",
                key="ads/ads.json",
                path=f"/ad_accounts/{aid}/ads",
                params={},
            )
            ads_analytics_params = build_analytics_params(
                start_date=None,
                end_date=None,
                metrics=None,
                extra_params=None,
                default_days=30,
                default_metrics=None,
            )
            export_get(
                stage="ads_ad_account_analytics",
                key="ads/analytics/ad_account.json",
                path=f"/ad_accounts/{aid}/analytics",
                params=ads_analytics_params,
            )
            export_get(
                stage="ads_campaigns_analytics",
                key="ads/analytics/campaigns.json",
                path=f"/ad_accounts/{aid}/campaigns/analytics",
                params=ads_analytics_params,
            )
            export_get(
                stage="ads_ad_groups_analytics",
                key="ads/analytics/ad_groups.json",
                path=f"/ad_accounts/{aid}/ad_groups/analytics",
                params=ads_analytics_params,
            )
            export_get(
                stage="ads_ads_analytics",
                key="ads/analytics/ads.json",
                path=f"/ad_accounts/{aid}/ads/analytics",
                params=ads_analytics_params,
            )
            export_get(
                stage="ads_pins_analytics",
                key="ads/analytics/pins.json",
                path=f"/ad_accounts/{aid}/pins/analytics",
                params=ads_analytics_params,
            )
            export_get(
                stage="ads_targeting_analytics_ad_account",
                key="ads/targeting_analytics/ad_account.json",
                path=f"/ad_accounts/{aid}/targeting_analytics",
                params=ads_analytics_params,
            )
            export_get(
                stage="ads_targeting_analytics_campaigns",
                key="ads/targeting_analytics/campaigns.json",
                path=f"/ad_accounts/{aid}/campaigns/targeting_analytics",
                params=ads_analytics_params,
            )
            export_get(
                stage="ads_targeting_analytics_ad_groups",
                key="ads/targeting_analytics/ad_groups.json",
                path=f"/ad_accounts/{aid}/ad_groups/targeting_analytics",
                params=ads_analytics_params,
            )
            export_get(
                stage="ads_targeting_analytics_ads",
                key="ads/targeting_analytics/ads.json",
                path=f"/ad_accounts/{aid}/ads/targeting_analytics",
                params=ads_analytics_params,
            )
            export_get(
                stage="ads_audience_insights",
                key="ads/audience_insights.json",
                path=f"/ad_accounts/{aid}/audience_insights",
                params={},
            )
            export_get(
                stage="ads_insights_audiences",
                key="ads/insights_audiences.json",
                path=f"/ad_accounts/{aid}/insights/audiences",
                params={},
            )

    # Catalogs exports (optional; warning-only)
    if include_catalogs:
        if not ad_account_id or not str(ad_account_id).strip():
            warnings.append(
                {
                    "stage": "catalogs",
                    "error": "--include-catalogs requires --ad-account-id (skipping catalogs exports; do not guess an account)",
                }
            )
        else:
            aid = str(ad_account_id).strip()
            catalogs = export_list(
                stage="catalogs_catalogs",
                key="catalogs/catalogs.json",
                path="/catalogs",
                params={"ad_account_id": aid},
            )
            feeds = export_list(
                stage="catalogs_feeds",
                key="catalogs/feeds.json",
                path="/catalogs/feeds",
                params={"ad_account_id": aid},
            )
            product_groups = export_list(
                stage="catalogs_product_groups",
                key="catalogs/product_groups.json",
                path="/catalogs/product_groups",
                params={"ad_account_id": aid},
            )
            _ = catalogs
            export_list(
                stage="catalogs_reports",
                key="catalogs/reports.json",
                path="/catalogs/reports",
                params={"ad_account_id": aid},
            )
            export_get(
                stage="catalogs_reports_stats",
                key="catalogs/reports_stats.json",
                path="/catalogs/reports/stats",
                params={"ad_account_id": aid},
            )

            if feeds:
                feed_results_dir = out_dir / "catalogs" / "feed_processing_results"
                item_issues_dir = out_dir / "catalogs" / "item_issues"
                files["catalogs_feed_processing_results_dir"] = str(feed_results_dir)
                files["catalogs_item_issues_dir"] = str(item_issues_dir)
                for feed in feeds:
                    feed_id = str(feed.get("id") or "").strip()
                    if not feed_id:
                        continue
                    results = export_list(
                        stage=f"catalogs_feed_processing_results_{feed_id}",
                        key=f"catalogs/feed_processing_results/{feed_id}.json",
                        path=f"/catalogs/feeds/{feed_id}/processing_results",
                        params={"ad_account_id": aid},
                        record_file=False,
                    ) or []
                    for pr in results:
                        processing_result_id = str(pr.get("id") or "").strip()
                        if not processing_result_id:
                            continue
                        export_list(
                            stage=f"catalogs_item_issues_{processing_result_id}",
                            key=f"catalogs/item_issues/{processing_result_id}.json",
                            path=f"/catalogs/processing_results/{processing_result_id}/item_issues",
                            params={"ad_account_id": aid},
                            record_file=False,
                        )

            if product_groups:
                product_group_products_dir = out_dir / "catalogs" / "product_group_products"
                files["catalogs_product_group_products_dir"] = str(product_group_products_dir)
                for pg in product_groups:
                    product_group_id = str(pg.get("id") or "").strip()
                    if not product_group_id:
                        continue
                    export_list(
                        stage=f"catalogs_product_group_products_{product_group_id}",
                        key=f"catalogs/product_group_products/{product_group_id}.json",
                        path=f"/catalogs/product_groups/{product_group_id}/products",
                        params={"ad_account_id": aid},
                        record_file=False,
                    )

    ok = len(fatal_errors) == 0
    out = {
        "ok": ok,
        "out_dir": str(out_dir),
        "files": files,
        "fatal_errors": fatal_errors,
        "warnings": warnings,
    }
    ctx["audit"].write(
        "audit.snapshot",
        {
            "ok": out["ok"],
            "out_dir": str(out_dir),
            "fatal_errors": len(fatal_errors),
            "warnings": len(warnings),
        },
    )
    ctx["out"].emit(out)
    return 0 if ok else 1
