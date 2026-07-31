from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

MAX_TOKEN_LIFETIME_SECONDS = 1800.0
MIN_TOKEN_LIFETIME_SECONDS = 1.0


@dataclass(frozen=True)
class TokenStatus:
    exists: bool
    path: str
    updated_at_utc: str | None
    fields: list[str]
    has_refresh_token: bool | None
    expires_at_utc: str | None


class TokenCache:
    def __init__(self) -> None:
        self._token: str | None = None
        self._payload: dict[str, Any] | None = None
        self._updated_at: float | None = None
        self._expires_at: float | None = None

    @staticmethod
    def _utc(ts: float) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))

    @staticmethod
    def _bounded_expires_in(payload: dict[str, Any], now: float) -> float:
        raw = payload.get("expires_in")
        try:
            seconds = float(0 if raw is None else raw)
        except Exception:
            seconds = MAX_TOKEN_LIFETIME_SECONDS
        if seconds <= 0 or seconds != seconds:
            seconds = MAX_TOKEN_LIFETIME_SECONDS
        if seconds < MIN_TOKEN_LIFETIME_SECONDS:
            seconds = MIN_TOKEN_LIFETIME_SECONDS
        if seconds > MAX_TOKEN_LIFETIME_SECONDS:
            seconds = MAX_TOKEN_LIFETIME_SECONDS
        return now + seconds

    @staticmethod
    def _safe_bool_refresh(payload: dict[str, Any]) -> bool | None:
        if "refresh_token" not in payload:
            return None
        return bool(payload.get("refresh_token"))

    def clear(self) -> None:
        self._token = None
        self._payload = None
        self._updated_at = None
        self._expires_at = None

    def set(self, payload: dict[str, Any], *, now: float | None = None) -> None:
        if not isinstance(payload, dict):
            raise ValueError("Token payload must be a JSON object")
        token = str(payload.get("access_token") or "").strip()
        if not token:
            raise ValueError("Token payload missing access_token")

        now_val = float(now if now is not None else time.time())
        self._token = token
        self._payload = dict(payload)
        self._updated_at = now_val
        self._expires_at = self._bounded_expires_in(payload, now=now_val)

    def get(self, *, now: float | None = None) -> str | None:
        if self._token is None or self._expires_at is None:
            return None
        now_val = float(now if now is not None else time.time())
        if now_val >= self._expires_at:
            self.clear()
            return None
        return self._token

    def get_payload(self, *, now: float | None = None) -> dict[str, Any] | None:
        if self.get(now=now) is None:
            return None
        return dict(self._payload) if self._payload is not None else None

    def status(self, path: str | None = None, *, now: float | None = None) -> TokenStatus:
        payload = self.get_payload(now=now)
        if payload is None or self._updated_at is None or self._expires_at is None:
            return TokenStatus(
                exists=False,
                path=str(path or ""),
                updated_at_utc=None,
                fields=[],
                has_refresh_token=None,
                expires_at_utc=None,
            )

        return TokenStatus(
            exists=True,
            path=str(path or ""),
            updated_at_utc=self._utc(self._updated_at),
            fields=sorted([k for k in payload.keys() if isinstance(k, str)]),
            has_refresh_token=self._safe_bool_refresh(payload),
            expires_at_utc=self._utc(self._expires_at),
        )


__all__ = ["TokenStatus", "TokenCache"]
