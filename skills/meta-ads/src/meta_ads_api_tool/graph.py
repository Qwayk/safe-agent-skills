from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

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
        url = _build_versioned_url(self._cfg, path)
        resp = self._http.request(
            "GET",
            url,
            headers=self._headers(),
            params=self._with_access_token_param(url, params),
            retries=self._cfg.max_retries,
        )
        payload = resp.json()
        self._raise_graph_error(payload)
        if not isinstance(payload, dict):
            raise RemoteApiError("Unexpected response shape (expected JSON object)")
        return payload

    def get_url(self, url: str) -> dict[str, Any]:
        resp = self._http.request(
            "GET",
            url,
            headers=self._headers(),
            params=self._with_access_token_param(url, None),
            retries=self._cfg.max_retries,
        )
        payload = resp.json()
        self._raise_graph_error(payload)
        if not isinstance(payload, dict):
            raise RemoteApiError("Unexpected response shape (expected JSON object)")
        return payload

    @staticmethod
    def _raise_graph_error(payload: Any) -> None:
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
        raise RemoteApiError(" ".join(parts))

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

        data = first_payload.get("data")
        if not isinstance(data, list):
            # Not a list response; treat as a single-page empty data set.
            return PageResult(data=[], paging=None, raw_pages=1)

        out: list[Any] = list(data)
        pages = 1
        paging = first_payload.get("paging")
        base_params: dict[str, Any] = dict(params or {})
        seen_next: set[str] = set()
        seen_after: set[str] = set()
        while True:
            if pages >= max_pages_i:
                break
            if max_items_i and len(out) >= max_items_i:
                out = out[:max_items_i]
                break
            if not isinstance(paging, dict):
                break
            nxt = paging.get("next")
            cursor_after: str | None = None
            if isinstance(nxt, str) and nxt.strip():
                nxt_s = nxt.strip()
                if nxt_s in seen_next:
                    break
                seen_next.add(nxt_s)
                payload = self.get_url(nxt_s)
            else:
                cursors = paging.get("cursors")
                if isinstance(cursors, dict):
                    after = cursors.get("after")
                    if isinstance(after, str) and after.strip():
                        cursor_after = after.strip()
                if not cursor_after:
                    break
                if cursor_after in seen_after:
                    break
                seen_after.add(cursor_after)
                next_params = dict(base_params)
                next_params["after"] = cursor_after
                payload = self.get(path, params=next_params)
            pages += 1
            data2 = payload.get("data")
            if isinstance(data2, list):
                out.extend(data2)
                if max_items_i and len(out) >= max_items_i:
                    out = out[:max_items_i]
                    paging = payload.get("paging") if isinstance(payload.get("paging"), dict) else paging
                    break
            paging = payload.get("paging") if isinstance(payload.get("paging"), dict) else paging
        return PageResult(data=out, paging=_redact_paging_urls(paging), raw_pages=pages)


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
