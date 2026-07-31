from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any
from urllib.parse import quote, urlparse

import requests

from .config import OFFICIAL_NAMEBRIGHT_TOKEN_URL, Config
from .errors import NotSupportedError, ToolError
from .http import HttpClient, HttpResponse
from .oauth_tokens import TokenCache
from .operations import OPERATIONS, OperationSpec
from .redaction import PII_SAFE_EXTRA_KEYS, redact_object

_ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE"}
_ALLOWED_FIELD_LOCATIONS = {"path", "query", "body"}
_PLACEHOLDER_RE = re.compile(r"{([^{}]+)}")


def _safe_now() -> float:
    return time.time()


def _parse_retry_after(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return max(0.0, float(str(value).strip()))
    except Exception:
        return 0.0


def _json_error(message: str) -> str:
    return message


def _build_safe_error(*, method: str, url: str, status: int) -> str:
    return f"{method} {url} returned HTTP {status}"


@dataclass(frozen=True)
class ResponseEnvelope:
    status: int
    headers: dict[str, str]
    payload: Any
    snapshot_sha256: str | None = None
    _contact_field_compare: Callable[[dict[str, Any]], dict[str, list[str]]] | None = dataclass_field(
        default=None,
        repr=False,
        compare=False,
    )

    def compare_contact_fields(
        self,
        expected: dict[str, Any],
    ) -> dict[str, list[str]] | None:
        if self._contact_field_compare is None:
            return None
        return self._contact_field_compare(dict(expected))


def _canonical_sha256(value: Any) -> str:
    blob = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _normalize_contact_key(value: Any) -> str:
    return str(value).lower().replace("-", "").replace("_", "").replace(" ", "")


def _normalize_contact_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def _collect_contact_fields(
    value: Any,
    out: dict[str, list[str]],
) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized_key = _normalize_contact_key(key)
            if isinstance(item, (dict, list, tuple)):
                _collect_contact_fields(item, out)
            elif item is not None:
                out.setdefault(normalized_key, []).append(
                    _normalize_contact_value(item)
                )
    elif isinstance(value, (list, tuple)):
        for item in value:
            _collect_contact_fields(item, out)


def _contact_field_comparator(
    raw_payload: Any,
) -> Callable[[dict[str, Any]], dict[str, list[str]]]:
    raw_fields: dict[str, list[str]] = {}
    _collect_contact_fields(raw_payload, raw_fields)

    def compare(expected: dict[str, Any]) -> dict[str, list[str]]:
        matched: list[str] = []
        mismatched: list[str] = []
        unavailable: list[str] = []
        for field_name in sorted(expected):
            candidates = raw_fields.get(_normalize_contact_key(field_name), [])
            if not candidates:
                unavailable.append(field_name)
                continue
            expected_value = _normalize_contact_value(expected[field_name])
            if all(candidate == expected_value for candidate in candidates):
                matched.append(field_name)
            else:
                mismatched.append(field_name)
        return {
            "matched": matched,
            "mismatched": mismatched,
            "unavailable": unavailable,
        }

    return compare


class NameBrightClient:
    """
    Transport client for NameBright API operations.
    """

    def __init__(
        self,
        *,
        cfg: Config,
        timeout_s: float,
        verbose: bool,
        user_agent: str,
        transport: requests.Session | None = None,
    ):
        self._cfg = cfg
        self._http = HttpClient(
            timeout_s=timeout_s,
            verbose=verbose,
            user_agent=user_agent,
            transport=transport,
        )
        self._requests: deque[float] = deque()
        self._client_id = cfg.client_id
        self._client_secret = cfg.client_secret
        self._token_cache = TokenCache()
        self._auth_spec = next(
            op for op in OPERATIONS if op.family == "auth" and op.command == "auth token"
        )

    @staticmethod
    def _normalize_path(path: str) -> str:
        clean = str(path or "").strip()
        return clean.lstrip("/") if clean else ""

    @staticmethod
    def _serialize_value(value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    @staticmethod
    def _as_dict(values: dict[str, Any] | None) -> dict[str, Any]:
        if values is None:
            return {}
        if not isinstance(values, dict):
            raise RuntimeError("values must be a mapping")
        return dict(values)

    @staticmethod
    def _replace_placeholders(template: str, values: dict[str, Any]) -> str:
        out = template
        for key in _PLACEHOLDER_RE.findall(template):
            if key not in values:
                raise RuntimeError(f"Missing required placeholder value: {key}")
            replacement = quote(str(values[key]), safe="")
            out = out.replace(f"{{{key}}}", replacement)
        if _PLACEHOLDER_RE.search(out):
            raise RuntimeError(f"Unresolved placeholders in path: {out}")
        return out

    @staticmethod
    def _strip_query(url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    def _validate_endpoint(self, *, url: str, method: str, allow_auth: bool) -> None:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme.lower() != "https":
            raise ToolError(f"Refused non-HTTPS request for {method}: {parsed.scheme or '<missing>'}")
        if host != "api.namebright.com":
            raise ToolError(f"Refused non-NameBright host for {method}: {host}")
        path = (parsed.path or "").rstrip("/")
        if allow_auth:
            if path != "/auth/token":
                raise ToolError("Refused: OAuth endpoint must be https://api.namebright.com/auth/token")
        else:
            if not (path == "/rest" or path.startswith("/rest/")):
                raise ToolError("Refused: Domain API endpoint must use https://api.namebright.com/rest")

    def _throttle(self) -> None:
        now = _safe_now()
        while self._requests and now - self._requests[0] >= 30.0:
            self._requests.popleft()

        while True:
            if self._requests and now - self._requests[-1] < 1.0:
                wait = 1.0 - (now - self._requests[-1])
                print(f"[namebright] waiting {wait:.2f}s to respect 1 requests/second", file=sys.stderr)
                time.sleep(wait)
                now = _safe_now()
                while self._requests and now - self._requests[0] >= 30.0:
                    self._requests.popleft()
                continue

            if len(self._requests) >= 30:
                wait = self._requests[0] + 30.0 - now
                if wait > 30.0:
                    wait = 30.0
                if wait > 0:
                    print(
                        f"[namebright] waiting {wait:.2f}s to satisfy 30 requests/30 seconds",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    now = _safe_now()
                    while self._requests and now - self._requests[0] >= 30.0:
                        self._requests.popleft()
                    continue
            break

        self._requests.append(now)

    def _request(
        self,
        *,
        method: str,
        full_url: str,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        auth_header: str | None,
        allow_auth: bool,
        retry_on_429: bool = True,
        _attempted_429_retry: bool = False,
    ) -> HttpResponse:
        self._validate_endpoint(url=full_url, method=method, allow_auth=allow_auth)
        self._throttle()

        headers = {} if auth_header is None else {"Authorization": auth_header}
        request_method = str(method or "").upper()
        request_body = body if request_method in {"POST", "PUT"} else None

        resp = self._http.request(
            request_method,
            full_url,
            headers=headers,
            params=params or {},
            data=request_body,
            json_body=None,
            raise_on_error=False,
        )

        if resp.status == 429 and retry_on_429 and not _attempted_429_retry:
            wait = _parse_retry_after(resp.headers.get("retry-after"))
            if wait > 30.0:
                wait = 30.0
            print(f"[namebright] HTTP 429 received; waiting {wait:.2f}s before one retry", file=sys.stderr)
            if wait > 0:
                time.sleep(wait)
            return self._request(
                method=request_method,
                full_url=full_url,
                params=params,
                body=body,
                auth_header=auth_header,
                allow_auth=allow_auth,
                retry_on_429=False,
                _attempted_429_retry=True,
            )

        if resp.status >= 400:
            raise RuntimeError(_build_safe_error(method=request_method, url=self._strip_query(full_url), status=resp.status))
        return resp

    def _parse_json(self, response: HttpResponse) -> Any:
        if not response.body:
            return None
        try:
            return response.json()
        except Exception:
            raise RuntimeError(_json_error("Invalid JSON response")) from None

    def _build_url(self, *, path: str, allow_auth: bool) -> str:
        if allow_auth:
            return OFFICIAL_NAMEBRIGHT_TOKEN_URL
        cleaned = self._normalize_path(path)
        return f"{self._cfg.base_url}/{cleaned}" if cleaned else self._cfg.base_url

    def _build_operation_payload(
        self,
        spec: OperationSpec,
        *,
        values: dict[str, Any] | None,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        values_map = self._as_dict(values)
        field_by_name = {field.api_name: field for field in spec.fields}
        cli_field_names = {
            field.api_name for field in spec.fields if field.source == "cli"
        }

        extras = set(values_map.keys()) - cli_field_names
        if extras:
            raise RuntimeError(f"Unknown operation fields: {', '.join(sorted(extras))}")

        resolved: dict[str, Any] = {}
        for field in spec.fields:
            if field.location not in _ALLOWED_FIELD_LOCATIONS:
                continue
            if field.api_name in values_map:
                raw = values_map[field.api_name]
            elif field.source == "config":
                if field.api_name == "client_id":
                    raw = self._client_id
                elif field.api_name == "client_secret":
                    raw = self._client_secret
                else:
                    raw = field.default
            else:
                raw = field.default
            if raw is None or raw == "":
                if field.required:
                    raise RuntimeError(f"Missing required value for {field.api_name}")
                continue
            resolved[field.api_name] = raw

        path_spec, _, query_template = self._normalize_path(spec.path).partition("?")

        path_values: dict[str, Any] = {}
        query_values: dict[str, Any] = {}
        body_values: dict[str, Any] = {}
        for name, value in resolved.items():
            field_spec = field_by_name.get(name)
            if field_spec is None:
                continue
            if field_spec.location == "path":
                path_values[name] = value
            elif field_spec.location == "query":
                query_values[name] = value
            elif field_spec.location == "body":
                body_values[name] = value

        resolved_path = self._replace_placeholders(path_spec, path_values)

        if query_template:
            for token in _PLACEHOLDER_RE.findall(query_template):
                if token not in query_values and token not in {f.api_name for f in spec.fields if f.location == "query"}:
                    if field_by_name.get(token) is None:
                        raise RuntimeError(f"Operation spec has unresolved query placeholder: {token}")

        params: dict[str, str] = {}
        for key, value in query_values.items():
            params[key] = self._serialize_value(value)

        if query_template:
            for raw_part in query_template.split("&"):
                if not raw_part or "=" not in raw_part:
                    continue
                param_name, param_value = raw_part.split("=", 1)
                placeholder_match = _PLACEHOLDER_RE.fullmatch(param_value)
                if placeholder_match:
                    name = placeholder_match.group(1)
                    if name in query_values:
                        params[param_name] = self._serialize_value(query_values[name])
                    else:
                        field_spec = field_by_name.get(name)
                        if field_spec is None:
                            raise RuntimeError(f"Missing query placeholder value: {name}")
                        if field_spec.required:
                            raise RuntimeError(f"Missing required query value: {name}")
                else:
                    if "{" not in param_value and "}" not in param_value:
                        params[param_name] = param_value

        body: dict[str, Any] = {}
        if spec.method in {"POST", "PUT"}:
            body = body_values

        if spec.method in {"POST", "PUT"} and not body:
            body = {}

        return str(spec.method or "").upper(), resolved_path, params, body

    def _is_known_operation(self, spec: OperationSpec) -> bool:
        return spec in OPERATIONS

    def _redact_response(self, spec: OperationSpec, payload: Any) -> Any:
        if payload is None:
            return None
        keys_to_redact = set(PII_SAFE_EXTRA_KEYS)
        keys_to_redact.update(spec.secret_response_fields)
        return redact_object(payload, redact_pii=True, extra_sensitive_keys=tuple(keys_to_redact))

    def _get_token_status_payload(self) -> dict[str, Any]:
        status = self._token_cache.status(path=self._cfg.token_url, now=_safe_now())
        safe_fields = [name for name in status.fields if name not in {"access_token", "refresh_token"}]
        return {
            "exists": status.exists,
            "updated_at_utc": status.updated_at_utc,
            "fields": safe_fields,
            "has_refresh_token": status.has_refresh_token,
            "expires_at_utc": status.expires_at_utc,
        }

    def _request_token(self) -> str:
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        response = self._request(
            method="POST",
            full_url=OFFICIAL_NAMEBRIGHT_TOKEN_URL,
            params=None,
            body=payload,
            auth_header=None,
            allow_auth=True,
            retry_on_429=False,
        )
        response_payload = self._parse_json(response)
        if not isinstance(response_payload, dict):
            raise RuntimeError("Token endpoint returned unexpected JSON object")
        token = str(response_payload.get("access_token") or "").strip()
        if not token:
            raise RuntimeError("Token endpoint did not return access_token")
        self._token_cache.set(response_payload, now=_safe_now())
        return token

    def _acquire_token(self) -> str:
        token = self._token_cache.get(now=_safe_now())
        if token is not None:
            return token
        token = self._request_token()
        if not token:
            raise RuntimeError("Token acquisition failed")
        return token

    def execute_operation(self, spec: OperationSpec, *, values: dict[str, Any] | None = None) -> ResponseEnvelope:
        if not isinstance(spec, OperationSpec) or not self._is_known_operation(spec):
            raise NotSupportedError("Unsupported NameBright operation")
        if spec.method not in _ALLOWED_METHODS:
            raise NotSupportedError(f"Unsupported HTTP method for NameBright operation: {spec.method}")

        method, path, params, body = self._build_operation_payload(spec, values=values)
        is_auth = spec.family == "auth" and self._normalize_path(spec.path) == "token"
        full_url = self._build_url(path=path, allow_auth=is_auth)

        if is_auth:
            response = self._request(
                method=method,
                full_url=OFFICIAL_NAMEBRIGHT_TOKEN_URL,
                params=params,
                body=body,
                auth_header=None,
                allow_auth=True,
                retry_on_429=False,
            )
            response_payload = self._parse_json(response)
            if not isinstance(response_payload, dict):
                raise RuntimeError("Token endpoint returned unexpected JSON object")
            token = str(response_payload.get("access_token") or "").strip()
            if not token:
                raise RuntimeError("Token endpoint did not return access_token")
            self._token_cache.set(response_payload, now=_safe_now())
            return ResponseEnvelope(
                status=response.status,
                headers=dict(response.headers),
                payload={"ok": True, "token_status": self._get_token_status_payload()},
            )

        token = self._acquire_token()
        response = self._request(
            method=method,
            full_url=full_url,
            params=params,
            body=body,
            auth_header=f"Bearer {token}",
            allow_auth=False,
        )
        response_payload = self._parse_json(response)
        is_contact_response = spec.family == "contacts"
        return ResponseEnvelope(
            status=response.status,
            headers=dict(response.headers),
            payload=self._redact_response(spec, response_payload),
            snapshot_sha256=(
                _canonical_sha256(response_payload)
                if is_contact_response
                else None
            ),
            _contact_field_compare=(
                _contact_field_comparator(response_payload)
                if is_contact_response
                else None
            ),
        )

    def request_token_status(self) -> dict[str, Any]:
        self._acquire_token()
        return {
            "ok": True,
            "token_status": redact_object(self._get_token_status_payload(), redact_pii=False),
        }
