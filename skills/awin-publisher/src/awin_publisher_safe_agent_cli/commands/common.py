from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..errors import SafetyError, ToolError, ValidationError


def bool_str(value: bool) -> str:
    return "true" if value else "false"


def require_token(cfg) -> str:
    if not cfg.token:
        raise ValidationError("AWIN_API_TOKEN is required for this command")
    return cfg.token


def require_feed_api_key(cfg) -> str:
    if not cfg.feed_api_key:
        raise ValidationError("AWIN_FEED_API_KEY is required for legacy feed commands")
    return cfg.feed_api_key


def require_proof_of_purchase_api_key(cfg) -> str:
    if not cfg.proof_of_purchase_api_key:
        raise ValidationError("AWIN_PROOF_OF_PURCHASE_API_KEY is required for proof-of-purchase commands")
    return cfg.proof_of_purchase_api_key


def parse_json_response(response: object, *, label: str) -> object:
    try:
        return response.json()
    except Exception as exc:  # noqa: BLE001
        raise ToolError(f"Response for {label} was not JSON: {exc}") from exc


def request_json(
    http,
    *,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
    label: str,
) -> tuple[object, int]:
    response = http.request(
        method,
        url,
        headers=headers,
        params=params,
        json_body=json_body,
    )
    return parse_json_response(response, label=label), response.status


def request_bytes(
    http,
    *,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    label: str,
) -> tuple[bytes, int, dict[str, str]]:
    response = http.request(
        method,
        url,
        headers=headers,
        params=params,
    )
    _ = label
    return response.body, response.status, response.headers


def split_csv_arg(raw: str | None) -> list[str]:
    if raw is None:
        return []
    out: list[str] = []
    for part in str(raw).split(","):
        value = part.strip()
        if value:
            out.append(value)
    return out


def csv_query_value(raw: str | None, *, flag: str) -> str | None:
    values = split_csv_arg(raw)
    if not values:
        return None
    if any("," in value for value in values):
        raise ValidationError(f"Invalid {flag}. Use a comma-separated list without embedded commas")
    return ",".join(values)


def csv_int_query_value(raw: str | None, *, flag: str) -> str | None:
    values = split_csv_arg(raw)
    if not values:
        return None
    for value in values:
        if not value.isdigit():
            raise ValidationError(f"Invalid {flag}. Use a comma-separated list of numeric ids")
    return ",".join(values)


def normalize_country_code(raw: str | None, *, flag: str) -> str | None:
    if raw is None:
        return None
    value = str(raw).strip().upper()
    if not value:
        return None
    if len(value) != 2 or not value.isalpha():
        raise ValidationError(f"Invalid {flag}. Use a two-letter ISO Alpha-2 code like US or GB")
    return value


def normalize_country_codes(raw: str | None, *, flag: str) -> list[str]:
    values = split_csv_arg(raw)
    out: list[str] = []
    for value in values:
        normalized = normalize_country_code(value, flag=flag)
        if normalized:
            out.append(normalized)
    return out


def normalize_positive_int(raw: Any, *, flag: str, minimum: int | None = None, maximum: int | None = None) -> int:
    try:
        value = int(raw)
    except Exception:
        raise ValidationError(f"Invalid {flag}. Use an integer") from None
    if minimum is not None and value < minimum:
        raise ValidationError(f"Invalid {flag}. Minimum is {minimum}")
    if maximum is not None and value > maximum:
        raise ValidationError(f"Invalid {flag}. Maximum is {maximum}")
    return value


def normalize_iso_date(raw: str | None, *, flag: str) -> str:
    value = str(raw or "").strip()
    if not value:
        raise ValidationError(f"Missing {flag}")
    try:
        date.fromisoformat(value)
    except Exception:
        raise ValidationError(f"Invalid {flag}. Use YYYY-MM-DD") from None
    return value


def normalize_iso_datetime(raw: str | None, *, flag: str) -> str:
    value = str(raw or "").strip()
    if not value:
        raise ValidationError(f"Missing {flag}")
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except Exception:
        raise ValidationError(f"Invalid {flag}. Use ISO 8601 like 2026-01-31T23:59:59Z") from None
    if parsed.tzinfo is None:
        raise ValidationError(f"Invalid {flag}. Include a timezone like Z or +00:00")
    return value


def validate_max_date_range_days(*, start: str, end: str, max_days: int, label: str, date_only: bool) -> None:
    if date_only:
        start_value = date.fromisoformat(start)
        end_value = date.fromisoformat(end)
        delta_days = (end_value - start_value).days
    else:
        start_value = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_value = datetime.fromisoformat(end.replace("Z", "+00:00"))
        delta_days = (end_value - start_value).total_seconds() / 86400
    if delta_days < 0:
        raise ValidationError(f"Invalid {label}. end date cannot be before start date")
    if delta_days > max_days:
        raise ValidationError(f"Invalid {label}. Maximum supported range is {max_days} days")


def normalize_timezone(raw: str | None, *, default: str = "UTC") -> str:
    value = str(raw or "").strip()
    return value or default


def normalize_optional_str(raw: str | None) -> str | None:
    value = str(raw or "").strip()
    return value or None


def safe_query_sent(params: dict[str, Any], *, include_access_token: bool = True) -> list[str]:
    keys = sorted(str(key) for key in params.keys())
    return (["accessToken"] if include_access_token else []) + keys


def load_json_file(path_raw: str | None, *, label: str) -> tuple[object, Path]:
    path_str = str(path_raw or "").strip()
    if not path_str:
        raise ValidationError(f"Missing {label}")
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"{label} not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8")), path
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{label} was not valid JSON: {exc}") from exc


def write_json_file(path_raw: str | None, payload: dict[str, Any]) -> str | None:
    path_str = str(path_raw or "").strip()
    if not path_str:
        return None
    path = Path(path_str).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(path)


def require_apply_and_yes(ctx: dict[str, Any], *, reason: str) -> None:
    if not bool(ctx.get("apply")):
        raise SafetyError(reason)
    if not bool(ctx.get("yes")):
        raise SafetyError(reason)


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_out_path(out_raw: str | None, *, overwrite: bool) -> Path:
    out_path = str(out_raw or "").strip()
    if not out_path:
        raise ValidationError("Missing --out")
    path = Path(out_path).expanduser().resolve()
    if path.exists() and not overwrite:
        raise ValidationError(f"Output file already exists: {path} (use --overwrite to replace it)")
    if path.exists() and path.is_dir():
        raise ValidationError(f"Output path is a directory: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_download_file(
    *,
    out_path: Path,
    data: bytes,
    content_type: str | None,
) -> dict[str, Any]:
    out_path.write_bytes(data)
    return {
        "path": str(out_path),
        "bytes_written": len(data),
        "sha256": sha256_of_bytes(data),
        "content_type": content_type,
        "line_count": data.count(b"\n"),
    }


def parse_csv_text(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(text.splitlines())
    rows: list[dict[str, str]] = []
    for row in reader:
        rows.append({str(k or ""): str(v or "") for k, v in row.items()})
    return rows


def validate_feed_download_url(url: str) -> str:
    value = url.strip()
    if not value:
        raise ValidationError("Missing --download-url")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        raise ValidationError("Invalid --download-url. Use an http or https URL from Awin")
    if parsed.netloc not in {"productdata.awin.com", "datafeed.api.productserve.com"}:
        raise ValidationError("Invalid --download-url. Use a legacy product feed URL generated by Awin")
    if "/datafeed/download/" not in parsed.path:
        raise ValidationError("Invalid --download-url. Expected an Awin legacy feed download URL")
    return value
