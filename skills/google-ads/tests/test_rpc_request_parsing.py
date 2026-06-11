from __future__ import annotations

import unittest

from google_ads_api_tool.errors import ValidationError
from google_ads_api_tool.protobuf_json import parse_request_json


class TestRpcRequestParsing(unittest.TestCase):
    def test_rejects_unknown_fields(self) -> None:
        with self.assertRaises(ValidationError):
            parse_request_json(
                service="GoogleAdsService",
                request_type="SearchGoogleAdsRequest",
                obj={"customer_id": "123", "query": "SELECT customer.id FROM customer", "nope": 1},
            )

    def test_accepts_empty_object_for_empty_request_messages(self) -> None:
        msg = parse_request_json(service="CustomerService", request_type="ListAccessibleCustomersRequest", obj={})
        self.assertIsNotNone(msg)

    def test_empty_object_still_fails_when_common_required_fields_exist(self) -> None:
        with self.assertRaises(ValidationError):
            parse_request_json(service="GoogleAdsService", request_type="SearchGoogleAdsRequest", obj={})

    def test_missing_common_required_fields(self) -> None:
        with self.assertRaises(ValidationError):
            parse_request_json(
                service="GoogleAdsService",
                request_type="SearchGoogleAdsRequest",
                obj={"query": "SELECT customer.id FROM customer"},
            )

    def test_mutate_requires_operations(self) -> None:
        with self.assertRaises(ValidationError):
            parse_request_json(
                service="CampaignService",
                request_type="MutateCampaignsRequest",
                obj={"customer_id": "123"},
            )
