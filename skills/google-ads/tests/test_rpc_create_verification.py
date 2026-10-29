from __future__ import annotations

import copy
import json
import re
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from google.ads.googleads.v25.services.types.google_ads_service import MutateGoogleAdsResponse
from google.api_core import exceptions

from google_ads_api_tool import rpc_commands as rpc
from google_ads_api_tool.google_ads_client import protobuf_to_dict
from google_ads_api_tool.protobuf_json import parse_request_json
from tests.test_rpc_write_verification import _FakeCfg, _FakeClient, _fake_search_request_class, _spec


class TestKeywordCreateVerification(unittest.TestCase):
    def fixture(self, count=1, mixed=False, negative=True):
        creates = [{"ad_group": "customers/123/adGroups/456", "negative": negative,
                    "keyword": {"text": f"keyword {index}", "match_type": "EXACT"},
                    "status": "ENABLED"} for index in range(count)]
        names = [f"customers/123/adGroupCriteria/456~{900-index}" for index in range(count)]
        # Deliberately descending resource IDs: sorted names must not determine pairing.
        if mixed:
            request = {"mutate_operations": [{"ad_group_criterion_operation": {"create": c}} for c in creates]}
            response = {"mutate_operation_responses": [{"ad_group_criterion_result": {"resource_name": n}} for n in names]}
            spec = _spec("GoogleAdsService", "Mutate")
        else:
            request = {"operations": [{"create": c} for c in creates]}
            response = {"results": [{"resource_name": n} for n in names]}
            spec = _spec("AdGroupCriterionService", "MutateAdGroupCriteria")
        request["customer_id"] = "123"
        rows = {n: {"ad_group_criterion": {"resource_name": n, **copy.deepcopy(c)}} for n, c in zip(names, creates)}
        return request, response, rows, spec

    def verify(self, request, response, rows, spec):
        client = _FakeClient(rows)
        search = client.svc.search
        def checked_search(request=None, **kwargs):
            table = re.search(r"FROM (\w+)", request.query).group(1)
            if table not in {"ad_group_criterion", "campaign"}:
                raise ValueError("Unsupported GAQL resource table in test")
            return search(request=request, **kwargs)
        client.svc.search = checked_search
        with _fake_search_request_class():
            result = rpc._best_effort_verify_after_write(
                client=client, customer_id="123", request_obj=request, response_obj=response,
                spec=spec, timeout_s=1, ctx={"cfg": _FakeCfg()})
        return result, client.svc.queries

    def test_direct_and_mixed_keyword_creates_compare_all_five_fields(self):
        for mixed in (False, True):
            with self.subTest(mixed=mixed):
                req, resp, rows, spec = self.fixture(3, mixed=mixed)
                result, queries = self.verify(req, resp, rows, spec)
                self.assertTrue(result["fully_verified"])
                self.assertEqual(result["verified_fields"], 15)
                self.assertEqual(len(queries), 3)
                for query in queries:
                    for field in ("ad_group", "keyword.text", "keyword.match_type", "negative", "status"):
                        self.assertIn(f"ad_group_criterion.{field}", query)

    def test_each_wrong_keyword_field_and_wrong_group_fail(self):
        for field in ("ad_group", "negative", "status", "keyword.text", "keyword.match_type"):
            with self.subTest(field=field):
                req, resp, rows, spec = self.fixture(mixed=True)
                row = next(iter(rows.values()))["ad_group_criterion"]
                if field.startswith("keyword."):
                    row["keyword"][field.split(".")[1]] = "WRONG"
                else:
                    row[field] = False if field == "negative" else "WRONG"
                result, _ = self.verify(req, resp, rows, spec)
                self.assertFalse(result["ok"])
                self.assertFalse(result["fully_verified"])
                self.assertEqual(result["failed_resources"][0]["field_path"], field)

    def test_missing_nondefault_field_is_partial_not_full(self):
        req, resp, rows, spec = self.fixture()
        del next(iter(rows.values()))["ad_group_criterion"]["keyword"]
        result, _ = self.verify(req, resp, rows, spec)
        self.assertTrue(result["ok"])
        self.assertFalse(result["fully_verified"])
        self.assertTrue(result["skipped_fields"])

    def test_keyword_text_is_compared_literally_even_when_numeric(self):
        req, resp, rows, spec = self.fixture()
        req["operations"][0]["create"]["keyword"]["text"] = "001"
        next(iter(rows.values()))["ad_group_criterion"]["keyword"]["text"] = "1"
        result, _ = self.verify(req, resp, rows, spec)
        self.assertFalse(result["fully_verified"])
        self.assertEqual(result["failed_resources"][0]["field_path"], "keyword.text")

    def test_omitted_status_does_not_add_an_unrequested_condition(self):
        req, resp, rows, spec = self.fixture()
        del req["operations"][0]["create"]["status"]
        result, queries = self.verify(req, resp, rows, spec)
        self.assertTrue(result["fully_verified"])
        self.assertEqual(result["verified_fields"], 4)
        self.assertNotIn("ad_group_criterion.status", queries[0])

    def test_mixed_update_create_and_remove_keep_operation_order(self):
        req, resp, rows, spec = self.fixture(mixed=True)
        update_name = "customers/123/campaigns/10"
        remove_name = "customers/123/adGroupCriteria/456~1"
        req["mutate_operations"].insert(0, {"campaign_operation": {
            "update": {"resource_name": update_name, "status": "PAUSED"}, "update_mask": "status"}})
        req["mutate_operations"].append({"ad_group_criterion_operation": {"remove": remove_name}})
        resp["mutate_operation_responses"].insert(0, {"campaign_result": {"resource_name": update_name}})
        resp["mutate_operation_responses"].append({"ad_group_criterion_result": {"resource_name": remove_name}})
        rows[update_name] = {"campaign": {"resource_name": update_name, "status": "PAUSED"}}
        result, _ = self.verify(req, resp, rows, spec)
        self.assertTrue(result["fully_verified"])
        self.assertEqual(result["verified_resources"], 3)
        self.assertEqual(result["verified_fields"], 6)

    def test_positive_keyword_omitted_false_uses_protobuf_default(self):
        req, resp, rows, spec = self.fixture(negative=False)
        del req["operations"][0]["create"]["negative"]
        del next(iter(rows.values()))["ad_group_criterion"]["negative"]
        result, queries = self.verify(req, resp, rows, spec)
        self.assertTrue(result["fully_verified"])
        self.assertEqual(result["verified_fields"], 5)
        self.assertIn("ad_group_criterion.negative", queries[0])

    def test_response_count_mismatch_and_empty_placeholder_are_partial(self):
        for count_mismatch in (True, False):
            with self.subTest(count_mismatch=count_mismatch):
                req, resp, rows, spec = self.fixture(2, mixed=True)
                if count_mismatch:
                    resp["mutate_operation_responses"].pop()
                else:
                    resp["mutate_operation_responses"][0] = {}
                result, _ = self.verify(req, resp, rows, spec)
                self.assertFalse(result["fully_verified"])
                self.assertTrue(result["skipped_fields"])

    def test_duplicate_result_names_are_partial(self):
        req, resp, rows, spec = self.fixture(2, mixed=True)
        resp["mutate_operation_responses"][1] = copy.deepcopy(resp["mutate_operation_responses"][0])
        result, _ = self.verify(req, resp, rows, spec)
        self.assertFalse(result["fully_verified"])
        self.assertTrue(result["skipped_fields"])

    def test_extra_create_field_and_nonkeyword_create_stay_partial(self):
        for extra in (True, False):
            with self.subTest(extra=extra):
                req, resp, rows, spec = self.fixture()
                if extra:
                    req["operations"][0]["create"]["cpc_bid_micros"] = 1000
                else:
                    req["operations"][0]["create"].pop("keyword")
                result, _ = self.verify(req, resp, rows, spec)
                self.assertFalse(result["fully_verified"])
                self.assertTrue(result["skipped_fields"])

    def test_twenty_target_cap_remains_partial(self):
        req, resp, rows, spec = self.fixture(21, mixed=True)
        result, queries = self.verify(req, resp, rows, spec)
        self.assertFalse(result["fully_verified"])
        self.assertEqual(result["unverified_resources"], 1)
        self.assertEqual(len(queries), 20)

    def test_remove_only_verifies_absence(self):
        req, resp, rows, spec = self.fixture()
        name = next(iter(rows))
        req["operations"] = [{"remove": name}]
        result, _ = self.verify(req, {"results": [{"resource_name": name}]}, {}, spec)
        self.assertTrue(result["fully_verified"])
        self.assertEqual(result["verified_fields"], 0)

    def run_write(self, wrong=False, omit=False, error=None):
        req, resp, rows, spec = self.fixture(3, mixed=True)
        request = parse_request_json(service=spec.service, request_type=spec.request_type, obj=req)
        response = MutateGoogleAdsResponse(resp)
        self.assertIn("mutate_operation_responses", protobuf_to_dict(response))
        if wrong:
            next(iter(rows.values()))["ad_group_criterion"]["keyword"]["text"] = "wrong"
        if omit:
            del next(iter(rows.values()))["ad_group_criterion"]["keyword"]
        fake_client = _FakeClient(rows)
        mutate = MagicMock(return_value=response, side_effect=error)
        # The engine loads the same GoogleAdsService for mutation and readback.
        fake_client.svc.mutate = mutate
        cfg = SimpleNamespace(retry_max_attempts=1, external_writes_disabled=False,
                              write_customer_id_allowlist={"123"})
        out = MagicMock()
        with tempfile.TemporaryDirectory() as td:
            receipt = Path(td) / "receipt.json"
            ctx = {"cfg": cfg, "apply": True, "yes": True, "ack_no_snapshot": True,
                   "out": out, "receipt_out": str(receipt), "artifacts_dir": td}
            with patch.object(rpc, "build_google_ads_client", return_value=fake_client), \
                 patch.object(rpc, "_write_plan_and_receipt_artifacts"):
                code = rpc._cmd_write(spec=spec, request_msg=request, in_path="test.json",
                                      ctx=ctx, customer_id_override=None)
            result = out.emit.call_args.args[0]
            self.assertEqual(json.loads(receipt.read_text()), result["receipt"])
        self.assertEqual(mutate.call_count, 1)
        self.assertIsNone(mutate.call_args.kwargs["retry"])
        return code, result["receipt"]

    def test_real_protobuf_end_to_end_verified_and_mismatched_receipts(self):
        for wrong in (False, True):
            with self.subTest(wrong=wrong):
                code, receipt = self.run_write(wrong=wrong)
                self.assertEqual(code, 1 if wrong else 0)
                self.assertEqual(receipt["outcome"], "verification_failed" if wrong else "verified")
                self.assertEqual(receipt["verification"]["verified_fields"], 14 if wrong else 15)

    def test_incomplete_readback_receipt_is_accepted_unverified(self):
        code, receipt = self.run_write(omit=True)
        self.assertEqual(code, 0)
        self.assertEqual(receipt["outcome"], "accepted_unverified")
        self.assertFalse(receipt["verification"]["fully_verified"])

    def test_ambiguous_keyword_create_is_never_resubmitted(self):
        code, receipt = self.run_write(error=exceptions.DeadlineExceeded("test timeout"))
        self.assertEqual(code, 1)
        self.assertEqual(receipt["outcome"], "outcome_unknown")
        self.assertFalse(receipt["verification"]["fully_verified"])


if __name__ == "__main__":
    unittest.main()
