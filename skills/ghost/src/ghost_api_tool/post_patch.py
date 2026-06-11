from __future__ import annotations

import dataclasses
import hashlib
import html as html_lib
from html.parser import HTMLParser
import re
import time
from typing import Any
from urllib.parse import urlparse

from .diffutil import diff_dict
from .ghost_api import GhostAdminApi
from .backup_snapshots import SnapshotWriter
from .errors import ValidationError


@dataclasses.dataclass(frozen=True)
class PatchPlan:
    selector: dict[str, Any]
    resource_id: str
    dry_run: bool
    changes: list[dict[str, Any]]
    refused: bool
    reasons: list[str]
    before: dict[str, Any]
    after: dict[str, Any]


_H_ID_RE = re.compile(r"(<h[1-6]\b[^>]*?)\s+\bid=(?P<q>['\"])[^'\"]*(?P=q)", re.IGNORECASE)
_A_ATTR_RE = re.compile(r"(<a\b[^>]*?)\s+\b(?P<attr>rel|target)=(?P<q>['\"]).*?(?P=q)", re.IGNORECASE)
_ATTR_URL_RE = re.compile(r"\b(?P<attr>href|src)=(?P<q>['\"])(?P<url>https?://[^'\"]+)(?P=q)", re.IGNORECASE)


def _internal_hosts_from_site(api: GhostAdminApi) -> set[str]:
    try:
        site = api.get_site().get("site") or {}
        site_url = str(site.get("url") or "").strip()
        host = urlparse(site_url).hostname or ""
    except Exception:
        host = ""
    if not host:
        return set()
    host = host.lower()
    out = {host}
    if host.startswith("www."):
        out.add(host[len("www.") :])
    else:
        out.add("www." + host)
    return out


def _normalize_html_for_verification(html: str, *, internal_hosts: set[str]) -> str:
    """
    Best-effort normalization for Ghost `source=html` updates.

    This is intentionally best-effort (Ghost may re-serialize HTML).
    We normalize a few high-signal differences so verification doesn't fail on irrelevant changes.
    """
    s = (html or "").replace("\r\n", "\n").replace("\r", "\n")
    s = html_lib.unescape(s)

    def normalize_internal_url(raw: str) -> str:
        if not internal_hosts:
            return raw
        try:
            p = urlparse(raw)
        except Exception:
            return raw
        host = (p.hostname or "").lower()
        if not host or host not in internal_hosts:
            return raw
        path = p.path or "/"
        if not path.startswith("/"):
            path = "/" + path
        if p.query:
            path = path + "?" + p.query
        if p.fragment:
            path = path + "#" + p.fragment
        return path

    def normalize_class_value(v: str) -> str:
        parts = [p for p in re.split(r"\s+", (v or "").strip()) if p]
        parts = sorted(dict.fromkeys(parts))  # stable de-dupe
        return " ".join(parts)

    class _Canonicalizer(HTMLParser):
        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.out: list[str] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            self._emit_tag(tag, attrs, closed=False)

        def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            self._emit_tag(tag, attrs, closed=True)

        def handle_endtag(self, tag: str) -> None:
            self.out.append(f"</{(tag or '').lower()}>")

        def handle_data(self, data: str) -> None:
            self.out.append(data)

        def handle_comment(self, data: str) -> None:
            # Drop comments (Ghost may add/remove them).
            return

        def _emit_tag(self, tag: str, attrs: list[tuple[str, str | None]], *, closed: bool) -> None:
            t = (tag or "").lower()

            norm_attrs: list[tuple[str, str]] = []
            for k, v in attrs or []:
                kk = (k or "").lower()
                if not kk:
                    continue
                vv = "" if v is None else str(v)

                # Remove auto-added heading ids: <h2 id="..."> -> <h2>
                if kk == "id" and t in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                    continue

                # Remove auto-added anchor attributes (Ghost may add rel/target).
                if t == "a" and kk in {"rel", "target"}:
                    continue

                # Normalize internal absolute URLs to relative (href/src only).
                if kk in {"href", "src"}:
                    vv = normalize_internal_url(vv)

                if kk == "class":
                    vv = normalize_class_value(vv)

                norm_attrs.append((kk, vv))

            norm_attrs.sort(key=lambda kv: (kv[0], kv[1]))
            rendered = "".join([f' {k}="{html_lib.escape(v, quote=True)}"' for k, v in norm_attrs])
            if closed:
                self.out.append(f"<{t}{rendered}/>")
            else:
                self.out.append(f"<{t}{rendered}>")

    try:
        c = _Canonicalizer()
        c.feed(s)
        c.close()
        s = "".join(c.out)
    except Exception:
        # Fallback to regex-only normalization (do not block applies).
        pass

    # Collapse whitespace.
    s = re.sub(r">\s+<", "><", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _html_summary(s: Any) -> dict[str, Any]:
    if not isinstance(s, str):
        return {"type": type(s).__name__}
    digest = hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()
    return {"len": len(s), "sha256": digest}


def _normalize_rel_list(value: Any, *, kind: str) -> tuple[list[tuple[str, str]], list[str]]:
    """
    Normalizes tag/author lists for verification.

    Returns a list of (key_type, key_value) tuples:
      - tags: ("id"|"name"|"slug", value)
      - authors: ("id"|"email"|"slug", value)
    """
    if not isinstance(value, list):
        return [], [f"{kind} must be a list"]
    out: list[tuple[str, str]] = []
    reasons: list[str] = []
    for i, item in enumerate(value):
        if isinstance(item, str):
            out.append(("name" if kind == "tags" else "email", item))
            continue
        if isinstance(item, dict):
            for k in ("id", "name", "slug", "email"):
                v = item.get(k)
                if isinstance(v, str) and v:
                    out.append((k, v))
                    break
            else:
                reasons.append(f"{kind}[{i}] must include one of: id,name,slug,email")
            continue
        reasons.append(f"{kind}[{i}] must be a string or object")
    return out, reasons


def _verify_rel_list(
    *,
    field: str,
    expected: Any,
    got: Any,
    required_keys: tuple[str, ...],
) -> list[dict[str, Any]]:
    """
    Verifies tags/authors lists by identifier presence instead of exact object equality.
    """
    norm, reasons = _normalize_rel_list(expected, kind=field)
    if reasons:
        return [{"field": field, "expected": expected, "got": got, "reason": reasons}]
    if not isinstance(got, list):
        return [{"field": field, "expected": expected, "got": got, "reason": "got is not a list"}]

    # Ensure we didn't accidentally merge; relations are replaced.
    if len(got) != len(norm):
        return [
            {
                "field": field,
                "expected": expected,
                "got_count": len(got),
                "expected_count": len(norm),
                "reason": "relation count mismatch (expected replacement semantics)",
            }
        ]

    missing: list[dict[str, str]] = []
    for key, val in norm:
        if key not in required_keys:
            missing.append({"key": key, "value": val, "reason": "unsupported identifier"})
            continue
        found = False
        for obj in got:
            if isinstance(obj, dict) and obj.get(key) == val:
                found = True
                break
        if not found:
            missing.append({"key": key, "value": val, "reason": "not found"})
    if missing:
        return [{"field": field, "expected": expected, "got": got, "reason": "missing identifiers", "missing": missing}]
    return []


def _rel_list_matches_ordered(
    *,
    field: str,
    expected: Any,
    got: Any,
    required_keys: tuple[str, ...],
) -> bool:
    """
    Returns True if `got` already matches `expected` (replacement semantics) in the same order.

    This is used for no-op detection before writing. Order matters for `authors` because the first
    author is the primary author in Ghost.
    """
    norm, reasons = _normalize_rel_list(expected, kind=field)
    if reasons:
        return False
    if not isinstance(got, list):
        return False
    if len(got) != len(norm):
        return False
    for i, (key, val) in enumerate(norm):
        if key not in required_keys:
            return False
        obj = got[i] if i < len(got) else None
        if not isinstance(obj, dict):
            return False
        if obj.get(key) != val:
            return False
    return True


def _pick_one(selector_slug: str | None, selector_id: str | None) -> tuple[str, str]:
    if bool(selector_slug) == bool(selector_id):
        raise ValidationError("Provide exactly one selector: --slug or --id")
    if selector_slug:
        return "slug", selector_slug
    return "id", str(selector_id)


def resolve_post(
    api: GhostAdminApi,
    *,
    slug: str | None,
    post_id: str | None,
    formats: str | None = None,
) -> dict[str, Any]:
    params = {}
    if formats:
        params["formats"] = formats
    kind, val = _pick_one(slug, post_id)
    if kind == "slug":
        obj = api.posts_read_by_slug(val, params=params if params else None)
    else:
        obj = api.posts_read_by_id(val, params=params if params else None)
    posts = obj.get("posts") or []
    if not posts:
        raise RuntimeError("Post not found")
    return posts[0]


def resolve_page(
    api: GhostAdminApi,
    *,
    slug: str | None,
    page_id: str | None,
    formats: str | None = None,
) -> dict[str, Any]:
    params = {}
    if formats:
        params["formats"] = formats
    kind, val = _pick_one(slug, page_id)
    if kind == "slug":
        obj = api.pages_read_by_slug(val, params=params if params else None)
    else:
        obj = api.pages_read_by_id(val, params=params if params else None)
    pages = obj.get("pages") or []
    if not pages:
        raise RuntimeError("Page not found")
    return pages[0]


def apply_post_patch(
    api: GhostAdminApi,
    *,
    slug: str | None,
    post_id: str | None,
    patch: dict[str, Any],
    apply: bool,
    require_current: str | None = None,
    params: dict[str, Any] | None = None,
    source: str | None = None,
    snapshot: SnapshotWriter | None = None,
    snapshot_action: str = "post.patch",
    snapshot_meta: dict[str, Any] | None = None,
) -> PatchPlan:
    """
    Safe update pattern:
    - GET latest post
    - merge fields
    - PUT with updated_at
    - GET verify and assert result matches desired state

    Note: tags/authors are replaced, not merged; we always merge by GET first.
    """
    reasons: list[str] = []
    formats = "html,lexical,mobiledoc"
    before = resolve_post(api, slug=slug, post_id=post_id, formats=formats)

    if require_current and before.get("status") != require_current:
        return PatchPlan(
            selector={"slug": slug} if slug else {"id": post_id},
            resource_id=str(before.get("id")),
            dry_run=not apply,
            changes=[],
            refused=True,
            reasons=[f"Refused: require-current={require_current} but status={before.get('status')}"],
            before=before,
            after=before,
        )

    internal_hosts = set()
    if source == "html" and "html" in patch and isinstance(patch.get("html"), str):
        internal_hosts = _internal_hosts_from_site(api)

    # If this is a source=html update, treat normalized-equal HTML as a no-op (do not write).
    patch_effective = dict(patch)
    if source == "html" and isinstance(patch.get("html"), str):
        before_html = before.get("html")
        if isinstance(before_html, str):
            if _normalize_html_for_verification(str(patch["html"]), internal_hosts=internal_hosts) == _normalize_html_for_verification(
                before_html, internal_hosts=internal_hosts
            ):
                patch_effective.pop("html", None)

    # Treat tags/authors as relations and detect no-ops by identifier matching (Ghost expands these objects on read).
    if "tags" in patch_effective:
        if not _verify_rel_list(
            field="tags",
            expected=patch_effective.get("tags"),
            got=before.get("tags"),
            required_keys=("id", "name", "slug"),
        ):
            patch_effective.pop("tags", None)

    if "authors" in patch_effective:
        if _rel_list_matches_ordered(
            field="authors",
            expected=patch_effective.get("authors"),
            got=before.get("authors"),
            required_keys=("id", "email", "slug"),
        ):
            patch_effective.pop("authors", None)

    # Merge on top of latest.
    after = dict(before)
    for k, v in patch_effective.items():
        after[k] = v

    # Ensure required updated_at is provided.
    updated_at = before.get("updated_at")
    if not updated_at:
        raise RuntimeError("Post is missing updated_at; cannot safely update")

    payload_post: dict[str, Any] = {"updated_at": updated_at}
    for k, v in patch_effective.items():
        payload_post[k] = v

    # Calculate change summary (only for keys in patch plus status/title commonly).
    keys = list(patch_effective.keys())
    changes = diff_dict(before, after, keys=keys)
    if not changes:
        # No-op is OK.
        return PatchPlan(
            selector={"slug": slug} if slug else {"id": post_id},
            resource_id=str(before.get("id")),
            dry_run=not apply,
            changes=[],
            refused=False,
            reasons=[],
            before=before,
            after=before,
        )

    if not apply:
        if snapshot is not None:
            correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-{snapshot_action}"
            snapshot.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action=snapshot_action,
                before=before,
                after=None,
                meta={
                    "stage": "before",
                    "correlation_id": correlation_id,
                    "selector": {"slug": slug} if slug else {"id": post_id},
                    "changes": changes,
                    **(snapshot_meta or {}),
                },
            )
        return PatchPlan(
            selector={"slug": slug} if slug else {"id": post_id},
            resource_id=str(before.get("id")),
            dry_run=True,
            changes=changes,
            refused=False,
            reasons=[],
            before=before,
            after=after,
        )

    request_params: dict[str, Any] = dict(params or {})
    if source:
        request_params["source"] = source

    correlation_id = None
    if snapshot is not None:
        # Best-effort link between multiple snapshot files for the same operation.
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-{snapshot_action}"
        snapshot.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action=snapshot_action,
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": {"slug": slug} if slug else {"id": post_id},
                "changes": changes,
                **(snapshot_meta or {}),
            },
        )

    try:
        api.posts_update(
            str(before["id"]),
            {"posts": [payload_post]},
            params=request_params if request_params else None,
        )
        verified = resolve_post(api, slug=None, post_id=str(before["id"]), formats=formats)
    except Exception as e:
        if snapshot is not None:
            snapshot.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action=snapshot_action,
                before=None,
                after=None,
                meta={
                    "stage": "error",
                    "correlation_id": correlation_id,
                    "selector": {"slug": slug} if slug else {"id": post_id},
                    "error": str(e),
                    **(snapshot_meta or {}),
                },
            )
        raise

    # Verify: requested keys match.
    verify_fail = []
    for k in patch_effective.keys():
        if k == "tags":
            verify_fail.extend(
                _verify_rel_list(
                    field="tags",
                    expected=after.get("tags"),
                    got=verified.get("tags"),
                    required_keys=("id", "name", "slug"),
                )
            )
            continue
        if k == "authors":
            verify_fail.extend(
                _verify_rel_list(
                    field="authors",
                    expected=after.get("authors"),
                    got=verified.get("authors"),
                    required_keys=("id", "email", "slug"),
                )
            )
            continue
        if k == "status":
            expected_status = after.get("status")
            got_status = verified.get("status")
            # Ghost sets `status=sent` for email-only posts after successful delivery.
            # When using the Admin API `newsletter` parameter, publishing/scheduling is the trigger for sending.
            if expected_status != got_status:
                if expected_status == "published" and got_status == "sent" and isinstance(params, dict) and params.get("newsletter"):
                    continue
                verify_fail.append({"field": "status", "expected": expected_status, "got": got_status})
            continue
        if k == "html" and source == "html":
            expected_html = after.get("html")
            got_html = verified.get("html")
            if not isinstance(expected_html, str) or not isinstance(got_html, str):
                verify_fail.append({"field": "html", "expected": _html_summary(expected_html), "got": _html_summary(got_html)})
                continue
            if _normalize_html_for_verification(expected_html, internal_hosts=internal_hosts) != _normalize_html_for_verification(
                got_html, internal_hosts=internal_hosts
            ):
                verify_fail.append(
                    {
                        "field": "html",
                        "expected": _html_summary(expected_html),
                        "got": _html_summary(got_html),
                        "note": "normalized html mismatch (source=html verification)",
                    }
                )
            continue
        if verified.get(k) != after.get(k):
            verify_fail.append({"field": k, "expected": after.get(k), "got": verified.get(k)})
    if verify_fail:
        if snapshot is not None:
            snapshot.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action=snapshot_action,
                before=None,
                after=verified,
                meta={
                    "stage": "after",
                    "correlation_id": correlation_id,
                    "selector": {"slug": slug} if slug else {"id": post_id},
                    "verified": False,
                    "changes": changes,
                    "verify_fail": verify_fail,
                    **(snapshot_meta or {}),
                },
            )
        raise RuntimeError(f"Verification failed after update: {verify_fail}")

    if snapshot is not None:
        snapshot.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action=snapshot_action,
            before=None,
            after=verified,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "selector": {"slug": slug} if slug else {"id": post_id},
                "verified": True,
                "changes": changes,
                **(snapshot_meta or {}),
            },
        )

    return PatchPlan(
        selector={"slug": slug} if slug else {"id": post_id},
        resource_id=str(before.get("id")),
        dry_run=False,
        changes=changes,
        refused=False,
        reasons=reasons,
        before=before,
        after=verified,
    )


def apply_page_patch(
    api: GhostAdminApi,
    *,
    slug: str | None,
    page_id: str | None,
    patch: dict[str, Any],
    apply: bool,
    require_current: str | None = None,
    params: dict[str, Any] | None = None,
    source: str | None = None,
    snapshot: SnapshotWriter | None = None,
    snapshot_action: str = "page.patch",
    snapshot_meta: dict[str, Any] | None = None,
) -> PatchPlan:
    formats = "html,lexical,mobiledoc"
    before = resolve_page(api, slug=slug, page_id=page_id, formats=formats)
    if require_current and before.get("status") != require_current:
        return PatchPlan(
            selector={"slug": slug} if slug else {"id": page_id},
            resource_id=str(before.get("id")),
            dry_run=not apply,
            changes=[],
            refused=True,
            reasons=[f"Refused: require-current={require_current} but status={before.get('status')}"],
            before=before,
            after=before,
        )

    internal_hosts = set()
    if source == "html" and "html" in patch and isinstance(patch.get("html"), str):
        internal_hosts = _internal_hosts_from_site(api)

    patch_effective = dict(patch)
    if source == "html" and isinstance(patch.get("html"), str):
        before_html = before.get("html")
        if isinstance(before_html, str):
            if _normalize_html_for_verification(str(patch["html"]), internal_hosts=internal_hosts) == _normalize_html_for_verification(
                before_html, internal_hosts=internal_hosts
            ):
                patch_effective.pop("html", None)

    after = dict(before)
    for k, v in patch_effective.items():
        after[k] = v

    updated_at = before.get("updated_at")
    if not updated_at:
        raise RuntimeError("Page is missing updated_at; cannot safely update")

    payload_page: dict[str, Any] = {"updated_at": updated_at}
    for k, v in patch_effective.items():
        payload_page[k] = v

    keys = list(patch_effective.keys())
    changes = diff_dict(before, after, keys=keys)
    if not changes:
        return PatchPlan(
            selector={"slug": slug} if slug else {"id": page_id},
            resource_id=str(before.get("id")),
            dry_run=not apply,
            changes=[],
            refused=False,
            reasons=[],
            before=before,
            after=before,
        )

    if not apply:
        if snapshot is not None:
            correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-{snapshot_action}"
            snapshot.write_before_after(
                kind="page",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action=snapshot_action,
                before=before,
                after=None,
                meta={
                    "stage": "before",
                    "correlation_id": correlation_id,
                    "selector": {"slug": slug} if slug else {"id": page_id},
                    "changes": changes,
                    **(snapshot_meta or {}),
                },
            )
        return PatchPlan(
            selector={"slug": slug} if slug else {"id": page_id},
            resource_id=str(before.get("id")),
            dry_run=True,
            changes=changes,
            refused=False,
            reasons=[],
            before=before,
            after=after,
        )

    request_params: dict[str, Any] = dict(params or {})
    if source:
        request_params["source"] = source

    correlation_id = None
    if snapshot is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-{snapshot_action}"
        snapshot.write_before_after(
            kind="page",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action=snapshot_action,
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": {"slug": slug} if slug else {"id": page_id},
                "changes": changes,
                **(snapshot_meta or {}),
            },
        )

    try:
        api.pages_update(
            str(before["id"]),
            {"pages": [payload_page]},
            params=request_params if request_params else None,
        )
        verified = resolve_page(api, slug=None, page_id=str(before["id"]), formats=formats)
    except Exception as e:
        if snapshot is not None:
            snapshot.write_before_after(
                kind="page",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action=snapshot_action,
                before=None,
                after=None,
                meta={
                    "stage": "error",
                    "correlation_id": correlation_id,
                    "selector": {"slug": slug} if slug else {"id": page_id},
                    "error": str(e),
                    **(snapshot_meta or {}),
                },
            )
        raise

    verify_fail = []
    for k in patch_effective.keys():
        if k == "html" and source == "html":
            expected_html = after.get("html")
            got_html = verified.get("html")
            if not isinstance(expected_html, str) or not isinstance(got_html, str):
                verify_fail.append({"field": "html", "expected": _html_summary(expected_html), "got": _html_summary(got_html)})
                continue
            if _normalize_html_for_verification(expected_html, internal_hosts=internal_hosts) != _normalize_html_for_verification(
                got_html, internal_hosts=internal_hosts
            ):
                verify_fail.append(
                    {
                        "field": "html",
                        "expected": _html_summary(expected_html),
                        "got": _html_summary(got_html),
                        "note": "normalized html mismatch (source=html verification)",
                    }
                )
            continue
        if verified.get(k) != after.get(k):
            verify_fail.append({"field": k, "expected": after.get(k), "got": verified.get(k)})
    if verify_fail:
        if snapshot is not None:
            snapshot.write_before_after(
                kind="page",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action=snapshot_action,
                before=None,
                after=verified,
                meta={
                    "stage": "after",
                    "correlation_id": correlation_id,
                    "selector": {"slug": slug} if slug else {"id": page_id},
                    "verified": False,
                    "changes": changes,
                    "verify_fail": verify_fail,
                    **(snapshot_meta or {}),
                },
            )
        raise RuntimeError(f"Verification failed after update: {verify_fail}")

    if snapshot is not None:
        snapshot.write_before_after(
            kind="page",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action=snapshot_action,
            before=None,
            after=verified,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "selector": {"slug": slug} if slug else {"id": page_id},
                "verified": True,
                "changes": changes,
                **(snapshot_meta or {}),
            },
        )

    return PatchPlan(
        selector={"slug": slug} if slug else {"id": page_id},
        resource_id=str(before.get("id")),
        dry_run=False,
        changes=changes,
        refused=False,
        reasons=[],
        before=before,
        after=verified,
    )
