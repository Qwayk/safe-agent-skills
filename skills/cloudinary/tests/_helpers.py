from __future__ import annotations

import io
import json
import re
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

from cloudinary_safe_agent_cli.cli import main
from cloudinary_safe_agent_cli.inventory import OperationSpec, load_operation_specs


class FakeResponse:
    def __init__(self, *, status_code: int = 200, payload: Any | None = None, text: str | None = None, url: str = "https://api.cloudinary.com/mock", headers: dict[str, str] | None = None):
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            hdrs = {"Content-Type": "application/json"}
        else:
            body = (text or "").encode("utf-8")
            hdrs = headers or {"Content-Type": "text/plain"}
        self.status_code = status_code
        self.content = body
        self.headers = hdrs
        self.url = url
        self.text = body.decode("utf-8", errors="replace")


def write_env(
    root: Path,
    *,
    product_context: bool = False,
    product_auth: bool = False,
    account_context: bool = False,
    account_auth: bool = False,
    product_secret: str = "product-secret",
    account_secret: str = "account-secret",
) -> Path:
    lines = ["CLOUDINARY_TIMEOUT_S=5"]
    if product_context or product_auth:
        lines.append("CLOUDINARY_CLOUD_NAME=demo")
        lines.append("CLOUDINARY_PRODUCT_API_HOST=api.cloudinary.com")
    if product_auth:
        lines.append("CLOUDINARY_API_KEY=demo-key")
        lines.append(f"CLOUDINARY_API_SECRET={product_secret}")
    if account_context or account_auth:
        lines.append("CLOUDINARY_ACCOUNT_ID=demo-account")
        lines.append("CLOUDINARY_ACCOUNT_API_HOST=api.cloudinary.com")
    if account_auth:
        lines.append("CLOUDINARY_ACCOUNT_API_KEY=account-key")
        lines.append(f"CLOUDINARY_ACCOUNT_API_SECRET={account_secret}")
    env_path = root / ".env"
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return env_path


def run_cli(args: list[str], *, request_side_effect: Callable[..., Any] | None = None) -> tuple[int, dict[str, Any]]:
    buf = io.StringIO()
    manager = (
        patch("cloudinary_safe_agent_cli.http.requests.Session.request", side_effect=request_side_effect)
        if request_side_effect is not None
        else None
    )
    if manager is None:
        with redirect_stdout(buf):
            rc = main(args)
    else:
        with manager:
            with redirect_stdout(buf):
                rc = main(args)
    payload = json.loads(buf.getvalue())
    return rc, payload


def assert_blocked_before_state(testcase: Any, plan: dict[str, Any]) -> None:
    before_state = plan.get("before_state")
    testcase.assertIsInstance(before_state, dict)
    testcase.assertTrue(before_state.get("required"))
    testcase.assertFalse(before_state.get("supported"))
    testcase.assertEqual(before_state.get("status"), "no_snapshot_available")
    testcase.assertIsNone(before_state.get("saved_path"))
    testcase.assertIsNone(before_state.get("provider_backup_id"))
    verification_plan = plan.get("verification_plan")
    testcase.assertIsInstance(verification_plan, dict)
    testcase.assertEqual(verification_plan.get("method"), "best_effort_after_apply")
    recovery = plan.get("recovery")
    testcase.assertIsInstance(recovery, dict)
    testcase.assertFalse(recovery.get("automatic_rollback"))
    testcase.assertEqual(recovery.get("backups"), [])
    testcase.assertEqual(recovery.get("snapshots"), [])
    testcase.assertIsNone(recovery.get("rollback_plan"))


def spec_for_area(area: str) -> OperationSpec:
    specs = [spec for spec in load_operation_specs() if spec.area == area]
    write_specs = [spec for spec in specs if spec.is_write]
    return write_specs[0] if write_specs else specs[0]


def env_for_spec(root: Path, spec: OperationSpec) -> Path:
    if spec.auth_scope == "public":
        return write_env(root)
    if spec.auth_scope == "product_unsigned":
        return write_env(root, product_context=True)
    if spec.auth_scope == "product_basic":
        if spec.is_write:
            return write_env(root, product_context=True)
        return write_env(root, product_context=True, product_auth=True)
    if spec.auth_scope == "account_basic":
        if spec.is_write:
            return write_env(root, account_context=True)
        return write_env(root, account_context=True, account_auth=True)
    raise AssertionError(f"Unsupported auth scope in test helper: {spec.auth_scope}")


def _placeholder_names(path_template: str) -> list[str]:
    path_part, _, query_part = path_template.partition("?")
    names = re.findall(r":([A-Za-z_][A-Za-z0-9_]*)", path_part)
    names.extend(re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", path_part))
    names.extend(re.findall(r"=:(\w+)", query_part))
    out: list[str] = []
    for name in names:
        if name not in out:
            out.append(name)
    return out


def _dummy_value(name: str) -> str:
    lower = name.lower()
    if "id" in lower:
        return "sample-id"
    if "name" in lower:
        return "sample-name"
    if "folder" in lower:
        return "sample-folder"
    if "tag" in lower:
        return "sample-tag"
    if "resource_type" in lower:
        return "image"
    if "type" == lower:
        return "upload"
    return "sample"


def build_cli_args_for_spec(root: Path, spec: OperationSpec, env_path: Path) -> list[str]:
    args = ["--output", "json", "--env-file", str(env_path), "operations", spec.area, spec.op_key]
    for name in _placeholder_names(spec.path_template):
        args.extend(["--path-param", f"{name}={_dummy_value(name)}"])
    if spec.body_required:
        if spec.input_style == "json":
            body_path = root / "body.json"
            body_path.write_text("{}\n", encoding="utf-8")
            args.extend(["--body-json-file", str(body_path)])
        else:
            args.extend(["--form-field", "sample=value"])
    if spec.requires_out and not spec.is_write:
        args.extend(["--out", "response.json", "--overwrite"])
    return args
