from __future__ import annotations

import re
import unittest

from google_ads_api_tool.rpc_commands import _READ_VERBS, _WRITE_VERBS, _method_is_write
from google_ads_api_tool.rpc_v22_registry import RPC_METHODS_V22


_CAMEL_BOUNDARY_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def _verb(method_name: str) -> str:
    return _CAMEL_BOUNDARY_RE.split(method_name.strip())[0]


def _spec(service: str, method: str):
    for s in RPC_METHODS_V22:
        if s.service == service and s.method == method:
            return s
    raise AssertionError(f"Missing spec: {service}.{method}")


class TestRpcWriteClassifier(unittest.TestCase):
    def test_every_registry_method_has_a_known_verb(self) -> None:
        allowed = set(_READ_VERBS) | set(_WRITE_VERBS)
        verbs = sorted({_verb(s.method) for s in RPC_METHODS_V22})
        unknown = [v for v in verbs if v not in allowed]
        self.assertEqual(unknown, [])

    def test_classifier_matches_known_verb_sets(self) -> None:
        for spec in RPC_METHODS_V22:
            verb = _verb(spec.method)
            if verb in _READ_VERBS:
                self.assertFalse(_method_is_write(spec), f"Expected read method: {spec.service}.{spec.method}")
            else:
                self.assertTrue(_method_is_write(spec), f"Expected write method: {spec.service}.{spec.method}")

    def test_previously_misclassified_verbs_are_writes(self) -> None:
        # These verbs are not Mutate*, but they are external state changes and must be gated as writes.
        examples = [
            ("BatchJobService", "AddBatchJobOperations"),
            ("CampaignDraftService", "PromoteCampaignDraft"),
            ("CustomerManagerLinkService", "MoveManagerLink"),
            ("ExperimentService", "ScheduleExperiment"),
            ("ExperimentService", "PromoteExperiment"),
            ("IdentityVerificationService", "StartIdentityVerification"),
            ("LocalServicesLeadService", "AppendLeadConversation"),
            ("RecommendationService", "DismissRecommendation"),
            ("ThirdPartyAppAnalyticsLinkService", "RegenerateShareableLinkId"),
        ]
        for service, method in examples:
            spec = _spec(service, method)
            self.assertTrue(_method_is_write(spec), f"Expected write: {service}.{method}")

