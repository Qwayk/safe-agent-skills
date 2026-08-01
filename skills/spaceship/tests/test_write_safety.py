from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from spaceship_safe_agent_cli import operations
from spaceship_safe_agent_cli.cli import Output, _preflight_request, _run_operation


class _FakeHttpResponse:
    def __init__(
        self,
        status: int,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        attempts: int = 1,
        retry_after: int | None = None,
        throttled: bool = False,
        raw_body: bytes | None = None,
    ) -> None:
        self.status = status
        self.headers = headers or {}
        self.body = raw_body if raw_body is not None else json.dumps(payload or {}).encode("utf-8")
        self.url = ""
        self.attempts = attempts
        self.retry_after = retry_after
        self.throttled = throttled

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class _FakeTransport:
    def __init__(self, responses: list[_FakeHttpResponse]) -> None:
        self._responses = responses
        self.calls: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> _FakeHttpResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers or {},
                "params": params or {},
                "json_body": json_body,
                "data": data,
            }
        )
        if not self._responses:
            return _FakeHttpResponse(500, payload={"error": "no response queued"})
        return self._responses.pop(0)


class TestWriteSafety(unittest.TestCase):
    _path_values = {
        "contact": "c-123",
        "currentHost": "ns1.example.com",
        "domain": "example.com",
        "operationId": "op-456",
        "transactionId": "tx-789",
    }

    @staticmethod
    def _cfg() -> SimpleNamespace:
        return SimpleNamespace(base_url="https://spaceship.test/api", api_key="k", api_secret="s")

    @staticmethod
    def _write_body(path: Path, body: dict[str, Any]) -> str:
        p = path / "body.json"
        p.write_text(json.dumps(body), encoding="utf-8")
        return str(p)

    @property
    def write_specs(self) -> list[operations.OperationSpec]:
        return [spec for spec in operations.OFFICIAL_OPERATIONS if spec.stable and spec.method != "GET" and not spec.read_like]

    def _args_for_spec(self, spec: operations.OperationSpec, *, body: dict[str, Any] | None = None, with_body: bool = True, **overrides: Any) -> tuple[SimpleNamespace, str | None]:
        args = SimpleNamespace()
        for key in spec.path_params:
            args.__dict__[key] = self._path_values[key]
        for key, value in overrides.items():
            setattr(args, key, value)
        body_path = None
        if spec.body or spec.read_like:
            if getattr(args, "body_file", None) is None:
                body_payload = body or {}
                if with_body and body is not None:
                    body_payload = body
                body_path = self._write_body(Path(tempfile.mkdtemp()), body_payload)
                args.body_file = body_path
        for key in spec.query_params:
            if getattr(args, key, None) is None:
                args.__dict__[key] = None
        if not (spec.body or spec.read_like):
            args.body_file = None
        return args, body_path

    def _run(self, spec: operations.OperationSpec, responses: list[_FakeHttpResponse], **kwargs: Any) -> tuple[int, dict[str, Any], _FakeTransport]:
        args, _ = self._args_for_spec(spec, **kwargs)
        transport = _FakeTransport(responses)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _run_operation(spec, cfg=self._cfg(), args=args, transport=transport, out=Output(mode="json"))
        payload = json.loads(buf.getvalue()) if buf.getvalue() else {}
        return rc, payload, transport

    def _build_plan(self, spec: operations.OperationSpec, body: dict[str, Any] | None = None, **kwargs: Any) -> tuple[dict[str, Any], dict[str, Any], _FakeTransport, str]:
        plan_path = Path(tempfile.mkdtemp()) / "plan.json"
        responses = []
        preflight = _preflight_request(spec.operation_id, {p: self._path_values[p] for p in spec.path_params}, body)
        if preflight is not None:
            responses.append(_FakeHttpResponse(200, payload={"price": 12, "currency": "USD", "status": "ok"}))
        args, body_path = self._args_for_spec(spec, body=body or {}, with_body=bool(spec.body or spec.read_like), plan_out=str(plan_path))
        if body_path is None and body is not None and (spec.body or spec.read_like):
            args.body_file = self._write_body(plan_path.parent, body)
        rc, payload, transport = self._run(spec, responses, **{k: v for k, v in vars(args).items() if v is not None})
        self.assertEqual(rc, 0)
        self.assertTrue(payload.get("plan_path"))
        self.assertTrue(plan_path.exists())
        return json.loads(plan_path.read_text(encoding="utf-8")), payload, transport, str(plan_path)

    def test_stable_write_specs_emit_plan_with_integrity(self) -> None:
        body_templates: dict[str, dict[str, Any]] = {
            "saveContactAttributes": {"contactId": "c-123", "email": "owner@example.com"},
            "saveDetails": {"name": "Example"},
            "default": {"ok": True},
        }
        for spec in self.write_specs:
            body = body_templates.get(spec.operation_id, body_templates["default"])
            preflight = _preflight_request(spec.operation_id, {p: self._path_values[p] for p in spec.path_params}, body)
            responses = []
            if preflight is not None:
                responses.append(_FakeHttpResponse(200, payload={"price": 1, "currency": "USD"}))
            args, _ = self._args_for_spec(spec, body=body, with_body=bool(spec.body or spec.read_like))
            rc, payload, _ = self._run(spec, responses, **vars(args))
            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("dry_run"))
            self.assertEqual(payload.get("operation_id"), spec.operation_id)
            self.assertIn("plan_integrity", payload)
            self.assertEqual(len(payload["plan_integrity"]), 64)
            self.assertIn("selector", payload)
            self.assertEqual(payload["selector"]["path"]["params"], {p: self._path_values[p] for p in spec.path_params})
            self.assertEqual(payload["plan_kind"], "deterministic_only")
            self.assertIn("required_acknowledgements", payload)

    def test_apply_refuses_without_plan_or_yes(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "setDomainContacts")
        plan, _, _, path = self._build_plan(spec, {"contacts": {"admin": "a@x.com"}})
        args, _ = self._args_for_spec(spec, with_body=True, body={"contacts": {"admin": "a@x.com"}}, plan_in=str(path), apply=True, yes=False)
        rc1, payload1, _ = self._run(spec, [], **vars(args))
        self.assertEqual(rc1, 0)
        self.assertTrue(payload1["refused"])
        self.assertIn("requires --yes", ",".join(payload1["reasons"]))

        args2, _ = self._args_for_spec(spec, with_body=True, body={"contacts": {"admin": "a@x.com"}}, plan_in=str(path), apply=False, yes=True)
        rc2, payload2, _ = self._run(spec, [], **vars(args2))
        self.assertEqual(rc2, 0)
        self.assertTrue(payload2["dry_run"])
        self.assertNotIn("refused", payload2)

    def test_apply_requires_exact_command_query_and_body_hash(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "transferRequest")
        plan_obj, payload, _, plan_path = self._build_plan(spec, {"authCode": "ABC"})
        bad_plan_path = Path(tempfile.mkdtemp()) / "bad_plan.json"
        plan_obj["command"] = "qwayk-spaceship-safe-agent-cli domains wrong-command"
        bad_plan_path.write_text(json.dumps(plan_obj), encoding="utf-8")
        args, _ = self._args_for_spec(
            spec,
            with_body=True,
            body={"authCode": "ABC"},
            apply=True,
            yes=True,
            plan_in=str(bad_plan_path),
            ack_spend=True,
            ack_ownership=True,
            ack_private_data=True,
        )
        rc, out_payload, _ = self._run(spec, [_FakeHttpResponse(200, payload={})], **vars(args))
        self.assertEqual(rc, 0)
        self.assertTrue(out_payload["refused"])
        self.assertIn("command does not match", ",".join(out_payload["reasons"]))

        plan_obj["command"] = payload["command"]
        plan_obj["body_sha256"] = "0000" + str(plan_obj["body_sha256"])[4:]
        bad_plan_path.write_text(json.dumps(plan_obj), encoding="utf-8")
        args2, _ = self._args_for_spec(
            spec,
            with_body=True,
            body={"authCode": "ABC"},
            apply=True,
            yes=True,
            plan_in=str(bad_plan_path),
            ack_spend=True,
            ack_ownership=True,
            ack_private_data=True,
        )
        rc2, out_payload2, _ = self._run(spec, [_FakeHttpResponse(200, payload={})], **vars(args2))
        self.assertEqual(rc2, 0)
        self.assertTrue(out_payload2["refused"])
        self.assertIn("body SHA-256 mismatch", ",".join(out_payload2["reasons"]))

    def test_apply_refuses_when_snapshot_drift_detected(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "setDomainContacts")
        plan_obj, _, _, plan_path = self._build_plan(spec, {"contacts": {"admin": "a@x.com"}})
        plan_obj["snapshot"]["preflight"]["snapshot_digest"] = "first"
        Path(plan_path).write_text(json.dumps(plan_obj), encoding="utf-8")

        args, _ = self._args_for_spec(
            spec,
            with_body=True,
            body={"contacts": {"admin": "a@x.com"}},
            apply=True,
            yes=True,
            plan_in=plan_path,
            ack_private_data=True,
        )
        # same plan, but different snapshot digest on apply-time preflight should refuse.
        responses = [_FakeHttpResponse(200, payload={"price": 1, "currency": "USD"})]
        rc, payload, transport = self._run(spec, responses, **vars(args))
        self.assertEqual(rc, 0)
        self.assertTrue(payload.get("refused"))
        self.assertIn("drift", ",".join(payload.get("reasons", [])))
        self.assertEqual(len(transport.calls), 1)

    def test_no_snapshot_ack_flag_required(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "createSellerHubDomain")
        plan, _, _, plan_path = self._build_plan(spec, {"domain": "example.com"})
        args, _ = self._args_for_spec(
            spec,
            body=plan.get("request_body", {"domain": "example.com"}) if isinstance(plan.get("request_body"), dict) else {"domain": "example.com"},
            apply=True,
            yes=True,
            plan_in=plan_path,
            # omit ack-no-snapshot intentionally
            ack_spend=True,
            ack_financial=True,
            ack_ownership=True,
        )
        rc, payload, _ = self._run(spec, [_FakeHttpResponse(200, payload={})], **vars(args))
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("ack-no-snapshot", ",".join(payload["reasons"]))

    def test_apply_success_writes_once_and_verifies(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "setDomainContacts")
        plan, _, _, plan_path = self._build_plan(spec, {"contacts": {"admin": "a@x.com"}})
        preflight_payload = (plan.get("snapshot", {}).get("preflight", {}).get("payload_redacted") or {"price": 12, "currency": "USD"})
        args, _ = self._args_for_spec(
            spec,
            with_body=True,
            body={"contacts": {"admin": "a@x.com"}},
            apply=True,
            yes=True,
            plan_in=plan_path,
            ack_private_data=True,
        )
        responses = [
            _FakeHttpResponse(200, payload=preflight_payload),  # preflight re-check
            _FakeHttpResponse(200, payload={"ok": True}),      # apply
            _FakeHttpResponse(200, payload={"contacts": {"admin": "a@x.com"}}),  # readback
        ]
        rc, payload, transport = self._run(spec, responses, **vars(args))
        self.assertEqual(rc, 0)
        self.assertFalse(payload["refused"])
        self.assertEqual(len([c for c in transport.calls if c["method"] in {"POST", "PUT", "PATCH", "DELETE"}]), 1)

    def test_receipt_written_on_success_and_refusal(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "domainRenew")
        plan, _, _, plan_path = self._build_plan(spec, {"duration": 1})
        preflight_payload = (plan.get("snapshot", {}).get("preflight", {}).get("payload_redacted") or {"price": 12, "currency": "USD"})
        good_receipt = Path(tempfile.mkdtemp()) / "receipt.json"
        args, _ = self._args_for_spec(
            spec,
            body={"duration": 1},
            apply=True,
            yes=True,
            plan_in=plan_path,
            ack_ownership=True,
            ack_spend=True,
            ack_no_snapshot=True,
            receipt_out=str(good_receipt),
        )
        responses = [
            _FakeHttpResponse(200, payload=preflight_payload),
            _FakeHttpResponse(200, payload={"ok": True}),
            _FakeHttpResponse(200, payload={"domain": "example.com"}),
        ]
        rc, payload, _ = self._run(spec, responses, **vars(args))
        self.assertEqual(rc, 0)
        self.assertTrue(good_receipt.exists())
        receipt_payload = json.loads(good_receipt.read_text(encoding="utf-8"))
        self.assertFalse(receipt_payload["refused"])
        self.assertEqual(receipt_payload["operation_id"], spec.operation_id)

        bad_receipt = Path(tempfile.mkdtemp()) / "bad-receipt.json"
        args2, _ = self._args_for_spec(
            spec,
            body={"duration": 1},
            apply=True,
            yes=True,
            plan_in=plan_path,
            receipt_out=str(bad_receipt),
        )
        rc2, payload2, _ = self._run(spec, [_FakeHttpResponse(200, payload={"price": 1, "currency": "USD"})], **vars(args2))
        self.assertEqual(rc2, 0)
        self.assertTrue(payload2["refused"])
        self.assertTrue(bad_receipt.exists())
        bad_receipt_payload = json.loads(bad_receipt.read_text(encoding="utf-8"))
        self.assertTrue(bad_receipt_payload["refused"])

    def test_plan_and_receipt_redact_private_fields(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "saveDetails")
        body = {"authorizationCode": "TOP", "privateContact": {"email": "a@x.com"}, "transferAuthCode": "SAFE", "safePay": {"cardNumber": "4111"}}
        args, _ = self._args_for_spec(spec, body=body)
        responses = [_FakeHttpResponse(200, payload={"status": "ok"})]
        rc, payload, _ = self._run(spec, responses, **vars(args))
        self.assertEqual(rc, 0)
        redacted_body = payload["redacted_body"]
        self.assertEqual(redacted_body["redacted"], True)
        self.assertEqual(len(redacted_body["sha256"]), 64)
        rendered = json.dumps(payload)
        self.assertNotIn("TOP", rendered)
        self.assertNotIn("a@x.com", rendered)
        self.assertNotIn("SAFE", rendered)
        self.assertNotIn("4111", rendered)

    def test_financial_no_recheck_warning_and_immediate_apply_preflight(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "createCheckoutLink")
        body = {
            "type": "BuyNow",
            "domainName": "example.com",
            "basePrice": {"amount": "250.00", "currency": "USD"},
            "feePercentageShare": {"seller": 75, "buyer": 25},
        }
        plan, _, _, plan_path = self._build_plan(spec, body)
        self.assertEqual(
            plan["snapshot"]["preflight"]["path_params"],
            {"domain": "example.com"},
        )
        self.assertTrue(plan["financial_recheck"]["required"])
        self.assertFalse(plan["financial_recheck"]["available"])
        self.assertIn("ack-no-snapshot", plan["required_acknowledgements"])
        self.assertEqual(plan["critical_request_fields"]["domainName"], "example.com")
        self.assertEqual(
            plan["critical_request_fields"]["basePrice"],
            {"amount": "250.00", "currency": "USD"},
        )

        args, _ = self._args_for_spec(
            spec,
            body=body,
            apply=True,
            yes=True,
            plan_in=plan_path,
            ack_ownership=True,
            ack_financial=True,
            ack_no_snapshot=True,
        )
        preflight_payload = plan["snapshot"]["preflight"]["payload_redacted"]
        rc, payload, transport = self._run(
            spec,
            [
                _FakeHttpResponse(200, payload=preflight_payload),
                _FakeHttpResponse(200, payload={"url": "https://checkout.example/secret"}),
            ],
            **vars(args),
        )
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(len(transport.calls), 2)
        self.assertEqual(transport.calls[0]["method"], "GET")
        self.assertTrue(transport.calls[0]["url"].endswith("/sellerhub/domains/example.com"))
        self.assertEqual(payload["result"]["url"], "***REDACTED***")

    def test_http_204_write_success_writes_receipt_and_verifies(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "setDomainContacts")
        body = {"registrant": "contact-private-id"}
        plan, _, _, plan_path = self._build_plan(spec, body)
        args, _ = self._args_for_spec(
            spec,
            body=body,
            apply=True,
            yes=True,
            plan_in=plan_path,
            ack_private_data=True,
        )
        preflight_payload = plan["snapshot"]["preflight"]["payload_redacted"]
        rc, payload, transport = self._run(
            spec,
            [
                _FakeHttpResponse(200, payload=preflight_payload),
                _FakeHttpResponse(204, raw_body=b""),
                _FakeHttpResponse(200, payload={"contacts": {"registrant": "contact-private-id"}}),
            ],
            **vars(args),
        )
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status_code"], 204)
        self.assertEqual(payload["status_label"], "completed")
        self.assertIsNone(payload["result"])
        self.assertEqual(payload["receipt"]["transport"]["status_code"], 204)
        self.assertEqual(
            len([call for call in transport.calls if call["method"] in {"POST", "PUT", "PATCH", "DELETE"}]),
            1,
        )

    def test_transfer_request_uses_get_transfer_info_preflight_and_drift_check(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "transferRequest")
        body = {"authCode": "PRIVATE-CODE"}
        plan, _, plan_transport, plan_path = self._build_plan(spec, body)
        self.assertEqual(plan["snapshot"]["preflight"]["operation_id"], "getTransferInfo")
        self.assertEqual(len(plan_transport.calls), 1)
        self.assertTrue(plan_transport.calls[0]["url"].endswith("/v1/domains/example.com/transfer"))

        args, _ = self._args_for_spec(
            spec,
            body=body,
            apply=True,
            yes=True,
            plan_in=plan_path,
            ack_ownership=True,
            ack_private_data=True,
        )
        rc, payload, transport = self._run(
            spec,
            [_FakeHttpResponse(200, payload={"status": "changed"})],
            **vars(args),
        )
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("drift", ",".join(payload["reasons"]))
        self.assertEqual(len(transport.calls), 1)

    def test_official_readback_mappings_use_request_or_response_keys(self) -> None:
        cases: list[
            tuple[
                str,
                dict[str, Any],
                dict[str, Any],
                dict[str, Any],
                str,
                str | None,
            ]
        ] = [
            (
                "domainCreate",
                {"years": 1},
                {"status": "created"},
                {"name": "example.com"},
                "/v1/domains/example.com",
                None,
            ),
            (
                "saveDetails",
                {"firstName": "Private"},
                {"contactId": "private-contact-id"},
                {"firstName": "Private"},
                "/v1/contacts/private-contact-id",
                "private-contact-id",
            ),
            (
                "saveContactAttributes",
                {"type": "us", "entityType": "citizen"},
                {"contactId": "private-contact-id"},
                {"type": "us"},
                "/v1/contacts/attributes/private-contact-id",
                "private-contact-id",
            ),
            (
                "createSellerHubDomain",
                {"name": "example.com"},
                {"status": "created"},
                {"name": "example.com"},
                "/v1/sellerhub/domains/example.com",
                None,
            ),
            (
                "createSafePayTransaction",
                {"domainName": "example.com", "buyerId": "private-buyer"},
                {"transactionId": "private-transaction-id"},
                {"status": "pending", "buyerId": "private-buyer"},
                "/v1/sellerhub/safepay-transactions/private-transaction-id",
                "private-transaction-id",
            ),
        ]
        for operation_id, body, write_payload, read_payload, read_suffix, private_id in cases:
            with self.subTest(operation_id=operation_id):
                spec = next(spec for spec in self.write_specs if spec.operation_id == operation_id)
                plan, _, _, plan_path = self._build_plan(spec, body)
                args, _ = self._args_for_spec(
                    spec,
                    body=body,
                    apply=True,
                    yes=True,
                    plan_in=plan_path,
                    ack_spend=True,
                    ack_ownership=True,
                    ack_financial=True,
                    ack_private_data=True,
                    ack_no_snapshot=True,
                )
                responses: list[_FakeHttpResponse] = []
                preflight = plan["snapshot"]["preflight"]
                if preflight.get("used"):
                    responses.append(
                        _FakeHttpResponse(200, payload=preflight["payload_redacted"])
                    )
                responses.extend(
                    [
                        _FakeHttpResponse(200, payload=write_payload),
                        _FakeHttpResponse(200, payload=read_payload),
                    ]
                )
                rc, payload, transport = self._run(spec, responses, **vars(args))
                self.assertEqual(rc, 0)
                self.assertEqual(payload["verification_status"], "verified")
                self.assertTrue(transport.calls[-1]["url"].endswith(read_suffix))
                provider_writes = [
                    call
                    for call in transport.calls
                    if call["method"] in {"POST", "PUT", "PATCH", "DELETE"}
                ]
                self.assertEqual(len(provider_writes), 1)
                if private_id:
                    self.assertNotIn(private_id, json.dumps(payload))
                    selector = payload["verification"]["selector"]["path"]["params"]
                    self.assertTrue(
                        any(
                            value == "***REDACTED***" or str(value).startswith("sha256:")
                            for value in selector.values()
                        )
                    )

    def test_response_key_readbacks_fall_back_honestly_when_id_is_missing(self) -> None:
        cases = [
            ("saveDetails", {"firstName": "Private"}, "missing_response_contact_id"),
            (
                "saveContactAttributes",
                {"type": "us", "entityType": "citizen"},
                "missing_response_contact_id",
            ),
            (
                "createSafePayTransaction",
                {"domainName": "example.com", "buyerId": "private-buyer"},
                "missing_response_transaction_id",
            ),
        ]
        for operation_id, body, reason in cases:
            with self.subTest(operation_id=operation_id):
                spec = next(spec for spec in self.write_specs if spec.operation_id == operation_id)
                plan, _, _, plan_path = self._build_plan(spec, body)
                args, _ = self._args_for_spec(
                    spec,
                    body=body,
                    apply=True,
                    yes=True,
                    plan_in=plan_path,
                    ack_spend=True,
                    ack_ownership=True,
                    ack_financial=True,
                    ack_private_data=True,
                    ack_no_snapshot=True,
                )
                responses: list[_FakeHttpResponse] = []
                preflight = plan["snapshot"]["preflight"]
                if preflight.get("used"):
                    responses.append(
                        _FakeHttpResponse(200, payload=preflight["payload_redacted"])
                    )
                responses.append(_FakeHttpResponse(200, payload={"status": "created"}))
                rc, payload, transport = self._run(spec, responses, **vars(args))
                self.assertEqual(rc, 0)
                self.assertEqual(payload["verification_status"], "unverified")
                self.assertEqual(payload["verification"]["reason"], reason)
                self.assertEqual(
                    len(
                        [
                            call
                            for call in transport.calls
                            if call["method"] in {"POST", "PUT", "PATCH", "DELETE"}
                        ]
                    ),
                    1,
                )

    def test_checkout_link_stays_honestly_unverified(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "createCheckoutLink")
        body = {"domainName": "example.com", "basePrice": {"amount": "10", "currency": "USD"}}
        plan, _, _, plan_path = self._build_plan(spec, body)
        args, _ = self._args_for_spec(
            spec,
            body=body,
            apply=True,
            yes=True,
            plan_in=plan_path,
            ack_ownership=True,
            ack_financial=True,
            ack_no_snapshot=True,
        )
        rc, payload, transport = self._run(
            spec,
            [
                _FakeHttpResponse(200, payload=plan["snapshot"]["preflight"]["payload_redacted"]),
                _FakeHttpResponse(200, payload={"url": "https://private.example/checkout"}),
            ],
            **vars(args),
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["verification_status"], "unverified")
        self.assertEqual(payload["verification"]["reason"], "no_reliable_readback_mapping")
        self.assertEqual(len(transport.calls), 2)

    def test_accepted_write_does_not_read_back(self) -> None:
        spec = next(spec for spec in self.write_specs if spec.operation_id == "saveContactAttributes")
        body = {"type": "us", "entityType": "citizen"}
        plan, _, _, plan_path = self._build_plan(spec, body)
        args, _ = self._args_for_spec(
            spec,
            body=body,
            apply=True,
            yes=True,
            plan_in=plan_path,
            ack_private_data=True,
            ack_no_snapshot=True,
        )
        rc, payload, transport = self._run(spec, [_FakeHttpResponse(202, payload={"operationId": "async-1"})], **vars(args))
        self.assertEqual(rc, 0)
        self.assertEqual(payload["verification_status"], "accepted_not_completed")
        self.assertEqual(len(transport.calls), 1)
