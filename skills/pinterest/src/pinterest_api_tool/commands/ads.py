from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..api import PinterestApi, build_analytics_params, resolve_access_token
from ..write_framework import build_plan, build_receipt, require_write_allowed, write_operation


def _api(ctx: dict[str, Any]) -> PinterestApi:
    cfg = ctx["cfg"]
    access_token = "write-plan-or-refusal"
    if not bool(ctx.get("skip_auth_for_write_plan")):
        access_token = resolve_access_token(
            env_file=ctx["env_file"],
            env_access_token=cfg.access_token,
            env_refresh_token=cfg.refresh_token,
            app_id=cfg.app_id,
            app_secret=cfg.app_secret,
            base_url=cfg.base_url,
            http=ctx["http"],
        )
    return PinterestApi(
        base_url=cfg.base_url,
        http=ctx["http"],
        access_token=access_token,
    )


def _parse_kv_pairs(pairs: list[str] | None) -> dict[str, Any]:
    if not pairs:
        return {}
    out: dict[str, Any] = {}
    for raw in pairs:
        s = (raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise RuntimeError(f"Invalid --param (expected key=value): {raw}")
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            raise RuntimeError(f"Invalid --param (empty key): {raw}")
        if k in out:
            prev = out[k]
            if isinstance(prev, list):
                prev.append(v)
            else:
                out[k] = [prev, v]
        else:
            out[k] = v
    return out


def _parse_columns(metrics: list[str] | None) -> str | None:
    if not metrics:
        return None
    cleaned = [m.strip().upper() for m in metrics if (m or "").strip()]
    if not cleaned:
        return None
    return ",".join(cleaned)


def _ads_analytics_params(args: Any) -> dict[str, Any]:
    params = build_analytics_params(
        start_date=getattr(args, "start_date", None),
        end_date=getattr(args, "end_date", None),
        metrics=None,
        extra_params=getattr(args, "param", None),
        default_days=30,
        default_metrics=None,
    )
    cols = _parse_columns(getattr(args, "metric", None))
    if cols:
        params["columns"] = cols
    granularity = getattr(args, "granularity", None)
    if isinstance(granularity, str) and granularity.strip():
        params["granularity"] = granularity.strip().upper()
    return params


def cmd_ads_accounts_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    params = _parse_kv_pairs(args.param)
    items, bookmark, pages = api.list_all(
        "/ad_accounts",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {"ok": True, "count": len(items), "pages": pages, "bookmark": bookmark, "items": items}
    ctx["audit"].write("ads.accounts.list", {"count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_ads_accounts_get(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.id).strip()
    if not ad_account_id:
        raise RuntimeError("--id is required")
    params = _parse_kv_pairs(args.param)
    data = api.get(f"/ad_accounts/{ad_account_id}", params=params or None)
    out = {"ok": True, "ad_account": data}
    ctx["audit"].write("ads.accounts.get", {"ad_account_id": ad_account_id})
    ctx["out"].emit(out)
    return 0


def _ads_analytics_get(args: Any, ctx: dict[str, Any], *, stage: str, path: str) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _ads_analytics_params(args)
    data = api.get(path.format(ad_account_id=ad_account_id), params=params or None)
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "path": path.format(ad_account_id=ad_account_id),
        "params": params,
        "data": data,
    }
    ctx["audit"].write(stage, {"ad_account_id": ad_account_id})
    ctx["out"].emit(out)
    return 0


def cmd_ads_ad_account_analytics(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_analytics_get(
        args,
        ctx,
        stage="ads.analytics.ad_account",
        path="/ad_accounts/{ad_account_id}/analytics",
    )


def cmd_ads_campaigns_analytics(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_analytics_get(
        args,
        ctx,
        stage="ads.analytics.campaigns",
        path="/ad_accounts/{ad_account_id}/campaigns/analytics",
    )


def cmd_ads_ad_groups_analytics(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_analytics_get(
        args,
        ctx,
        stage="ads.analytics.ad_groups",
        path="/ad_accounts/{ad_account_id}/ad_groups/analytics",
    )


def cmd_ads_ads_analytics(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_analytics_get(
        args,
        ctx,
        stage="ads.analytics.ads",
        path="/ad_accounts/{ad_account_id}/ads/analytics",
    )


def cmd_ads_pins_analytics(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_analytics_get(
        args,
        ctx,
        stage="ads.analytics.pins",
        path="/ad_accounts/{ad_account_id}/pins/analytics",
    )


def _ads_targeting_analytics_params(args: Any) -> dict[str, Any]:
    params = build_analytics_params(
        start_date=getattr(args, "start_date", None),
        end_date=getattr(args, "end_date", None),
        metrics=getattr(args, "metric_type", None),
        extra_params=getattr(args, "param", None),
        default_days=30,
        default_metrics=None,
    )
    granularity = getattr(args, "granularity", None)
    if isinstance(granularity, str) and granularity.strip():
        params["granularity"] = granularity.strip().upper()
    return params


def _ads_targeting_analytics_get(args: Any, ctx: dict[str, Any], *, stage: str, path: str) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _ads_targeting_analytics_params(args)
    full_path = path.format(ad_account_id=ad_account_id)
    data = api.get(full_path, params=params or None)
    out = {"ok": True, "ad_account_id": ad_account_id, "path": full_path, "params": params, "data": data}
    ctx["audit"].write(stage, {"ad_account_id": ad_account_id})
    ctx["out"].emit(out)
    return 0


def cmd_ads_targeting_analytics_ad_account(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_targeting_analytics_get(
        args,
        ctx,
        stage="ads.targeting_analytics.ad_account",
        path="/ad_accounts/{ad_account_id}/targeting_analytics",
    )


def cmd_ads_targeting_analytics_campaigns(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_targeting_analytics_get(
        args,
        ctx,
        stage="ads.targeting_analytics.campaigns",
        path="/ad_accounts/{ad_account_id}/campaigns/targeting_analytics",
    )


def cmd_ads_targeting_analytics_ad_groups(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_targeting_analytics_get(
        args,
        ctx,
        stage="ads.targeting_analytics.ad_groups",
        path="/ad_accounts/{ad_account_id}/ad_groups/targeting_analytics",
    )


def cmd_ads_targeting_analytics_ads(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_targeting_analytics_get(
        args,
        ctx,
        stage="ads.targeting_analytics.ads",
        path="/ad_accounts/{ad_account_id}/ads/targeting_analytics",
    )


def _ads_simple_get(args: Any, ctx: dict[str, Any], *, stage: str, path: str) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _parse_kv_pairs(args.param)
    full_path = path.format(ad_account_id=ad_account_id)
    data = api.get(full_path, params=params or None)
    out = {"ok": True, "ad_account_id": ad_account_id, "path": full_path, "params": params, "data": data}
    ctx["audit"].write(stage, {"ad_account_id": ad_account_id})
    ctx["out"].emit(out)
    return 0


def cmd_ads_audience_insights(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_simple_get(
        args,
        ctx,
        stage="ads.audience_insights",
        path="/ad_accounts/{ad_account_id}/audience_insights",
    )


def cmd_ads_audiences(args: Any, ctx: dict[str, Any]) -> int:
    return _ads_simple_get(
        args,
        ctx,
        stage="ads.insights.audiences",
        path="/ad_accounts/{ad_account_id}/insights/audiences",
    )


def cmd_ads_campaigns_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _parse_kv_pairs(args.param)
    items, bookmark, pages = api.list_all(
        f"/ad_accounts/{ad_account_id}/campaigns",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write("ads.campaigns.list", {"ad_account_id": ad_account_id, "count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_ads_campaigns_get(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    campaign_id = str(args.id).strip()
    if not campaign_id:
        raise RuntimeError("--id is required")
    params = _parse_kv_pairs(args.param)
    data = api.get(f"/ad_accounts/{ad_account_id}/campaigns/{campaign_id}", params=params or None)
    out = {"ok": True, "ad_account_id": ad_account_id, "campaign": data}
    ctx["audit"].write("ads.campaigns.get", {"ad_account_id": ad_account_id, "campaign_id": campaign_id})
    ctx["out"].emit(out)
    return 0


def cmd_ads_ad_groups_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _parse_kv_pairs(args.param)
    items, bookmark, pages = api.list_all(
        f"/ad_accounts/{ad_account_id}/ad_groups",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write("ads.ad_groups.list", {"ad_account_id": ad_account_id, "count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_ads_ad_groups_get(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    ad_group_id = str(args.id).strip()
    if not ad_group_id:
        raise RuntimeError("--id is required")
    params = _parse_kv_pairs(args.param)
    data = api.get(f"/ad_accounts/{ad_account_id}/ad_groups/{ad_group_id}", params=params or None)
    out = {"ok": True, "ad_account_id": ad_account_id, "ad_group": data}
    ctx["audit"].write("ads.ad_groups.get", {"ad_account_id": ad_account_id, "ad_group_id": ad_group_id})
    ctx["out"].emit(out)
    return 0


def cmd_ads_ads_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _parse_kv_pairs(args.param)
    items, bookmark, pages = api.list_all(
        f"/ad_accounts/{ad_account_id}/ads",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write("ads.ads.list", {"ad_account_id": ad_account_id, "count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_ads_ads_get(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    ad_id = str(args.id).strip()
    if not ad_id:
        raise RuntimeError("--id is required")
    params = _parse_kv_pairs(args.param)
    data = api.get(f"/ad_accounts/{ad_account_id}/ads/{ad_id}", params=params or None)
    out = {"ok": True, "ad_account_id": ad_account_id, "ad": data}
    ctx["audit"].write("ads.ads.get", {"ad_account_id": ad_account_id, "ad_id": ad_id})
    ctx["out"].emit(out)
    return 0


def _load_json_file(path: str) -> Any:
    p = Path(str(path)).expanduser().resolve()
    if not p.exists():
        raise RuntimeError(f"JSON file not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Invalid JSON in file: {p}: {type(e).__name__}") from None


def _load_json_object_file(path: str) -> dict[str, Any]:
    body = _load_json_file(path)
    if not isinstance(body, dict):
        raise RuntimeError("JSON body must be an object")
    return body


def _ensure_list(body: Any) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        raise RuntimeError("JSON body must be an object")
    return [body]


def _inject_ad_account_id(items: list[dict[str, Any]], *, ad_account_id: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for it in items:
        cur = dict(it)
        if "ad_account_id" not in cur:
            cur["ad_account_id"] = ad_account_id
        else:
            if str(cur.get("ad_account_id") or "").strip() != ad_account_id:
                raise RuntimeError("JSON body ad_account_id does not match --ad-account-id")
        out.append(cur)
    return out


def _extract_ids(resp: Any) -> list[str]:
    if not isinstance(resp, dict):
        return []
    ids: list[str] = []
    items = resp.get("items")
    if isinstance(items, list):
        for it in items:
            if not isinstance(it, dict):
                continue
            data = it.get("data")
            if isinstance(data, dict):
                v = data.get("id")
                if isinstance(v, str) and v.strip():
                    ids.append(v.strip())
            v = it.get("id")
            if isinstance(v, str) and v.strip():
                ids.append(v.strip())
    v = resp.get("id")
    if isinstance(v, str) and v.strip():
        ids.append(v.strip())
    # Dedup preserve order.
    seen: set[str] = set()
    out: list[str] = []
    for i in ids:
        if i in seen:
            continue
        seen.add(i)
        out.append(i)
    return out


def _ads_write_common(
    args: Any,
    ctx: dict[str, Any],
    *,
    resource: str,
    operation: str,
    method: str,
    path: str,
    json_body: Any | None,
    ack_spend_required: bool,
    get_path_template: str | None = None,
    verify_status: str | None = None,
    idempotent_if_status: str | None = None,
) -> int:
    api = _api(ctx)
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")

    formatted_path = path.format(ad_account_id=ad_account_id)
    ops = [write_operation(method=method, path=formatted_path, json_body=json_body)]
    action = f"ads.{resource}.{operation}"
    acks_required: list[str] = []
    if ack_spend_required:
        acks_required.append("ack-spend")

    if not bool(ctx.get("apply")):
        out = build_plan(action=action, operations=ops, acks_required=acks_required, request=ops[0])
        out.update({"resource": resource, "operation": operation, "ad_account_id": ad_account_id})
        ctx["audit"].write(action, {"dry_run": True, "ad_account_id": ad_account_id})
        ctx["out"].emit(out)
        return 0

    require_write_allowed(ctx, acks_required=acks_required)

    before: dict[str, Any] | None = None
    verification: dict[str, Any] = {"read_back": bool(get_path_template)}
    if get_path_template and (verify_status or idempotent_if_status):
        rid = str(getattr(args, "id", "") or "").strip()
        if not rid:
            raise RuntimeError("--id is required")
        before = api.get(get_path_template.format(ad_account_id=ad_account_id, id=rid))
        if not isinstance(before, dict):
            raise RuntimeError("Unexpected response (not an object)")
        status = str(before.get("status") or "").strip().upper()
        if idempotent_if_status and status == str(idempotent_if_status).strip().upper():
            verification.update(
                {
                    "idempotent": True,
                    "expected_status": str(idempotent_if_status).strip().upper(),
                    "actual_status": status,
                    "verified_ids": [rid],
                }
            )
            out = build_receipt(
                action=action,
                changed=False,
                operations=ops,
                acks_required=acks_required,
                request=ops[0],
                before=before,
                write_result=None,
                after=before,
            )
            out.update({"resource": resource, "operation": operation, "ad_account_id": ad_account_id, "verification": verification})
            ctx["audit"].write(action, {"dry_run": False, "ad_account_id": ad_account_id, "changed": False})
            ctx["out"].emit(out)
            return 0

    if method == "POST":
        resp = api.post(formatted_path, json_body=json_body)
    elif method == "PATCH":
        if json_body is None:
            raise RuntimeError("Internal error: missing json_body for PATCH")
        resp = api.patch(formatted_path, json_body=json_body)  # type: ignore[arg-type]
    else:
        raise RuntimeError(f"Unsupported method: {method}")

    verified_items: list[dict[str, Any]] = []
    if get_path_template:
        ids = _extract_ids(resp)
        rid_arg = str(getattr(args, "id", "") or "").strip()
        if rid_arg and method == "PATCH" and not ids:
            ids = [rid_arg]
        if not ids:
            raise RuntimeError("Write response did not include any ids for read-back verification")
        verification["verified_ids"] = list(ids)
        for rid in ids:
            after = api.get(get_path_template.format(ad_account_id=ad_account_id, id=rid))
            if not isinstance(after, dict):
                raise RuntimeError("Unexpected read-back response (not an object)")
            if str(after.get("id") or "").strip() != rid:
                raise RuntimeError(f"Verification failed: expected id {rid}, got {after.get('id')!r}")
            if verify_status:
                st = str(after.get("status") or "").strip().upper()
                if st != str(verify_status).strip().upper():
                    raise RuntimeError(f"Verification failed: status is {st!r} (expected {verify_status!r})")
                verification["expected_status"] = str(verify_status).strip().upper()
            verified_items.append(after)

    out = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        acks_required=acks_required,
        request=ops[0],
        before=before,
        write_result=resp,
        after=verified_items or None,
    )
    out.update({"resource": resource, "operation": operation, "ad_account_id": ad_account_id, "verification": verification})
    ctx["audit"].write(action, {"dry_run": False, "ad_account_id": ad_account_id, "changed": True})
    ctx["out"].emit(out)
    return 0


def cmd_ads_campaigns_create(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    body = _inject_ad_account_id(_ensure_list(_load_json_object_file(args.body_file)), ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="campaigns",
        operation="create",
        method="POST",
        path="/ad_accounts/{ad_account_id}/campaigns",
        json_body=body,
        ack_spend_required=True,
        get_path_template="/ad_accounts/{ad_account_id}/campaigns/{id}",
    )


def cmd_ads_campaigns_update(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    rid = str(args.id).strip()
    it = dict(_load_json_object_file(args.body_file))
    if "id" not in it:
        it["id"] = rid
    if str(it.get("id") or "").strip() != rid:
        raise RuntimeError("JSON body id does not match --id")
    items = _inject_ad_account_id([it], ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="campaigns",
        operation="update",
        method="PATCH",
        path="/ad_accounts/{ad_account_id}/campaigns",
        json_body=items,
        ack_spend_required=True,
        get_path_template="/ad_accounts/{ad_account_id}/campaigns/{id}",
    )


def cmd_ads_campaigns_pause(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    rid = str(args.id).strip()
    body = _inject_ad_account_id([{"id": rid, "status": "PAUSED"}], ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="campaigns",
        operation="pause",
        method="PATCH",
        path="/ad_accounts/{ad_account_id}/campaigns",
        json_body=body,
        ack_spend_required=False,
        get_path_template="/ad_accounts/{ad_account_id}/campaigns/{id}",
        verify_status="PAUSED",
        idempotent_if_status="PAUSED",
    )


def cmd_ads_campaigns_resume(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    rid = str(args.id).strip()
    body = _inject_ad_account_id([{"id": rid, "status": "ACTIVE"}], ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="campaigns",
        operation="resume",
        method="PATCH",
        path="/ad_accounts/{ad_account_id}/campaigns",
        json_body=body,
        ack_spend_required=True,
        get_path_template="/ad_accounts/{ad_account_id}/campaigns/{id}",
        verify_status="ACTIVE",
        idempotent_if_status="ACTIVE",
    )


def cmd_ads_ad_groups_create(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    body = _inject_ad_account_id(_ensure_list(_load_json_object_file(args.body_file)), ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="ad_groups",
        operation="create",
        method="POST",
        path="/ad_accounts/{ad_account_id}/ad_groups",
        json_body=body,
        ack_spend_required=True,
        get_path_template="/ad_accounts/{ad_account_id}/ad_groups/{id}",
    )


def cmd_ads_ad_groups_update(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    rid = str(args.id).strip()
    it = dict(_load_json_object_file(args.body_file))
    if "id" not in it:
        it["id"] = rid
    if str(it.get("id") or "").strip() != rid:
        raise RuntimeError("JSON body id does not match --id")
    items = _inject_ad_account_id([it], ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="ad_groups",
        operation="update",
        method="PATCH",
        path="/ad_accounts/{ad_account_id}/ad_groups",
        json_body=items,
        ack_spend_required=True,
        get_path_template="/ad_accounts/{ad_account_id}/ad_groups/{id}",
    )


def cmd_ads_ad_groups_pause(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    rid = str(args.id).strip()
    body = _inject_ad_account_id([{"id": rid, "status": "PAUSED"}], ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="ad_groups",
        operation="pause",
        method="PATCH",
        path="/ad_accounts/{ad_account_id}/ad_groups",
        json_body=body,
        ack_spend_required=False,
        get_path_template="/ad_accounts/{ad_account_id}/ad_groups/{id}",
        verify_status="PAUSED",
        idempotent_if_status="PAUSED",
    )


def cmd_ads_ad_groups_resume(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    rid = str(args.id).strip()
    body = _inject_ad_account_id([{"id": rid, "status": "ACTIVE"}], ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="ad_groups",
        operation="resume",
        method="PATCH",
        path="/ad_accounts/{ad_account_id}/ad_groups",
        json_body=body,
        ack_spend_required=True,
        get_path_template="/ad_accounts/{ad_account_id}/ad_groups/{id}",
        verify_status="ACTIVE",
        idempotent_if_status="ACTIVE",
    )


def cmd_ads_ads_create(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    body = _inject_ad_account_id(_ensure_list(_load_json_object_file(args.body_file)), ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="ads",
        operation="create",
        method="POST",
        path="/ad_accounts/{ad_account_id}/ads",
        json_body=body,
        ack_spend_required=True,
        get_path_template="/ad_accounts/{ad_account_id}/ads/{id}",
    )


def cmd_ads_ads_update(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    rid = str(args.id).strip()
    it = dict(_load_json_object_file(args.body_file))
    if "id" not in it:
        it["id"] = rid
    if str(it.get("id") or "").strip() != rid:
        raise RuntimeError("JSON body id does not match --id")
    items = _inject_ad_account_id([it], ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="ads",
        operation="update",
        method="PATCH",
        path="/ad_accounts/{ad_account_id}/ads",
        json_body=items,
        ack_spend_required=True,
        get_path_template="/ad_accounts/{ad_account_id}/ads/{id}",
    )


def cmd_ads_ads_pause(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    rid = str(args.id).strip()
    body = _inject_ad_account_id([{"id": rid, "status": "PAUSED"}], ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="ads",
        operation="pause",
        method="PATCH",
        path="/ad_accounts/{ad_account_id}/ads",
        json_body=body,
        ack_spend_required=False,
        get_path_template="/ad_accounts/{ad_account_id}/ads/{id}",
        verify_status="PAUSED",
        idempotent_if_status="PAUSED",
    )


def cmd_ads_ads_resume(args: Any, ctx: dict[str, Any]) -> int:
    ad_account_id = str(args.ad_account_id).strip()
    rid = str(args.id).strip()
    body = _inject_ad_account_id([{"id": rid, "status": "ACTIVE"}], ad_account_id=ad_account_id)
    return _ads_write_common(
        args,
        ctx,
        resource="ads",
        operation="resume",
        method="PATCH",
        path="/ad_accounts/{ad_account_id}/ads",
        json_body=body,
        ack_spend_required=True,
        get_path_template="/ad_accounts/{ad_account_id}/ads/{id}",
        verify_status="ACTIVE",
        idempotent_if_status="ACTIVE",
    )
