from __future__ import annotations

from typing import Any

from ..api import PinterestApi, resolve_access_token


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


def cmd_user_account_get(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    api = _api(ctx)
    data = api.get("/user_account")
    out = {"ok": True, "path": "/user_account", "data": data}
    ctx["audit"].write("user_account.get", {})
    ctx["out"].emit(out)
    return 0


def _list_user_account(args: Any, ctx: dict[str, Any], *, stage: str, path: str) -> int:
    api = _api(ctx)
    params = _parse_kv_pairs(getattr(args, "param", None))
    items, bookmark, pages = api.list_all(
        path,
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "path": path,
        "params": params,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write(stage, {"count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_user_account_businesses_list(args: Any, ctx: dict[str, Any]) -> int:
    return _list_user_account(args, ctx, stage="user_account.businesses.list", path="/user_account/businesses")


def cmd_user_account_followers_list(args: Any, ctx: dict[str, Any]) -> int:
    return _list_user_account(args, ctx, stage="user_account.followers.list", path="/user_account/followers")


def cmd_user_account_following_list(args: Any, ctx: dict[str, Any]) -> int:
    return _list_user_account(args, ctx, stage="user_account.following.list", path="/user_account/following")


def cmd_user_account_following_boards_list(args: Any, ctx: dict[str, Any]) -> int:
    return _list_user_account(
        args,
        ctx,
        stage="user_account.following_boards.list",
        path="/user_account/following/boards",
    )


def cmd_user_account_websites_list(args: Any, ctx: dict[str, Any]) -> int:
    return _list_user_account(args, ctx, stage="user_account.websites.list", path="/user_account/websites")


def cmd_user_account_websites_verification(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    api = _api(ctx)
    data = api.get("/user_account/websites/verification")
    out = {"ok": True, "path": "/user_account/websites/verification", "data": data}
    ctx["audit"].write("user_account.websites.verification", {})
    ctx["out"].emit(out)
    return 0

