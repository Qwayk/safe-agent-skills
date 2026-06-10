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


def cmd_registrar_domains_list(args, ctx) -> int:  # noqa: ANN001
    account_id = _opt_str(getattr(args, "account_id", None))
    path_params: dict[str, str] = {}
    if account_id:
        path_params["account_id"] = account_id
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/registrar/domains",
        path_params=path_params,
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_registrar_domains_get(args, ctx) -> int:  # noqa: ANN001
    account_id = _opt_str(getattr(args, "account_id", None))
    domain_name = _require(_opt_str(getattr(args, "domain_name", None)), flag="--domain-name")
    path_params: dict[str, str] = {"domain_name": domain_name}
    if account_id:
        path_params["account_id"] = account_id
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/registrar/domains/{domain_name}",
        path_params=path_params,
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_registrar_domains_update(args, ctx) -> int:  # noqa: ANN001
    account_id = _opt_str(getattr(args, "account_id", None))
    domain_name = _require(_opt_str(getattr(args, "domain_name", None)), flag="--domain-name")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    path_params: dict[str, str] = {"domain_name": domain_name}
    if account_id:
        path_params["account_id"] = account_id
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/accounts/{account_id}/registrar/domains/{domain_name}",
        path_params=path_params,
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )

