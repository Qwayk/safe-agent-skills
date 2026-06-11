from __future__ import annotations

import dataclasses
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import requests

STREAM_CHUNK_SIZE = 4096
STREAM_PREVIEW_LIMIT = 1024


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str
    artifact_path: str | None = None
    artifact_sha256: str | None = None
    artifact_byte_count: int | None = None
    artifact_content_type: str | None = None
    artifact_truncated: bool = False

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

    def _read_stream_response(
        self,
        resp: requests.Response,
        stream_to: Path,
        stop_token: bytes | None,
        max_bytes: int | None,
    ) -> HttpResponse:
        stream_to.parent.mkdir(parents=True, exist_ok=True)
        preview = bytearray()
        sha256 = hashlib.sha256()
        total_bytes = 0
        truncated = False
        last_chunk = b""
        try:
            with stream_to.open("wb") as fh:
                for chunk in resp.iter_content(chunk_size=STREAM_CHUNK_SIZE):
                    if not chunk:
                        continue
                    fh.write(chunk)
                    sha256.update(chunk)
                    total_bytes += len(chunk)
                    if len(preview) < STREAM_PREVIEW_LIMIT:
                        preview.extend(chunk)
                        if len(preview) > STREAM_PREVIEW_LIMIT:
                            preview = preview[:STREAM_PREVIEW_LIMIT]
                    segment = last_chunk + chunk if last_chunk else chunk
                    if stop_token and stop_token in segment:
                        truncated = True
                        break
                    last_chunk = chunk[-len(stop_token) + 1 :] if stop_token and len(stop_token) > 1 else chunk
                    if max_bytes and total_bytes >= max_bytes:
                        truncated = True
                        break
        finally:
            resp.close()
        return HttpResponse(
            status=resp.status_code,
            headers={k.lower(): v for k, v in resp.headers.items()},
            body=bytes(preview),
            url=resp.url,
            artifact_path=str(stream_to),
            artifact_sha256=sha256.hexdigest(),
            artifact_byte_count=total_bytes,
            artifact_content_type=resp.headers.get("Content-Type"),
            artifact_truncated=truncated,
        )

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
        files: dict[str, Any] | None = None,
        stream_to: Path | None = None,
        stream_stop_token: bytes | None = None,
        max_stream_bytes: int | None = None,
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
                    files=files,
                    timeout=self._timeout_s,
                    stream=bool(stream_to),
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
                if stream_to:
                    return self._read_stream_response(
                        resp=resp,
                        stream_to=stream_to,
                        stop_token=stream_stop_token,
                        max_bytes=max_stream_bytes,
                    )
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
