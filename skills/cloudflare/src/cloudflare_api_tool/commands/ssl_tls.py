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


def cmd_ssl_automatic_mode_get(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/settings/ssl_automatic_mode",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_ssl_automatic_mode_set(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/zones/{zone_id}/settings/ssl_automatic_mode",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_ssl_analyze(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _opt_str(getattr(args, "body_json_file", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/ssl/analyze",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_ssl_recommendation(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/ssl/recommendation",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_universal_ssl_get(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/ssl/universal/settings",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_universal_ssl_set(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/zones/{zone_id}/ssl/universal/settings",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_ssl_verification_get(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/ssl/verification",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_ssl_verification_update(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    certificate_pack_id = _require(_opt_str(getattr(args, "certificate_pack_id", None)), flag="--certificate-pack-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/zones/{zone_id}/ssl/verification/{certificate_pack_id}",
        path_params={"zone_id": zone_id, "certificate_pack_id": certificate_pack_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_certificate_packs_list(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/ssl/certificate_packs",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_certificate_packs_get(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    certificate_pack_id = _require(_opt_str(getattr(args, "certificate_pack_id", None)), flag="--certificate-pack-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/ssl/certificate_packs/{certificate_pack_id}",
        path_params={"zone_id": zone_id, "certificate_pack_id": certificate_pack_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_certificate_packs_quota(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/ssl/certificate_packs/quota",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_certificate_packs_order(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/ssl/certificate_packs/order",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_certificate_packs_update(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    certificate_pack_id = _require(_opt_str(getattr(args, "certificate_pack_id", None)), flag="--certificate-pack-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/zones/{zone_id}/ssl/certificate_packs/{certificate_pack_id}",
        path_params={"zone_id": zone_id, "certificate_pack_id": certificate_pack_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_certificate_packs_restart(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    certificate_pack_id = _require(_opt_str(getattr(args, "certificate_pack_id", None)), flag="--certificate-pack-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/zones/{zone_id}/ssl/certificate_packs/{certificate_pack_id}",
        path_params={"zone_id": zone_id, "certificate_pack_id": certificate_pack_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_certificate_packs_delete(args, ctx) -> int:  # noqa: ANN001
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    certificate_pack_id = _require(_opt_str(getattr(args, "certificate_pack_id", None)), flag="--certificate-pack-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/zones/{zone_id}/ssl/certificate_packs/{certificate_pack_id}",
        path_params={"zone_id": zone_id, "certificate_pack_id": certificate_pack_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )
