from __future__ import annotations

import dataclasses
import json
import sys
import time
from pathlib import Path
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
        stream: bool = False,
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
                    stream=stream,
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

            body = resp.content
            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=body,
                    url=resp.url,
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            raise RuntimeError(f"HTTP {resp.status_code} for {method} {resp.url}\n{resp.text}")

    def download_to_path(
        self,
        url: str,
        path: Path,
        *,
        headers: dict[str, str] | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
        chunk_size: int = 1024 * 1024,
    ) -> str:
        """
        Stream a binary response to `path` using a temporary `.part` file then atomic rename.
        Returns the final response URL (after redirects).
        """
        attempt = 0
        display_url = url
        tmp_path = path.with_name(path.name + ".part")
        while True:
            attempt += 1
            start = time.time()
            if self._verbose:
                print(f"[http] GET {display_url} (start)", file=sys.stderr)
            try:
                with self._session.get(
                    url=url,
                    headers=headers,
                    timeout=self._timeout_s,
                    stream=True,
                    allow_redirects=True,
                ) as resp:
                    ms = int((time.time() - start) * 1000)
                    if self._verbose:
                        print(f"[http] GET {resp.url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

                    if resp.status_code >= 400:
                        if attempt <= retries and resp.status_code in retry_on:
                            time.sleep(min(2**attempt, 10))
                            continue
                        raise RuntimeError(f"HTTP {resp.status_code} for GET {resp.url}\n{resp.text}")

                    path.parent.mkdir(parents=True, exist_ok=True)
                    if tmp_path.exists():
                        tmp_path.unlink()
                    with tmp_path.open("wb") as f:
                        for chunk in resp.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                    tmp_path.replace(path)
                    return resp.url
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                if self._verbose:
                    print(
                        f"[http] GET {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {e}",
                        file=sys.stderr,
                    )
                raise RuntimeError(f"Request failed for GET {display_url}: {type(e).__name__}: {e}") from e
            finally:
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except OSError:
                        pass
