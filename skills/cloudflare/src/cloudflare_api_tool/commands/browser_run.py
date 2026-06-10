from __future__ import annotations

import argparse
import json
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from . import openapi_runner as openapi_runner_cmd
from ..errors import ValidationError


def _opt_str(v) -> str | None:  # noqa: ANN001
    s = str(v or "").strip()
    return s or None


def _account_path_params(args) -> dict[str, str]:  # noqa: ANN001
    account_id = _opt_str(getattr(args, "account_id", None))
    if not account_id:
        return {}
    return {"account_id": account_id}


def _require_out(args) -> str:  # noqa: ANN001
    out = _opt_str(getattr(args, "out", None))
    if not out:
        raise ValidationError("Missing --out")
    return out


def _query_args(args) -> list[str]:  # noqa: ANN001
    out: list[str] = []
    cache_ttl = getattr(args, "cache_ttl", None)
    if cache_ttl is not None:
        if int(cache_ttl) < 0:
            raise ValidationError("--cache-ttl must be >= 0")
        out.append(f"cacheTTL={int(cache_ttl)}")
    return out


def _input_body(args, *, allow_html: bool) -> dict[str, object]:  # noqa: ANN001
    body: dict[str, object] = {}
    url = _opt_str(getattr(args, "url", None))
    html = _opt_str(getattr(args, "html", None)) if allow_html else None
    if allow_html:
        if bool(url) == bool(html):
            raise ValidationError("Provide exactly one of --url or --html")
    elif not url:
        raise ValidationError("Missing --url")

    if url:
        body["url"] = url
    elif html:
        body["html"] = html

    user_agent = _opt_str(getattr(args, "user_agent", None))
    if user_agent:
        body["userAgent"] = user_agent

    goto_timeout_ms = getattr(args, "goto_timeout_ms", None)
    goto_wait_until = _opt_str(getattr(args, "goto_wait_until", None))
    goto_options: dict[str, object] = {}
    if goto_timeout_ms is not None:
        if int(goto_timeout_ms) < 0:
            raise ValidationError("--goto-timeout-ms must be >= 0")
        goto_options["timeout"] = int(goto_timeout_ms)
    if goto_wait_until:
        goto_options["waitUntil"] = goto_wait_until
    if goto_options:
        body["gotoOptions"] = goto_options

    wait_for_timeout_ms = getattr(args, "wait_for_timeout_ms", None)
    if wait_for_timeout_ms is not None:
        if int(wait_for_timeout_ms) < 0:
            raise ValidationError("--wait-for-timeout-ms must be >= 0")
        body["waitForTimeout"] = int(wait_for_timeout_ms)

    wait_for_selector = _opt_str(getattr(args, "wait_for_selector", None))
    wait_for_selector_timeout_ms = getattr(args, "wait_for_selector_timeout_ms", None)
    wait_for_selector_visible = bool(getattr(args, "wait_for_selector_visible", False))
    if wait_for_selector:
        wait_obj: dict[str, object] = {"selector": wait_for_selector}
        if wait_for_selector_timeout_ms is not None:
            if int(wait_for_selector_timeout_ms) < 0:
                raise ValidationError("--wait-for-selector-timeout-ms must be >= 0")
            wait_obj["timeout"] = int(wait_for_selector_timeout_ms)
        if wait_for_selector_visible:
            wait_obj["visible"] = True
        body["waitForSelector"] = wait_obj

    reject_resource_types = [str(v).strip() for v in (getattr(args, "reject_resource_type", None) or []) if str(v).strip()]
    if reject_resource_types:
        body["rejectResourceTypes"] = reject_resource_types

    viewport_width = getattr(args, "viewport_width", None)
    viewport_height = getattr(args, "viewport_height", None)
    if viewport_width is not None or viewport_height is not None:
        if viewport_width is None or viewport_height is None:
            raise ValidationError("Provide both --viewport-width and --viewport-height")
        if int(viewport_width) <= 0 or int(viewport_height) <= 0:
            raise ValidationError("--viewport-width and --viewport-height must be > 0")
        body["viewport"] = {"width": int(viewport_width), "height": int(viewport_height)}

    return body


@contextmanager
def _temp_json_file(obj: dict[str, object]) -> Iterator[str]:
    fh = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
    try:
        with fh:
            json.dump(obj, fh, ensure_ascii=False)
        yield fh.name
    finally:
        Path(fh.name).unlink(missing_ok=True)


def _delegate_openapi_call(
    *,
    ctx: dict,
    method: str,
    path_template: str,
    path_params: dict[str, str] | None = None,
    query: list[str] | None = None,
    body_json_file: str | None = None,
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
        content_type=None,
        out=out,
        overwrite=bool(overwrite),
    )
    return int(openapi_runner_cmd.cmd_openapi_call(ns, ctx))


def cmd_browser_run_markdown(args, ctx) -> int:  # noqa: ANN001
    body = _input_body(args, allow_html=True)
    with _temp_json_file(body) as body_file:
        return _delegate_openapi_call(
            ctx=ctx,
            method="POST",
            path_template="/accounts/{account_id}/browser-rendering/markdown",
            path_params=_account_path_params(args),
            query=_query_args(args),
            body_json_file=body_file,
            out=_require_out(args),
            overwrite=bool(getattr(args, "overwrite", False)),
        )


def cmd_browser_run_links(args, ctx) -> int:  # noqa: ANN001
    body = _input_body(args, allow_html=True)
    if bool(getattr(args, "visible_links_only", False)):
        body["visibleLinksOnly"] = True
    if bool(getattr(args, "exclude_external_links", False)):
        body["excludeExternalLinks"] = True
    with _temp_json_file(body) as body_file:
        return _delegate_openapi_call(
            ctx=ctx,
            method="POST",
            path_template="/accounts/{account_id}/browser-rendering/links",
            path_params=_account_path_params(args),
            query=_query_args(args),
            body_json_file=body_file,
            out=_require_out(args),
            overwrite=bool(getattr(args, "overwrite", False)),
        )


def cmd_browser_run_scrape(args, ctx) -> int:  # noqa: ANN001
    selectors = [str(v).strip() for v in (getattr(args, "selector", None) or []) if str(v).strip()]
    if not selectors:
        raise ValidationError("Provide at least one --selector")
    body = _input_body(args, allow_html=True)
    body["elements"] = [{"selector": selector} for selector in selectors]
    with _temp_json_file(body) as body_file:
        return _delegate_openapi_call(
            ctx=ctx,
            method="POST",
            path_template="/accounts/{account_id}/browser-rendering/scrape",
            path_params=_account_path_params(args),
            query=_query_args(args),
            body_json_file=body_file,
            out=_require_out(args),
            overwrite=bool(getattr(args, "overwrite", False)),
        )


def cmd_browser_run_screenshot(args, ctx) -> int:  # noqa: ANN001
    body = _input_body(args, allow_html=True)
    if bool(getattr(args, "full_page", False)):
        body["fullPage"] = True
    if bool(getattr(args, "omit_background", False)):
        body["omitBackground"] = True
    if _opt_str(getattr(args, "image_type", None)):
        body["type"] = _opt_str(getattr(args, "image_type", None))
    with _temp_json_file(body) as body_file:
        return _delegate_openapi_call(
            ctx=ctx,
            method="POST",
            path_template="/accounts/{account_id}/browser-rendering/screenshot",
            path_params=_account_path_params(args),
            query=_query_args(args),
            body_json_file=body_file,
            out=_require_out(args),
            overwrite=bool(getattr(args, "overwrite", False)),
        )


def cmd_browser_run_crawl(args, ctx) -> int:  # noqa: ANN001
    body = _input_body(args, allow_html=False)
    depth = getattr(args, "depth", None)
    limit = getattr(args, "limit", None)
    source = _opt_str(getattr(args, "source", None))
    if depth is not None:
        if int(depth) < 1:
            raise ValidationError("--depth must be >= 1")
        body["depth"] = int(depth)
    if limit is not None:
        if int(limit) < 1:
            raise ValidationError("--limit must be >= 1")
        body["limit"] = int(limit)
    if source:
        body["source"] = source
    formats = [str(v).strip() for v in (getattr(args, "format", None) or []) if str(v).strip()]
    if formats:
        body["formats"] = formats
    include_patterns = [str(v).strip() for v in (getattr(args, "include_pattern", None) or []) if str(v).strip()]
    exclude_patterns = [str(v).strip() for v in (getattr(args, "exclude_pattern", None) or []) if str(v).strip()]
    if include_patterns:
        body["includePatterns"] = include_patterns
    if exclude_patterns:
        body["excludePatterns"] = exclude_patterns
    if bool(getattr(args, "include_subdomains", False)):
        body["includeSubdomains"] = True
    if bool(getattr(args, "include_external_links", False)):
        body["includeExternalLinks"] = True
    if bool(getattr(args, "no_render", False)):
        body["render"] = False
    with _temp_json_file(body) as body_file:
        return _delegate_openapi_call(
            ctx=ctx,
            method="POST",
            path_template="/accounts/{account_id}/browser-rendering/crawl",
            path_params=_account_path_params(args),
            query=_query_args(args),
            body_json_file=body_file,
            out=_require_out(args),
            overwrite=bool(getattr(args, "overwrite", False)),
        )


def cmd_browser_run_crawl_result(args, ctx) -> int:  # noqa: ANN001
    job_id = _opt_str(getattr(args, "job_id", None))
    if not job_id:
        raise ValidationError("Missing --job-id")
    query = _query_args(args)
    limit = getattr(args, "limit", None)
    cursor = _opt_str(getattr(args, "cursor", None))
    status = _opt_str(getattr(args, "status", None))
    if limit is not None:
        if int(limit) < 1:
            raise ValidationError("--limit must be >= 1")
        query.append(f"limit={int(limit)}")
    if cursor:
        query.append(f"cursor={cursor}")
    if status:
        query.append(f"status={status}")
    path_params = _account_path_params(args)
    path_params["job_id"] = job_id
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/browser-rendering/crawl/{job_id}",
        path_params=path_params,
        query=query,
        out=_require_out(args),
        overwrite=bool(getattr(args, "overwrite", False)),
    )
