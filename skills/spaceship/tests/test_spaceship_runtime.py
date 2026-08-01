from __future__ import annotations

import argparse
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from spaceship_safe_agent_cli import operations
from spaceship_safe_agent_cli.cli import (
    Output,
    _build_parser,
    _build_url,
    _persisted_command_display,
    _prepare_query_params,
    _redact,
    _redact_operation_payload,
    _run_operation,
    main,
)
from spaceship_safe_agent_cli.config import load_config
from spaceship_safe_agent_cli.http import HttpClient


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
        self.body = raw_body if raw_body is not None else json.dumps(payload if payload is not None else {}).encode("utf-8")
        self.url = ""
        self.attempts = attempts
        self.retry_after = retry_after
        self.throttled = throttled

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class _FakeTransport:
    def __init__(self, responses: list[_FakeHttpResponse]) -> None:
        self.responses = responses
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
        return self.responses.pop(0)


class _NoNetworkTransport:
    def __init__(self) -> None:
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
    ) -> None:
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
        raise AssertionError("network request attempted while no credentials were configured")


class TestSpaceshipRuntime(unittest.TestCase):
    _path_values = {
        "contact": "c-123",
        "currentHost": "ns1.example.com",
        "domain": "example.com",
        "operationId": "op-456",
        "transactionId": "tx-789",
    }

    @staticmethod
    def _cfg() -> SimpleNamespace:
        return SimpleNamespace(
            base_url="https://spaceship.dev/api",
            api_key="api-key",
            api_secret="api-secret",
        )

    def _write_body(self, body: dict[str, Any], root: Path) -> str:
        body_path = root / "body.json"
        body_path.write_text(json.dumps(body), encoding="utf-8")
        return str(body_path)

    def _run(self, spec: operations.OperationSpec, response_payload: list[_FakeHttpResponse], **kwargs: Any) -> tuple[int, dict[str, Any], _FakeTransport]:
        transport = _FakeTransport(response_payload)
        cfg = self._cfg()

        args = SimpleNamespace()
        for param in spec.path_params:
            args.__dict__[param] = self._path_values[param]
        for param, value in kwargs.get("query", {}).items():
            args.__dict__[param] = value
        for param in spec.query_params:
            if getattr(args, param, None) is None:
                # keep defaults optional; inject defaults by query intent in the test.
                args.__dict__[param] = None

        if spec.body or spec.read_like:
            with tempfile.TemporaryDirectory() as d:
                body_path = self._write_body(kwargs.get("body", {"ok": True}), Path(d))
                args.body_file = body_path
                with io.StringIO() as out:
                    with redirect_stdout(out):
                        rc = _run_operation(spec, cfg=cfg, args=args, transport=transport, out=Output(mode="json"))
                    payload = json.loads(out.getvalue()) if out.getvalue() else {}
            return rc, payload, transport

        with io.StringIO() as out:
            with redirect_stdout(out):
                rc = _run_operation(spec, cfg=cfg, args=args, transport=transport, out=Output(mode="json"))
            payload = json.loads(out.getvalue()) if out.getvalue() else {}
        return rc, payload, transport

    def test_runtime_command_count_and_stability(self) -> None:
        specs = operations.OFFICIAL_OPERATIONS
        self.assertEqual(len(specs), 40)
        self.assertEqual(sum(1 for s in specs if s.stable), 38)
        self.assertEqual(sum(1 for s in specs if not s.stable), 2)

    def test_persisted_commands_digest_sensitive_identifiers(self) -> None:
        parser = _build_parser()
        cases = (
            (["contacts", "get", "CONTACT-PATH-CANARY-a11"], "CONTACT-PATH-CANARY-a11"),
            (
                ["contacts", "attributes", "get", "CONTACT-ATTRIBUTE-CANARY-b22"],
                "CONTACT-ATTRIBUTE-CANARY-b22",
            ),
            (
                ["sellerhub", "safepay", "get", "TRANSACTION-CANARY-c33"],
                "TRANSACTION-CANARY-c33",
            ),
        )
        for argv, canary in cases:
            args = parser.parse_args(argv)
            displayed = _persisted_command_display(args, argv)
            self.assertNotIn(canary, displayed)
            self.assertIn("sha256:", displayed)
        domain_argv = ["domains", "get", "example.com"]
        self.assertIn(
            "example.com",
            _persisted_command_display(parser.parse_args(domain_argv), domain_argv),
        )

    def test_billing_and_opaque_private_error_fields_are_redacted(self) -> None:
        billing_canary = "BILLING-CONTACT-CANARY-d44"
        opaque_canary = "OPAQUE-PRIVATE-ERROR-CANARY-e55"
        safe = _redact({"contacts": {"billing": billing_canary}, "status": "safe"})
        self.assertNotIn(billing_canary, json.dumps(safe))
        self.assertEqual(safe["status"], "safe")
        domain_info = next(
            spec
            for spec in operations.OFFICIAL_OPERATIONS
            if spec.operation_id == "getDomainInfo"
        )
        _, ordinary_output, _ = self._run(
            domain_info,
            [_FakeHttpResponse(200, {"contacts": {"billing": billing_canary}})],
        )
        self.assertNotIn(billing_canary, json.dumps(ordinary_output))
        self.assertEqual(ordinary_output["result"]["contacts"], "***REDACTED***")
        for operation_id in ("transferRequest", "setDomainContacts", "createSafePayTransaction"):
            for private_payload in (
                {"detail": opaque_canary, "statusCode": 400},
                {"failure": {"response": opaque_canary}, "statusCode": 400},
                opaque_canary,
            ):
                redacted = _redact_operation_payload(operation_id, private_payload)
                encoded = json.dumps(redacted)
                self.assertNotIn(opaque_canary, encoded)
                self.assertTrue(redacted["redacted"])
                self.assertIn("sha256", redacted)

    def test_operation_body_and_query_flags_match_openapi_contract(self) -> None:
        expected_body_true = {
            "saveDetails",
            "saveContactAttributes",
            "deleteRecords",
            "saveRecords",
            "checkDomainsAvailability",
            "domainCreate",
            "domainRenew",
            "updateAutorenewal",
            "setDomainContacts",
            "setDomainNameservers",
            "updateDomainEmailProtectionPreference",
            "updateDomainPrivacyPreference",
            "transferRequest",
            "updateTransferLock",
            "updateDomainPersonalNameserverHostInfo",
            "updateSellerHubDomain",
            "createCheckoutLink",
            "createSellerHubDomain",
            "createSafePayTransaction",
        }
        self.assertEqual(sum(1 for spec in operations.OFFICIAL_OPERATIONS if spec.body), len(expected_body_true))

        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "openapi-query-parameters.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            fixture["source_sha256"],
            "d4025290f62a5d14ad17142e2d75a59c19504f61066dfdaf7fab3d357cb75eeb",
        )
        expected_query: dict[str, tuple[str, ...]] = {}
        components = fixture["components"]["parameters"]
        for operation_id, raw_parameters in fixture["operations"].items():
            resolved = []
            for parameter in raw_parameters:
                if "$ref" in parameter:
                    resolved.append(components[parameter["$ref"].split("/")[-1]])
                else:
                    resolved.append(parameter)
            expected_query[operation_id] = tuple(
                parameter["name"] for parameter in resolved if parameter["in"] == "query"
            )

        for spec in operations.OFFICIAL_OPERATIONS:
            self.assertEqual(spec.body, spec.operation_id in expected_body_true)
            self.assertEqual(set(spec.query_params), set(expected_query.get(spec.operation_id, ())), spec.operation_id)

    def test_registry_matches_supplied_official_openapi_directly(self) -> None:
        official_path = Path.home() / "Downloads" / "openapi.json"
        if not official_path.exists():
            self.skipTest("Supplied official OpenAPI input is not present on this machine")
        raw = official_path.read_bytes()
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "d4025290f62a5d14ad17142e2d75a59c19504f61066dfdaf7fab3d357cb75eeb",
        )
        document = json.loads(raw)
        self.assertEqual(document["openapi"].split(".")[0], "3")
        found: dict[str, tuple[str, str, tuple[str, ...], bool]] = {}
        for path, path_item in document["paths"].items():
            inherited_parameters = path_item.get("parameters", [])
            for method in ("get", "post", "put", "patch", "delete"):
                operation = path_item.get(method)
                if not isinstance(operation, dict):
                    continue
                parameters = [*inherited_parameters, *operation.get("parameters", [])]
                query_names: list[str] = []
                for parameter in parameters:
                    if "$ref" in parameter:
                        parameter = document["components"]["parameters"][
                            parameter["$ref"].split("/")[-1]
                        ]
                    if parameter.get("in") == "query":
                        query_names.append(parameter["name"])
                found[operation["operationId"]] = (
                    method.upper(),
                    path,
                    tuple(query_names),
                    "requestBody" in operation,
                )
        self.assertEqual(set(found), {spec.operation_id for spec in operations.OFFICIAL_OPERATIONS})
        for spec in operations.OFFICIAL_OPERATIONS:
            method, path, registered_query_names, has_body = found[spec.operation_id]
            self.assertEqual(method, spec.method, spec.operation_id)
            self.assertEqual(path, spec.path_template, spec.operation_id)
            self.assertEqual(
                set(registered_query_names), set(spec.query_params), spec.operation_id
            )
            self.assertEqual(has_body, spec.body or spec.read_like, spec.operation_id)

    def test_api_parser_registers_exact_nested_paths(self) -> None:
        parser = _build_parser()
        with tempfile.TemporaryDirectory() as d:
            body_path = self._write_body({"ok": True}, Path(d))
            for spec in operations.OFFICIAL_OPERATIONS:
                argv = list(spec.command)
                for path_arg in spec.path_params:
                    argv.append(self._path_values[path_arg])
                if spec.body or spec.read_like:
                    argv.extend(["--body-file", body_path])
                for query in spec.query_params:
                    flags = {
                        "orderBy": "--order-by",
                        "saleDateTimeFrom": "--sale-date-time-from",
                        "saleDateTimeTo": "--sale-date-time-to",
                    }
                    flag = flags.get(query, f"--{query}")
                    value = "1" if query in {"take", "skip"} else "2024-01-01T00:00:00.000Z"
                    argv.extend([flag, value])
                parsed = parser.parse_args(argv)
                self.assertIs(parsed.spec, spec)

    def test_cli_has_only_local_front_doors_and_fixed_operations(self) -> None:
        parser = _build_parser()
        top_action = next(
            action for action in parser._actions if isinstance(action, argparse._SubParsersAction)
        )
        top_commands = set(top_action.choices)
        self.assertTrue({"auth", "onboarding", "runs"}.issubset(top_commands))
        self.assertFalse({"demo", "jobs", "raw", "request", "rest", "oauth", "token"} & top_commands)
        self.assertEqual(len(operations.OFFICIAL_OPERATIONS), 40)
        help_text = parser.format_help()
        self.assertNotIn("--config", help_text)
        self.assertNotIn("--project-dir", help_text)
        self.assertNotIn("--ack-irreversible", help_text)

    def test_path_parameters_are_encoded_as_single_segments(self) -> None:
        url = _build_url(
            "https://spaceship.dev/api",
            "/v1/domains/{domain}/personal-nameservers/{currentHost}",
            {"domain": "example.com/../../escape", "currentHost": "ns 1/host"},
        )
        self.assertEqual(
            url,
            "https://spaceship.dev/api/v1/domains/example.com%2F..%2F..%2Fescape/personal-nameservers/ns%201%2Fhost",
        )
        with self.assertRaisesRegex(Exception, "Missing path parameter"):
            _build_url("https://spaceship.dev/api", "/v1/{operationId}", {})

    def test_refusal_operations_do_not_require_network(self) -> None:
        cfg = self._cfg()
        out = io.StringIO()
        transport = _FakeTransport([_FakeHttpResponse(500)])
        for operation_id in {"domainDelete", "getDomainPersonalNameserverHostInfo"}:
            spec = next(spec for spec in operations.OFFICIAL_OPERATIONS if spec.operation_id == operation_id)
            args = SimpleNamespace(**{param: self._path_values[param] for param in spec.path_params})
            with redirect_stdout(out):
                out.seek(0)
                out.truncate()
                rc = _run_operation(spec, cfg=cfg, args=args, transport=transport, out=Output(mode="json"))
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "UnavailableOperation")

    def test_load_config_allows_missing_credentials_when_optional(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("", encoding="utf-8")
            cfg = load_config(str(env_path), require_credentials=False)
            self.assertEqual(cfg.api_key, "")
            self.assertEqual(cfg.api_secret, "")

    def test_no_credentials_write_plan_does_not_call_network(self) -> None:
        spec = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "domainCreate")
        args = SimpleNamespace()
        args.domain = "example.com"
        with tempfile.TemporaryDirectory() as d:
            body_path = self._write_body({"nameServers": ["ns1.example.com", "ns2.example.com"]}, Path(d))
            args.body_file = body_path
            out = io.StringIO()
            transport = _NoNetworkTransport()
            cfg = SimpleNamespace(base_url="https://spaceship.dev/api", api_key="", api_secret="", timeout_s=30)
            with redirect_stdout(out):
                rc = _run_operation(spec, cfg=cfg, args=args, transport=transport, out=Output(mode="json"))
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan_kind"], "deterministic_only")
            self.assertEqual(payload["required_acknowledgements"], ["ack-spend", "ack-ownership", "ack-no-snapshot"])
            self.assertEqual(len(transport.calls), 0)

    def test_no_credentials_unavailable_operation_refuses_without_network(self) -> None:
        spec = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "domainDelete")
        args = SimpleNamespace(domain="example.com")
        out = io.StringIO()
        transport = _NoNetworkTransport()
        cfg = SimpleNamespace(base_url="https://spaceship.dev/api", api_key="", api_secret="", timeout_s=30)
        with redirect_stdout(out):
            rc = _run_operation(spec, cfg=cfg, args=args, transport=transport, out=Output(mode="json"))
        payload = json.loads(out.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["refusal_type"], "UnavailableOperation")
        self.assertEqual(len(transport.calls), 0)

    def test_cli_refuses_both_unavailable_commands_without_credentials(self) -> None:
        cases = [
            ["domains", "delete", "example.com"],
            ["domains", "personal-nameservers", "get-host", "example.com", "ns1.example.com"],
        ]
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("", encoding="utf-8")
            for argv in cases:
                out = io.StringIO()
                with redirect_stdout(out):
                    rc = main(["--env-file", str(env_path), "--no-artifacts", *argv])
                payload = json.loads(out.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["refused"])
                self.assertEqual(payload["status_code"], 501)

    def test_get_and_read_like_post_dispatch(self) -> None:
        spec_get = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "getDomainInfo")
        rc, payload, transport = self._run(
            spec_get,
            [_FakeHttpResponse(200, payload={"name": "Example"}, headers={"spaceship-async-operationid": "async-get"})],
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "GET")
        self.assertEqual(transport.calls[0]["method"], "GET")
        self.assertEqual(payload["async_operation_id"], "async-get")

        spec_read_like = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "checkDomainsAvailability")
        rc2, payload2, transport2 = self._run(
            spec_read_like,
            [_FakeHttpResponse(201, payload={"available": ["example.com"]})],
            body={"domains": ["example.com"]},
        )
        self.assertEqual(rc2, 0)
        self.assertEqual(payload2["method"], "POST")
        self.assertEqual(transport2.calls[0]["method"], "POST")

    def test_read_like_bulk_availability_requires_auth_and_rejects_write_flags(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("", encoding="utf-8")
            body_path = Path(self._write_body({"domains": ["example.com"]}, root))
            missing = io.StringIO()
            with redirect_stdout(missing):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--no-artifacts",
                        "domains",
                        "check-domains",
                        "--body-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc, 1)
            self.assertIn("Missing SPACESHIP_API_KEY", missing.getvalue())
            self.assertFalse((root / ".state").exists())

            env_path.write_text(
                "SPACESHIP_API_KEY=fake-key\nSPACESHIP_API_SECRET=fake-secret\n",
                encoding="utf-8",
            )
            transport = _FakeTransport([_FakeHttpResponse(200, payload={"items": []})])
            configured = io.StringIO()
            with patch("spaceship_safe_agent_cli.cli.HttpClient", return_value=transport):
                with redirect_stdout(configured):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--no-artifacts",
                            "domains",
                            "check-domains",
                            "--body-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(rc2, 0)
            self.assertEqual(len(transport.calls), 1)
            self.assertEqual(transport.calls[0]["method"], "POST")
            self.assertFalse((root / ".state").exists())

            rejected_transport = _FakeTransport([])
            rejected = io.StringIO()
            with patch("spaceship_safe_agent_cli.cli.HttpClient", return_value=rejected_transport):
                with redirect_stdout(rejected):
                    rc3 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--plan-out",
                            str(root / "not-allowed.json"),
                            "domains",
                            "check-domains",
                            "--body-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(rc3, 1)
            self.assertIn("does not accept write flags", rejected.getvalue())
            self.assertEqual(rejected_transport.calls, [])

    def test_pagination_skip_and_cursor_operations(self) -> None:
        spec_skip = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "getDomainList")
        _, payload_skip, transport_skip = self._run(
            spec_skip,
            [
                _FakeHttpResponse(200, payload={"domains": ["a.com"], "nextSkip": 1}),
                _FakeHttpResponse(200, payload={}),
            ],
            query={"take": 10, "skip": 0, "orderBy": "expirationDate"},
        )
        self.assertEqual(payload_skip["result"]["items"], ["a.com"])
        self.assertEqual(transport_skip.calls[0]["params"]["skip"], 0)
        self.assertEqual(transport_skip.calls[1]["params"]["skip"], 1)

        spec_cursor = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "getSoldDomains")
        _, payload_cursor, transport_cursor = self._run(
            spec_cursor,
            [
                _FakeHttpResponse(200, payload={"items": ["one"], "cursor": "cursor-2"}),
                _FakeHttpResponse(200, payload={"items": []}),
            ],
            query={
                "cursor": "cursor-1",
                "saleDateTimeFrom": "2024-01-01T00:00:00.000Z",
                "saleDateTimeTo": "2024-02-01T00:00:00.000Z",
            },
        )
        self.assertEqual(payload_cursor["cursor"], "cursor-2")
        self.assertEqual(payload_cursor["result"]["items"], ["one"])
        self.assertEqual(transport_cursor.calls[0]["params"]["take"], 100)
        self.assertEqual(transport_cursor.calls[0]["params"]["cursor"], "cursor-1")
        self.assertEqual(transport_cursor.calls[1]["params"]["cursor"], "cursor-2")
        self.assertEqual(
            transport_cursor.calls[1]["params"]["saleDateTimeFrom"],
            "2024-01-01T00:00:00.000Z",
        )

    def test_query_defaults_bounds_and_order_by_validate_before_network(self) -> None:
        domains = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "getDomainList")
        dns = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "getResourceRecordsList")
        sold = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "getSoldDomains")

        defaults = _prepare_query_params(sold, SimpleNamespace(take=None, cursor=None, saleDateTimeFrom=None, saleDateTimeTo=None))
        self.assertEqual(defaults, {"take": 100})
        with self.assertRaisesRegex(Exception, "take must be between 1 and 100"):
            _prepare_query_params(domains, SimpleNamespace(take=101, skip=0, orderBy=None))
        with self.assertRaisesRegex(Exception, "skip must be between 0"):
            _prepare_query_params(domains, SimpleNamespace(take=10, skip=-1, orderBy=None))
        with self.assertRaisesRegex(Exception, "orderBy must be one of"):
            _prepare_query_params(domains, SimpleNamespace(take=10, skip=0, orderBy="createdAt:asc"))
        self.assertEqual(
            _prepare_query_params(dns, SimpleNamespace(take=500, skip=0, orderBy="-type"))["take"],
            500,
        )
        with self.assertRaisesRegex(Exception, "take must be between 1 and 500"):
            _prepare_query_params(dns, SimpleNamespace(take=501, skip=0, orderBy=None))

    def test_sold_query_parser_uses_official_flag_names(self) -> None:
        parsed = _build_parser().parse_args(
            [
                "sellerhub",
                "list-sold-domains",
                "--take",
                "25",
                "--cursor",
                "cursor-1",
                "--sale-date-time-from",
                "2024-01-01T00:00:00.000Z",
                "--sale-date-time-to",
                "2024-02-01T00:00:00.000Z",
            ]
        )
        self.assertEqual(parsed.take, 25)
        self.assertEqual(parsed.cursor, "cursor-1")
        self.assertEqual(parsed.saleDateTimeFrom, "2024-01-01T00:00:00.000Z")
        self.assertEqual(parsed.saleDateTimeTo, "2024-02-01T00:00:00.000Z")

    def test_transfer_auth_code_and_opaque_private_payloads_are_redacted(self) -> None:
        spec = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "getAuthCode")
        _, payload, _ = self._run(
            spec,
            [_FakeHttpResponse(200, payload={"authCode": "TRANSFER-SECRET", "expires": "tomorrow"})],
        )
        rendered = json.dumps(payload)
        self.assertNotIn("TRANSFER-SECRET", rendered)
        self.assertEqual(payload["result"]["authCode"], "***REDACTED***")
        self.assertEqual(payload["result"]["expires"], "tomorrow")

        cases = {
            "getAuthCode": "TRANSFER-RAW",
            "readDetails": "CONTACT-RAW",
            "getSafePayTransaction": "SAFEPAY-RAW",
            "createCheckoutLink": "CHECKOUT-RAW",
        }
        for operation_id, marker in cases.items():
            safe = _redact_operation_payload(operation_id, {"response": marker})
            self.assertNotIn(marker, json.dumps(safe))
            self.assertTrue(safe["redacted"])
            self.assertEqual(len(safe["sha256"]), 64)

        _, raw_error, _ = self._run(
            spec,
            [_FakeHttpResponse(500, raw_body=b"TRANSFER-RAW")],
        )
        self.assertNotIn("TRANSFER-RAW", json.dumps(raw_error))
        self.assertTrue(raw_error["error"]["redacted"])

    def test_http_429_retry_is_bounded_without_real_sleep(self) -> None:
        class FakeResponse:
            def __init__(self, status: int) -> None:
                self.status_code = status
                self.headers = {"Retry-After": "1"}
                self.url = "https://spaceship.dev/api/v1/ping"
                self.content = b"{}"

        class FakeSession:
            def __init__(self) -> None:
                self.headers: dict[str, str] = {}
                self.calls = 0

            def request(self, *args: Any, **kwargs: Any) -> FakeResponse:
                self.calls += 1
                if self.calls < 3:
                    return FakeResponse(429)
                return FakeResponse(200)

        client = HttpClient(timeout_s=1, verbose=False, user_agent="x")
        client._session = cast(Any, FakeSession())
        sleeps: list[float] = []

        with patch("spaceship_safe_agent_cli.http.time.sleep", side_effect=lambda seconds: sleeps.append(seconds)):
            response = client.request("GET", "https://spaceship.dev/api/v1/ping")

        self.assertEqual(response.status, 200)
        self.assertEqual(response.attempts, 3)
        self.assertEqual(len(sleeps), 2)
        self.assertTrue(all(isinstance(x, float) and x > 0 for x in sleeps))

    def test_http_redirects_are_disabled_for_custom_credentials(self) -> None:
        class RedirectResponse:
            status_code = 302
            headers = {"Location": "https://evil.example/steal"}
            url = "https://spaceship.dev/api/v1/domains"
            content = b""

        class RedirectSession:
            def __init__(self) -> None:
                self.headers: dict[str, str] = {}
                self.calls: list[dict[str, Any]] = []

            def request(self, *args: Any, **kwargs: Any) -> RedirectResponse:
                self.calls.append(dict(kwargs))
                return RedirectResponse()

        client = HttpClient(timeout_s=1, verbose=False, user_agent="x")
        session = RedirectSession()
        client._session = cast(Any, session)
        response = client.request(
            "GET",
            "https://spaceship.dev/api/v1/domains",
            headers={"X-API-Key": "key", "X-API-Secret": "secret"},
        )
        self.assertEqual(response.status, 302)
        self.assertEqual(len(session.calls), 1)
        self.assertIs(session.calls[0]["allow_redirects"], False)

        spec = next(
            spec
            for spec in operations.OFFICIAL_OPERATIONS
            if spec.operation_id == "getDomainInfo"
        )
        rc, payload, transport = self._run(
            spec,
            [_FakeHttpResponse(302, payload={"location": "https://evil.example/steal"})],
        )
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["status_label"], "failed")
        self.assertEqual(payload["error_type"], "RequestError")
        self.assertEqual(len(transport.calls), 1)

    def test_runtime_host_enforcement_and_redaction(self) -> None:
        client = HttpClient(timeout_s=1, verbose=False, user_agent="x")
        with self.assertRaises(RuntimeError):
            client.request("GET", "http://spaceship.dev/api/v1/domains")
        with self.assertRaises(RuntimeError):
            client.request("GET", "https://example.com/api/v1/domains")

        payload = {
            "authorizationCode": "AUTH",
            "transferAuthCode": "XFER",
            "privateContact": {"email": "a@b.com"},
            "privateContacts": [{"phone": "123-456"}],
            "safePay": {"cardNumber": "4111", "cvv": "123"},
        }
        safe = _redact(payload)
        self.assertEqual(safe["authorizationCode"], "***REDACTED***")
        self.assertEqual(safe["transferAuthCode"], "***REDACTED***")
        self.assertEqual(safe["privateContact"], "***REDACTED***")
        self.assertEqual(safe["privateContacts"], "***REDACTED***")
        self.assertEqual(safe["safePay"]["cardNumber"], "***REDACTED***")
        self.assertEqual(safe["safePay"]["cvv"], "***REDACTED***")

        safepay = _redact_operation_payload(
            "getSafePayTransaction",
            {
                "id": "private-id",
                "buyerEmail": "buyer@example.com",
                "sellerUsername": "seller",
                "basePrice": {"amount": "100", "currency": "USD"},
                "status": "pending",
            },
        )
        self.assertEqual(safepay["id"], "***REDACTED***")
        self.assertEqual(safepay["buyerEmail"], "***REDACTED***")
        self.assertEqual(safepay["sellerUsername"], "***REDACTED***")
        self.assertEqual(safepay["basePrice"], {"amount": "100", "currency": "USD"})

        checkout = _redact_operation_payload(
            "createCheckoutLink",
            {"url": "https://private.example/checkout/secret", "domainName": "example.com"},
        )
        self.assertEqual(checkout["url"], "***REDACTED***")

    def test_preserves_spaceship_async_operation_id(self) -> None:
        spec = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "getAsyncOperationDetails")
        _, payload, _ = self._run(
            spec,
            [_FakeHttpResponse(200, payload={"done": True}, headers={"spaceship-async-operationid": "async-202"})],
            query={"operationId": "op-456"},
        )
        self.assertEqual(payload["async_operation_id"], "async-202")

    def test_accepted_not_completed_status_for_202(self) -> None:
        spec = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "getDomainList")
        _, payload, _ = self._run(
            spec,
            [_FakeHttpResponse(202, payload={"message": "accepted"}, headers={"spaceship-async-operationid": "async-202"})],
        )
        self.assertEqual(payload["status_label"], "accepted_not_completed")

    def test_empty_http_204_is_success_not_json_failure(self) -> None:
        spec = next(s for s in operations.OFFICIAL_OPERATIONS if s.operation_id == "getDomainInfo")
        rc, payload, _ = self._run(spec, [_FakeHttpResponse(204, raw_body=b"")])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status_code"], 204)
        self.assertEqual(payload["status_label"], "completed")
        self.assertIsNone(payload["result"])
