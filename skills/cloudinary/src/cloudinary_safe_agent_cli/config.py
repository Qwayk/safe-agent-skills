from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .errors import ValidationError
from .inventory import OperationSpec
from .redaction import redact_text


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            out[key] = value
    return out


def _get(env: dict[str, str], key: str) -> str:
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


def _normalize_value(value: str) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered.startswith("<") and lowered.endswith(">"):
        return None
    if lowered in {"paste_here", "paste_value_here", "change_me", "your_value_here"}:
        return None
    if lowered.startswith("paste_") or lowered.startswith("your_"):
        return None
    return text


def _basic_auth_header(user: str, password: str) -> str:
    import base64

    token = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


@dataclasses.dataclass(frozen=True)
class Config:
    cloud_name: str | None
    api_key: str | None
    api_secret: str | None
    product_api_host: str
    account_id: str | None
    account_api_key: str | None
    account_api_secret: str | None
    account_api_host: str
    timeout_s: float

    def secrets_for_redaction(self) -> list[str]:
        return [
            value
            for value in [
                self.api_key,
                self.api_secret,
                self.account_api_key,
                self.account_api_secret,
            ]
            if value
        ]

    def redact(self, text: str) -> str:
        return redact_text(text, tuple(self.secrets_for_redaction()))

    def env_fingerprint(self) -> str:
        return (
            f"product={self.product_api_host}/{self.cloud_name or '-'}"
            f"|account={self.account_api_host}/{self.account_id or '-'}"
        )

    def has_product_context(self) -> bool:
        return bool(self.cloud_name)

    def has_product_basic_auth(self) -> bool:
        return bool(self.cloud_name and self.api_key and self.api_secret)

    def has_account_context(self) -> bool:
        return bool(self.account_id)

    def has_account_basic_auth(self) -> bool:
        return bool(self.account_id and self.account_api_key and self.account_api_secret)

    def product_v1_base_url(self) -> str:
        if not self.cloud_name:
            raise ValidationError("Missing CLOUDINARY_CLOUD_NAME")
        return f"https://{self.product_api_host}/v1_1/{self.cloud_name}"

    def product_video_v2_base_url(self) -> str:
        if not self.cloud_name:
            raise ValidationError("Missing CLOUDINARY_CLOUD_NAME")
        return f"https://{self.product_api_host}/v2/video/{self.cloud_name}"

    def product_analysis_v2_base_url(self) -> str:
        if not self.cloud_name:
            raise ValidationError("Missing CLOUDINARY_CLOUD_NAME")
        return f"https://{self.product_api_host}/v2/analysis/{self.cloud_name}"

    def account_provisioning_base_url(self) -> str:
        if not self.account_id:
            raise ValidationError("Missing CLOUDINARY_ACCOUNT_ID")
        return f"https://{self.account_api_host}/v1_1/provisioning/accounts/{self.account_id}"

    def account_permissions_base_url(self) -> str:
        return f"https://{self.account_api_host}"

    def product_auth_header(self) -> dict[str, str]:
        if not self.has_product_basic_auth():
            raise ValidationError("Missing CLOUDINARY_API_KEY or CLOUDINARY_API_SECRET")
        return {"Authorization": _basic_auth_header(self.api_key or "", self.api_secret or "")}

    def account_auth_header(self) -> dict[str, str]:
        if not self.has_account_basic_auth():
            raise ValidationError("Missing CLOUDINARY_ACCOUNT_API_KEY or CLOUDINARY_ACCOUNT_API_SECRET")
        return {
            "Authorization": _basic_auth_header(self.account_api_key or "", self.account_api_secret or "")
        }

    def runtime_base_and_headers_for(self, *, spec: OperationSpec, need_credentials: bool) -> tuple[str, dict[str, str]]:
        scope = spec.auth_scope
        if scope == "public":
            return (self.account_permissions_base_url(), {})
        if scope == "product_unsigned":
            if not self.has_product_context():
                raise ValidationError("Missing CLOUDINARY_CLOUD_NAME")
            return (self.product_v1_base_url(), {})
        if scope == "product_basic":
            if spec.api_group in {"upload", "admin"}:
                base = self.product_v1_base_url()
            elif spec.api_group in {"live_streaming", "player_profiles", "video_config"}:
                base = self.product_video_v2_base_url()
            elif spec.api_group == "analyze":
                base = self.product_analysis_v2_base_url()
            else:
                raise ValidationError(f"Unsupported product API group: {spec.api_group}")
            headers = self.product_auth_header() if need_credentials else {}
            return (base, headers)
        if scope == "account_basic":
            if spec.api_group == "provisioning":
                base = self.account_provisioning_base_url()
            elif spec.api_group == "permissions":
                if not self.has_account_context():
                    raise ValidationError("Missing CLOUDINARY_ACCOUNT_ID")
                base = self.account_permissions_base_url()
            else:
                raise ValidationError(f"Unsupported account API group: {spec.api_group}")
            headers = self.account_auth_header() if need_credentials else {}
            return (base, headers)
        raise ValidationError(f"Unsupported auth scope: {scope}")


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    cloud_name = _normalize_value(_get(env, "CLOUDINARY_CLOUD_NAME"))
    api_key = _normalize_value(_get(env, "CLOUDINARY_API_KEY"))
    api_secret = _normalize_value(_get(env, "CLOUDINARY_API_SECRET"))
    product_api_host = _normalize_value(_get(env, "CLOUDINARY_PRODUCT_API_HOST")) or "api.cloudinary.com"

    account_id = _normalize_value(_get(env, "CLOUDINARY_ACCOUNT_ID"))
    account_api_key = _normalize_value(_get(env, "CLOUDINARY_ACCOUNT_API_KEY"))
    account_api_secret = _normalize_value(_get(env, "CLOUDINARY_ACCOUNT_API_SECRET"))
    account_api_host = _normalize_value(_get(env, "CLOUDINARY_ACCOUNT_API_HOST")) or "api.cloudinary.com"

    timeout_s_raw = _normalize_value(_get(env, "CLOUDINARY_TIMEOUT_S")) or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("CLOUDINARY_TIMEOUT_S must be a number (seconds)") from None
    if timeout_s <= 0:
        raise RuntimeError("CLOUDINARY_TIMEOUT_S must be > 0")

    return Config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        product_api_host=product_api_host.rstrip("/"),
        account_id=account_id,
        account_api_key=account_api_key,
        account_api_secret=account_api_secret,
        account_api_host=account_api_host.rstrip("/"),
        timeout_s=timeout_s,
    )
