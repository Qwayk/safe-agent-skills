from __future__ import annotations

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


def _board_name_matches(board: dict[str, Any], name: str) -> bool:
    return str(board.get("name") or "").strip() == name


def _find_boards_by_name(api: PinterestApi, *, name: str, params: dict[str, Any], scan_limit: int) -> list[dict[str, Any]]:
    items, _, _ = api.list_all("/boards", params=params, limit=int(scan_limit), page_size=100)
    return [b for b in items if isinstance(b, dict) and _board_name_matches(b, name)]


def _find_sections_by_name(
    api: PinterestApi,
    *,
    board_id: str,
    name: str,
    params: dict[str, Any],
    scan_limit: int,
) -> list[dict[str, Any]]:
    items, _, _ = api.list_all(f"/boards/{board_id}/sections", params=params, limit=int(scan_limit), page_size=100)
    return [s for s in items if isinstance(s, dict) and str(s.get("name") or "").strip() == name]


def cmd_boards_create(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    name = str(args.name).strip()
    if not name:
        raise RuntimeError("--name is required")

    params = _param_ad_account_id(args)
    body: dict[str, Any] = {"name": name}
    if args.description is not None:
        body["description"] = str(args.description)
    if args.privacy is not None:
        body["privacy"] = str(args.privacy).strip()
    if bool(getattr(args, "is_ads_only", False)):
        body["is_ads_only"] = True

    scan_limit = int(getattr(args, "scan_limit", 5000))
    if scan_limit < 1:
        raise RuntimeError("--scan-limit must be >= 1")

    action = "boards.create"
    ops = [
        write_operation(method="GET", path="/boards", params={**params, "limit": scan_limit}),
        write_operation(method="POST", path="/boards", params=params or None, json_body=body),
        write_operation(method="GET", path="/boards/{board_id}", params=params or None),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(
            action=action,
            operations=ops,
            request={"name": name, "description": args.description, "privacy": args.privacy, "is_ads_only": args.is_ads_only},
        )
        ctx["audit"].write("boards.create.plan", {"name": name})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx)
    existing = _find_boards_by_name(api, name=name, params=params, scan_limit=scan_limit)
    if existing and not bool(getattr(args, "allow_mismatch", False)):
        raise RuntimeError(
            f"Refusing to create board {name!r}: a board with this name already exists. "
            "Use `boards ensure` or pass --allow-mismatch to force a duplicate."
        )

    created = api.post("/boards", json_body=body, params=params or None)
    board_id = str(created.get("id") or "").strip()
    if not board_id:
        raise RuntimeError("Unexpected create board response: missing id")
    after = api.get(f"/boards/{board_id}", params=params or None)

    if str(after.get("id") or "").strip() != board_id:
        raise RuntimeError("Verification failed: board id mismatch")
    if str(after.get("name") or "").strip() != name:
        raise RuntimeError("Verification failed: board name mismatch")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request={"name": name, "description": args.description, "privacy": args.privacy, "is_ads_only": args.is_ads_only},
        before={"existing_name_matches": [{"id": b.get("id"), "name": b.get("name")} for b in existing]},
        write_result={"created": {"id": board_id}},
        after=after,
    )
    ctx["audit"].write("boards.create.apply", {"name": name, "board_id": board_id})
    ctx["out"].emit(receipt)
    return 0


def cmd_boards_update(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.id).strip()
    if not board_id:
        raise RuntimeError("--id is required")

    body: dict[str, Any] = {}
    if args.name is not None:
        body["name"] = str(args.name).strip()
    if args.description is not None:
        body["description"] = str(args.description)
    if args.privacy is not None:
        body["privacy"] = str(args.privacy).strip()
    if not body:
        raise RuntimeError("At least one of --name/--description/--privacy is required")

    params = _param_ad_account_id(args)
    action = "boards.update"
    ops = [
        write_operation(method="GET", path=f"/boards/{board_id}", params=params or None),
        write_operation(method="PATCH", path=f"/boards/{board_id}", params=params or None, json_body=body),
        write_operation(method="GET", path=f"/boards/{board_id}", params=params or None),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(action=action, operations=ops, request={"board_id": board_id, **body})
        ctx["audit"].write("boards.update.plan", {"board_id": board_id, "fields": sorted(body.keys())})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx)
    before = api.get(f"/boards/{board_id}", params=params or None)
    _ = api.patch(f"/boards/{board_id}", json_body=body, params=params or None)
    after = api.get(f"/boards/{board_id}", params=params or None)

    for k, v in body.items():
        if str(after.get(k) or "") != str(v):
            raise RuntimeError(f"Verification failed: {k} mismatch")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request={"board_id": board_id, **body},
        before=before,
        write_result={"updated_fields": sorted(body.keys())},
        after=after,
    )
    ctx["audit"].write("boards.update.apply", {"board_id": board_id, "fields": sorted(body.keys())})
    ctx["out"].emit(receipt)
    return 0


def cmd_boards_delete(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.id).strip()
    if not board_id:
        raise RuntimeError("--id is required")

    params = _param_ad_account_id(args)
    action = "boards.delete"
    ops = [
        write_operation(method="GET", path=f"/boards/{board_id}", params=params or None),
        write_operation(method="DELETE", path=f"/boards/{board_id}", params=params or None),
        write_operation(method="GET", path=f"/boards/{board_id}", params=params or None),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(
            action=action,
            operations=ops,
            acks_required=["ack-irreversible"],
            request={"board_id": board_id},
        )
        ctx["audit"].write("boards.delete.plan", {"board_id": board_id})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx, acks_required=["ack-irreversible"])
    before_resp = api.get_response(f"/boards/{board_id}", params=params or None, allowed_statuses=(404,))
    before = before_resp.json() if before_resp.status != 404 else None

    if before_resp.status == 404:
        receipt = build_receipt(
            action=action,
            changed=False,
            operations=ops,
            acks_required=["ack-irreversible"],
            request={"board_id": board_id},
            before=None,
            write_result={"skipped": "already_missing"},
            after=None,
        )
        ctx["audit"].write("boards.delete.apply", {"board_id": board_id, "changed": False})
        ctx["out"].emit(receipt)
        return 0

    _ = api.delete(f"/boards/{board_id}", params=params or None)
    after_resp = api.get_response(f"/boards/{board_id}", params=params or None, allowed_statuses=(404,))
    if after_resp.status != 404:
        raise RuntimeError("Verification failed: board still exists after delete")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        acks_required=["ack-irreversible"],
        request={"board_id": board_id},
        before=before,
        write_result={"deleted": True},
        after={"status": 404},
    )
    ctx["audit"].write("boards.delete.apply", {"board_id": board_id, "changed": True})
    ctx["out"].emit(receipt)
    return 0


def cmd_boards_ensure(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    name = str(args.name).strip()
    if not name:
        raise RuntimeError("--name is required")

    params = _param_ad_account_id(args)
    scan_limit = int(getattr(args, "scan_limit", 5000))
    if scan_limit < 1:
        raise RuntimeError("--scan-limit must be >= 1")

    desired: dict[str, Any] = {}
    if args.description is not None:
        desired["description"] = str(args.description)
    if args.privacy is not None:
        desired["privacy"] = str(args.privacy).strip()

    action = "boards.ensure"

    matches = _find_boards_by_name(api, name=name, params=params, scan_limit=scan_limit)
    if len(matches) > 1:
        raise RuntimeError(f"Refusing: multiple boards named {name!r} found; use boards update/delete by id.")

    if not matches:
        # Ensure missing -> create.
        ops = [
            write_operation(method="GET", path="/boards", params={**params, "limit": scan_limit}),
            write_operation(
                method="POST",
                path="/boards",
                params=params or None,
                json_body={"name": name, **desired, **({"is_ads_only": True} if bool(getattr(args, "is_ads_only", False)) else {})},
            ),
            write_operation(method="GET", path="/boards/{board_id}", params=params or None),
        ]
        if not bool(ctx.get("apply")):
            plan = build_plan(
                action=action,
                operations=ops,
                request={"name": name, **desired, "is_ads_only": bool(getattr(args, "is_ads_only", False))},
            )
            ctx["audit"].write("boards.ensure.plan", {"name": name, "mode": "create"})
            ctx["out"].emit(plan)
            return 0

        require_write_allowed(ctx)
        created = api.post(
            "/boards",
            json_body={
                "name": name,
                **desired,
                **({"is_ads_only": True} if bool(getattr(args, "is_ads_only", False)) else {}),
            },
            params=params or None,
        )
        board_id = str(created.get("id") or "").strip()
        if not board_id:
            raise RuntimeError("Unexpected create board response: missing id")
        after = api.get(f"/boards/{board_id}", params=params or None)
        if str(after.get("name") or "").strip() != name:
            raise RuntimeError("Verification failed: board name mismatch")

        receipt = build_receipt(
            action=action,
            changed=True,
            operations=ops,
            request={"name": name, **desired, "is_ads_only": bool(getattr(args, "is_ads_only", False))},
            before=None,
            write_result={"created": {"id": board_id}},
            after=after,
        )
        ctx["audit"].write("boards.ensure.apply", {"name": name, "board_id": board_id, "changed": True})
        ctx["out"].emit(receipt)
        return 0

    board_id = str(matches[0].get("id") or "").strip()
    if not board_id:
        raise RuntimeError(f"Unexpected board list item for {name!r}: missing id")

    before = api.get(f"/boards/{board_id}", params=params or None)
    patch_body = {k: v for k, v in desired.items() if str(before.get(k) or "") != str(v)}
    if patch_body:
        ops = [
            write_operation(method="GET", path=f"/boards/{board_id}", params=params or None),
            write_operation(method="PATCH", path=f"/boards/{board_id}", params=params or None, json_body=patch_body),
            write_operation(method="GET", path=f"/boards/{board_id}", params=params or None),
        ]
        if not bool(ctx.get("apply")):
            plan = build_plan(action=action, operations=ops, request={"board_id": board_id, **patch_body})
            ctx["audit"].write("boards.ensure.plan", {"name": name, "board_id": board_id, "mode": "update"})
            ctx["out"].emit(plan)
            return 0

        require_write_allowed(ctx)
        _ = api.patch(f"/boards/{board_id}", json_body=patch_body, params=params or None)
        after = api.get(f"/boards/{board_id}", params=params or None)
        for k, v in patch_body.items():
            if str(after.get(k) or "") != str(v):
                raise RuntimeError(f"Verification failed: {k} mismatch")
        receipt = build_receipt(
            action=action,
            changed=True,
            operations=ops,
            request={"board_id": board_id, **patch_body},
            before=before,
            write_result={"updated_fields": sorted(patch_body.keys())},
            after=after,
        )
        ctx["audit"].write("boards.ensure.apply", {"name": name, "board_id": board_id, "changed": True})
        ctx["out"].emit(receipt)
        return 0

    ops = [write_operation(method="GET", path=f"/boards/{board_id}", params=params or None)]
    if not bool(ctx.get("apply")):
        plan = build_plan(action=action, operations=ops, request={"board_id": board_id, "name": name})
        ctx["audit"].write("boards.ensure.plan", {"name": name, "board_id": board_id, "mode": "noop"})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx)
    receipt = build_receipt(
        action=action,
        changed=False,
        operations=ops,
        request={"board_id": board_id, "name": name},
        before=before,
        write_result={"skipped": "already_desired"},
        after=before,
    )
    ctx["audit"].write("boards.ensure.apply", {"name": name, "board_id": board_id, "changed": False})
    ctx["out"].emit(receipt)
    return 0


def cmd_board_sections_create(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.board_id).strip()
    if not board_id:
        raise RuntimeError("--board-id is required")
    name = str(args.name).strip()
    if not name:
        raise RuntimeError("--name is required")

    params = _param_ad_account_id(args)
    scan_limit = int(getattr(args, "scan_limit", 5000))
    if scan_limit < 1:
        raise RuntimeError("--scan-limit must be >= 1")

    action = "board_sections.create"
    ops = [
        write_operation(method="GET", path=f"/boards/{board_id}/sections", params={**params, "limit": scan_limit}),
        write_operation(method="POST", path=f"/boards/{board_id}/sections", params=params or None, json_body={"name": name}),
        write_operation(method="GET", path=f"/boards/{board_id}/sections", params={**params, "limit": scan_limit}),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(action=action, operations=ops, request={"board_id": board_id, "name": name})
        ctx["audit"].write("board_sections.create.plan", {"board_id": board_id, "name": name})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx)
    existing = _find_sections_by_name(api, board_id=board_id, name=name, params=params, scan_limit=scan_limit)
    if existing and not bool(getattr(args, "allow_mismatch", False)):
        raise RuntimeError(
            f"Refusing to create section {name!r}: a section with this name already exists on board {board_id}. "
            "Use `board-sections ensure` or pass --allow-mismatch to force a duplicate."
        )

    created = api.post(f"/boards/{board_id}/sections", json_body={"name": name}, params=params or None)
    section_id = str(created.get("id") or "").strip()
    if not section_id:
        raise RuntimeError("Unexpected create section response: missing id")
    # Verification: list sections and ensure the new id exists.
    sections, _, _ = api.list_all(f"/boards/{board_id}/sections", params=params, limit=scan_limit, page_size=100)
    created_sections = [s for s in sections if isinstance(s, dict) and str(s.get("id") or "") == section_id]
    if not created_sections:
        raise RuntimeError("Verification failed: section id not found after create")
    if str(created_sections[0].get("name") or "").strip() != name:
        raise RuntimeError("Verification failed: section name mismatch after create")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request={"board_id": board_id, "name": name},
        before={"existing_name_matches": [{"id": s.get("id"), "name": s.get("name")} for s in existing]},
        write_result={"created": {"id": section_id}},
        after={"count": len(sections), "items": [{"id": s.get("id"), "name": s.get("name")} for s in sections if isinstance(s, dict)]},
    )
    ctx["audit"].write(
        "board_sections.create.apply",
        {"board_id": board_id, "section_id": section_id, "name": name},
    )
    ctx["out"].emit(receipt)
    return 0


def cmd_board_sections_update(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.board_id).strip()
    section_id = str(args.section_id).strip()
    if not board_id:
        raise RuntimeError("--board-id is required")
    if not section_id:
        raise RuntimeError("--section-id is required")
    name = str(args.name).strip()
    if not name:
        raise RuntimeError("--name is required")

    params = _param_ad_account_id(args)
    action = "board_sections.update"
    ops = [
        write_operation(method="GET", path=f"/boards/{board_id}/sections", params=params or None),
        write_operation(
            method="PATCH",
            path=f"/boards/{board_id}/sections/{section_id}",
            params=params or None,
            json_body={"name": name},
        ),
        write_operation(method="GET", path=f"/boards/{board_id}/sections", params=params or None),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(action=action, operations=ops, request={"board_id": board_id, "section_id": section_id, "name": name})
        ctx["audit"].write("board_sections.update.plan", {"board_id": board_id, "section_id": section_id})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx)
    before_sections, _, _ = api.list_all(f"/boards/{board_id}/sections", params=params, limit=5000, page_size=100)
    _ = api.patch(
        f"/boards/{board_id}/sections/{section_id}",
        json_body={"name": name},
        params=params or None,
    )
    after_sections, _, _ = api.list_all(f"/boards/{board_id}/sections", params=params, limit=5000, page_size=100)
    updated = [s for s in after_sections if isinstance(s, dict) and str(s.get("id") or "") == section_id]
    if not updated:
        raise RuntimeError("Verification failed: section id not found after update")
    if str(updated[0].get("name") or "").strip() != name:
        raise RuntimeError("Verification failed: section name mismatch")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request={"board_id": board_id, "section_id": section_id, "name": name},
        before={"count": len(before_sections)},
        write_result={"updated": {"section_id": section_id}},
        after={"count": len(after_sections)},
    )
    ctx["audit"].write("board_sections.update.apply", {"board_id": board_id, "section_id": section_id})
    ctx["out"].emit(receipt)
    return 0


def cmd_board_sections_delete(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.board_id).strip()
    section_id = str(args.section_id).strip()
    if not board_id:
        raise RuntimeError("--board-id is required")
    if not section_id:
        raise RuntimeError("--section-id is required")

    params = _param_ad_account_id(args)
    action = "board_sections.delete"
    ops = [
        write_operation(method="GET", path=f"/boards/{board_id}/sections", params=params or None),
        write_operation(method="DELETE", path=f"/boards/{board_id}/sections/{section_id}", params=params or None),
        write_operation(method="GET", path=f"/boards/{board_id}/sections", params=params or None),
    ]

    if not bool(ctx.get("apply")):
        plan = build_plan(
            action=action,
            operations=ops,
            acks_required=["ack-irreversible"],
            request={"board_id": board_id, "section_id": section_id},
        )
        ctx["audit"].write("board_sections.delete.plan", {"board_id": board_id, "section_id": section_id})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx, acks_required=["ack-irreversible"])
    before_sections, _, _ = api.list_all(f"/boards/{board_id}/sections", params=params, limit=5000, page_size=100)
    exists_before = any(str(s.get("id") or "") == section_id for s in before_sections if isinstance(s, dict))
    if not exists_before:
        after_sections, _, _ = api.list_all(f"/boards/{board_id}/sections", params=params, limit=5000, page_size=100)
        receipt = build_receipt(
            action=action,
            changed=False,
            operations=ops,
            acks_required=["ack-irreversible"],
            request={"board_id": board_id, "section_id": section_id},
            before={"count": len(before_sections)},
            write_result={"skipped": "already_missing"},
            after={"count": len(after_sections)},
        )
        ctx["audit"].write(
            "board_sections.delete.apply",
            {"board_id": board_id, "section_id": section_id, "changed": False},
        )
        ctx["out"].emit(receipt)
        return 0

    _ = api.delete(f"/boards/{board_id}/sections/{section_id}", params=params or None)
    after_sections, _, _ = api.list_all(f"/boards/{board_id}/sections", params=params, limit=5000, page_size=100)
    if any(str(s.get("id") or "") == section_id for s in after_sections if isinstance(s, dict)):
        raise RuntimeError("Verification failed: section still exists after delete")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        acks_required=["ack-irreversible"],
        request={"board_id": board_id, "section_id": section_id},
        before={"count": len(before_sections)},
        write_result={"deleted": True},
        after={"count": len(after_sections)},
    )
    ctx["audit"].write("board_sections.delete.apply", {"board_id": board_id, "section_id": section_id, "changed": True})
    ctx["out"].emit(receipt)
    return 0


def cmd_board_sections_ensure(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.board_id).strip()
    if not board_id:
        raise RuntimeError("--board-id is required")
    name = str(args.name).strip()
    if not name:
        raise RuntimeError("--name is required")

    params = _param_ad_account_id(args)
    scan_limit = int(getattr(args, "scan_limit", 5000))
    if scan_limit < 1:
        raise RuntimeError("--scan-limit must be >= 1")

    action = "board_sections.ensure"
    matches = _find_sections_by_name(api, board_id=board_id, name=name, params=params, scan_limit=scan_limit)
    if len(matches) > 1:
        raise RuntimeError(f"Refusing: multiple sections named {name!r} found on board {board_id}; use update/delete by id.")

    if matches:
        section_id = str(matches[0].get("id") or "").strip()
        ops = [write_operation(method="GET", path=f"/boards/{board_id}/sections", params={**params, "limit": scan_limit})]
        if not bool(ctx.get("apply")):
            plan = build_plan(action=action, operations=ops, request={"board_id": board_id, "section_id": section_id, "name": name})
            ctx["audit"].write("board_sections.ensure.plan", {"board_id": board_id, "section_id": section_id, "mode": "noop"})
            ctx["out"].emit(plan)
            return 0

        require_write_allowed(ctx)
        receipt = build_receipt(
            action=action,
            changed=False,
            operations=ops,
            request={"board_id": board_id, "section_id": section_id, "name": name},
            before={"matched": {"id": section_id, "name": name}},
            write_result={"skipped": "already_exists"},
            after={"matched": {"id": section_id, "name": name}},
        )
        ctx["audit"].write("board_sections.ensure.apply", {"board_id": board_id, "section_id": section_id, "changed": False})
        ctx["out"].emit(receipt)
        return 0

    ops = [
        write_operation(method="GET", path=f"/boards/{board_id}/sections", params={**params, "limit": scan_limit}),
        write_operation(method="POST", path=f"/boards/{board_id}/sections", params=params or None, json_body={"name": name}),
        write_operation(method="GET", path=f"/boards/{board_id}/sections", params={**params, "limit": scan_limit}),
    ]
    if not bool(ctx.get("apply")):
        plan = build_plan(action=action, operations=ops, request={"board_id": board_id, "name": name})
        ctx["audit"].write("board_sections.ensure.plan", {"board_id": board_id, "name": name, "mode": "create"})
        ctx["out"].emit(plan)
        return 0

    require_write_allowed(ctx)
    created = api.post(f"/boards/{board_id}/sections", json_body={"name": name}, params=params or None)
    section_id = str(created.get("id") or "").strip()
    if not section_id:
        raise RuntimeError("Unexpected create section response: missing id")
    after_sections, _, _ = api.list_all(f"/boards/{board_id}/sections", params=params, limit=scan_limit, page_size=100)
    created_sections = [s for s in after_sections if isinstance(s, dict) and str(s.get("id") or "") == section_id]
    if not created_sections:
        raise RuntimeError("Verification failed: section id not found after create")
    if str(created_sections[0].get("name") or "").strip() != name:
        raise RuntimeError("Verification failed: section name mismatch after create")

    receipt = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request={"board_id": board_id, "name": name},
        before=None,
        write_result={"created": {"id": section_id}},
        after={"count": len(after_sections)},
    )
    ctx["audit"].write("board_sections.ensure.apply", {"board_id": board_id, "section_id": section_id, "changed": True})
    ctx["out"].emit(receipt)
    return 0


def cmd_boards_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    params: dict[str, Any] = {}
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()
    if args.privacy:
        params["privacy"] = str(args.privacy).strip()

    items, bookmark, pages = api.list_all(
        "/boards",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {"ok": True, "count": len(items), "pages": pages, "bookmark": bookmark, "items": items}
    ctx["audit"].write("boards.list", {"count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_boards_get(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.id).strip()
    if not board_id:
        raise RuntimeError("--id is required")
    params: dict[str, Any] = {}
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()
    data = api.get(f"/boards/{board_id}", params=params or None)
    out = {"ok": True, "board": data}
    ctx["audit"].write("boards.get", {"board_id": board_id})
    ctx["out"].emit(out)
    return 0


def cmd_board_sections_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.board_id).strip()
    if not board_id:
        raise RuntimeError("--board-id is required")
    params: dict[str, Any] = {}
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()

    items, bookmark, pages = api.list_all(
        f"/boards/{board_id}/sections",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "board_id": board_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write("board_sections.list", {"board_id": board_id, "count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_board_pins_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    board_id = str(args.board_id).strip()
    if not board_id:
        raise RuntimeError("--board-id is required")

    params: dict[str, Any] = {}
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()

    if args.section_id:
        # When listing by section, Pinterest uses a distinct endpoint (section_id is a path param).
        section_id = str(args.section_id).strip()
        if not section_id:
            raise RuntimeError("--section-id must not be empty")
        if args.creative_types or args.pin_metrics:
            raise RuntimeError("--creative-types/--pin-metrics are only supported when listing pins for a whole board")

        items, bookmark, pages = api.list_all(
            f"/boards/{board_id}/sections/{section_id}/pins",
            params=params,
            limit=int(args.limit),
            page_size=int(args.page_size),
            bookmark=(str(args.bookmark).strip() if args.bookmark else None),
        )
        out = {
            "ok": True,
            "board_id": board_id,
            "section_id": section_id,
            "count": len(items),
            "pages": pages,
            "bookmark": bookmark,
            "items": items,
        }
        ctx["audit"].write(
            "boards.section_pins_list",
            {"board_id": board_id, "section_id": section_id, "count": out["count"], "pages": pages},
        )
        ctx["out"].emit(out)
        return 0

    if args.creative_types:
        creative_types = [s.strip().upper() for s in str(args.creative_types).split(",") if s.strip()]
        if creative_types:
            params["creative_types"] = creative_types
    if args.pin_metrics:
        params["pin_metrics"] = True

    items, bookmark, pages = api.list_all(
        f"/boards/{board_id}/pins",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "board_id": board_id,
        "section_id": None,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write(
        "boards.pins_list",
        {"board_id": board_id, "section_id": None, "count": out["count"], "pages": pages},
    )
    ctx["out"].emit(out)
    return 0
