from __future__ import annotations

import unittest

from google_ads_api_tool.cli import build_parser
from google_ads_api_tool.commands.helpers import (
    build_campaign_negatives_add_request,
    build_campaign_set_budget_request,
    build_campaign_set_max_clicks_cpc_ceiling_request,
    build_entity_status_request,
    build_keywords_add_request,
    build_keywords_pause_request,
    build_upload_click_conversions_request,
)
from google_ads_api_tool.protobuf_json import parse_request_json


class TestHelperCommandBuilders(unittest.TestCase):
    def test_helper_commands_are_registered_in_cli(self) -> None:
        args = build_parser().parse_args(
            [
                "helpers",
                "campaign",
                "set-budget",
                "--customer-id",
                "1234567890",
                "--budget-id",
                "999",
                "--amount",
                "70",
            ]
        )
        self.assertTrue(args.write_capable)
        self.assertEqual(args.func.__name__, "cmd_helpers_campaign_set_budget")
        lookup_args = build_parser().parse_args(
            [
                "helpers",
                "entities",
                "lookup-by-name",
                "--customer-id",
                "1234567890",
                "--resource-type",
                "campaign",
                "--name",
                "Main Search",
            ]
        )
        self.assertFalse(lookup_args.write_capable)
        self.assertEqual(lookup_args.func.__name__, "cmd_helpers_entities_lookup_by_name")

    def test_build_keywords_pause_request_accepts_multiple_item_shapes(self) -> None:
        request = build_keywords_pause_request(
            customer_id="1234567890",
            items=[
                "customers/1234567890/adGroupCriteria/111~222",
                {"ad_group_id": "333", "criterion_id": "444"},
            ],
        )
        self.assertEqual(
            request,
            {
                "customer_id": "1234567890",
                "operations": [
                    {
                        "update": {
                            "resource_name": "customers/1234567890/adGroupCriteria/111~222",
                            "status": "PAUSED",
                        },
                        "update_mask": "status",
                    },
                    {
                        "update": {
                            "resource_name": "customers/1234567890/adGroupCriteria/333~444",
                            "status": "PAUSED",
                        },
                        "update_mask": "status",
                    },
                ],
            },
        )

    def test_build_keywords_add_request_uses_defaults_and_item_overrides(self) -> None:
        request = build_keywords_add_request(
            customer_id="1234567890",
            items=[
                "sliding door repair dallas",
                {"text": "patio door rollers", "match_type": "PHRASE", "status": "PAUSED"},
            ],
            default_ad_group_id="789",
            default_match_type="EXACT",
            default_status="ENABLED",
        )
        self.assertEqual(request["customer_id"], "1234567890")
        self.assertEqual(request["operations"][0]["create"]["ad_group"], "customers/1234567890/adGroups/789")
        self.assertEqual(request["operations"][0]["create"]["keyword"]["match_type"], "EXACT")
        self.assertEqual(request["operations"][1]["create"]["keyword"]["match_type"], "PHRASE")
        self.assertEqual(request["operations"][1]["create"]["status"], "PAUSED")

    def test_build_campaign_negatives_add_request_marks_negative_true(self) -> None:
        request = build_campaign_negatives_add_request(
            customer_id="1234567890",
            items=["glass repair"],
            default_campaign_id="555",
            default_match_type="PHRASE",
        )
        criterion = request["operations"][0]["create"]
        self.assertTrue(criterion["negative"])
        self.assertEqual(criterion["campaign"], "customers/1234567890/campaigns/555")
        self.assertEqual(criterion["keyword"]["text"], "glass repair")

    def test_build_campaign_set_budget_request_converts_amount_to_micros(self) -> None:
        request = build_campaign_set_budget_request(
            customer_id="1234567890",
            budget_id="999",
            resource_name=None,
            amount="70.50",
            amount_micros=None,
        )
        op = request["operations"][0]
        self.assertEqual(op["update"]["resource_name"], "customers/1234567890/campaignBudgets/999")
        self.assertEqual(op["update"]["amount_micros"], 70500000)
        self.assertEqual(op["update_mask"], "amountMicros")

    def test_build_campaign_set_max_clicks_cpc_ceiling_request_uses_target_spend(self) -> None:
        request = build_campaign_set_max_clicks_cpc_ceiling_request(
            customer_id="1234567890",
            campaign_id="111",
            resource_name=None,
            amount="12",
            amount_micros=None,
        )
        op = request["operations"][0]
        self.assertEqual(op["update"]["resource_name"], "customers/1234567890/campaigns/111")
        self.assertEqual(op["update"]["target_spend"]["cpc_bid_ceiling_micros"], 12000000)
        self.assertEqual(op["update_mask"], "targetSpend.cpcBidCeilingMicros")

    def test_build_entity_status_request_for_ad_group_ad(self) -> None:
        service, method, request = build_entity_status_request(
            customer_id="1234567890",
            resource_type="ad-group-ad",
            items=[{"ad_group_id": "222", "ad_id": "333"}],
            status="ENABLED",
        )
        self.assertEqual((service, method), ("AdGroupAdService", "MutateAdGroupAds"))
        self.assertEqual(
            request["operations"][0]["update"]["resource_name"],
            "customers/1234567890/adGroupAds/222~333",
        )
        self.assertEqual(request["operations"][0]["update"]["status"], "ENABLED")

    def test_build_upload_click_conversions_request_wraps_items(self) -> None:
        request = build_upload_click_conversions_request(
            customer_id="1234567890",
            items=[
                {
                    "gclid": "abc123",
                    "conversion_action": "customers/1234567890/conversionActions/777",
                    "conversion_date_time": "2026-05-22 10:00:00-05:00",
                    "conversion_value": 1.0,
                    "currency_code": "USD",
                    "order_id": "row-1",
                }
            ],
            validate_only=False,
            partial_failure=True,
            job_id=44,
        )
        self.assertTrue(request["partial_failure"])
        self.assertFalse(request["validate_only"])
        self.assertEqual(request["job_id"], 44)
        self.assertEqual(request["conversions"][0]["gclid"], "abc123")

    def test_helper_requests_parse_into_real_messages(self) -> None:
        parse_request_json(
            service="AdGroupCriterionService",
            request_type="MutateAdGroupCriteriaRequest",
            obj=build_keywords_pause_request(
                customer_id="1234567890",
                items=["customers/1234567890/adGroupCriteria/111~222"],
            ),
        )
        parse_request_json(
            service="CampaignBudgetService",
            request_type="MutateCampaignBudgetsRequest",
            obj=build_campaign_set_budget_request(
                customer_id="1234567890",
                budget_id="999",
                resource_name=None,
                amount=None,
                amount_micros=70000000,
            ),
        )
        parse_request_json(
            service="CampaignService",
            request_type="MutateCampaignsRequest",
            obj=build_campaign_set_max_clicks_cpc_ceiling_request(
                customer_id="1234567890",
                campaign_id="111",
                resource_name=None,
                amount=None,
                amount_micros=12000000,
            ),
        )
