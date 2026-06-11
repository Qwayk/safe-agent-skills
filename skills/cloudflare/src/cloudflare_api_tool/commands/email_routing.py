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
        k, _v = raw.split("=", 1)
        if not k.strip():
            raise ValidationError(f"Invalid key=value (empty key): {raw!r}")
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


def _path_params_with_zone_id(args) -> dict[str, str]:  # noqa: ANN001
    params: dict[str, str] = {}
    zone_id = _opt_str(getattr(args, "zone_id", None))
    if zone_id is None:
        raise ValidationError("Missing --zone-id")
    params["zone_id"] = zone_id
    return params


# Addresses (account-scoped)
def cmd_email_routing_addresses_list(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/email/routing/addresses",
        path_params=_path_params_with_account_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_addresses_get(args, ctx) -> int:  # noqa: ANN001
    dest_id = _require(_opt_str(getattr(args, "destination_address_identifier", None)), flag="--destination-address-identifier")
    params = _path_params_with_account_id(args)
    params["destination_address_identifier"] = dest_id
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/email/routing/addresses/{destination_address_identifier}",
        path_params=params,
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_addresses_create(args, ctx) -> int:  # noqa: ANN001
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/email/routing/addresses",
        path_params=_path_params_with_account_id(args),
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_addresses_delete(args, ctx) -> int:  # noqa: ANN001
    dest_id = _require(_opt_str(getattr(args, "destination_address_identifier", None)), flag="--destination-address-identifier")
    params = _path_params_with_account_id(args)
    params["destination_address_identifier"] = dest_id
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/accounts/{account_id}/email/routing/addresses/{destination_address_identifier}",
        path_params=params,
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


# Settings (zone-scoped)
def cmd_email_routing_settings_get(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/email/routing",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_settings_enable(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/email/routing/enable",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_settings_disable(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/email/routing/disable",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


# DNS (zone-scoped)
def cmd_email_routing_dns_get(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/email/routing/dns",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_dns_enable(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/email/routing/dns",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_dns_disable(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/zones/{zone_id}/email/routing/dns",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_dns_unlock(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/zones/{zone_id}/email/routing/dns",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


# Rules (zone-scoped)
def cmd_email_routing_rules_list(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/email/routing/rules",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_rules_get(args, ctx) -> int:  # noqa: ANN001
    rule_id = _require(_opt_str(getattr(args, "rule_identifier", None)), flag="--rule-identifier")
    params = _path_params_with_zone_id(args)
    params["rule_identifier"] = rule_id
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/email/routing/rules/{rule_identifier}",
        path_params=params,
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_rules_create(args, ctx) -> int:  # noqa: ANN001
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/email/routing/rules",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_rules_update(args, ctx) -> int:  # noqa: ANN001
    rule_id = _require(_opt_str(getattr(args, "rule_identifier", None)), flag="--rule-identifier")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    params = _path_params_with_zone_id(args)
    params["rule_identifier"] = rule_id
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/zones/{zone_id}/email/routing/rules/{rule_identifier}",
        path_params=params,
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_rules_delete(args, ctx) -> int:  # noqa: ANN001
    rule_id = _require(_opt_str(getattr(args, "rule_identifier", None)), flag="--rule-identifier")
    params = _path_params_with_zone_id(args)
    params["rule_identifier"] = rule_id
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/zones/{zone_id}/email/routing/rules/{rule_identifier}",
        path_params=params,
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


# Catch-all (zone-scoped)
def cmd_email_routing_rules_catch_all_get(args, ctx) -> int:  # noqa: ANN001
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/email/routing/rules/catch_all",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_email_routing_rules_catch_all_update(args, ctx) -> int:  # noqa: ANN001
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/zones/{zone_id}/email/routing/rules/catch_all",
        path_params=_path_params_with_zone_id(args),
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )

