from __future__ import annotations

import argparse

from . import openapi_runner as openapi_runner_cmd
from ..errors import ValidationError


def _opt_str(v) -> str | None:  # noqa: ANN001
    s = str(v or "").strip()
    return s or None


def _require(value: str | None, *, flag: str) -> str:
    if value is None:
        raise ValidationError(f"Missing {flag}")
    return value


def _kv_list(values: list[str] | None) -> list[str]:
    out: list[str] = []
    for s in values or []:
        raw = str(s or "").strip()
        if not raw:
            continue
        if "=" not in raw:
            raise ValidationError(f"Invalid key=value: {raw!r}")
        out.append(raw)
    return out


def _delegate_openapi_call(
    *,
    ctx: dict,
    method: str,
    path_template: str,
    path_params: dict[str, str] | None = None,
    query: list[str] | None = None,
    body_json_file: str | None = None,
    content_type: str | None = None,
    out: str | None = None,
    overwrite: bool = False,
) -> int:
    ns = argparse.Namespace(
        operation_id=None,
        method=str(method or "").upper().strip(),
        path=str(path_template or "").strip(),
        path_param=[f"{k}={v}" for k, v in sorted((path_params or {}).items())],
        query=list(query or []),
        body_json_file=body_json_file,
        body_bytes_file=None,
        multipart_spec_file=None,
        content_type=content_type,
        out=out,
        overwrite=bool(overwrite),
    )
    return int(openapi_runner_cmd.cmd_openapi_call(ns, ctx))


def _path_params_with_account_id(args) -> dict[str, str]:  # noqa: ANN001
    params: dict[str, str] = {}
    account_id = _opt_str(getattr(args, "account_id", None))
    if account_id is not None:
        params["account_id"] = account_id
    return params


def cmd_turnstile_widgets_list(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/challenges/widgets",
        path_params=_path_params_with_account_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_turnstile_widgets_get(args, ctx) -> int:  # noqa: ANN001
    sitekey = _require(_opt_str(getattr(args, "sitekey", None)), flag="--sitekey")
    params = _path_params_with_account_id(args)
    params["sitekey"] = sitekey
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/challenges/widgets/{sitekey}",
        path_params=params,
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_turnstile_widgets_create(args, ctx) -> int:  # noqa: ANN001
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/challenges/widgets",
        path_params=_path_params_with_account_id(args),
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_turnstile_widgets_update(args, ctx) -> int:  # noqa: ANN001
    sitekey = _require(_opt_str(getattr(args, "sitekey", None)), flag="--sitekey")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    params = _path_params_with_account_id(args)
    params["sitekey"] = sitekey
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/accounts/{account_id}/challenges/widgets/{sitekey}",
        path_params=params,
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_turnstile_widgets_delete(args, ctx) -> int:  # noqa: ANN001
    sitekey = _require(_opt_str(getattr(args, "sitekey", None)), flag="--sitekey")
    params = _path_params_with_account_id(args)
    params["sitekey"] = sitekey
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/accounts/{account_id}/challenges/widgets/{sitekey}",
        path_params=params,
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_turnstile_widgets_rotate_secret(args, ctx) -> int:  # noqa: ANN001
    sitekey = _require(_opt_str(getattr(args, "sitekey", None)), flag="--sitekey")
    params = _path_params_with_account_id(args)
    params["sitekey"] = sitekey
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/challenges/widgets/{sitekey}/rotate_secret",
        path_params=params,
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )

