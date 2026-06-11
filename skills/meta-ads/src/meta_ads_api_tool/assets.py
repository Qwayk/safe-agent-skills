from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

from .errors import ValidationError
from .http import HttpClient


@dataclass(frozen=True)
class AssetResult:
    creative_id: str | None
    url: str
    kind: str
    url_sha256: str
    relpath: str | None
    status: str  # downloaded|skipped_exists|failed
    bytes: int | None
    error: str | None

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "creative_id": self.creative_id,
            "url": self.url,
            "kind": self.kind,
            "url_sha256": self.url_sha256,
            "relpath": self.relpath,
            "status": self.status,
            "bytes": self.bytes,
            "error": self.error,
        }


def safe_asset_filename(url: str) -> str:
    u = str(url or "").strip()
    if not u:
        raise ValidationError("Missing asset url")
    parsed = urlparse(u)
    path = parsed.path or ""
    base = os.path.basename(path)
    ext = ""
    if "." in base:
        ext = "." + base.rsplit(".", 1)[-1].lower()
    if ext and not re.match(r"^[.][a-z0-9]{1,8}$", ext):
        ext = ""
    if ext in {".php", ".asp", ".aspx", ".jsp"}:
        ext = ""
    h = hashlib.sha256(u.encode("utf-8")).hexdigest()[:16]
    return f"{h}{ext or '.bin'}"


def download_assets(
    *,
    http: HttpClient,
    items: Iterable[dict[str, Any]],
    out_dir: Path,
    overwrite: str,
    errors: list[dict[str, Any]],
) -> list[AssetResult]:
    if overwrite not in {"never", "if_missing", "always"}:
        raise ValidationError("--assets-overwrite must be one of: never, if_missing, always")
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[AssetResult] = []
    for it in items:
        url = str(it.get("url") or "").strip()
        redacted_url = HttpClient.redact_url(url)
        kind = str(it.get("kind") or "").strip() or "asset"
        url_sha = str(it.get("url_sha256") or "").strip()
        creative_id = str(it.get("creative_id") or "").strip() or None
        if not url or not re.match(r"^https?://", url, flags=re.IGNORECASE):
            continue
        if not url_sha:
            url_sha = hashlib.sha256(url.encode("utf-8")).hexdigest()

        fname = safe_asset_filename(url)
        path = out_dir / fname
        if path.exists() and overwrite in {"never", "if_missing"}:
            results.append(
                AssetResult(
                    creative_id=creative_id,
                    url=redacted_url,
                    kind=kind,
                    url_sha256=url_sha,
                    relpath=str(Path("assets") / fname),
                    status="skipped_exists",
                    bytes=None,
                    error=None,
                )
            )
            continue

        try:
            resp = http.request("GET", url, headers=None, params=None, retries=0)
            path.write_bytes(resp.body)
            results.append(
                AssetResult(
                    creative_id=creative_id,
                    url=redacted_url,
                    kind=kind,
                    url_sha256=url_sha,
                    relpath=str(Path("assets") / fname),
                    status="downloaded",
                    bytes=len(resp.body),
                    error=None,
                )
            )
        except Exception as e:  # noqa: BLE001
            safe_err = HttpClient.redact_url(str(e))
            results.append(
                AssetResult(
                    creative_id=creative_id,
                    url=redacted_url,
                    kind=kind,
                    url_sha256=url_sha,
                    relpath=str(Path("assets") / fname),
                    status="failed",
                    bytes=None,
                    error=safe_err,
                )
            )
            errors.append(
                {
                    "type": "asset_download_failed",
                    "creative_id": creative_id,
                    "kind": kind,
                    "url_sha256": url_sha,
                    "error_type": type(e).__name__,
                    "error": safe_err,
                }
            )
    return results
