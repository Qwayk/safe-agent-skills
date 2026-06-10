from __future__ import annotations

import dataclasses
import json
import os
import sys
import tempfile
import time
from typing import Any

import requests


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class HttpClient:
    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    @staticmethod
    def _format_url(url: str, params: dict[str, Any] | None) -> str:
        if not params:
            return url
        try:
            return requests.Request("GET", url, params=params).prepare().url or url
        except Exception:
            return url

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        data: dict[str, Any] | None = None,
        allowed_statuses: tuple[int, ...] = (),
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        display_url = self._format_url(url, params)
        while True:
            attempt += 1
            start = time.time()
            if self._verbose:
                print(f"[http] {method} {display_url} (start)", file=sys.stderr)
            try:
                resp = self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_body,
                    data=data,
                    timeout=self._timeout_s,
                )
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {e}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {display_url}: {type(e).__name__}: {e}"
                ) from e
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] {method} {resp.url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=resp.url,
                )

            if allowed_statuses and resp.status_code in allowed_statuses:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=resp.url,
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            raise RuntimeError(f"HTTP {resp.status_code} for {method} {resp.url}\n{resp.text}")

    def download_to_file(
        self,
        url: str,
        *,
        headers: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        max_bytes: int,
        dest_path: str,
    ) -> "DownloadResult":
        return download_to_file(
            session=self._session,
            url=url,
            headers=headers,
            params=params,
            timeout_s=float(self._timeout_s),
            verbose=bool(self._verbose),
            max_bytes=max_bytes,
            dest_path=dest_path,
        )


class DownloadExceededError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class DownloadResult:
    status: int
    headers: dict[str, str]
    final_url: str
    bytes_written: int
    dest_path: str


def _safe_unlink(path: str) -> None:
    try:
        os.unlink(path)
    except FileNotFoundError:
        return


def _tmp_path_for_dest(dest_path: str) -> str:
    dest_dir = os.path.dirname(dest_path) or "."
    base = os.path.basename(dest_path) or "download"
    fd, tmp_path = tempfile.mkstemp(prefix=f".{base}.", suffix=".partial", dir=dest_dir)
    os.close(fd)
    return tmp_path


def _snip(s: str, max_chars: int = 2000) -> str:
    s = s or ""
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + "…"


def _normalize_headers(h: dict[str, Any] | None) -> dict[str, str] | None:
    if not h:
        return None
    out: dict[str, str] = {}
    for k, v in h.items():
        if k is None:
            continue
        out[str(k)] = str(v)
    return out or None


def _lower_headers(h: Any) -> dict[str, str]:
    if not h:
        return {}
    out: dict[str, str] = {}
    try:
        for k, v in dict(h).items():
            out[str(k).lower()] = str(v)
    except Exception:
        return {}
    return out


def download_to_file(
    *,
    session: requests.Session,
    url: str,
    headers: dict[str, Any] | None,
    params: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
    max_bytes: int,
    dest_path: str,
) -> DownloadResult:
    if max_bytes < 1:
        raise RuntimeError("--max-download-bytes must be >= 1")

    dest_path = str(dest_path)
    os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
    tmp_path = _tmp_path_for_dest(dest_path)

    display_url = HttpClient._format_url(url, params)
    start = time.time()
    if verbose:
        print(f"[http] GET {display_url} (download start)", file=sys.stderr)

    try:
        resp = session.request(
            method="GET",
            url=url,
            headers=_normalize_headers(headers),
            params=params or None,
            timeout=timeout_s,
            stream=True,
        )
    except requests.RequestException as e:
        _safe_unlink(tmp_path)
        ms = int((time.time() - start) * 1000)
        if verbose:
            print(
                f"[http] GET {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {e}",
                file=sys.stderr,
            )
        raise RuntimeError(f"Download request failed for GET {display_url}: {type(e).__name__}: {e}") from e

    ms = int((time.time() - start) * 1000)
    if verbose:
        print(f"[http] GET {resp.url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

    if resp.status_code >= 400:
        try:
            txt = resp.text
        except Exception:
            txt = ""
        _safe_unlink(tmp_path)
        raise RuntimeError(f"HTTP {resp.status_code} for GET {resp.url}\n{_snip(txt)}")

    bytes_written = 0
    try:
        with open(tmp_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                bytes_written += len(chunk)
                if bytes_written > max_bytes:
                    raise DownloadExceededError(
                        f"Download exceeded max_bytes ({max_bytes}) after {bytes_written} bytes for {resp.url}"
                    )
                f.write(chunk)
        os.replace(tmp_path, dest_path)
    except DownloadExceededError:
        _safe_unlink(tmp_path)
        _safe_unlink(dest_path)
        raise
    except Exception:
        _safe_unlink(tmp_path)
        raise

    return DownloadResult(
        status=int(resp.status_code),
        headers=_lower_headers(getattr(resp, "headers", None)),
        final_url=str(getattr(resp, "url", url)),
        bytes_written=int(bytes_written),
        dest_path=dest_path,
    )
