from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from google.api_core import exceptions
from google.ads.googleads.v25.services.types.conversion_upload_service import UploadClickConversionsResponse
from google.ads.googleads.v25.errors.types.errors import GoogleAdsFailure
from google.protobuf.any_pb2 import Any

from google_ads_api_tool import rpc_commands as rpc
from google_ads_api_tool.protobuf_json import parse_request_json
from google_ads_api_tool.rpc_v25_registry import RPC_METHODS_V25


class TestWriteOutcomes(unittest.TestCase):
    def run_write(self, response=None, error=None, validate_only=False, receipt_out=None):
        spec = next(s for s in RPC_METHODS_V25 if s.method == "UploadClickConversions")
        request = parse_request_json(service=spec.service, request_type=spec.request_type,
            obj={"customer_id": "123", "partial_failure": True, "validate_only": validate_only,
                 "conversions": [{"gclid": "private-click", "conversion_action": "customers/123/conversionActions/1"}]})
        cfg = SimpleNamespace(retry_max_attempts=3, external_writes_disabled=False,
                              write_customer_id_allowlist={"123"})
        out, client = MagicMock(), MagicMock()
        method = client.get_service.return_value.upload_click_conversions
        method.return_value = response or UploadClickConversionsResponse()
        method.side_effect = error
        ctx = {"cfg": cfg, "apply": True, "out": out, "yes": True, "ack_no_snapshot": True,
               "receipt_out": receipt_out}
        with patch.object(rpc, "build_google_ads_client", return_value=client), \
             patch.object(rpc, "_artifact_before_dir"), \
             patch.object(rpc, "_write_plan_and_receipt_artifacts") as artifacts:
            code = rpc._cmd_write(spec=spec, request_msg=request, in_path="synthetic.json",
                                  ctx=ctx, customer_id_override=None)
        self.assertEqual(method.call_count, 1)
        self.assertIsNone(method.call_args.kwargs["retry"])
        self.assertIsNotNone(artifacts.call_args.kwargs["receipt"])
        return code, out.emit.call_args.args[0]

    def test_partial_failure_decodes_item_without_echoing_private_values(self):
        failure = GoogleAdsFailure(errors=[{
            "error_code": {"conversion_upload_error": "UNPARSEABLE_GCLID"},
            "message": "Rejected private-click", "trigger": {"string_value": "private-click"},
            "location": {"field_path_elements": [{"field_name": "conversions", "index": 0}]},
        }])
        detail = Any(); detail.Pack(failure._pb)
        response = UploadClickConversionsResponse(partial_failure_error={
            "code": 3, "message": "Rejected private-click", "details": [detail]})
        code, result = self.run_write(response=response)
        self.assertEqual(code, 1)
        self.assertFalse(result["ok"])
        receipt = result["receipt"]
        self.assertEqual(receipt["outcome"], "partial_failure")
        self.assertEqual(receipt["partial_failure"]["errors"][0]["location"]["field_path_elements"][0]["index"], 0)
        self.assertNotIn("private-click", json.dumps(result))

    def test_ambiguous_errors_are_not_retried_and_leave_uncertain_receipt(self):
        for cls in (exceptions.DeadlineExceeded, exceptions.ServiceUnavailable, exceptions.InternalServerError):
            with self.subTest(error=cls):
                code, result = self.run_write(error=cls("private server detail"))
                self.assertEqual(code, 1)
                self.assertEqual(result["receipt"]["outcome"], "outcome_unknown")
                self.assertNotIn("private server detail", json.dumps(result))

    def test_unknown_and_malformed_details_preserve_receipt_and_known_errors(self):
        failure = GoogleAdsFailure(errors=[{
            "error_code": {"conversion_upload_error": "UNPARSEABLE_GCLID"},
            "location": {"field_path_elements": [{"field_name": "conversions", "index": 0}]},
        }])
        known = Any(); known.Pack(failure._pb)
        unknown = Any(type_url="type.googleapis.com/example.FutureErrorDetail", value=b"private-opaque-bytes")
        malformed = Any(type_url=known.type_url, value=b"\xff")
        for details, known_count, undecoded_count in (
            ([unknown], 0, 1), ([malformed], 0, 1), ([unknown, known, malformed], 1, 2),
        ):
            with self.subTest(details=len(details)), tempfile.TemporaryDirectory() as td:
                response = UploadClickConversionsResponse(partial_failure_error={
                    "code": 3, "message": "private-provider-message", "details": details})
                original = response._pb.SerializeToString()
                receipt_path = Path(td) / "receipt.json"
                code, result = self.run_write(response=response, receipt_out=str(receipt_path))
                self.assertEqual(code, 1)
                self.assertFalse(result["ok"])
                saved = json.loads(receipt_path.read_text())
                self.assertEqual(saved, result["receipt"])
                self.assertEqual(saved["outcome"], "partial_failure")
                self.assertEqual(len(saved["partial_failure"]["errors"]), known_count)
                self.assertEqual(saved["partial_failure"]["undecoded_details"], undecoded_count)
                self.assertFalse(saved["partial_failure"]["errors_decoded"])
                self.assertEqual(response._pb.SerializeToString(), original)
                self.assertNotIn("private-", json.dumps(result))

    def test_no_targets_does_not_claim_verified(self):
        code, result = self.run_write()
        self.assertEqual(code, 0)
        self.assertEqual(result["receipt"]["outcome"], "accepted_unverified")
        self.assertFalse(result["receipt"]["verification"]["fully_verified"])

    def test_validate_only_reports_validation_not_a_completed_write(self):
        code, result = self.run_write(validate_only=True)
        self.assertEqual(code, 0)
        self.assertEqual(result["receipt"]["outcome"], "validated")
        self.assertFalse(result["receipt"]["verification"]["attempted"])

    def test_readback_mismatch_is_not_reported_as_success(self):
        with patch.object(rpc, "_best_effort_verify_after_write", return_value={
            "attempted": True, "ok": False, "fully_verified": False,
        }):
            code, result = self.run_write()
        self.assertEqual(code, 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["receipt"]["outcome"], "verification_failed")

    def test_readback_success_does_not_erase_ambiguous_submission(self):
        with patch.object(rpc, "_best_effort_verify_after_write", return_value={
            "attempted": True, "ok": True, "fully_verified": True,
        }):
            code, result = self.run_write(error=exceptions.DeadlineExceeded("timeout"))
        self.assertEqual(code, 1)
        self.assertEqual(result["receipt"]["outcome"], "outcome_unknown")

    def test_read_retries_remain_available(self):
        fn = MagicMock(side_effect=[exceptions.ServiceUnavailable("temporary"), "result"])
        with patch.object(rpc.time, "sleep"):
            result = rpc._call_with_retries(fn, ctx={"cfg": SimpleNamespace(retry_max_attempts=3)})
        self.assertEqual(result, "result")
        self.assertEqual(fn.call_count, 2)

    def test_capped_readback_does_not_claim_full_verification(self):
        spec = next(s for s in RPC_METHODS_V25 if s.method == "MutateCampaigns")
        client = MagicMock()
        client.get_service.return_value.search.return_value = [{"campaign": {"resource_name": "present"}}]
        result = rpc._best_effort_verify_after_write(
            client=client, customer_id="123", request_obj={}, spec=spec, timeout_s=1,
            response_obj={"results": [{"resource_name": f"customers/123/campaigns/{i}"} for i in range(21)]},
            ctx={"cfg": SimpleNamespace(retry_max_attempts=1)})
        self.assertTrue(result["ok"])
        self.assertFalse(result["fully_verified"])
        self.assertEqual(result["unverified_resources"], 1)
