from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import stat
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import TestCase
from unittest import main as unittest_main
from unittest.mock import patch

from qwayk_porkbun_safe_agent_cli import cli
from qwayk_porkbun_safe_agent_cli.http import TransportResponse


class FakeTransport:
    def __init__(self, responses: list[TransportResponse] | None = None):
        self.responses = list(responses or [])
        self.calls: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | list[Any] | None = None,
        timeout_s: float = 30.0,
    ) -> TransportResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers or {},
                "params": dict(params or {}),
                "json_body": json_body,
                "timeout_s": timeout_s,
            }
        )
        if not self.responses:
            raise AssertionError("Unexpected transport request")
        return self.responses.pop(0)


class RaisingTransport(FakeTransport):
    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | list[Any] | None = None,
        timeout_s: float = 30.0,
    ) -> TransportResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers or {},
                "params": dict(params or {}),
                "json_body": json_body,
                "timeout_s": timeout_s,
            }
        )
        raise RuntimeError(self.message)



def _json_response(payload: dict[str, Any], status: int = 200, headers: dict[str, str] | None = None, url: str = "https://api.porkbun.com/api/json/v3") -> TransportResponse:
    return TransportResponse(
        status=status,
        headers={str(k).lower(): str(v) for k, v in (headers or {}).items()},
        body=json.dumps(payload).encode("utf-8"),
        url=url,
    )


def _run_cli(argv: list[str], transport: FakeTransport) -> tuple[int, dict[str, Any]]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv, transport=transport)
    output = buf.getvalue().strip()
    try:
        payload = json.loads(output) if output else {}
    except json.JSONDecodeError as exc:  # noqa: BLE001
        raise AssertionError(f"CLI output is not JSON: {output!r}") from exc
    return code, payload


def _env_file(path: Path, host: str = "default", api_key: str = "API_KEY", secret: str = "SECRET") -> str:
    path.write_text(
        "\n".join(
            [
                f"PORKBUN_API_HOST={host}",
                f"PORKBUN_API_KEY={api_key}",
                f"PORKBUN_SECRET_API_KEY={secret}",
                "PORKBUN_TIMEOUT_S=30",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return str(path)


@contextmanager
def _working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _recompute_public_plan_hash(plan: dict[str, Any]) -> None:
    unsigned = {
        key: value
        for key, value in plan.items()
        if key not in {"plan_hash", "plan_signature"}
    }
    plan["plan_hash"] = hashlib.sha256(
        json.dumps(unsigned, sort_keys=True).encode("utf-8")
    ).hexdigest()


class TestPorkbunRuntime(TestCase):
    def test_inventory_count_and_fixed_commands(self) -> None:
        resource = cli._resource_inventory()
        self.assertEqual(resource["summary"]["totals"]["operation_count"], 66)
        self.assertEqual(len(cli._OPERATION_MAP), 66)

        parser = cli.build_parser()
        sub_action = next(
            act for act in parser._actions if isinstance(act, argparse._SubParsersAction) and act.dest == "_cmd_group"
        )
        groups = set(sub_action.choices)
        expected = {"onboarding", "auth", "operations", "utility", "pricing", "api-key", "domain", "dns", "ssl", "email-hosting", "marketplace", "account", "webhooks"}
        self.assertTrue(expected.issubset(groups))

    def test_resources_and_spec_parity(self) -> None:
        pkg_spec = Path(__file__).resolve().parent.parent / "src" / "qwayk_porkbun_safe_agent_cli" / "resources" / "porkbun-openapi-v3.9.json"
        vendor_spec = Path(__file__).resolve().parent.parent / "vendor" / "porkbun-openapi-v3.9.json"
        self.assertEqual(pkg_spec.read_bytes(), vendor_spec.read_bytes())

        pkg_inventory = Path(__file__).resolve().parent.parent / "src" / "qwayk_porkbun_safe_agent_cli" / "resources" / "operation_inventory.json"
        docs_inventory = Path(__file__).resolve().parent.parent / "docs" / "operation_inventory.json"
        self.assertEqual(json.loads(pkg_inventory.read_text()), json.loads(docs_inventory.read_text()))

    def test_config_rejects_unknown_host(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(td) / "bad.env"
            env.write_text("PORKBUN_API_HOST=bad\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                cli.load_config(str(env))

    def test_input_is_json_file_not_inline(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            input_path = Path(td) / "payload.json"
            input_path.write_text('{"yourIp":"127.0.0.1"}', encoding="utf-8")

            transport = FakeTransport([_json_response({"status": "SUCCESS"})])
            code, _ = _run_cli(
                ["--env-file", str(env), "utility", "ping", "--input", str(input_path)],
                transport=transport,
            )
            self.assertEqual(code, 0)

            transport = FakeTransport()
            code, payload = _run_cli(
                ["--env-file", str(env), "utility", "ping", "--input", "{\"inline\": true}"],
                transport=transport,
            )
            self.assertEqual(code, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_public_calls_send_no_auth_headers(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env", api_key="", secret=""))
            transport = FakeTransport([_json_response({"status": "SUCCESS", "yourIp": "1.2.3.4"})])
            code, _ = _run_cli(
                ["--env-file", str(env), "utility", "get-ip"],
                transport=transport,
            )
            self.assertEqual(code, 0)
            headers = transport.calls[0]["headers"]
            self.assertIn("User-Agent", headers)
            self.assertNotIn("X-API-Key", headers)
            self.assertNotIn("X-Secret-API-Key", headers)

    def test_authenticated_calls_send_credentials(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            transport = FakeTransport(
                [
                    _json_response({"status": "SUCCESS", "domain": "example.com"}),
                ]
            )
            code, _ = _run_cli(
                ["--env-file", str(env), "domain", "get-domain", "--domain", "example.com"],
                transport=transport,
            )
            self.assertEqual(code, 0)
            headers = transport.calls[0]["headers"]
            self.assertEqual(headers.get("X-API-Key"), "API_KEY")
            self.assertEqual(headers.get("X-Secret-API-Key"), "SECRET")

    def test_auth_check_sends_configured_credentials_to_optional_auth_ping(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            transport = FakeTransport(
                [_json_response({"status": "SUCCESS", "credentialsValid": True})]
            )
            code, payload = _run_cli(
                ["--env-file", str(env), "auth", "check"],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["authenticated"], True)
            self.assertEqual(transport.calls[0]["headers"]["X-API-Key"], "API_KEY")
            self.assertEqual(transport.calls[0]["headers"]["X-Secret-API-Key"], "SECRET")

    def test_resolve_request_schema_handles_ref_and_allof(self) -> None:
        op = cli._OPERATION_MAP["emailSetPassword"]
        payload = {"emailAddress": "a@b.com", "password": "secret"}
        self.assertEqual(cli._validate_body(op, payload), payload)

        ping_op = cli._OPERATION_MAP["domainCheckDomain"]
        self.assertIn("domain", ping_op.parameters[0].get("name"))

    def test_snapshot_uses_payload_for_snapshot_targeting(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            body = Path(td) / "payload.json"
            body.write_text('{"id": 77}', encoding="utf-8")

            transport = FakeTransport(
                [
                    _json_response({"status": "SUCCESS", "id": 77}),
                    _json_response({"status": "SUCCESS"}),
                ]
            )
            code, payload_out = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-delete",
                    "--input",
                    str(body),
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertTrue(payload_out["plan"]["dry_run"])
            self.assertTrue(transport.calls[0]["url"].endswith("/webhook/get/77"))
            plan_path = Path(payload_out["plan"]["plan_out"])
            self.assertTrue(plan_path.exists())

    def test_apply_readback_targets_body_id(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            body = Path(td) / "payload.json"
            body.write_text('{"id": 55, "url": "https://example.com/callback"}', encoding="utf-8")
            plan = Path(td) / "plan.json"

            transport = FakeTransport(
                [
                    _json_response({"status": "SUCCESS", "id": 55}),
                    _json_response({"status": "SUCCESS"}),
                ]
            )
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-update",
                    "--input",
                    str(body),
                    "--plan-out",
                    str(plan),
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertTrue(plan.exists())

            secret_out = Path(td) / "result.json"
            transport = FakeTransport(
                [
                    _json_response({"status": "SUCCESS", "id": 55}),
                    _json_response({"status": "SUCCESS", "id": 55, "url": "https://example.com/callback"}),
                ]
            )
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-update",
                    "--input",
                    str(body),
                    "--plan-in",
                    str(plan),
                    "--apply",
                    "--ack-secret",
                    "--yes",
                    "--secret-out",
                    str(secret_out),
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload.get("ok"), True)
            self.assertTrue(transport.calls[-1]["url"].endswith("/webhook/get/55"))

    def test_plan_expiry_and_target_input_tamper_checks(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            body = Path(td) / "payload.json"
            body.write_text('{"id": 44, "url": "https://example.com/callback"}', encoding="utf-8")
            plan = Path(td) / "plan.json"

            transport = FakeTransport(
                [
                    _json_response({"status": "SUCCESS", "id": 44}),
                    _json_response({"status": "SUCCESS"}),
                ]
            )
            code, _ = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-update",
                    "--input",
                    str(body),
                    "--plan-out",
                    str(plan),
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)

            original = json.loads(plan.read_text(encoding="utf-8"))
            expired = json.loads(json.dumps(original))
            expired["expires_at_utc"] = "2000-01-01T00:00:00Z"
            cli._sign_plan(expired, cli._load_plan_signing_key(create=False))
            plan.write_text(json.dumps(expired) + "\n", encoding="utf-8")

            secret_out = Path(td) / "result.json"
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-update",
                    "--input",
                    str(body),
                    "--plan-in",
                    str(plan),
                    "--apply",
                    "--ack-secret",
                    "--yes",
                    "--secret-out",
                    str(secret_out),
                ],
                transport=FakeTransport(),
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["refused"], True)
            self.assertEqual(payload["reasons"], ["Plan has expired"])

            mismatched = json.loads(json.dumps(original))
            mismatched["input_sha256"] = "x"
            cli._sign_plan(mismatched, cli._load_plan_signing_key(create=False))
            plan.write_text(json.dumps(mismatched) + "\n", encoding="utf-8")
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-update",
                    "--input",
                    str(body),
                    "--plan-in",
                    str(plan),
                    "--apply",
                    "--ack-secret",
                    "--yes",
                    "--secret-out",
                    str(secret_out),
                ],
                transport=FakeTransport(),
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["refused"], True)
            self.assertEqual(payload["reasons"], ["Plan input hash does not match this command input"])

    def test_billable_apply_reruns_dry_run(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            body = Path(td) / "payload.json"
            body.write_text('{"cost": 1000}', encoding="utf-8")
            plan = Path(td) / "plan.json"

            transport = FakeTransport(
                [
                    _json_response({"status": "SUCCESS", "domain": "example.com"}),
                    _json_response({"status": "SUCCESS", "cost": 10}),
                    _json_response({"status": "SUCCESS", "cost": 10}),
                ]
            )
            code, _ = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "domain",
                    "domain-renew",
                    "--domain",
                    "example.com",
                    "--input",
                    str(body),
                    "--plan-out",
                    str(plan),
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)

            apply_transport = FakeTransport(
                [
                    _json_response({"status": "SUCCESS", "cost": 10}),
                    _json_response({"status": "SUCCESS", "cost": 10}),
                    _json_response({"status": "SUCCESS", "domain": "example.com"}),
                ]
            )
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "domain",
                    "domain-renew",
                    "--domain",
                    "example.com",
                    "--input",
                    str(body),
                    "--plan-in",
                    str(plan),
                    "--apply",
                    "--ack-spend",
                    "--yes",
                ],
                transport=apply_transport,
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["ok"], True)
            self.assertTrue(apply_transport.calls[0]["json_body"].get("dryRun"))

            # plan should not be considered tampered when target/input unchanged
            plan_data = json.loads(plan.read_text(encoding="utf-8"))
            self.assertEqual(plan_data["plan_hash"], plan_data["plan_hash"])

    def test_plan_is_hmac_signed_with_private_state_from_creation(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            body = root / "payload.json"
            body.write_text('{"url": "https://example.com/callback"}', encoding="utf-8")
            old_umask = os.umask(0)
            try:
                with _working_directory(root):
                    code, payload = _run_cli(
                        [
                            "--env-file",
                            str(env),
                            "webhooks",
                            "webhook-create",
                            "--input",
                            str(body),
                        ],
                        transport=FakeTransport(),
                    )
            finally:
                os.umask(old_umask)

            self.assertEqual(code, 0)
            plan_path = Path(payload["plan"]["plan_out"])
            if not plan_path.is_absolute():
                plan_path = root / plan_path
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            signing_key = root / ".state" / "plan-signing.key"
            self.assertIn("plan_signature", plan)
            self.assertTrue(signing_key.is_file())
            self.assertEqual(stat.S_IMODE((root / ".state").stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((root / ".state" / "plans").stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(signing_key.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(plan_path.stat().st_mode), 0o600)

    def test_recomputed_hash_cannot_bypass_dynamic_no_snapshot_ack(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            body = root / "payload.json"
            body.write_text('{"id": 42}', encoding="utf-8")
            plan_path = root / "plan.json"
            with _working_directory(root):
                code, _ = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "webhooks",
                        "webhook-delete",
                        "--input",
                        str(body),
                        "--plan-out",
                        str(plan_path),
                    ],
                    transport=FakeTransport(
                        [_json_response({"status": "ERROR", "code": "NOT_FOUND"}, status=404)]
                    ),
                )
                self.assertEqual(code, 0)

                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                plan["snapshot"]["requires_no_snapshot_ack"] = False
                _recompute_public_plan_hash(plan)
                plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")

                apply_transport = FakeTransport(
                    [
                        _json_response({"status": "SUCCESS"}),
                        _json_response({"status": "SUCCESS"}),
                    ]
                )
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "webhooks",
                        "webhook-delete",
                        "--input",
                        str(body),
                        "--plan-in",
                        str(plan_path),
                        "--apply",
                        "--ack-destructive",
                        "--yes",
                    ],
                    transport=apply_transport,
                )

            self.assertEqual(code, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("signature", payload["reasons"][0].lower())
            self.assertEqual(apply_transport.calls, [])

    def test_hmac_rejects_expiry_and_idempotency_edits(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            body = root / "payload.json"
            body.write_text('{"url": "https://example.com/callback"}', encoding="utf-8")
            plan_path = root / "plan.json"
            with _working_directory(root):
                code, _ = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "webhooks",
                        "webhook-create",
                        "--input",
                        str(body),
                        "--plan-out",
                        str(plan_path),
                    ],
                    transport=FakeTransport(),
                )
                self.assertEqual(code, 0)
                original = json.loads(plan_path.read_text(encoding="utf-8"))

                for field, value in (
                    ("expires_at_utc", "2099-01-01T00:00:00Z"),
                    ("idempotency_key", "0" * 32),
                ):
                    with self.subTest(field=field):
                        forged = json.loads(json.dumps(original))
                        forged[field] = value
                        _recompute_public_plan_hash(forged)
                        plan_path.write_text(json.dumps(forged) + "\n", encoding="utf-8")
                        transport = FakeTransport(
                            [
                                _json_response({"status": "SUCCESS", "id": 42, "secret": "provider-secret"}),
                                _json_response({"status": "SUCCESS", "id": 42}),
                            ]
                        )
                        code, payload = _run_cli(
                            [
                                "--env-file",
                                str(env),
                                "webhooks",
                                "webhook-create",
                                "--input",
                                str(body),
                                "--plan-in",
                                str(plan_path),
                                "--apply",
                                "--ack-secret",
                                "--ack-no-snapshot",
                                "--yes",
                                "--secret-out",
                                str(root / f"{field}.json"),
                            ],
                            transport=transport,
                        )
                        self.assertEqual(code, 0)
                        self.assertTrue(payload.get("refused", False), payload)
                        self.assertIn("signature", payload["reasons"][0].lower())
                        self.assertEqual(transport.calls, [])

    def test_missing_or_invalid_plan_signature_and_key_fail_closed(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            body = root / "payload.json"
            body.write_text('{"status": "on"}', encoding="utf-8")
            plan_path = root / "plan.json"
            with _working_directory(root):
                code, _ = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "domain",
                        "domain-update-auto-renew",
                        "--domain",
                        "example.com",
                        "--input",
                        str(body),
                        "--plan-out",
                        str(plan_path),
                    ],
                    transport=FakeTransport(
                        [_json_response({"status": "SUCCESS", "domain": "example.com"})]
                    ),
                )
                self.assertEqual(code, 0)
                original = json.loads(plan_path.read_text(encoding="utf-8"))
                key_path = root / ".state" / "plan-signing.key"

                variants: list[tuple[str, dict[str, Any], bytes | None]] = []
                missing_signature = json.loads(json.dumps(original))
                missing_signature.pop("plan_signature", None)
                variants.append(("missing signature", missing_signature, key_path.read_bytes() if key_path.exists() else None))
                invalid_signature = json.loads(json.dumps(original))
                invalid_signature["plan_signature"] = "0" * 64
                variants.append(("invalid signature", invalid_signature, key_path.read_bytes() if key_path.exists() else None))
                variants.append(("missing key", original, None))
                variants.append(("invalid key", original, b"short"))

                for label, candidate, key_bytes in variants:
                    with self.subTest(label=label):
                        plan_path.write_text(json.dumps(candidate) + "\n", encoding="utf-8")
                        if key_bytes is None:
                            key_path.unlink(missing_ok=True)
                        else:
                            key_path.parent.mkdir(parents=True, exist_ok=True)
                            key_path.write_bytes(key_bytes)
                            key_path.chmod(0o600)
                        transport = FakeTransport()
                        code, payload = _run_cli(
                            [
                                "--env-file",
                                str(env),
                                "domain",
                                "domain-update-auto-renew",
                                "--domain",
                                "example.com",
                                "--input",
                                str(body),
                                "--plan-in",
                                str(plan_path),
                                "--apply",
                                "--yes",
                            ],
                            transport=transport,
                        )
                        self.assertEqual(code, 0)
                        self.assertTrue(payload["refused"])
                        self.assertEqual(transport.calls, [])

    def test_billable_apply_refuses_missing_planned_or_fresh_cost(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            body = root / "payload.json"
            body.write_text('{"cost": 1000}', encoding="utf-8")
            plan_path = root / "plan.json"
            with _working_directory(root):
                code, _ = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "domain",
                        "domain-renew",
                        "--domain",
                        "example.com",
                        "--input",
                        str(body),
                        "--plan-out",
                        str(plan_path),
                    ],
                    transport=FakeTransport(
                        [
                            _json_response({"status": "SUCCESS", "domain": "example.com"}),
                            _json_response({"status": "SUCCESS", "cost": 10}),
                        ]
                    ),
                )
                self.assertEqual(code, 0)
                original = json.loads(plan_path.read_text(encoding="utf-8"))

                missing_planned = json.loads(json.dumps(original))
                missing_planned["dry_run"]["cost_signature"] = ""
                cli._sign_plan(
                    missing_planned,
                    cli._load_plan_signing_key(create=False),
                )
                plan_path.write_text(json.dumps(missing_planned) + "\n", encoding="utf-8")
                transport = FakeTransport(
                    [
                        _json_response({"status": "SUCCESS", "cost": 20}),
                        _json_response({"status": "SUCCESS"}),
                        _json_response({"status": "SUCCESS", "domain": "example.com"}),
                    ]
                )
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "domain",
                        "domain-renew",
                        "--domain",
                        "example.com",
                        "--input",
                        str(body),
                        "--plan-in",
                        str(plan_path),
                        "--apply",
                        "--ack-spend",
                        "--yes",
                    ],
                    transport=transport,
                )
                self.assertEqual(code, 0)
                self.assertTrue(payload["refused"])
                self.assertEqual(transport.calls, [])

                malformed_planned = json.loads(json.dumps(original))
                malformed_planned["dry_run"]["cost_signature"] = "cost=unknown"
                cli._sign_plan(
                    malformed_planned,
                    cli._load_plan_signing_key(create=False),
                )
                plan_path.write_text(
                    json.dumps(malformed_planned) + "\n",
                    encoding="utf-8",
                )
                transport = FakeTransport()
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "domain",
                        "domain-renew",
                        "--domain",
                        "example.com",
                        "--input",
                        str(body),
                        "--plan-in",
                        str(plan_path),
                        "--apply",
                        "--ack-spend",
                        "--yes",
                    ],
                    transport=transport,
                )
                self.assertEqual(code, 0)
                self.assertTrue(payload["refused"])
                self.assertEqual(transport.calls, [])

                plan_path.write_text(json.dumps(original) + "\n", encoding="utf-8")
                transport = FakeTransport(
                    [
                        _json_response({"status": "SUCCESS"}),
                        _json_response({"status": "SUCCESS"}),
                    ]
                )
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "domain",
                        "domain-renew",
                        "--domain",
                        "example.com",
                        "--input",
                        str(body),
                        "--plan-in",
                        str(plan_path),
                        "--apply",
                        "--ack-spend",
                        "--yes",
                    ],
                    transport=transport,
                )
                self.assertEqual(code, 0)
                self.assertTrue(payload["refused"])
                self.assertEqual(len(transport.calls), 1)

                plan_path.write_text(json.dumps(original) + "\n", encoding="utf-8")
                transport = FakeTransport(
                    [
                        _json_response({"status": "SUCCESS", "cost": 20}),
                        _json_response({"status": "SUCCESS"}),
                    ]
                )
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "domain",
                        "domain-renew",
                        "--domain",
                        "example.com",
                        "--input",
                        str(body),
                        "--plan-in",
                        str(plan_path),
                        "--apply",
                        "--ack-spend",
                        "--yes",
                    ],
                    transport=transport,
                )
                self.assertEqual(code, 0)
                self.assertTrue(payload["refused"])
                self.assertIn("cost signature changed", payload["reasons"][0])
                self.assertEqual(len(transport.calls), 1)

    def test_static_acknowledgements_are_rebuilt_from_operation_metadata(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            body = root / "payload.json"
            body.write_text(
                '{"emailAddress": "user@example.com", "password": "PASSWORD_SENTINEL"}',
                encoding="utf-8",
            )
            plan_path = root / "plan.json"
            with _working_directory(root):
                code, _ = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "email-hosting",
                        "email-set-password",
                        "--input",
                        str(body),
                        "--plan-out",
                        str(plan_path),
                    ],
                    transport=FakeTransport(),
                )
                self.assertEqual(code, 0)
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                plan["risk_flags"] = {
                    key: False for key in plan["risk_flags"]
                }
                cli._sign_plan(plan, cli._load_plan_signing_key(create=False))
                plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")

                transport = FakeTransport()
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "email-hosting",
                        "email-set-password",
                        "--input",
                        str(body),
                        "--plan-in",
                        str(plan_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                    ],
                    transport=transport,
                )
            self.assertEqual(code, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--ack-secret", payload["reasons"][0])
            self.assertEqual(transport.calls, [])

    def test_billable_and_terms_inputs_are_not_weakened(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))

            renew = Path(td) / "renew.json"
            renew.write_text("{}", encoding="utf-8")
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "domain",
                    "domain-renew",
                    "--domain",
                    "example.com",
                    "--input",
                    str(renew),
                ],
                transport=FakeTransport(),
            )
            self.assertEqual(code, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("cost", payload["error"])

            create = Path(td) / "create.json"
            create.write_text('{"cost": 1000, "agreeToTerms": "no"}', encoding="utf-8")
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "domain",
                    "domain-create",
                    "--domain",
                    "example.com",
                    "--input",
                    str(create),
                ],
                transport=FakeTransport(),
            )
            self.assertEqual(code, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_secret_write_requires_output_path_before_transport(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            body = Path(td) / "webhook.json"
            body.write_text('{"url": "https://example.com/callback"}', encoding="utf-8")
            plan = Path(td) / "plan.json"

            code, _ = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-create",
                    "--input",
                    str(body),
                    "--ack-no-snapshot",
                    "--plan-out",
                    str(plan),
                ],
                transport=FakeTransport(),
            )
            self.assertEqual(code, 0)

            transport = FakeTransport()
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-create",
                    "--input",
                    str(body),
                    "--plan-in",
                    str(plan),
                    "--apply",
                    "--ack-secret",
                    "--ack-no-snapshot",
                    "--yes",
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["refused"], True)
            self.assertIn("--secret-out", payload["reasons"][0])
            self.assertEqual(transport.calls, [])

    def test_successful_write_still_gets_receipt_when_readback_mapping_is_unavailable(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            body = Path(td) / "webhook.json"
            body.write_text('{"url": "https://example.com/callback"}', encoding="utf-8")
            plan = Path(td) / "plan.json"
            secret_out = Path(td) / "secret.json"
            receipt_out = Path(td) / "receipt.json"

            code, _ = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-create",
                    "--input",
                    str(body),
                    "--plan-out",
                    str(plan),
                ],
                transport=FakeTransport(),
            )
            self.assertEqual(code, 0)

            transport = FakeTransport(
                [
                    _json_response(
                        {
                            "status": "SUCCESS",
                            "endpoint": {"id": 42, "secret": "SHOULD_NOT_LEAK"},
                        }
                    )
                ]
            )
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-create",
                    "--input",
                    str(body),
                    "--plan-in",
                    str(plan),
                    "--apply",
                    "--ack-secret",
                    "--ack-no-snapshot",
                    "--yes",
                    "--secret-out",
                    str(secret_out),
                    "--receipt-out",
                    str(receipt_out),
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["ok"], True)
            self.assertTrue(receipt_out.exists())
            receipt = json.loads(receipt_out.read_text(encoding="utf-8"))
            self.assertEqual(receipt["verification"]["performed"], True)
            self.assertEqual(receipt["verification"]["confirmed"], False)
            self.assertIn("Missing required mapped argument", receipt["verification"]["details"])
            self.assertNotIn("SHOULD_NOT_LEAK", json.dumps(payload))

    def test_missing_plan_hash_is_refused(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            body = Path(td) / "payload.json"
            body.write_text('{"status": "on"}', encoding="utf-8")
            plan = Path(td) / "plan.json"
            transport = FakeTransport(
                [
                    _json_response({"status": "SUCCESS", "domain": "example.com"}),
                ]
            )
            code, _ = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "domain",
                    "domain-update-auto-renew",
                    "--domain",
                    "example.com",
                    "--input",
                    str(body),
                    "--plan-out",
                    str(plan),
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)

            plan_data = json.loads(plan.read_text(encoding="utf-8"))
            plan_data.pop("plan_hash")
            plan.write_text(json.dumps(plan_data) + "\n", encoding="utf-8")
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "domain",
                    "domain-update-auto-renew",
                    "--domain",
                    "example.com",
                    "--input",
                    str(body),
                    "--plan-in",
                    str(plan),
                    "--apply",
                    "--yes",
                ],
                transport=FakeTransport(),
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["refused"], True)
            self.assertIn("signature", payload["reasons"][0].lower())

    def test_failed_snapshot_requires_explicit_no_snapshot_ack(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            body = Path(td) / "payload.json"
            body.write_text('{"id": 42}', encoding="utf-8")
            plan = Path(td) / "plan.json"

            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-delete",
                    "--input",
                    str(body),
                    "--plan-out",
                    str(plan),
                ],
                transport=FakeTransport(
                    [_json_response({"status": "ERROR", "code": "NOT_FOUND", "message": "Not found"}, status=404)]
                ),
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["plan"]["snapshot"]["requires_no_snapshot_ack"], True)

            transport = FakeTransport()
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-delete",
                    "--input",
                    str(body),
                    "--plan-in",
                    str(plan),
                    "--apply",
                    "--ack-destructive",
                    "--yes",
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["refused"], True)
            self.assertEqual(payload["reasons"], ["Plan requires --ack-no-snapshot"])
            self.assertEqual(transport.calls, [])

    def test_http_200_error_body_is_structured_provider_error(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env", api_key="", secret=""))
            transport = FakeTransport(
                [_json_response({"status": "ERROR", "code": "INVALID_DOMAIN", "message": "Invalid domain."})]
            )
            code, payload = _run_cli(
                ["--env-file", str(env), "utility", "get-ip"],
                transport=transport,
            )
            self.assertEqual(code, 1)
            self.assertEqual(payload["error_type"], "ProviderError")
            self.assertEqual(payload["code"], "INVALID_DOMAIN")

    def test_secret_results_go_to_secret_file_0600(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            secret_out = Path(td) / "secret.json"
            transport = FakeTransport([_json_response({"status": "SUCCESS", "secret": "SHOULD_NOT_LEAK"})])
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-list",
                    "--secret-out",
                    str(secret_out),
                    "--ack-secret",
                    "--output",
                    "json",
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["ok"], True)
            raw = transport.calls[0]["url"]
            self.assertTrue(raw.startswith("https://api.porkbun.com"))
            self.assertTrue(secret_out.exists())
            mode = stat.S_IMODE(secret_out.stat().st_mode)
            self.assertEqual(mode, 0o600)
            secret_payload = json.loads(secret_out.read_text(encoding="utf-8"))
            self.assertIn("secret", secret_payload)
            self.assertNotIn("secret", json.dumps(payload))

    def test_secret_read_requires_ack_before_transport(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env"))
            secret_out = Path(td) / "secret.json"
            transport = FakeTransport()
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-list",
                    "--secret-out",
                    str(secret_out),
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["refused"], True)
            self.assertEqual(payload["reasons"], ["Secret-bearing results require --ack-secret"])
            self.assertEqual(transport.calls, [])

    def test_secret_destination_is_reserved_before_any_provider_call(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            directory_target = root / "directory"
            directory_target.mkdir()
            existing = root / "existing.json"
            existing.write_text("do-not-touch", encoding="utf-8")
            symlink_target = root / "secret-link.json"
            symlink_target.symlink_to(existing)
            parent_file = root / "not-a-directory"
            parent_file.write_text("x", encoding="utf-8")
            unwritable_parent = root / "unwritable"
            unwritable_parent.mkdir()
            unwritable_parent.chmod(0o500)

            try:
                for label, secret_out in (
                    ("directory", directory_target),
                    ("symlink", symlink_target),
                    ("invalid parent", parent_file / "secret.json"),
                    ("unwritable parent", unwritable_parent / "secret.json"),
                ):
                    with self.subTest(label=label):
                        transport = FakeTransport(
                            [_json_response({"status": "SUCCESS", "privatekey": "provider-secret"})]
                        )
                        code, payload = _run_cli(
                            [
                                "--env-file",
                                str(env),
                                "ssl",
                                "ssl-retrieve",
                                "--domain",
                                "example.com",
                                "--secret-out",
                                str(secret_out),
                                "--ack-secret",
                            ],
                            transport=transport,
                        )
                        self.assertNotEqual(code, 0)
                        self.assertFalse(payload.get("ok", False))
                        self.assertEqual(transport.calls, [])
                self.assertEqual(existing.read_text(encoding="utf-8"), "do-not-touch")
            finally:
                unwritable_parent.chmod(0o700)

    def test_plan_write_uses_private_same_directory_atomic_replace(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            body = root / "payload.json"
            body.write_text('{"url": "https://example.com/callback"}', encoding="utf-8")
            plan_path = root / "plan.json"
            plan_path.write_text('{"old": true}\n', encoding="utf-8")
            real_replace = os.replace
            observed: list[tuple[Path, Path, int]] = []

            def inspect_replace(source: str | os.PathLike[str], destination: str | os.PathLike[str]) -> None:
                source_path = Path(source)
                destination_path = Path(destination)
                observed.append(
                    (
                        source_path.parent,
                        destination_path.parent,
                        stat.S_IMODE(source_path.stat().st_mode),
                    )
                )
                real_replace(source, destination)

            with _working_directory(root), patch("os.replace", side_effect=inspect_replace):
                code, _ = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "webhooks",
                        "webhook-create",
                        "--input",
                        str(body),
                        "--plan-out",
                        str(plan_path),
                    ],
                    transport=FakeTransport(),
                )

            self.assertEqual(code, 0)
            self.assertTrue(observed)
            self.assertTrue(all(source == destination for source, destination, _ in observed))
            self.assertTrue(all(mode == 0o600 for _, _, mode in observed))
            self.assertNotIn('"old"', plan_path.read_text(encoding="utf-8"))

    def test_normal_outputs_cannot_overwrite_the_plan_signing_key(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            body = root / "payload.json"
            body.write_text(
                '{"url": "https://example.com/callback"}',
                encoding="utf-8",
            )
            protected = root / ".state" / "plan-signing.key"
            with _working_directory(root):
                transport = FakeTransport()
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "webhooks",
                        "webhook-create",
                        "--input",
                        str(body),
                        "--plan-out",
                        str(protected),
                    ],
                    transport=transport,
                )
            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
            self.assertIn("protected tool file", payload["error"])
            self.assertEqual(transport.calls, [])
            self.assertFalse(protected.exists())

    def test_plan_output_refuses_control_file_collisions_and_aliases(self) -> None:
        cases = (
            "plan/env",
            "plan/input",
            "relative-dotdot/env",
            "symlink/env",
            "default-plan/env",
        )
        for case in cases:
            with self.subTest(case=case), TemporaryDirectory() as td:
                root = Path(td)
                nested = root / "nested"
                nested.mkdir()
                body = root / "payload.json"
                body.write_text('{"id": 42}', encoding="utf-8")
                env = root / ".env"
                _env_file(env)
                env_before = env.read_bytes()
                input_before = body.read_bytes()
                argv = [
                    "--env-file",
                    str(env),
                    "webhooks",
                    "webhook-update",
                    "--input",
                    str(body),
                ]
                token_hex_patch = None

                if case == "plan/env":
                    argv.extend(["--plan-out", str(env)])
                elif case == "plan/input":
                    argv.extend(["--plan-out", str(body)])
                elif case == "relative-dotdot/env":
                    argv.extend(["--plan-out", str(nested / ".." / ".env")])
                elif case == "symlink/env":
                    alias = root / "env-alias"
                    alias.symlink_to(env)
                    argv.extend(["--plan-out", str(alias)])
                else:
                    operation = cli._OPERATION_MAP["webhookUpdate"]
                    default_plan = (
                        root
                        / ".state"
                        / "plans"
                        / f"{cli._sha256_text(operation.operation_id)[:8]}-{'ab' * 6}.json"
                    )
                    default_plan.parent.mkdir(parents=True)
                    env = default_plan
                    _env_file(env)
                    env_before = env.read_bytes()
                    argv[1] = str(env)
                    token_hex_patch = patch(
                        "qwayk_porkbun_safe_agent_cli.cli.secrets.token_hex",
                        side_effect=lambda size: "ab" * size,
                    )

                transport = FakeTransport(
                    [_json_response({"status": "SUCCESS", "endpoint": {"id": 42}})]
                )
                with _working_directory(root):
                    if token_hex_patch is None:
                        code, payload = _run_cli(argv, transport=transport)
                    else:
                        with token_hex_patch:
                            code, payload = _run_cli(argv, transport=transport)

                self.assertEqual(code, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
                self.assertIn("file role collision", payload["error"].lower())
                self.assertEqual(transport.calls, [])
                self.assertEqual(env.read_bytes(), env_before)
                self.assertEqual(body.read_bytes(), input_before)
                self.assertEqual(list(root.rglob("*.tmp")), [])
                self.assertFalse(payload.get("ok", False))

    def test_apply_outputs_refuse_every_control_and_output_collision(self) -> None:
        cases = (
            "secret/receipt-relative-absolute",
            "receipt/env",
            "receipt/input-hardlink",
            "receipt/plan-in",
            "secret/env",
            "secret/input",
            "secret/plan-in",
            "secret/input-symlink",
        )
        for case in cases:
            with self.subTest(case=case), TemporaryDirectory() as td:
                root = Path(td)
                env = root / ".env"
                _env_file(env)
                body = root / "payload.json"
                body.write_text(
                    '{"url": "https://example.com/callback"}',
                    encoding="utf-8",
                )
                plan = root / "plan.json"
                with _working_directory(root):
                    code, _ = _run_cli(
                        [
                            "--env-file",
                            str(env),
                            "webhooks",
                            "webhook-create",
                            "--input",
                            str(body),
                            "--plan-out",
                            str(plan),
                        ],
                        transport=FakeTransport(),
                    )
                self.assertEqual(code, 0)

                secret_out = root / "secret.json"
                receipt_out = root / "receipt.json"
                if case == "secret/receipt-relative-absolute":
                    secret_out = Path("shared.json")
                    receipt_out = root / "shared.json"
                elif case == "receipt/env":
                    receipt_out = env
                elif case == "receipt/input-hardlink":
                    receipt_out = root / "input-hardlink.json"
                    os.link(body, receipt_out)
                elif case == "receipt/plan-in":
                    receipt_out = plan
                elif case == "secret/env":
                    secret_out = env
                elif case == "secret/input":
                    secret_out = body
                elif case == "secret/plan-in":
                    secret_out = plan
                elif case == "secret/input-symlink":
                    secret_out = root / "input-symlink.json"
                    secret_out.symlink_to(body)

                protected = {
                    env: env.read_bytes(),
                    body: body.read_bytes(),
                    plan: plan.read_bytes(),
                }
                transport = FakeTransport(
                    [
                        _json_response(
                            {
                                "status": "SUCCESS",
                                "endpoint": {"id": 42, "secret": "ONE_TIME_SECRET"},
                            }
                        ),
                        _json_response(
                            {"status": "SUCCESS", "endpoint": {"id": 42}}
                        ),
                    ]
                )
                with _working_directory(root):
                    code, payload = _run_cli(
                        [
                            "--env-file",
                            str(env),
                            "webhooks",
                            "webhook-create",
                            "--input",
                            str(body),
                            "--plan-in",
                            str(plan),
                            "--apply",
                            "--ack-secret",
                            "--ack-no-snapshot",
                            "--yes",
                            "--secret-out",
                            str(secret_out),
                            "--receipt-out",
                            str(receipt_out),
                        ],
                        transport=transport,
                    )

                self.assertEqual(code, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
                self.assertIn("file role collision", payload["error"].lower())
                self.assertEqual(transport.calls, [])
                for path, before in protected.items():
                    self.assertEqual(path.read_bytes(), before)
                self.assertEqual(list(root.rglob("*.tmp")), [])
                self.assertFalse(payload.get("ok", False))

    def test_default_receipt_refuses_plan_input_collision(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            body = root / "payload.json"
            body.write_text(
                '{"url": "https://example.com/callback"}',
                encoding="utf-8",
            )
            first_plan = root / "first-plan.json"
            with _working_directory(root):
                code, _ = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "webhooks",
                        "webhook-create",
                        "--input",
                        str(body),
                        "--plan-out",
                        str(first_plan),
                    ],
                    transport=FakeTransport(),
                )
            self.assertEqual(code, 0)
            plan_data = json.loads(first_plan.read_text(encoding="utf-8"))
            plan_in = (
                root
                / ".state"
                / "receipts"
                / f"{plan_data['plan_hash'][:16]}.json"
            )
            plan_in.parent.mkdir(parents=True, exist_ok=True)
            plan_in.write_bytes(first_plan.read_bytes())
            plan_before = plan_in.read_bytes()
            secret_out = root / "secret.json"
            transport = FakeTransport(
                [
                    _json_response(
                        {
                            "status": "SUCCESS",
                            "endpoint": {"id": 42, "secret": "ONE_TIME_SECRET"},
                        }
                    )
                ]
            )
            with _working_directory(root):
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "webhooks",
                        "webhook-create",
                        "--input",
                        str(body),
                        "--plan-in",
                        str(plan_in),
                        "--apply",
                        "--ack-secret",
                        "--ack-no-snapshot",
                        "--yes",
                        "--secret-out",
                        str(secret_out),
                    ],
                    transport=transport,
                )
            self.assertEqual(code, 1)
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("file role collision", payload["error"].lower())
            self.assertEqual(transport.calls, [])
            self.assertEqual(plan_in.read_bytes(), plan_before)
            self.assertFalse(secret_out.exists())
            self.assertEqual(list(root.rglob("*.tmp")), [])

    def test_concurrent_first_plans_share_one_signing_key(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            operation = cli._OPERATION_MAP["webhookCreate"]
            cfg = cli.Config(
                api_host="https://api.porkbun.com/api/json/v3",
                api_key="FAKE_KEY",
                secret_api_key="FAKE_SECRET",
                timeout_s=30,
            )
            workers = 8
            barrier = threading.Barrier(workers)
            token_lock = threading.Lock()
            token_counter = 0

            def competing_token_bytes(size: int) -> bytes:
                nonlocal token_counter
                barrier.wait(timeout=5)
                with token_lock:
                    token_counter += 1
                    marker = token_counter
                return bytes([marker]) * size

            def create_plan(index: int) -> dict[str, Any]:
                args = argparse.Namespace(plan_out=str(root / f"plan-{index}.json"))
                payload = {"url": f"https://example.com/callback/{index}"}
                plan, _ = cli._create_plan(
                    operation=operation,
                    cfg=cfg,
                    args=args,
                    path_params={},
                    query_params={},
                    payload=payload,
                    transport=FakeTransport(),
                    target=cli._effective_target(operation, {}, {}),
                )
                return plan

            with _working_directory(root), patch(
                "qwayk_porkbun_safe_agent_cli.cli.secrets.token_bytes",
                side_effect=competing_token_bytes,
            ):
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    plans = list(executor.map(create_plan, range(workers)))

                key_path = root / ".state" / "plan-signing.key"
                key = key_path.read_bytes()
                self.assertEqual(len(key), 32)
                self.assertEqual(stat.S_IMODE(key_path.stat().st_mode), 0o600)
                saved_plans = [
                    json.loads((root / f"plan-{index}.json").read_text(encoding="utf-8"))
                    for index in range(workers)
                ]
                for plan in saved_plans:
                    cli._verify_plan_signature(plan)
                self.assertEqual(len(plans), workers)
                self.assertEqual(
                    len({plan["plan_signature"] for plan in saved_plans}),
                    workers,
                )

            self.assertEqual(stat.S_IMODE((root / ".state").stat().st_mode), 0o700)
            self.assertEqual(list(root.rglob("*.tmp")), [])

    def test_secret_reservation_is_private_atomic_and_cleaned_on_provider_failure(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            secret_out = root / "secret.json"
            old_umask = os.umask(0)
            try:
                transport = FakeTransport(
                    [_json_response({"status": "ERROR", "code": "FAIL", "message": "failed"}, status=500)]
                )
                code, _ = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "ssl",
                        "ssl-retrieve",
                        "--domain",
                        "example.com",
                        "--secret-out",
                        str(secret_out),
                        "--ack-secret",
                    ],
                    transport=transport,
                )
            finally:
                os.umask(old_umask)

            self.assertEqual(code, 1)
            self.assertFalse(secret_out.exists())
            self.assertEqual(list(root.glob(".secret.json.*.tmp")), [])

    def test_provider_and_validation_errors_scrub_all_secret_sentinels(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            api_key = "API_KEY_SENTINEL_123"
            secret_key = "SECRET_KEY_SENTINEL_456"
            verifier = "CODE_VERIFIER_SENTINEL"
            request_token = "a" * 64
            env = Path(_env_file(root / ".env", api_key=api_key, secret=secret_key))

            for mode in ("json", "text"):
                transport = FakeTransport(
                    [
                        _json_response(
                            {
                                "status": "ERROR",
                                "code": "AUTH_FAILED",
                                "message": f"bad {api_key} and {secret_key}",
                            }
                        )
                    ]
                )
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--output",
                        mode,
                        "domain",
                        "get-domain",
                        "--domain",
                        "example.com",
                    ],
                    transport=transport,
                )
                rendered = json.dumps(payload)
                self.assertEqual(code, 1)
                self.assertNotIn(api_key, rendered)
                self.assertNotIn(secret_key, rendered)
                self.assertEqual(payload["code"], "AUTH_FAILED")

            body = root / "retrieve.json"
            body.write_text(
                json.dumps({"requestToken": request_token, "codeVerifier": verifier}),
                encoding="utf-8",
            )
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "api-key",
                    "apikey-retrieve",
                    "--input",
                    str(body),
                    "--ack-secret",
                ],
                transport=FakeTransport(),
            )
            rendered = json.dumps(payload)
            self.assertEqual(code, 1)
            self.assertNotIn(verifier, rendered)
            self.assertNotIn(request_token, rendered)

            invite_token = "INVITE_TRANSPORT_SENTINEL"
            valid_body = root / "invite-status.json"
            valid_body.write_text(
                json.dumps({"token": invite_token}),
                encoding="utf-8",
            )
            transport = RaisingTransport(
                f"transport echoed {api_key} {secret_key} {invite_token}"
            )
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "account",
                    "get-account-invite-status",
                    "--input",
                    str(valid_body),
                ],
                transport=transport,
            )
            rendered = json.dumps(payload)
            self.assertEqual(code, 1)
            for sentinel in (api_key, secret_key, invite_token):
                self.assertNotIn(sentinel, rendered)
            self.assertEqual(payload["code"], "TRANSPORT_ERROR")

            with patch(
                "qwayk_porkbun_safe_agent_cli.cli._run_operation",
                side_effect=RuntimeError(f"generic exception echoed {invite_token}"),
            ):
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--debug",
                        "account",
                        "get-account-invite-status",
                        "--input",
                        str(valid_body),
                    ],
                    transport=FakeTransport(),
                )
            self.assertEqual(code, 1)
            self.assertEqual(payload["error_type"], "RuntimeError")
            self.assertNotIn(invite_token, json.dumps(payload))

    def test_secret_input_and_provider_echo_never_reach_plan_receipt_or_stdout(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env"))
            password = "PASSWORD_SENTINEL_789"
            body = root / "password.json"
            body.write_text(
                json.dumps({"emailAddress": "user@example.com", "password": password}),
                encoding="utf-8",
            )
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"
            with _working_directory(root):
                code, plan_output = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "email-hosting",
                        "email-set-password",
                        "--input",
                        str(body),
                        "--plan-out",
                        str(plan_path),
                    ],
                    transport=FakeTransport(),
                )
                self.assertEqual(code, 0)
                self.assertNotIn(password, json.dumps(plan_output))
                self.assertNotIn(password, plan_path.read_text(encoding="utf-8"))

                transport = FakeTransport(
                    [
                        _json_response(
                            {
                                "status": "SUCCESS",
                                "message": f"password changed from {password}",
                            }
                        )
                    ]
                )
                code, apply_output = _run_cli(
                    [
                        "--env-file",
                        str(env),
                        "email-hosting",
                        "email-set-password",
                        "--input",
                        str(body),
                        "--plan-in",
                        str(plan_path),
                        "--apply",
                        "--ack-secret",
                        "--ack-no-snapshot",
                        "--yes",
                        "--receipt-out",
                        str(receipt_path),
                    ],
                    transport=transport,
                )
            self.assertEqual(code, 0)
            self.assertNotIn(password, json.dumps(apply_output))
            self.assertNotIn(password, receipt_path.read_text(encoding="utf-8"))

    def test_account_invite_status_token_is_file_only_and_never_echoed(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            token = "INVITE_TOKEN_SENTINEL"
            env = Path(_env_file(root / ".env"))

            inline_transport = FakeTransport()
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "account",
                    "get-account-invite-status",
                    "--token",
                    token,
                ],
                transport=inline_transport,
            )
            self.assertEqual(code, 1)
            self.assertNotIn(token, json.dumps(payload))
            self.assertEqual(inline_transport.calls, [])

            token_file = root / "invite-token.json"
            token_file.write_text(json.dumps({"token": token}), encoding="utf-8")
            transport = FakeTransport(
                [
                    _json_response(
                        {
                            "status": "SUCCESS",
                            "message": f"invite {token} is pending",
                        }
                    )
                ]
            )
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "account",
                    "get-account-invite-status",
                    "--input",
                    str(token_file),
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertNotIn(token, json.dumps(payload))
            self.assertEqual(transport.calls[0]["params"]["token"], token)
            self.assertIsNone(transport.calls[0]["json_body"])

    def test_redirect_response_cannot_succeed_or_create_write_receipt(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            env = Path(_env_file(root / ".env", api_key="", secret=""))
            code, payload = _run_cli(
                ["--env-file", str(env), "utility", "get-ip"],
                transport=FakeTransport(
                    [_json_response({"status": "SUCCESS"}, status=302, headers={"location": "https://evil.example"})]
                ),
            )
            self.assertEqual(code, 1)
            self.assertEqual(payload["error_type"], "ProviderError")

            auth_env = Path(_env_file(root / "auth.env"))
            body = root / "password.json"
            body.write_text(
                '{"emailAddress":"user@example.com","password":"safe-password"}',
                encoding="utf-8",
            )
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"
            with _working_directory(root):
                code, _ = _run_cli(
                    [
                        "--env-file",
                        str(auth_env),
                        "email-hosting",
                        "email-set-password",
                        "--input",
                        str(body),
                        "--plan-out",
                        str(plan_path),
                    ],
                    transport=FakeTransport(),
                )
                self.assertEqual(code, 0)
                code, payload = _run_cli(
                    [
                        "--env-file",
                        str(auth_env),
                        "email-hosting",
                        "email-set-password",
                        "--input",
                        str(body),
                        "--plan-in",
                        str(plan_path),
                        "--apply",
                        "--ack-secret",
                        "--ack-no-snapshot",
                        "--yes",
                        "--receipt-out",
                        str(receipt_path),
                    ],
                    transport=FakeTransport(
                        [_json_response({"status": "SUCCESS"}, status=302, headers={"location": "https://evil.example"})]
                    ),
                )
            self.assertEqual(code, 1)
            self.assertEqual(payload["error_type"], "ProviderError")
            self.assertFalse(receipt_path.exists())

    def test_provider_error_is_structured(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env", api_key="", secret=""))
            transport = FakeTransport(
                [
                    _json_response(
                        {"code": "ERR", "message": "bad things"},
                        status=400,
                        headers={
                            "x-request-id": "rid-1",
                            "x-api-version": "v3.9",
                            "X-RateLimit-Remaining": "5",
                            "Retry-After": "12",
                        },
                    )
                ]
            )
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "utility",
                    "get-ip",
                ],
                transport=transport,
            )
            self.assertEqual(code, 1)
            self.assertEqual(payload["error_type"], "ProviderError")
            self.assertEqual(payload["code"], "ERR")
            self.assertEqual(payload["error"], "bad things")
            self.assertEqual(payload["request_id"], "rid-1")
            self.assertEqual(payload["api_version"], "v3.9")
            self.assertIn("x-ratelimit-remaining", payload["rate_limits"])
            self.assertEqual(payload["retry_after"], "12")

    def test_onboarding_creates_placeholder_env(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(td) / ".env"
            old_umask = os.umask(0)
            try:
                code, payload = _run_cli(
                    ["onboarding", "--env-file", str(env)],
                    FakeTransport(),
                )
            finally:
                os.umask(old_umask)
            self.assertEqual(code, 0)
            self.assertEqual(payload["onboarding"]["env_created"], True)
            body = env.read_text(encoding="utf-8")
            self.assertIn("PORKBUN_API_KEY=", body)
            self.assertIn("PORKBUN_SECRET_API_KEY=", body)
            self.assertEqual(stat.S_IMODE(env.stat().st_mode), 0o600)
            self.assertEqual(list(env.parent.glob("..env.*.tmp")), [])

    def test_provider_output_is_single_json(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env", api_key="", secret=""))
            transport = FakeTransport([_json_response({"status": "SUCCESS", "statusText": "ok"})])
            code, payload = _run_cli(["--env-file", str(env), "utility", "get-ip"], transport=transport)
            self.assertEqual(code, 0)
            self.assertIsInstance(payload, dict)
            self.assertEqual(payload.get("ok"), True)

    def test_timeout_override_reaches_transport(self) -> None:
        with TemporaryDirectory() as td:
            env = Path(_env_file(Path(td) / ".env", api_key="", secret=""))
            transport = FakeTransport(
                [_json_response({"status": "SUCCESS", "yourIp": "1.2.3.4"})]
            )
            code, payload = _run_cli(
                [
                    "--env-file",
                    str(env),
                    "--timeout-s",
                    "7.5",
                    "utility",
                    "get-ip",
                ],
                transport=transport,
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["ok"], True)
            self.assertEqual(transport.calls[0]["timeout_s"], 7.5)


if __name__ == "__main__":
    unittest_main()
