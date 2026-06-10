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


def cmd_load_balancers_monitors_list(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/monitors",
        path_params={"account_id": account_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitors_get(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_id = _require(_opt_str(getattr(args, "monitor_id", None)), flag="--monitor-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/monitors/{monitor_id}",
        path_params={"account_id": account_id, "monitor_id": monitor_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitors_create(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/load_balancers/monitors",
        path_params={"account_id": account_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitors_update(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_id = _require(_opt_str(getattr(args, "monitor_id", None)), flag="--monitor-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/accounts/{account_id}/load_balancers/monitors/{monitor_id}",
        path_params={"account_id": account_id, "monitor_id": monitor_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitors_patch(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_id = _require(_opt_str(getattr(args, "monitor_id", None)), flag="--monitor-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/accounts/{account_id}/load_balancers/monitors/{monitor_id}",
        path_params={"account_id": account_id, "monitor_id": monitor_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitors_delete(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_id = _require(_opt_str(getattr(args, "monitor_id", None)), flag="--monitor-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/accounts/{account_id}/load_balancers/monitors/{monitor_id}",
        path_params={"account_id": account_id, "monitor_id": monitor_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitors_preview(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_id = _require(_opt_str(getattr(args, "monitor_id", None)), flag="--monitor-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/load_balancers/monitors/{monitor_id}/preview",
        path_params={"account_id": account_id, "monitor_id": monitor_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=_opt_str(getattr(args, "body_json_file", None)),
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitors_references(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_id = _require(_opt_str(getattr(args, "monitor_id", None)), flag="--monitor-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/monitors/{monitor_id}/references",
        path_params={"account_id": account_id, "monitor_id": monitor_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_pools_list(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/pools",
        path_params={"account_id": account_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_pools_get(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    pool_id = _require(_opt_str(getattr(args, "pool_id", None)), flag="--pool-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/pools/{pool_id}",
        path_params={"account_id": account_id, "pool_id": pool_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_pools_create(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/load_balancers/pools",
        path_params={"account_id": account_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_pools_update(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    pool_id = _require(_opt_str(getattr(args, "pool_id", None)), flag="--pool-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/accounts/{account_id}/load_balancers/pools/{pool_id}",
        path_params={"account_id": account_id, "pool_id": pool_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_pools_patch(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    pool_id = _require(_opt_str(getattr(args, "pool_id", None)), flag="--pool-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/accounts/{account_id}/load_balancers/pools/{pool_id}",
        path_params={"account_id": account_id, "pool_id": pool_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_pools_patch_all(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/accounts/{account_id}/load_balancers/pools",
        path_params={"account_id": account_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_pools_delete(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    pool_id = _require(_opt_str(getattr(args, "pool_id", None)), flag="--pool-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/accounts/{account_id}/load_balancers/pools/{pool_id}",
        path_params={"account_id": account_id, "pool_id": pool_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_pools_health(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    pool_id = _require(_opt_str(getattr(args, "pool_id", None)), flag="--pool-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/pools/{pool_id}/health",
        path_params={"account_id": account_id, "pool_id": pool_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_pools_preview(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    pool_id = _require(_opt_str(getattr(args, "pool_id", None)), flag="--pool-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/load_balancers/pools/{pool_id}/preview",
        path_params={"account_id": account_id, "pool_id": pool_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=_opt_str(getattr(args, "body_json_file", None)),
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_pools_references(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    pool_id = _require(_opt_str(getattr(args, "pool_id", None)), flag="--pool-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/pools/{pool_id}/references",
        path_params={"account_id": account_id, "pool_id": pool_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitor_groups_list(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/monitor_groups",
        path_params={"account_id": account_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitor_groups_get(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_group_id = _require(_opt_str(getattr(args, "monitor_group_id", None)), flag="--monitor-group-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/monitor_groups/{monitor_group_id}",
        path_params={"account_id": account_id, "monitor_group_id": monitor_group_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitor_groups_create(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/load_balancers/monitor_groups",
        path_params={"account_id": account_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitor_groups_update(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_group_id = _require(_opt_str(getattr(args, "monitor_group_id", None)), flag="--monitor-group-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/accounts/{account_id}/load_balancers/monitor_groups/{monitor_group_id}",
        path_params={"account_id": account_id, "monitor_group_id": monitor_group_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitor_groups_patch(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_group_id = _require(_opt_str(getattr(args, "monitor_group_id", None)), flag="--monitor-group-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/accounts/{account_id}/load_balancers/monitor_groups/{monitor_group_id}",
        path_params={"account_id": account_id, "monitor_group_id": monitor_group_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitor_groups_delete(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_group_id = _require(_opt_str(getattr(args, "monitor_group_id", None)), flag="--monitor-group-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/accounts/{account_id}/load_balancers/monitor_groups/{monitor_group_id}",
        path_params={"account_id": account_id, "monitor_group_id": monitor_group_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_monitor_groups_references(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    monitor_group_id = _require(_opt_str(getattr(args, "monitor_group_id", None)), flag="--monitor-group-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/monitor_groups/{monitor_group_id}/references",
        path_params={"account_id": account_id, "monitor_group_id": monitor_group_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_regions_list(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/regions",
        path_params={"account_id": account_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_regions_get(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    region_id = _require(_opt_str(getattr(args, "region_id", None)), flag="--region-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/regions/{region_id}",
        path_params={"account_id": account_id, "region_id": region_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_search(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/search",
        path_params={"account_id": account_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_load_balancers_preview_result_get(args, ctx) -> int:  # noqa: ANN001
    account_id = _require(_opt_str(getattr(args, "account_id", None)), flag="--account-id")
    preview_id = _require(_opt_str(getattr(args, "preview_id", None)), flag="--preview-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/load_balancers/preview/{preview_id}",
        path_params={"account_id": account_id, "preview_id": preview_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )
