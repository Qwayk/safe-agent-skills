from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

from jira_safe_agent_cli.operations import canonical_hash

from .helpers import fake_response, run_cli, write_basic_env


class WriteSafetyTests(unittest.TestCase):
    def make_body(self, root: Path) -> Path:
        path = root / "body.json"
        path.write_text(json.dumps({"fields": {"summary": "Example"}}), encoding="utf-8")
        return path

    def plan_create(self, root: Path) -> tuple[Path, Path, Path]:
        env = write_basic_env(root)
        body = self.make_body(root)
        artifacts = root / "plan-run"
        rc, payload, _ = run_cli(
            [
                "--env-file",
                str(env),
                "--artifacts-dir",
                str(artifacts),
                "platform",
                "create-issue",
                "--body-file",
                str(body),
            ]
        )
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(oct((artifacts / "plan.json").stat().st_mode & 0o777), "0o600")
        return env, body, artifacts / "plan.json"

    def test_create_plan_makes_no_http_request(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            patch("requests.Session.request") as request,
        ):
            self.plan_create(Path(directory))
        request.assert_not_called()

    def test_recomputed_public_hash_cannot_tamper_with_plan(self) -> None:
        mutations = {
            "path": lambda plan: plan.__setitem__("path", "/rest/api/3/issue/EX-1"),
            "query": lambda plan: plan.__setitem__("query", {"notifyUsers": "false"}),
            "headers": lambda plan: plan.__setitem__("headers", {"X-Override": "1"}),
            "body": lambda plan: plan["body"].__setitem__("content_type", "text/plain"),
            "high_risk": lambda plan: plan.__setitem__("high_risk", True),
            "snapshot_get_available": lambda plan: plan.__setitem__(
                "snapshot_get_available", True
            ),
            "snapshot_query": lambda plan: plan.__setitem__("snapshot_query", {"expand": "all"}),
            "no_snapshot_warning": lambda plan: plan.__setitem__(
                "no_snapshot_warning", None
            ),
        }
        for field, mutate in mutations.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                env, _, plan_path = self.plan_create(root)
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                mutate(plan)
                unsigned = {
                    key: value
                    for key, value in plan.items()
                    if key != "integrity_hmac_sha256"
                }
                # This reproduces the old public self-hash attack. It is not a valid HMAC.
                plan["integrity_hmac_sha256"] = canonical_hash(unsigned)
                plan_path.write_text(json.dumps(plan), encoding="utf-8")
                with patch("requests.Session.request") as request:
                    rc, payload, _ = run_cli(
                        [
                            "--env-file",
                            str(env),
                            "--apply",
                            "--yes",
                            "--ack-no-snapshot",
                            "--ack-high-risk",
                            "--plan-in",
                            str(plan_path),
                            "platform",
                            "create-issue",
                        ]
                    )
                self.assertEqual(rc, 0)
                self.assertTrue(payload["refused"])
                self.assertIn("integrity", payload["reasons"][0].lower())
                request.assert_not_called()

    def test_plan_signing_key_is_private_and_required_for_apply(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env, _, plan = self.plan_create(root)
            key = root / ".state" / "plan-signing.key"
            self.assertEqual(key.stat().st_mode & 0o777, 0o600)
            key.unlink()
            with patch("requests.Session.request") as request:
                rc, payload, _ = run_cli(
                    [
                        "--env-file", str(env), "--apply", "--yes", "--ack-no-snapshot",
                        "--plan-in", str(plan), "platform", "create-issue",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("signing key is missing", payload["reasons"][0])
            request.assert_not_called()

    def test_apply_requires_no_snapshot_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env, _, plan = self.plan_create(root)
            with patch("requests.Session.request") as request:
                rc, payload, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan),
                        "platform",
                        "create-issue",
                    ]
                )
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--ack-no-snapshot", payload["reasons"][0])
        request.assert_not_called()

    def test_body_drift_refuses_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env, body, plan = self.plan_create(root)
            body.write_text(json.dumps({"fields": {"summary": "Changed"}}), encoding="utf-8")
            with patch("requests.Session.request") as request:
                rc, payload, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan),
                        "platform",
                        "create-issue",
                    ]
                )
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("changed after planning", payload["reasons"][0])
        request.assert_not_called()

    def test_no_snapshot_apply_writes_private_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env, _, plan = self.plan_create(root)
            artifacts = root / "apply-run"
            with patch(
                "requests.Session.request",
                return_value=fake_response(status=201, body={"id": "10001", "key": "EX-1"}),
            ):
                rc, payload, raw = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--artifacts-dir",
                        str(artifacts),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan),
                        "platform",
                        "create-issue",
                    ]
                )
            receipt = artifacts / "receipt.json"
            self.assertEqual(rc, 0)
            self.assertTrue(payload["applied"])
            self.assertEqual(oct(receipt.stat().st_mode & 0o777), "0o600")
            self.assertNotIn("test-secret-token", raw + receipt.read_text(encoding="utf-8"))

    def test_provider_http_failure_still_writes_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env, _, plan = self.plan_create(root)
            artifacts = root / "failed-apply"
            with patch(
                "requests.Session.request",
                return_value=fake_response(status=500, body={"errorMessages": ["failed"]}),
            ):
                rc, payload, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--artifacts-dir",
                        str(artifacts),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan),
                        "platform",
                        "create-issue",
                    ]
                )
            receipt = json.loads((artifacts / "receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "HttpError")
            self.assertFalse(receipt["ok"])
            self.assertEqual(receipt["provider_status"], 500)

    def test_matching_get_saves_before_state_and_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = write_basic_env(root)
            body = self.make_body(root)
            plan_run = root / "edit-plan"
            rc, _, _ = run_cli(
                [
                    "--env-file",
                    str(env),
                    "--artifacts-dir",
                    str(plan_run),
                    "platform",
                    "edit-issue",
                    "--issue-id-or-key",
                    "EX-1",
                    "--body-file",
                    str(body),
                ]
            )
            self.assertEqual(rc, 0)
            apply_run = root / "edit-apply"
            responses = [
                fake_response(body={"key": "EX-1", "fields": {"summary": "Before"}}),
                fake_response(status=204),
                fake_response(body={"key": "EX-1", "fields": {"summary": "After"}}),
            ]
            with patch("requests.Session.request", side_effect=responses) as request:
                rc, payload, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--artifacts-dir",
                        str(apply_run),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_run / "plan.json"),
                        "platform",
                        "edit-issue",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["snapshot_saved"])
            self.assertTrue(payload["verification"]["verified"])
            self.assertTrue((apply_run / "before.json").exists())
            self.assertTrue((apply_run / "after.json").exists())
            self.assertEqual(
                [call.kwargs["method"] for call in request.call_args_list],
                ["GET", "PUT", "GET"],
            )

    def test_verification_failure_is_recorded_after_successful_apply(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = write_basic_env(root)
            body = self.make_body(root)
            plan_run = root / "verify-plan"
            rc, _, _ = run_cli(
                [
                    "--env-file",
                    str(env),
                    "--artifacts-dir",
                    str(plan_run),
                    "platform",
                    "edit-issue",
                    "--issue-id-or-key",
                    "EX-1",
                    "--body-file",
                    str(body),
                ]
            )
            self.assertEqual(rc, 0)
            apply_run = root / "verify-apply"
            responses = [
                fake_response(body={"key": "EX-1"}),
                fake_response(status=204),
                requests.ConnectionError("offline"),
            ]
            with patch("requests.Session.request", side_effect=responses):
                rc, payload, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--artifacts-dir",
                        str(apply_run),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_run / "plan.json"),
                        "platform",
                        "edit-issue",
                    ]
                )
            receipt = json.loads((apply_run / "receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(rc, 0)
            self.assertTrue(payload["applied"])
            self.assertFalse(payload["verification"]["verified"])
            self.assertFalse(receipt["verification"]["verified"])

    def test_high_risk_delete_requires_extra_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = write_basic_env(root)
            plan_run = root / "delete-plan"
            rc, plan_payload, _ = run_cli(
                [
                    "--env-file",
                    str(env),
                    "--artifacts-dir",
                    str(plan_run),
                    "platform",
                    "delete-issue",
                    "--issue-id-or-key",
                    "EX-1",
                    "--delete-subtasks",
                    "true",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(plan_payload["high_risk"])
            delete_plan = json.loads((plan_run / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual(delete_plan["query"], {"deleteSubtasks": "true"})
            self.assertEqual(delete_plan["snapshot_query"], {})
            with patch("requests.Session.request") as request:
                rc, payload, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_run / "plan.json"),
                        "platform",
                        "delete-issue",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--ack-high-risk", payload["reasons"][0])
            request.assert_not_called()

    def test_project_administration_apply_requires_extra_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = write_basic_env(root)
            body = root / "component.json"
            body.write_text(
                json.dumps({"name": "Reviewed component", "project": "EX"}),
                encoding="utf-8",
            )
            plan_run = root / "component-plan"
            rc, plan_payload, _ = run_cli(
                [
                    "--env-file",
                    str(env),
                    "--artifacts-dir",
                    str(plan_run),
                    "platform",
                    "create-component",
                    "--body-file",
                    str(body),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(plan_payload["high_risk"])
            with patch("requests.Session.request") as request:
                rc, payload, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_run / "plan.json"),
                        "platform",
                        "create-component",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--ack-high-risk", payload["reasons"][0])
            request.assert_not_called()

    def test_multipart_plan_hashes_upload_without_http(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = write_basic_env(root)
            upload = root / "evidence.txt"
            upload.write_text("test evidence", encoding="utf-8")
            second_upload = root / "second.txt"
            second_upload.write_text("second file", encoding="utf-8")
            artifacts = root / "attachment-plan"
            with patch("requests.Session.request") as request:
                rc, _, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--artifacts-dir",
                        str(artifacts),
                        "platform",
                        "add-attachment",
                        "--issue-id-or-key",
                        "EX-1",
                        "--file",
                        f"file={upload}",
                        "--file",
                        f"file={second_upload}",
                    ]
                )
            plan = json.loads((artifacts / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual(rc, 0)
            self.assertEqual(plan["body"]["mode"], "multipart")
            self.assertEqual(len(plan["body"]["files"]), 2)
            request.assert_not_called()

    def test_documented_free_form_property_filter_expands_query(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = write_basic_env(root)
            artifacts = root / "property-delete-plan"
            with patch("requests.Session.request") as request:
                rc, _, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--artifacts-dir",
                        str(artifacts),
                        "software",
                        "delete-remote-links-by-property",
                        "--params",
                        "accountId=account-123",
                        "--params",
                        "repoId=repo-345",
                    ]
                )
            plan = json.loads((artifacts / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual(plan["query"], {"accountId": "account-123", "repoId": "repo-345"})
            request.assert_not_called()

    def test_wildcard_json_body_gets_a_real_content_type(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = write_basic_env(root)
            body = root / "columns.json"
            body.write_text('["summary", "status"]', encoding="utf-8")
            artifacts = root / "columns-plan"
            rc, _, _ = run_cli(
                [
                    "--env-file",
                    str(env),
                    "--artifacts-dir",
                    str(artifacts),
                    "platform",
                    "set-issue-navigator-default-columns",
                    "--body-file",
                    str(body),
                ]
            )
            plan = json.loads((artifacts / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual(rc, 0)
            self.assertEqual(plan["body"]["content_type"], "application/json")


if __name__ == "__main__":
    unittest.main()
