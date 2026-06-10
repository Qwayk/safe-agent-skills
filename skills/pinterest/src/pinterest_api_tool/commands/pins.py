from __future__ import annotations

from urllib.parse import urlparse, urlunparse
from typing import Any

from ..api import PinterestApi, resolve_access_token
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


def _param_ad_account_id(args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if getattr(args, "ad_account_id", None):
        params["ad_account_id"] = str(args.ad_account_id).strip()
    return params


def _canonicalize_link(url: str) -> str | None:
    s = (url or "").strip()
    if not s:
        return None
    try:
        u = urlparse(s)
    except Exception:
        return None
    if u.scheme not in {"http", "https"}:
        return None
    if not u.hostname:
        return None

    host = u.hostname.lower()
    netloc = host
    if u.port:
        netloc = f"{host}:{u.port}"

    path = u.path or "/"
    if path and not path.endswith("/") and "." not in path.split("/")[-1]:
        path = f"{path}/"

    return urlunparse(("https", netloc, path, "", "", ""))


def _list_destination_pins(
    api: PinterestApi,
    *,
    board_id: str,
    board_section_id: str | None,
    params: dict[str, Any],
    scan_limit: int,
) -> list[dict[str, Any]]:
    path = f"/boards/{board_id}/pins"
    if board_section_id:
        path = f"/boards/{board_id}/sections/{board_section_id}/pins"
    items, _, _ = api.list_all(path, params=params or None, limit=int(scan_limit), page_size=100)
    return items


def _find_pins_by_canonical_link(pins: list[dict[str, Any]], canonical_link: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in pins:
        if not isinstance(p, dict):
            continue
        link = p.get("link")
        if not isinstance(link, str) or not link.strip():
            continue
        c = _canonicalize_link(link)
        if c and c == canonical_link:
            out.append(p)
    return out


def _build_pin_media_source(args: Any) -> dict[str, Any]:
    st = str(getattr(args, "media_source_type", "") or "").strip()
    if not st:
        raise RuntimeError("--media-source-type is required")

    if st == "image_url":
        url = str(getattr(args, "media_url", "") or "").strip()
        if not url:
            raise RuntimeError("--media-url is required when --media-source-type=image_url")
        return {"source_type": "image_url", "url": url}

    if st == "video_id":
        media_id = str(getattr(args, "media_id", "") or "").strip()
        if not media_id:
            raise RuntimeError("--media-id is required when --media-source-type=video_id")
        out: dict[str, Any] = {"source_type": "video_id", "media_id": media_id}
        cover = str(getattr(args, "media_cover_image_url", "") or "").strip()
        if cover:
            out["cover_image_url"] = cover
        return out

    if st == "image_base64":
        content_type = str(getattr(args, "media_content_type", "") or "").strip()
        data = str(getattr(args, "media_data", "") or "").strip()
        if not content_type or not data:
            raise RuntimeError("--media-content-type and --media-data are required when --media-source-type=image_base64")
        return {"source_type": "image_base64", "content_type": content_type, "data": data}

    raise RuntimeError(f"Unsupported --media-source-type: {st!r}")


def cmd_pins_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    params: dict[str, Any] = {}
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()
    if args.include_protected_pins:
        params["include_protected_pins"] = True
    if args.pin_filter:
        params["pin_filter"] = str(args.pin_filter).strip()
    if args.pin_type:
        params["pin_type"] = str(args.pin_type).strip()
    if args.creative_types:
        creative_types = [s.strip() for s in str(args.creative_types).split(",") if s.strip()]
        if creative_types:
            # Encode as repeated query params.
            params["creative_types"] = creative_types
    if args.pin_metrics:
        params["pin_metrics"] = True

    items, bookmark, pages = api.list_all(
        "/pins",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {"ok": True, "count": len(items), "pages": pages, "bookmark": bookmark, "items": items}
    ctx["audit"].write("pins.list", {"count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_pins_get(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    pin_id = str(args.id).strip()
    if not pin_id:
        raise RuntimeError("--id is required")
    params: dict[str, Any] = {}
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()
    if args.pin_metrics:
        params["pin_metrics"] = True
    data = api.get(f"/pins/{pin_id}", params=params or None)
    out = {"ok": True, "pin": data}
    ctx["audit"].write("pins.get", {"pin_id": pin_id})
    ctx["out"].emit(out)
    return 0


def cmd_pins_create(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.board_id).strip()
    if not board_id:
        raise RuntimeError("--board-id is required")
    board_section_id = str(args.board_section_id).strip() if getattr(args, "board_section_id", None) else None
    if board_section_id is not None and not board_section_id:
        raise RuntimeError("--board-section-id must not be empty")

    scan_limit = int(getattr(args, "scan_limit", 5000))
    if scan_limit < 1:
        raise RuntimeError("--scan-limit must be >= 1")

    media_source = _build_pin_media_source(args)

    body: dict[str, Any] = {"board_id": board_id, "media_source": media_source}
    if board_section_id:
        body["board_section_id"] = board_section_id
    if args.title is not None:
        body["title"] = str(args.title)
    if args.description is not None:
        body["description"] = str(args.description)
    if args.link is not None:
        link = str(args.link).strip()
        if link and _canonicalize_link(link) is None:
            raise RuntimeError("Refused: --link must be a valid http(s) URL")
        body["link"] = link
    if args.alt_text is not None:
        body["alt_text"] = str(args.alt_text)

    params = _param_ad_account_id(args)
    action = "pins.create"
    list_path = f"/boards/{board_id}/pins" if not board_section_id else f"/boards/{board_id}/sections/{board_section_id}/pins"
    ops = [
        write_operation(method="GET", path=list_path, params={**params, "limit": scan_limit}),
        write_operation(method="POST", path="/pins", params=params or None, json_body=body),
        write_operation(method="GET", path="/pins/{pin_id}", params=params or None),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(
            action=action,
            operations=ops,
            request={
                "board_id": board_id,
                "board_section_id": board_section_id,
                "scan_limit": scan_limit,
                "title": args.title,
                "description": args.description,
                "link": args.link,
                "alt_text": args.alt_text,
                "media_source_type": getattr(args, "media_source_type", None),
            },
        )
        ctx["audit"].write("pins.create.plan", {"board_id": board_id, "board_section_id": board_section_id})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx)

    desired_link = str(args.link).strip() if args.link is not None else ""
    desired_canonical = _canonicalize_link(desired_link) if desired_link else None
    existing_matches: list[dict[str, Any]] = []
    if desired_canonical:
        existing_pins = _list_destination_pins(
            api,
            board_id=board_id,
            board_section_id=board_section_id,
            params=params,
            scan_limit=scan_limit,
        )
        matches = _find_pins_by_canonical_link(existing_pins, desired_canonical)
        existing_matches = [{"id": p.get("id"), "link": p.get("link")} for p in matches]
        if matches and not bool(getattr(args, "allow_mismatch", False)):
            raise RuntimeError(
                "Refusing to create a duplicate pin: a pin with this canonical link already exists on the destination. "
                "Use `pins ensure`, pick a different link, or pass --allow-mismatch to force a duplicate."
            )

    created = api.post("/pins", json_body=body, params=params or None)
    pin_id = str(created.get("id") or "").strip()
    if not pin_id:
        raise RuntimeError("Unexpected create pin response: missing id")
    after = api.get(f"/pins/{pin_id}", params=params or None)

    if str(after.get("id") or "").strip() != pin_id:
        raise RuntimeError("Verification failed: pin id mismatch")
    if str(after.get("board_id") or "").strip() != board_id:
        raise RuntimeError("Verification failed: board_id mismatch")

    mismatches: list[str] = []
    if board_section_id is not None and str(after.get("board_section_id") or "").strip() != (board_section_id or ""):
        mismatches.append("board_section_id")
    if args.title is not None and str(after.get("title") or "") != str(args.title):
        mismatches.append("title")
    if args.description is not None and str(after.get("description") or "") != str(args.description):
        mismatches.append("description")
    if args.alt_text is not None and str(after.get("alt_text") or "") != str(args.alt_text):
        mismatches.append("alt_text")
    if args.link is not None and desired_canonical:
        after_canonical = _canonicalize_link(str(after.get("link") or ""))
        if after_canonical != desired_canonical:
            mismatches.append("link")

    if mismatches and not bool(getattr(args, "allow_mismatch", False)):
        raise RuntimeError(f"Verification failed: {', '.join(mismatches)} mismatch")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request={
            "board_id": board_id,
            "board_section_id": board_section_id,
            "scan_limit": scan_limit,
            "title": args.title,
            "description": args.description,
            "link": args.link,
            "alt_text": args.alt_text,
            "media_source_type": getattr(args, "media_source_type", None),
        },
        before={"existing_matches": existing_matches},
        write_result={"created": {"id": pin_id}},
        after=after,
    )
    ctx["audit"].write("pins.create.apply", {"pin_id": pin_id, "board_id": board_id})
    ctx["out"].emit(receipt)
    return 0


def cmd_pins_update(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    pin_id = str(args.id).strip()
    if not pin_id:
        raise RuntimeError("--id is required")

    body: dict[str, Any] = {}
    if args.title is not None:
        body["title"] = str(args.title)
    if args.description is not None:
        body["description"] = str(args.description)
    if args.link is not None:
        link = str(args.link).strip()
        if link and _canonicalize_link(link) is None:
            raise RuntimeError("Refused: --link must be a valid http(s) URL")
        body["link"] = link
    if args.alt_text is not None:
        body["alt_text"] = str(args.alt_text)
    if getattr(args, "board_id", None) is not None:
        bid = str(args.board_id).strip()
        if not bid:
            raise RuntimeError("--board-id must not be empty")
        body["board_id"] = bid
    if getattr(args, "board_section_id", None) is not None:
        sid = str(args.board_section_id).strip()
        if not sid:
            raise RuntimeError("--board-section-id must not be empty")
        body["board_section_id"] = sid

    if not body:
        raise RuntimeError(
            "At least one of --title/--description/--link/--alt-text/--board-id/--board-section-id is required"
        )

    params = _param_ad_account_id(args)
    action = "pins.update"
    ops = [
        write_operation(method="GET", path=f"/pins/{pin_id}", params=params or None),
        write_operation(method="PATCH", path=f"/pins/{pin_id}", params=params or None, json_body=body),
        write_operation(method="GET", path=f"/pins/{pin_id}", params=params or None),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(action=action, operations=ops, request={"pin_id": pin_id, **body})
        ctx["audit"].write("pins.update.plan", {"pin_id": pin_id, "fields": sorted(body.keys())})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx)
    before = api.get(f"/pins/{pin_id}", params=params or None)
    _ = api.patch(f"/pins/{pin_id}", json_body=body, params=params or None)
    after = api.get(f"/pins/{pin_id}", params=params or None)

    mismatches: list[str] = []
    for k, v in body.items():
        if k == "link":
            desired = _canonicalize_link(str(v))
            got = _canonicalize_link(str(after.get("link") or ""))
            if desired and got != desired:
                mismatches.append("link")
        else:
            if str(after.get(k) or "") != str(v):
                mismatches.append(k)

    if mismatches and not bool(getattr(args, "allow_mismatch", False)):
        raise RuntimeError(f"Verification failed: {', '.join(sorted(set(mismatches)))} mismatch")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request={"pin_id": pin_id, **body},
        before=before,
        write_result={"updated_fields": sorted(body.keys())},
        after=after,
    )
    ctx["audit"].write("pins.update.apply", {"pin_id": pin_id, "fields": sorted(body.keys())})
    ctx["out"].emit(receipt)
    return 0


def cmd_pins_delete(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    pin_id = str(args.id).strip()
    if not pin_id:
        raise RuntimeError("--id is required")

    params = _param_ad_account_id(args)
    action = "pins.delete"
    ops = [
        write_operation(method="GET", path=f"/pins/{pin_id}", params=params or None),
        write_operation(method="DELETE", path=f"/pins/{pin_id}", params=params or None),
        write_operation(method="GET", path=f"/pins/{pin_id}", params=params or None),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(action=action, operations=ops, acks_required=["ack-irreversible"], request={"pin_id": pin_id})
        ctx["audit"].write("pins.delete.plan", {"pin_id": pin_id})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx, acks_required=["ack-irreversible"])
    before_resp = api.get_response(f"/pins/{pin_id}", params=params or None, allowed_statuses=(404,))
    before = before_resp.json() if before_resp.status != 404 else None

    if before_resp.status == 404:
        receipt = build_receipt(
            action=action,
            changed=False,
            operations=ops,
            acks_required=["ack-irreversible"],
            request={"pin_id": pin_id},
            before=None,
            write_result={"skipped": "already_missing"},
            after=None,
        )
        ctx["audit"].write("pins.delete.apply", {"pin_id": pin_id, "changed": False})
        ctx["out"].emit(receipt)
        return 0

    _ = api.delete(f"/pins/{pin_id}", params=params or None)
    after_resp = api.get_response(f"/pins/{pin_id}", params=params or None, allowed_statuses=(404,))
    if after_resp.status != 404:
        raise RuntimeError("Verification failed: pin still exists after delete")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        acks_required=["ack-irreversible"],
        request={"pin_id": pin_id},
        before=before,
        write_result={"deleted": True},
        after={"status": 404},
    )
    ctx["audit"].write("pins.delete.apply", {"pin_id": pin_id, "changed": True})
    ctx["out"].emit(receipt)
    return 0


def cmd_pins_save(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    source_id = str(args.id).strip()
    if not source_id:
        raise RuntimeError("--id is required")
    board_id = str(args.board_id).strip()
    if not board_id:
        raise RuntimeError("--board-id is required")
    board_section_id = str(args.board_section_id).strip() if getattr(args, "board_section_id", None) else None
    if board_section_id is not None and not board_section_id:
        raise RuntimeError("--board-section-id must not be empty")

    scan_limit = int(getattr(args, "scan_limit", 5000))
    if scan_limit < 1:
        raise RuntimeError("--scan-limit must be >= 1")

    params = _param_ad_account_id(args)
    list_path = f"/boards/{board_id}/pins" if not board_section_id else f"/boards/{board_id}/sections/{board_section_id}/pins"
    action = "pins.save"
    ops = [
        write_operation(method="GET", path=f"/pins/{source_id}", params=params or None),
        write_operation(method="GET", path=list_path, params={**params, "limit": scan_limit}),
        write_operation(
            method="POST",
            path=f"/pins/{source_id}/save",
            params=params or None,
            json_body={"board_id": board_id, **({"board_section_id": board_section_id} if board_section_id else {})},
        ),
        write_operation(method="GET", path="/pins/{pin_id}", params=params or None),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(
            action=action,
            operations=ops,
            request={"source_pin_id": source_id, "board_id": board_id, "board_section_id": board_section_id, "scan_limit": scan_limit},
        )
        ctx["audit"].write("pins.save.plan", {"source_id": source_id, "board_id": board_id, "board_section_id": board_section_id})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx)

    source = api.get(f"/pins/{source_id}", params=params or None)
    source_canonical = _canonicalize_link(str(source.get("link") or ""))
    dest_pins = _list_destination_pins(api, board_id=board_id, board_section_id=board_section_id, params=params, scan_limit=scan_limit)
    already_saved: list[dict[str, Any]] = []
    for p in dest_pins:
        if not isinstance(p, dict):
            continue
        if str(p.get("parent_pin_id") or "").strip() == source_id:
            already_saved.append(p)
            continue
        if source_canonical:
            link = p.get("link")
            if isinstance(link, str) and link.strip() and _canonicalize_link(link) == source_canonical:
                already_saved.append(p)

    if already_saved and not bool(getattr(args, "allow_mismatch", False)):
        receipt = build_receipt(
            action=action,
            changed=False,
            operations=ops,
            request={"source_pin_id": source_id, "board_id": board_id, "board_section_id": board_section_id, "scan_limit": scan_limit},
            before={"existing_matches": [{"id": p.get("id"), "parent_pin_id": p.get("parent_pin_id")} for p in already_saved]},
            write_result={"skipped": "already_saved"},
            after=None,
        )
        ctx["audit"].write("pins.save.apply", {"source_id": source_id, "board_id": board_id, "changed": False})
        ctx["out"].emit(receipt)
        return 0

    saved = api.post(
        f"/pins/{source_id}/save",
        json_body={"board_id": board_id, **({"board_section_id": board_section_id} if board_section_id else {})},
        params=params or None,
    )
    saved_id = str(saved.get("id") or "").strip()
    if not saved_id:
        raise RuntimeError("Unexpected save pin response: missing id")
    after = api.get(f"/pins/{saved_id}", params=params or None)

    mismatches: list[str] = []
    if str(after.get("board_id") or "").strip() != board_id:
        mismatches.append("board_id")
    if board_section_id is not None and str(after.get("board_section_id") or "").strip() != (board_section_id or ""):
        mismatches.append("board_section_id")
    if "parent_pin_id" in after and str(after.get("parent_pin_id") or "").strip() != source_id:
        mismatches.append("parent_pin_id")

    if mismatches and not bool(getattr(args, "allow_mismatch", False)):
        raise RuntimeError(f"Verification failed: {', '.join(mismatches)} mismatch")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request={"source_pin_id": source_id, "board_id": board_id, "board_section_id": board_section_id, "scan_limit": scan_limit},
        before={"existing_matches": [{"id": p.get("id"), "parent_pin_id": p.get("parent_pin_id")} for p in already_saved]},
        write_result={"saved": {"id": saved_id}},
        after=after,
    )
    ctx["audit"].write("pins.save.apply", {"source_id": source_id, "saved_id": saved_id, "board_id": board_id, "changed": True})
    ctx["out"].emit(receipt)
    return 0


def cmd_pins_ensure(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.board_id).strip()
    if not board_id:
        raise RuntimeError("--board-id is required")
    board_section_id = str(args.board_section_id).strip() if getattr(args, "board_section_id", None) else None
    if board_section_id is not None and not board_section_id:
        raise RuntimeError("--board-section-id must not be empty")

    link = str(args.link).strip()
    if not link:
        raise RuntimeError("--link is required")
    canonical = _canonicalize_link(link)
    if not canonical:
        raise RuntimeError("Refused: --link must be a valid http(s) URL")

    scan_limit = int(getattr(args, "scan_limit", 5000))
    if scan_limit < 1:
        raise RuntimeError("--scan-limit must be >= 1")

    params = _param_ad_account_id(args)
    dest_pins = _list_destination_pins(api, board_id=board_id, board_section_id=board_section_id, params=params, scan_limit=scan_limit)
    matches = _find_pins_by_canonical_link(dest_pins, canonical)
    if len(matches) > 1:
        raise RuntimeError(
            "Refusing: multiple destination pins match this canonical link. Use `pins update`/`pins delete` by id."
        )

    list_path = f"/boards/{board_id}/pins" if not board_section_id else f"/boards/{board_id}/sections/{board_section_id}/pins"
    action = "pins.ensure"

    if matches:
        ops = [write_operation(method="GET", path=list_path, params={**params, "limit": scan_limit})]
        if not bool(ctx.get("apply")):
            plan = build_plan(action=action, operations=ops, request={"board_id": board_id, "board_section_id": board_section_id, "link": link})
            ctx["audit"].write("pins.ensure.plan", {"board_id": board_id, "board_section_id": board_section_id, "mode": "noop"})
            ctx["out"].emit(plan)
            return 0

        require_write_allowed(ctx)
        receipt = build_receipt(
            action=action,
            changed=False,
            operations=ops,
            request={"board_id": board_id, "board_section_id": board_section_id, "link": link},
            before={"existing_match": {"id": matches[0].get("id"), "link": matches[0].get("link")}},
            write_result={"skipped": "already_exists"},
            after={"id": matches[0].get("id")},
        )
        ctx["audit"].write("pins.ensure.apply", {"board_id": board_id, "board_section_id": board_section_id, "changed": False})
        ctx["out"].emit(receipt)
        return 0

    media_source = _build_pin_media_source(args)
    body: dict[str, Any] = {"board_id": board_id, "media_source": media_source}
    if board_section_id:
        body["board_section_id"] = board_section_id
    if args.title is not None:
        body["title"] = str(args.title)
    if args.description is not None:
        body["description"] = str(args.description)
    body["link"] = link
    if args.alt_text is not None:
        body["alt_text"] = str(args.alt_text)

    ops = [
        write_operation(method="GET", path=list_path, params={**params, "limit": scan_limit}),
        write_operation(method="POST", path="/pins", params=params or None, json_body=body),
        write_operation(method="GET", path="/pins/{pin_id}", params=params or None),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(
            action=action,
            operations=ops,
            request={
                "board_id": board_id,
                "board_section_id": board_section_id,
                "link": link,
                "scan_limit": scan_limit,
                "title": args.title,
                "description": args.description,
                "alt_text": args.alt_text,
                "media_source_type": getattr(args, "media_source_type", None),
            },
        )
        ctx["audit"].write("pins.ensure.plan", {"board_id": board_id, "board_section_id": board_section_id, "mode": "create"})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx)
    created = api.post("/pins", json_body=body, params=params or None)
    pin_id = str(created.get("id") or "").strip()
    if not pin_id:
        raise RuntimeError("Unexpected create pin response: missing id")
    after = api.get(f"/pins/{pin_id}", params=params or None)

    mismatches: list[str] = []
    if str(after.get("board_id") or "").strip() != board_id:
        mismatches.append("board_id")
    if board_section_id is not None and str(after.get("board_section_id") or "").strip() != (board_section_id or ""):
        mismatches.append("board_section_id")
    after_canonical = _canonicalize_link(str(after.get("link") or ""))
    if after_canonical != canonical:
        mismatches.append("link")
    if args.title is not None and str(after.get("title") or "") != str(args.title):
        mismatches.append("title")
    if args.description is not None and str(after.get("description") or "") != str(args.description):
        mismatches.append("description")
    if args.alt_text is not None and str(after.get("alt_text") or "") != str(args.alt_text):
        mismatches.append("alt_text")

    if mismatches and not bool(getattr(args, "allow_mismatch", False)):
        raise RuntimeError(f"Verification failed: {', '.join(mismatches)} mismatch")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request={
            "board_id": board_id,
            "board_section_id": board_section_id,
            "link": link,
            "scan_limit": scan_limit,
            "title": args.title,
            "description": args.description,
            "alt_text": args.alt_text,
            "media_source_type": getattr(args, "media_source_type", None),
        },
        before=None,
        write_result={"created": {"id": pin_id}},
        after=after,
    )
    ctx["audit"].write("pins.ensure.apply", {"pin_id": pin_id, "board_id": board_id, "board_section_id": board_section_id, "changed": True})
    ctx["out"].emit(receipt)
    return 0
