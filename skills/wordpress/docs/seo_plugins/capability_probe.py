from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from typing import Any

import requests

from wordpress_api_tool.config import load_config


def _basic_auth_header(username: str, app_password: str) -> str:
    token = base64.b64encode(f"{username}:{app_password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _lower_headers(headers: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(headers).items():
        out[str(k).lower()] = str(v)
    return out


def _try_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except Exception:
        return None


class ProbeHttp:
    def __init__(self, *, timeout_s: float, verbose: bool, auth_header: str):
        self._timeout_s = float(timeout_s)
        self._verbose = bool(verbose)
        self._auth_header = auth_header
        self._session = requests.Session()
        self._session.headers["User-Agent"] = "wordpress-api-tool-seo-probe/0.1"

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, str], str, Any | None]:
        headers = {"Authorization": self._auth_header, "Accept": "application/json"}
        display_url = url
        if params:
            try:
                display_url = requests.Request("GET", url, params=params).prepare().url or url
            except Exception:
                display_url = url

        start = time.time()
        if self._verbose:
            print(f"[http] {method} {display_url} (start)", file=sys.stderr)
        try:
            resp = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=self._timeout_s,
            )
        except requests.RequestException as e:
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {e}", file=sys.stderr)
            raise RuntimeError(f"Request failed for {method} {display_url}: {type(e).__name__}: {e}") from e

        ms = int((time.time() - start) * 1000)
        if self._verbose:
            print(f"[http] {method} {resp.url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

        text = resp.text or ""
        return resp.status_code, _lower_headers(resp.headers), text, _try_json(text)


def _pick_target_post(
    http: ProbeHttp,
    *,
    wp_json_base: str,
    post_type: str,
    me_user_id: int,
) -> dict[str, Any]:
    url = f"{wp_json_base}/wp/v2/{post_type}"
    status, _hdrs, _text, data = http.request(
        "GET",
        url,
        params={
            "per_page": "10",
            "page": "1",
            "context": "edit",
            "status": "any",
            "orderby": "date",
            "order": "desc",
        },
    )
    if status >= 400 or not isinstance(data, list) or not data:
        raise RuntimeError(f"Could not auto-pick a {post_type!r} post for probing.")

    owned = [p for p in data if isinstance(p, dict) and p.get("author") == me_user_id]
    return owned[0] if owned else data[0]


def _get_post_by_id(http: ProbeHttp, *, wp_json_base: str, post_type: str, post_id: int) -> dict[str, Any]:
    url = f"{wp_json_base}/wp/v2/{post_type}/{int(post_id)}"
    status, _hdrs, _text, data = http.request("GET", url, params={"context": "edit"})
    if status >= 400 or not isinstance(data, dict):
        raise RuntimeError(f"Failed to fetch post by id={post_id}.")
    return data


def _get_post_by_slug(http: ProbeHttp, *, wp_json_base: str, post_type: str, slug: str) -> dict[str, Any]:
    url = f"{wp_json_base}/wp/v2/{post_type}"
    status, _hdrs, _text, data = http.request(
        "GET",
        url,
        params={"slug": slug, "context": "edit", "status": "any", "per_page": "100"},
    )
    if status >= 400 or not isinstance(data, list) or not data:
        raise RuntimeError(f"No {post_type} found for slug={slug!r}")
    if len(data) > 1:
        raise RuntimeError(f"Multiple {post_type} found for slug={slug!r}")
    if not isinstance(data[0], dict):
        raise RuntimeError("Unexpected response shape for slug query.")
    return data[0]


def _detect_signals(post: dict[str, Any]) -> dict[str, bool]:
    # These are “read” signals only (headless outputs).
    return {
        "yoast_head_json": "yoast_head_json" in post,
        "yoast_head": "yoast_head" in post,
        "aioseo_head_json": "aioseo_head_json" in post,
        "aioseo_head": "aioseo_head" in post,
        "seopress_head": "seopress_head" in post,
        "rank_math_head": "rank_math_head" in post,
    }


def _rest_index(http: ProbeHttp, *, wp_json_base: str) -> dict[str, Any]:
    status, _hdrs, _text, data = http.request("GET", f"{wp_json_base}")
    if status >= 400 or not isinstance(data, dict):
        raise RuntimeError("Failed to fetch REST API index (/wp-json).")
    return data


def _methods_from_route(route_info: dict[str, Any]) -> list[str]:
    methods: set[str] = set()
    for m in route_info.get("methods", []) if isinstance(route_info.get("methods"), list) else []:
        if isinstance(m, str):
            methods.add(m.upper())
    endpoints = route_info.get("endpoints")
    if isinstance(endpoints, list):
        for ep in endpoints:
            if not isinstance(ep, dict):
                continue
            for m in ep.get("methods", []) if isinstance(ep.get("methods"), list) else []:
                if isinstance(m, str):
                    methods.add(m.upper())
    return sorted(methods)


def _find_route_methods(routes: dict[str, Any], *, contains: str, also_contains: str | None = None) -> dict[str, Any] | None:
    # REST index uses route templates like:
    #   /yoast/v1
    #   /seopress/v1/posts/(?P<id>[\\d]+)/title-description-metas
    for path, info in routes.items():
        if not isinstance(path, str) or contains not in path:
            continue
        if also_contains is not None and also_contains not in path:
            continue
        if not isinstance(info, dict):
            continue
        return {"path": path, "methods": _methods_from_route(info)}
    return None


def _probe_seopress(
    *,
    wp_index: dict[str, Any],
    wp_json_base: str,
    user_can_edit_target: bool,
) -> dict[str, Any]:
    namespaces = wp_index.get("namespaces", [])
    routes = wp_index.get("routes", {})
    if not isinstance(routes, dict):
        routes = {}

    detected = isinstance(namespaces, list) and any(ns == "seopress/v1" for ns in namespaces if isinstance(ns, str))
    # Some installs may omit namespaces but still list routes; cover that too.
    if not detected:
        detected = any(isinstance(p, str) and p.startswith("/seopress/v1") for p in routes.keys())

    seopress_routes: list[dict[str, Any]] = []
    for path, info in routes.items():
        if not isinstance(path, str) or not path.startswith("/seopress/v1"):
            continue
        if not isinstance(info, dict):
            continue
        seopress_routes.append({"path": path, "methods": _methods_from_route(info)})

    endpoints: dict[str, Any] = {}
    for name, needle in {
        "title_description": "title-description-metas",
        "robots": "meta-robot-settings",
        "social": "social-settings",
    }.items():
        picked = _find_route_methods(routes, contains="/seopress/v1", also_contains=needle)
        endpoints[name] = {
            "detected": bool(picked and picked.get("path") and "/seopress/v1/" in str(picked.get("path"))),
            "route": picked,
            "example_url": f"{wp_json_base}/seopress/v1/posts/{{id}}/{needle}",
        }

    # Determine PUT support:
    # - Prefer the title/desc route (the core “SEO basics” capability).
    # - Fallback to “any SEOPress /posts route supports PUT”.
    title_route = endpoints["title_description"].get("route") or {}
    title_methods = title_route.get("methods", []) if isinstance(title_route, dict) else []
    supports_put_title = "PUT" in [m.upper() for m in title_methods if isinstance(m, str)]
    supports_put_any_posts = any(
        "PUT" in r.get("methods", []) and "/posts/" in str(r.get("path", "")) for r in seopress_routes
    )
    supports_put = bool(supports_put_title or supports_put_any_posts)

    can_write = bool(detected and supports_put and user_can_edit_target)
    confidence = "high" if can_write else ("medium" if detected and supports_put else ("low" if detected else "low"))

    return {
        "detected": detected,
        "supports_put": supports_put,
        "supports_put_title_description": supports_put_title,
        "supports_put_any_posts": supports_put_any_posts,
        "user_can_edit_target": user_can_edit_target,
        "can_write": can_write,
        "confidence": confidence,
        "routes_sample": seopress_routes[:20],
        "endpoints": endpoints,
        "note": (
            "Detection uses the REST API index (/wp-json) to avoid false positives from OPTIONS responses. "
            "can_write=true means: SEOPress routes exist, they declare PUT, and the current user could fetch the target post with context=edit."
        ),
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="seo-capability-probe")
    p.add_argument("--env-file", default=".env", help="Path to .env (default: .env)")
    p.add_argument("--timeout-s", type=float, default=30.0)
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--post-type", default="posts", help="WP REST type (default: posts)")
    p.add_argument("--id", type=int, default=None, help="Post id (optional)")
    p.add_argument("--slug", default=None, help="Post slug (optional)")
    args = p.parse_args(argv)

    if args.id is not None and args.slug is not None:
        raise SystemExit("Provide only one of --id or --slug.")

    cfg = load_config(args.env_file)
    wp_json_base = cfg.base_url.rstrip("/") + "/wp-json"
    auth_header = _basic_auth_header(cfg.username, cfg.app_password)

    http = ProbeHttp(timeout_s=args.timeout_s, verbose=args.verbose, auth_header=auth_header)

    # Auth check
    me_status, _me_headers, _me_text, me_json = http.request("GET", f"{wp_json_base}/wp/v2/users/me")
    if me_status >= 400 or not isinstance(me_json, dict):
        raise RuntimeError("Auth check failed.")

    me_user_id = int(me_json.get("id", 0) or 0)
    if me_user_id <= 0:
        raise RuntimeError("Unexpected /users/me response (missing id).")

    # Target post selection
    post_type = str(args.post_type)
    if args.id is not None:
        post = _get_post_by_id(http, wp_json_base=wp_json_base, post_type=post_type, post_id=int(args.id))
    elif args.slug is not None:
        post = _get_post_by_slug(http, wp_json_base=wp_json_base, post_type=post_type, slug=str(args.slug))
    else:
        post = _pick_target_post(http, wp_json_base=wp_json_base, post_type=post_type, me_user_id=me_user_id)

    post_id = int(post.get("id", 0) or 0)
    if post_id <= 0:
        raise RuntimeError("Unexpected post payload (missing id).")

    signals = _detect_signals(post)
    wp_index = _rest_index(http, wp_json_base=wp_json_base)

    user_can_edit_target = True  # We fetched it with context=edit successfully.
    seopress = _probe_seopress(
        wp_index=wp_index,
        wp_json_base=wp_json_base,
        user_can_edit_target=user_can_edit_target,
    )

    # Lightweight plugin “presence” guesses (read-only signals)
    plugins: dict[str, Any] = {
        "seopress": seopress,
        "aioseo": {
            "detected": bool(signals["aioseo_head_json"] or signals["aioseo_head"]),
            "can_write": False,
            "confidence": "low",
            "note": "Write support is site/version/permissions dependent; not probed here.",
        },
        "yoast": {
            "detected": bool(signals["yoast_head_json"] or signals["yoast_head"])
            or (
                isinstance(wp_index.get("namespaces"), list)
                and any(ns == "yoast/v1" for ns in wp_index.get("namespaces", []) if isinstance(ns, str))
            ),
            "can_write": False,
            "confidence": "low",
            "note": "Typically not writable via REST without extra enablement.",
        },
        "rank_math": {
            "detected": bool(signals["rank_math_head"])
            or (
                isinstance(wp_index.get("namespaces"), list)
                and any(ns == "rankmath/v1" for ns in wp_index.get("namespaces", []) if isinstance(ns, str))
            ),
            "can_write": False,
            "confidence": "low",
            "note": "Typically not writable via REST without extra enablement.",
        },
    }

    detected = [k for k, v in plugins.items() if isinstance(v, dict) and v.get("detected")]
    can_write = bool(plugins["seopress"]["can_write"])
    recommendation = {
        "seo_write_supported": can_write,
        "best_path": "seopress" if can_write else None,
        "detected_plugins": detected,
        "note": "If seopress.can_write=false, assume SEO fields are not writable via API without extra enablement.",
    }

    out = {
        "site": {"base_url": cfg.base_url.rstrip("/"), "wp_json_base": wp_json_base},
        "auth": {"me": {"id": me_user_id, "name": me_json.get("name"), "slug": me_json.get("slug")}},
        "target": {
            "post_type": post_type,
            "id": post_id,
            "slug": post.get("slug"),
            "owned_by_me": post.get("author") == me_user_id,
        },
        "signals": signals,
        "rest_index": {
            "namespaces": wp_index.get("namespaces", []),
            "has_seopress_v1": isinstance(wp_index.get("namespaces"), list)
            and any(ns == "seopress/v1" for ns in wp_index.get("namespaces", []) if isinstance(ns, str)),
        },
        "plugins": plugins,
        "recommendation": recommendation,
    }

    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
