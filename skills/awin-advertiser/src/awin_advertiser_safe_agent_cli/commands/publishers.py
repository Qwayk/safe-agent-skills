from __future__ import annotations

from ..errors import ValidationError
from .read_api import read_request, extract_list, redact_error, require_read_context


def cmd_publishers_list(args, ctx) -> int:
    cfg = require_read_context(ctx["out"], ctx["cfg"])
    if cfg is None:
        return 1

    advertiser_id = str(getattr(args, "advertiser_id", "") or "").strip()
    if not advertiser_id:
        out = {
            "ok": False,
            "error": "Missing --advertiser-id",
            "error_type": "ValidationError",
            "blocked": False,
        }
        ctx["out"].emit(out)
        return 1

    token = cfg.token
    http = ctx["http_client"]
    url_path = f"advertisers/{advertiser_id}/publishers"
    endpoint = "/advertisers/{advertiser_id}/publishers".format(advertiser_id=advertiser_id)

    try:
        resp = read_request(http= http, base_url=cfg.base_url, token=token, endpoint=url_path)
    except Exception as exc:  # noqa: BLE001
        message = redact_error(str(exc), token)
        raise ValidationError(f"publishers list request failed: {message}") from exc

    try:
        payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"publishers list response was not JSON: {exc}") from exc

    items = extract_list(payload, keys=("publishers", "items", "data"))

    out = {
        "ok": True,
        "command": "publishers list",
        "advertiser_id": advertiser_id,
        "endpoint": endpoint,
        "method": "GET",
        "status": resp.status,
        "count": len(items),
        "publishers": items,
    }
    ctx["out"].emit(out)
    return 0
