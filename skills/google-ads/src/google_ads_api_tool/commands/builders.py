from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..errors import ValidationError
from ..json_files import read_json_file, write_json_file
from ..protobuf_json import parse_request_json
from ..rpc_commands import _cmd_write, _payload_digest
from ..rpc_v22_registry import RPC_METHODS_V22, RpcMethodSpec
from .helpers import _amount_to_micros, _digits, _normalize_match_type, _normalize_status


def register_builder_commands(sub) -> None:
    builders = sub.add_parser("builders", help="Strict campaign builders for repeated Google Ads setups")
    builders_sub = builders.add_subparsers(dest="builders_cmd", required=True, parser_class=type(builders))

    dsa = builders_sub.add_parser("dsa-feed-search", help="Build a page-feed-only DSA Search campaign from a strict spec")
    dsa_sub = dsa.add_subparsers(dest="builders_dsa_cmd", required=True, parser_class=type(dsa))
    dsa_from_spec = dsa_sub.add_parser("from-spec", help="Compile one DSA feed Search campaign from a JSON spec")
    dsa_from_spec.add_argument("--spec", required=True, help="Path to the builder JSON spec")
    dsa_from_spec.set_defaults(func=cmd_builder_dsa_feed_search_from_spec, write_capable=True)

    search = builders_sub.add_parser("search-campaign", help="Build a standard Search campaign from a strict spec")
    search_sub = search.add_subparsers(dest="builders_search_cmd", required=True, parser_class=type(search))
    search_from_spec = search_sub.add_parser("from-spec", help="Compile one Search campaign from a JSON spec")
    search_from_spec.add_argument("--spec", required=True, help="Path to the builder JSON spec")
    search_from_spec.set_defaults(func=cmd_builder_search_campaign_from_spec, write_capable=True)

    competitor = builders_sub.add_parser("competitor-search", help="Build a competitor Search campaign from a strict spec")
    competitor_sub = competitor.add_subparsers(
        dest="builders_competitor_cmd",
        required=True,
        parser_class=type(competitor),
    )
    competitor_from_spec = competitor_sub.add_parser("from-spec", help="Compile one competitor Search campaign from a JSON spec")
    competitor_from_spec.add_argument("--spec", required=True, help="Path to the builder JSON spec")
    competitor_from_spec.set_defaults(func=cmd_builder_competitor_search_from_spec, write_capable=True)


@dataclass
class _BuilderCompilation:
    customer_id: str
    request_obj: dict[str, Any]
    manifest: dict[str, Any]


class _CaptureOutput:
    def __init__(self) -> None:
        self.last: Any | None = None

    def emit(self, obj: Any) -> None:
        self.last = obj


class _TempIds:
    def __init__(self) -> None:
        self._next = -1

    def take(self) -> int:
        value = self._next
        self._next -= 1
        return value


def _rpc_spec(service: str, method: str) -> RpcMethodSpec:
    for spec in RPC_METHODS_V22:
        if spec.service == service and spec.method == method:
            return spec
    raise ValidationError(f"Unknown RPC spec: {service}.{method}")


def _ensure_dict(obj: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise ValidationError(f"{label} must be a JSON object.")
    return obj


def _ensure_list(obj: Any, *, label: str, allow_empty: bool = True) -> list[Any]:
    if not isinstance(obj, list):
        raise ValidationError(f"{label} must be a JSON list.")
    if not allow_empty and not obj:
        raise ValidationError(f"{label} must not be empty.")
    return obj


def _optional_list(obj: Any, *, label: str) -> list[Any]:
    if obj is None:
        return []
    return _ensure_list(obj, label=label)


def _resource_name(customer_id: str, collection: str, value: Any) -> str:
    s = str(value or "").strip()
    if s.startswith("customers/"):
        return s
    if not s:
        raise ValidationError(f"Missing resource id for {collection}.")
    if s.startswith("-"):
        digits = "-" + "".join(ch for ch in s[1:] if ch.isdigit())
        if digits == "-":
            raise ValidationError(f"Invalid temporary id for {collection}.")
        return f"customers/{customer_id}/{collection}/{digits}"
    digits = _digits(s, label=collection)
    return f"customers/{customer_id}/{collection}/{digits}"


def _geo_target_constant(value: Any) -> str:
    s = str(value or "").strip()
    if not s:
        raise ValidationError("Geo target constant value is required.")
    if s.startswith("geoTargetConstants/"):
        return s
    return f"geoTargetConstants/{_digits(s, label='geo target constant')}"


def _language_constant(value: Any) -> str:
    s = str(value or "").strip()
    if not s:
        raise ValidationError("Language constant value is required.")
    if s.startswith("languageConstants/"):
        return s
    return f"languageConstants/{_digits(s, label='language constant')}"


def _normalize_day_of_week(value: Any) -> str:
    day = str(value or "").strip().upper()
    allowed = {
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
    }
    if day not in allowed:
        raise ValidationError("day_of_week must be one of MONDAY through SUNDAY.")
    return day


def _normalize_minute(value: Any, *, label: str) -> str:
    minute = str(value or "ZERO").strip().upper()
    allowed = {"ZERO", "FIFTEEN", "THIRTY", "FORTY_FIVE"}
    if minute not in allowed:
        raise ValidationError(f"{label} must be ZERO, FIFTEEN, THIRTY, or FORTY_FIVE.")
    return minute


def _normalize_schedule(entries: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        item = _ensure_dict(entry, label="ad_schedule entry")
        start_hour = int(item.get("start_hour"))
        end_hour = int(item.get("end_hour"))
        if start_hour < 0 or start_hour > 23:
            raise ValidationError("start_hour must be between 0 and 23.")
        if end_hour < 0 or end_hour > 24:
            raise ValidationError("end_hour must be between 0 and 24.")
        normalized.append(
            {
                "day_of_week": _normalize_day_of_week(item.get("day_of_week")),
                "start_hour": start_hour,
                "start_minute": _normalize_minute(item.get("start_minute"), label="start_minute"),
                "end_hour": end_hour,
                "end_minute": _normalize_minute(item.get("end_minute"), label="end_minute"),
            }
        )
    return normalized


def _normalize_url_list(values: Any, *, label: str) -> list[str]:
    urls = _ensure_list(values, label=label, allow_empty=False)
    out: list[str] = []
    for raw in urls:
        url = str(raw or "").strip()
        if not url.startswith(("http://", "https://")):
            raise ValidationError(f"{label} entries must be full http or https URLs.")
        out.append(url)
    return out


def _normalize_headlines(values: Any) -> list[dict[str, Any]]:
    items = _ensure_list(values, label="responsive_search_ad.headlines", allow_empty=False)
    if len(items) < 3:
        raise ValidationError("Responsive Search Ads need at least 3 headlines.")
    if len(items) > 15:
        raise ValidationError("Responsive Search Ads cannot have more than 15 headlines.")
    out: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, str):
            text = item.strip()
            pinned_field = None
        else:
            obj = _ensure_dict(item, label="headline")
            text = str(obj.get("text") or "").strip()
            pinned_field = str(obj.get("pinned_field") or "").strip().upper() or None
        if not text:
            raise ValidationError("Each headline needs text.")
        row = {"text": text}
        if pinned_field:
            row["pinned_field"] = pinned_field
        out.append(row)
    return out


def _normalize_descriptions(values: Any) -> list[dict[str, Any]]:
    items = _ensure_list(values, label="responsive_search_ad.descriptions", allow_empty=False)
    if len(items) < 2:
        raise ValidationError("Responsive Search Ads need at least 2 descriptions.")
    if len(items) > 4:
        raise ValidationError("Responsive Search Ads cannot have more than 4 descriptions.")
    out: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, str):
            text = item.strip()
        else:
            obj = _ensure_dict(item, label="description")
            text = str(obj.get("text") or "").strip()
        if not text:
            raise ValidationError("Each description needs text.")
        out.append({"text": text})
    return out


def _normalize_negative_keyword(item: Any, *, default_match_type: str = "PHRASE") -> dict[str, Any]:
    if isinstance(item, str):
        text = item.strip()
        match_type = default_match_type
    else:
        obj = _ensure_dict(item, label="negative keyword")
        text = str(obj.get("text") or "").strip()
        match_type = str(obj.get("match_type") or default_match_type)
    if not text:
        raise ValidationError("Negative keyword text is required.")
    return {
        "text": text,
        "match_type": _normalize_match_type(match_type, label="negative keyword match_type"),
    }


def _normalize_positive_keyword(item: Any, *, default_match_type: str = "EXACT", default_status: str = "ENABLED") -> dict[str, Any]:
    if isinstance(item, str):
        text = item.strip()
        match_type = default_match_type
        status = default_status
    else:
        obj = _ensure_dict(item, label="keyword")
        text = str(obj.get("text") or "").strip()
        match_type = str(obj.get("match_type") or default_match_type)
        status = str(obj.get("status") or default_status)
    if not text:
        raise ValidationError("Keyword text is required.")
    return {
        "text": text,
        "match_type": _normalize_match_type(match_type, label="keyword match_type"),
        "status": _normalize_status(status, label="keyword status"),
    }


def _normalize_campaign_settings(
    spec: dict[str, Any],
    *,
    customer_id: str,
    temp_campaign_budget: str,
    dsa: bool,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    campaign = _ensure_dict(spec.get("campaign"), label="campaign")
    targeting = _ensure_dict(spec.get("targeting"), label="targeting")

    campaign_obj: dict[str, Any] = {
        "name": str(campaign.get("name") or "").strip(),
        "status": _normalize_status(campaign.get("status") or "PAUSED", label="campaign status"),
        "advertising_channel_type": "SEARCH",
        "campaign_budget": temp_campaign_budget,
        "contains_eu_political_advertising": str(
            campaign.get("contains_eu_political_advertising") or "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"
        ).strip(),
        "network_settings": {
            "target_google_search": bool(campaign.get("target_google_search", True)),
            "target_search_network": bool(campaign.get("target_search_network", False)),
            "target_partner_search_network": bool(campaign.get("target_partner_search_network", False)),
            "target_content_network": bool(campaign.get("target_content_network", False)),
        },
        "geo_target_type_setting": {
            "positive_geo_target_type": str(campaign.get("positive_geo_target_type") or "PRESENCE").strip(),
            "negative_geo_target_type": str(campaign.get("negative_geo_target_type") or "PRESENCE").strip(),
        },
    }
    if not campaign_obj["name"]:
        raise ValidationError("campaign.name is required.")

    cpc_ceiling_amount = campaign.get("max_clicks_cpc_ceiling_amount")
    cpc_ceiling_micros = campaign.get("max_clicks_cpc_ceiling_micros")
    if cpc_ceiling_amount is not None or cpc_ceiling_micros is not None:
        campaign_obj["target_spend"] = {
            "cpc_bid_ceiling_micros": _amount_to_micros(cpc_ceiling_amount)
            if cpc_ceiling_amount is not None
            else int(cpc_ceiling_micros)
        }

    if bool(campaign.get("asset_automation_text_opt_out", True)):
        campaign_obj["asset_automation_settings"] = [
            {
                "asset_automation_type": "TEXT_ASSET_AUTOMATION",
                "asset_automation_status": "OPTED_OUT",
            }
        ]

    locations = [_geo_target_constant(v) for v in _ensure_list(targeting.get("locations"), label="targeting.locations", allow_empty=False)]
    languages = [_language_constant(v) for v in _ensure_list(targeting.get("languages"), label="targeting.languages", allow_empty=False)]
    schedule = _normalize_schedule(_ensure_list(targeting.get("ad_schedule"), label="targeting.ad_schedule", allow_empty=False))
    campaign_negatives = [_normalize_negative_keyword(v, default_match_type="BROAD") for v in _optional_list(spec.get("campaign_negatives"), label="campaign_negatives")]
    cross_campaign_negatives = []
    for entry in _optional_list(spec.get("cross_campaign_negatives"), label="cross_campaign_negatives"):
        item = _ensure_dict(entry, label="cross_campaign_negative")
        text = _normalize_negative_keyword(item, default_match_type="EXACT")
        text["campaign"] = _resource_name(customer_id, "campaigns", item.get("campaign_id") or item.get("campaign"))
        cross_campaign_negatives.append(text)

    if dsa:
        dsa_spec = _ensure_dict(spec.get("page_feed"), label="page_feed")
        domain_name = str(dsa_spec.get("domain_name") or "").strip()
        if not domain_name:
            first_url = _normalize_url_list(dsa_spec.get("urls"), label="page_feed.urls")[0]
            domain_name = urlparse(first_url).netloc
        campaign_obj["dynamic_search_ads_setting"] = {
            "domain_name": domain_name,
            "language_code": str(dsa_spec.get("language_code") or campaign.get("dynamic_search_language_code") or "en").strip(),
            "use_supplied_urls_only": True,
        }

    return campaign, campaign_obj, [{"geo_target_constant": v} for v in locations], [{"language_constant": v} for v in languages], schedule, campaign_negatives, cross_campaign_negatives


def _asset_field_type(asset_type: str) -> str:
    mapping = {
        "CALL": "CALL",
        "CALLOUT": "CALLOUT",
        "SITELINK": "SITELINK",
        "STRUCTURED_SNIPPET": "STRUCTURED_SNIPPET",
    }
    field_type = mapping.get(str(asset_type or "").strip().upper())
    if not field_type:
        raise ValidationError("Asset type must be CALL, CALLOUT, SITELINK, or STRUCTURED_SNIPPET.")
    return field_type


def _compile_asset_create(asset_def: Any, *, customer_id: str, temp_ids: _TempIds) -> tuple[str, str, dict[str, Any]]:
    item = _ensure_dict(asset_def, label="asset create entry")
    asset_type = _asset_field_type(item.get("type"))
    alias = str(item.get("alias") or "").strip()
    if not alias:
        raise ValidationError("Each asset create entry needs an alias.")
    asset_rn = _resource_name(customer_id, "assets", temp_ids.take())
    create: dict[str, Any] = {
        "resource_name": asset_rn,
        "name": str(item.get("name") or "").strip(),
    }
    if not create["name"]:
        raise ValidationError("Each created asset needs a name.")
    if asset_type == "CALL":
        call_asset: dict[str, Any] = {
            "country_code": str(item.get("country_code") or "").strip() or "US",
            "phone_number": str(item.get("phone_number") or "").strip(),
        }
        if not call_asset["phone_number"]:
            raise ValidationError("CALL assets need phone_number.")
        if item.get("call_conversion_reporting_state") is not None:
            call_asset["call_conversion_reporting_state"] = str(item.get("call_conversion_reporting_state")).strip()
        if item.get("call_conversion_action") is not None:
            call_asset["call_conversion_action"] = str(item.get("call_conversion_action")).strip()
        schedule_targets = _optional_list(item.get("ad_schedule_targets"), label="asset ad_schedule_targets")
        if schedule_targets:
            call_asset["ad_schedule_targets"] = _normalize_schedule(schedule_targets)
        create["call_asset"] = call_asset
    elif asset_type == "CALLOUT":
        text = str(item.get("callout_text") or "").strip()
        if not text:
            raise ValidationError("CALLOUT assets need callout_text.")
        create["callout_asset"] = {"callout_text": text}
    elif asset_type == "SITELINK":
        link_text = str(item.get("link_text") or "").strip()
        if not link_text:
            raise ValidationError("SITELINK assets need link_text.")
        create["final_urls"] = _normalize_url_list(item.get("final_urls"), label="sitelink final_urls")
        sitelink = {"link_text": link_text}
        if item.get("description1") is not None:
            sitelink["description1"] = str(item.get("description1")).strip()
        if item.get("description2") is not None:
            sitelink["description2"] = str(item.get("description2")).strip()
        create["sitelink_asset"] = sitelink
    elif asset_type == "STRUCTURED_SNIPPET":
        header = str(item.get("header") or "").strip()
        values = [str(v).strip() for v in _ensure_list(item.get("values"), label="structured snippet values", allow_empty=False)]
        if not header:
            raise ValidationError("STRUCTURED_SNIPPET assets need header.")
        create["structured_snippet_asset"] = {"header": header, "values": values}
    return alias, asset_rn, {"asset_operation": {"create": create}}


def _compile_campaign_asset_links(
    asset_links: list[Any],
    *,
    customer_id: str,
    campaign_rn: str,
    created_assets: dict[str, tuple[str, str]],
) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    for raw in asset_links:
        item = _ensure_dict(raw, label="campaign asset link")
        asset_alias = str(item.get("asset_alias") or "").strip()
        asset_rn = str(item.get("asset") or "").strip()
        field_type = str(item.get("field_type") or "").strip().upper()
        if asset_alias:
            if asset_alias not in created_assets:
                raise ValidationError(f"Unknown asset_alias in campaign asset link: {asset_alias}")
            created_rn, derived_field_type = created_assets[asset_alias]
            asset_rn = created_rn
            if not field_type:
                field_type = derived_field_type
        if not asset_rn:
            raise ValidationError("Campaign asset link needs asset or asset_alias.")
        if not field_type:
            raise ValidationError("Campaign asset link needs field_type when linking an existing asset.")
        operations.append(
            {
                "campaign_asset_operation": {
                    "create": {
                        "campaign": campaign_rn,
                        "asset": asset_rn,
                        "field_type": field_type,
                        "status": _normalize_status(item.get("status") or "ENABLED", label="campaign asset link status"),
                    }
                }
            }
        )
    return operations


def build_search_campaign_request(spec_obj: dict[str, Any]) -> _BuilderCompilation:
    spec = _ensure_dict(spec_obj, label="spec")
    customer_id = _digits(spec.get("customer_id"), label="customer_id")
    temp_ids = _TempIds()

    budget_spec = _ensure_dict(spec.get("budget"), label="budget")
    budget_rn = _resource_name(customer_id, "campaignBudgets", temp_ids.take())
    campaign_rn = _resource_name(customer_id, "campaigns", temp_ids.take())
    campaign_settings, campaign_obj, locations, languages, schedule, campaign_negatives, cross_campaign_negatives = _normalize_campaign_settings(
        spec,
        customer_id=customer_id,
        temp_campaign_budget=budget_rn,
        dsa=False,
    )
    campaign_obj["resource_name"] = campaign_rn

    operations: list[dict[str, Any]] = [
        {
            "campaign_budget_operation": {
                "create": {
                    "resource_name": budget_rn,
                    "name": str(budget_spec.get("name") or "").strip(),
                    "amount_micros": _amount_to_micros(budget_spec.get("amount")),
                    "delivery_method": str(budget_spec.get("delivery_method") or "STANDARD").strip(),
                    "explicitly_shared": bool(budget_spec.get("explicitly_shared", True)),
                }
            }
        },
        {
            "campaign_operation": {
                "create": campaign_obj,
            }
        },
    ]
    if not operations[0]["campaign_budget_operation"]["create"]["name"]:
        raise ValidationError("budget.name is required.")

    for location in locations:
        operations.append({"campaign_criterion_operation": {"create": {"campaign": campaign_rn, "location": location}}})
    for language in languages:
        operations.append({"campaign_criterion_operation": {"create": {"campaign": campaign_rn, "language": language}}})
    for entry in schedule:
        operations.append({"campaign_criterion_operation": {"create": {"campaign": campaign_rn, "ad_schedule": entry}}})
    for negative in campaign_negatives:
        operations.append(
            {
                "campaign_criterion_operation": {
                    "create": {
                        "campaign": campaign_rn,
                        "negative": True,
                        "keyword": {
                            "text": negative["text"],
                            "match_type": negative["match_type"],
                        },
                    }
                }
            }
        )

    created_assets: dict[str, tuple[str, str]] = {}
    for asset_def in _optional_list(spec.get("asset_creates"), label="asset_creates"):
        alias, asset_rn, op = _compile_asset_create(asset_def, customer_id=customer_id, temp_ids=temp_ids)
        created_assets[alias] = (asset_rn, _asset_field_type(_ensure_dict(asset_def, label="asset create entry").get("type")))
        operations.append(op)

    ad_groups = _ensure_list(spec.get("ad_groups"), label="ad_groups", allow_empty=False)
    ad_group_resource_names: dict[str, str] = {}
    for index, raw_ad_group in enumerate(ad_groups, start=1):
        item = _ensure_dict(raw_ad_group, label="ad_group")
        alias = str(item.get("alias") or "").strip() or f"ad_group_{index}"
        if alias in ad_group_resource_names:
            raise ValidationError(f"Duplicate ad_group alias: {alias}")
        ad_group_rn = _resource_name(customer_id, "adGroups", temp_ids.take())
        ad_group_resource_names[alias] = ad_group_rn
        operations.append(
            {
                "ad_group_operation": {
                    "create": {
                        "resource_name": ad_group_rn,
                        "name": str(item.get("name") or "").strip(),
                        "campaign": campaign_rn,
                        "status": _normalize_status(item.get("status") or "PAUSED", label="ad group status"),
                        "type": str(item.get("type") or "SEARCH_STANDARD").strip(),
                    }
                }
            }
        )
        if not str(item.get("name") or "").strip():
            raise ValidationError("Each ad group needs a name.")
        if item.get("cpc_bid_micros") is not None:
            operations[-1]["ad_group_operation"]["create"]["cpc_bid_micros"] = int(item.get("cpc_bid_micros"))

        for keyword in _optional_list(item.get("keywords"), label=f"ad_group.keywords[{alias}]"):
            normalized = _normalize_positive_keyword(keyword)
            operations.append(
                {
                    "ad_group_criterion_operation": {
                        "create": {
                            "ad_group": ad_group_rn,
                            "status": normalized["status"],
                            "keyword": {
                                "text": normalized["text"],
                                "match_type": normalized["match_type"],
                            },
                        }
                    }
                }
            )
        for negative in _optional_list(item.get("negative_keywords"), label=f"ad_group.negative_keywords[{alias}]"):
            normalized = _normalize_negative_keyword(negative)
            operations.append(
                {
                    "ad_group_criterion_operation": {
                        "create": {
                            "ad_group": ad_group_rn,
                            "negative": True,
                            "keyword": {
                                "text": normalized["text"],
                                "match_type": normalized["match_type"],
                            },
                        }
                    }
                }
            )
        for ad in _optional_list(item.get("ads"), label=f"ad_group.ads[{alias}]"):
            ad_obj = _ensure_dict(ad, label="ad")
            final_urls = _normalize_url_list(ad_obj.get("final_urls"), label="ad final_urls")
            operations.append(
                {
                    "ad_group_ad_operation": {
                        "create": {
                            "ad_group": ad_group_rn,
                            "status": _normalize_status(ad_obj.get("status") or "PAUSED", label="ad status"),
                            "ad": {
                                "final_urls": final_urls,
                                "responsive_search_ad": {
                                    "headlines": _normalize_headlines(ad_obj.get("headlines")),
                                    "descriptions": _normalize_descriptions(ad_obj.get("descriptions")),
                                },
                            },
                        }
                    }
                }
            )

    operations.extend(
        _compile_campaign_asset_links(
            _optional_list(spec.get("campaign_asset_links"), label="campaign_asset_links"),
            customer_id=customer_id,
            campaign_rn=campaign_rn,
            created_assets=created_assets,
        )
    )

    for negative in cross_campaign_negatives:
        operations.append(
            {
                "campaign_criterion_operation": {
                    "create": {
                        "campaign": negative["campaign"],
                        "negative": True,
                        "keyword": {
                            "text": negative["text"],
                            "match_type": negative["match_type"],
                        },
                    }
                }
            }
        )

    request_obj = {
        "customer_id": customer_id,
        "partial_failure": bool(spec.get("partial_failure", True)),
        "mutate_operations": operations,
    }
    manifest = {
        "builder_kind": "search-campaign",
        "campaign_name": campaign_settings["name"],
        "budget_name": str(budget_spec.get("name") or "").strip(),
        "ad_group_count": len(ad_groups),
        "operation_count": len(operations),
        "created_asset_count": len(created_assets),
        "campaign_asset_link_count": len(_optional_list(spec.get("campaign_asset_links"), label="campaign_asset_links")),
        "cross_campaign_negative_count": len(cross_campaign_negatives),
        "operation_action_counts": _operation_action_counts(request_obj),
    }
    return _BuilderCompilation(customer_id=customer_id, request_obj=request_obj, manifest=manifest)


def build_competitor_search_request(spec_obj: dict[str, Any]) -> _BuilderCompilation:
    compilation = build_search_campaign_request(spec_obj)
    spec = _ensure_dict(spec_obj, label="spec")
    for ad_group in _ensure_list(spec.get("ad_groups"), label="ad_groups", allow_empty=False):
        for keyword in _optional_list(_ensure_dict(ad_group, label="ad_group").get("keywords"), label="competitor positive keywords"):
            normalized = _normalize_positive_keyword(keyword)
            if normalized["match_type"] != "EXACT":
                raise ValidationError("Competitor search builder allows only EXACT positive keywords.")
    compilation.manifest["builder_kind"] = "competitor-search"
    return compilation


def build_dsa_feed_search_request(spec_obj: dict[str, Any]) -> _BuilderCompilation:
    spec = _ensure_dict(spec_obj, label="spec")
    customer_id = _digits(spec.get("customer_id"), label="customer_id")
    temp_ids = _TempIds()

    budget_spec = _ensure_dict(spec.get("budget"), label="budget")
    page_feed = _ensure_dict(spec.get("page_feed"), label="page_feed")
    ad_group = _ensure_dict(spec.get("ad_group"), label="ad_group")
    ad = _ensure_dict(spec.get("ad"), label="ad")
    webpage_target = _ensure_dict(spec.get("webpage_target"), label="webpage_target")

    urls = _normalize_url_list(page_feed.get("urls"), label="page_feed.urls")
    label = str(page_feed.get("label") or "").strip()
    if not label:
        raise ValidationError("page_feed.label is required.")

    budget_rn = _resource_name(customer_id, "campaignBudgets", temp_ids.take())
    campaign_rn = _resource_name(customer_id, "campaigns", temp_ids.take())
    asset_set_rn = _resource_name(customer_id, "assetSets", temp_ids.take())
    ad_group_rn = _resource_name(customer_id, "adGroups", temp_ids.take())
    _, campaign_obj, locations, languages, schedule, campaign_negatives, cross_campaign_negatives = _normalize_campaign_settings(
        spec,
        customer_id=customer_id,
        temp_campaign_budget=budget_rn,
        dsa=True,
    )
    campaign_obj["resource_name"] = campaign_rn

    operations: list[dict[str, Any]] = [
        {
            "campaign_budget_operation": {
                "create": {
                    "resource_name": budget_rn,
                    "name": str(budget_spec.get("name") or "").strip(),
                    "amount_micros": _amount_to_micros(budget_spec.get("amount")),
                    "delivery_method": str(budget_spec.get("delivery_method") or "STANDARD").strip(),
                    "explicitly_shared": bool(budget_spec.get("explicitly_shared", True)),
                }
            }
        },
        {"campaign_operation": {"create": campaign_obj}},
    ]
    if not operations[0]["campaign_budget_operation"]["create"]["name"]:
        raise ValidationError("budget.name is required.")

    for location in locations:
        operations.append({"campaign_criterion_operation": {"create": {"campaign": campaign_rn, "location": location}}})
    for language in languages:
        operations.append({"campaign_criterion_operation": {"create": {"campaign": campaign_rn, "language": language}}})
    for entry in schedule:
        operations.append({"campaign_criterion_operation": {"create": {"campaign": campaign_rn, "ad_schedule": entry}}})
    for negative in campaign_negatives:
        operations.append(
            {
                "campaign_criterion_operation": {
                    "create": {
                        "campaign": campaign_rn,
                        "negative": True,
                        "keyword": {
                            "text": negative["text"],
                            "match_type": negative["match_type"],
                        },
                    }
                }
            }
        )

    page_asset_names: list[str] = []
    for url in urls:
        asset_rn = _resource_name(customer_id, "assets", temp_ids.take())
        page_asset_names.append(asset_rn)
        operations.append(
            {
                "asset_operation": {
                    "create": {
                        "resource_name": asset_rn,
                        "page_feed_asset": {
                            "page_url": url,
                            "labels": [label],
                        },
                    }
                }
            }
        )
    operations.append(
        {
            "asset_set_operation": {
                "create": {
                    "resource_name": asset_set_rn,
                    "name": str(page_feed.get("asset_set_name") or "").strip(),
                    "type": "PAGE_FEED",
                }
            }
        }
    )
    if not str(page_feed.get("asset_set_name") or "").strip():
        raise ValidationError("page_feed.asset_set_name is required.")
    for asset_rn in page_asset_names:
        operations.append(
            {
                "asset_set_asset_operation": {
                    "create": {
                        "asset": asset_rn,
                        "asset_set": asset_set_rn,
                    }
                }
            }
        )
    operations.append(
        {
            "campaign_asset_set_operation": {
                "create": {
                    "campaign": campaign_rn,
                    "asset_set": asset_set_rn,
                }
            }
        }
    )
    operations.append(
        {
            "ad_group_operation": {
                "create": {
                    "resource_name": ad_group_rn,
                    "name": str(ad_group.get("name") or "").strip(),
                    "campaign": campaign_rn,
                    "status": _normalize_status(ad_group.get("status") or "PAUSED", label="ad group status"),
                    "type": "SEARCH_DYNAMIC_ADS",
                }
            }
        }
    )
    if not str(ad_group.get("name") or "").strip():
        raise ValidationError("ad_group.name is required.")
    operations.append(
        {
            "ad_group_ad_operation": {
                "create": {
                    "ad_group": ad_group_rn,
                    "status": _normalize_status(ad.get("status") or "PAUSED", label="ad status"),
                    "ad": {
                        "expanded_dynamic_search_ad": {
                            "description": str(ad.get("description") or "").strip(),
                            "description2": str(ad.get("description2") or "").strip(),
                        }
                    },
                }
            }
        }
    )
    if not str(ad.get("description") or "").strip():
        raise ValidationError("ad.description is required.")
    if not str(ad.get("description2") or "").strip():
        raise ValidationError("ad.description2 is required.")
    operations.append(
        {
            "ad_group_criterion_operation": {
                "create": {
                    "ad_group": ad_group_rn,
                    "negative": False,
                    "webpage": {
                        "criterion_name": str(webpage_target.get("criterion_name") or "").strip(),
                        "conditions": [
                            {
                                "operand": "CUSTOM_LABEL",
                                "operator": "EQUALS",
                                "argument": str(webpage_target.get("label") or label).strip(),
                            }
                        ],
                    },
                }
            }
        }
    )
    if not str(webpage_target.get("criterion_name") or "").strip():
        raise ValidationError("webpage_target.criterion_name is required.")
    for negative in cross_campaign_negatives:
        operations.append(
            {
                "campaign_criterion_operation": {
                    "create": {
                        "campaign": negative["campaign"],
                        "negative": True,
                        "keyword": {
                            "text": negative["text"],
                            "match_type": negative["match_type"],
                        },
                    }
                }
            }
        )

    request_obj = {
        "customer_id": customer_id,
        "partial_failure": bool(spec.get("partial_failure", True)),
        "mutate_operations": operations,
    }
    manifest = {
        "builder_kind": "dsa-feed-search",
        "campaign_name": campaign_obj["name"],
        "budget_name": str(budget_spec.get("name") or "").strip(),
        "page_url_count": len(urls),
        "operation_count": len(operations),
        "cross_campaign_negative_count": len(cross_campaign_negatives),
        "operation_action_counts": _operation_action_counts(request_obj),
    }
    return _BuilderCompilation(customer_id=customer_id, request_obj=request_obj, manifest=manifest)


def _operation_action_counts(request_obj: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for operation in _ensure_list(request_obj.get("mutate_operations"), label="mutate_operations", allow_empty=False):
        for key in _ensure_dict(operation, label="mutate operation").keys():
            counts[key] = counts.get(key, 0) + 1
    return {key: counts[key] for key in sorted(counts.keys())}


def _artifact_path(ctx: dict[str, Any], filename: str) -> Path | None:
    artifacts_dir = ctx.get("artifacts_dir")
    if not artifacts_dir:
        return None
    path = Path(artifacts_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path / filename


def _write_builder_readme(
    *,
    ctx: dict[str, Any],
    builder_kind: str,
    spec_path: str,
    manifest: dict[str, Any],
    result: dict[str, Any] | None,
) -> None:
    readme_path = _artifact_path(ctx, "README.md")
    if not readme_path:
        return
    lines = [
        f"# Builder README — {builder_kind}",
        "",
        f"- Spec path: `{spec_path}`",
        f"- Dry run: `{bool(result.get('dry_run')) if isinstance(result, dict) else not bool(ctx.get('apply'))}`",
        f"- Operation count: `{manifest.get('operation_count')}`",
        "",
        "## Key files",
        "- `spec.json` — saved input spec",
        "- `request.json` — compiled `MutateGoogleAdsRequest` JSON",
        "- `builder_manifest.json` — builder summary and operation counts",
        "- `plan.json` — standard Google Ads write plan",
        "- `receipt.json` — standard Google Ads write receipt after apply",
        "- `after.json` — short post-apply summary from the receipt",
        "",
    ]
    if isinstance(result, dict):
        if bool(result.get("dry_run")) and isinstance(result.get("plan"), dict):
            lines.append(f"- Plan fingerprint: `{result['plan'].get('plan_fingerprint')}`")
        if not bool(result.get("dry_run")) and isinstance(result.get("receipt"), dict):
            lines.append(f"- Verified resources: `{result['receipt'].get('verification', {}).get('verified_resources')}`")
    readme_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _emit_builder_files(
    *,
    ctx: dict[str, Any],
    spec_obj: dict[str, Any],
    request_obj: dict[str, Any],
    manifest: dict[str, Any],
    result: dict[str, Any] | None,
) -> None:
    for filename, obj in (
        ("spec.json", spec_obj),
        ("request.json", request_obj),
        ("builder_manifest.json", manifest),
    ):
        path = _artifact_path(ctx, filename)
        if path:
            write_json_file(path, obj)
    if isinstance(result, dict) and isinstance(result.get("receipt"), dict):
        after_path = _artifact_path(ctx, "after.json")
        if after_path:
            write_json_file(
                after_path,
                {
                    "verification": result["receipt"].get("verification"),
                    "response_summary": result["receipt"].get("response_summary"),
                },
            )


def _execute_builder(
    *,
    builder_kind: str,
    spec_path: str,
    spec_obj: dict[str, Any],
    compilation: _BuilderCompilation,
    ctx: dict[str, Any],
) -> int:
    request_obj = compilation.request_obj
    manifest = dict(compilation.manifest)
    manifest["spec_digest"] = _payload_digest(spec_obj)
    manifest["request_digest"] = _payload_digest(request_obj)

    silent_ctx = dict(ctx)
    silent_out = _CaptureOutput()
    silent_ctx["out"] = silent_out

    spec = _rpc_spec("GoogleAdsService", "Mutate")
    request_msg = parse_request_json(
        service="GoogleAdsService",
        request_type=spec.request_type,
        obj=request_obj,
        customer_id_override=compilation.customer_id,
    )
    _emit_builder_files(
        ctx=ctx,
        spec_obj=spec_obj,
        request_obj=request_obj,
        manifest=manifest,
        result=None,
    )
    rc = _cmd_write(
        spec=spec,
        request_msg=request_msg,
        in_path=f"builder:{builder_kind}:{spec_path}",
        ctx=silent_ctx,
        customer_id_override=compilation.customer_id,
    )
    result = silent_out.last if isinstance(silent_out.last, dict) else {"ok": rc == 0}
    _emit_builder_files(
        ctx=ctx,
        spec_obj=spec_obj,
        request_obj=request_obj,
        manifest=manifest,
        result=result if isinstance(result, dict) else None,
    )
    _write_builder_readme(
        ctx=ctx,
        builder_kind=builder_kind,
        spec_path=spec_path,
        manifest=manifest,
        result=result if isinstance(result, dict) else None,
    )

    out = ctx["out"]
    payload: dict[str, Any] = {
        "ok": bool(result.get("ok")) if isinstance(result, dict) else rc == 0,
        "dry_run": bool(result.get("dry_run")) if isinstance(result, dict) else not bool(ctx.get("apply")),
        "builder": {
            "kind": builder_kind,
            "spec_path": str(spec_path),
            "manifest": manifest,
            "artifacts_dir": str(ctx.get("artifacts_dir")) if ctx.get("artifacts_dir") else None,
        },
    }
    if isinstance(result, dict):
        if "plan" in result:
            payload["plan"] = result["plan"]
        if "receipt" in result:
            payload["receipt"] = result["receipt"]
        if "refused" in result:
            payload["refused"] = result["refused"]
        if "reasons" in result:
            payload["reasons"] = result["reasons"]
    out.emit(payload)
    return rc


def _load_spec(path_value: str) -> tuple[str, dict[str, Any]]:
    path = str(path_value or "").strip()
    if not path:
        raise ValidationError("Missing --spec PATH.")
    obj = read_json_file(Path(path))
    return path, _ensure_dict(obj, label="spec")


def cmd_builder_search_campaign_from_spec(args, ctx: dict[str, Any]) -> int:
    spec_path, spec_obj = _load_spec(str(args.spec))
    compilation = build_search_campaign_request(spec_obj)
    return _execute_builder(
        builder_kind="search-campaign",
        spec_path=spec_path,
        spec_obj=spec_obj,
        compilation=compilation,
        ctx=ctx,
    )


def cmd_builder_competitor_search_from_spec(args, ctx: dict[str, Any]) -> int:
    spec_path, spec_obj = _load_spec(str(args.spec))
    compilation = build_competitor_search_request(spec_obj)
    return _execute_builder(
        builder_kind="competitor-search",
        spec_path=spec_path,
        spec_obj=spec_obj,
        compilation=compilation,
        ctx=ctx,
    )


def cmd_builder_dsa_feed_search_from_spec(args, ctx: dict[str, Any]) -> int:
    spec_path, spec_obj = _load_spec(str(args.spec))
    compilation = build_dsa_feed_search_request(spec_obj)
    return _execute_builder(
        builder_kind="dsa-feed-search",
        spec_path=spec_path,
        spec_obj=spec_obj,
        compilation=compilation,
        ctx=ctx,
    )
