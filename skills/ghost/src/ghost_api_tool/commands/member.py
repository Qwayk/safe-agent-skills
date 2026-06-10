from __future__ import annotations

import time
from typing import Any

from ..errors import SafetyError
from ..member_utils import MemberCsvRow, merge_labels, read_member_csv, redact_email, slugify_label
from ..runtime import get_api


def add_member_commands(member_sub) -> None:
    member_list = member_sub.add_parser("list", help="Browse members (emails redacted by default)")
    member_list.add_argument("--filter", default=None, help="NQL filter (e.g. label:test)")
    member_list.add_argument("--limit", type=int, default=15)
    member_list.add_argument("--page", type=int, default=None)
    member_list.add_argument("--order", default=None)
    member_list.add_argument("--fields", default=None)
    member_list.add_argument("--include", default="labels,newsletters")
    member_list.add_argument("--include-emails", action="store_true", help="Include raw emails in output (unsafe)")
    member_list.add_argument("--raw", action="store_true", help="Output raw API payload (unsafe; includes PII)")
    member_list.set_defaults(func=cmd_member_list)

    member_count = member_sub.add_parser("count", help="Count members matching a filter")
    member_count.add_argument("--filter", default=None, help="NQL filter (e.g. status:free)")
    member_count.set_defaults(func=cmd_member_count)

    member_get = member_sub.add_parser("get", help="Fetch a member by id (emails redacted by default)")
    member_get.add_argument("--id", required=True)
    member_get.add_argument("--include", default="labels,newsletters")
    member_get.add_argument("--include-emails", action="store_true", help="Include raw emails in output (unsafe)")
    member_get.add_argument("--raw", action="store_true", help="Output raw API payload (unsafe; includes PII)")
    member_get.set_defaults(func=cmd_member_get)

    member_create = member_sub.add_parser("create", help="Create a member (dry-run by default)")
    member_create.add_argument("--email", required=True)
    member_create.add_argument("--name", default=None)
    member_create.add_argument("--note", default=None)
    member_create.add_argument("--label", action="append", default=[], help="Label to add (repeatable)")
    member_create.add_argument("--newsletter", action="append", default=[], help="Newsletter slug or id (repeatable)")
    member_create.set_defaults(func=cmd_member_create)

    member_update = member_sub.add_parser("update", help="Update member fields/labels/newsletters (dry-run by default)")
    member_update.add_argument("--id", required=True)
    member_update.add_argument("--set-name", default=None)
    member_update.add_argument("--set-note", default=None)
    member_update.add_argument("--add-label", action="append", default=[], help="Add label (repeatable)")
    member_update.add_argument("--remove-label", action="append", default=[], help="Remove label (repeatable)")
    member_update.add_argument("--replace-labels", default=None, help="Replace labels (comma/; or | separated)")
    member_update.add_argument("--subscribe-newsletter", action="append", default=[], help="Subscribe to newsletter slug/id")
    member_update.add_argument("--unsubscribe-newsletter", action="append", default=[], help="Unsubscribe from newsletter slug/id")
    member_update.set_defaults(func=cmd_member_update)

    member_import = member_sub.add_parser("import", help="Import members from CSV (dry-run by default)")
    member_import.add_argument("--csv", required=True, help="CSV path (must include email column)")
    member_import.add_argument("--default-label", action="append", default=[], help="Label(s) applied to all rows")
    member_import.add_argument(
        "--default-newsletter",
        action="append",
        default=[],
        help="Newsletter slug/id subscribed for all rows (repeatable)",
    )
    member_import.add_argument("--mode", choices=("create-only", "upsert"), default="create-only")
    member_import.add_argument(
        "--sleep-ms",
        type=int,
        default=0,
        help="Sleep between API calls (ms). Useful for large imports (default: 0)",
    )
    member_import.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing after an error (default: stop at first error)",
    )
    member_import.set_defaults(func=cmd_member_import)

    member_export = member_sub.add_parser("export-engagement", help="Export member engagement fields to CSV")
    member_export.add_argument("--out", required=True, help="Output CSV path")
    member_export.add_argument("--filter", default=None, help="NQL filter (optional)")
    member_export.add_argument("--include-emails", action="store_true", help="Include raw emails in CSV (unsafe)")
    member_export.add_argument("--limit", type=int, default=100, help="Page size (default: 100)")
    member_export.add_argument("--max-pages", type=int, default=500, help="Max pages to fetch (default: 500)")
    member_export.set_defaults(func=cmd_member_export_engagement)


def _should_retry_error(msg: str) -> bool:
    # HttpClient raises RuntimeError("HTTP {code} for ...") on non-2xx.
    return msg.startswith("HTTP 429") or msg.startswith("HTTP 5") or msg.startswith("HTTP 408")


def _call_with_retries(fn, *, max_attempts: int = 4) -> Any:
    attempt = 0
    while True:
        attempt += 1
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if attempt >= max_attempts or not _should_retry_error(msg):
                raise
            time.sleep(min(2**attempt, 10))


def _resolve_newsletter_ids(api, refs: list[str]) -> list[str]:
    wanted = [r.strip() for r in refs if r and r.strip()]
    if not wanted:
        return []
    # If it looks like an id (hex), keep it. Otherwise treat as slug.
    ids: list[str] = []
    slugs: list[str] = []
    for r in wanted:
        if len(r) >= 12 and all(c in "0123456789abcdef" for c in r.lower()):
            ids.append(r)
        else:
            slugs.append(r)
    if not slugs:
        return ids
    res = api.newsletters_browse(params={"limit": 100})
    newsletters = res.get("newsletters") or []
    slug_to_id: dict[str, str] = {}
    for n in newsletters:
        if isinstance(n, dict) and isinstance(n.get("slug"), str) and isinstance(n.get("id"), str):
            slug_to_id[n["slug"]] = n["id"]
    for slug in slugs:
        nid = slug_to_id.get(slug)
        if not nid:
            raise RuntimeError(f"Unknown newsletter slug: {slug}")
        ids.append(nid)
    # Deduplicate while preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for nid in ids:
        if nid in seen:
            continue
        seen.add(nid)
        out.append(nid)
    return out


def _redact_member(member: dict[str, Any]) -> dict[str, Any]:
    out = dict(member)
    email = out.get("email")
    if isinstance(email, str):
        out["email"] = redact_email(email)
    return out


def _prefetch_newsletter_slug_map(api) -> dict[str, str]:
    res = _call_with_retries(lambda: api.newsletters_browse(params={"limit": 100}))
    newsletters = res.get("newsletters") or []
    slug_to_id: dict[str, str] = {}
    if isinstance(newsletters, list):
        for n in newsletters:
            if isinstance(n, dict) and isinstance(n.get("slug"), str) and isinstance(n.get("id"), str):
                slug_to_id[n["slug"]] = n["id"]
    return slug_to_id


def _resolve_newsletter_ids_cached(*, refs: list[str], slug_to_id: dict[str, str]) -> list[str]:
    wanted = [r.strip() for r in refs if r and r.strip()]
    if not wanted:
        return []
    ids: list[str] = []
    for r in wanted:
        if len(r) >= 12 and all(c in "0123456789abcdef" for c in r.lower()):
            ids.append(r)
        else:
            nid = slug_to_id.get(r)
            if not nid:
                raise RuntimeError(f"Unknown newsletter slug: {r}")
            ids.append(nid)
    seen: set[str] = set()
    out: list[str] = []
    for nid in ids:
        if nid in seen:
            continue
        seen.add(nid)
        out.append(nid)
    return out


def _summarize_member(member: dict[str, Any], *, include_email: bool) -> dict[str, Any]:
    email = member.get("email") if isinstance(member.get("email"), str) else ""
    labels = member.get("labels") if isinstance(member.get("labels"), list) else []
    label_slugs: list[str] = []
    for lab in labels:
        if isinstance(lab, dict) and isinstance(lab.get("slug"), str):
            label_slugs.append(lab["slug"])
    newsletters = member.get("newsletters") if isinstance(member.get("newsletters"), list) else []
    newsletter_ids: list[str] = []
    for nl in newsletters:
        if isinstance(nl, dict) and isinstance(nl.get("id"), str):
            newsletter_ids.append(nl.get("slug") if isinstance(nl.get("slug"), str) else nl["id"])
    return {
        "id": member.get("id"),
        "uuid": member.get("uuid"),
        "email": email if include_email else redact_email(email),
        "name": member.get("name"),
        "status": member.get("status"),
        "labels": sorted(set(label_slugs)),
        "newsletters": sorted(set(newsletter_ids)),
        "email_count": member.get("email_count"),
        "email_opened_count": member.get("email_opened_count"),
        "email_open_rate": member.get("email_open_rate"),
        "last_seen_at": member.get("last_seen_at"),
        "created_at": member.get("created_at"),
        "updated_at": member.get("updated_at"),
        "email_suppression": member.get("email_suppression"),
        "subscribed": member.get("subscribed"),
    }


def cmd_member_list(args, ctx) -> int:
    api = get_api(ctx)
    params: dict[str, Any] = {"limit": args.limit, "include": args.include}
    if args.filter and args.filter.strip().lower() != "all":
        params["filter"] = args.filter
    if args.page is not None:
        params["page"] = args.page
    if args.order:
        params["order"] = args.order
    if args.fields:
        params["fields"] = args.fields
    res = _call_with_retries(lambda: api.members_browse(params=params))
    if args.raw:
        ctx["out"].print(res)
        return 0
    members = res.get("members") or []
    meta = res.get("meta")
    summarized: list[dict[str, Any]] = []
    if isinstance(members, list):
        for m in members:
            if isinstance(m, dict):
                summarized.append(_summarize_member(m, include_email=bool(args.include_emails)))
    ctx["out"].print({"members": summarized, "meta": meta})
    return 0


def cmd_member_count(args, ctx) -> int:
    api = get_api(ctx)
    params: dict[str, Any] = {"limit": 1}
    if args.filter and args.filter.strip().lower() != "all":
        params["filter"] = args.filter
    res = _call_with_retries(lambda: api.members_browse(params=params))
    total = None
    meta = res.get("meta") if isinstance(res, dict) else None
    pagination = meta.get("pagination") if isinstance(meta, dict) else None
    if isinstance(pagination, dict):
        total = pagination.get("total")
    ctx["out"].print({"filter": args.filter, "total": total})
    return 0


def cmd_member_get(args, ctx) -> int:
    api = get_api(ctx)
    res = _call_with_retries(
        lambda: api.members_read_by_id(args.id, params={"include": args.include} if args.include else None)
    )
    if args.raw:
        ctx["out"].print(res)
        return 0
    members = res.get("members") or []
    summarized: list[dict[str, Any]] = []
    if isinstance(members, list):
        for m in members:
            if isinstance(m, dict):
                summarized.append(_summarize_member(m, include_email=bool(args.include_emails)))
    ctx["out"].print({"members": summarized})
    return 0


def cmd_member_create(args, ctx) -> int:
    api = get_api(ctx)
    member: dict[str, Any] = {"email": args.email.strip()}
    if args.name:
        member["name"] = args.name
    if args.note:
        member["note"] = args.note
    if args.label:
        member["labels"] = [{"name": l.strip(), "slug": slugify_label(l)} for l in args.label if l.strip()]
    if args.newsletter:
        newsletter_ids = _call_with_retries(lambda: _resolve_newsletter_ids(api, args.newsletter))
        member["newsletters"] = [{"id": nid} for nid in newsletter_ids]

    if not ctx["apply"]:
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "create": {
                    "email": redact_email(member["email"]),
                    "name": member.get("name"),
                    "note": bool(member.get("note")),
                    "labels": [slugify_label(l) for l in args.label if l.strip()],
                    "newsletters": args.newsletter,
                },
            }
        )
        return 0
    if not ctx["yes"]:
        raise SafetyError("Refused: member create requires --yes")

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-email-{slugify_label(member['email'])}-member.create"
        backup.write_before_after(
            kind="member",
            resource_id=f"email:{redact_email(member['email'])}",
            slug="",
            action="member.create",
            before=None,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "email": redact_email(member["email"]),
                "labels": [slugify_label(l) for l in args.label if l.strip()],
                "newsletters": args.newsletter,
            },
        )

    res = _call_with_retries(lambda: api.members_create({"members": [member]}))
    created = (res.get("members") or [{}])[0]
    member_id = created.get("id")
    if not isinstance(member_id, str) or not member_id:
        raise RuntimeError(f"Unexpected create response (missing id): {res}")
    verified = _call_with_retries(lambda: api.members_read_by_id(member_id, params={"include": "labels,newsletters"}))
    ctx["audit"].write("member.create", {"apply": True, "member_id": member_id})
    if backup is not None:
        backup.write_before_after(
            kind="member",
            resource_id=f"id:{member_id}",
            slug="",
            action="member.create",
            before=None,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id},
        )
    members = verified.get("members") or []
    if isinstance(members, list) and members and isinstance(members[0], dict):
        ctx["out"].print({"members": [_summarize_member(members[0], include_email=False)]})
    else:
        ctx["out"].print({"ok": True, "member_id": member_id})
    return 0


def cmd_member_update(args, ctx) -> int:
    api = get_api(ctx)
    current_res = _call_with_retries(lambda: api.members_read_by_id(args.id, params={"include": "labels,newsletters"}))
    members = current_res.get("members") or []
    if not isinstance(members, list) or not members or not isinstance(members[0], dict):
        raise RuntimeError(f"Member not found: {args.id}")
    current = members[0]

    patch: dict[str, Any] = {}
    if args.set_name is not None:
        patch["name"] = args.set_name
    if args.set_note is not None:
        patch["note"] = args.set_note

    replace_labels = None
    if args.replace_labels is not None:
        replace_labels = [s.strip() for s in args.replace_labels.replace("|", ",").replace(";", ",").split(",") if s.strip()]
    if args.add_label or args.remove_label or replace_labels is not None:
        patch["labels"] = merge_labels(
            existing=current.get("labels"),
            add=args.add_label or [],
            remove=args.remove_label or [],
            replace=replace_labels,
        )

    # Newsletters are stored as relation objects; we manage by id only.
    if args.subscribe_newsletter or args.unsubscribe_newsletter:
        wanted_add = _resolve_newsletter_ids(api, args.subscribe_newsletter or [])
        wanted_remove = set(_resolve_newsletter_ids(api, args.unsubscribe_newsletter or []))
        existing = current.get("newsletters")
        existing_ids: list[str] = []
        if isinstance(existing, list):
            for n in existing:
                if isinstance(n, dict) and isinstance(n.get("id"), str):
                    existing_ids.append(n["id"])
        next_ids: list[str] = [nid for nid in existing_ids if nid not in wanted_remove]
        for nid in wanted_add:
            if nid not in next_ids:
                next_ids.append(nid)
        patch["newsletters"] = [{"id": nid} for nid in next_ids]

    if not patch:
        ctx["out"].print({"apply": ctx["apply"], "refused": False, "reasons": [], "note": "No changes requested"})
        return 0

    if not ctx["apply"]:
        backup = ctx.get("backup")
        if backup is not None:
            correlation_id = f"{int(time.time() * 1000)}-id-{args.id}-member.update"
            backup.write_before_after(
                kind="member",
                resource_id=f"id:{args.id}",
                slug="",
                action="member.update",
                before=current_res,
                after=None,
                meta={
                    "stage": "before",
                    "correlation_id": correlation_id,
                    "patch_fields": sorted(patch.keys()),
                },
            )
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "member_id": args.id,
                "planned": {"fields": sorted(patch.keys())},
                "member": _summarize_member(current, include_email=False),
            }
        )
        return 0

    if not ctx["yes"]:
        raise SafetyError("Refused: member update requires --yes")

    # Ghost requires updated_at to avoid edit conflicts.
    payload = {"members": [{**patch, "id": args.id, "updated_at": current.get("updated_at")}]}

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-id-{args.id}-member.update"
        backup.write_before_after(
            kind="member",
            resource_id=f"id:{args.id}",
            slug="",
            action="member.update",
            before=current_res,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "patch_fields": sorted(patch.keys())},
        )

    res = _call_with_retries(lambda: api.members_update(args.id, payload))
    verified = _call_with_retries(lambda: api.members_read_by_id(args.id, params={"include": "labels,newsletters"}))
    ctx["audit"].write("member.update", {"apply": True, "member_id": args.id, "fields": sorted(patch.keys())})
    if backup is not None:
        backup.write_before_after(
            kind="member",
            resource_id=f"id:{args.id}",
            slug="",
            action="member.update",
            before=current_res,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id, "patch_fields": sorted(patch.keys())},
        )

    members2 = verified.get("members") or []
    if isinstance(members2, list) and members2 and isinstance(members2[0], dict):
        verified_member = members2[0]
        if "name" in patch and verified_member.get("name") != patch.get("name"):
            raise RuntimeError("Verification failed: name mismatch")
        if "note" in patch and verified_member.get("note") != patch.get("note"):
            raise RuntimeError("Verification failed: note mismatch")
        if "labels" in patch:
            want = set()
            for lab in patch.get("labels") or []:
                if isinstance(lab, dict) and isinstance(lab.get("slug"), str):
                    want.add(lab["slug"])
            got = set()
            for lab in (verified_member.get("labels") or []):
                if isinstance(lab, dict) and isinstance(lab.get("slug"), str):
                    got.add(lab["slug"])
            if want != got:
                raise RuntimeError("Verification failed: labels mismatch")
        if "newsletters" in patch:
            want = set()
            for nl in patch.get("newsletters") or []:
                if isinstance(nl, dict) and isinstance(nl.get("id"), str):
                    want.add(nl["id"])
            got = set()
            for nl in (verified_member.get("newsletters") or []):
                if isinstance(nl, dict) and isinstance(nl.get("id"), str):
                    got.add(nl["id"])
            if want != got:
                raise RuntimeError("Verification failed: newsletters mismatch")

    # Redact emails in output.
    members_out = verified.get("members") or []
    if isinstance(members_out, list) and members_out and isinstance(members_out[0], dict):
        ctx["out"].print({"members": [_summarize_member(members_out[0], include_email=False)]})
    else:
        ctx["out"].print({"ok": True, "member_id": args.id})
    return 0


def cmd_member_import(args, ctx) -> int:
    rows: list[MemberCsvRow] = read_member_csv(args.csv)
    default_labels = args.default_label or []
    default_newsletters = args.default_newsletter or []

    if args.sleep_ms < 0 or args.sleep_ms > 60_000:
        raise RuntimeError("--sleep-ms must be between 0 and 60000")

    if not ctx["apply"]:
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "mode": args.mode,
                "rows": len(rows),
                "default_labels": default_labels,
                "default_newsletters": default_newsletters,
                "sleep_ms": int(args.sleep_ms),
                "note": "Dry-run: no changes applied; output omits emails",
            }
        )
        return 0

    if not ctx["yes"]:
        raise SafetyError("Refused: member import requires --yes")

    api = get_api(ctx)
    slug_to_id = _prefetch_newsletter_slug_map(api)
    newsletter_ids_default = _resolve_newsletter_ids_cached(refs=default_newsletters, slug_to_id=slug_to_id)

    existing_by_email: dict[str, str] = {}
    if args.mode == "upsert":
        page = 1
        while True:
            res = _call_with_retries(lambda: api.members_browse(params={"limit": 100, "page": page, "fields": "id,email"}))
            members = res.get("members") or []
            if not isinstance(members, list):
                break
            for m in members:
                if not isinstance(m, dict):
                    continue
                email = m.get("email")
                mid = m.get("id")
                if isinstance(email, str) and isinstance(mid, str) and email and mid:
                    existing_by_email[email.lower()] = mid
            meta = res.get("meta") if isinstance(res, dict) else None
            pagination = meta.get("pagination") if isinstance(meta, dict) else None
            pages = pagination.get("pages") if isinstance(pagination, dict) else None
            if not isinstance(pages, int) or page >= pages:
                break
            page += 1

    created = 0
    updated = 0
    errors: list[dict[str, Any]] = []

    def verify_member_state(member_id: str, *, want_label_slugs: set[str], want_newsletter_ids: set[str]) -> None:
        verified = _call_with_retries(lambda: api.members_read_by_id(member_id, params={"include": "labels,newsletters"}))
        members = verified.get("members") or []
        if not isinstance(members, list) or not members or not isinstance(members[0], dict):
            raise RuntimeError("Verification failed: member read returned empty")
        m = members[0]
        got_labels: set[str] = set()
        for lab in (m.get("labels") or []):
            if isinstance(lab, dict) and isinstance(lab.get("slug"), str):
                got_labels.add(lab["slug"])
        got_news: set[str] = set()
        for nl in (m.get("newsletters") or []):
            if isinstance(nl, dict) and isinstance(nl.get("id"), str):
                got_news.add(nl["id"])
        # Labels/newsletters are sets: order doesn't matter.
        if want_label_slugs and want_label_slugs != got_labels:
            raise RuntimeError("Verification failed: labels mismatch")
        if want_newsletter_ids and want_newsletter_ids != got_news:
            raise RuntimeError("Verification failed: newsletters mismatch")
    def sleep_if_needed() -> None:
        if int(args.sleep_ms) > 0:
            time.sleep(int(args.sleep_ms) / 1000.0)

    for row in rows:
        try:
            target_email = row.email.strip()
            if not target_email:
                continue
            labels = [*default_labels, *row.labels]
            newsletters = [*newsletter_ids_default]
            if row.newsletters:
                newsletters.extend(_resolve_newsletter_ids_cached(refs=row.newsletters, slug_to_id=slug_to_id))
            # Deduplicate newsletters
            seen_n: set[str] = set()
            newsletters = [nid for nid in newsletters if not (nid in seen_n or seen_n.add(nid))]

            if args.mode == "upsert":
                existing_id = existing_by_email.get(target_email.lower())
            else:
                existing_id = None

            if existing_id:
                current_res = _call_with_retries(
                    lambda: api.members_read_by_id(existing_id, params={"include": "labels,newsletters"})
                )
                cur_members = current_res.get("members") or []
                if not isinstance(cur_members, list) or not cur_members or not isinstance(cur_members[0], dict):
                    raise RuntimeError(f"Member not found by id: {existing_id}")
                current = cur_members[0]
                patch: dict[str, Any] = {"updated_at": current.get("updated_at")}
                if row.name:
                    patch["name"] = row.name
                if row.note:
                    patch["note"] = row.note
                if labels:
                    patch["labels"] = merge_labels(existing=current.get("labels"), add=labels)
                if newsletters:
                    existing_news = current.get("newsletters")
                    existing_ids: list[str] = []
                    if isinstance(existing_news, list):
                        for n in existing_news:
                            if isinstance(n, dict) and isinstance(n.get("id"), str):
                                existing_ids.append(n["id"])
                    next_ids = existing_ids[:]
                    for nid in newsletters:
                        if nid not in next_ids:
                            next_ids.append(nid)
                    patch["newsletters"] = [{"id": nid} for nid in next_ids]
                _call_with_retries(lambda: api.members_update(existing_id, {"members": [{**patch, "id": existing_id}]}))
                want_label_slugs = set()
                if "labels" in patch:
                    for lab in (patch.get("labels") or []):
                        if isinstance(lab, dict) and isinstance(lab.get("slug"), str):
                            want_label_slugs.add(lab["slug"])
                want_newsletter_ids = set()
                if "newsletters" in patch:
                    for nl in (patch.get("newsletters") or []):
                        if isinstance(nl, dict) and isinstance(nl.get("id"), str):
                            want_newsletter_ids.add(nl["id"])
                verify_member_state(existing_id, want_label_slugs=want_label_slugs, want_newsletter_ids=want_newsletter_ids)
                updated += 1
                sleep_if_needed()
            else:
                member: dict[str, Any] = {"email": target_email}
                if row.name:
                    member["name"] = row.name
                if row.note:
                    member["note"] = row.note
                if labels:
                    member["labels"] = [{"name": l.strip(), "slug": slugify_label(l)} for l in labels if l.strip()]
                if newsletters:
                    member["newsletters"] = [{"id": nid} for nid in newsletters]
                res = _call_with_retries(lambda: api.members_create({"members": [member]}))
                members = res.get("members") or []
                if not (
                    isinstance(members, list)
                    and members
                    and isinstance(members[0], dict)
                    and isinstance(members[0].get("id"), str)
                    and members[0].get("id")
                ):
                    raise RuntimeError("Unexpected members.create response (missing id)")
                member_id = str(members[0]["id"])
                want_label_slugs = set()
                for lab in (member.get("labels") or []):
                    if isinstance(lab, dict) and isinstance(lab.get("slug"), str):
                        want_label_slugs.add(lab["slug"])
                want_newsletter_ids = set()
                for nl in (member.get("newsletters") or []):
                    if isinstance(nl, dict) and isinstance(nl.get("id"), str):
                        want_newsletter_ids.add(nl["id"])
                verify_member_state(member_id, want_label_slugs=want_label_slugs, want_newsletter_ids=want_newsletter_ids)
                created += 1
                sleep_if_needed()
        except Exception as e:  # noqa: BLE001
            errors.append({"email": redact_email(row.email), "error": str(e)})
            if not args.continue_on_error:
                break

    backup = ctx.get("backup")
    if backup is not None:
        backup.write_before_after(
            kind="member",
            resource_id=f"import:{args.csv}",
            slug="",
            action="member.import",
            before=None,
            after={"created": created, "updated": updated, "errors": errors},
            meta={
                "stage": "summary",
                "mode": args.mode,
                "rows": len(rows),
                "created": created,
                "updated": updated,
                "errors": len(errors),
            },
        )

    ctx["audit"].write(
        "member.import",
        {"apply": True, "mode": args.mode, "rows": len(rows), "created": created, "updated": updated, "errors": len(errors)},
    )
    ctx["out"].print(
        {
            "apply": True,
            "mode": args.mode,
            "rows": len(rows),
            "created": created,
            "updated": updated,
            "errors": errors,
        }
    )
    return 0


def cmd_member_export_engagement(args, ctx) -> int:
    import csv
    from pathlib import Path

    api = get_api(ctx)
    limit = int(args.limit)
    if limit < 1 or limit > 200:
        raise RuntimeError("--limit must be between 1 and 200")
    max_pages = int(args.max_pages)
    if max_pages < 1:
        raise RuntimeError("--max-pages must be >= 1")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "member_id",
        "uuid",
        "email",
        "name",
        "status",
        "email_count",
        "email_opened_count",
        "email_open_rate",
        "last_seen_at",
        "labels",
        "newsletters",
        "created_at",
        "updated_at",
    ]

    rows_written = 0
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        page = 1
        while page <= max_pages:
            params: dict[str, Any] = {
                "limit": limit,
                "page": page,
                "include": "labels,newsletters",
                "fields": "id,uuid,email,name,status,email_count,email_opened_count,email_open_rate,last_seen_at,created_at,updated_at",
            }
            if args.filter and args.filter.strip().lower() != "all":
                params["filter"] = args.filter
            res = api.members_browse(params=params)
            members = res.get("members") or []
            if not isinstance(members, list) or not members:
                break
            for m in members:
                if not isinstance(m, dict):
                    continue
                labels = m.get("labels") if isinstance(m.get("labels"), list) else []
                label_slugs = []
                for lab in labels:
                    if isinstance(lab, dict) and isinstance(lab.get("slug"), str):
                        label_slugs.append(lab["slug"])
                newsletters = m.get("newsletters") if isinstance(m.get("newsletters"), list) else []
                newsletter_slugs = []
                for nl in newsletters:
                    if isinstance(nl, dict) and isinstance(nl.get("id"), str):
                        # Prefer slug if present.
                        if isinstance(nl.get("slug"), str):
                            newsletter_slugs.append(nl["slug"])
                        else:
                            newsletter_slugs.append(nl["id"])
                email = m.get("email") if isinstance(m.get("email"), str) else ""
                w.writerow(
                    {
                        "member_id": m.get("id"),
                        "uuid": m.get("uuid"),
                        "email": email if args.include_emails else redact_email(email),
                        "name": m.get("name"),
                        "status": m.get("status"),
                        "email_count": m.get("email_count"),
                        "email_opened_count": m.get("email_opened_count"),
                        "email_open_rate": m.get("email_open_rate"),
                        "last_seen_at": m.get("last_seen_at"),
                        "labels": "|".join(sorted(set(label_slugs))),
                        "newsletters": "|".join(sorted(set(newsletter_slugs))),
                        "created_at": m.get("created_at"),
                        "updated_at": m.get("updated_at"),
                    }
                )
                rows_written += 1
            meta = res.get("meta") if isinstance(res, dict) else None
            pagination = meta.get("pagination") if isinstance(meta, dict) else None
            pages = pagination.get("pages") if isinstance(pagination, dict) else None
            if isinstance(pages, int) and page >= pages:
                break
            page += 1

    ctx["audit"].write(
        "member.export_engagement",
        {"apply": True, "out": str(out_path), "rows": rows_written, "include_emails": bool(args.include_emails)},
    )
    ctx["out"].print({"ok": True, "out": str(out_path), "rows": rows_written, "include_emails": bool(args.include_emails)})
    return 0
