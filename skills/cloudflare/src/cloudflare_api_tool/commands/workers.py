from __future__ import annotations

from ..errors import NotSupportedError, ValidationError
from ..state import get_default_account_id


def _resolve_account_id(args, ctx) -> str:
    account_id = str(getattr(args, "account_id", "") or "").strip()
    if account_id:
        return account_id
    default = get_default_account_id(ctx["env_file"], fingerprint=ctx.get("env_fingerprint"))
    if default:
        return default
    raise ValidationError(
        "Missing --account-id and no default is set. "
        "Run: cloudflare-api-tool accounts set-default --account-id <id>"
    )


def _require_token(ctx) -> None:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")


def cmd_workers_scripts_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    tags = str(getattr(args, "tags", "") or "").strip()
    params: dict[str, object] = {}
    if tags:
        params["tags"] = tags
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts", params=params or None)
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.scripts.list",
        "account_id": account_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
        "result_info": res.result_info,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_scripts_search(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    name = str(getattr(args, "name", "") or "").strip()
    page = int(getattr(args, "page", 1) or 1)
    per_page = int(getattr(args, "per_page", 50) or 50)
    params: dict[str, object] = {"page": page, "per_page": per_page}
    if name:
        params["name"] = name
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts-search", params=params)
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.scripts.search",
        "account_id": account_id,
        "page": page,
        "per_page": per_page,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
        "result_info": res.result_info,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_scripts_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    # Metadata/settings only. Do not call the Worker download/content endpoints.
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/settings")
    out = {
        "ok": True,
        "command": "workers.scripts.get",
        "account_id": account_id,
        "script_name": script_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_scripts_schedules_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/schedules")
    out = {
        "ok": True,
        "command": "workers.scripts.schedules.get",
        "account_id": account_id,
        "script_name": script_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_scripts_script_settings_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/script-settings")
    out = {
        "ok": True,
        "command": "workers.scripts.script_settings.get",
        "account_id": account_id,
        "script_name": script_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_scripts_usage_model_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/usage-model")
    out = {
        "ok": True,
        "command": "workers.scripts.usage_model.get",
        "account_id": account_id,
        "script_name": script_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_scripts_subdomain_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/subdomain")
    out = {
        "ok": True,
        "command": "workers.scripts.subdomain.get",
        "account_id": account_id,
        "script_name": script_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_scripts_secrets_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    # Metadata only: this endpoint does not return secret values.
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/secrets")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.scripts.secrets.list",
        "account_id": account_id,
        "script_name": script_name,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_scripts_secrets_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    secret_name = str(getattr(args, "secret_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    if not secret_name:
        raise ValidationError("Missing --secret-name")
    # Metadata only: this endpoint does not return secret values.
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/secrets/{secret_name}")
    out = {
        "ok": True,
        "command": "workers.scripts.secrets.get",
        "account_id": account_id,
        "script_name": script_name,
        "secret_name": secret_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_routes_list(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/workers/routes")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.routes.list",
        "zone_id": zone_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_routes_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    route_id = str(getattr(args, "route_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not route_id:
        raise ValidationError("Missing --route-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/workers/routes/{route_id}")
    out = {"ok": True, "command": "workers.routes.get", "zone_id": zone_id, "route_id": route_id, "result": res.result}
    ctx["out"].emit(out)
    return 0


def cmd_workers_subdomain_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/subdomain")
    out = {"ok": True, "command": "workers.subdomain.get", "account_id": account_id, "result": res.result}
    ctx["out"].emit(out)
    return 0


def cmd_workers_domains_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/domains")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.domains.list",
        "account_id": account_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
        "result_info": res.result_info,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_domains_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    domain_id = str(getattr(args, "domain_id", "") or "").strip()
    if not domain_id:
        raise ValidationError("Missing --domain-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/domains/{domain_id}")
    out = {"ok": True, "command": "workers.domains.get", "account_id": account_id, "domain_id": domain_id, "result": res.result}
    ctx["out"].emit(out)
    return 0


def cmd_workers_account_settings_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/account-settings")
    out = {"ok": True, "command": "workers.account_settings.get", "account_id": account_id, "result": res.result}
    ctx["out"].emit(out)
    return 0


def cmd_workers_placement_regions_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/placement/regions")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.placement.regions.list",
        "account_id": account_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_platforms_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/workers")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.platforms.list",
        "account_id": account_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_platforms_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    worker_id = str(getattr(args, "worker_id", "") or "").strip()
    if not worker_id:
        raise ValidationError("Missing --worker-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/workers/{worker_id}")
    out = {
        "ok": True,
        "command": "workers.platforms.get",
        "account_id": account_id,
        "worker_id": worker_id,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_services_env_settings_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    service_name = str(getattr(args, "service_name", "") or "").strip()
    environment_name = str(getattr(args, "environment_name", "") or "").strip()
    if not service_name:
        raise ValidationError("Missing --service-name")
    if not environment_name:
        raise ValidationError("Missing --environment-name")
    res = ctx["cf"].get_json(
        f"/accounts/{account_id}/workers/services/{service_name}/environments/{environment_name}/settings"
    )
    out = {
        "ok": True,
        "command": "workers.services.env.settings.get",
        "account_id": account_id,
        "service_name": service_name,
        "environment_name": environment_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_dispatch_namespaces_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/dispatch/namespaces")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.dispatch.namespaces.list",
        "account_id": account_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_dispatch_namespaces_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    ns = str(getattr(args, "dispatch_namespace", "") or "").strip()
    if not ns:
        raise ValidationError("Missing --dispatch-namespace")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/dispatch/namespaces/{ns}")
    out = {
        "ok": True,
        "command": "workers.dispatch.namespaces.get",
        "account_id": account_id,
        "dispatch_namespace": ns,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_dispatch_scripts_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    ns = str(getattr(args, "dispatch_namespace", "") or "").strip()
    if not ns:
        raise ValidationError("Missing --dispatch-namespace")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/dispatch/namespaces/{ns}/scripts")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.dispatch.scripts.list",
        "account_id": account_id,
        "dispatch_namespace": ns,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_dispatch_scripts_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    ns = str(getattr(args, "dispatch_namespace", "") or "").strip()
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not ns:
        raise ValidationError("Missing --dispatch-namespace")
    if not script_name:
        raise ValidationError("Missing --script-name")
    # Metadata/settings only. Do not call `/content`.
    res = ctx["cf"].get_json(
        f"/accounts/{account_id}/workers/dispatch/namespaces/{ns}/scripts/{script_name}/settings"
    )
    out = {
        "ok": True,
        "command": "workers.dispatch.scripts.get",
        "account_id": account_id,
        "dispatch_namespace": ns,
        "script_name": script_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_dispatch_scripts_bindings_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    ns = str(getattr(args, "dispatch_namespace", "") or "").strip()
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not ns:
        raise ValidationError("Missing --dispatch-namespace")
    if not script_name:
        raise ValidationError("Missing --script-name")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/dispatch/namespaces/{ns}/scripts/{script_name}/bindings")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.dispatch.scripts.bindings.list",
        "account_id": account_id,
        "dispatch_namespace": ns,
        "script_name": script_name,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_dispatch_scripts_tags_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    ns = str(getattr(args, "dispatch_namespace", "") or "").strip()
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not ns:
        raise ValidationError("Missing --dispatch-namespace")
    if not script_name:
        raise ValidationError("Missing --script-name")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/dispatch/namespaces/{ns}/scripts/{script_name}/tags")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.dispatch.scripts.tags.list",
        "account_id": account_id,
        "dispatch_namespace": ns,
        "script_name": script_name,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_dispatch_scripts_secrets_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    ns = str(getattr(args, "dispatch_namespace", "") or "").strip()
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not ns:
        raise ValidationError("Missing --dispatch-namespace")
    if not script_name:
        raise ValidationError("Missing --script-name")
    # Metadata only: this endpoint does not return secret values.
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/dispatch/namespaces/{ns}/scripts/{script_name}/secrets")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.dispatch.scripts.secrets.list",
        "account_id": account_id,
        "dispatch_namespace": ns,
        "script_name": script_name,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_dispatch_scripts_secrets_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    ns = str(getattr(args, "dispatch_namespace", "") or "").strip()
    script_name = str(getattr(args, "script_name", "") or "").strip()
    secret_name = str(getattr(args, "secret_name", "") or "").strip()
    if not ns:
        raise ValidationError("Missing --dispatch-namespace")
    if not script_name:
        raise ValidationError("Missing --script-name")
    if not secret_name:
        raise ValidationError("Missing --secret-name")
    # Metadata only: this endpoint does not return secret values.
    res = ctx["cf"].get_json(
        f"/accounts/{account_id}/workers/dispatch/namespaces/{ns}/scripts/{script_name}/secrets/{secret_name}"
    )
    out = {
        "ok": True,
        "command": "workers.dispatch.scripts.secrets.get",
        "account_id": account_id,
        "dispatch_namespace": ns,
        "script_name": script_name,
        "secret_name": secret_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_kv_namespaces_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/storage/kv/namespaces")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.kv.namespaces.list",
        "account_id": account_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
        "result_info": res.result_info,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_kv_namespaces_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    namespace_id = str(getattr(args, "namespace_id", "") or "").strip()
    if not namespace_id:
        raise ValidationError("Missing --namespace-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/storage/kv/namespaces/{namespace_id}")
    out = {
        "ok": True,
        "command": "workers.kv.namespaces.get",
        "account_id": account_id,
        "namespace_id": namespace_id,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_kv_keys_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    namespace_id = str(getattr(args, "namespace_id", "") or "").strip()
    if not namespace_id:
        raise ValidationError("Missing --namespace-id")

    limit = int(getattr(args, "limit", 1000) or 1000)
    prefix = str(getattr(args, "prefix", "") or "").strip()
    cursor = str(getattr(args, "cursor", "") or "").strip() or None
    all_pages = bool(getattr(args, "all", False))
    max_rows = int(getattr(args, "max_rows", 5000) or 5000)

    base_params: dict[str, object] = {"limit": limit}
    if prefix:
        base_params["prefix"] = prefix
    if cursor and not all_pages:
        base_params["cursor"] = cursor

    path = f"/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/keys"
    if not all_pages:
        res = ctx["cf"].get_json(path, params=base_params)
        items = res.result or []
        out = {
            "ok": True,
            "command": "workers.kv.keys.list",
            "account_id": account_id,
            "namespace_id": namespace_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
        ctx["out"].emit(out)
        return 0

    rows: list[object] = []
    for it in ctx["cf"].paginate_cursor(path, params=base_params, cursor=cursor):
        rows.append(it)
        if len(rows) >= max_rows:
            break
    out = {
        "ok": True,
        "command": "workers.kv.keys.list",
        "account_id": account_id,
        "namespace_id": namespace_id,
        "all": True,
        "max_rows": max_rows,
        "count": len(rows),
        "result": rows,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_kv_keys_metadata_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    namespace_id = str(getattr(args, "namespace_id", "") or "").strip()
    key_name = str(getattr(args, "key_name", "") or "").strip()
    if not namespace_id:
        raise ValidationError("Missing --namespace-id")
    if not key_name:
        raise ValidationError("Missing --key-name")
    # Metadata only: never fetch KV values.
    res = ctx["cf"].get_json(f"/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/metadata/{key_name}")
    out = {
        "ok": True,
        "command": "workers.kv.keys.metadata_get",
        "account_id": account_id,
        "namespace_id": namespace_id,
        "key_name": key_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_versions_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/versions")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.versions.list",
        "account_id": account_id,
        "script_name": script_name,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
        "result_info": res.result_info,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_versions_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    version_id = str(getattr(args, "version_id", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    if not version_id:
        raise ValidationError("Missing --version-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/versions/{version_id}")
    out = {
        "ok": True,
        "command": "workers.versions.get",
        "account_id": account_id,
        "script_name": script_name,
        "version_id": version_id,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_deployments_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/deployments")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.deployments.list",
        "account_id": account_id,
        "script_name": script_name,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
        "result_info": res.result_info,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_deployments_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    deployment_id = str(getattr(args, "deployment_id", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    if not deployment_id:
        raise ValidationError("Missing --deployment-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/deployments/{deployment_id}")
    out = {
        "ok": True,
        "command": "workers.deployments.get",
        "account_id": account_id,
        "script_name": script_name,
        "deployment_id": deployment_id,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_tails_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")
    # GET only. Do not implement streaming or POST/DELETE tail lifecycle endpoints.
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/tails")
    out = {
        "ok": True,
        "command": "workers.tails.list",
        "account_id": account_id,
        "script_name": script_name,
        "result": res.result,
        "result_info": res.result_info,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_builds_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    external_script_id = str(getattr(args, "external_script_id", "") or "").strip()
    if not external_script_id:
        raise ValidationError("Missing --external-script-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/builds/workers/{external_script_id}/builds")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.builds.list",
        "account_id": account_id,
        "external_script_id": external_script_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_builds_triggers_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    external_script_id = str(getattr(args, "external_script_id", "") or "").strip()
    if not external_script_id:
        raise ValidationError("Missing --external-script-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/builds/workers/{external_script_id}/triggers")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.builds.triggers.list",
        "account_id": account_id,
        "external_script_id": external_script_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_pipelines_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/pipelines/v1/pipelines")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.pipelines.list",
        "account_id": account_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_pipelines_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    pipeline_id = str(getattr(args, "pipeline_id", "") or "").strip()
    if not pipeline_id:
        raise ValidationError("Missing --pipeline-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/pipelines/v1/pipelines/{pipeline_id}")
    out = {
        "ok": True,
        "command": "workers.pipelines.get",
        "account_id": account_id,
        "pipeline_id": pipeline_id,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_pipelines_sinks_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/pipelines/v1/sinks")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.pipelines.sinks.list",
        "account_id": account_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_pipelines_sinks_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    sink_id = str(getattr(args, "sink_id", "") or "").strip()
    if not sink_id:
        raise ValidationError("Missing --sink-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/pipelines/v1/sinks/{sink_id}")
    out = {
        "ok": True,
        "command": "workers.pipelines.sinks.get",
        "account_id": account_id,
        "sink_id": sink_id,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_pipelines_streams_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/pipelines/v1/streams")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.pipelines.streams.list",
        "account_id": account_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_pipelines_streams_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    stream_id = str(getattr(args, "stream_id", "") or "").strip()
    if not stream_id:
        raise ValidationError("Missing --stream-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/pipelines/v1/streams/{stream_id}")
    out = {
        "ok": True,
        "command": "workers.pipelines.streams.get",
        "account_id": account_id,
        "stream_id": stream_id,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_pipelines_legacy_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/pipelines")
    items = res.result or []
    out = {
        "ok": True,
        "command": "workers.pipelines.legacy.list",
        "account_id": account_id,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_pipelines_legacy_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    pipeline_name = str(getattr(args, "pipeline_name", "") or "").strip()
    if not pipeline_name:
        raise ValidationError("Missing --pipeline-name")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/pipelines/{pipeline_name}")
    out = {
        "ok": True,
        "command": "workers.pipelines.legacy.get",
        "account_id": account_id,
        "pipeline_name": pipeline_name,
        "result": res.result,
    }
    ctx["out"].emit(out)
    return 0


def cmd_workers_refuse_not_supported(args, ctx) -> int:
    _ = args
    _ = ctx
    raise NotSupportedError("This operation is intentionally not implemented in this tool.")
