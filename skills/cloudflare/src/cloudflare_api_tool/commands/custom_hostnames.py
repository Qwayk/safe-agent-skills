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


def cmd_custom_hostnames_list(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/custom_hostnames",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_custom_hostnames_get(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    custom_hostname_id = _require(_opt_str(getattr(args, "custom_hostname_id", None)), flag="--custom-hostname-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/custom_hostnames/{custom_hostname_id}",
        path_params={"zone_id": zone_id, "custom_hostname_id": custom_hostname_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_custom_hostnames_create(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/custom_hostnames",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_custom_hostnames_update(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    custom_hostname_id = _require(_opt_str(getattr(args, "custom_hostname_id", None)), flag="--custom-hostname-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/zones/{zone_id}/custom_hostnames/{custom_hostname_id}",
        path_params={"zone_id": zone_id, "custom_hostname_id": custom_hostname_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_custom_hostnames_delete(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    custom_hostname_id = _require(_opt_str(getattr(args, "custom_hostname_id", None)), flag="--custom-hostname-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/zones/{zone_id}/custom_hostnames/{custom_hostname_id}",
        path_params={"zone_id": zone_id, "custom_hostname_id": custom_hostname_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_custom_hostnames_fallback_origin_get(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/custom_hostnames/fallback_origin",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_custom_hostnames_fallback_origin_update(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/zones/{zone_id}/custom_hostnames/fallback_origin",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_custom_hostnames_fallback_origin_delete(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/zones/{zone_id}/custom_hostnames/fallback_origin",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_custom_hostnames_cert_replace(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    custom_hostname_id = _require(_opt_str(getattr(args, "custom_hostname_id", None)), flag="--custom-hostname-id")
    certificate_pack_id = _require(_opt_str(getattr(args, "certificate_pack_id", None)), flag="--certificate-pack-id")
    certificate_id = _require(_opt_str(getattr(args, "certificate_id", None)), flag="--certificate-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/zones/{zone_id}/custom_hostnames/{custom_hostname_id}/certificate_pack/{certificate_pack_id}/certificates/{certificate_id}",
        path_params={
            "zone_id": zone_id,
            "custom_hostname_id": custom_hostname_id,
            "certificate_pack_id": certificate_pack_id,
            "certificate_id": certificate_id,
        },
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_custom_hostnames_cert_delete(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    custom_hostname_id = _require(_opt_str(getattr(args, "custom_hostname_id", None)), flag="--custom-hostname-id")
    certificate_pack_id = _require(_opt_str(getattr(args, "certificate_pack_id", None)), flag="--certificate-pack-id")
    certificate_id = _require(_opt_str(getattr(args, "certificate_id", None)), flag="--certificate-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/zones/{zone_id}/custom_hostnames/{custom_hostname_id}/certificate_pack/{certificate_pack_id}/certificates/{certificate_id}",
        path_params={
            "zone_id": zone_id,
            "custom_hostname_id": custom_hostname_id,
            "certificate_pack_id": certificate_pack_id,
            "certificate_id": certificate_id,
        },
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )

