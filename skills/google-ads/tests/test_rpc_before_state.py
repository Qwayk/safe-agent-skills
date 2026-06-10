from __future__ import annotations

import builtins
import json
import re
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any, Generator
from unittest import mock

from google_ads_api_tool.config import Config
from google_ads_api_tool.errors import SafetyError
from google_ads_api_tool.protobuf_json import parse_request_json
from google_ads_api_tool.rpc_commands import _cmd_write
from google_ads_api_tool.rpc_v22_registry import RPC_METHODS_V22


class _Out:
    def __init__(self) -> None:
        self.last: Any | None = None

    def emit(self, obj: Any) -> None:
        self.last = obj


class _FakeSearchGoogleAdsRequest:
    def __init__(self, customer_id: str, query: str) -> None:
        self.customer_id = customer_id
        self.query = query


class _FakeGoogleAdsService:
    def __init__(self, resource_name: str) -> None:
        self.resource_name = resource_name
        self.queries: list[str] = []

    def search(self, request: Any = None, **_: Any) -> list[dict[str, Any]]:
        query = str(getattr(request, "query", "") or "")
        self.queries.append(query)
        match = re.search(r"resource_name\s*=\s*'([^']*)'", query)
        if not match:
            return []
        if match.group(1) != self.resource_name:
            return []
        status = "ENABLED" if len(self.queries) == 1 else "PAUSED"
        return [{"campaign": {"resource_name": self.resource_name, "status": status}}]


class _FakeCampaignService:
    def __init__(self, resource_name: str) -> None:
        self.resource_name = resource_name
        self.calls = 0

    def mutate_campaigns(self, request: Any = None, **_: Any) -> dict[str, Any]:
        self.calls += 1
        return {"results": [{"resource_name": self.resource_name}]}


class _FakeCampaignCriterionGoogleAdsService:
    def __init__(self, resource_name: str, *, ad_schedule: bool = True) -> None:
        self.resource_name = resource_name
        self.ad_schedule = ad_schedule
        self.removed = False
        self.queries: list[str] = []

    def search(self, request: Any = None, **_: Any) -> list[dict[str, Any]]:
        query = str(getattr(request, "query", "") or "")
        self.queries.append(query)
        match = re.search(r"resource_name\s*=\s*'([^']*)'", query)
        if not match or match.group(1) != self.resource_name or self.removed:
            return []
        criterion: dict[str, Any] = {
            "resource_name": self.resource_name,
            "campaign": "customers/123/campaigns/456",
            "criterion_id": "789",
            "type": "AD_SCHEDULE" if self.ad_schedule else "LOCATION",
            "status": "ENABLED",
        }
        if self.ad_schedule:
            criterion["ad_schedule"] = {
                "day_of_week": "SUNDAY",
                "start_hour": 6,
                "start_minute": "FORTY_FIVE",
                "end_hour": 18,
                "end_minute": "FORTY_FIVE",
            }
        return [{"campaign_criterion": criterion}]


class _FakeCampaignCriterionService:
    def __init__(self, google_ads_service: _FakeCampaignCriterionGoogleAdsService) -> None:
        self.google_ads_service = google_ads_service
        self.calls = 0

    def mutate_campaign_criteria(self, request: Any = None, **_: Any) -> dict[str, Any]:
        self.calls += 1
        self.google_ads_service.removed = True
        return {"results": [{"resource_name": self.google_ads_service.resource_name}]}


class _FakeClient:
    def __init__(self, resource_name: str) -> None:
        self.google_ads_service = _FakeGoogleAdsService(resource_name)
        self.campaign_service = _FakeCampaignService(resource_name)

    def get_service(self, name: str, **_: Any) -> Any:
        if name == "GoogleAdsService":
            return self.google_ads_service
        if name == "CampaignService":
            return self.campaign_service
        raise KeyError(name)


class _FakeCampaignCriterionClient:
    def __init__(self, resource_name: str, *, ad_schedule: bool = True) -> None:
        self.google_ads_service = _FakeCampaignCriterionGoogleAdsService(resource_name, ad_schedule=ad_schedule)
        self.campaign_criterion_service = _FakeCampaignCriterionService(self.google_ads_service)

    def get_service(self, name: str, **_: Any) -> Any:
        if name == "GoogleAdsService":
            return self.google_ads_service
        if name == "CampaignCriterionService":
            return self.campaign_criterion_service
        raise KeyError(name)


def _spec(service: str, method: str):
    for s in RPC_METHODS_V22:
        if s.service == service and s.method == method:
            return s
    raise AssertionError(f"Missing spec: {service}.{method}")


def _cfg() -> Config:
    return Config(
        developer_token="devtoken",
        client_id="clientid",
        client_secret="clientsecret",
        refresh_token="refreshtoken",
        login_customer_id=None,
        timeout_s=30.0,
        external_writes_disabled=False,
        write_customer_id_allowlist={"123"},
        max_mutate_operations_per_request=100,
        max_mutate_operations_per_run=1000,
        retry_max_attempts=1,
        retry_base_delay_s=0.0,
    )


def _base_ctx(artifacts_dir: Path | None) -> dict[str, Any]:
    return {
        "cfg": _cfg(),
        "apply": True,
        "out": _Out(),
        "plan_out": None,
        "plan_in": None,
        "receipt_out": None,
        "yes": False,
        "ack_irreversible": False,
        "ack_spend": False,
        "include_rpc_payload": False,
        "ack_sensitive_payload": False,
        "timeout_s": 1.0,
        "artifacts_dir": artifacts_dir,
    }


@contextmanager
def _fake_search_request_class() -> Generator[None, None, None]:
    fake_module = ModuleType("google.ads.googleads.v22.services.types.google_ads_service")
    fake_module.SearchGoogleAdsRequest = _FakeSearchGoogleAdsRequest
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: A002
        if name == "google.ads.googleads.v22.services.types.google_ads_service":
            return fake_module
        return original_import(name, globals, locals, fromlist, level)

    with mock.patch("builtins.__import__", side_effect=fake_import):
        yield


class TestRpcBeforeState(unittest.TestCase):
    def test_update_apply_saves_before_state_before_mutation(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        resource_name = "customers/123/campaigns/456"
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj={
                "customer_id": "123",
                "operations": [
                    {
                        "update": {"resource_name": resource_name, "status": "PAUSED"},
                        "update_mask": "status",
                    }
                ],
            },
        )

        with tempfile.TemporaryDirectory() as td:
            ctx = _base_ctx(Path(td) / "artifacts")
            fake_client = _FakeClient(resource_name)
            with mock.patch("google_ads_api_tool.rpc_commands.build_google_ads_client", return_value=fake_client):
                with _fake_search_request_class():
                    rc = _cmd_write(
                        spec=spec,
                        request_msg=request_msg,
                        in_path="request.json",
                        ctx=ctx,
                        customer_id_override="123",
                    )

            self.assertEqual(rc, 0)
            self.assertEqual(fake_client.campaign_service.calls, 1)
            payload = ctx["out"].last
            self.assertIsInstance(payload, dict)
            self.assertIn("before_state", payload)
            before_state = payload["receipt"]["before_state"]
            self.assertEqual(len(before_state["saved"]), 1)
            before_path = Path(before_state["saved"][0]["path"])
            self.assertTrue(before_path.exists())
            saved = json.loads(before_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["rows"][0]["campaign"]["status"], "ENABLED")
            self.assertTrue((Path(td) / "artifacts" / "plan.json").exists())
            self.assertTrue((Path(td) / "artifacts" / "receipt.json").exists())

    def test_campaign_criterion_ad_schedule_remove_saves_before_state_before_mutation(self) -> None:
        spec = _spec("CampaignCriterionService", "MutateCampaignCriteria")
        resource_name = "customers/123/campaignCriteria/456~789"
        request_obj = {"customer_id": "123", "operations": [{"remove": resource_name}]}
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj=request_obj,
        )

        with tempfile.TemporaryDirectory() as td:
            plan_path = Path(td) / "plan.json"
            dry_ctx = _base_ctx(None)
            dry_ctx["apply"] = False
            dry_ctx["plan_out"] = str(plan_path)
            _cmd_write(
                spec=spec,
                request_msg=request_msg,
                in_path="request.json",
                ctx=dry_ctx,
                customer_id_override="123",
            )

            apply_ctx = _base_ctx(Path(td) / "artifacts")
            apply_ctx["yes"] = True
            apply_ctx["ack_irreversible"] = True
            apply_ctx["plan_in"] = str(plan_path)
            fake_client = _FakeCampaignCriterionClient(resource_name)
            with mock.patch("google_ads_api_tool.rpc_commands.build_google_ads_client", return_value=fake_client):
                with _fake_search_request_class():
                    rc = _cmd_write(
                        spec=spec,
                        request_msg=request_msg,
                        in_path="request.json",
                        ctx=apply_ctx,
                        customer_id_override="123",
                    )

            self.assertEqual(rc, 0)
            self.assertEqual(fake_client.campaign_criterion_service.calls, 1)
            self.assertEqual(len(fake_client.google_ads_service.queries), 2)
            self.assertIn("campaign_criterion.ad_schedule.day_of_week", fake_client.google_ads_service.queries[0])

            payload = apply_ctx["out"].last
            before_state = payload["receipt"]["before_state"]
            self.assertEqual(len(before_state["saved"]), 1)
            saved_item = before_state["saved"][0]
            self.assertEqual(saved_item["metadata"]["remove_kind"], "campaign_criterion_ad_schedule")
            before_path = Path(saved_item["path"])
            saved = json.loads(before_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["rows"][0]["campaign_criterion"]["ad_schedule"]["day_of_week"], "SUNDAY")
            self.assertEqual(saved["metadata"]["operation_type"], "remove")

            recipes = payload["receipt"]["restore_recipes"]
            self.assertEqual(len(recipes), 1)
            self.assertEqual(recipes[0]["type"], "campaign_criterion_ad_schedule_add_back")
            self.assertEqual(recipes[0]["source_before_state_path"], str(before_path))
            self.assertTrue(payload["receipt"]["verification"]["ok"])

    def test_campaign_criterion_non_ad_schedule_remove_refuses_before_mutation(self) -> None:
        spec = _spec("CampaignCriterionService", "MutateCampaignCriteria")
        resource_name = "customers/123/campaignCriteria/456~789"
        request_obj = {"customer_id": "123", "operations": [{"remove": resource_name}]}
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj=request_obj,
        )

        with tempfile.TemporaryDirectory() as td:
            plan_path = Path(td) / "plan.json"
            dry_ctx = _base_ctx(None)
            dry_ctx["apply"] = False
            dry_ctx["plan_out"] = str(plan_path)
            _cmd_write(
                spec=spec,
                request_msg=request_msg,
                in_path="request.json",
                ctx=dry_ctx,
                customer_id_override="123",
            )

            apply_ctx = _base_ctx(Path(td) / "artifacts")
            apply_ctx["yes"] = True
            apply_ctx["ack_irreversible"] = True
            apply_ctx["plan_in"] = str(plan_path)
            fake_client = _FakeCampaignCriterionClient(resource_name, ad_schedule=False)
            with mock.patch("google_ads_api_tool.rpc_commands.build_google_ads_client", return_value=fake_client):
                with _fake_search_request_class():
                    with self.assertRaises(SafetyError) as cm:
                        _cmd_write(
                            spec=spec,
                            request_msg=request_msg,
                            in_path="request.json",
                            ctx=apply_ctx,
                            customer_id_override="123",
                        )

            self.assertIn("not AD_SCHEDULE", str(cm.exception))
            self.assertEqual(fake_client.campaign_criterion_service.calls, 0)

    def test_create_apply_refuses_before_client_construction(self) -> None:
        spec = _spec("AdGroupCriterionService", "MutateAdGroupCriteria")
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj={
                "customer_id": "123",
                "operations": [
                    {
                        "create": {
                            "ad_group": "customers/123/adGroups/456",
                            "status": "ENABLED",
                            "keyword": {"text": "test", "match_type": "EXACT"},
                        }
                    }
                ],
            },
        )

        with tempfile.TemporaryDirectory() as td:
            ctx = _base_ctx(Path(td) / "artifacts")
            with mock.patch("google_ads_api_tool.rpc_commands.build_google_ads_client") as build_client:
                build_client.side_effect = AssertionError("client should not be constructed")
                with self.assertRaises(SafetyError) as cm:
                    _cmd_write(
                        spec=spec,
                        request_msg=request_msg,
                        in_path="request.json",
                        ctx=ctx,
                        customer_id_override="123",
                    )
            self.assertIn("create", str(cm.exception))
            self.assertIn("before-state", str(cm.exception))

    def test_unsupported_remove_refuses_before_client_construction(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj={
                "customer_id": "123",
                "operations": [
                    {
                        "remove": "customers/123/campaigns/456",
                    }
                ],
            },
        )

        with tempfile.TemporaryDirectory() as td:
            plan_path = Path(td) / "plan.json"
            dry_ctx = _base_ctx(None)
            dry_ctx["apply"] = False
            dry_ctx["plan_out"] = str(plan_path)
            _cmd_write(
                spec=spec,
                request_msg=request_msg,
                in_path="request.json",
                ctx=dry_ctx,
                customer_id_override="123",
            )

            ctx = _base_ctx(Path(td) / "artifacts")
            ctx["yes"] = True
            ctx["ack_irreversible"] = True
            ctx["plan_in"] = str(plan_path)
            with mock.patch("google_ads_api_tool.rpc_commands.build_google_ads_client") as build_client:
                build_client.side_effect = AssertionError("client should not be constructed")
                with self.assertRaises(SafetyError) as cm:
                    _cmd_write(
                        spec=spec,
                        request_msg=request_msg,
                        in_path="request.json",
                        ctx=ctx,
                        customer_id_override="123",
                    )
            self.assertIn("unsupported remove", str(cm.exception))

    def test_update_apply_refuses_without_artifacts_before_client_construction(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj={
                "customer_id": "123",
                "operations": [
                    {
                        "update": {"resource_name": "customers/123/campaigns/456", "status": "PAUSED"},
                        "update_mask": "status",
                    }
                ],
            },
        )

        ctx = _base_ctx(None)
        with mock.patch("google_ads_api_tool.rpc_commands.build_google_ads_client") as build_client:
            build_client.side_effect = AssertionError("client should not be constructed")
            with self.assertRaises(SafetyError) as cm:
                _cmd_write(
                    spec=spec,
                    request_msg=request_msg,
                    in_path="request.json",
                    ctx=ctx,
                    customer_id_override="123",
                )
        self.assertIn("local run artifacts", str(cm.exception))
