from __future__ import annotations

import hashlib
import hmac
import io
import json
import shutil
import stat
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from sav_domain_api import OPERATIONS
from sav_domain_api.cli import main
from sav_domain_api.errors import StateError, ToolError
from sav_domain_api.redaction import redact
from sav_domain_api.state import write_private_json


class FakeResponse:
    def __init__(
        self,
        status_code: int = 200,
        payload: object = None,
        url: str = "https://api.sav.com/domains_api_v1",
    ):
        self.status_code = status_code
        self._payload = payload if payload is not None else {"ok": True}
        self.url = url
        self.headers: dict[str, str] = {}
        body = (
            json.dumps(self._payload, ensure_ascii=False, sort_keys=True)
            if isinstance(self._payload, (dict, list))
            else str(self._payload)
        )
        self.content = body.encode("utf-8")
        self.text = body

    def json(self) -> Any:
        if not isinstance(self._payload, (dict, list)):
            raise ValueError("invalid json")
        return self._payload


def _cmd_to_argv(command_path: str) -> list[str]:
    return command_path.split(" ")


def _flag_args(values: dict[str, str]) -> list[str]:
    parts: list[str] = []
    for flag, value in values.items():
        if value.startswith("-"):
            parts.append(f"{flag}={value}")
        else:
            parts.extend((flag, value))
    return parts


def _write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _resign_plan(plan: dict[str, Any], key: bytes) -> dict[str, Any]:
    body = {name: value for name, value in plan.items() if name != "plan_hmac"}
    plan["plan_hmac"] = hmac.new(
        key,
        json.dumps(
            body,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return plan


def _run_cli(argv: list[str], request_handler) -> tuple[int, dict[str, Any], list[dict[str, Any]]]:
    with patch("sav_domain_api.http.requests.Session.request") as mock_request:
        call_log: list[dict[str, Any]] = []

        def _handler(*args, **kwargs) -> FakeResponse:
            method, url = args[-2:]
            call = {
                "method": method,
                "url": url,
                "headers": kwargs.get("headers") or {},
                "params": kwargs.get("params") or {},
                "timeout": kwargs.get("timeout"),
                "allow_redirects": kwargs.get("allow_redirects"),
                "rest_count": max(0, len(args) - 2),
            }
            call_log.append(call)
            return request_handler(call)

        mock_request.side_effect = _handler
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(argv)
    text = out.getvalue().strip()
    payload = json.loads(text) if text else {}
    return code, payload, call_log


def _empty_planless_env(tmp_dir: Path) -> Path:
    file = tmp_dir / "env"
    file.write_text("", encoding="utf-8")
    return file


def _auth_env(tmp_dir: Path) -> Path:
    file = tmp_dir / "env"
    file.write_text("SAV_API_KEY=fake-sav-test-key\n", encoding="utf-8")
    return file


def _operation_args(command_path: str, *, tmp_dir: Path | None = None) -> dict[str, str]:
    if command_path == "domains active":
        return {}
    if command_path == "sales recent-auction":
        return {}
    if command_path == "sales recent-premium":
        return {}
    if command_path == "pricing list":
        return {}
    if command_path == "domains remove-from-sale":
        return {"--domain-name": "example.com"}
    if command_path == "domains submit-transfer-code":
        if tmp_dir is None:
            raise AssertionError("transfer command test requires a private temp directory")
        code_file = tmp_dir / "transfer-code.txt"
        code_file.write_text("transfer-000\n", encoding="utf-8")
        code_file.chmod(0o600)
        return {"--domain-name": "example.com", "--auth-code-file": str(code_file)}
    if command_path == "domains set-auto-renewal":
        return {"--domain-name": "example.com", "--enabled": "1"}
    if command_path == "domains set-sale-price":
        return {"--domain-name": "example.com", "--sale-price": "42"}
    if command_path == "domains set-nameservers":
        return {
            "--domain-name": "example.com",
            "--ns-1": "ns1.example.net",
            "--ns-2": "ns2.example.net",
        }
    if command_path == "domains set-privacy":
        return {"--domain-name": "example.com", "--enabled": "0"}
    if command_path == "domains set-whois-contacts":
        return {
            "--domain-name": "example.com",
            "--name": "Alice One",
            "--organization": "Example LLC",
            "--email-address": "alice@example.com",
            "--street": "123 Main St",
            "--city": "Austin",
            "--country": "US",
            "--phone": "+1-555-0000",
            "--state": "TX",
            "--postal-code": "78701",
            "--update-registrant": "1",
            "--update-tech": "0",
            "--update-admin": "0",
        }
    if command_path == "domains list-external-sale":
        return {"--domain-name": "example.com", "--sale-price": "12"}
    raise AssertionError(f"Unknown command path {command_path}")


class TestSavRuntime(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="sav-test-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_all_12_dispatch_paths_and_plan_for_writes(self) -> None:
        for op in OPERATIONS:
            command = _cmd_to_argv(op["command_path"])
            args = _operation_args(op["command_path"], tmp_dir=self.tmp)
            base = ["--env-file", str(_auth_env(self.tmp)), "--output", "json"]
            if op["kind"] == "read":
                _, payload, calls = _run_cli(
                    [*base, *command, *_flag_args(args)],
                    lambda call: FakeResponse(),
                )
                self.assertEqual(calls[0]["method"], "GET")
                self.assertEqual(
                    calls[0]["url"], f"https://api.sav.com/domains_api_v1/{op['operation_id']}"
                )
                self.assertEqual(payload["operation_id"], op["operation_id"])
                self.assertEqual(payload["ok"], True)
            else:
                plan_path = self.tmp / f"{op['operation_id']}.plan.json"
                _, payload, calls = _run_cli(
                    [*base, "--plan-out", str(plan_path), *command, *_flag_args(args)],
                    lambda call: (_ for _ in ()).throw(
                        AssertionError("write dry-run must not call HTTP")
                    ),
                )
                self.assertEqual(calls, [])
                self.assertEqual(payload["dry_run"], True)
                self.assertEqual(payload["operation_id"], op["operation_id"])

    def test_fixed_host_and_api_key_header_on_apply(self) -> None:
        args = _operation_args("domains set-sale-price")
        dry_plan_path = self.tmp / "plan.json"
        _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(dry_plan_path),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )

        def _handler(call: dict[str, Any]) -> FakeResponse:
            self.assertEqual(call["method"], "GET")
            self.assertEqual(
                call["url"], "https://api.sav.com/domains_api_v1/update_domain_for_sale_price"
            )
            self.assertEqual(call["headers"].get("APIKEY"), "fake-sav-test-key")
            self.assertEqual(call["params"]["domain_name"], "example.com")
            self.assertEqual(call["params"]["sale_price"], "42")
            return FakeResponse(200, {"ok": True, "status": "updated"}, url=call["url"])

        rc, payload, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(dry_plan_path),
                "--receipt-out",
                str(self.tmp / "apply.receipt.json"),
                "domains",
                "set-sale-price",
                "--domain-name",
                "example.com",
                "--sale-price",
                "42",
            ],
            _handler,
        )
        self.assertEqual(rc, 0)
        self.assertEqual(
            calls[0]["url"], "https://api.sav.com/domains_api_v1/update_domain_for_sale_price"
        )
        self.assertEqual(payload["receipt"]["provider_response_only"], True)
        self.assertEqual(payload["provider_response_received"], True)
        self.assertEqual(payload["durable_state_verified"], False)
        self.assertEqual(payload["outcome"], "provider_accepted")
        self.assertNotIn("applied", payload)
        self.assertNotIn("durable", payload)
        self.assertTrue(payload["receipt_written"])
        self.assertEqual(payload["receipt_written"], Path(payload["receipt_path"]).is_file())
        self.assertEqual(
            payload["receipt"]["provider_response_only"],
            payload["provider_response_received"],
        )
        self.assertNotIn("verified", payload["receipt"]["verification"])
        self.assertNotIn("durable", payload["receipt"]["verification"].lower())
        self.assertIn("No independent readback", payload["receipt"]["verification"])

    def test_write_dry_run_no_key_and_zero_network(self) -> None:
        args = _operation_args("domains list-external-sale")
        rc, payload, calls = _run_cli(
            [
                "--env-file",
                str(_empty_planless_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "external-sale.plan.json"),
                "domains",
                "list-external-sale",
                *_flag_args(args),
            ],
            lambda call: (_ for _ in ()).throw(
                AssertionError("write dry-run should not call HTTP")
            ),
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["dry_run"], True)
        self.assertEqual(calls, [])

    def test_missing_approval_and_conflicts(self) -> None:
        args = _operation_args("domains remove-from-sale")
        dry_plan = self.tmp / "plan.json"
        _, _, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(dry_plan),
                "domains",
                "remove-from-sale",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        # apply without --plan-in
        _, payload, _calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "domains",
                "remove-from-sale",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertTrue(payload["refused"])
        _, payload2, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--plan-in",
                str(dry_plan),
                "domains",
                "remove-from-sale",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertTrue(payload2["refused"])
        _, payload3, _ = _run_cli(
            [
                "--env-file",
                str(_empty_planless_env(self.tmp)),
                "--output",
                "json",
                "--plan-in",
                str(dry_plan),
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "domains",
                "remove-from-sale",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertTrue(payload3["error"] == "Missing SAV_API_KEY in environment or env file")
        self.assertFalse(payload3["ok"])

    def test_plan_schema_and_command_mismatch(self) -> None:
        args = _operation_args("domains set-privacy")
        _, payload, _calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "plan.json"),
                "domains",
                "set-privacy",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        plan_path = Path(payload["plan_path"])
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["command"] = "sav domains active"
        _write_file(plan_path, json.dumps(plan))

        _, payload2, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(plan_path),
                "--receipt-out",
                str(self.tmp / "transfer.receipt.json"),
                "domains",
                "set-privacy",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertTrue(payload2["refused"])
        self.assertIn("Plan command does not match", payload2["reason"])

    def test_plan_and_receipt_are_mode_0600(self) -> None:
        args = _operation_args("domains set-sale-price")
        plan_path = self.tmp / "plan.json"
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(plan_path),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        mode = stat.S_IMODE(plan_path.stat().st_mode)
        self.assertEqual(mode, 0o600)
        self.assertEqual(payload["plan_path"], str(plan_path))

        def _handler(call: dict[str, Any]) -> FakeResponse:
            return FakeResponse(200, {"status": "ok"}, url=call["url"])

        receipt_path = self.tmp / "receipt.json"
        _, payload_apply, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(plan_path),
                "--receipt-out",
                str(receipt_path),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            _handler,
        )
        mode2 = stat.S_IMODE(receipt_path.stat().st_mode)
        self.assertEqual(mode2, 0o600)
        self.assertEqual(payload_apply["receipt_path"], str(receipt_path))
        self.assertEqual(payload_apply["receipt"]["provider_response_only"], True)

    def test_redaction_in_plan_and_receipt(self) -> None:
        args = _operation_args("domains submit-transfer-code", tmp_dir=self.tmp)
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_empty_planless_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "transfer-plan.json"),
                "domains",
                "submit-transfer-code",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertNotIn("transfer-000", json.dumps(payload))
        self.assertIn("<redacted>", json.dumps(payload))
        plan_path = Path(payload["plan_path"])
        self.assertIn("transfer-000", plan_path.read_text(encoding="utf-8"))
        self.assertEqual(stat.S_IMODE(plan_path.stat().st_mode), 0o600)
        _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(plan_path),
                "domains",
                "submit-transfer-code",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )

        def _handler(call: dict[str, Any]) -> FakeResponse:
            return FakeResponse(
                200,
                {
                    "ok": True,
                    "auth_code": "abc-xyz",
                    "whois": {"name": "Jane", "postal_code": "78701"},
                },
                url=call["url"],
            )

        _, payload_apply, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(plan_path),
                "--receipt-out",
                str(self.tmp / "redacted.receipt.json"),
                "domains",
                "submit-transfer-code",
                "--domain-name",
                "example.com",
            ],
            _handler,
        )
        receipt_json = json.dumps(payload_apply["receipt"]["response"])
        self.assertNotIn("abc-xyz", receipt_json)
        self.assertNotIn("Jane", receipt_json)
        self.assertNotIn("78701", receipt_json)
        self.assertIn("<redacted>", receipt_json)

    def test_missing_api_key_is_single_json_error_without_secret_leak(self) -> None:
        secret_env = self.tmp / "env"
        secret_env.write_text("NOISE=top-secret-token\n", encoding="utf-8")
        _, payload, calls = _run_cli(
            [
                "--env-file",
                str(secret_env),
                "--output",
                "json",
                "domains",
                "active",
            ],
            lambda call: FakeResponse(500, {"error": "should-not-run"}),
        )
        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertEqual(payload["error"], "Missing SAV_API_KEY in environment or env file")
        self.assertEqual(calls, [])
        self.assertNotIn("top-secret-token", json.dumps(payload))

    def test_plan_hmac_tamper_is_refused_without_network(self) -> None:
        args = _operation_args("domains set-sale-price")
        _, payload, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "tamper-plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertEqual(calls, [])
        plan_path = Path(payload["plan_path"])
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["plan_hmac"] = "0" * 64
        _write_file(plan_path, json.dumps(plan, ensure_ascii=False, sort_keys=True))

        rc, apply_payload, call_log = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(plan_path),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(
                200, {"unexpected": "network should be blocked"}, url=call["url"]
            ),
        )
        self.assertEqual(rc, 0)
        self.assertTrue(apply_payload["refused"])
        self.assertEqual(apply_payload["reason"], "Plan signature mismatch")
        self.assertEqual(call_log, [])

    def test_malformed_non_ascii_plan_hmac_is_safe_and_never_calls_network(self) -> None:
        args = _operation_args("domains set-sale-price")
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "malformed-hmac.plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"unexpected": True}, url=call["url"]),
        )
        plan_path = Path(payload["plan_path"])
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["plan_hmac"] = "é" * 64
        _write_file(plan_path, json.dumps(plan, ensure_ascii=False))
        plan_path.chmod(0o600)

        rc, result, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(plan_path),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"unexpected": True}, url=call["url"]),
        )
        self.assertEqual(rc, 1)
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["error_type"], "ValidationError")
        self.assertEqual(calls, [])

    def test_world_readable_plan_is_refused_without_network(self) -> None:
        args = _operation_args("domains set-whois-contacts")
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "public-plan.json"),
                "domains",
                "set-whois-contacts",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        plan_path = Path(payload["plan_path"])
        plan_path.chmod(0o644)
        rc, apply_payload, call_log = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(plan_path),
                "domains",
                "set-whois-contacts",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertEqual(rc, 0)
        self.assertTrue(apply_payload["refused"])
        self.assertEqual(apply_payload["reason"], "Plan file must use private mode 0600")
        self.assertEqual(call_log, [])

    def test_whois_private_plan_retains_exact_values_and_stdout_is_redacted(self) -> None:
        args = _operation_args("domains set-whois-contacts")
        rc, payload, call_log = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "whois.plan.json"),
                "domains",
                "set-whois-contacts",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertEqual(rc, 0)
        self.assertEqual(call_log, [])
        self.assertEqual(stat.S_IMODE((Path(payload["plan_path"])).stat().st_mode), 0o600)

        plan_payload = json.loads(Path(payload["plan_path"]).read_text(encoding="utf-8"))
        expected = {
            "domain_name": "example.com",
            "name": "Alice One",
            "organization": "Example LLC",
            "email_address": "alice@example.com",
            "street": "123 Main St",
            "city": "Austin",
            "country": "US",
            "phone": "+1-555-0000",
            "state": "TX",
            "postal_code": "78701",
            "update_admin": "0",
            "update_registrant": "1",
            "update_tech": "0",
        }
        self.assertEqual(plan_payload["params"], expected)
        redacted_plan = json.dumps(payload["plan"])
        self.assertIn("<redacted>", redacted_plan)
        self.assertNotIn("Alice One", redacted_plan)
        self.assertNotIn("Example LLC", redacted_plan)
        self.assertNotIn("alice@example.com", redacted_plan)
        self.assertNotIn("123 Main St", redacted_plan)

    def test_write_dry_run_defaults_to_dot_state_plan_path(self) -> None:
        env_dir = self.tmp / "stateful"
        env_dir.mkdir(parents=True, exist_ok=True)
        env_file = env_dir / ".env"
        env_file.write_text("SAV_API_KEY=fake-sav-test-key\n", encoding="utf-8")
        args = _operation_args("domains set-auto-renewal")
        try:
            rc, payload, call_log = _run_cli(
                [
                    "--env-file",
                    str(env_file),
                    "--output",
                    "json",
                    "domains",
                    "set-auto-renewal",
                    *_flag_args(args),
                ],
                lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
            )
            self.assertEqual(rc, 0)
            self.assertEqual(call_log, [])
            expected_dir = (env_dir / ".state" / "plans").resolve()
            self.assertEqual(Path(payload["plan_path"]).parent.resolve(), expected_dir)
        finally:
            shutil.rmtree(env_dir)

    def test_provider_http_error_returns_single_json_object(self) -> None:
        args = _operation_args("domains active")
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "domains",
                "active",
                *_flag_args(args),
            ],
            lambda call: (_ for _ in ()).throw(RuntimeError("Provider request failed: HTTP 500")),
        )
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "RuntimeError")
        self.assertEqual(payload["error"], "Provider request failed: HTTP 500")

    def test_read_http_error_responses_are_single_safe_json_without_body_leak(self) -> None:
        cases: tuple[tuple[str, object, str], ...] = (
            ("json", {"status": "failed", "authCode": "read-secret"}, "read-secret"),
            ("non_json", "raw read-secret provider body", "read-secret"),
        )
        for case_name, response_body, secret in cases:
            rc, payload, calls = _run_cli(
                [
                    "--env-file",
                    str(_auth_env(self.tmp)),
                    "--output",
                    "json",
                    "domains",
                    "active",
                ],
                lambda call, body=response_body: FakeResponse(
                    500,
                    body,
                    url=call["url"],
                ),
            )
            self.assertEqual(rc, 1, case_name)
            self.assertEqual(payload["ok"], False)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(payload["error"], "Provider request failed: HTTP 500")
            self.assertEqual(payload["parse_error"], True)
            self.assertEqual(len(calls), 1)
            self.assertNotIn(secret, json.dumps(payload))

    def test_provider_list_response_is_accepted(self) -> None:
        args = _operation_args("domains active")
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "domains",
                "active",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, [{"ok": True}], url=call["url"]),
        )
        self.assertEqual(payload["read"]["response"], [{"ok": True}])

    def test_parse_errors_are_single_json_object(self) -> None:
        def _bad_handler(call: dict[str, Any]) -> FakeResponse:
            response = FakeResponse(200, "not-json", url=call["url"])
            response.content = b"not-json"
            response.text = "not-json"
            response.json = lambda: (_ for _ in ()).throw(ValueError("bad json"))
            return response

        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "domains",
                "active",
            ],
            _bad_handler,
        )
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_sale_price_rejected_on_na_nan_and_bad_values_before_network(self) -> None:
        bad_values = ["NaN", "Infinity", "-Infinity", "0", "-1", "abc"]
        for command_path in ("domains set-sale-price", "domains list-external-sale"):
            for raw_value in bad_values:
                args = _operation_args(command_path)
                args["--sale-price"] = raw_value
                _, payload, calls = _run_cli(
                    [
                        "--env-file",
                        str(_auth_env(self.tmp)),
                        "--output",
                        "json",
                        *_cmd_to_argv(command_path),
                        *_flag_args(args),
                    ],
                    lambda call: (_ for _ in ()).throw(
                        AssertionError(
                            "sale-price validation must fail before any request is allowed"
                        )
                    ),
                )
                self.assertEqual(payload["ok"], False)
                self.assertEqual(payload["error_type"], "ValidationError")
                self.assertEqual(payload["error"], "sale-price must be a positive number")
                self.assertEqual(payload.get("parse_error"), True)
                self.assertEqual(calls, [])

    def test_tampered_plan_price_rehash_is_still_rejected_without_network(self) -> None:
        args = _operation_args("domains set-sale-price")
        _, payload, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "sale-price.plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: (_ for _ in ()).throw(AssertionError("dry-run should not call network")),
        )
        self.assertEqual(payload["dry_run"], True)
        self.assertEqual(calls, [])
        plan_path = Path(payload["plan_path"])
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["params"]["sale_price"] = "999"
        digest_payload = {key: value for key, value in plan.items() if key != "plan_digest"}
        plan["plan_digest"] = hashlib.sha256(
            json.dumps(
                digest_payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        _write_file(plan_path, json.dumps(plan, ensure_ascii=False, sort_keys=True))

        _, apply_payload, apply_calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(plan_path),
                "domains",
                "set-sale-price",
                "--domain-name",
                "example.com",
                "--sale-price",
                "999",
            ],
            lambda call: FakeResponse(200, {"unexpected": "must not run"}, url=call["url"]),
        )
        self.assertTrue(apply_payload.get("refused") or apply_payload["ok"] is False)
        self.assertEqual(apply_calls, [])

    def test_plan_state_failure_modes_remain_single_json_and_no_network(self) -> None:
        args = _operation_args("domains set-sale-price")
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "valid.plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        plan_path = Path(payload["plan_path"])
        signed_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        _write_file(plan_path, json.dumps(signed_plan))

        malformed_plan_path = self.tmp / "bad_json.plan.json"
        malformed_plan_path.write_text("{", encoding="utf-8")
        malformed_plan_path.chmod(0o600)
        missing_path = self.tmp / "missing.plan.json"
        if missing_path.exists():
            missing_path.unlink()

        bad_required_acks_plan = {**signed_plan, "required_acks": "--apply"}
        key_path = self.tmp / ".state" / "keys" / "plan-hmac.key"
        _resign_plan(bad_required_acks_plan, key_path.read_bytes())
        bad_required_acks_plan_path = self.tmp / "bad-acks.plan.json"
        _write_file(bad_required_acks_plan_path, json.dumps(bad_required_acks_plan, ensure_ascii=False))
        bad_required_acks_plan_path.chmod(0o600)

        cases = (
            ("missing", missing_path, "Plan file not found"),
            ("malformed", malformed_plan_path, "Malformed plan JSON"),
            ("bad_required_acks_type", bad_required_acks_plan_path, "Plan approvals field is invalid"),
        )
        for case_name, path, expected_error in cases:
            _, apply_payload, calls = _run_cli(
                [
                    "--env-file",
                    str(_auth_env(self.tmp)),
                    "--output",
                    "json",
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-high-risk",
                    "--plan-in",
                    str(path),
                    "domains",
                    "set-sale-price",
                    "--domain-name",
                    "example.com",
                    "--sale-price",
                    "42",
                ],
                lambda call, name=case_name: (_ for _ in ()).throw(
                    AssertionError(
                        f"plan state failure for {name} should not call network"
                    )
                ),
            )
            if apply_payload.get("ok", True):
                self.assertTrue(apply_payload["refused"])
                self.assertIn(expected_error, str(apply_payload.get("reason", "")))
            else:
                self.assertIn("error_type", apply_payload)
                self.assertEqual(apply_payload["error_type"], "ValidationError")
                self.assertIn(expected_error, apply_payload["error"])
            self.assertEqual(calls, [])

    def test_http_500_apply_still_creates_private_redacted_failure_receipt(self) -> None:
        args = _operation_args("domains set-sale-price")
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "sale-price.plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        plan_path = Path(payload["plan_path"])
        receipt_path = self.tmp / "failed.receipt.json"

        def _http_500(call: dict[str, Any]) -> FakeResponse:
            return FakeResponse(
                500,
                {
                    "ok": False,
                    "error_code": "downstream",
                    "status": "failed",
                    "auth_code": "should-never-appear",
                    "phone": "+1-555-0000",
                    "postal_code": "78701",
                },
                url=call["url"],
            )

        rc, apply_payload, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(plan_path),
                "--receipt-out",
                str(receipt_path),
                "domains",
                "set-sale-price",
                *_flag_args(_operation_args("domains set-sale-price")),
            ],
            _http_500,
        )
        self.assertEqual(rc, 1)
        self.assertEqual(apply_payload["ok"], False)
        self.assertEqual(
            apply_payload["error"], "Provider request failed: HTTP 500"
        )
        self.assertEqual(apply_payload["error_type"], "RuntimeError")
        self.assertEqual(apply_payload["retry"], "do-not-retry")
        self.assertEqual(apply_payload["provider_received"], True)
        self.assertEqual(apply_payload["provider_response_received"], True)
        self.assertFalse(apply_payload["durable_state_verified"])
        self.assertEqual(
            apply_payload["receipt"]["provider_response_only"],
            apply_payload["provider_response_received"],
        )
        self.assertEqual(apply_payload["receipt"]["outcome"], "failure")
        self.assertNotIn("durable", apply_payload)
        self.assertTrue(receipt_path.exists())
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["method"], "GET")
        self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o600)
        receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(receipt_payload["ok"], False)
        receipt_json = json.dumps(receipt_payload)
        self.assertNotIn("should-never-appear", receipt_json)
        self.assertIn("<redacted>", receipt_json)

    def test_unparseable_apply_response_creates_opaque_failure_receipt(self) -> None:
        args = _operation_args("domains set-sale-price")
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "unparseable.plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        receipt_path = self.tmp / "unparseable.receipt.json"
        rc, result, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(payload["plan_path"]),
                "--receipt-out",
                str(receipt_path),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(
                200,
                "raw provider body with transfer-secret",
                url=call["url"],
            ),
        )
        self.assertEqual(rc, 1)
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["error_type"], "RuntimeError")
        self.assertEqual(len(calls), 1)
        self.assertTrue(receipt_path.is_file())
        receipt_text = receipt_path.read_text(encoding="utf-8")
        self.assertNotIn("transfer-secret", receipt_text)
        self.assertIn("<redacted>", receipt_text)

    def test_redaction_variants_in_receipt_payload(self) -> None:
        args = _operation_args("domains set-whois-contacts")
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "whois.plan.json"),
                "domains",
                "set-whois-contacts",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        plan_path = Path(payload["plan_path"])
        receipt_path = self.tmp / "variants.receipt.json"

        def _response_with_sensitive_variants(call: dict[str, Any]) -> FakeResponse:
            _ = call
            return FakeResponse(
                200,
                {
                    "status": "ok",
                    "statusMeta": "200",
                    "authCode": "redacted-me",
                    "auth-code": "redacted-me-2",
                    "auth_code": "redacted-me-3",
                    "authcode": "redacted-me-4",
                    "whois": {
                        "fullName": "Jane",
                        "emailAddress": "jane@example.com",
                        "email": "legacy@example.com",
                        "postalCode": "78701",
                        "phoneNumber": "+1-555-9999",
                        "phone": "+1-555-0000",
                    },
                    "contactAddress": {"streetName": "1 Main", "postal_code": "10001", "phone": "+1-555-1111"},
                    "contact-address": "2 Main Ave",
                    "contactAddressLine1": "3 Main Street",
                    "contactAddressLine2": "4 Main Way",
                    "postal_code": "90001",
                    "postal-code": "90002",
                    "address": "1 Main Road",
                    "addressLine1": "2 Main Road",
                    "phone-number": "+1-555-2222",
                    "contact_email": "contact@example.com",
                    "contact": {"email": "contact2@example.com", "phone": "+1-555-3333"},
                },
                url="https://api.sav.com/domains_api_v1/update_domain_whois_contacts",
            )

        _, apply_payload, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(plan_path),
                "--receipt-out",
                str(receipt_path),
                "domains",
                "set-whois-contacts",
                *_flag_args(_operation_args("domains set-whois-contacts")),
            ],
            _response_with_sensitive_variants,
        )
        self.assertEqual(apply_payload["ok"], True)
        self.assertEqual(calls[0]["method"], "GET")
        receipt_json = json.dumps(apply_payload["receipt"]["response"])
        self.assertIn("status", receipt_json)
        self.assertIn("statusMeta", receipt_json)
        self.assertNotIn("redacted-me", receipt_json)
        self.assertNotIn("redacted-me-2", receipt_json)
        self.assertNotIn("redacted-me-3", receipt_json)
        self.assertNotIn("redacted-me-4", receipt_json)
        self.assertNotIn("jane@example.com", receipt_json)
        self.assertNotIn("legacy@example.com", receipt_json)
        self.assertNotIn("1 Main", receipt_json)
        self.assertNotIn("2 Main Ave", receipt_json)
        self.assertNotIn("3 Main Street", receipt_json)
        self.assertNotIn("4 Main Way", receipt_json)
        self.assertNotIn("1 Main Road", receipt_json)
        self.assertNotIn("2 Main Road", receipt_json)
        self.assertNotIn("78701", receipt_json)
        self.assertNotIn("+1-555-9999", receipt_json)
        self.assertNotIn("+1-555-1111", receipt_json)
        self.assertNotIn("90001", receipt_json)
        self.assertNotIn("90002", receipt_json)
        self.assertNotIn("+1-555-0000", receipt_json)
        self.assertNotIn("+1-555-2222", receipt_json)
        self.assertNotIn("+1-555-3333", receipt_json)
        self.assertNotIn("contact@example.com", receipt_json)
        self.assertNotIn("contact2@example.com", receipt_json)
        self.assertIn("<redacted>", receipt_json)
        receipt_file_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o600)
        self.assertIn("<redacted>", json.dumps(receipt_file_payload["receipt"]))

    def test_compact_sensitive_keys_redact_without_hiding_domain_metadata(self) -> None:
        result = redact(
            {
                "domainname": "example.com",
                "nameservers": ["ns1.example.net"],
                "statusmetadata": "kept",
                "authcode": "auth-secret",
                "whoisemail": "whois@example.com",
                "contactemail": "contact@example.com",
                "fullname": "Jane Example",
                "organizationname": "Example LLC",
                "emailaddress": "jane@example.com",
                "streetaddress": "1 Main Street",
                "countrycode": "US",
                "postalcode": "78701",
                "zipcode": "78701",
                "phonenumber": "+1-555-0100",
            }
        )
        self.assertEqual(result["domainname"], "example.com")
        self.assertEqual(result["nameservers"], ["ns1.example.net"])
        self.assertEqual(result["statusmetadata"], "kept")
        for key, value in result.items():
            if key not in {"domainname", "nameservers", "statusmetadata"}:
                self.assertEqual(value, "<redacted>", key)

    def test_transfer_does_not_accept_literal_auth_code_flag(self) -> None:
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "domains",
                "submit-transfer-code",
                "--domain-name",
                "example.com",
                "--auth-code",
                "  transfer-000  ",
            ],
            lambda call: (_ for _ in ()).throw(
                AssertionError("transfer should fail parser before any request")
            ),
        )
        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--auth-code", payload["error"])

    def test_transfer_dry_run_accepts_auth_code_file_and_hides_trimmed_secret(self) -> None:
        code_file = self.tmp / "transfer-code.txt"
        code_file.write_text("  transfer-secret  \n", encoding="utf-8")
        code_file.chmod(0o600)
        _, payload, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "transfer.plan.json"),
                "domains",
                "submit-transfer-code",
                "--domain-name",
                "example.com",
                "--auth-code-file",
                str(code_file),
            ],
            lambda call: (_ for _ in ()).throw(
                AssertionError("auth-code-file dry-run must not call network")
            ),
        )
        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["dry_run"], True)
        self.assertEqual(calls, [])
        redacted = json.dumps(payload)
        self.assertNotIn("transfer-secret", redacted)
        self.assertNotIn("  transfer-secret  ", redacted)
        plan_path = Path(payload["plan_path"])
        plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
        self.assertEqual(stat.S_IMODE(plan_path.stat().st_mode), 0o600)
        plan_dump = json.dumps(plan_payload, ensure_ascii=False, sort_keys=True)
        self.assertIn("transfer-secret", plan_dump)
        self.assertNotIn("  transfer-secret  ", plan_dump)

    def test_transfer_apply_does_not_require_auth_code_argument(self) -> None:
        code_file = self.tmp / "transfer-code.txt"
        code_file.write_text("  transfer-secret  \n", encoding="utf-8")
        code_file.chmod(0o600)
        dry_rc, dry_payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "transfer.plan.json"),
                "domains",
                "submit-transfer-code",
                "--domain-name",
                "example.com",
                "--auth-code-file",
                str(code_file),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertEqual(dry_rc, 0)
        self.assertIn("plan_path", dry_payload)
        plan_path = Path(dry_payload["plan_path"])
        _, apply_payload, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(plan_path),
                "domains",
                "submit-transfer-code",
                "--domain-name",
                "example.com",
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertEqual(apply_payload["ok"], True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["method"], "GET")

    def test_default_plan_and_signing_key_use_private_state(self) -> None:
        env_dir = self.tmp / "private-state"
        env_dir.mkdir(mode=0o700)
        env_file = _auth_env(env_dir)
        rc, payload, calls = _run_cli(
            [
                "--env-file",
                str(env_file),
                "--output",
                "json",
                "domains",
                "set-sale-price",
                "--domain-name",
                "example.com",
                "--sale-price",
                "42",
            ],
            lambda call: (_ for _ in ()).throw(
                AssertionError("dry-run must not call the provider")
            ),
        )
        self.assertEqual(rc, 0)
        self.assertEqual(calls, [])
        state_dir = env_dir / ".state"
        plans_dir = state_dir / "plans"
        keys_dir = state_dir / "keys"
        key_path = keys_dir / "plan-hmac.key"
        self.assertEqual(Path(payload["plan_path"]).parent.resolve(), plans_dir.resolve())
        for directory in (state_dir, plans_dir, keys_dir):
            self.assertTrue(directory.is_dir())
            self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)
        self.assertTrue(key_path.is_file())
        self.assertEqual(stat.S_IMODE(key_path.stat().st_mode), 0o600)
        self.assertEqual(len(key_path.read_bytes()), 32)
        self.assertEqual(stat.S_IMODE(Path(payload["plan_path"]).stat().st_mode), 0o600)

    def test_missing_changed_and_malformed_signing_keys_fail_before_network(self) -> None:
        for case_name in ("missing", "changed", "malformed"):
            case_dir = self.tmp / case_name
            case_dir.mkdir(mode=0o700)
            env_file = _auth_env(case_dir)
            _, dry_payload, dry_calls = _run_cli(
                [
                    "--env-file",
                    str(env_file),
                    "--output",
                    "json",
                    "domains",
                    "set-sale-price",
                    "--domain-name",
                    "example.com",
                    "--sale-price",
                    "42",
                ],
                lambda call: (_ for _ in ()).throw(
                    AssertionError("dry-run must not call the provider")
                ),
            )
            self.assertEqual(dry_calls, [])
            plan_path = Path(dry_payload["plan_path"])
            key_path = case_dir / ".state" / "keys" / "plan-hmac.key"
            self.assertTrue(key_path.is_file())
            if case_name == "missing":
                key_path.unlink()
            elif case_name == "changed":
                key_path.write_bytes(b"x" * 32)
                key_path.chmod(0o600)
            else:
                key_path.write_bytes(b"too-short")
                key_path.chmod(0o600)

            rc, result, calls = _run_cli(
                [
                    "--env-file",
                    str(env_file),
                    "--output",
                    "json",
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-high-risk",
                    "--plan-in",
                    str(plan_path),
                    "domains",
                    "set-sale-price",
                    "--domain-name",
                    "example.com",
                    "--sale-price",
                    "42",
                ],
                lambda call: FakeResponse(200, {"unexpected": True}, url=call["url"]),
            )
            self.assertIn(rc, (0, 1))
            self.assertEqual(calls, [])
            self.assertIn("ok", result)
            self.assertTrue(result.get("refused") or result["ok"] is False)
            self.assertNotIn(str(key_path), json.dumps(result))

    def test_valid_hmac_does_not_bypass_strict_plan_schema_types(self) -> None:
        env_dir = self.tmp / "typed-plan"
        env_dir.mkdir(mode=0o700)
        env_file = _auth_env(env_dir)
        _, dry_payload, _ = _run_cli(
            [
                "--env-file",
                str(env_file),
                "--output",
                "json",
                "domains",
                "set-sale-price",
                "--domain-name",
                "example.com",
                "--sale-price",
                "42",
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        plan_path = Path(dry_payload["plan_path"])
        key = (env_dir / ".state" / "keys" / "plan-hmac.key").read_bytes()
        original = json.loads(plan_path.read_text(encoding="utf-8"))
        cases = (
            ("schema_version", True),
            ("operation_id", 123),
            ("params", ["not", "an", "object"]),
            ("required_acks", "--apply"),
        )
        for field, value in cases:
            malformed = dict(original)
            malformed[field] = value
            _resign_plan(malformed, key)
            _write_file(plan_path, json.dumps(malformed, ensure_ascii=False))
            plan_path.chmod(0o600)
            rc, result, calls = _run_cli(
                [
                    "--env-file",
                    str(env_file),
                    "--output",
                    "json",
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-high-risk",
                    "--plan-in",
                    str(plan_path),
                    "domains",
                    "set-sale-price",
                    "--domain-name",
                    "example.com",
                    "--sale-price",
                    "42",
                ],
                lambda call: FakeResponse(200, {"unexpected": True}, url=call["url"]),
            )
            self.assertIn(rc, (0, 1))
            self.assertEqual(calls, [])
            self.assertIn("ok", result)
            self.assertTrue(result.get("refused") or result["ok"] is False)

    def test_private_auth_code_file_rejects_unsafe_state(self) -> None:
        cases: list[tuple[str, Path]] = []
        public_file = self.tmp / "public-code.txt"
        public_file.write_text("secret\n", encoding="utf-8")
        public_file.chmod(0o644)
        cases.append(("public", public_file))
        multiline_file = self.tmp / "multiline-code.txt"
        multiline_file.write_text("first\nsecond\n", encoding="utf-8")
        multiline_file.chmod(0o600)
        cases.append(("multiline", multiline_file))
        empty_file = self.tmp / "empty-code.txt"
        empty_file.write_text(" \n", encoding="utf-8")
        empty_file.chmod(0o600)
        cases.append(("empty", empty_file))
        directory = self.tmp / "code-directory"
        directory.mkdir(mode=0o700)
        cases.append(("directory", directory))
        invalid_utf8 = self.tmp / "invalid-utf8-code.txt"
        invalid_utf8.write_bytes(b"\xff\xfe")
        invalid_utf8.chmod(0o600)
        cases.append(("invalid_utf8", invalid_utf8))

        for case_name, path in cases:
            rc, result, calls = _run_cli(
                [
                    "--env-file",
                    str(_auth_env(self.tmp)),
                    "--output",
                    "json",
                    "domains",
                    "submit-transfer-code",
                    "--domain-name",
                    "example.com",
                    "--auth-code-file",
                    str(path),
                ],
                lambda call, name=case_name: FakeResponse(
                    200, {"unexpected": name}, url=call["url"]
                ),
            )
            self.assertEqual(rc, 1)
            self.assertEqual(result["ok"], False)
            self.assertEqual(result["error_type"], "ValidationError")
            self.assertEqual(calls, [])
            self.assertNotIn("secret", json.dumps(result))
            if case_name == "invalid_utf8":
                self.assertEqual(result["error"], "Unable to read --auth-code-file")

    def test_plan_in_parent_must_be_private(self) -> None:
        args = _operation_args("domains set-sale-price")
        _, payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "private.plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"unexpected": True}, url=call["url"]),
        )
        private_plan = Path(payload["plan_path"])
        public_dir = self.tmp / "public-plan-parent"
        public_dir.mkdir(mode=0o755)
        public_plan = public_dir / "copied.plan.json"
        public_plan.write_bytes(private_plan.read_bytes())
        public_plan.chmod(0o600)
        rc, result, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(public_plan),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"unexpected": True}, url=call["url"]),
        )
        self.assertEqual(rc, 0)
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["refused"], True)
        self.assertEqual(calls, [])

    def test_custom_plan_parent_must_be_private(self) -> None:
        public_dir = self.tmp / "public-state"
        public_dir.mkdir(mode=0o755)
        env_file = _auth_env(public_dir)
        plan_path = public_dir / "unsafe.plan.json"
        rc, result, calls = _run_cli(
            [
                "--env-file",
                str(env_file),
                "--output",
                "json",
                "--plan-out",
                str(plan_path),
                "domains",
                "set-sale-price",
                "--domain-name",
                "example.com",
                "--sale-price",
                "42",
            ],
            lambda call: FakeResponse(200, {"unexpected": True}, url=call["url"]),
        )
        self.assertEqual(rc, 1)
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["error_type"], "StateError")
        self.assertEqual(calls, [])
        self.assertFalse(plan_path.exists())

    def test_atomic_plan_write_oserror_is_one_safe_json_result(self) -> None:
        plan_path = self.tmp / "atomic.plan.json"
        with patch("sav_domain_api.state.os.replace", side_effect=OSError("private detail")):
            rc, result, calls = _run_cli(
                [
                    "--env-file",
                    str(_auth_env(self.tmp)),
                    "--output",
                    "json",
                    "--plan-out",
                    str(plan_path),
                    "domains",
                    "set-sale-price",
                    "--domain-name",
                    "example.com",
                    "--sale-price",
                    "42",
                ],
                lambda call: FakeResponse(200, {"unexpected": True}, url=call["url"]),
            )
        self.assertEqual(rc, 1)
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["error_type"], "StateError")
        self.assertEqual(calls, [])
        self.assertFalse(plan_path.exists())
        self.assertNotIn("private detail", json.dumps(result))

    def test_read_and_apply_set_redirect_control_and_reject_http_302(self) -> None:
        read_rc, read_payload, read_calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "domains",
                "active",
            ],
            lambda call: FakeResponse(
                302,
                {"status": "moved"},
                url=call["url"],
            ),
        )
        self.assertEqual(read_calls[0]["url"], "https://api.sav.com/domains_api_v1/get_active_domains_in_account")
        self.assertEqual(read_calls[0].get("allow_redirects"), False)
        self.assertEqual(read_rc, 1)
        self.assertEqual(read_payload["ok"], False)
        self.assertEqual(read_payload["error_type"], "ValidationError")

        dry_args = _operation_args("domains set-sale-price")
        dry, dry_payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "redirection.plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(dry_args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertEqual(dry, 0)

        apply_rc, apply_payload, apply_calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(dry_payload["plan_path"]),
                "--receipt-out",
                str(self.tmp / "redirected.receipt.json"),
                "domains",
                "set-sale-price",
                *_flag_args(_operation_args("domains set-sale-price")),
            ],
            lambda call: FakeResponse(
                302,
                {"status": "moved"},
                url=call["url"],
            ),
        )
        self.assertEqual(apply_calls[0]["url"], "https://api.sav.com/domains_api_v1/update_domain_for_sale_price")
        self.assertEqual(apply_calls[0].get("allow_redirects"), False)
        self.assertEqual(apply_rc, 1)
        self.assertEqual(apply_payload["ok"], False)
        self.assertEqual(apply_payload["error_type"], "ValidationError")
        self.assertEqual(apply_payload["retry"], "do-not-retry")
        self.assertTrue(apply_payload["provider_received"])
        self.assertTrue(apply_payload["provider_response_received"])
        self.assertFalse(apply_payload["durable_state_verified"])
        self.assertTrue(apply_payload["receipt_written"])
        self.assertEqual(
            apply_payload["receipt"]["provider_response_only"],
            apply_payload["provider_response_received"],
        )
        self.assertEqual(apply_payload["receipt"]["outcome"], "failure")
        self.assertNotIn("durable", apply_payload)

    def test_redaction_keeps_domain_and_nameserver_identifiers(self) -> None:
        rc, dry_payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "nameserver-plan.json"),
                "domains",
                "set-nameservers",
                "--domain-name",
                "Example.Com",
                "--ns-1",
                "NS1.Example.NET",
                "--ns-2",
                "NS2.Example.NET",
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertEqual(rc, 0)
        plan_dump = json.dumps(dry_payload["plan"])
        self.assertIn("example.com", plan_dump)
        self.assertIn("ns1.example.net", plan_dump)
        self.assertIn("ns2.example.net", plan_dump)
        self.assertIn("domain_name", plan_dump)

        _, apply_payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--apply",
                "--yes",
                "--ack-no-snapshot",
                "--ack-high-risk",
                "--plan-in",
                str(dry_payload["plan_path"]),
                "--receipt-out",
                str(self.tmp / "redaction.receipt.json"),
                "domains",
                "set-nameservers",
                "--domain-name",
                "example.com",
                "--ns-1",
                "ns1.example.net",
                "--ns-2",
                "ns2.example.net",
            ],
            lambda call: FakeResponse(
                200,
                {
                    "status": "ok",
                    "statusMeta": "200",
                    "domain": "example.com",
                    "domainName": "example.com",
                    "domain_name": "example.com",
                    "nameserver": "ns1.example.net",
                    "nameservers": ["ns1.example.net", "ns2.example.net"],
                    "contact": "contact@example.com",
                    "auth_code": "abc-xyz",
                    "authCode": "abc-xyz",
                    "auth-code": "abc-xyz",
                    "whois": "Jane Example",
                    "whoisEmail": "private@example.com",
                },
                url=call["url"],
            ),
        )
        self.assertEqual(apply_payload["ok"], True)
        receipt_response = json.dumps(apply_payload["receipt"]["response"])
        self.assertNotIn("abc-xyz", receipt_response)
        self.assertNotIn("Jane Example", receipt_response)
        self.assertNotIn("private@example.com", receipt_response)
        self.assertNotIn("contact@example.com", receipt_response)
        self.assertIn("example.com", receipt_response)
        self.assertIn("ns1.example.net", receipt_response)
        self.assertIn("ns2.example.net", receipt_response)
        self.assertIn("<redacted>", receipt_response)

    def test_active_domain_read_keeps_useful_identifiers_and_redacts_contacts(self) -> None:
        rc, payload, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "domains",
                "active",
            ],
            lambda call: FakeResponse(
                200,
                [
                    {
                        "domain": "example.com",
                        "domain_name": "example.net",
                        "domainName": "example.org",
                        "nameservers": ["ns1.example.net", "ns2.example.net"],
                        "emailAddress": "private@example.com",
                    }
                ],
                url=call["url"],
            ),
        )
        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 1)
        response_text = json.dumps(payload["read"]["response"])
        self.assertIn("example.com", response_text)
        self.assertIn("example.net", response_text)
        self.assertIn("example.org", response_text)
        self.assertIn("ns1.example.net", response_text)
        self.assertNotIn("private@example.com", response_text)
        self.assertIn("<redacted>", response_text)

    def test_apply_with_request_exception_records_unknown_outcome_and_pre_transport_receipt(self) -> None:
        args = _operation_args("domains set-sale-price")
        _, dry_payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "exception.plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )

        receipt_path = self.tmp / "request-exception.receipt.json"
        with patch(
            "sav_domain_api.cli.HttpClient.get",
            side_effect=ToolError("SAV request failed before a response was received"),
        ):
            rc, payload, calls = _run_cli(
                [
                    "--env-file",
                    str(_auth_env(self.tmp)),
                    "--output",
                    "json",
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-high-risk",
                    "--plan-in",
                    str(dry_payload["plan_path"]),
                    "--receipt-out",
                    str(receipt_path),
                    "domains",
                    "set-sale-price",
                    "--domain-name",
                    "example.com",
                    "--sale-price",
                    "42",
                ],
                lambda call: FakeResponse(200, {"unexpected": "should not run"}, url=call["url"]),
            )
        self.assertEqual(rc, 1)
        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["error_type"], "ToolError")
        self.assertEqual(payload["error"], "SAV request failed before a response was received")
        self.assertFalse(payload["durable_state_verified"])
        self.assertIn("provider_received", payload)
        self.assertFalse(payload["provider_received"])
        self.assertIn("outcome", payload)
        self.assertEqual(payload["outcome"], "unknown")
        self.assertNotIn("durable", payload)
        self.assertEqual(
            payload["receipt"]["provider_response_only"],
            payload["provider_response_received"],
        )
        self.assertIn("retry", payload)
        self.assertEqual(payload["retry"], "do-not-retry")
        self.assertIn("receipt_written", payload)
        self.assertTrue(payload["receipt_written"])
        self.assertTrue(receipt_path.is_file())
        saved_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertTrue(saved_receipt["receipt"]["request_attempted"])
        self.assertFalse(saved_receipt["receipt"]["provider_response_received"])
        self.assertFalse(saved_receipt["receipt"]["provider_response_only"])
        self.assertEqual(saved_receipt["receipt"]["outcome"], "unknown")
        self.assertEqual(
            payload["receipt_written"],
            saved_receipt["receipt"]["request_attempted"] is True,
        )
        self.assertEqual(calls, [])

    def test_provider_response_then_receipt_write_failure_keeps_account_state_unverified(self) -> None:
        args = _operation_args("domains set-sale-price")
        _, dry_payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "receipt-failure.plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        receipt_path = self.tmp / "provider-outcome.receipt.json"
        real_write = write_private_json
        write_count = 0

        def _fail_final_write(*args, **kwargs):
            nonlocal write_count
            write_count += 1
            if write_count == 1:
                return real_write(*args, **kwargs)
            raise StateError("receipt write failed")

        with patch("sav_domain_api.cli.write_private_json", side_effect=_fail_final_write):
            rc, payload, calls = _run_cli(
                [
                    "--env-file",
                    str(_auth_env(self.tmp)),
                    "--output",
                    "json",
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-high-risk",
                    "--plan-in",
                    str(dry_payload["plan_path"]),
                    "--receipt-out",
                    str(receipt_path),
                    "domains",
                    "set-sale-price",
                    "--domain-name",
                    "example.com",
                    "--sale-price",
                    "42",
                ],
                lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
            )
        self.assertEqual(rc, 1)
        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["error_type"], "StateError")
        self.assertIn("provider_received", payload)
        self.assertTrue(payload["provider_received"])
        self.assertIn("provider_status", payload)
        self.assertEqual(payload["provider_status"], 200)
        self.assertNotIn("durable", payload)
        self.assertFalse(payload["durable_state_verified"])
        self.assertEqual(payload["receipt"]["provider_response_only"], payload["provider_response_received"])
        self.assertEqual(payload["outcome"], "provider_accepted")
        self.assertIn("receipt_written", payload)
        self.assertFalse(payload["receipt_written"])
        self.assertIn("retry", payload)
        self.assertEqual(payload["retry"], "do-not-retry")
        self.assertEqual(len(calls), 1)
        saved_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(saved_receipt["receipt"]["outcome"], "unknown")
        self.assertEqual(saved_receipt["receipt"]["request_attempted"], "unknown")
        self.assertFalse(saved_receipt["receipt"]["provider_response_received"])
        self.assertFalse(saved_receipt["receipt"]["provider_response_only"])

    def test_pre_transport_receipt_failure_stops_before_network(self) -> None:
        args = _operation_args("domains set-sale-price")
        _, dry_payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "pre-transport.plan.json"),
                "domains",
                "set-sale-price",
                *_flag_args(args),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        with patch(
            "sav_domain_api.cli.write_private_json",
            side_effect=StateError("receipt path unavailable"),
        ):
            rc, payload, calls = _run_cli(
                [
                    "--env-file",
                    str(_auth_env(self.tmp)),
                    "--output",
                    "json",
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-high-risk",
                    "--plan-in",
                    str(dry_payload["plan_path"]),
                    "--receipt-out",
                    str(self.tmp / "blocked.receipt.json"),
                    "domains",
                    "set-sale-price",
                    *_flag_args(args),
                ],
                lambda call: FakeResponse(200, {"unexpected": True}, url=call["url"]),
            )
        self.assertEqual(rc, 1)
        self.assertEqual(calls, [])
        self.assertFalse(payload["provider_response_received"])
        self.assertFalse(payload["durable_state_verified"])
        self.assertFalse(payload["receipt_written"])
        self.assertNotIn("durable", payload)
        self.assertNotIn("applied", payload)
        self.assertIn("retry", payload)
        self.assertEqual(payload["retry"], "fix-receipt-path-before-retry")
        self.assertNotIn("receipt", payload)
        self.assertEqual(payload["outcome"], "not_attempted")
        self.assertFalse((self.tmp / "blocked.receipt.json").exists())

    def test_timeouts_must_be_finite_positive(self) -> None:
        for raw in ("NaN", "Infinity", "-Infinity", "0", "-1", "not-a-number"):
            env_file = self.tmp / f"timeout-{raw.replace('/', '-')}.env"
            env_file.write_text(
                f"SAV_API_KEY=fake-sav-test-key\nSAV_TIMEOUT_S={raw}\n",
                encoding="utf-8",
            )
            rc, payload, calls = _run_cli(
                [
                    "--env-file",
                    str(env_file),
                    "--output",
                    "json",
                    "domains",
                    "active",
                ],
                lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
            )
            self.assertEqual(rc, 1, raw)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(calls, [])

            rc2, payload2, calls2 = _run_cli(
                [
                    "--env-file",
                    str(_auth_env(self.tmp)),
                    "--output",
                    "json",
                    "--timeout-s",
                    raw,
                    "domains",
                    "active",
                ],
                lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
            )
            self.assertEqual(rc2, 1, raw)
            self.assertEqual(payload2["error_type"], "ValidationError")
            self.assertEqual(calls2, [])

    def test_invalid_domain_and_nameserver_inputs_are_rejected_without_transport(self) -> None:
        too_long_label = "a" * 64 + ".com"
        too_long_host = ".".join(["a" * 63] * 4) + ".com"
        for invalid_domain in (
            "bad@@example",
            "a..com",
            "a.-bad.com",
            "a.bad-.com",
            too_long_label,
            too_long_host,
        ):
            invalid_rc, invalid_payload, calls = _run_cli(
                [
                    "--env-file",
                    str(_auth_env(self.tmp)),
                    "--output",
                    "json",
                    "domains",
                    "set-sale-price",
                    "--domain-name",
                    invalid_domain,
                    "--sale-price",
                    "42",
                ],
                lambda call: (_ for _ in ()).throw(
                    AssertionError("invalid domain should fail before network")
                ),
            )
            self.assertEqual(invalid_rc, 1, invalid_domain)
            self.assertEqual(invalid_payload["error_type"], "ValidationError")
            self.assertEqual(calls, [])

        _, dry_payload, _ = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "nameserver.plan.json"),
                "domains",
                "set-nameservers",
                "--domain-name",
                "example.com",
                "--ns-1",
                "ns1.example.net",
                "--ns-2",
                "ns2.example.net",
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )

        for invalid_nameserver in (
            "a..net",
            "a.-bad.net",
            "a.bad-.net",
            too_long_label,
            too_long_host,
        ):
            _, apply_payload, apply_calls = _run_cli(
                [
                    "--env-file",
                    str(_auth_env(self.tmp)),
                    "--output",
                    "json",
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-high-risk",
                    "--plan-in",
                    str(dry_payload["plan_path"]),
                    "domains",
                    "set-nameservers",
                    "--domain-name",
                    "example.com",
                    "--ns-1",
                    invalid_nameserver,
                    "--ns-2",
                    "ns2.example.net",
                ],
                lambda call: (_ for _ in ()).throw(
                    AssertionError("invalid nameserver should fail before network")
                ),
            )
            self.assertEqual(apply_payload["ok"], False, invalid_nameserver)
            self.assertEqual(apply_payload["error_type"], "ValidationError")
            self.assertEqual(apply_calls, [])

    def test_non_json_plan_out_is_rejected_before_state(self) -> None:
        rc, payload, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "--plan-out",
                str(self.tmp / "bad-plan.txt"),
                "domains",
                "set-sale-price",
                "--domain-name",
                "example.com",
                "--sale-price",
                "42",
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertEqual(rc, 1)
        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertEqual(calls, [])
        self.assertFalse((self.tmp / ".state").exists())

    def test_auth_code_file_requires_private_parent_and_regular_file(self) -> None:
        public_parent = self.tmp / "public-parent"
        public_parent.mkdir(mode=0o755)
        public_code = public_parent / "code.txt"
        public_code.write_text("transfer-secret\n", encoding="utf-8")
        public_code.chmod(0o600)
        rc, payload, calls = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "domains",
                "submit-transfer-code",
                "--domain-name",
                "example.com",
                "--auth-code-file",
                str(public_code),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertEqual(rc, 1)
        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertEqual(calls, [])

        symlink_parent = self.tmp / "symlink-parent"
        symlink_parent.mkdir(mode=0o700)
        symlink_target = self.tmp / "symlink-target.txt"
        symlink_target.write_text("transfer-secret\n", encoding="utf-8")
        symlink_code = symlink_parent / "code-link.txt"
        symlink_code.symlink_to(symlink_target)
        rc2, payload2, calls2 = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "domains",
                "submit-transfer-code",
                "--domain-name",
                "example.com",
                "--auth-code-file",
                str(symlink_code),
            ],
            lambda call: FakeResponse(200, {"ok": True}, url=call["url"]),
        )
        self.assertEqual(rc2, 1)
        self.assertEqual(payload2["ok"], False)
        self.assertEqual(payload2["error_type"], "ValidationError")
        self.assertEqual(calls2, [])

        real_secret_dir = self.tmp / "real-secret-parent"
        real_secret_dir.mkdir(mode=0o700)
        parent_link = self.tmp / "linked-secret-parent"
        parent_link.symlink_to(real_secret_dir, target_is_directory=True)
        linked_code = parent_link / "code.txt"
        (real_secret_dir / "code.txt").write_text("transfer-secret\n", encoding="utf-8")
        (real_secret_dir / "code.txt").chmod(0o600)
        rc3, payload3, calls3 = _run_cli(
            [
                "--env-file",
                str(_auth_env(self.tmp)),
                "--output",
                "json",
                "domains",
                "submit-transfer-code",
                "--domain-name",
                "example.com",
                "--auth-code-file",
                str(linked_code),
            ],
            lambda call: FakeResponse(200, {"unexpected": True}, url=call["url"]),
        )
        self.assertEqual(rc3, 1)
        self.assertEqual(payload3["error_type"], "ValidationError")
        self.assertEqual(calls3, [])


if __name__ == "__main__":
    unittest.main()
