from __future__ import annotations

import dataclasses
import datetime as dt
import time
from base64 import b64encode
from typing import Any

from .http import HttpClient, HttpResponse
from .oauth_tokens import read_token_json, token_path_for_env_file, write_token_dict


def _parse_kv_pairs(pairs: list[str] | None) -> dict[str, Any]:
    """
    Parse `key=value` pairs into a params dict.

    If the same key appears multiple times, we store a list (requests encodes it as repeated params).
    """
    if not pairs:
        return {}
    out: dict[str, Any] = {}
    for raw in pairs:
        s = (raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise RuntimeError(f"Invalid --param (expected key=value): {raw}")
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            raise RuntimeError(f"Invalid --param (empty key): {raw}")
        if k in out:
            prev = out[k]
            # Pinterest expects `metric_types` as a single CSV string (`explode=false`),
            # so treat repeated `metric_types=...` params as CSV, not repeated keys.
            if k == "metric_types":
                if isinstance(prev, list):
                    out[k] = ",".join([*prev, v])
                else:
                    out[k] = ",".join([str(prev), v])
            else:
                if isinstance(prev, list):
                    prev.append(v)
                else:
                    out[k] = [prev, v]
        else:
            out[k] = v
    return out


def _clamp_page_size(page_size: int) -> int:
    if page_size < 1 or page_size > 100:
        raise RuntimeError("--page-size must be between 1 and 100")
    return int(page_size)


def _parse_limit(limit: int) -> int:
    if limit < 1:
        raise RuntimeError("--limit must be >= 1")
    return int(limit)


def _date_range_last_n_days(days: int) -> tuple[str, str]:
    if days < 1:
        raise RuntimeError("days must be >= 1")
    today = dt.date.today()
    start = today - dt.timedelta(days=days)
    return start.isoformat(), today.isoformat()


def _normalize_yyyy_mm_dd(s: str) -> str:
    # Validate, keep original normalized via date -> isoformat.
    try:
        return dt.date.fromisoformat(s).isoformat()
    except Exception:
        raise RuntimeError("Dates must be YYYY-MM-DD") from None


def _now() -> int:
    return int(time.time())


def _is_token_expired(token: dict[str, Any]) -> bool:
    """
    Best-effort expiry check:
    - if `expires_at` (unix seconds) exists and is within 60s, treat as expired
    - otherwise unknown -> treat as not expired
    """
    exp = token.get("expires_at")
    if isinstance(exp, (int, float)):
        return int(exp) <= (_now() + 60)
    return False


def refresh_access_token(
    *,
    base_url: str,
    http: HttpClient,
    app_id: str,
    app_secret: str,
    refresh_token: str,
) -> dict[str, Any]:
    """
    Exchange a refresh token for a new access token.

    Pinterest expects:
    - POST {base_url}/oauth/token
    - Authorization: Basic base64(app_id:app_secret)
    - form body: grant_type=refresh_token, refresh_token=...
    """
    basic = b64encode(f"{app_id}:{app_secret}".encode("utf-8")).decode("utf-8")
    resp = http.request(
        "POST",
        f"{base_url.rstrip('/')}/oauth/token",
        headers={
            "Accept": "application/json",
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        retries=2,
    )
    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError("Unexpected token response (not an object)")
    if not isinstance(data.get("access_token"), str) or not data["access_token"].strip():
        raise RuntimeError("Token refresh response missing access_token")
    # Compute expires_at if expires_in exists.
    if isinstance(data.get("expires_in"), (int, float)):
        data["expires_at"] = _now() + int(data["expires_in"])
    return data


def resolve_access_token(
    *,
    env_file: str,
    env_access_token: str | None,
    env_refresh_token: str | None,
    app_id: str | None,
    app_secret: str | None,
    base_url: str,
    http: HttpClient,
) -> str:
    """
    Read `.state/token.json` next to `--env-file` and extract `access_token`.
    """
    tok_path = token_path_for_env_file(env_file)
    token = read_token_json(tok_path) or {}

    access_token = token.get("access_token")
    if isinstance(access_token, str) and access_token.strip() and not _is_token_expired(token):
        return access_token.strip()

    # Try refresh (from env or token file).
    rt = env_refresh_token
    if rt is None and isinstance(token.get("refresh_token"), str):
        rt = token["refresh_token"]

    if rt and app_id and app_secret:
        refreshed = refresh_access_token(
            base_url=base_url,
            http=http,
            app_id=app_id,
            app_secret=app_secret,
            refresh_token=rt,
        )
        # Store a minimal token file (no secrets beyond tokens themselves).
        st = write_token_dict(
            data={
                "access_token": refreshed.get("access_token"),
                "refresh_token": refreshed.get("refresh_token") or rt,
                "expires_at": refreshed.get("expires_at"),
                "scope": refreshed.get("scope"),
                "token_type": refreshed.get("token_type"),
            },
            dest_file=tok_path,
        )
        _ = st  # status available if needed later
        return str(refreshed["access_token"]).strip()

    # Fall back to env access token (short-term/manual mode).
    if env_access_token is not None and env_access_token.strip():
        return env_access_token.strip()

    raise RuntimeError(
        "No usable access token found. Either set PINTEREST_ACCESS_TOKEN in .env, or store `.state/token.json`, "
        "or configure PINTEREST_APP_ID + PINTEREST_APP_SECRET + PINTEREST_REFRESH_TOKEN to enable auto-refresh."
    )


@dataclasses.dataclass(frozen=True)
class Page:
    items: list[dict[str, Any]]
    bookmark: str | None


class PinterestApi:
    def __init__(self, *, base_url: str, http: HttpClient, access_token: str):
        self._base_url = base_url.rstrip("/")
        self._http = http
        self._access_token = access_token

    @staticmethod
    def _json_or_empty(resp: HttpResponse) -> dict[str, Any]:
        if not resp.body:
            return {}
        data = resp.json()
        if isinstance(data, dict):
            return data
        return {"_value": data}

    def get_response(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        allowed_statuses: tuple[int, ...] = (),
    ) -> HttpResponse:
        return self._http.request(
            "GET",
            f"{self._base_url}{path}",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self._access_token}",
            },
            params=params or None,
            allowed_statuses=allowed_statuses,
            retries=2,
        )

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._json_or_empty(self.get_response(path, params=params))

    def post_response(
        self,
        path: str,
        *,
        json_body: Any | None,
        params: dict[str, Any] | None = None,
        allowed_statuses: tuple[int, ...] = (),
    ) -> HttpResponse:
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._access_token}",
        }
        if json_body is not None:
            headers["Content-Type"] = "application/json"
        return self._http.request(
            "POST",
            f"{self._base_url}{path}",
            headers=headers,
            params=params or None,
            json_body=json_body,
            allowed_statuses=allowed_statuses,
            retries=2,
        )

    def post(self, path: str, *, json_body: Any | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._json_or_empty(self.post_response(path, json_body=json_body, params=params))

    def patch_response(
        self,
        path: str,
        *,
        json_body: dict[str, Any],
        params: dict[str, Any] | None = None,
        allowed_statuses: tuple[int, ...] = (),
    ) -> HttpResponse:
        return self._http.request(
            "PATCH",
            f"{self._base_url}{path}",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            },
            params=params or None,
            json_body=json_body,
            allowed_statuses=allowed_statuses,
            retries=2,
        )

    def patch(self, path: str, *, json_body: dict[str, Any], params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._json_or_empty(self.patch_response(path, json_body=json_body, params=params))

    def delete_response(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        allowed_statuses: tuple[int, ...] = (),
    ) -> HttpResponse:
        return self._http.request(
            "DELETE",
            f"{self._base_url}{path}",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self._access_token}",
            },
            params=params or None,
            allowed_statuses=allowed_statuses,
            retries=2,
        )

    def delete(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._json_or_empty(self.delete_response(path, params=params))

    def get_page(
        self,
        path: str,
        *,
        params: dict[str, Any] | None,
        page_size: int,
        bookmark: str | None,
    ) -> Page:
        q: dict[str, Any] = dict(params or {})
        q["page_size"] = _clamp_page_size(page_size)
        if bookmark:
            q["bookmark"] = bookmark
        data = self.get(path, params=q)
        items = data.get("items", [])
        if not isinstance(items, list):
            raise RuntimeError("Unexpected API response: `items` is not a list")
        b = data.get("bookmark")
        if b is not None and not isinstance(b, str):
            raise RuntimeError("Unexpected API response: `bookmark` is not a string or null")
        return Page(items=items, bookmark=b)

    def list_all(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        limit: int,
        page_size: int,
        bookmark: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None, int]:
        limit = _parse_limit(limit)
        page_size = _clamp_page_size(page_size)

        all_items: list[dict[str, Any]] = []
        pages = 0
        next_bookmark: str | None = bookmark
        while True:
            page = self.get_page(path, params=params, page_size=page_size, bookmark=next_bookmark)
            pages += 1
            for item in page.items:
                if not isinstance(item, dict):
                    # Best-effort: keep raw items too, but ensure JSON-serializable.
                    all_items.append({"_value": item})
                else:
                    all_items.append(item)
                if len(all_items) >= limit:
                    return all_items[:limit], page.bookmark, pages
            next_bookmark = page.bookmark
            if not next_bookmark:
                return all_items, None, pages


def build_analytics_params(
    *,
    start_date: str | None,
    end_date: str | None,
    metrics: list[str] | None,
    extra_params: list[str] | None,
    default_days: int = 90,
    default_metrics: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build a best-effort analytics query param dict.

    Pinterest analytics endpoints have required params that depend on the endpoint and access tier.
    We provide:
    - `start_date` and `end_date` (default last N days)
    - `metric_types` if metrics are provided, otherwise optional defaults (if given)
    - `--param key=value` passthrough for anything else
    """
    if start_date is None or end_date is None:
        d0, d1 = _date_range_last_n_days(default_days)
        start_date = start_date or d0
        end_date = end_date or d1

    params: dict[str, Any] = {
        "start_date": _normalize_yyyy_mm_dd(start_date),
        "end_date": _normalize_yyyy_mm_dd(end_date),
    }

    metric_types = metrics if metrics else default_metrics
    if metric_types:
        # Pinterest uses `explode=false` for `metric_types`, so encode as a single CSV string.
        cleaned = [m.strip().upper() for m in metric_types if (m or "").strip()]
        if cleaned:
            params["metric_types"] = ",".join(cleaned)

    params.update(_parse_kv_pairs(extra_params))
    return params
