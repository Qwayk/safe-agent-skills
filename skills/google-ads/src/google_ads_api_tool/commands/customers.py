from __future__ import annotations

from typing import Any

from ..google_ads_client import build_google_ads_client, parse_customer_id_from_resource_name


def cmd_customers_list_accessible(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    cfg = ctx["cfg"]
    client = build_google_ads_client(cfg)
    customer_service = client.get_service("CustomerService")
    resp = customer_service.list_accessible_customers()

    resource_names = list(getattr(resp, "resource_names", []) or [])
    customer_ids: list[str] = []
    for rn in resource_names:
        cid = parse_customer_id_from_resource_name(str(rn))
        if cid:
            customer_ids.append(cid)

    out = {
        "ok": True,
        "customer_count": len(customer_ids),
        "customer_ids": customer_ids,
        "resource_names": resource_names,
    }
    ctx["audit"].write("customers.list_accessible", {"ok": True, "customer_count": len(customer_ids)})
    ctx["out"].emit(out)
    return 0

