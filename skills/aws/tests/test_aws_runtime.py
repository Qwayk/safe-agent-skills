from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from botocore.exceptions import ReadTimeoutError

from aws_safe_agent_cli.aws_runtime import _operation_policy, build_parser, main
from aws_safe_agent_cli.config import load_config
from aws_safe_agent_cli.errors import ValidationError
from aws_safe_agent_cli.generated_registry import load_generated_registry
from aws_safe_agent_cli.redaction import REDACTED, redact_obj, redact_text
from aws_safe_agent_cli.sts_identity import CallerIdentity
from aws_safe_agent_cli.validation import load_input_json, validate_operation_input


class TestAwsConfigAndRedaction(unittest.TestCase):
    def test_config_defaults_and_csv_lists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "AWS_PROFILE=demo-profile",
                        "AWS_ALLOWED_ACCOUNTS=111111111111, 222222222222",
                        "AWS_ALLOWED_REGIONS=us-east-1, eu-west-1",
                        "AWS_TIMEOUT_S=12",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            profiles = Path(td) / "config"
            profiles.write_text("[profile demo-profile]\nregion = eu-west-1\n")
            with patch.dict(os.environ, {"AWS_CONFIG_FILE": str(profiles)}, clear=True):
                cfg = load_config(str(env_path))
                with patch.dict(os.environ, {"AWS_DEFAULT_REGION": "us-west-2"}):
                    override = load_config(str(env_path))
        self.assertEqual(cfg.region_name, "eu-west-1")
        self.assertEqual(override.region_name, "us-west-2")
        self.assertEqual(cfg.profile_name, "demo-profile")
        self.assertEqual(cfg.allowed_accounts, ("111111111111", "222222222222"))
        self.assertEqual(cfg.allowed_regions, ("us-east-1", "eu-west-1"))
        self.assertEqual(cfg.timeout_s, 12.0)

    def test_redaction_masks_nested_secrets_and_text(self) -> None:
        payload = redact_obj(
            {
                "token": "abc",
                "nested": {"secret": "xyz", "safe": "ok"},
                "message": "token=abc",
            }
        )
        self.assertEqual(payload["token"], REDACTED)
        self.assertEqual(payload["nested"]["secret"], REDACTED)
        self.assertEqual(payload["nested"]["safe"], "ok")
        self.assertIn(REDACTED, redact_text("token=abc"))


class TestRegistryAndParsing(unittest.TestCase):
    def test_registry_lookup_and_parser_recognizes_real_commands(self) -> None:
        registry = load_generated_registry()
        self.assertEqual(registry.summary.service_count, 428)
        self.assertEqual(registry.get_operation("sts", "get-caller-identity").operation_name, "GetCallerIdentity")
        self.assertEqual(registry.get_operation("iam", "list-users").operation_kebab, "list-users")

        parser = build_parser()
        cases = [
            ("sts", "get-caller-identity"),
            ("iam", "list-users"),
            ("s3", "list-buckets"),
            ("ec2", "describe-instances"),
        ]
        for service, operation in cases:
            args = parser.parse_args([service, operation])
            self.assertEqual(args.cmd, service)
            self.assertEqual(args.operation, operation)

    def test_template_commands_are_not_exposed(self) -> None:
        parser = build_parser()
        cases = [
            ["auth", "token", "status"],
            ["jobs", "run"],
            ["demo", "read"],
            ["demo", "write"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                with self.assertRaises(ValidationError):
                    parser.parse_args(argv)

    def test_validation_rejects_unknown_parameter_and_loads_json_from_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "input.json"
            p.write_text('{"UserName":"demo"}\n', encoding="utf-8")
            self.assertEqual(load_input_json(str(p)), {"UserName": "demo"})

        with self.assertRaises(ValidationError):
            validate_operation_input(
                service_name="iam",
                operation_name="ListUsers",
                input_obj={"Bogus": 1},
            )


class TestAwsCommands(unittest.TestCase):
    def _run_main(self, argv: list[str]) -> tuple[int, dict[str, object]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(argv)
        return rc, json.loads(buf.getvalue())

    def test_inventory_summary_is_local_and_read_only(self) -> None:
        rc, payload = self._run_main(["--output", "json", "inventory", "summary"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["inventory"]["service_count"], 428)
        self.assertEqual(payload["inventory"]["operation_count"], 18727)

    @patch("aws_safe_agent_cli.commands.auth.fetch_caller_identity")
    def test_auth_check_uses_sts_identity(self, mock_fetch) -> None:
        mock_fetch.return_value = CallerIdentity(
            account="123456789012",
            arn="arn:aws:sts::123456789012:assumed-role/demo/user",
            user_id="AIDATESTUSER",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "AWS_DEFAULT_REGION=us-east-1",
                        "AWS_PROFILE=demo",
                        "AWS_ALLOWED_ACCOUNTS=123456789012",
                        "AWS_ALLOWED_REGIONS=us-east-1",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            rc, payload = self._run_main(["--output", "json", "--env-file", str(env_path), "auth", "check"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["auth"]["caller_identity"]["account"], "123456789012")
        self.assertTrue(payload["auth"]["allowlists"]["allowed"])

    def test_dry_run_write_emits_plan_without_live_call(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWS_DEFAULT_REGION=us-east-1\nAWS_TIMEOUT_S=5\n", encoding="utf-8")
            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "iam",
                    "create-user",
                    "--input-json",
                    '{"UserName":"demo"}',
                ]
            )
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["service"], "iam")
        self.assertEqual(payload["operation"], "create-user")
        self.assertEqual(payload["plan"]["input"]["UserName"], "demo")

    @patch("aws_safe_agent_cli.aws_runtime.fetch_caller_identity")
    def test_live_write_refuses_without_plan_and_yes(self, mock_fetch) -> None:
        mock_fetch.side_effect = AssertionError("STS should not be called")
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWS_DEFAULT_REGION=us-east-1\nAWS_TIMEOUT_S=5\n", encoding="utf-8")
            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "ec2",
                    "terminate-instances",
                    "--input-json",
                    '{"InstanceIds":["i-1234567890abcdef0"]}',
                    "--apply",
                ]
            )
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertTrue(any("plan-in" in reason for reason in payload["reasons"]))
        self.assertTrue(any("--yes" in reason for reason in payload["reasons"]))

    @patch("boto3.Session")
    @patch("aws_safe_agent_cli.aws_runtime.fetch_caller_identity")
    def test_live_write_without_read_back_records_limited_verification(self, mock_fetch, mock_session) -> None:
        class FakeIamClient:
            meta = SimpleNamespace(endpoint_url="https://iam.amazonaws.com")

            def create_user(self, **kwargs):
                self.last_kwargs = kwargs
                return {
                    "User": {
                        "UserName": kwargs["UserName"],
                        "Arn": "arn:aws:iam::123456789012:user/demo",
                        "UserId": "AIDAEXAMPLEUSER",
                    },
                    "ResponseMetadata": {"HTTPStatusCode": 200},
                }

        fake_client = FakeIamClient()
        mock_session.return_value.client.return_value = fake_client
        mock_fetch.return_value = CallerIdentity(
            account="123456789012",
            arn="arn:aws:sts::123456789012:assumed-role/demo/user",
            user_id="AIDATESTUSER",
        )

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "AWS_DEFAULT_REGION=us-east-1",
                        "AWS_ALLOWED_ACCOUNTS=123456789012",
                        "AWS_ALLOWED_REGIONS=us-east-1",
                        "AWS_TIMEOUT_S=5",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            plan_path = root / "plan.json"
            code, preview = self._run_main([
                "--env-file", str(env_path), "--bind-aws", "--plan-out", str(plan_path),
                "iam", "create-user", "--input-json", '{"UserName":"demo"}',
            ])
            self.assertEqual(code, 0)
            self.assertTrue(preview["approval_ready"])
            receipt_path = root / "receipt.json"

            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "iam",
                    "create-user",
                    "--input-json",
                    '{"UserName":"demo"}',
                    "--apply",
                    "--plan-in",
                    str(plan_path),
                    "--yes",
                    "--ack-no-snapshot",
                    "--receipt-out",
                    str(receipt_path),
                ]
            )
            receipt_file_payload = json.loads(receipt_path.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["applied"])
        self.assertEqual(fake_client.last_kwargs, {"UserName": "demo"})
        receipt = payload["receipt"]
        self.assertIn("verification", receipt)
        verification = receipt["verification"]
        self.assertTrue(verification["ran"])
        self.assertEqual(verification["status"], "limited")
        self.assertGreaterEqual(len(verification["checks"]), 3)
        self.assertIn("read_back", verification)
        self.assertFalse(verification["read_back"]["attempted"])
        self.assertIn("limits", verification)
        self.assertEqual(receipt_file_payload["verification"], verification)

    def test_live_write_requires_ack_no_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text("AWS_DEFAULT_REGION=us-east-1\nAWS_TIMEOUT_S=5\n", encoding="utf-8")
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "service": "ec2",
                        "operation": "stop-instances",
                        "region": "us-east-1",
                        "input": {"InstanceIds": ["i-1234567890abcdef0"]},
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "ec2",
                    "stop-instances",
                    "--input-json",
                    '{"InstanceIds":["i-1234567890abcdef0"]}',
                    "--apply",
                    "--plan-in",
                    str(plan_path),
                    "--yes",
                ]
            )
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertTrue(any("ack-no-snapshot" in reason for reason in payload["reasons"]))

    def test_unknown_mutating_policy_requires_no_snapshot_ack(self) -> None:
        policy = _operation_policy("s3", "DoSomethingUnclassified")
        self.assertEqual(policy["mode"], "unknown_mutating")
        self.assertTrue(policy["requires_ack_no_snapshot"])

    def test_dangerous_aws_categories_get_stronger_gates(self) -> None:
        examples = [
            ("iam", "CreateUser", "security_identity"),
            ("secretsmanager", "PutSecretValue", "secret"),
            ("ec2", "RunInstances", "spend_quota"),
            ("sns", "Publish", "messaging"),
            ("s3", "PutBucketPolicy", "public_exposure"),
            ("datasync", "StartTaskExecution", "data_movement"),
            ("budgets", "CreateBudget", "spend_quota"),
            ("cloudtrail", "DeregisterOrganizationDelegatedAdmin", "security_identity"),
        ]
        for service, operation, category in examples:
            with self.subTest(service=service, operation=operation):
                policy = _operation_policy(service, operation)
                self.assertIn(category, policy["risk_categories"])
                self.assertTrue(policy["requires_ack_no_snapshot"])
                self.assertTrue(policy["high_risk"])

        terminate = _operation_policy("ec2", "TerminateInstances")
        self.assertTrue(terminate["requires_ack_irreversible"])
        self.assertTrue(terminate["requires_ack_no_snapshot"])


class TestSavedAwsPlans(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.settings = self.root / "test.env"
        self.settings.write_text("AWS_DEFAULT_REGION=us-east-1\n")
        self.plan = self.root / "plan.json"
        self.receipt = self.root / "receipt.json"
        self.command = ["ec2", "start-instances", "--input-json", '{"InstanceIds":["i-example"]}']
        self.flags = ["--apply", "--yes", "--ack-no-snapshot", "--plan-in", str(self.plan)]
        self.client = patch("aws_safe_agent_cli.aws_runtime.make_client").start().return_value
        self.client.meta.endpoint_url = "https://ec2.us-east-1.amazonaws.com"
        self.session = patch("aws_safe_agent_cli.aws_runtime.make_session").start()
        self.sts = patch("aws_safe_agent_cli.aws_runtime.fetch_caller_identity").start()
        self.sts.return_value = self.identity()
        self.addCleanup(patch.stopall)

    @staticmethod
    def identity(account="123456789012", role="TestRole", session="first", role_id="AROAFIXTURE"):
        return CallerIdentity(account, f"arn:aws:sts::{account}:assumed-role/{role}/{session}", f"{role_id}:{session}")

    def run_cli(self, *args):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--env-file", str(self.settings), "--no-artifacts", *args])
        return code, json.loads(output.getvalue())

    def save(self, *, bind=True):
        flags = ["--bind-aws"] if bind else []
        code, payload = self.run_cli(*flags, "--plan-out", str(self.plan), *self.command)
        self.assertEqual(0, code)
        self.assertIs(payload["approval_ready"], bind)
        return payload

    def test_offline_plan_needs_an_aws_check_before_apply(self):
        self.save(bind=False)
        _, refused = self.run_cli(*self.flags, *self.command, "--ack-spend-money")
        self.assertIn("--bind-aws", refused["reasons"][0])
        self.session.assert_not_called()

    def test_plan_refuses_changed_account_role_region_and_endpoint(self):
        self.save()
        for identity in (self.identity(account="210987654321"), self.identity(role="OtherRole"),
                         self.identity(role_id="AROAOTHER")):
            self.sts.return_value = identity
            _, refused = self.run_cli(*self.flags, *self.command, "--ack-spend-money")
            self.assertIn("AWS account, role or endpoint", refused["reasons"][0])
        self.sts.return_value = self.identity()
        self.settings.write_text("AWS_DEFAULT_REGION=us-west-2\n")
        _, refused = self.run_cli(*self.flags, *self.command, "--ack-spend-money")
        self.assertIn("region", refused["reasons"][0])
        self.settings.write_text("AWS_DEFAULT_REGION=us-east-1\n")
        self.client.meta.endpoint_url = "https://alternate.example.invalid"
        _, refused = self.run_cli(*self.flags, *self.command, "--ack-spend-money")
        self.assertIn("endpoint", refused["reasons"][0])
        self.client.start_instances.assert_not_called()

    def test_exact_input_is_checked_when_its_display_is_masked(self):
        self.command = [
            "iam", "create-login-profile", "--input-json",
            '{"UserName":"example","Password":"fixture-one"}',
        ]
        preview = self.save()
        self.assertEqual(REDACTED, preview["plan"]["input"]["Password"])
        self.assertNotIn("fixture-one", self.plan.read_text())
        altered = [*self.command[:-1], self.command[-1].replace("fixture-one", "fixture-two")]
        _, refused = self.run_cli(*self.flags, *altered)
        self.assertIn("input", refused["reasons"][0])
        self.client.create_login_profile.assert_not_called()

    def test_spending_approval_and_pending_result(self):
        self.save()
        _, refused = self.run_cli(*self.flags, *self.command)
        self.assertIn("--ack-spend-money", refused["reasons"][0])
        self.client.start_instances.assert_not_called()
        self.sts.return_value = self.identity(session="second")
        self.client.start_instances.return_value = {
            "StartingInstances": [{"CurrentState": {"Name": "pending"}}],
            "ResponseMetadata": {"HTTPStatusCode": 200},
        }
        code, payload = self.run_cli(*self.flags, *self.command, "--ack-spend-money", "--receipt-out", str(self.receipt))
        self.assertEqual(0, code)
        self.client.start_instances.assert_called_once_with(InstanceIds=["i-example"])
        self.assertIsNone(payload["applied"])
        self.assertEqual("pending", json.loads(self.receipt.read_text())["verification"]["status"])
        self.assertFalse(payload["receipt"]["verification"]["read_back"]["attempted"])

    def test_lost_reply_records_uncertain_result_once(self):
        self.save()
        self.client.start_instances.side_effect = ReadTimeoutError(endpoint_url=self.client.meta.endpoint_url)
        code, payload = self.run_cli(*self.flags, *self.command, "--ack-spend-money", "--receipt-out", str(self.receipt))
        self.assertEqual(1, code)
        self.client.start_instances.assert_called_once()
        self.assertIsNone(payload["applied"])
        verification = json.loads(self.receipt.read_text())["verification"]
        self.assertEqual("outcome_unknown", verification["status"])
        self.assertIn("before retrying", verification["next_step"])

    def test_unavailable_streaming_operation_stops_before_aws_sign_in(self):
        _, result = self.run_cli("polly", "start-speech-synthesis-stream")
        self.assertTrue(result["refused"])
        self.assertIn("two-way event stream", result["reasons"][0])
        self.session.assert_not_called()
