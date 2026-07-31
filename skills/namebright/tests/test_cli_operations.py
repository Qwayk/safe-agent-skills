from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from namebright_safe_cli.cli import build_parser, main
from namebright_safe_cli.operations import OPERATIONS, get_operation, method_counts


class _FakeOperationResponse:
    def __init__(self, payload: dict | list):
        self.payload = payload


class _FakeClient:
    def __init__(self, *_args, **_kwargs):
        pass

    def execute_operation(self, spec, values=None):
        return _FakeOperationResponse({"ok": True})


class _FakeAuthClient:
    def __init__(self, *_args, **_kwargs):
        pass

    def request_token_status(self):
        return {
            "ok": True,
            "token_status": {
                "exists": True,
                "fields": ["access_token", "scope"],
                "updated_at_utc": "2026-07-31T00:00:00Z",
            },
        }


class TestCliOperations(unittest.TestCase):
    def _env_file(self, d: str) -> str:
        path = Path(d) / ".env"
        path.write_text(
            "\n".join(
                [
                    "NAMEBRIGHT_CLIENT_ID=client-id",
                    "NAMEBRIGHT_CLIENT_SECRET=client-secret",
                    "NAMEBRIGHT_TIMEOUT_S=30",
                ],
            ),
            encoding="utf-8",
        )
        return str(path)

    def _run_main(self, args: list[str], client: object | None = None) -> tuple[int, dict]:
        buf = io.StringIO()
        fake = client or _FakeClient()
        with redirect_stdout(buf):
            rc = main(args, client_factory=lambda **kwargs: fake)
        output = buf.getvalue().strip()
        payload = json.loads(output) if output else {}
        return rc, payload

    def _run_main_with_factory(self, args: list[str], factory) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(args, client_factory=factory)
        payload = json.loads(buf.getvalue())
        return rc, payload

    @staticmethod
    def _required_operation_args(op) -> list[str]:
        args: list[str] = []
        for field in op.fields:
            if field.source != "cli" or not field.required or field.kind == "secret_file":
                continue
            args.append(f"--{field.cli_name}")
            if field.choices:
                args.append(str(field.choices[0]))
            elif field.kind == "int":
                args.append("1")
            elif field.kind == "bool":
                args.append("true")
            elif field.api_name in {"domain", "DomainName"}:
                args.append("example.com")
            elif field.api_name in {"Email", "EmailAddress"}:
                args.append("user@example.com")
            elif field.api_name == "PhoneNumber":
                args.append("+15555550123")
            elif field.api_name == "IpAddress":
                args.append("127.0.0.1")
            elif field.api_name == "nameServer":
                args.append("ns1.example.com")
            else:
                args.append("example")
        return args

    def test_family_leaf_and_counts(self) -> None:
        self.assertEqual(len(OPERATIONS), 61)
        self.assertEqual(len(set((op.family, op.command) for op in OPERATIONS)), 61)
        self.assertEqual(method_counts(), {"GET": 23, "POST": 18, "PUT": 8, "DELETE": 12})
        self.assertEqual(sum(1 for op in OPERATIONS if op.write_capable), 37)

    def test_all_61_operation_leaves_bind_exact_registry_specs(self) -> None:
        parser = build_parser()
        for op in OPERATIONS:
            with self.subTest(operation=op.command):
                leaf = op.command.split(" ", 1)[1]
                parsed = parser.parse_args(
                    [op.family, leaf, *self._required_operation_args(op)]
                )
                self.assertIs(parsed._registry_spec, op)

    def test_every_read_dispatches_and_every_write_defaults_to_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = self._env_file(d)
            for op in OPERATIONS:
                leaf = op.command.split(" ", 1)[1]
                operation_args = self._required_operation_args(op)
                with self.subTest(operation=op.command):
                    if op.write_capable:
                        with patch(
                            "namebright_safe_cli.cli.create_plan",
                            return_value={"fingerprint": "safe"},
                        ) as planned:
                            rc, payload = self._run_main(
                                [
                                    "--output",
                                    "json",
                                    "--env-file",
                                    env_file,
                                    "--no-artifacts",
                                    "--plan-out",
                                    str(Path(d) / "plan.json"),
                                    op.family,
                                    leaf,
                                    *operation_args,
                                ],
                                client=_FakeClient(),
                            )
                        self.assertEqual(rc, 0)
                        self.assertTrue(payload.get("dry_run"))
                        planned.assert_called_once()
                    else:
                        rc, payload = self._run_main(
                            [
                                "--output",
                                "json",
                                "--env-file",
                                env_file,
                                op.family,
                                leaf,
                                *operation_args,
                            ],
                            client=_FakeClient(),
                        )
                        self.assertEqual(rc, 0)
                        self.assertEqual(
                            payload.get("operation"),
                            {"family": op.family, "command": op.command},
                        )

    def test_plan_apply_flags_are_separate_and_timeout_is_positive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = self._env_file(d)
            cases = [
                ["--plan-in", f"{d}/plan.json"],
                ["--receipt-out", f"{d}/receipt.json"],
                ["--yes"],
                ["--ack-high-risk"],
            ]
            for extra in cases:
                with self.subTest(extra=extra):
                    rc, payload = self._run_main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            *extra,
                            "domains",
                            "update",
                            "--domain",
                            "example.com",
                            "--opt-out-of-lock",
                            "true",
                        ],
                    )
                    self.assertEqual(rc, 1)
                    self.assertEqual(payload.get("error_type"), "ValidationError")

            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env_file,
                    "--timeout-s",
                    "0",
                    "account",
                    "show",
                ],
            )
            self.assertEqual(rc, 1)
            self.assertEqual(payload.get("error_type"), "ValidationError")

    def test_exact_field_flags(self) -> None:
        op = get_operation("domains", "domains update")
        self.assertIsNotNone(op)
        assert op is not None
        cli_flags = {f"--{f.cli_name}" for f in op.fields if f.cli_name}
        self.assertEqual(
            cli_flags,
            {"--domain", "--opt-out-of-lock", "--locked", "--auto-renew", "--who-is-privacy"},
        )

        op = get_operation("purchase", "purchase register")
        self.assertIsNotNone(op)
        assert op is not None
        cli_flags = {f"--{f.cli_name}" for f in op.fields if f.cli_name}
        self.assertEqual(cli_flags, {"--domain-name", "--years", "--category-id", "--category-name"})

    def test_parse_single_json_object_for_forbidden_commands(self) -> None:
        for bad in ["jobs", "demo", "batch"]:
            with self.subTest(command=bad):
                rc, payload = self._run_main(["--output", "json", bad, "run"], client=None)
                self.assertEqual(rc, 1)
                self.assertIsInstance(payload, dict)
                self.assertEqual(payload.get("error_type"), "ValidationError")

    def test_bool_fields_require_true_or_false(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = self._env_file(d)
            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env_file,
                    "domains",
                    "update",
                    "--domain",
                    "example.com",
                    "--opt-out-of-lock",
                    "1",
                ],
                client=_FakeClient(),
            )
            self.assertEqual(rc, 1)
            self.assertEqual(payload.get("error_type"), "ValidationError")

    def test_read_operation_rejects_write_flags_and_acks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = self._env_file(d)
            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env_file,
                    "--plan-in",
                    f"{d}/plan.json",
                    "--plan-out",
                    f"{d}/plan2.json",
                    "--receipt-out",
                    f"{d}/receipt.json",
                    "--apply",
                    "--yes",
                    "--ack-high-risk",
                    "--ack-spend",
                    "account",
                    "show",
                ],
                client=_FakeClient(),
            )
            self.assertEqual(rc, 1)
            self.assertEqual(payload.get("error_type"), "ValidationError")
            self.assertIn("only available for write-capable", payload.get("error", ""))

    def test_write_requirements_and_apply_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = self._env_file(d)
            plan_out = Path(d) / "plan.json"
            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env_file,
                    "--plan-out",
                    str(plan_out),
                    "domains",
                    "update",
                    "--domain",
                    "example.com",
                    "--opt-out-of-lock",
                    "true",
                ],
                client=_FakeClient(),
            )
            self.assertEqual(rc, 0)
            self.assertTrue(plan_out.exists())
            self.assertIn("plan", payload)

            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env_file,
                    "--apply",
                    "--plan-in",
                    str(plan_out),
                    "--yes",
                    "--ack-high-risk",
                    "domains",
                    "update",
                    "--domain",
                    "example.com",
                    "--opt-out-of-lock",
                    "true",
                ],
                client=_FakeClient(),
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("refused") or payload.get("ok"))
            if payload.get("ok"):
                self.assertIn("receipt", payload)
                self.assertIn("receipt_out", payload)

            # no write artifacts means explicit requirement for plan/receipt paths.
            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env_file,
                    "--no-artifacts",
                    "--apply",
                    "--plan-in",
                    str(plan_out),
                    "--yes",
                    "--ack-high-risk",
                    "domains",
                    "update",
                    "--domain",
                    "example.com",
                    "--opt-out-of-lock",
                    "true",
                ],
                client=_FakeClient(),
            )
            self.assertEqual(rc, 1)
            self.assertEqual(payload.get("error_type"), "ValidationError")

    def test_secret_file_plans_do_not_require_secret_and_apply_is_safe(self) -> None:
        cases = [
            ("contact-verification", "contact-verification verify-contact", ["--ip-address", "127.0.0.1"], "--link-auth-code-file"),
            ("contact-verification", "contact-verification verify-email", ["--email", "user@example.com", "--ip-address", "127.0.0.1"], "--verification-code-file"),
            ("contact-verification", "contact-verification verify-phone", ["--phone-number", "+15550000000", "--ip-address", "127.0.0.1"], "--verification-code-file"),
        ]
        for family, op, req_args, secret_flag in cases:
            with self.subTest(operation=op):
                leaf = op.split(" ", 1)[1]
                with tempfile.TemporaryDirectory() as d:
                    env_file = self._env_file(d)
                    artifacts = Path(d) / "artifacts"
                    plan_out = artifacts / "plan.json"
                    rc, payload = self._run_main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "--artifacts-dir",
                            str(artifacts),
                            "--plan-out",
                            str(plan_out),
                            family,
                            leaf,
                            *req_args,
                        ],
                        client=_FakeClient(),
                    )
                    self.assertEqual(rc, 0)
                    self.assertTrue(plan_out.exists())

                    rc, payload = self._run_main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "--artifacts-dir",
                            str(artifacts),
                            "--apply",
                            "--plan-in",
                            str(plan_out),
                            "--yes",
                            "--ack-high-risk",
                            "--ack-spend",
                            family,
                            leaf,
                            *req_args,
                        ],
                        client=_FakeClient(),
                    )
                    self.assertEqual(rc, 1)
                    self.assertEqual(payload.get("error_type"), "ValidationError")
                    self.assertIn("verification" if "verification" in secret_flag else "link-auth-code-file", payload.get("error", ""))

                    secret_file = artifacts / "secret.txt"
                    secret_file.write_text("super-secret-code", encoding="utf-8")
                    secret_file.chmod(0o600)

                    rc, payload = self._run_main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "--artifacts-dir",
                            str(artifacts),
                            "--apply",
                            "--plan-in",
                            str(plan_out),
                            "--yes",
                            "--ack-high-risk",
                            family,
                            leaf,
                            *req_args,
                            secret_flag,
                            str(secret_file),
                        ],
                        client=_FakeClient(),
                    )
                    self.assertEqual(rc, 0)
                    raw = json.dumps(payload)
                    self.assertIn("receipt", payload)
                    self.assertNotIn(str(secret_file), raw)
                    self.assertNotIn("super-secret-code", raw)
                    summary_text = (artifacts / "summary.md").read_text(encoding="utf-8")
                    self.assertNotIn(str(secret_file), summary_text)
                    self.assertNotIn("super-secret-code", summary_text)

    def test_auth_check_uses_request_token_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = self._env_file(d)
            rc, payload = self._run_main_with_factory(
                ["--output", "json", "--env-file", env_file, "auth", "check"],
                factory=lambda **kwargs: _FakeAuthClient(),
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("ok"))
            self.assertIn("token_status", payload)
            self.assertIsInstance(payload.get("token_status"), dict)

    def test_representative_fake_read_and_no_forbidden_options(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = self._env_file(d)
            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env_file,
                    "account",
                    "show",
                ],
                client=_FakeClient(),
            )
            self.assertEqual(rc, 0)
            self.assertEqual(payload.get("operation"), {"family": "account", "command": "account show"})
            self.assertIn("response", payload)

            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env_file,
                    "account",
                    "show",
                    "--selector",
                    "x",
                ],
                client=_FakeClient(),
            )
            self.assertEqual(rc, 1)
            self.assertEqual(payload.get("error_type"), "ValidationError")
