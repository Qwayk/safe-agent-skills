from __future__ import annotations

import builtins
import re
import unittest
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Generator
from unittest.mock import patch

from google_ads_api_tool.rpc_commands import (
    _best_effort_verify_after_write,
    _extract_request_update_expectations,
    _resource_table_from_resource_name,
    _resource_tables_for_verification,
    _verification_targets,
)
from google_ads_api_tool.rpc_v22_registry import RPC_METHODS_V22


class _FakeSearchGoogleAdsRequest:
    def __init__(self, customer_id: str, query: str) -> None:
        self.customer_id = customer_id
        self.query = query


class _FakeGoogleAdsService:
    def __init__(self, rows_by_resource: dict[str, Any]):
        self.rows_by_resource = rows_by_resource
        self.queries: list[str] = []

    def search(self, request: Any = None, **_: Any):  # noqa: ANN401
        query = ""
        if request is not None and hasattr(request, "query"):
            query = str(request.query)
        self.queries.append(query)
        match = re.search(r"resource_name\s*=\s*'([^']*)'", query)
        if not match:
            return []
        name = match.group(1).replace("\\'", "'")
        row = self.rows_by_resource.get(name)
        if row is None or row is False:
            return []
        if row is True:
            return [{}]
        return [row]


class _FakeClient:
    def __init__(self, rows_by_resource: dict[str, Any]):
        self.svc = _FakeGoogleAdsService(rows_by_resource)

    def get_service(self, name: str, **_: Any):  # noqa: ANN401
        if name != "GoogleAdsService":
            raise KeyError(name)
        return self.svc


class _FakeCfg:
    retry_max_attempts = 1
    retry_base_delay_s = 0


def _spec(service: str, method: str):
    for s in RPC_METHODS_V22:
        if s.service == service and s.method == method:
            return s
    raise AssertionError(f"Missing rpc spec: {service}.{method}")


@contextmanager
def _fake_search_request_class() -> Generator[None, None, None]:
    fake_module = ModuleType("google.ads.googleads.v22.services.types.google_ads_service")
    fake_module.SearchGoogleAdsRequest = _FakeSearchGoogleAdsRequest
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: A002
        if name == "google.ads.googleads.v22.services.types.google_ads_service":
            return fake_module
        return original_import(name, globals, locals, fromlist, level)

    with patch("builtins.__import__", side_effect=fake_import):
        yield


class TestRpcWriteVerification(unittest.TestCase):
    def test_verification_targets_marks_remove_as_absent(self) -> None:
        request_obj = {
            "operations": [
                {"remove": "customers/123/campaigns/111"},
                {"create": {"campaign": {"name": "new"}}},
            ]
        }
        response_obj = {"results": [{"resource_name": "customers/123/campaigns/222"}]}

        targets = _verification_targets(request_obj=request_obj, response_obj=response_obj)
        self.assertEqual(
            targets,
            [
                {
                    "resource_name": "customers/123/campaigns/111",
                    "should_exist": False,
                    "field_expectations": {},
                },
                {
                    "resource_name": "customers/123/campaigns/222",
                    "should_exist": True,
                    "field_expectations": {},
                },
            ],
        )

    def test_verification_targets_marks_mutate_remove_as_absent(self) -> None:
        request_obj = {
            "mutate_operations": [
                {
                    "campaign_operation": {
                        "remove": "customers/123/campaigns/111",
                    }
                }
            ]
        }
        response_obj = {"results": [{"resource_name": "customers/123/campaigns/222"}]}

        targets = _verification_targets(request_obj=request_obj, response_obj=response_obj)
        self.assertEqual(
            targets,
            [
                {
                    "resource_name": "customers/123/campaigns/111",
                    "should_exist": False,
                    "field_expectations": {},
                },
                {
                    "resource_name": "customers/123/campaigns/222",
                    "should_exist": True,
                    "field_expectations": {},
                },
            ],
        )

    def test_resource_tables_for_verification_dedupes_and_orders(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        tables = _resource_tables_for_verification(
            spec=spec,
            resource_name="customers/123/campaigns/111",
        )
        self.assertEqual(tables, ["campaign"])

    def test_best_effort_verify_create_or_update_target_is_present(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        request_obj = {"operations": [{"create": {"campaign": {"name": "Campaign 1"}}}]}
        response_obj = {"results": [{"resource_name": "customers/123/campaigns/123"}]}

        client = _FakeClient({"customers/123/campaigns/123": True})
        ctx = {"timeout_s": 5, "cfg": _FakeCfg()}

        with _fake_search_request_class():
            result = _best_effort_verify_after_write(
                client=client,
                customer_id="123",
                request_obj=request_obj,
                response_obj=response_obj,
                spec=spec,
                timeout_s=5.0,
                ctx=ctx,
            )

        self.assertTrue(result["ok"])
        self.assertTrue(result["fully_verified"])
        self.assertEqual(result["verified_resources"], 1)
        self.assertEqual(result["verified_fields"], 0)
        self.assertEqual(result["failed_resources"], [])

    def test_best_effort_verify_remove_target_is_absent(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        request_obj = {"operations": [{"remove": "customers/123/campaigns/123"}]}
        response_obj: dict[str, Any] = {}

        client = _FakeClient({"customers/123/campaigns/123": False})
        ctx = {"timeout_s": 5, "cfg": _FakeCfg()}

        with _fake_search_request_class():
            result = _best_effort_verify_after_write(
                client=client,
                customer_id="123",
                request_obj=request_obj,
                response_obj=response_obj,
                spec=spec,
                timeout_s=5.0,
                ctx=ctx,
            )

        self.assertTrue(result["ok"])
        self.assertTrue(result["fully_verified"])
        self.assertEqual(result["verified_resources"], 1)
        self.assertEqual(result["verified_fields"], 0)
        self.assertEqual(result["failed_resources"], [])

    def test_extract_request_update_expectations_normalizes_field_mask_paths(self) -> None:
        expectations, skipped = _extract_request_update_expectations(
            {
                "operations": [
                    {
                        "update": {
                            "resource_name": "customers/123/campaigns/123",
                            "status": "PAUSED",
                            "manual_cpc": {"enhanced_cpc_enabled": False},
                        },
                        "update_mask": "status,manualCpc.enhancedCpcEnabled",
                    }
                ]
            }
        )
        self.assertEqual(
            expectations,
            {
                "customers/123/campaigns/123": {
                    "manual_cpc.enhanced_cpc_enabled": False,
                    "status": "PAUSED",
                }
            },
        )
        self.assertEqual(skipped, [])

    def test_extract_request_update_expectations_supports_mutate_operations(self) -> None:
        expectations, skipped = _extract_request_update_expectations(
            {
                "mutate_operations": [
                    {
                        "campaign_operation": {
                            "update": {
                                "resource_name": "customers/123/campaigns/123",
                                "status": "PAUSED",
                            },
                            "update_mask": "status",
                        }
                    }
                ]
            }
        )
        self.assertEqual(
            expectations,
            {
                "customers/123/campaigns/123": {
                    "status": "PAUSED",
                }
            },
        )
        self.assertEqual(skipped, [])

    def test_best_effort_verify_update_fields_match(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        request_obj = {
            "operations": [
                {
                    "update": {
                        "resource_name": "customers/123/campaigns/123",
                        "status": "PAUSED",
                        "manual_cpc": {"enhanced_cpc_enabled": False},
                    },
                    "update_mask": "status,manualCpc.enhancedCpcEnabled",
                }
            ]
        }
        response_obj = {"results": [{"resource_name": "customers/123/campaigns/123"}]}

        client = _FakeClient(
            {
                "customers/123/campaigns/123": {
                    "campaign": {
                        "resource_name": "customers/123/campaigns/123",
                        "status": "PAUSED",
                    }
                }
            }
        )
        ctx = {"timeout_s": 5, "cfg": _FakeCfg()}

        with _fake_search_request_class():
            result = _best_effort_verify_after_write(
                client=client,
                customer_id="123",
                request_obj=request_obj,
                response_obj=response_obj,
                spec=spec,
                timeout_s=5.0,
                ctx=ctx,
            )

        self.assertTrue(result["ok"])
        self.assertEqual(result["verified_resources"], 1)
        self.assertEqual(result["verified_fields"], 2)
        self.assertEqual(result["failed_resources"], [])

    def test_best_effort_verify_update_field_mismatch_fails(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        request_obj = {
            "operations": [
                {
                    "update": {
                        "resource_name": "customers/123/campaigns/123",
                        "status": "PAUSED",
                    },
                    "update_mask": "status",
                }
            ]
        }
        response_obj = {"results": [{"resource_name": "customers/123/campaigns/123"}]}

        client = _FakeClient(
            {
                "customers/123/campaigns/123": {
                    "campaign": {
                        "resource_name": "customers/123/campaigns/123",
                        "status": "ENABLED",
                    }
                }
            }
        )
        ctx = {"timeout_s": 5, "cfg": _FakeCfg()}

        with _fake_search_request_class():
            result = _best_effort_verify_after_write(
                client=client,
                customer_id="123",
                request_obj=request_obj,
                response_obj=response_obj,
                spec=spec,
                timeout_s=5.0,
                ctx=ctx,
            )

        self.assertFalse(result["ok"])
        self.assertFalse(result["fully_verified"])
        self.assertEqual(result["verified_resources"], 0)
        self.assertEqual(result["verified_fields"], 0)
        self.assertEqual(len(result["failed_resources"]), 1)
        self.assertEqual(result["failed_resources"][0]["field_path"], "status")

    def test_resource_table_from_resource_name(self) -> None:
        self.assertEqual(_resource_table_from_resource_name("customers/123/campaignBudgets/555"), "campaign_budget")
        self.assertEqual(_resource_table_from_resource_name("customers/123/campaignCriteria/555"), "campaign_criterion")
