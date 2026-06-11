from __future__ import annotations

from ..errors import ValidationError
from .api_helpers import build_access_token_query, build_bearer_headers


PROGRAMS_LIST_RELATIONSHIPS = ("joined", "pending", "suspended", "rejected", "notjoined")
PROGRAMS_DETAILS_RELATIONSHIPS = PROGRAMS_LIST_RELATIONSHIPS + ("any",)

_PROGRAMS_LIST_PATH = "/publishers/{publisher_id}/programmes"
_PROGRAMS_DETAILS_PATH = "/publishers/{publisher_id}/programmedetails"


def _to_bool_str(value: bool) -> str:
    return "true" if value else "false"


def _normalize_params(
    relationship: str | None,
    country_code: str | None,
    include_hidden: bool,
) -> dict[str, str]:
    params: dict[str, str] = {}
    if relationship:
        if relationship not in PROGRAMS_LIST_RELATIONSHIPS:
            raise ValidationError(
                "Invalid --relationship for programs list. "
                f"Use one of: {', '.join(PROGRAMS_LIST_RELATIONSHIPS)}"
            )
        if include_hidden:
            raise ValidationError("--include-hidden can only be used when --relationship is not set")
        params["relationship"] = relationship
    if country_code:
        normalized_country = country_code.strip().upper()
        if len(normalized_country) != 2 or not normalized_country.isalpha():
            raise ValidationError("Invalid --country-code. Use a two-letter ISO Alpha-2 country code like US or GB")
        params["countryCode"] = normalized_country
    if include_hidden:
        params["includeHidden"] = _to_bool_str(include_hidden)
    return params


def _send_program_request(cfg, http, method: str, path: str, params: dict[str, str]) -> tuple[object, int]:
    headers = build_bearer_headers(cfg.token or "")
    query = build_access_token_query(cfg.token or "")
    query.update(params)

    resp = http.request(
        "GET",
        f"{cfg.api_host}{path}",
        headers=headers,
        params=query,
    )
    try:
        payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"Response for {method} {path} was not JSON: {exc}") from exc

    return payload, resp.status


def cmd_programs_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]

    publisher_id = str(args.publisher_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")

    params = _normalize_params(
        relationship=getattr(args, "relationship", None),
        country_code=getattr(args, "country_code", None),
        include_hidden=bool(getattr(args, "include_hidden", False)),
    )
    payload, status = _send_program_request(
        cfg,
        http,
        "programs.list",
        _PROGRAMS_LIST_PATH.format(publisher_id=publisher_id),
        params,
    )

    response_payload = {
        "operation": "programs.list",
        "ok": True,
        "publisher_id": publisher_id,
        "programs": payload,
        "request": {
            "method": "GET",
            "endpoint": f"{cfg.api_host}/publishers/{publisher_id}/programmes",
            "query": {
                "required": ["accessToken"],
                "sent": ["accessToken"] + sorted(params.keys()),
            },
            "response_status": status,
        },
        "metadata": {
            "auth_mode": "bearer",
            "relationship": args.relationship or None,
            "country_code": params.get("countryCode"),
            "include_hidden": bool(args.include_hidden),
        },
    }

    ctx["audit"].write("programs.list", response_payload)
    ctx["out"].emit(response_payload)
    return 0


def cmd_programs_details(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]

    publisher_id = str(args.publisher_id).strip()
    advertiser_id = str(args.advertiser_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")
    if not advertiser_id:
        raise ValidationError("Missing --advertiser-id")

    params = {}
    relationship = getattr(args, "relationship", None)
    if relationship:
        if relationship not in PROGRAMS_DETAILS_RELATIONSHIPS:
            raise ValidationError(
                "Invalid --relationship for programs details. "
                f"Use one of: {', '.join(PROGRAMS_DETAILS_RELATIONSHIPS)}"
            )
        params["relationship"] = relationship
    params["advertiserId"] = advertiser_id

    payload, status = _send_program_request(
        cfg,
        http,
        "programs.details",
        _PROGRAMS_DETAILS_PATH.format(publisher_id=publisher_id),
        params,
    )

    out = {
        "operation": "programs.details",
        "ok": True,
        "publisher_id": publisher_id,
        "advertiser_id": advertiser_id,
        "program": payload,
        "request": {
            "method": "GET",
            "endpoint": f"{cfg.api_host}/publishers/{publisher_id}/programmedetails",
            "query": {
                "required": ["accessToken", "advertiserId"],
                "sent": ["accessToken"] + sorted(params.keys()),
            },
            "response_status": status,
        },
        "metadata": {
            "auth_mode": "bearer",
            "relationship": args.relationship or None,
        },
    }

    ctx["audit"].write("programs.details", out)
    ctx["out"].emit(out)
    return 0
