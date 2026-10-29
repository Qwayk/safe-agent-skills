from __future__ import annotations

import importlib
import unittest
from unittest.mock import patch

from google.auth.credentials import AnonymousCredentials
from google.ads.googleads.client import GoogleAdsClient

from google_ads_api_tool.config import load_config
from google_ads_api_tool.google_ads_client import SUPPORTED_API_VERSION, build_google_ads_client
from google_ads_api_tool.protobuf_json import _service_to_types_module
from google_ads_api_tool.rpc_commands import _classify_mutate_risk, _method_is_write
from google_ads_api_tool.rpc_v25_registry import RPC_METHODS_V25


class TestApiVersion(unittest.TestCase):
    def test_oauth_config_works_without_developer_token_and_never_sends_legacy_token(self) -> None:
        for legacy in ("", "legacy-secret"):
            with patch.dict("os.environ", {
                "GOOGLE_ADS_CLIENT_ID": "test", "GOOGLE_ADS_CLIENT_SECRET": "test",
                "GOOGLE_ADS_REFRESH_TOKEN": "test", "GOOGLE_ADS_DEVELOPER_TOKEN": legacy,
            }, clear=True):
                cfg = load_config("/nonexistent-test-env")
            with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as factory:
                build_google_ads_client(cfg)
            self.assertNotIn("developer_token", factory.call_args.args[0])

    def test_client_default_is_explicit_for_reporting_and_helpers(self) -> None:
        with patch.dict("os.environ", {
            "GOOGLE_ADS_DEVELOPER_TOKEN": "test",
            "GOOGLE_ADS_CLIENT_ID": "test",
            "GOOGLE_ADS_CLIENT_SECRET": "test",
            "GOOGLE_ADS_REFRESH_TOKEN": "test",
        }):
            cfg = load_config("/nonexistent-test-env")
        with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as factory:
            build_google_ads_client(cfg)
        self.assertEqual(factory.call_args.kwargs["version"], SUPPORTED_API_VERSION)

    def test_every_registered_method_and_request_resolves_in_selected_api(self) -> None:
        client = GoogleAdsClient(credentials=AnonymousCredentials(), developer_token="test",
                                 version=SUPPORTED_API_VERSION, use_proto_plus=True)
        for spec in RPC_METHODS_V25:
            with self.subTest(method=f"{spec.service}.{spec.method}"):
                service = client.get_service(spec.service)
                self.assertTrue(callable(getattr(service, spec.python_method)))
                module = importlib.import_module(_service_to_types_module(spec.service))
                request = getattr(module, spec.request_type)()
                self.assertTrue(request._pb.DESCRIPTOR.full_name.startswith(
                    f"google.ads.googleads.{SUPPORTED_API_VERSION}."))
                self.assertIn(f".{SUPPORTED_API_VERSION}.", spec.rpc_path)

    def test_new_booking_and_authorization_methods_require_write_approval(self) -> None:
        for spec in RPC_METHODS_V25:
            if spec.method in {"BookCampaigns", "QuoteCampaigns", "ResolveMultiPartyAuthReview"}:
                self.assertTrue(_method_is_write(spec))
            if spec.method == "BookCampaigns":
                level, _ = _classify_mutate_risk(spec=spec, irreversible=False)
                self.assertEqual(level, "high")

    def test_retired_lifecycle_services_are_not_exposed(self) -> None:
        services = {s.service for s in RPC_METHODS_V25}
        self.assertNotIn("CampaignLifecycleGoalService", services)
        self.assertNotIn("CustomerLifecycleGoalService", services)
