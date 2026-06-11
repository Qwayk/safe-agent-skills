from __future__ import annotations

import argparse
import traceback
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .audit_log import AuditLogger
from .config import Config, endpoint_url, load_config
from .errors import ToolError, ValidationError
from .http import HttpClient
from .output import Output
from .registry import arg_dest, load_endpoint_catalog

TOOL_NAME = "qwayk-pipedrive-safe-agent-cli"
MAX_PAGES_LIMIT = 25


def _redact_error_text(text: str, token: str | None) -> str:
    if not token:
        return text
    if not text:
        return text
    return text.replace(token, "***REDACTED***")


class _ToolArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    value = str(argv[idx + 1]).strip()
    return value if value in {"json", "text"} else "json"


def _coerce_int(value: str | int, name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"{name} must be an integer") from e


def _coerce_bool_like(value: str | int | bool, name: str) -> int:
    if isinstance(value, bool):
        return int(value)
    text = str(value).strip().lower()
    if text in {"0", "false", "f", "no", "off"}:
        return 0
    if text in {"1", "true", "t", "yes", "on"}:
        return 1
    raise ValidationError(f"{name} must be 0 or 1")


def _coerce_param(name: str, raw: Any, ptype: str | None, enum: list[Any] | None) -> Any:
    if raw is None:
        return None
    t = (ptype or "").lower()

    if enum and isinstance(enum, list) and enum:
        if all(v in {0, 1} for v in enum):
            return _coerce_bool_like(raw, name)
        if all(isinstance(v, int) for v in enum):
            return _coerce_int(raw, name)

    if t == "boolean":
        return _coerce_bool_like(raw, name)

    if t in {"integer", "number"}:
        if isinstance(raw, str) and "," in raw:
            return raw
        return _coerce_int(raw, name)

    return str(raw)


def _normalize_api_version(raw: Any) -> str:
    value = str(raw or "v1").strip().lower()
    if value.startswith("api/"):
        value = value.split("/", 1)[1]
    if not value:
        return "v1"
    if value.startswith("v"):
        return value
    return f"v{value}"


def _api_version_rank(raw: Any) -> int:
    text = _normalize_api_version(raw)
    if text.startswith("v") and text[1:].isdigit():
        return int(text[1:])
    return 0


def _to_api_query_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    text = str(value).strip().lower()
    if not text:
        return False
    if text in {"true", "1", "yes", "y", "on"}:
        return True
    if text in {"false", "0", "no", "n", "off"}:
        return False
    return False


def _collect_param_specs(entries: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for entry in entries:
        params = entry.get(key)
        if not isinstance(params, list):
            continue
        for raw in params:
            if not isinstance(raw, dict):
                continue
            name = str(raw.get("name") or "").strip()
            if not name:
                continue
            entry_spec = out.setdefault(
                name,
                {
                    "name": name,
                    "flag": "",
                    "type": str(raw.get("type") or "").strip(),
                    "required": bool(raw.get("required")),
                    "enum": list(raw.get("enum")) if isinstance(raw.get("enum"), list) else None,
                },
            )
            entry_spec["required"] = bool(entry_spec["required"]) or bool(raw.get("required"))
            if not entry_spec["flag"]:
                entry_spec["flag"] = str(raw.get("flag") or "").strip() or name
            ptype = str(raw.get("type") or "").strip()
            if not entry_spec["type"] and ptype:
                entry_spec["type"] = ptype
            if entry_spec["enum"] is None and isinstance(raw.get("enum"), list):
                entry_spec["enum"] = list(raw.get("enum"))

    return out


def _group_catalog_entries(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if not str(entry.get("operation") or "").strip().upper().startswith("GET"):
            continue
        tokens = [str(t).strip() for t in entry.get("command_tokens", []) if str(t).strip()]
        if len(tokens) != 2:
            continue
        grouped[" ".join(tokens)] = grouped.get(" ".join(tokens), []) + [entry]
    return grouped


def _bounded_max_pages(raw: Any) -> int:
    pages = _coerce_int(raw or 1, "max-pages")
    if pages < 1:
        raise ValidationError("max-pages must be at least 1")
    return pages if pages <= MAX_PAGES_LIMIT else MAX_PAGES_LIMIT


def _emit_error(
    *,
    out: Output,
    error: Exception,
    cfg: Config | None,
    debug: bool,
    audit: AuditLogger | None,
) -> None:
    token = cfg.token if isinstance(cfg, Config) else None
    message = _redact_error_text(str(error), token)
    if debug:
        tb = traceback.format_exc()
        if token:
            tb = _redact_error_text(tb, token)
        print(tb, file=sys.stderr)

    if audit is not None:
        audit.write("command_error", {"error_type": type(error).__name__, "error": message})

    out.emit({"ok": False, "error": message, "error_type": type(error).__name__})


def _build_request(entry: dict[str, Any], args: Any) -> tuple[dict[str, str], dict[str, Any], str]:
    rendered_path = str(entry.get("path") or "").strip()
    if not rendered_path:
        raise ValidationError("Missing operation path in catalog entry")

    path_params: dict[str, str] = {}
    for p in entry.get("path_parameters", []):
        if not isinstance(p, dict):
            continue
        name = str(p.get("name") or "").strip()
        if not name:
            continue
        raw = getattr(args, arg_dest(name), None)
        if raw is None or str(raw).strip() == "":
            if bool(p.get("required")):
                raise ValidationError(f"Missing required path parameter: {name}")
            continue
        value = str(raw).strip()
        path_params[name] = value
        rendered_path = rendered_path.replace("{" + name + "}", value)

    query: dict[str, Any] = {}
    for p in entry.get("query_parameters", []):
        if not isinstance(p, dict):
            continue
        name = str(p.get("name") or "").strip()
        if not name:
            continue
        raw = getattr(args, arg_dest(name), None)
        if raw is None or str(raw).strip() == "":
            if bool(p.get("required")):
                raise ValidationError(f"Missing required query parameter: {name}")
            continue
        coerce = _coerce_param(name, raw, str(p.get("type") or ""), p.get("enum") if isinstance(p.get("enum"), list) else None)
        query[name] = coerce

    return path_params, query, rendered_path


def _extract_page_signal(payload: Any, mode: str | None) -> tuple[bool, Any | None]:
    if not isinstance(payload, dict):
        return False, None

    additional = payload.get("additional_data")
    if not isinstance(additional, dict):
        return False, None

    normalized_mode = str(mode or "").strip().lower()
    if normalized_mode == "cursor":
        next_cursor = additional.get("next_cursor")
        if next_cursor is not None and str(next_cursor).strip() != "":
            return True, next_cursor
        pagination = additional.get("pagination")
        if isinstance(pagination, dict):
            pagination_cursor = pagination.get("next_cursor")
            if pagination_cursor is not None and str(pagination_cursor).strip() != "":
                return True, pagination_cursor
        return _to_api_query_bool(additional.get("more_items_in_collection")), None

    more = _to_api_query_bool(additional.get("more_items_in_collection"))
    pagination = additional.get("pagination") if isinstance(additional.get("pagination"), dict) else None
    if isinstance(pagination, dict):
        more = more or _to_api_query_bool(pagination.get("more_items_in_collection"))
        next_start = pagination.get("next_start")
        if next_start is not None:
            return bool(more), next_start

    return bool(more), additional.get("next_start")


def _build_payload(
    *,
    operation: str,
    api_version: str,
    http_method: str,
    request_path: str,
    path_params: dict[str, str],
    query: dict[str, Any],
    status: int,
    url: str,
    is_binary: bool,
    pagination: dict[str, Any],
    data: Any,
) -> dict[str, Any]:
    return {
        "operation": operation,
        "api_version": api_version,
        "http": {
            "method": http_method,
            "url": url,
            "status": status,
        },
        "request": {
            "path": request_path,
            "path_parameters": path_params,
            "query": query,
        },
        "response": {
            "binary": bool(is_binary),
        },
        "pagination": pagination,
        "data": data,
    }


def _run_read_request(
    *,
    cfg: Config,
    http: HttpClient,
    entry: dict[str, Any],
    path: str,
    path_params: dict[str, str],
    query: dict[str, Any],
    max_pages: int,
) -> dict[str, Any]:
    api_version = _normalize_api_version(entry.get("api_version"))
    paging = entry.get("paging") or {}
    mode = str(paging.get("mode") or "").strip().lower()
    page_param = str(paging.get("page_param") or "").strip() or None
    limit_param = str(paging.get("limit_param") or "").strip() or None

    request_query = dict(query)
    if mode in {"offset", "cursor"} and limit_param and request_query.get(limit_param) is None:
        request_query[limit_param] = 100

    headers = {"x-api-token": cfg.token or ""}
    base_url = endpoint_url(cfg=cfg, api_version=api_version, path=path)

    if bool(entry.get("binary")):
        is_download = str(path).endswith("/download")
        method_used = "HEAD" if is_download else "GET"
        response = http.request(
            method_used,
            base_url,
            headers=headers,
            params=request_query,
            allow_redirects=False,
            stream=True,
        )
        if response.status == 405 and is_download:
            # Some hosts do not allow HEAD on download endpoints.
            # Fall back to GET but still prevent redirects and streaming.
            method_used = "GET"
            response = http.request(
                method_used,
                base_url,
                headers=headers,
                params=request_query,
                allow_redirects=False,
                stream=True,
            )

        data = {
            "download": "metadata-only",
            "content_type": response.headers.get("content-type", ""),
            "location": response.headers.get("location", ""),
            "content_length": response.headers.get("content-length", ""),
        }
        if response.status in {301, 302, 303, 307, 308}:
            data["download"] = "redirect-metadata-only"
        return _build_payload(
            operation=str(entry.get("operation") or ""),
            api_version=api_version,
            http_method=method_used,
            request_path=path,
            path_params=path_params,
            query=request_query,
            status=response.status,
            url=response.url,
            is_binary=True,
            pagination={"mode": "none", "requested_pages": 1, "fetched_pages": 1, "has_more": False, "next_cursor": None},
            data=data,
        )

    if mode not in {"offset", "cursor"}:
        response = http.request("GET", base_url, headers=headers, params=request_query)
        parsed = response.json()
        data = parsed.get("data") if isinstance(parsed, dict) else parsed
        if data is None:
            data = parsed
        if isinstance(data, list):
            payload_data = data
        elif data is None:
            payload_data = []
        else:
            payload_data = [data]
        return _build_payload(
            operation=str(entry.get("operation") or ""),
            api_version=api_version,
            http_method="GET",
            request_path=path,
            path_params=path_params,
            query=request_query,
            status=response.status,
            url=response.url,
            is_binary=False,
            pagination={"mode": "none", "requested_pages": 1, "fetched_pages": 1, "has_more": False, "next_cursor": None},
            data=payload_data,
        )

    requested_pages = _bounded_max_pages(max_pages)
    fetched_pages = 0
    all_data: list[Any] = []
    next_cursor: Any | None = None
    has_more = False

    while fetched_pages < requested_pages:
        response = http.request("GET", base_url, headers=headers, params=request_query)
        parsed = response.json()
        fetched_pages += 1

        page_data = parsed.get("data") if isinstance(parsed, dict) else None
        if page_data is None:
            page_data = parsed
        if isinstance(page_data, list):
            all_data.extend(page_data)
        elif page_data is None:
            pass
        else:
            all_data.append(page_data)

        has_more, next_cursor = _extract_page_signal(parsed, mode)
        if not has_more:
            break

        if mode == "cursor":
            if page_param and next_cursor is not None:
                request_query[page_param] = str(next_cursor)
            else:
                break
            continue

        if page_param:
            current = int(request_query.get(page_param, 0) or 0)
            step_raw = request_query.get(limit_param) if limit_param else 100
            step = int(step_raw) if step_raw is not None else 100
            if step <= 0:
                step = 100
            request_query[page_param] = current + step
            continue
        break

    return _build_payload(
        operation=str(entry.get("operation") or ""),
        api_version=api_version,
        http_method="GET",
        request_path=path,
        path_params=path_params,
        query=request_query,
        status=response.status,
        url=response.url,
        is_binary=False,
        pagination={
            "mode": mode,
            "requested_pages": requested_pages,
            "fetched_pages": fetched_pages,
            "has_more": bool(has_more),
            "next_cursor": next_cursor,
        },
        data=all_data,
    )


def _resolve_command_entry(command_entries: list[dict[str, Any]]) -> dict[str, Any]:
    if len(command_entries) == 0:
        raise ValidationError("Missing command catalog entry")
    return sorted(
        command_entries,
        key=lambda entry: _api_version_rank(entry.get("api_version")),
        reverse=True,
    )[0]


def _cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    cfg = ctx["cfg"]
    if not isinstance(cfg, Config):
        raise ValidationError("Missing configuration")
    if not cfg.token:
        raise ValidationError("Missing PIPEDRIVE_API_TOKEN")

    payload = _run_read_request(
        cfg=cfg,
        http=ctx["http"],
        entry={
            "operation": "GET /users/me",
            "api_version": "v1",
            "path": "/users/me",
            "paging": {"mode": None, "page_param": None, "limit_param": None},
            "query_parameters": [],
            "path_parameters": [],
            "binary": False,
        },
        path="/users/me",
        path_params={},
        query={},
        max_pages=1,
    )
    payload["operation"] = "GET /api/v1/users/me"
    ctx["out"].emit(payload)
    return 0


def _cmd_read(args: Any, ctx: dict[str, Any]) -> int:
    command_entries = args.command_entries
    if not isinstance(command_entries, list) or not command_entries:
        raise ValidationError("Missing command registry entry")

    entry = _resolve_command_entry(command_entries)
    cfg = ctx.get("cfg")
    if not isinstance(cfg, Config):
        raise ValidationError("Missing configuration")
    if not cfg.token:
        raise ValidationError("Missing PIPEDRIVE_API_TOKEN")

    path_params, query, rendered_path = _build_request(entry, args)
    payload = _run_read_request(
        cfg=cfg,
        http=ctx["http"],
        entry=entry,
        path=rendered_path,
        path_params=path_params,
        query=query,
        max_pages=getattr(args, "max_pages", 1),
    )
    if entry.get("binary"):
        payload.setdefault("data", {})
        payload["data"]["path"] = rendered_path
    ctx["out"].emit(payload)
    return 0


def _cmd_onboarding(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    env_file = ctx["env_file"]
    env_path = Path(str(env_file))
    env_created = False
    if not env_path.exists():
        candidates = [env_path.parent / ".env.example", Path(".env.example")]
        for source in candidates:
            if source.exists():
                env_path.parent.mkdir(parents=True, exist_ok=True)
                env_path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
                env_created = True
                break
    out = ctx["out"]
    out.emit(
        {
            "ok": True,
            "onboarding": {
                "env_file": env_file,
                "env_created": env_created,
                "next_command": f"{TOOL_NAME} --env-file {env_file} auth check",
                "required_env_vars": {
                    "required": ["PIPEDRIVE_API_TOKEN"],
                    "required_one_of": ["PIPEDRIVE_API_DOMAIN", "PIPEDRIVE_BASE_URL"],
                    "optional": ["PIPEDRIVE_TIMEOUT_S"],
                },
            },
        }
    )
    return 0


def _add_command_parser(action_parser: argparse.ArgumentParser, entries: list[dict[str, Any]]) -> None:
    path_specs = _collect_param_specs(entries, "path_parameters")
    query_specs = _collect_param_specs(entries, "query_parameters")

    for name in sorted(path_specs):
        spec = path_specs[name]
        flag = str(spec.get("flag") or name).strip()
        if not flag:
            continue
        action_parser.add_argument(f"--{flag}", dest=arg_dest(name), required=False, help="Path parameter")

    for name in sorted(query_specs):
        spec = query_specs[name]
        flag = str(spec.get("flag") or name).strip()
        if not flag:
            continue
        enum = spec.get("enum")
        qtype = str(spec.get("type") or "").strip()

        help_text = str(qtype or "value")
        if isinstance(enum, list) and enum:
            help_text = "Allowed values: " + ", ".join(map(str, enum))

        action_parser.add_argument(f"--{flag}", dest=arg_dest(name), required=False, type=str, help=help_text)

    modes = {str((entry.get("paging") or {}).get("mode") or "").strip().lower() for entry in entries}
    if any(mode in {"offset", "cursor"} for mode in modes):
        action_parser.add_argument(
            "--max-pages",
            type=int,
            default=1,
            help=f"Maximum pages to fetch (1-{MAX_PAGES_LIMIT})",
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = _ToolArgumentParser(prog=TOOL_NAME)
    parser.add_argument("--version", action="store_true", help="Show tool and version")
    parser.add_argument("--config", default=None, help="Optional JSON file with base_url/api_domain/timeout_s")
    parser.add_argument("--env-file", default=".env", help="Optional .env path")
    parser.add_argument("--timeout-s", type=float, help="Optional timeout override")
    parser.add_argument("--verbose", action="store_true", help="Verbose HTTP logs")
    parser.add_argument("--debug", action="store_true", help="Show stack trace on errors")
    parser.add_argument("--log-file", default=None, help="Optional audit log JSONL path")
    parser.add_argument("--output", choices=("json", "text"), default="json", help="Output format")

    sub = parser.add_subparsers(dest="command_root", required=False, parser_class=_ToolArgumentParser)

    onboarding = sub.add_parser("onboarding", help="Setup instructions")
    onboarding.set_defaults(func=_cmd_onboarding, requires_api=False)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test against /users/me")
    auth_check.set_defaults(func=_cmd_auth_check, requires_api=True)

    groups: dict[str, argparse._SubParsersAction] = {}
    grouped = _group_catalog_entries(load_endpoint_catalog())

    for command_key, entries in sorted(grouped.items(), key=lambda item: item[0]):
        group, action = command_key.split(" ", 1)
        if group not in groups:
            group_parser = sub.add_parser(group, help=f"{group} operations")
            groups[group] = group_parser.add_subparsers(dest=f"{group}_action", required=True, parser_class=_ToolArgumentParser)

        action_parser = groups[group].add_parser(action, help=f"{command_key} command")
        action_parser.set_defaults(
            func=_cmd_read,
            requires_api=True,
            command_entries=entries,
            command_tokens=command_key,
        )
        _add_command_parser(action_parser, entries)

    return parser


def main(argv: list[str]) -> int:
    parser = _build_parser()
    out = Output(mode=_output_mode_from_argv(argv))

    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    except SystemExit as e:
        try:
            return int(e.code or 0)
        except Exception:
            return 1

    debug = bool(getattr(args, "debug", False))
    cfg: Config | None = None
    audit = AuditLogger(path=getattr(args, "log_file", None), enabled=bool(getattr(args, "log_file", None)))
    audit.bind_context(
        {
            "tool": TOOL_NAME,
            "version": __version__,
            "command": f"{TOOL_NAME} {' '.join(argv)}",
            "env_file": str(getattr(args, "env_file", ".env")),
        }
    )
    audit.write(
        "command_start",
        {"argv": argv, "debug": debug, "has_config": bool(getattr(args, "config", None))},
    )

    try:
        if bool(args.version):
            out.emit({"ok": True, "tool": TOOL_NAME, "version": __version__})
            audit.write("command_ok", {"exit_code": 0, "output": out.last})
            return 0

        if not getattr(args, "func", None):
            out.emit({"ok": False, "error": "Missing command", "error_type": "ValidationError"})
            audit.write("command_error", {"error_type": "ValidationError", "error": "Missing command"})
            return 1

        if bool(getattr(args, "requires_api", False)):
            try:
                cfg = load_config(
                    str(getattr(args, "env_file", ".env")),
                    config_file=getattr(args, "config", None),
                )
            except RuntimeError as e:
                raise ValidationError(str(e)) from e

            timeout_override = getattr(args, "timeout_s", None)
            if timeout_override is not None:
                cfg = Config(
                    base_url=cfg.base_url,
                    api_domain=cfg.api_domain,
                    token=cfg.token,
                    timeout_s=float(timeout_override),
                )

        timeout = cfg.timeout_s if cfg else 30.0
        if timeout <= 0:
            raise ValidationError("--timeout-s must be > 0")

        http = HttpClient(
            timeout_s=timeout,
            verbose=bool(getattr(args, "verbose", False)),
            user_agent=f"{TOOL_NAME}/{__version__}",
        )

        ctx = {
            "cfg": cfg,
            "out": out,
            "env_file": str(getattr(args, "env_file", ".env")),
            "http": http,
            "audit": audit,
            "debug": debug,
        }

        rc = int(args.func(args, ctx))
        audit.write("command_ok", {"exit_code": rc, "output": out.last})
        return rc
    except ValidationError as e:
        _emit_error(out=out, error=e, cfg=cfg, debug=debug, audit=audit)
        return 1
    except ToolError as e:
        _emit_error(out=out, error=e, cfg=cfg, debug=debug, audit=audit)
        return 1
    except Exception as e:  # noqa: BLE001
        _emit_error(out=out, error=e, cfg=cfg, debug=debug, audit=audit)
        return 1
    finally:
        audit.close()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
