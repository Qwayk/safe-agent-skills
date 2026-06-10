from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..google_ads_client import build_google_ads_client, protobuf_to_dict
from ..json_files import read_json_file
from ..protobuf_json import parse_request_json
from ..rpc_commands import _call_with_retries, _cmd_write
from ..rpc_v22_registry import RPC_METHODS_V22, RpcMethodSpec


def register_helper_commands(sub: argparse._SubParsersAction) -> None:
    helpers = sub.add_parser("helpers", help="Common write helpers for repeated Google Ads jobs")
    helpers_sub = helpers.add_subparsers(dest="helpers_cmd", required=True, parser_class=type(helpers))

    keywords = helpers_sub.add_parser("keywords", help="Keyword helpers")
    keywords_sub = keywords.add_subparsers(dest="helpers_keywords_cmd", required=True, parser_class=type(keywords))

    keywords_pause = keywords_sub.add_parser("pause-from-list", help="Pause existing keyword criteria from a JSON list")
    keywords_pause.add_argument("--customer-id", required=True, help="Customer id (digits)")
    keywords_pause.add_argument("--items", required=True, help="JSON or CSV list of keyword criteria to pause")
    keywords_pause.set_defaults(func=cmd_helpers_keywords_pause_from_list, write_capable=True)

    keywords_add = keywords_sub.add_parser("add-from-list", help="Add keywords from a JSON list")
    keywords_add.add_argument("--customer-id", required=True, help="Customer id (digits)")
    keywords_add.add_argument("--items", required=True, help="JSON or CSV list of keywords to add")
    keywords_add.add_argument("--ad-group-id", default=None, help="Default ad group id for items that do not include one")
    keywords_add.add_argument("--match-type", default="EXACT", help="Default match type (EXACT, PHRASE, BROAD)")
    keywords_add.add_argument("--status", default="ENABLED", help="Default status for created keywords")
    keywords_add.set_defaults(func=cmd_helpers_keywords_add_from_list, write_capable=True)

    negatives = helpers_sub.add_parser("campaign-negatives", help="Campaign negative keyword helpers")
    negatives_sub = negatives.add_subparsers(
        dest="helpers_campaign_negatives_cmd",
        required=True,
        parser_class=type(negatives),
    )
    negatives_add = negatives_sub.add_parser("add-from-list", help="Add campaign negative keywords from a JSON list")
    negatives_add.add_argument("--customer-id", required=True, help="Customer id (digits)")
    negatives_add.add_argument("--items", required=True, help="JSON or CSV list of campaign negatives to add")
    negatives_add.add_argument("--campaign-id", default=None, help="Default campaign id for items that do not include one")
    negatives_add.add_argument("--match-type", default="PHRASE", help="Default match type (EXACT, PHRASE, BROAD)")
    negatives_add.set_defaults(func=cmd_helpers_campaign_negatives_add_from_list, write_capable=True)

    campaign = helpers_sub.add_parser("campaign", help="Campaign update helpers")
    campaign_sub = campaign.add_subparsers(dest="helpers_campaign_cmd", required=True, parser_class=type(campaign))

    budget = campaign_sub.add_parser("set-budget", help="Set campaign budget amount_micros")
    budget.add_argument("--customer-id", required=True, help="Customer id (digits)")
    budget.add_argument("--budget-id", default=None, help="Campaign budget id (digits)")
    budget.add_argument("--resource-name", default=None, help="Campaign budget resource name")
    budget.add_argument("--amount", default=None, help="Budget amount in normal currency units, for example 70 or 70.50")
    budget.add_argument("--amount-micros", type=int, default=None, help="Budget amount in micros")
    budget.set_defaults(func=cmd_helpers_campaign_set_budget, write_capable=True)

    cpc = campaign_sub.add_parser(
        "set-max-clicks-cpc-ceiling",
        help="Set the Maximize Clicks CPC ceiling for a campaign",
    )
    cpc.add_argument("--customer-id", required=True, help="Customer id (digits)")
    cpc.add_argument("--campaign-id", default=None, help="Campaign id (digits)")
    cpc.add_argument("--resource-name", default=None, help="Campaign resource name")
    cpc.add_argument("--amount", default=None, help="CPC ceiling in normal currency units, for example 12 or 12.50")
    cpc.add_argument("--amount-micros", type=int, default=None, help="CPC ceiling in micros")
    cpc.set_defaults(func=cmd_helpers_campaign_set_max_clicks_cpc_ceiling, write_capable=True)

    entities = helpers_sub.add_parser("entities", help="Enable or pause campaigns, ad groups, and ads")
    entities_sub = entities.add_subparsers(dest="helpers_entities_cmd", required=True, parser_class=type(entities))

    entities_lookup = entities_sub.add_parser("lookup-by-name", help="Find campaigns, ad groups, budgets, or conversions by name")
    entities_lookup.add_argument("--customer-id", required=True, help="Customer id (digits)")
    entities_lookup.add_argument(
        "--resource-type",
        required=True,
        choices=("campaign", "ad-group", "campaign-budget", "conversion-action"),
    )
    entities_lookup.add_argument("--name", required=True, help="Name to search for")
    entities_lookup.add_argument("--match", choices=("exact", "contains"), default="exact")
    entities_lookup.add_argument("--limit", type=int, default=20, help="Max rows to return (default: 20)")
    entities_lookup.set_defaults(func=cmd_helpers_entities_lookup_by_name, write_capable=False)

    entities_pause = entities_sub.add_parser("pause", help="Pause entities from a JSON list")
    entities_pause.add_argument("--customer-id", required=True, help="Customer id (digits)")
    entities_pause.add_argument("--resource-type", required=True, choices=("campaign", "ad-group", "ad-group-ad"))
    entities_pause.add_argument("--items", required=True, help="JSON or CSV list of entity ids or resource names")
    entities_pause.set_defaults(func=cmd_helpers_entities_pause, write_capable=True)

    entities_enable = entities_sub.add_parser("enable", help="Enable entities from a JSON list")
    entities_enable.add_argument("--customer-id", required=True, help="Customer id (digits)")
    entities_enable.add_argument("--resource-type", required=True, choices=("campaign", "ad-group", "ad-group-ad"))
    entities_enable.add_argument("--items", required=True, help="JSON or CSV list of entity ids or resource names")
    entities_enable.set_defaults(func=cmd_helpers_entities_enable, write_capable=True)

    campaign_tree = helpers_sub.add_parser("campaign-tree", help="Enable or pause a campaign and its children together")
    campaign_tree_sub = campaign_tree.add_subparsers(
        dest="helpers_campaign_tree_cmd",
        required=True,
        parser_class=type(campaign_tree),
    )

    for action_name, func in (
        ("pause", cmd_helpers_campaign_tree_pause),
        ("enable", cmd_helpers_campaign_tree_enable),
    ):
        action = campaign_tree_sub.add_parser(action_name, help=f"{action_name.title()} a campaign tree")
        action.add_argument("--customer-id", required=True, help="Customer id (digits)")
        action.add_argument("--campaign-id", default=None, help="Campaign id (digits)")
        action.add_argument("--campaign-name", default=None, help="Campaign name for lookup")
        action.add_argument("--campaign-resource", default=None, help="Campaign resource name")
        action.add_argument("--name-match", choices=("exact", "contains"), default="exact")
        action.add_argument("--include-ad-groups", action="store_true", help="Also update child ad groups")
        action.add_argument("--include-ads", action="store_true", help="Also update ads under child ad groups")
        action.set_defaults(func=func, write_capable=True)

    precheck = helpers_sub.add_parser("precheck", help="Read-only prechecks for overlap and policy risk")
    precheck_sub = precheck.add_subparsers(dest="helpers_precheck_cmd", required=True, parser_class=type(precheck))

    overlap = precheck_sub.add_parser("overlap", help="Find positive keyword overlap across campaigns")
    overlap.add_argument("--customer-id", required=True, help="Customer id (digits)")
    overlap.add_argument(
        "--campaign-id",
        action="append",
        default=[],
        help="Optional campaign id to limit the check. Repeat for more than one.",
    )
    overlap.add_argument("--limit", type=int, default=1000, help="Max keyword rows to inspect (default: 1000)")
    overlap.set_defaults(func=cmd_helpers_precheck_overlap, write_capable=False)

    policy = precheck_sub.add_parser("policy-risk", help="Flag risky keyword themes before launch")
    policy.add_argument("--items", required=True, help="JSON or CSV list of planned keywords or negatives")
    policy.add_argument("--strict", action="store_true", help="Return a failed result when risky terms are found")
    policy.set_defaults(func=cmd_helpers_precheck_policy_risk, write_capable=False)

    offline = helpers_sub.add_parser("offline", help="Offline conversion helpers")
    offline_sub = offline.add_subparsers(dest="helpers_offline_cmd", required=True, parser_class=type(offline))

    upload_clicks = offline_sub.add_parser(
        "upload-click-conversions",
        help="Upload click conversions from a JSON list without writing a full RPC envelope",
    )
    upload_clicks.add_argument("--customer-id", required=True, help="Customer id (digits)")
    upload_clicks.add_argument("--items", required=True, help="JSON or CSV list of click conversions")
    upload_clicks.add_argument("--validate-only", action="store_true", help="Validate the upload without applying it")
    upload_clicks.add_argument(
        "--no-partial-failure",
        action="store_true",
        help="Disable partial failure mode (default is partial failure on)",
    )
    upload_clicks.add_argument("--job-id", type=int, default=None, help="Optional job id for the upload request")
    upload_clicks.set_defaults(func=cmd_helpers_offline_upload_click_conversions, write_capable=True)


def _rpc_spec(service: str, method: str) -> RpcMethodSpec:
    for spec in RPC_METHODS_V22:
        if spec.service == service and spec.method == method:
            return spec
    raise ValidationError(f"Unknown RPC spec: {service}.{method}")


def _digits(value: Any, *, label: str) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if not digits:
        raise ValidationError(f"Missing or invalid {label}.")
    return digits


def _normalize_status(value: str, *, label: str) -> str:
    status = str(value or "").strip().upper()
    if status not in {"ENABLED", "PAUSED"}:
        raise ValidationError(f"{label} must be ENABLED or PAUSED.")
    return status


def _normalize_match_type(value: str, *, label: str) -> str:
    match_type = str(value or "").strip().upper()
    if match_type not in {"EXACT", "PHRASE", "BROAD"}:
        raise ValidationError(f"{label} must be EXACT, PHRASE, or BROAD.")
    return match_type


def _amount_to_micros(amount: str) -> int:
    try:
        dec = Decimal(str(amount).strip())
    except (InvalidOperation, ValueError):
        raise ValidationError("Amount must be a valid number.") from None
    if dec < 0:
        raise ValidationError("Amount must not be negative.")
    return int((dec * Decimal("1000000")).to_integral_value(rounding=ROUND_HALF_UP))


def _resolve_amount_micros(*, amount: Any, amount_micros: Any) -> int:
    if amount_micros is not None:
        micros = int(amount_micros)
        if micros < 0:
            raise ValidationError("amount_micros must not be negative.")
        return micros
    if amount is None:
        raise ValidationError("Pass either --amount or --amount-micros.")
    return _amount_to_micros(str(amount))


def _load_items(path_value: str) -> list[Any]:
    path = Path(str(path_value))
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValidationError("CSV items file must have a header row.")
            rows: list[dict[str, Any]] = []
            for row in reader:
                cleaned = {
                    str(key).strip(): str(value or "").strip()
                    for key, value in row.items()
                    if key is not None and str(key).strip()
                }
                if any(str(value).strip() for value in cleaned.values()):
                    rows.append(cleaned)
            return rows

    obj = read_json_file(path)
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        if isinstance(obj.get("items"), list):
            return obj["items"]
        if isinstance(obj.get("conversions"), list):
            return obj["conversions"]
    raise ValidationError("Items file must be a JSON list or an object with an `items` or `conversions` list.")


def _escape_gaql_string(value: str) -> str:
    return str(value or "").replace("\\", "\\\\").replace("'", "\\'")


def _gaql_rows(*, ctx: dict[str, Any], customer_id: str, query: str, limit: int | None = None) -> list[dict[str, Any]]:
    client = build_google_ads_client(ctx["cfg"])
    ga_service = client.get_service("GoogleAdsService")
    req = client.get_type("SearchGoogleAdsRequest")
    req.customer_id = customer_id
    req.query = query
    rows = _call_with_retries(lambda: ga_service.search(request=req), ctx=ctx)
    out_rows: list[dict[str, Any]] = []
    for row in rows:
        out_rows.append(protobuf_to_dict(row))
        if limit is not None and len(out_rows) >= limit:
            break
    return out_rows


def _campaign_resource_name(customer_id: str, campaign_id: str) -> str:
    return f"customers/{customer_id}/campaigns/{_digits(campaign_id, label='campaign_id')}"


def _campaign_budget_resource_name(customer_id: str, budget_id: str) -> str:
    return f"customers/{customer_id}/campaignBudgets/{_digits(budget_id, label='budget_id')}"


def _ad_group_resource_name(customer_id: str, ad_group_id: str) -> str:
    return f"customers/{customer_id}/adGroups/{_digits(ad_group_id, label='ad_group_id')}"


def _ad_group_criterion_resource_name(customer_id: str, ad_group_id: str, criterion_id: str) -> str:
    return (
        f"customers/{customer_id}/adGroupCriteria/"
        f"{_digits(ad_group_id, label='ad_group_id')}~{_digits(criterion_id, label='criterion_id')}"
    )


def _ad_group_ad_resource_name(customer_id: str, ad_group_id: str, ad_id: str) -> str:
    return (
        f"customers/{customer_id}/adGroupAds/"
        f"{_digits(ad_group_id, label='ad_group_id')}~{_digits(ad_id, label='ad_id')}"
    )


LOOKUP_RESOURCE_QUERIES: dict[str, dict[str, str]] = {
    "campaign": {
        "table": "campaign",
        "name_field": "campaign.name",
        "resource_name_field": "campaign.resource_name",
        "id_field": "campaign.id",
        "select": "campaign.resource_name, campaign.id, campaign.name, campaign.status",
        "order_by": "campaign.id",
    },
    "ad-group": {
        "table": "ad_group",
        "name_field": "ad_group.name",
        "resource_name_field": "ad_group.resource_name",
        "id_field": "ad_group.id",
        "select": "ad_group.resource_name, ad_group.id, ad_group.name, ad_group.status, ad_group.campaign",
        "order_by": "ad_group.id",
    },
    "campaign-budget": {
        "table": "campaign_budget",
        "name_field": "campaign_budget.name",
        "resource_name_field": "campaign_budget.resource_name",
        "id_field": "campaign_budget.id",
        "select": "campaign_budget.resource_name, campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros",
        "order_by": "campaign_budget.id",
    },
    "conversion-action": {
        "table": "conversion_action",
        "name_field": "conversion_action.name",
        "resource_name_field": "conversion_action.resource_name",
        "id_field": "conversion_action.id",
        "select": (
            "conversion_action.resource_name, conversion_action.id, conversion_action.name, "
            "conversion_action.status, conversion_action.type, conversion_action.primary_for_goal"
        ),
        "order_by": "conversion_action.id",
    },
}


def _resource_name_from_item(item: Any, *, customer_id: str, resource_type: str) -> str:
    if isinstance(item, str):
        s = item.strip()
        if not s:
            raise ValidationError("Item strings must not be empty.")
        if s.startswith("customers/"):
            return s
        if resource_type == "campaign":
            return _campaign_resource_name(customer_id, s)
        if resource_type == "ad-group":
            return _ad_group_resource_name(customer_id, s)
        raise ValidationError("ad-group-ad items must include a resource_name or both ad_group_id and ad_id.")

    if not isinstance(item, dict):
        raise ValidationError("Each item must be a string or object.")

    resource_name = str(item.get("resource_name") or "").strip()
    if resource_name:
        return resource_name

    if resource_type == "campaign":
        return _campaign_resource_name(customer_id, str(item.get("campaign_id") or ""))
    if resource_type == "ad-group":
        return _ad_group_resource_name(customer_id, str(item.get("ad_group_id") or ""))
    if resource_type == "ad-group-ad":
        return _ad_group_ad_resource_name(
            customer_id,
            str(item.get("ad_group_id") or ""),
            str(item.get("ad_id") or ""),
        )
    raise ValidationError(f"Unsupported resource_type: {resource_type}")


def _lookup_by_name(
    *,
    ctx: dict[str, Any],
    customer_id: str,
    resource_type: str,
    name: str,
    match: str,
    limit: int,
) -> list[dict[str, Any]]:
    spec = LOOKUP_RESOURCE_QUERIES.get(resource_type)
    if spec is None:
        raise ValidationError(f"Unsupported lookup resource type: {resource_type}")
    normalized_match = str(match or "exact").strip().lower()
    if normalized_match not in {"exact", "contains"}:
        raise ValidationError("match must be exact or contains.")
    escaped_name = _escape_gaql_string(name)
    if normalized_match == "exact":
        where = f"{spec['name_field']} = '{escaped_name}'"
    else:
        where = f"{spec['name_field']} LIKE '%{escaped_name}%'"
    query = (
        f"SELECT {spec['select']} "
        f"FROM {spec['table']} "
        f"WHERE {where} "
        f"ORDER BY {spec['order_by']} "
        f"LIMIT {max(1, int(limit or 20))}"
    )
    return _gaql_rows(ctx=ctx, customer_id=customer_id, query=query, limit=max(1, int(limit or 20)))


def _resolve_single_lookup_resource_name(
    *,
    ctx: dict[str, Any],
    customer_id: str,
    resource_type: str,
    name: str,
    match: str,
) -> str:
    rows = _lookup_by_name(
        ctx=ctx,
        customer_id=customer_id,
        resource_type=resource_type,
        name=name,
        match=match,
        limit=10,
    )
    if not rows:
        raise ValidationError(f"No {resource_type} matched name: {name}")
    if len(rows) > 1:
        raise ValidationError(f"Name lookup matched more than one {resource_type}; refine the name or use an id/resource name.")
    spec = LOOKUP_RESOURCE_QUERIES[resource_type]
    resource_name = (
        rows[0]
        .get(spec["table"], {})
        .get(spec["resource_name_field"].split(".", 1)[1])
    )
    if not isinstance(resource_name, str) or not resource_name.strip():
        raise ValidationError(f"Matched {resource_type} row did not include a resource name.")
    return resource_name.strip()


POLICY_RISK_RULES: tuple[tuple[str, str], ...] = (
    ("locksmith", "restricted locksmith services"),
    ("locked out", "lockout intent"),
    ("lockout", "lockout intent"),
    ("unlock", "lockout intent"),
    ("rekey", "locksmith rekey intent"),
    ("keys", "key-copy or locksmith intent"),
    ("key replacement", "key-copy or locksmith intent"),
    ("broken glass", "glass replacement intent"),
    ("replacement glass", "glass replacement intent"),
    ("screen repair", "screen-only intent"),
    ("screen replacement", "screen-only intent"),
    ("buy parts", "parts buyer intent"),
    ("diy", "do-it-yourself intent"),
)


def _policy_risk_hits(items: list[Any]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        texts: list[str] = []
        if isinstance(item, str):
            texts.append(item.strip())
        elif isinstance(item, dict):
            for key in ("text", "keyword", "name", "resource_name"):
                value = str(item.get(key) or "").strip()
                if value:
                    texts.append(value)
        joined = " | ".join(texts).strip()
        if not joined:
            continue
        lowered = joined.lower()
        matched_reasons = sorted({reason for token, reason in POLICY_RISK_RULES if token in lowered})
        if matched_reasons:
            hits.append(
                {
                    "item_index": index,
                    "text": joined,
                    "reasons": matched_reasons,
                }
            )
    return hits


def _keyword_criterion_resource_name(item: Any, *, customer_id: str) -> str:
    if isinstance(item, str):
        s = item.strip()
        if not s:
            raise ValidationError("Item strings must not be empty.")
        if s.startswith("customers/"):
            return s
        raise ValidationError(
            "Keyword pause items must be resource names or objects with resource_name, ad_group_id, and criterion_id."
        )
    if not isinstance(item, dict):
        raise ValidationError("Each keyword pause item must be a string or object.")

    resource_name = str(item.get("resource_name") or "").strip()
    if resource_name:
        return resource_name
    return _ad_group_criterion_resource_name(
        customer_id,
        str(item.get("ad_group_id") or ""),
        str(item.get("criterion_id") or ""),
    )


def _execute_helper_write(
    *,
    service: str,
    method: str,
    request_obj: dict[str, Any],
    ctx: dict[str, Any],
    customer_id_override: str,
    in_path_label: str,
) -> int:
    spec = _rpc_spec(service, method)
    msg = parse_request_json(
        service=service,
        request_type=spec.request_type,
        obj=request_obj,
        customer_id_override=customer_id_override,
    )
    return _cmd_write(
        spec=spec,
        request_msg=msg,
        in_path=in_path_label,
        ctx=ctx,
        customer_id_override=customer_id_override,
    )


def build_keywords_pause_request(*, customer_id: str, items: list[Any]) -> dict[str, Any]:
    cid = _digits(customer_id, label="customer_id")
    operations = []
    for item in items:
        operations.append(
            {
                "update": {
                    "resource_name": _keyword_criterion_resource_name(item, customer_id=cid),
                    "status": "PAUSED",
                },
                "update_mask": "status",
            }
        )
    if not operations:
        raise ValidationError("Items list must not be empty.")
    return {"customer_id": cid, "operations": operations}


def build_keywords_add_request(
    *,
    customer_id: str,
    items: list[Any],
    default_ad_group_id: str | None,
    default_match_type: str,
    default_status: str,
) -> dict[str, Any]:
    cid = _digits(customer_id, label="customer_id")
    match_type = _normalize_match_type(default_match_type, label="match type")
    status = _normalize_status(default_status, label="status")
    operations = []
    for item in items:
        if isinstance(item, str):
            text = item.strip()
            item_obj: dict[str, Any] = {}
        elif isinstance(item, dict):
            item_obj = item
            text = str(item.get("text") or "").strip()
        else:
            raise ValidationError("Keyword add items must be strings or objects.")
        if not text:
            raise ValidationError("Each keyword add item needs a keyword text.")
        ad_group_id = str((item_obj.get("ad_group_id") if isinstance(item_obj, dict) else None) or default_ad_group_id or "").strip()
        if not ad_group_id:
            raise ValidationError("Each keyword add item needs an ad_group_id or a command-level --ad-group-id.")
        item_match_type = _normalize_match_type(
            str(item_obj.get("match_type") or match_type),
            label="match type",
        )
        item_status = _normalize_status(
            str(item_obj.get("status") or status),
            label="status",
        )
        criterion: dict[str, Any] = {
            "ad_group": _ad_group_resource_name(cid, ad_group_id),
            "status": item_status,
            "keyword": {"text": text, "match_type": item_match_type},
        }
        if "cpc_bid_micros" in item_obj and item_obj.get("cpc_bid_micros") is not None:
            criterion["cpc_bid_micros"] = int(item_obj["cpc_bid_micros"])
        operations.append({"create": criterion})
    if not operations:
        raise ValidationError("Items list must not be empty.")
    return {"customer_id": cid, "operations": operations}


def build_campaign_negatives_add_request(
    *,
    customer_id: str,
    items: list[Any],
    default_campaign_id: str | None,
    default_match_type: str,
) -> dict[str, Any]:
    cid = _digits(customer_id, label="customer_id")
    match_type = _normalize_match_type(default_match_type, label="match type")
    operations = []
    for item in items:
        if isinstance(item, str):
            text = item.strip()
            item_obj: dict[str, Any] = {}
        elif isinstance(item, dict):
            item_obj = item
            text = str(item.get("text") or "").strip()
        else:
            raise ValidationError("Campaign negative items must be strings or objects.")
        if not text:
            raise ValidationError("Each campaign negative item needs a keyword text.")
        campaign_id = str(item_obj.get("campaign_id") or default_campaign_id or "").strip()
        if not campaign_id:
            raise ValidationError("Each campaign negative item needs a campaign_id or a command-level --campaign-id.")
        item_match_type = _normalize_match_type(
            str(item_obj.get("match_type") or match_type),
            label="match type",
        )
        operations.append(
            {
                "create": {
                    "campaign": _campaign_resource_name(cid, campaign_id),
                    "negative": True,
                    "keyword": {
                        "text": text,
                        "match_type": item_match_type,
                    },
                }
            }
        )
    if not operations:
        raise ValidationError("Items list must not be empty.")
    return {"customer_id": cid, "operations": operations}


def build_campaign_set_budget_request(
    *,
    customer_id: str,
    budget_id: str | None,
    resource_name: str | None,
    amount: Any,
    amount_micros: Any,
) -> dict[str, Any]:
    cid = _digits(customer_id, label="customer_id")
    rn = str(resource_name or "").strip() or _campaign_budget_resource_name(cid, str(budget_id or ""))
    micros = _resolve_amount_micros(amount=amount, amount_micros=amount_micros)
    return {
        "customer_id": cid,
        "operations": [
            {
                "update": {
                    "resource_name": rn,
                    "amount_micros": micros,
                },
                "update_mask": "amountMicros",
            }
        ],
    }


def build_campaign_set_max_clicks_cpc_ceiling_request(
    *,
    customer_id: str,
    campaign_id: str | None,
    resource_name: str | None,
    amount: Any,
    amount_micros: Any,
) -> dict[str, Any]:
    cid = _digits(customer_id, label="customer_id")
    rn = str(resource_name or "").strip() or _campaign_resource_name(cid, str(campaign_id or ""))
    micros = _resolve_amount_micros(amount=amount, amount_micros=amount_micros)
    return {
        "customer_id": cid,
        "operations": [
            {
                "update": {
                    "resource_name": rn,
                    "target_spend": {
                        "cpc_bid_ceiling_micros": micros,
                    },
                },
                "update_mask": "targetSpend.cpcBidCeilingMicros",
            }
        ],
    }


def build_entity_status_request(
    *,
    customer_id: str,
    resource_type: str,
    items: list[Any],
    status: str,
) -> tuple[str, str, dict[str, Any]]:
    cid = _digits(customer_id, label="customer_id")
    normalized_status = _normalize_status(status, label="status")
    normalized_type = str(resource_type or "").strip()
    if normalized_type not in {"campaign", "ad-group", "ad-group-ad"}:
        raise ValidationError("resource_type must be campaign, ad-group, or ad-group-ad.")

    service_map = {
        "campaign": ("CampaignService", "MutateCampaigns"),
        "ad-group": ("AdGroupService", "MutateAdGroups"),
        "ad-group-ad": ("AdGroupAdService", "MutateAdGroupAds"),
    }

    operations = []
    for item in items:
        operations.append(
            {
                "update": {
                    "resource_name": _resource_name_from_item(
                        item,
                        customer_id=cid,
                        resource_type=normalized_type,
                    ),
                    "status": normalized_status,
                },
                "update_mask": "status",
            }
        )
    if not operations:
        raise ValidationError("Items list must not be empty.")
    request_obj = {"customer_id": cid, "operations": operations}
    service, method = service_map[normalized_type]
    return service, method, request_obj


def build_upload_click_conversions_request(
    *,
    customer_id: str,
    items: list[Any],
    validate_only: bool,
    partial_failure: bool,
    job_id: int | None,
) -> dict[str, Any]:
    cid = _digits(customer_id, label="customer_id")
    conversions: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValidationError("Each click conversion item must be an object.")
        conversion = dict(item)
        conversions.append(conversion)
    if not conversions:
        raise ValidationError("Items list must not be empty.")
    request_obj: dict[str, Any] = {
        "customer_id": cid,
        "conversions": conversions,
        "partial_failure": partial_failure,
        "validate_only": bool(validate_only),
    }
    if job_id is not None:
        request_obj["job_id"] = int(job_id)
    return request_obj


def build_campaign_tree_status_request(
    *,
    ctx: dict[str, Any],
    customer_id: str,
    campaign_id: str | None,
    campaign_name: str | None,
    campaign_resource: str | None,
    name_match: str,
    include_ad_groups: bool,
    include_ads: bool,
    status: str,
) -> dict[str, Any]:
    cid = _digits(customer_id, label="customer_id")
    normalized_status = _normalize_status(status, label="status")
    campaign_rn = str(campaign_resource or "").strip()
    if not campaign_rn:
        if campaign_id:
            campaign_rn = _campaign_resource_name(cid, campaign_id)
        elif campaign_name:
            campaign_rn = _resolve_single_lookup_resource_name(
                ctx=ctx,
                customer_id=cid,
                resource_type="campaign",
                name=str(campaign_name),
                match=name_match,
            )
        else:
            raise ValidationError("Pass --campaign-resource, --campaign-id, or --campaign-name.")

    mutate_operations: list[dict[str, Any]] = [
        {
            "campaign_operation": {
                "update": {
                    "resource_name": campaign_rn,
                    "status": normalized_status,
                },
                "update_mask": "status",
            }
        }
    ]

    ad_group_resource_names: list[str] = []
    if include_ad_groups or include_ads:
        ad_group_rows = _gaql_rows(
            ctx=ctx,
            customer_id=cid,
            query=(
                "SELECT ad_group.resource_name "
                "FROM ad_group "
                f"WHERE ad_group.campaign = '{_escape_gaql_string(campaign_rn)}' "
                "AND ad_group.status IN ('ENABLED', 'PAUSED') "
                "ORDER BY ad_group.id"
            ),
            limit=500,
        )
        for row in ad_group_rows:
            ad_group = row.get("ad_group", {})
            resource_name = str(ad_group.get("resource_name") or "").strip()
            if resource_name:
                ad_group_resource_names.append(resource_name)

    if include_ad_groups:
        for ad_group_rn in ad_group_resource_names:
            mutate_operations.append(
                {
                    "ad_group_operation": {
                        "update": {
                            "resource_name": ad_group_rn,
                            "status": normalized_status,
                        },
                        "update_mask": "status",
                    }
                }
            )

    if include_ads:
        for ad_group_rn in ad_group_resource_names:
            ad_rows = _gaql_rows(
                ctx=ctx,
                customer_id=cid,
                query=(
                    "SELECT ad_group_ad.resource_name "
                    "FROM ad_group_ad "
                    f"WHERE ad_group_ad.ad_group = '{_escape_gaql_string(ad_group_rn)}' "
                    "AND ad_group_ad.status IN ('ENABLED', 'PAUSED')"
                ),
                limit=500,
            )
            for row in ad_rows:
                ad_group_ad = row.get("ad_group_ad", {})
                resource_name = str(ad_group_ad.get("resource_name") or "").strip()
                if not resource_name:
                    continue
                mutate_operations.append(
                    {
                        "ad_group_ad_operation": {
                            "update": {
                                "resource_name": resource_name,
                                "status": normalized_status,
                            },
                            "update_mask": "status",
                        }
                    }
                )

    return {
        "customer_id": cid,
        "mutate_operations": mutate_operations,
    }


def cmd_helpers_keywords_pause_from_list(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    request_obj = build_keywords_pause_request(
        customer_id=str(args.customer_id),
        items=_load_items(str(args.items)),
    )
    return _execute_helper_write(
        service="AdGroupCriterionService",
        method="MutateAdGroupCriteria",
        request_obj=request_obj,
        ctx=ctx,
        customer_id_override=str(args.customer_id),
        in_path_label="helper:keywords.pause-from-list",
    )


def cmd_helpers_keywords_add_from_list(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    request_obj = build_keywords_add_request(
        customer_id=str(args.customer_id),
        items=_load_items(str(args.items)),
        default_ad_group_id=str(args.ad_group_id) if args.ad_group_id else None,
        default_match_type=str(args.match_type),
        default_status=str(args.status),
    )
    return _execute_helper_write(
        service="AdGroupCriterionService",
        method="MutateAdGroupCriteria",
        request_obj=request_obj,
        ctx=ctx,
        customer_id_override=str(args.customer_id),
        in_path_label="helper:keywords.add-from-list",
    )


def cmd_helpers_campaign_negatives_add_from_list(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    request_obj = build_campaign_negatives_add_request(
        customer_id=str(args.customer_id),
        items=_load_items(str(args.items)),
        default_campaign_id=str(args.campaign_id) if args.campaign_id else None,
        default_match_type=str(args.match_type),
    )
    return _execute_helper_write(
        service="CampaignCriterionService",
        method="MutateCampaignCriteria",
        request_obj=request_obj,
        ctx=ctx,
        customer_id_override=str(args.customer_id),
        in_path_label="helper:campaign-negatives.add-from-list",
    )


def cmd_helpers_campaign_set_budget(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    request_obj = build_campaign_set_budget_request(
        customer_id=str(args.customer_id),
        budget_id=str(args.budget_id) if args.budget_id else None,
        resource_name=str(args.resource_name) if args.resource_name else None,
        amount=args.amount,
        amount_micros=args.amount_micros,
    )
    return _execute_helper_write(
        service="CampaignBudgetService",
        method="MutateCampaignBudgets",
        request_obj=request_obj,
        ctx=ctx,
        customer_id_override=str(args.customer_id),
        in_path_label="helper:campaign.set-budget",
    )


def cmd_helpers_campaign_set_max_clicks_cpc_ceiling(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    request_obj = build_campaign_set_max_clicks_cpc_ceiling_request(
        customer_id=str(args.customer_id),
        campaign_id=str(args.campaign_id) if args.campaign_id else None,
        resource_name=str(args.resource_name) if args.resource_name else None,
        amount=args.amount,
        amount_micros=args.amount_micros,
    )
    return _execute_helper_write(
        service="CampaignService",
        method="MutateCampaigns",
        request_obj=request_obj,
        ctx=ctx,
        customer_id_override=str(args.customer_id),
        in_path_label="helper:campaign.set-max-clicks-cpc-ceiling",
    )


def cmd_helpers_entities_lookup_by_name(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    customer_id = _digits(str(args.customer_id), label="customer_id")
    rows = _lookup_by_name(
        ctx=ctx,
        customer_id=customer_id,
        resource_type=str(args.resource_type),
        name=str(args.name),
        match=str(args.match),
        limit=int(args.limit),
    )
    ctx["out"].emit(
        {
            "ok": True,
            "meta": {
                "customer_id": customer_id,
                "resource_type": str(args.resource_type),
                "match": str(args.match),
                "row_count": len(rows),
            },
            "rows": rows,
        }
    )
    return 0


def cmd_helpers_entities_pause(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    service, method, request_obj = build_entity_status_request(
        customer_id=str(args.customer_id),
        resource_type=str(args.resource_type),
        items=_load_items(str(args.items)),
        status="PAUSED",
    )
    return _execute_helper_write(
        service=service,
        method=method,
        request_obj=request_obj,
        ctx=ctx,
        customer_id_override=str(args.customer_id),
        in_path_label=f"helper:entities.pause:{args.resource_type}",
    )


def cmd_helpers_entities_enable(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    service, method, request_obj = build_entity_status_request(
        customer_id=str(args.customer_id),
        resource_type=str(args.resource_type),
        items=_load_items(str(args.items)),
        status="ENABLED",
    )
    return _execute_helper_write(
        service=service,
        method=method,
        request_obj=request_obj,
        ctx=ctx,
        customer_id_override=str(args.customer_id),
        in_path_label=f"helper:entities.enable:{args.resource_type}",
    )


def _execute_campaign_tree_status(
    *,
    args: argparse.Namespace,
    ctx: dict[str, Any],
    status: str,
) -> int:
    request_obj = build_campaign_tree_status_request(
        ctx=ctx,
        customer_id=str(args.customer_id),
        campaign_id=str(args.campaign_id) if args.campaign_id else None,
        campaign_name=str(args.campaign_name) if args.campaign_name else None,
        campaign_resource=str(args.campaign_resource) if args.campaign_resource else None,
        name_match=str(args.name_match),
        include_ad_groups=bool(args.include_ad_groups),
        include_ads=bool(args.include_ads),
        status=status,
    )
    return _execute_helper_write(
        service="GoogleAdsService",
        method="Mutate",
        request_obj=request_obj,
        ctx=ctx,
        customer_id_override=str(args.customer_id),
        in_path_label=f"helper:campaign-tree.{status.lower()}",
    )


def cmd_helpers_campaign_tree_pause(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    return _execute_campaign_tree_status(args=args, ctx=ctx, status="PAUSED")


def cmd_helpers_campaign_tree_enable(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    return _execute_campaign_tree_status(args=args, ctx=ctx, status="ENABLED")


def cmd_helpers_precheck_overlap(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    customer_id = _digits(str(args.customer_id), label="customer_id")
    campaign_ids = [_digits(value, label="campaign_id") for value in list(args.campaign_id or []) if str(value).strip()]
    campaign_filter = ""
    if campaign_ids:
        resource_names = [
            _campaign_resource_name(customer_id, campaign_id)
            for campaign_id in campaign_ids
        ]
        joined = ", ".join(f"'{_escape_gaql_string(value)}'" for value in resource_names)
        campaign_filter = f" AND campaign.resource_name IN ({joined})"
    query = (
        "SELECT campaign.id, campaign.name, campaign.resource_name, "
        "ad_group.id, ad_group.name, ad_group.resource_name, "
        "ad_group_criterion.resource_name, ad_group_criterion.status, "
        "ad_group_criterion.negative, ad_group_criterion.keyword.text, "
        "ad_group_criterion.keyword.match_type "
        "FROM keyword_view "
        "WHERE ad_group_criterion.status IN ('ENABLED', 'PAUSED') "
        "AND ad_group_criterion.negative = FALSE"
        f"{campaign_filter} "
        "LIMIT 10000"
    )
    rows = _gaql_rows(ctx=ctx, customer_id=customer_id, query=query, limit=max(1, int(args.limit or 1000)))
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        criterion = row.get("ad_group_criterion", {})
        keyword = criterion.get("keyword", {})
        text = str(keyword.get("text") or "").strip().lower()
        match_type = str(keyword.get("match_type") or "").strip().upper()
        if not text or not match_type:
            continue
        groups.setdefault((text, match_type), []).append(row)

    overlaps: list[dict[str, Any]] = []
    for (text, match_type), matched_rows in sorted(groups.items()):
        campaign_names = sorted(
            {
                str(row.get("campaign", {}).get("name") or "").strip()
                for row in matched_rows
                if str(row.get("campaign", {}).get("name") or "").strip()
            }
        )
        if len(campaign_names) < 2:
            continue
        overlaps.append(
            {
                "keyword_text": text,
                "match_type": match_type,
                "campaign_names": campaign_names,
                "row_count": len(matched_rows),
                "resource_names": sorted(
                    {
                        str(row.get("ad_group_criterion", {}).get("resource_name") or "").strip()
                        for row in matched_rows
                        if str(row.get("ad_group_criterion", {}).get("resource_name") or "").strip()
                    }
                ),
            }
        )
    ctx["out"].emit(
        {
            "ok": True,
            "meta": {
                "customer_id": customer_id,
                "checked_rows": len(rows),
                "overlap_count": len(overlaps),
            },
            "overlaps": overlaps,
        }
    )
    return 0


def cmd_helpers_precheck_policy_risk(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    items = _load_items(str(args.items))
    hits = _policy_risk_hits(items)
    ok = not hits
    strict = bool(args.strict)
    ctx["out"].emit(
        {
            "ok": ok if strict else True,
            "strict_failed": bool(strict and hits),
            "meta": {
                "checked_items": len(items),
                "risky_items": len(hits),
            },
            "hits": hits,
        }
    )
    return 0 if (ok or not strict) else 1


def cmd_helpers_offline_upload_click_conversions(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    request_obj = build_upload_click_conversions_request(
        customer_id=str(args.customer_id),
        items=_load_items(str(args.items)),
        validate_only=bool(args.validate_only),
        partial_failure=not bool(args.no_partial_failure),
        job_id=args.job_id,
    )
    return _execute_helper_write(
        service="ConversionUploadService",
        method="UploadClickConversions",
        request_obj=request_obj,
        ctx=ctx,
        customer_id_override=str(args.customer_id),
        in_path_label="helper:offline.upload-click-conversions",
    )
