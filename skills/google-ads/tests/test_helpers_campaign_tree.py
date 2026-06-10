from __future__ import annotations

import argparse
import unittest
from unittest import mock

from google_ads_api_tool.commands.helpers import (
    build_campaign_tree_status_request,
    cmd_helpers_precheck_overlap,
    cmd_helpers_precheck_policy_risk,
)
from google_ads_api_tool.protobuf_json import parse_request_json


class _Out:
    def __init__(self) -> None:
        self.last = None

    def emit(self, obj):  # noqa: ANN001
        self.last = obj


class TestHelperCampaignTree(unittest.TestCase):
    @mock.patch("google_ads_api_tool.commands.helpers._gaql_rows")
    def test_build_campaign_tree_status_request_compiles_mutate_request(self, mock_rows: mock.Mock) -> None:
        mock_rows.side_effect = [
            [
                {"campaign": {"resource_name": "customers/123/campaigns/99"}},
            ],
            [
                {"ad_group": {"resource_name": "customers/123/adGroups/11"}},
                {"ad_group": {"resource_name": "customers/123/adGroups/12"}},
            ],
            [
                {"ad_group_ad": {"resource_name": "customers/123/adGroupAds/11~201"}},
            ],
            [
                {"ad_group_ad": {"resource_name": "customers/123/adGroupAds/12~202"}},
            ],
        ]
        request_obj = build_campaign_tree_status_request(
            ctx={"cfg": object()},
            customer_id="123",
            campaign_id=None,
            campaign_name="Main Search",
            campaign_resource=None,
            name_match="exact",
            include_ad_groups=True,
            include_ads=True,
            status="PAUSED",
        )
        parse_request_json(
            service="GoogleAdsService",
            request_type="MutateGoogleAdsRequest",
            obj=request_obj,
        )
        self.assertEqual(len(request_obj["mutate_operations"]), 5)

    @mock.patch("google_ads_api_tool.commands.helpers._gaql_rows")
    def test_overlap_precheck_reports_cross_campaign_duplicates(self, mock_rows: mock.Mock) -> None:
        mock_rows.return_value = [
            {
                "campaign": {"name": "Main"},
                "ad_group_criterion": {
                    "resource_name": "customers/123/adGroupCriteria/11~1",
                    "keyword": {"text": "sliding door repair", "match_type": "EXACT"},
                },
            },
            {
                "campaign": {"name": "Discovery"},
                "ad_group_criterion": {
                    "resource_name": "customers/123/adGroupCriteria/12~2",
                    "keyword": {"text": "sliding door repair", "match_type": "EXACT"},
                },
            },
        ]
        out = _Out()
        rc = cmd_helpers_precheck_overlap(
            argparse.Namespace(customer_id="123", campaign_id=[], limit=1000),
            {"cfg": object(), "out": out},
        )
        self.assertEqual(rc, 0)
        self.assertEqual(out.last["meta"]["overlap_count"], 1)

    @mock.patch("google_ads_api_tool.commands.helpers._load_items")
    def test_policy_risk_precheck_flags_locksmith_words(self, mock_load_items: mock.Mock) -> None:
        mock_load_items.return_value = [{"text": "sliding door locksmith"}]
        out = _Out()
        rc = cmd_helpers_precheck_policy_risk(
            argparse.Namespace(
                items="/tmp/does-not-matter.json",
                strict=True,
            ),
            {"cfg": object(), "out": out},
        )
        self.assertEqual(rc, 1)
        self.assertTrue(out.last["strict_failed"])


if __name__ == "__main__":
    unittest.main()
