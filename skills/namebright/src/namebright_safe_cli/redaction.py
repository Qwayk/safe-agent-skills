from __future__ import annotations

from typing import Any

REDACTED_VALUE = "***REDACTED***"

SENSITIVE_KEYS = {
    "accesstoken",
    "token",
    "accesstokenstatus",
    "apikey",
    "password",
    "secret",
    "clientsecret",
    "authorization",
    "authcode",
    "authcodefile",
    "accountbalance",
    "verification",
    "verificationcode",
    "verificationcodefile",
    "linkauthcode",
    "linkauthcodefile",
}

PII_SAFE_EXTRA_KEYS = {
    "accountbalance",
    "authcode",
    "authcodefile",
    "verificationcode",
    "verification",
    "linkauthcode",
    "linkauthcodefile",
    "token",
}

PII_SENSITIVE_KEYS = {
    "firstname",
    "lastname",
    "organization",
    "department",
    "address1",
    "address2",
    "city",
    "region",
    "country",
    "postalcode",
    "email",
    "emailaddress",
    "phone",
    "phonecountry",
    "phonenumber",
    "phonenumbercountrycode",
    "fax",
    "faxcountry",
}


def _normalize_key(key: Any) -> str:
    return str(key).lower().replace("-", "").replace("_", "").replace(" ", "")


def _contains_secret_fragment(value: str, secret_values: tuple[str, ...]) -> str:
    out = value
    for candidate in sorted((secret_values), key=len, reverse=True):
        if candidate:
            out = out.replace(candidate, REDACTED_VALUE)
    return out


def redact_string(value: str, *, secret_values: tuple[str, ...] = ()) -> str:
    if not isinstance(value, str):
        return str(value)
    return _contains_secret_fragment(value, tuple(secret_values))


def _normalized_key_set(keys: tuple[str, ...]) -> set[str]:
    return {str(key).lower().replace("-", "").replace("_", "").replace(" ", "") for key in keys if key}


def redact_object(
    value: Any,
    *,
    secret_values: tuple[str, ...] = (),
    extra_sensitive_keys: tuple[str, ...] = (),
    redact_pii: bool = False,
) -> Any:
    extra = _normalized_key_set(extra_sensitive_keys)
    pii = _normalized_key_set(tuple(PII_SENSITIVE_KEYS)) if redact_pii else set()
    sensitive = _normalized_key_set(tuple(SENSITIVE_KEYS)).union(extra).union(pii)

    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            norm_key = _normalize_key(key)
            if norm_key in sensitive:
                out[key] = REDACTED_VALUE
            else:
                out[key] = redact_object(
                    item,
                    secret_values=secret_values,
                    extra_sensitive_keys=extra_sensitive_keys,
                    redact_pii=redact_pii,
                )
        return out
    if isinstance(value, list):
        return [
            redact_object(
                item,
                secret_values=secret_values,
                extra_sensitive_keys=extra_sensitive_keys,
                redact_pii=redact_pii,
            )
            for item in value
        ]
    if isinstance(value, tuple):
        return tuple(
            redact_object(
                item,
                secret_values=secret_values,
                extra_sensitive_keys=extra_sensitive_keys,
                redact_pii=redact_pii,
            )
            for item in value
        )
    if isinstance(value, str):
        return redact_string(value, secret_values=secret_values)
    return value


def redact_headers(headers: dict[str, Any], *, secret_values: tuple[str, ...] = (), redact_pii: bool = False) -> dict[str, str]:
    return {
        str(key): (
            REDACTED_VALUE
            if _normalize_key(key) in _normalized_key_set(tuple(SENSITIVE_KEYS)).union(
                _normalized_key_set(tuple(PII_SENSITIVE_KEYS)) if redact_pii else set()
            )
            else redact_string(str(value), secret_values=secret_values)
        )
        for key, value in headers.items()
    }


__all__ = [
    "REDACTED_VALUE",
    "redact_object",
    "redact_string",
    "redact_headers",
    "SENSITIVE_KEYS",
    "PII_SAFE_EXTRA_KEYS",
]
