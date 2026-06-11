from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import sys
import time
from typing import Any

import requests


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class HttpClient:
    def __init__(self, *, timeout_s: float, verbose: bool):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session()
        self._session.headers["User-Agent"] = "wordpress-api-tool/0.1"

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
        data: bytes | None = None,
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
                # Never print auth headers here (requests stores them separately); url may include query params.
                print(f"[http] {method} {resp.url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            content_type = (resp.headers.get("content-type") or "").lower()
            msg = resp.text
            if "text/html" in content_type and len(msg) > 800:
                msg = msg[:800] + "\n... (truncated)"
            hint = ""
            if "text/html" in content_type:
                hint = (
                    "\nHint: response is HTML, not JSON. "
                    "Check that WP_BASE_URL points to a WordPress site and supports /wp-json/."
                )
            raise RuntimeError(f"HTTP {resp.status_code} for {method} {resp.url}\n{msg}{hint}")

    def download_to_file(
        self,
        url: str,
        *,
        out_path: str,
        headers: dict[str, str] | None = None,
        chunk_size: int = 1024 * 256,
    ) -> dict[str, Any]:
        """
        Download a URL to a local file (streaming).

        Returns a small metadata dict (sha256, bytes, content_type).
        """
        tmp_path = f"{out_path}.part"
        start = time.time()
        if self._verbose:
            print(f"[http] GET {url} (download start)", file=sys.stderr)
        try:
            resp = self._session.get(url, stream=True, timeout=self._timeout_s, headers=headers)
            resp.raise_for_status()
            h = hashlib.sha256()
            n = 0
            with open(tmp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if not chunk:
                        continue
                    f.write(chunk)
                    h.update(chunk)
                    n += len(chunk)
            os.replace(tmp_path, out_path)
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] GET {url} -> {resp.status_code} ({ms}ms) downloaded={n}", file=sys.stderr)
            return {"sha256": h.hexdigest(), "bytes": n, "content_type": resp.headers.get("content-type")}
        except requests.RequestException as e:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] GET {url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {e}", file=sys.stderr)
            raise RuntimeError(f"Download failed for GET {url}: {type(e).__name__}: {e}") from e
        except Exception as e:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] GET {url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {e}", file=sys.stderr)
            raise RuntimeError(f"Download failed for GET {url}: {type(e).__name__}: {e}") from e
