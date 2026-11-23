from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .auth_store import auth_path_for_env_file, get_access_key_from_store
from .config import Config
from .errors import SafetyError, ToolError, ValidationError
from .http import HttpClient, HttpStatusError

_PHOTO_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_photo_id(value: str, *, field: str = "--id") -> str:
    v = (value or "").strip()
    if not v:
        raise ValidationError(f"Missing {field}")
    if not _PHOTO_ID_RE.match(v):
        raise ValidationError(f"Invalid {field} (expected Unsplash id like 'Dwu85P9SOIk')")
    return v


def validate_collection_id(value: Any, *, field: str = "--id") -> int | str:
    collection = validate_photo_id(str(value or ""), field=field)
    if collection.isascii() and collection.isdecimal() and not collection.startswith("0"):
        return int(collection)
    return collection


def validate_username(value: str, *, field: str = "--username") -> str:
    v = (value or "").strip()
    if not v:
        raise ValidationError(f"Missing {field}")
    if "/" in v or " " in v:
        raise ValidationError(f"Invalid {field}")
    return v


def validate_positive_int(value: Any, *, field: str) -> int:
    try:
        n = int(value)
    except Exception:
        raise ValidationError(f"{field} must be an integer") from None
    if n <= 0:
        raise ValidationError(f"{field} must be > 0")
    return n


def validate_optional_int(value: Any, *, field: str) -> int | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    return validate_positive_int(raw, field=field)


@dataclass(frozen=True)
class UnsplashClient:
    cfg: Config
    http: HttpClient
    env_file: str

    def _access_key(self) -> str:
        key = self.cfg.access_key
        if key:
            return key
        stored = get_access_key_from_store(auth_path_for_env_file(self.env_file))
        if stored:
            return stored
        raise ValidationError("Missing UNSPLASH_ACCESS_KEY (set it in your env file or via `unsplash-api-tool auth key set`)")

    def _headers(self) -> dict[str, str]:
        return {
            "Accept-Version": "v1",
            "Authorization": f"Client-ID {self._access_key()}",
        }

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            raise ToolError("Internal error: path must start with /")
        return self.cfg.base_url.rstrip("/") + path

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        resp = self.http.request("GET", self._url(path), headers=self._headers(), params=params)
        return resp.json()

    def connection_fingerprint(self) -> str:
        return sha256(f"{self.cfg.base_url}\0{self._access_key()}".encode()).hexdigest()

    def validate_tracking_url(self, photo_id: str, url: str) -> str:
        target = urlsplit(url)
        expected = urlsplit(self._url(f"/photos/{photo_id}/download"))
        if (
            (target.scheme, target.netloc, target.path) != (expected.scheme, expected.netloc, expected.path)
            or target.scheme not in {"https", "http"}
            or target.username is not None
            or target.fragment
        ):
            raise ValidationError("Unsplash did not return a tracking link for this photo on the configured API host.")
        return url

    def download_tracking(self, photo_id: str, url: str) -> dict[str, Any]:
        tracking_url = self.validate_tracking_url(photo_id, url)
        response = self.http.request("GET", tracking_url, headers=self._headers(), allow_redirects=False)
        if not 200 <= response.status < 300:
            raise HttpStatusError(response.status, "Unsplash did not accept the download tracking request.")
        data = response.json()
        if not isinstance(data, dict):
            raise ToolError("Unexpected response from the Unsplash download tracking request.")
        return data

    def download_file(
        self,
        url: str,
        *,
        dest: Path,
        overwrite: bool,
    ) -> dict[str, Any]:
        if dest.exists() and not overwrite:
            raise SafetyError(f"Refused: destination exists (use --overwrite with --apply --yes): {dest}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        info = self.http.download_to_file(url, dest, overwrite=overwrite)
        if not dest.exists() or dest.stat().st_size <= 0:
            raise ToolError("Download verification failed: file missing or empty")
        return info
