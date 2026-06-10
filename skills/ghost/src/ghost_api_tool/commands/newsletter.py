from __future__ import annotations

import time
from typing import Any

from ..runtime import get_api
from ..errors import SafetyError


def add_newsletter_commands(newsletter_sub) -> None:
    nl_list = newsletter_sub.add_parser("list", help="List newsletters")
    nl_list.add_argument("--limit", type=int, default=50)
    nl_list.add_argument("--page", type=int, default=None)
    nl_list.add_argument("--fields", default=None)
    nl_list.set_defaults(func=cmd_newsletter_list)

    nl_get = newsletter_sub.add_parser("get", help="Get a newsletter by id")
    nl_get.add_argument("--id", required=True)
    nl_get.set_defaults(func=cmd_newsletter_get)

    nl_create = newsletter_sub.add_parser("create", help="Create a newsletter (dry-run by default)")
    nl_create.add_argument("--name", required=True)
    nl_create.add_argument("--slug", default=None, help="Optional slug (Ghost may ignore/override)")
    nl_create.add_argument("--description", default=None)
    nl_create.add_argument("--sender-reply-to", choices=("newsletter", "support"), default=None)
    nl_create.add_argument("--subscribe-on-signup", type=str, default=None, help="true|false")
    nl_create.add_argument("--opt-in-existing", action="store_true", help="Subscribe existing members")
    nl_create.set_defaults(func=cmd_newsletter_create)

    nl_update = newsletter_sub.add_parser("update", help="Update newsletter fields (dry-run by default)")
    nl_update.add_argument("--id", required=True)
    nl_update.add_argument("--name", default=None)
    nl_update.add_argument("--description", default=None)
    nl_update.add_argument("--sender-name", default=None)
    nl_update.add_argument("--sender-email", default=None, help="Requires email validation click")
    nl_update.add_argument("--sender-reply-to", choices=("newsletter", "support"), default=None)
    nl_update.add_argument("--subscribe-on-signup", type=str, default=None, help="true|false")
    nl_update.add_argument("--show-feature-image", type=str, default=None, help="true|false")
    nl_update.add_argument("--show-badge", type=str, default=None, help="true|false")
    nl_update.set_defaults(func=cmd_newsletter_update)


def _parse_boolish(value: str | None) -> bool | None:
    if value is None:
        return None
    s = value.strip().lower()
    if s in ("true", "1", "yes", "y", "on"):
        return True
    if s in ("false", "0", "no", "n", "off"):
        return False
    raise RuntimeError(f"Invalid boolean value: {value!r} (expected true/false)")


def cmd_newsletter_list(args, ctx) -> int:
    api = get_api(ctx)
    params: dict[str, Any] = {"limit": args.limit}
    if args.page is not None:
        params["page"] = args.page
    if args.fields:
        params["fields"] = args.fields
    res = api.newsletters_browse(params=params)
    ctx["out"].print(res)
    return 0


def cmd_newsletter_get(args, ctx) -> int:
    api = get_api(ctx)
    res = api.newsletters_read_by_id(args.id)
    ctx["out"].print(res)
    return 0


def cmd_newsletter_create(args, ctx) -> int:
    newsletter: dict[str, Any] = {"name": args.name}
    if args.description is not None:
        newsletter["description"] = args.description
    if args.slug is not None:
        newsletter["slug"] = args.slug
    if args.sender_reply_to is not None:
        newsletter["sender_reply_to"] = args.sender_reply_to
    val = _parse_boolish(args.subscribe_on_signup)
    if val is not None:
        newsletter["subscribe_on_signup"] = val

    if not ctx["apply"]:
        ctx["out"].print({"apply": False, "refused": False, "create": newsletter, "opt_in_existing": bool(args.opt_in_existing)})
        return 0
    if not ctx["yes"]:
        raise SafetyError("Refused: newsletter create requires --yes")
    api = get_api(ctx)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-newsletter.create"
        backup.write_before_after(
            kind="newsletter",
            resource_id=f"name:{args.name}",
            slug=str(args.slug or ""),
            action="newsletter.create",
            before=None,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "create": newsletter, "opt_in_existing": bool(args.opt_in_existing)},
        )

    params = {"opt_in_existing": "true"} if args.opt_in_existing else None
    res = api.newsletters_create({"newsletters": [newsletter]}, params=params)
    created = (res.get("newsletters") or [{}])[0]
    newsletter_id = created.get("id") if isinstance(created, dict) else None
    verified = None
    if isinstance(newsletter_id, str) and newsletter_id:
        verified = api.newsletters_read_by_id(newsletter_id)
    ctx["audit"].write("newsletter.create", {"apply": True, "name": args.name})
    if backup is not None:
        backup.write_before_after(
            kind="newsletter",
            resource_id=f"id:{newsletter_id}" if isinstance(newsletter_id, str) else f"name:{args.name}",
            slug=str(created.get("slug") if isinstance(created, dict) else args.slug or ""),
            action="newsletter.create",
            before=None,
            after=verified or res,
            meta={"stage": "after", "correlation_id": correlation_id},
        )
    ctx["out"].print(verified or res)
    return 0


def cmd_newsletter_update(args, ctx) -> int:
    api = get_api(ctx)
    current = api.newsletters_read_by_id(args.id)

    newsletters = current.get("newsletters") or []
    if not isinstance(newsletters, list) or not newsletters or not isinstance(newsletters[0], dict):
        raise RuntimeError(f"Newsletter not found: {args.id}")
    cur = newsletters[0]

    patch: dict[str, Any] = {}
    if args.name is not None:
        patch["name"] = args.name
    if args.description is not None:
        patch["description"] = args.description
    if args.sender_name is not None:
        patch["sender_name"] = args.sender_name
    if args.sender_email is not None:
        patch["sender_email"] = args.sender_email
    if args.sender_reply_to is not None:
        patch["sender_reply_to"] = args.sender_reply_to
    b = _parse_boolish(args.subscribe_on_signup)
    if b is not None:
        patch["subscribe_on_signup"] = b
    b = _parse_boolish(args.show_feature_image)
    if b is not None:
        patch["show_feature_image"] = b
    b = _parse_boolish(args.show_badge)
    if b is not None:
        patch["show_badge"] = b

    if not patch:
        ctx["out"].print({"apply": ctx["apply"], "refused": False, "reasons": [], "note": "No changes requested"})
        return 0

    if not ctx["apply"]:
        backup = ctx.get("backup")
        if backup is not None:
            correlation_id = f"{int(time.time() * 1000)}-id-{args.id}-newsletter.update"
            backup.write_before_after(
                kind="newsletter",
                resource_id=f"id:{args.id}",
                slug=str(cur.get("slug") or ""),
                action="newsletter.update",
                before=current,
                after=None,
                meta={
                    "stage": "before",
                    "correlation_id": correlation_id,
                    "patch_fields": sorted(patch.keys()),
                },
            )
        ctx["out"].print({"apply": False, "refused": False, "newsletter_id": args.id, "planned": {"fields": sorted(patch.keys())}})
        return 0
    if not ctx["yes"]:
        raise SafetyError("Refused: newsletter update requires --yes")

    payload = {"newsletters": [{**patch, "id": args.id, "updated_at": cur.get("updated_at")}]}

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-id-{args.id}-newsletter.update"
        backup.write_before_after(
            kind="newsletter",
            resource_id=f"id:{args.id}",
            slug=str(cur.get("slug") or ""),
            action="newsletter.update",
            before=current,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "patch_fields": sorted(patch.keys())},
        )

    res = api.newsletters_update(args.id, payload)
    verified = api.newsletters_read_by_id(args.id)
    ctx["audit"].write("newsletter.update", {"apply": True, "newsletter_id": args.id, "fields": sorted(patch.keys())})
    if backup is not None:
        backup.write_before_after(
            kind="newsletter",
            resource_id=f"id:{args.id}",
            slug=str(cur.get("slug") or ""),
            action="newsletter.update",
            before=current,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id, "patch_fields": sorted(patch.keys())},
        )

    # Verify requested fields.
    v_list = verified.get("newsletters") or []
    v = v_list[0] if isinstance(v_list, list) and v_list and isinstance(v_list[0], dict) else {}
    for key, value in patch.items():
        if key == "sender_email":
            # Sender email is applied only after validation; accept pending state.
            continue
        if v.get(key) != value:
            raise RuntimeError(f"Verification failed: {key} mismatch")

    ctx["out"].print({"ok": True, "newsletter_id": args.id, "updated_fields": sorted(patch.keys())})
    return 0
