from __future__ import annotations

from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


def _coerce_account_id(raw: Any) -> str:
    value = str(raw or "").strip()
    if not value:
        raise ValidationError("Missing --account-id")
    return value


def _coerce_paging(*, limit: int | None, offset: int | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if limit is not None:
        if not isinstance(limit, int) or limit < 0 or limit > 50:
            raise ValidationError("--limit must be between 0 and 50")
        params["paging.limit"] = int(limit)
    if offset is not None:
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("--offset must be 0 or greater")
        params["paging.offset"] = int(offset)
    return params


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=dict(headers),
        params=params,
        json_body=None,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_success(
    *,
    method: str,
    auth_mode: str,
    request: dict[str, Any],
    response: dict[str, Any],
    ctx: dict[str, Any],
) -> None:
    out = {
        "ok": True,
        "method": method,
        "auth_mode": auth_mode,
        "request": request,
        "response": response,
    }
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def cmd_accounts_get(args, ctx) -> int:
    try:
        account_id = _coerce_account_id(getattr(args, "account_id", None))
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="accounts",
        )
        request_path = f"/accounts/v1/accounts/{account_id}"
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth["headers"],
            params=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="accounts.get",
            auth_mode=auth["mode"],
            request={"method": "GET", "path": request_path},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1


def cmd_accounts_list_child_accounts(args, ctx) -> int:
    try:
        params = _coerce_paging(
            limit=getattr(args, "limit", None),
            offset=getattr(args, "offset", None),
        )
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="accounts",
        )
        request_path = "/accounts/v1/account/child-accounts"
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth["headers"],
            params=params or None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="accounts.list-child-accounts",
            auth_mode=auth["mode"],
            request={"method": "GET", "path": request_path, "params": params},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
