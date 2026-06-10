from __future__ import annotations

import dataclasses
import hashlib
import json
import sys
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
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
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

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            raise RuntimeError(f"HTTP {resp.status_code} for {method} {resp.url}\n{resp.text}")

    def download_to_file(
        self,
        url: str,
        dest_path,
        *,
        headers: dict[str, str] | None = None,
        overwrite: bool = False,
        chunk_size: int = 1024 * 128,
    ) -> dict[str, Any]:
        from pathlib import Path

        dest = Path(dest_path)
        if dest.exists() and not overwrite:
            raise RuntimeError(f"Refused to overwrite existing file: {dest}")

        start = time.time()
        if self._verbose:
            print(f"[http] GET {url} (download start)", file=sys.stderr)

        resp = self._session.request(
            method="GET",
            url=url,
            headers=headers,
            stream=True,
            timeout=self._timeout_s,
            allow_redirects=True,
        )
        ms = int((time.time() - start) * 1000)
        if self._verbose:
            print(f"[http] GET {resp.url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code} for GET {resp.url}")

        h = hashlib.sha256()
        written = 0
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                f.write(chunk)
                h.update(chunk)
                written += len(chunk)

        return {
            "url": resp.url,
            "status": resp.status_code,
            "bytes_written": written,
            "sha256": h.hexdigest(),
        }
