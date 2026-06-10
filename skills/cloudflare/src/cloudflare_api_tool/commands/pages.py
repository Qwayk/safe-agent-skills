from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from typing import Any

from blake3 import blake3

from ..errors import ToolError
from ..errors import ValidationError
from ._storage_db_common import (
    base_plan,
    base_receipt,
    emit_plan,
    emit_receipt,
    require_apply,
    require_token,
    require_yes,
    resolve_account_id,
    verify_and_require_plan,
    write_raw_response_to_file,
)

MAX_ASSET_COUNT_DEFAULT = 20_000
MAX_ASSET_SIZE_BYTES = 25 * 1024 * 1024
MAX_BUCKET_SIZE_BYTES = 40 * 1024 * 1024
MAX_BUCKET_FILE_COUNT = 2000
IGNORE_DIR_NAMES = {"functions", "node_modules", ".git", ".wrangler"}
IGNORE_FILE_NAMES = {"_worker.js", "_headers", "_redirects", "_routes.json", ".DS_Store"}


def _guess_content_type(path: Path) -> str:
    guess, _ = mimetypes.guess_type(str(path))
    return str(guess or "application/octet-stream")


def _decode_jwt_payload(token: str) -> dict[str, Any]:
    parts = str(token or "").split(".")
    if len(parts) < 2:
        return {}
    payload = parts[1]
    payload += "=" * (-len(payload) % 4)
    try:
        raw = base64.urlsafe_b64decode(payload.encode("ascii"))
        obj = json.loads(raw.decode("utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _max_file_count_from_jwt(token: str) -> int:
    payload = _decode_jwt_payload(token)
    raw = payload.get("max_file_count_allowed")
    if isinstance(raw, int) and raw > 0:
        return raw
    return MAX_ASSET_COUNT_DEFAULT


def _asset_hash(path: Path) -> str:
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    ext = path.suffix[1:]
    return blake3((encoded + ext).encode("utf-8")).hexdigest()[:32]


def _should_skip_asset(relative_path: Path) -> bool:
    parts = relative_path.parts
    if not parts:
        return True
    if any(part in IGNORE_DIR_NAMES for part in parts[:-1]):
        return True
    return parts[-1] in IGNORE_FILE_NAMES


def _collect_assets(source_dir: Path, *, file_count_limit: int) -> list[dict[str, Any]]:
    if not source_dir.exists() or not source_dir.is_dir():
        raise ValidationError(f"Source directory not found: {source_dir}")

    assets: list[dict[str, Any]] = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(source_dir)
        if _should_skip_asset(rel):
            continue
        size_bytes = path.stat().st_size
        if size_bytes > MAX_ASSET_SIZE_BYTES:
            raise ValidationError(f"Pages only supports files up to {MAX_ASSET_SIZE_BYTES} bytes: {rel.as_posix()}")
        assets.append(
            {
                "abs_path": path,
                "rel_path": rel.as_posix(),
                "size_bytes": size_bytes,
                "content_type": _guess_content_type(path),
                "hash": _asset_hash(path),
            }
        )

    if len(assets) > int(file_count_limit):
        raise ValidationError(
            f"Pages only supports up to {file_count_limit} files in a deployment for this upload token."
        )
    return assets


def _optional_text_file(source_dir: Path, name: str) -> str | None:
    path = source_dir / name
    if not path.exists() or not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _bucket_assets(assets: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    buckets: list[list[dict[str, Any]]] = []
    cur: list[dict[str, Any]] = []
    cur_size = 0
    for asset in assets:
        size = int(asset["size_bytes"])
        if cur and ((cur_size + size) > MAX_BUCKET_SIZE_BYTES or len(cur) >= MAX_BUCKET_FILE_COUNT):
            buckets.append(cur)
            cur = []
            cur_size = 0
        cur.append(asset)
        cur_size += size
    if cur:
        buckets.append(cur)
    return buckets


def _parse_deployment_result(body: bytes) -> dict[str, Any]:
    try:
        obj = json.loads(body.decode("utf-8"))
    except Exception:
        return {}
    if isinstance(obj, dict):
        result = obj.get("result")
        if isinstance(result, dict):
            return result
    return {}


def _maybe_get_project_info(ctx, project_path: str) -> tuple[dict[str, Any] | None, bool]:
    try:
        project_res = ctx["cf"].get_json(project_path)
    except ToolError as exc:
        if "HTTP 404" in str(exc):
            return (None, False)
        raise
    result = project_res.result
    return ((result if isinstance(result, dict) else {}), True)


def cmd_pages_deploy(args, ctx) -> int:
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    project_name = str(getattr(args, "project_name", "") or "").strip()
    branch = str(getattr(args, "branch", "") or "").strip() or None
    production_branch = str(getattr(args, "production_branch", "") or "").strip() or "main"
    source_dir = Path(str(getattr(args, "source_dir", "") or "").strip()) if getattr(args, "source_dir", None) else Path(".")
    if not project_name:
        raise ValidationError("Missing --project-name")
    if not source_dir:
        raise ValidationError("Missing --source-dir")

    out_arg = str(getattr(args, "out", "") or "").strip()
    if bool(ctx.get("apply")) and not out_arg:
        raise ValidationError("Missing --out for sensitive Pages deployment result.")

    project_path = f"/accounts/{account_id}/pages/projects/{project_name}"
    target_environment = "preview" if branch and branch != production_branch else "production"

    selector = {
        "account_id": account_id,
        "project_name": project_name,
        "source_dir": str(source_dir),
        "branch": branch,
        "production_branch": production_branch,
        "target_environment": target_environment,
    }
    risk_level = "medium" if target_environment == "preview" else "high"
    plan = base_plan(
        ctx,
        selector=selector,
        risk_level=risk_level,
        risk_reasons=[
            "Uploads static assets to Cloudflare Pages using the direct-upload asset flow.",
            "Pages deployment responses are sensitive and must be written to a file.",
        ],
    )
    plan["request"] = {
        "method": "POST",
        "path": f"{project_path}/deployments",
        "sensitivity": "sensitive_write_result",
        "out": out_arg,
    }
    plan["proposed_changes"] = [
        {
            "resource": "pages_project",
            "action": "ensure_present",
            "details": {"project_name": project_name, "production_branch": production_branch},
        },
        {
            "resource": "pages_assets_manifest",
            "action": "upload_if_missing",
            "details": {"project_name": project_name, "source_dir": str(source_dir)},
        },
        {
            "resource": "cloudflare_pages_deployment",
            "action": "create",
            "details": {"project_name": project_name, "branch": branch, "target_environment": target_environment},
        },
    ]
    plan["verification_plan"] = [
        "If the project does not exist yet, create it before requesting the upload token.",
        "Confirm the deployment response is written to --out and includes a deployment id.",
        "Fetch the deployment by id and confirm Cloudflare returns the created deployment.",
    ]
    plan["notes"].append("Dry-run is local only; the Pages project is checked during apply.")
    if branch and branch != production_branch:
        plan["notes"].append(f"Branch {branch} is not the production branch ({production_branch}); this targets a preview deployment.")
    else:
        plan["notes"].append(f"Using production branch {production_branch}.")

    if not bool(ctx.get("apply")):
        return emit_plan(ctx, command="pages.deploy", plan=plan)

    require_apply(ctx)
    require_yes(ctx)
    verify_and_require_plan(ctx, plan=plan)

    project_info, project_exists = _maybe_get_project_info(ctx, project_path)
    project_created = False
    if not project_exists:
        created = ctx["cf"].request_json(
            "POST",
            f"/accounts/{account_id}/pages/projects",
            json_body={
                "name": project_name,
                "production_branch": production_branch,
            },
            retries=3,
        )
        result = created.result
        project_info = result if isinstance(result, dict) else {}
        project_created = True
    project_info = project_info or {}
    resolved_production_branch = str(project_info.get("production_branch") or "").strip() or production_branch
    target_environment = "preview" if branch and branch != resolved_production_branch else "production"

    token_res = ctx["cf"].get_json(f"{project_path}/upload-token")
    token_info = token_res.result if isinstance(token_res.result, dict) else {}
    upload_jwt = str(token_info.get("jwt") or "").strip()
    if not upload_jwt:
        raise ValidationError("Cloudflare Pages upload-token response did not include a JWT.")

    file_count_limit = _max_file_count_from_jwt(upload_jwt)
    assets = _collect_assets(source_dir, file_count_limit=file_count_limit)
    headers_text = _optional_text_file(source_dir, "_headers")
    redirects_text = _optional_text_file(source_dir, "_redirects")
    manifest = {f"/{asset['rel_path']}": asset["hash"] for asset in assets}
    all_hashes = [str(asset["hash"]) for asset in assets]

    missing_hashes: list[str]
    if bool(getattr(args, "skip_caching", False)):
        missing_hashes = list(all_hashes)
    else:
        missing_res = ctx["cf"].request_json(
            "POST",
            "/pages/assets/check-missing",
            json_body={"hashes": all_hashes},
            headers={"authorization": f"Bearer {upload_jwt}"},
            retries=3,
        )
        missing_raw = missing_res.result
        missing_hashes = [str(x) for x in missing_raw] if isinstance(missing_raw, list) else list(all_hashes)

    missing_assets = [asset for asset in assets if asset["hash"] in set(missing_hashes)]
    uploaded_files_count = 0
    for bucket in _bucket_assets(missing_assets):
        payload = []
        for asset in bucket:
            raw = Path(asset["abs_path"]).read_bytes()
            payload.append(
                {
                    "key": asset["hash"],
                    "value": base64.b64encode(raw).decode("ascii"),
                    "metadata": {"contentType": asset["content_type"]},
                    "base64": True,
                }
            )
        if payload:
            ctx["cf"].request_raw(
                "POST",
                "/pages/assets/upload",
                json_body=payload,
                headers={"authorization": f"Bearer {upload_jwt}"},
                retries=3,
            )
            uploaded_files_count += len(payload)

    if all_hashes:
        ctx["cf"].request_raw(
            "POST",
            "/pages/assets/upsert-hashes",
            json_body={"hashes": all_hashes},
            headers={"authorization": f"Bearer {upload_jwt}"},
            retries=1,
        )

    multipart_fields: list[tuple[str, Any]] = [("manifest", (None, json.dumps(manifest, separators=(",", ":"), sort_keys=True)))]
    if branch:
        multipart_fields.append(("branch", (None, branch)))
    if headers_text is not None:
        multipart_fields.append(("_headers", ("_headers", headers_text.encode("utf-8"), "text/plain")))
    if redirects_text is not None:
        multipart_fields.append(("_redirects", ("_redirects", redirects_text.encode("utf-8"), "text/plain")))

    deploy_resp = ctx["cf"].request_raw(
        "POST",
        f"{project_path}/deployments",
        files=multipart_fields,
        retries=3,
    )

    wrote = write_raw_response_to_file(
        ctx=ctx,
        out_path=out_arg,
        overwrite=bool(getattr(args, "overwrite", False)),
        method="POST",
        http_status=int(deploy_resp.status),
        body=deploy_resp.body,
    )

    deployment_result = _parse_deployment_result(deploy_resp.body)
    deployment_id = str(deployment_result.get("id") or "").strip() or None
    deployment_url = str(deployment_result.get("url") or "").strip() or None
    created_environment = str(deployment_result.get("environment") or "").strip() or None

    verification: dict[str, Any] = {
        "ok": bool(deployment_id),
        "method": "response_contains_deployment_id",
        "details": {
            "out_file": wrote["out_rel"],
            "deployment_id": deployment_id,
        },
    }
    if deployment_id:
        read_back = ctx["cf"].get_json(f"{project_path}/deployments/{deployment_id}")
        verify_result = read_back.result if isinstance(read_back.result, dict) else {}
        verification = {
            "ok": str(verify_result.get("id") or "").strip() == deployment_id,
            "method": "read_back_get_pages_deployment",
            "details": {
                "out_file": wrote["out_rel"],
                "deployment_id": deployment_id,
                "environment": verify_result.get("environment"),
                "latest_stage": ((verify_result.get("latest_stage") or {}) if isinstance(verify_result.get("latest_stage"), dict) else {}),
            },
        }

    receipt = base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [
        {
            "resource": "pages_project",
            "action": "created" if project_created else "already_present",
            "project_name": project_name,
            "production_branch": resolved_production_branch,
        },
        {
            "resource": "pages_assets_manifest",
            "action": "uploaded_if_missing",
            "project_name": project_name,
            "files_total": len(assets),
            "files_uploaded": uploaded_files_count,
            "files_reused": len(assets) - uploaded_files_count,
        },
        {
            "resource": "pages_deployment",
            "action": "created",
            "project_name": project_name,
            "branch": branch,
            "deployment_id": deployment_id,
            "environment": created_environment or target_environment,
            "deployment_url": deployment_url,
        },
    ]
    receipt["verification"] = verification
    receipt["output_file"] = wrote
    return emit_receipt(ctx, command="pages.deploy", receipt=receipt)
