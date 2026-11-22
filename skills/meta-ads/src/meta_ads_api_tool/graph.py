from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlsplit

from .config import Config, normalize_ad_account_id
from .errors import RemoteApiError, ValidationError
from .http import HttpClient


def _clean_path(path: str) -> str:
    p = str(path or "").strip()
    p = p.lstrip("/")
    return p


def _build_versioned_url(cfg: Config, path: str) -> str:
    # Graph expects base_url + /vXX.X/<path>
    base = cfg.base_url.rstrip("/") + "/"
    version_prefix = cfg.api_version.strip().strip("/")
    if not version_prefix:
        raise ValidationError("Missing api version")
    return urljoin(base, f"{version_prefix}/{_clean_path(path)}")


def _parse_kv_pairs(pairs: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in pairs or []:
        if "=" not in raw:
            raise ValidationError(f"Invalid --param value (expected k=v): {raw}")
        k, v = raw.split("=", 1)
        k = k.strip()
        if not k:
            raise ValidationError(f"Invalid --param value (empty key): {raw}")
        out[k] = v
    return out


@dataclass(frozen=True)
class PageResult:
    data: list[Any]
    paging: dict[str, Any] | None
    raw_pages: int
    incomplete_reason: str | None = None


class GraphClient:
    def __init__(self, *, cfg: Config, http: HttpClient):
        self._cfg = cfg
        self._http = http

    def _headers(self) -> dict[str, str]:
        tok = self._cfg.access_token
        if not tok:
            raise ValidationError("Missing META_ADS_ACCESS_TOKEN")
        return {"Authorization": f"Bearer {tok}"}

    def _with_access_token_param(self, url: str | None, params: dict[str, Any] | None) -> dict[str, Any]:
        tok = self._cfg.access_token
        if not tok:
            raise ValidationError("Missing META_ADS_ACCESS_TOKEN")
        params = dict(params or {})
        if "access_token" in params:
            return params
        if url and re.search(r"(?i)(?:^|[?&])access_token=", url):
            return params
        params["access_token"] = tok
        return params

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._get(_build_versioned_url(self._cfg, path), params=params)

    def get_url(self, url: str) -> dict[str, Any]:
        return self._get(urljoin(self._cfg.base_url.rstrip("/") + "/", url))

    def _get(self, url: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        requested = urlsplit(url)
        configured = urlsplit(self._cfg.base_url)
        if (
            requested.scheme != configured.scheme
            or requested.hostname != configured.hostname
            or (requested.port or (443 if requested.scheme == "https" else 80))
            != (configured.port or (443 if configured.scheme == "https" else 80))
            or requested.username is not None
            or requested.password is not None
        ):
            raise RemoteApiError("Meta Ads request would leave the configured API host")
        resp = self._http.request(
            "GET",
            url,
            headers=self._headers(),
            params=self._with_access_token_param(url, params),
            retries=self._cfg.max_retries,
            allow_redirects=False,
        )
        payload = resp.json()
        self._raise_graph_error(payload)
        if not isinstance(payload, dict):
            raise RemoteApiError("Unexpected response shape (expected JSON object)")
        return payload

    def _raise_graph_error(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        err = payload.get("error")
        if not isinstance(err, dict):
            return
        msg = str(err.get("message") or "Graph API error").strip()
        etype = str(err.get("type") or "").strip() or None
        code = err.get("code")
        subcode = err.get("error_subcode")
        fbtrace = str(err.get("fbtrace_id") or "").strip() or None

        parts: list[str] = [msg]
        meta: list[str] = []
        if etype:
            meta.append(f"type={etype}")
        if code is not None:
            meta.append(f"code={code}")
        if subcode is not None:
            meta.append(f"subcode={subcode}")
        if fbtrace:
            meta.append(f"fbtrace_id={fbtrace}")
        if meta:
            parts.append("(" + ", ".join(meta) + ")")
        message = HttpClient.redact_url(" ".join(parts))
        if self._cfg.access_token:
            message = message.replace(self._cfg.access_token, "***REDACTED***")
        raise RemoteApiError(message)

    def list_edge(
        self,
        *,
        object_id: str,
        edge: str,
        params: dict[str, Any] | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> PageResult:
        obj = str(object_id or "").strip()
        if not obj:
            raise ValidationError("Missing object_id")
        ed = str(edge or "").strip().lstrip("/")
        if not ed:
            raise ValidationError("Missing edge")

        path = f"{obj}/{ed}"
        first = self.get(path, params=params)
        return self._paginate(path=path, params=params, first_payload=first, max_pages=max_pages, max_items=max_items)

    def list_me_adaccounts(
        self, *, params: dict[str, Any] | None = None, max_pages: int | None = None, max_items: int | None = None
    ) -> PageResult:
        path = "me/adaccounts"
        first = self.get(path, params=params)
        return self._paginate(path=path, params=params, first_payload=first, max_pages=max_pages, max_items=max_items)

    def get_ad_account(self, ad_account_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        aid = normalize_ad_account_id(ad_account_id)
        if not aid:
            raise ValidationError("Missing ad account id")
        return self.get(aid, params=params)

    def _paginate(
        self,
        *,
        path: str,
        params: dict[str, Any] | None,
        first_payload: dict[str, Any],
        max_pages: int | None,
        max_items: int | None,
    ) -> PageResult:
        max_pages_i = int(max_pages) if max_pages is not None else 50
        max_items_i = int(max_items) if max_items is not None else 0
        if max_pages_i <= 0:
            raise ValidationError("--max-pages must be > 0")
        if max_items_i < 0:
            raise ValidationError("--max-items must be >= 0")

        payload = first_payload
        out: list[Any] = []
        pages = 0
        seen: set[tuple[str, str]] = set()
        reason = None
        while True:
            data = payload.get("data")
            if not isinstance(data, list):
                raise RemoteApiError("Meta Ads response is missing a valid data list")
            out.extend(data)
            pages += 1
            paging = payload.get("paging")
            next_url = paging.get("next") if isinstance(paging, dict) else None
            cursors = paging.get("cursors") if isinstance(paging, dict) else None
            after = cursors.get("after") if isinstance(cursors, dict) else None
            if isinstance(next_url, str) and next_url.strip():
                next_page = ("url", next_url.strip())
            elif isinstance(after, str) and after.strip():
                next_page = ("after", after.strip())
            else:
                next_page = None

            if max_items_i and (len(out) > max_items_i or (len(out) == max_items_i and next_page)):
                out = out[:max_items_i]
                reason = "max_items"
                break
            if next_page is None:
                break
            if pages >= max_pages_i:
                reason = "max_pages"
                break
            if next_page in seen:
                reason = "repeated_page"
                break
            seen.add(next_page)
            kind, value = next_page
            if kind == "url":
                payload = self.get_url(value)
            else:
                payload = self.get(path, params={**(params or {}), "after": value})
        return PageResult(
            data=out, paging=_redact_paging_urls(paging), raw_pages=pages, incomplete_reason=reason
        )


__all__ = ["GraphClient", "PageResult", "_parse_kv_pairs"]


def _redact_paging_urls(paging: Any) -> dict[str, Any] | None:
    """
    Redact secrets from paging URLs before returning them to callers.

    Meta Graph pagination URLs may contain `access_token=...`. We must never
    surface those tokens in stdout JSON or logs.
    """
    if not isinstance(paging, dict):
        return None
    out: dict[str, Any] = dict(paging)
    for k in ("next", "previous"):
        v = out.get(k)
        if isinstance(v, str) and v.strip():
            out[k] = HttpClient.redact_url(v.strip())
    return out
