from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .cache import ShortTtlCache
from .errors import ToolError
from .http import HttpClient


@dataclass(frozen=True)
class CloudflareResult:
    result: Any
    result_info: dict[str, Any] | None
    http: dict[str, Any] | None = None


class CloudflareClient:
    def __init__(
        self,
        *,
        base_url: str,
        token: str | None,
        connect_timeout_s: float,
        read_timeout_s: float,
        verbose: bool,
        progress: bool,
        cache: ShortTtlCache | None = None,
        user_agent: str,
    ) -> None:
        self._base_url = str(base_url or "").rstrip("/")
        self._token = str(token or "") or None
        self._http = HttpClient(
            connect_timeout_s=float(connect_timeout_s),
            read_timeout_s=float(read_timeout_s),
            verbose=bool(verbose),
            progress=bool(progress),
            user_agent=user_agent,
        )
        self._cache = cache

    def _url(self, path: str) -> str:
        p = str(path or "").lstrip("/")
        if not p:
            return self._base_url + "/"
        return f"{self._base_url}/{p}"

    def _headers(self) -> dict[str, str]:
        h = {"accept": "application/json"}
        if self._token:
            h["authorization"] = f"Bearer {self._token}"
        return h

    def _parse_envelope(self, *, method: str, path: str, status: int, obj: Any) -> CloudflareResult:
        if not isinstance(obj, dict):
            if status >= 400:
                raise ToolError(f"Cloudflare API error for {method} {path}: HTTP {status}")
            return CloudflareResult(result=obj, result_info=None)

        if "success" not in obj:
            if status >= 400:
                raise ToolError(f"Cloudflare API error for {method} {path}: HTTP {status}")
            return CloudflareResult(result=obj, result_info=None)

        if bool(obj.get("success")) is True:
            return CloudflareResult(result=obj.get("result"), result_info=obj.get("result_info"))

        errors = obj.get("errors") or []
        parts: list[str] = []
        if isinstance(errors, list):
            for e in errors[:5]:
                if not isinstance(e, dict):
                    continue
                code = e.get("code")
                msg = e.get("message")
                if code is not None and msg:
                    parts.append(f"{code}: {msg}")
                elif msg:
                    parts.append(str(msg))
        summary = "; ".join(parts) if parts else "Unknown error"
        if "Method not allowed for this authentication scheme" in summary:
            summary += " This usually means the token is valid, but Cloudflare wants a different auth path for this endpoint."
        if "auth.forbidden" in summary:
            summary += " This usually means the token or plan cannot access this log or analytics surface."
        raise ToolError(f"Cloudflare API error for {method} {path}: HTTP {status}: {summary}")

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
        retries: int = 3,
        cacheable: bool = False,
    ) -> CloudflareResult:
        url = self._url(path)
        h = self._headers()
        if headers:
            for k, v in headers.items():
                h[str(k).lower()] = str(v)
        if cacheable and method.upper() == "GET" and self._cache is not None:
            try:
                cached = self._cache.get(url=str(url), params=params)
            except Exception:
                cached = None
            if isinstance(cached, dict):
                return CloudflareResult(
                    result=cached.get("result"),
                    result_info=cached.get("result_info"),
                    http={
                        "status": 200,
                        "url": str(url),
                        "duration_ms": int(((cached.get("http") or {}) if isinstance(cached.get("http"), dict) else {}).get("duration_ms") or 0),
                        "attempts": 0,
                        "cf_ray": None,
                        "from_cache": True,
                    },
                )
        resp = self._http.request(
            method,
            url,
            headers=h,
            params=params,
            json_body=json_body,
            data=data,
            files=files,
            retries=int(retries),
        )
        if resp.status == 204 or not resp.body:
            return CloudflareResult(
                result=None,
                result_info=None,
                http={
                    "status": int(resp.status),
                    "url": str(resp.url),
                    "duration_ms": int(resp.duration_ms),
                    "attempts": int(resp.attempts),
                    "cf_ray": resp.headers.get("cf-ray"),
                    "from_cache": False,
                },
            )
        try:
            obj = resp.json()
        except Exception:
            raise ToolError(f"Cloudflare API returned non-JSON for {method} {path}: HTTP {resp.status}") from None
        parsed = self._parse_envelope(method=method, path=path, status=resp.status, obj=obj)
        http_meta = {
            "status": int(resp.status),
            "url": str(resp.url),
            "duration_ms": int(resp.duration_ms),
            "attempts": int(resp.attempts),
            "cf_ray": resp.headers.get("cf-ray"),
            "from_cache": False,
        }
        if cacheable and method.upper() == "GET" and self._cache is not None:
            try:
                self._cache.set(url=str(url), params=params, value={"result": parsed.result, "result_info": parsed.result_info, "http": http_meta})
            except Exception:
                pass
        return CloudflareResult(result=parsed.result, result_info=parsed.result_info, http=http_meta)

    def get_json(self, path: str, *, params: dict[str, Any] | None = None, cacheable: bool = False) -> CloudflareResult:
        return self.request_json("GET", path, params=params, cacheable=bool(cacheable))

    def post_json(self, path: str, *, json_body: dict[str, Any] | None = None) -> CloudflareResult:
        return self.request_json("POST", path, json_body=json_body)

    def put_json(self, path: str, *, json_body: dict[str, Any] | None = None) -> CloudflareResult:
        return self.request_json("PUT", path, json_body=json_body)

    def patch_json(self, path: str, *, json_body: dict[str, Any] | None = None) -> CloudflareResult:
        return self.request_json("PATCH", path, json_body=json_body)

    def delete_json(self, path: str, *, json_body: dict[str, Any] | None = None) -> CloudflareResult:
        return self.request_json("DELETE", path, json_body=json_body)

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
        retries: int = 3,
    ):
        url = self._url(path)
        base = self._headers()
        if headers:
            for k, v in headers.items():
                base[str(k).lower()] = str(v)
        resp = self._http.request(
            method,
            url,
            headers=base,
            params=params,
            json_body=json_body,
            data=data,
            files=files,
            retries=int(retries),
        )
        if resp.status >= 400:
            try:
                obj = resp.json()
            except Exception:
                raise ToolError(f"Cloudflare API error for {method} {path}: HTTP {resp.status}") from None
            # This call raises ToolError with a useful Cloudflare error summary when possible.
            _ = self._parse_envelope(method=method, path=path, status=resp.status, obj=obj)
            raise ToolError(f"Cloudflare API error for {method} {path}: HTTP {resp.status}")
        return resp

    def request_raw_allow_errors(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
        retries: int = 3,
    ):
        url = self._url(path)
        base = self._headers()
        if headers:
            for k, v in headers.items():
                base[str(k).lower()] = str(v)
        return self._http.request(
            method,
            url,
            headers=base,
            params=params,
            json_body=json_body,
            data=data,
            files=files,
            retries=int(retries),
        )

    def paginate_page_per_page(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        page: int = 1,
        per_page: int = 50,
        max_pages: int = 100,
    ) -> Iterable[Any]:
        p = dict(params or {})
        cur = int(page)
        pp = int(per_page)
        for _ in range(max_pages):
            p["page"] = cur
            p["per_page"] = pp
            res = self.get_json(path, params=p)
            items = res.result or []
            if isinstance(items, list):
                for it in items:
                    yield it
            else:
                yield items
                return
            info = res.result_info or {}
            total_pages = info.get("total_pages") if isinstance(info, dict) else None
            if isinstance(total_pages, int) and cur >= total_pages:
                return
            if not items:
                return
            cur += 1

    def paginate_cursor(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        cursor: str | None = None,
        max_pages: int = 200,
    ) -> Iterable[Any]:
        p = dict(params or {})
        cur = str(cursor) if cursor else None
        for _ in range(max_pages):
            if cur:
                p["cursor"] = cur
            res = self.get_json(path, params=p)
            items = res.result or []
            if isinstance(items, list):
                for it in items:
                    yield it
            else:
                yield items
                return
            info = res.result_info or {}
            nxt: str | None = None
            if isinstance(info, dict):
                cursors = info.get("cursors")
                if isinstance(cursors, dict):
                    nxt = cursors.get("after") or cursors.get("next")  # type: ignore[assignment]
                if not nxt:
                    nxt = info.get("cursor")  # type: ignore[assignment]
            if not nxt or nxt == cur:
                return
            cur = str(nxt)
