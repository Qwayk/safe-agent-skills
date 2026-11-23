from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from requests.exceptions import Timeout

from giantpanda_api_tool.cli import main
from giantpanda_api_tool.commands.domains import DOMAINS_ADD_MAX_DOMAINS, DOMAINS_ADD_PATH
from giantpanda_api_tool.safety_state import read_json_file, write_private_json


def _mock_json_response(payload: object, status: int = 200):
    data = payload

    def _response(*_args, **_kwargs):  # noqa: ANN001
        body = json.dumps(data).encode("utf-8")
        return SimpleNamespace(
            status_code=status,
            content=body,
            url="https://account.giantpanda.com" + DOMAINS_ADD_PATH,
            headers={"content-type": "application/json"},
        )

    return _response


def _created(*names: str) -> dict[str, Any]:
    created = list(names) or ["example.com"]
    return {"created": created, "existing": [], "created_count": len(created), "existing_count": 0}


def _mock_non_json_response():
    def _response(*_args, **_kwargs):  # noqa: ANN001
        return SimpleNamespace(
            status_code=200,
            content=b"not-json",
            url="https://account.giantpanda.com" + DOMAINS_ADD_PATH,
            headers={"content-type": "text/plain"},
        )

    return _response


class TestDomainsAdd(unittest.TestCase):
    def _write_env(self, path: str, token: str | None = None) -> None:
        with open(path, "w", encoding="utf-8") as f:
            if token is not None:
                f.write(f"GIANTPANDA_API_TOKEN={token}\n")

    def _run(self, cwd: str, argv: list[str], env_path: str) -> tuple[int, dict[str, Any]]:
        previous = os.getcwd()
        try:
            os.chdir(cwd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path] + argv)
        finally:
            os.chdir(previous)
        payload = cast(dict[str, Any], json.loads(buf.getvalue()))
        return rc, payload

    def _state_plan_path(self, cwd: str, payload: dict[str, Any]) -> str:
        plan_out = str(payload["plan_out"])
        if os.path.isabs(plan_out):
            return plan_out
        return os.path.join(cwd, plan_out)

    def _state_receipt_path(self, cwd: str, payload: dict[str, Any]) -> str:
        receipt_out = str(payload["receipt_out"])
        if os.path.isabs(receipt_out):
            return receipt_out
        return os.path.join(cwd, receipt_out)

    def test_domains_add_deduplicates_with_normalized_domains(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path)
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                rc, payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--dry-run",
                        "--domain",
                        " Example.COM ",
                        "--domain",
                        "example.com",
                        "--domain",
                        "EXAMPLE.com",
                    ],
                    env_path,
                )
            self.assertEqual(rc, 0)
            self.assertEqual(payload["plan"]["request_body"]["domains"], [{"name": "example.com"}])
            self.assertEqual(payload["plan"]["safety"]["duplicates_removed"], ["example.com"])
            plan_path = self._state_plan_path(td, payload)
            self.assertTrue(os.path.exists(plan_path))

    def test_domains_add_plan_includes_no_snapshot_warning_and_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path)
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, payload = self._run(
                    td,
                    ["domains", "add", "--dry-run", "--domain", "Example.COM"],
                    env_path,
                )
            plan = payload["plan"]
            self.assertEqual(
                plan["safety_warning"],
                "No snapshot, rollback, restore, or undo is available for this operation.",
            )
            self.assertFalse(plan["snapshot_available"])
            self.assertFalse(plan["rollback_supported"])
            self.assertEqual(
                plan["apply_requirements"],
                {
                    "apply": "--apply required",
                    "plan_in": "--plan-in required",
                    "approve_plan": "--approve-plan with exact plan id required",
                    "ack_no_snapshot": "--ack-no-snapshot required",
                    "snapshot_available": False,
                    "rollback_supported": False,
                    "safety_warning": "No snapshot, rollback, restore, or undo is available for this operation.",
                },
            )

    def test_domains_add_rejects_invalid_domains(self) -> None:
        invalid = [
            "http://example.com",
            "https://example.com/path",
            "example.com:443",
            "user@example.com",
            "*.example.com",
            "example.com/path",
            "example .com",
            ".example.com",
            "example.com.",
            "-bad.com",
            "bad-.com",
            "exa..mple.com",
            "a" * 64 + ".com",
            "",
            "héllo.com",
            "192.168.0.1",
            "example.123",
        ]
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path)
            for value in invalid:
                with patch("giantpanda_api_tool.http.requests.Session.request"):
                    rc, payload = self._run(td, ["domains", "add", "--domain", value], env_path)
                self.assertEqual(rc, 1, msg=value)
                self.assertEqual(payload["error_type"], "ValidationError", msg=value)

    def test_default_state_paths_are_anchored_to_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_dir = os.path.join(td, "configs")
            os.makedirs(env_dir)
            env_path = os.path.join(env_dir, ".env")
            self._write_env(env_path)
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, payload = self._run(td, ["domains", "add", "--domain", "example.com"], env_path)
            env_dir = os.path.realpath(env_dir)
            expected_plan = os.path.join(env_dir, ".state", "plans", f"{payload['plan']['plan_id']}.json")
            self.assertEqual(payload["plan_out"], expected_plan)
            self.assertTrue(os.path.exists(payload["plan_out"]))
            self.assertTrue(payload["plan_out"].startswith(os.path.join(env_dir, ".state", "plans")))

    def test_domains_add_rejects_raw_and_unique_bounded_input(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path)
            raw_domains = [f"site{idx}.example.com" for idx in range(DOMAINS_ADD_MAX_DOMAINS + 1)]
            rc, payload = self._run(
                td,
                ["domains", "add"] + [value for domain in raw_domains for value in ("--domain", domain)],
                env_path,
            )
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

            duplicated = ["example.com"] * (DOMAINS_ADD_MAX_DOMAINS + 1)
            rc, payload = self._run(
                td,
                ["domains", "add"] + [value for domain in duplicated for value in ("--domain", domain)],
                env_path,
            )
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_domains_add_default_dry_run_never_calls_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path)
            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                rc, payload = self._run(
                    td,
                    ["domains", "add", "--domain", "example.com"],
                    env_path,
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(req.call_count, 0)

    def test_domains_add_plan_and_receipt_are_private_0600(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token="token_abc")
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                rc, dry_payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--domain",
                        "example.com",
                        "--domain",
                        "shop.example.com",
                    ],
                    env_path,
                )
            self.assertEqual(rc, 0)
            plan_path = self._state_plan_path(td, dry_payload)
            self.assertEqual(os.stat(plan_path).st_mode & 0o777, 0o600)

            with patch(
                "giantpanda_api_tool.http.requests.Session.request",
                side_effect=_mock_json_response(_created("example.com", "shop.example.com")),
            ) as req:
                rc_apply, apply_payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--approve-plan",
                        dry_payload["plan"]["plan_id"],
                        "--ack-no-snapshot",
                        "--domain",
                        "example.com",
                        "--domain",
                        "shop.example.com",
                    ],
                    env_path,
                )
            self.assertEqual(rc_apply, 0)
            self.assertEqual(req.call_count, 1)
            receipt_path = self._state_receipt_path(td, apply_payload)
            self.assertEqual(os.stat(receipt_path).st_mode & 0o777, 0o600)

    def test_domains_add_one_send_per_approval(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token="token_abc")
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(td, ["domains", "add", "--domain", "example.com"], env_path)
            plan_path = self._state_plan_path(td, dry_payload)
            apply_args = [
                "domains",
                "add",
                "--apply",
                "--plan-in",
                plan_path,
                "--approve-plan",
                dry_payload["plan"]["plan_id"],
                "--ack-no-snapshot",
                "--domain",
                "example.com",
            ]

            with patch(
                "giantpanda_api_tool.http.requests.Session.request",
                side_effect=_mock_json_response(_created()),
            ) as req:
                rc, first = self._run(td, apply_args, env_path)
                again, second = self._run(td, apply_args + ["--receipt-out", "another.json"], env_path)
            self.assertEqual(rc, 0)
            self.assertEqual(again, 1)
            self.assertEqual(req.call_count, 1)
            self.assertEqual(second["error_type"], "ApprovalAlreadyUsed")
            self.assertEqual(first["receipt_out"], second["receipt_out"])
            self.assertFalse(Path(td, "another.json").exists())

    def test_domains_add_new_plan_preserves_canonical_request_with_new_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path)
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, payload1 = self._run(
                    td,
                    ["domains", "add", "--domain", "shop.example.com", "--domain", "example.com"],
                    env_path,
                )
                _, payload2 = self._run(
                    td,
                    ["domains", "add", "--domain", "example.com", "--domain", "SHOP.EXAMPLE.COM"],
                    env_path,
                )
            self.assertNotEqual(payload1["plan"]["plan_id"], payload2["plan"]["plan_id"])
            self.assertEqual(payload1["plan"]["request_body"]["domains"], payload2["plan"]["request_body"]["domains"])

    def test_domains_add_apply_gate_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token="token_abc")
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(td, ["domains", "add", "--domain", "example.com"], env_path)
            plan_path = self._state_plan_path(td, dry_payload)

            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                rc, err = self._run(
                    td,
                [
                    "domains",
                    "add",
                    "--apply",
                    "--approve-plan",
                    dry_payload["plan"]["plan_id"],
                    "--ack-no-snapshot",
                    "--domain",
                        "example.com",
                    ],
                    env_path,
                )
            self.assertEqual(rc, 1)
            self.assertEqual(err["error_type"], "SafetyRequirementError")
            self.assertEqual(req.call_count, 0)

            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                rc, err = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--approve-plan",
                        "bad-plan-id",
                        "--ack-no-snapshot",
                        "--domain",
                        "example.com",
                    ],
                    env_path,
                )
            self.assertEqual(rc, 1)
            self.assertEqual(err["error_type"], "SafetyRequirementError")
            self.assertEqual(req.call_count, 0)

            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                rc, err = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--approve-plan",
                        dry_payload["plan"]["plan_id"],
                        "--domain",
                        "example.com",
                    ],
                    env_path,
                )
            self.assertEqual(rc, 1)
            self.assertEqual(err["error_type"], "SafetyRequirementError")
            self.assertEqual(req.call_count, 0)

    def test_domains_add_rejects_tampered_or_drifted_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token="token_abc")
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(td, ["domains", "add", "--domain", "example.com"], env_path)
            plan_path = self._state_plan_path(td, dry_payload)

            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                tampered = read_json_file(plan_path)
                tampered["host"] = "https://evil.example.com"
                with open(plan_path, "w", encoding="utf-8") as f:
                    json.dump(tampered, f)
            rc, err = self._run(
                td,
                [
                    "domains",
                    "add",
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--approve-plan",
                        dry_payload["plan"]["plan_id"],
                        "--ack-no-snapshot",
                        "--domain",
                        "example.com",
                    ],
                env_path,
            )
            self.assertEqual(rc, 1)
            self.assertEqual(err["error_type"], "InvalidPlanError")
            self.assertEqual(req.call_count, 0)

    def test_domains_add_rejects_plans_with_drifted_safety_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token="token_abc")
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(td, ["domains", "add", "--domain", "example.com"], env_path)
            plan_path = self._state_plan_path(td, dry_payload)
            base_plan = read_json_file(plan_path)

            tamper_cases = [
                lambda plan: plan.update({"snapshot_available": True}),
                lambda plan: plan.update({"rollback_supported": True}),
                lambda plan: plan.update({"safety_warning": "Changed warning"}),
                lambda plan: plan.update({"apply_requirements": {"apply": "--apply required"}}),
            ]

            for mutator in tamper_cases:
                with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                    tampered = json.loads(json.dumps(base_plan))
                    mutator(tampered)
                    with open(plan_path, "w", encoding="utf-8") as f:
                        json.dump(tampered, f)
                    rc, err = self._run(
                        td,
                        [
                            "domains",
                            "add",
                            "--apply",
                            "--plan-in",
                            plan_path,
                            "--approve-plan",
                            dry_payload["plan"]["plan_id"],
                            "--ack-no-snapshot",
                            "--domain",
                            "example.com",
                        ],
                        env_path,
                    )
                self.assertEqual(rc, 1)
                self.assertEqual(err["error_type"], "InvalidPlanError")
                self.assertEqual(req.call_count, 0)

            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                rc, err = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--approve-plan",
                        dry_payload["plan"]["plan_id"],
                        "--ack-no-snapshot",
                        "--domain",
                        "example.org",
                    ],
                    env_path,
                )
            self.assertEqual(rc, 1)
            self.assertEqual(err["error_type"], "InvalidPlanError")
            self.assertEqual(req.call_count, 0)

    def test_domains_add_rejects_plans_with_drifted_safety_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token="token_abc")
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(td, ["domains", "add", "--domain", "example.com"], env_path)
            plan_path = self._state_plan_path(td, dry_payload)
            base_plan = read_json_file(plan_path)

            tamper_cases = [
                lambda plan: plan["safety"].update({"max_domains": DOMAINS_ADD_MAX_DOMAINS - 1}),
                lambda plan: plan["safety"].update({"duplicates_removed": ["example.net"]}),
                lambda plan: plan.update({"safety": {"max_domains": DOMAINS_ADD_MAX_DOMAINS}}),
                lambda plan: plan.update({"safety": []}),
                lambda plan: plan.pop("safety"),
            ]

            for mutator in tamper_cases:
                with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                    tampered = json.loads(json.dumps(base_plan))
                    mutator(tampered)
                    with open(plan_path, "w", encoding="utf-8") as f:
                        json.dump(tampered, f)
                    rc, err = self._run(
                        td,
                        [
                            "domains",
                            "add",
                            "--apply",
                            "--plan-in",
                            plan_path,
                            "--approve-plan",
                            dry_payload["plan"]["plan_id"],
                            "--ack-no-snapshot",
                            "--domain",
                            "example.com",
                        ],
                        env_path,
                    )
                self.assertEqual(rc, 1)
                self.assertEqual(err["error_type"], "InvalidPlanError")
                self.assertEqual(req.call_count, 0)

    def test_domains_add_rejects_tampered_duplicates_removed_with_matching_duplicate_apply_args(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token="token_abc")
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--domain",
                        "example.com",
                        "--domain",
                        "shop.example.com",
                        "--domain",
                        "shop.example.com",
                    ],
                    env_path,
                )
            plan_path = self._state_plan_path(td, dry_payload)
            plan = read_json_file(plan_path)
            plan["safety"].update({"duplicates_removed": ["example.com"]})
            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(plan, f)

            with patch("giantpanda_api_tool.http.requests.Session.request") as req:
                rc, err = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--approve-plan",
                        dry_payload["plan"]["plan_id"],
                        "--ack-no-snapshot",
                        "--domain",
                        "example.com",
                        "--domain",
                        "example.com",
                        "--domain",
                        "shop.example.com",
                    ],
                    env_path,
                )
            self.assertEqual(rc, 1)
            self.assertEqual(err["error_type"], "InvalidPlanError")
            self.assertEqual(req.call_count, 0)

    def test_domains_add_posts_exact_body_and_receipt_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token="token_apply")
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(td, ["domains", "add", "--domain", "example.com"], env_path)
            plan_path = self._state_plan_path(td, dry_payload)

            with patch(
                "giantpanda_api_tool.http.requests.Session.request",
                side_effect=_mock_json_response(_created()),
            ) as req:
                rc, payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--approve-plan",
                        dry_payload["plan"]["plan_id"],
                        "--ack-no-snapshot",
                        "--domain",
                        "example.com",
                    ],
                    env_path,
                )
            self.assertEqual(rc, 0)
            called = req.call_args.kwargs
            self.assertEqual(called["method"], "POST")
            self.assertEqual(called["url"], "https://account.giantpanda.com" + DOMAINS_ADD_PATH)
            self.assertEqual(called["json"], {"domains": [{"name": "example.com"}]})
            receipt = read_json_file(self._state_receipt_path(td, payload))
            self.assertEqual(receipt["verification"], {"created": ["example.com"], "existing": [], "needs_check": []})
            self.assertEqual(payload["provider"]["verification"], receipt["verification"])

    def test_domains_add_apply_response_parse_failure(self) -> None:
        token = "sentinel_parse_token"
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token=token)
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(td, ["domains", "add", "--domain", "example.com"], env_path)
            plan_path = self._state_plan_path(td, dry_payload)
            with patch("giantpanda_api_tool.http.requests.Session.request", side_effect=_mock_non_json_response()):
                _, payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--approve-plan",
                        dry_payload["plan"]["plan_id"],
                        "--ack-no-snapshot",
                        "--domain",
                        "example.com",
                    ],
                    env_path,
                )
            self.assertEqual(payload["ok"], False)
            self.assertEqual(payload["error_type"], "ResponseParseError")
            self.assertTrue(payload["applied_may_have_occurred"])
            self.assertNotIn("retry", payload["error"].lower())
            receipt = read_json_file(self._state_receipt_path(td, payload))
            self.assertFalse(receipt["verification_available"])
            self.assertTrue(receipt["applied_may_have_occurred"])
            self.assertNotIn(token, json.dumps(payload))
            self.assertNotIn(token, json.dumps(receipt))

    def test_domains_add_apply_receipt_write_failure(self) -> None:
        token = "sentinel_receipt_write_token"
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token=token)
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(td, ["domains", "add", "--domain", "example.com"], env_path)
            plan_path = self._state_plan_path(td, dry_payload)
            response_payload = _created()
            def fail_after_reservation(path, value, *, exclusive=False):
                if exclusive:
                    write_private_json(path, value, exclusive=True)
                else:
                    raise OSError("write denied")

            with patch("giantpanda_api_tool.commands.domains.write_private_json", side_effect=fail_after_reservation):
                with patch(
                    "giantpanda_api_tool.http.requests.Session.request",
                    side_effect=_mock_json_response(response_payload),
                ) as req:
                    _, payload = self._run(
                        td,
                        [
                            "domains",
                            "add",
                            "--apply",
                            "--plan-in",
                            plan_path,
                            "--approve-plan",
                            dry_payload["plan"]["plan_id"],
                            "--ack-no-snapshot",
                            "--domain",
                            "example.com",
                        ],
                        env_path,
                    )
            self.assertEqual(req.call_count, 1)
            self.assertEqual(payload["ok"], False)
            self.assertEqual(payload["error_type"], "ReceiptWriteError")
            self.assertTrue(payload["applied"])
            self.assertEqual(payload["provider"]["verification"]["created"], ["example.com"])
            saved = read_json_file(payload["receipt_out"])
            self.assertEqual(saved["status"], "pending")
            self.assertNotIn("retry", payload["error"].lower())
            self.assertNotIn(token, json.dumps(payload))

    def test_domains_add_apply_with_duplicates_from_plan_accepts_unique_args(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token="token_abc")
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--domain",
                        "Example.COM",
                        "--domain",
                        "example.com",
                        "--domain",
                        "shop.example.com",
                    ],
                    env_path,
                )
            plan_path = self._state_plan_path(td, dry_payload)

            with patch(
                "giantpanda_api_tool.http.requests.Session.request",
                side_effect=_mock_json_response(_created("example.com", "shop.example.com")),
            ) as req:
                rc, payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--approve-plan",
                        dry_payload["plan"]["plan_id"],
                        "--ack-no-snapshot",
                        "--domain",
                        "example.com",
                        "--domain",
                        "shop.example.com",
                    ],
                    env_path,
                )
            self.assertEqual(rc, 0)
            self.assertEqual(req.call_count, 1)
            self.assertEqual(payload["command"], "domains add")

    def test_domains_add_explicit_plan_and_receipt_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            plan_path = os.path.join(td, "state", "custom", "myplan.json")
            receipt_path = os.path.join(td, "state", "custom", "myreceipt.json")
            self._write_env(env_path, token="token_abc")

            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--dry-run",
                        "--plan-out",
                        plan_path,
                        "--domain",
                        "example.com",
                    ],
                    env_path,
                )
            self.assertEqual(dry_payload["plan_out"], plan_path)
            self.assertTrue(os.path.exists(plan_path))

            with patch(
                "giantpanda_api_tool.http.requests.Session.request",
                side_effect=_mock_json_response(_created()),
            ):
                _, apply_payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--apply",
                        "--plan-in",
                        plan_path,
                        "--approve-plan",
                        dry_payload["plan"]["plan_id"],
                        "--ack-no-snapshot",
                        "--receipt-out",
                        receipt_path,
                        "--domain",
                        "example.com",
                    ],
                    env_path,
                )
            self.assertEqual(apply_payload["receipt_out"], receipt_path)
            self.assertTrue(os.path.exists(receipt_path))

    def _prepare_apply(self, td: str, env_path: str, *names: str) -> list[str]:
        args = ["domains", "add"]
        for name in names:
            args.extend(["--domain", name])
        rc, preview = self._run(td, args, env_path)
        self.assertEqual(rc, 0)
        return [
            *args, "--apply", "--ack-no-snapshot", "--plan-in", preview["plan_out"],
            "--approve-plan", preview["plan"]["plan_id"],
        ]

    def test_domains_add_refuses_changed_credentials_and_accepts_original(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, "account.env")
            self._write_env(env_path, "first-test-token")
            apply_args = self._prepare_apply(td, env_path, "example.com")
            self._write_env(env_path, "second-test-token")
            shifted = Path(td, "other", "account.env")
            shifted.parent.mkdir()
            self._write_env(str(shifted), "first-test-token")
            with patch(
                "giantpanda_api_tool.http.requests.Session.request", side_effect=_mock_json_response(_created()),
            ) as request:
                self.assertEqual(self._run(td, apply_args, env_path)[0], 1)
                self.assertEqual(self._run(td, apply_args, str(shifted))[0], 1)
                request.assert_not_called()
                self._write_env(env_path, "first-test-token")
                self.assertEqual(self._run(td, apply_args, env_path)[0], 0)
                self.assertEqual(request.call_args.kwargs["headers"]["Authorization"], "Token first-test-token")

    def test_domains_add_records_lost_reply_before_refusing_repeat(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, "test-token")
            apply_args = self._prepare_apply(td, env_path, "example.com")
            with patch("giantpanda_api_tool.http.requests.Session.request", side_effect=Timeout) as request:
                rc, first = self._run(td, apply_args, env_path)
                again, second = self._run(td, apply_args, env_path)
                self.assertEqual(request.call_count, 1)
            self.assertEqual(rc, 1)
            self.assertEqual(again, 1)
            self.assertEqual(second["error_type"], "ApprovalAlreadyUsed")
            saved = read_json_file(first["receipt_out"])
            self.assertEqual(saved["status"], "needs_check")
            self.assertTrue(saved["applied_may_have_occurred"])

    def test_domains_add_shows_created_existing_and_unconfirmed_domains(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, "test-token")
            apply_args = self._prepare_apply(td, env_path, "example.com", "example.net", "example.org")
            reply = {"created": ["example.com"], "existing": ["example.net"], "created_count": 1, "existing_count": 1}
            with patch("giantpanda_api_tool.http.requests.Session.request", side_effect=_mock_json_response(reply)):
                rc, payload = self._run(td, apply_args, env_path)
            self.assertEqual(rc, 1)
            self.assertFalse(payload["applied"])
            self.assertEqual(payload["receipt"]["verification"], {
                "created": ["example.com"], "existing": ["example.net"], "needs_check": ["example.org"],
            })

    def test_domains_add_checks_output_before_sending(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, "test-token")
            apply_args = self._prepare_apply(td, env_path, "example.com")
            plan_path = apply_args[apply_args.index("--plan-in") + 1]
            for protected in (env_path, plan_path):
                with patch("giantpanda_api_tool.http.requests.Session.request") as request:
                    rc, _ = self._run(td, [*apply_args, "--receipt-out", protected], env_path)
                    self.assertEqual(rc, 1)
                    request.assert_not_called()

    def test_domains_add_stops_if_it_cannot_save_receipt_before_sending(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, "test-token")
            apply_args = self._prepare_apply(td, env_path, "example.com")
            with (
                patch("giantpanda_api_tool.commands.domains.write_private_json", side_effect=OSError),
                patch("giantpanda_api_tool.http.requests.Session.request") as request,
            ):
                rc, payload = self._run(td, apply_args, env_path)
            request.assert_not_called()
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ReceiptWriteError")
            self.assertFalse(Path(payload["receipt_out"]).exists())

    def test_domains_add_requires_a_fresh_plan_after_an_unbound_preview_or_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path)
            preview_args = self._prepare_apply(td, env_path, "example.com")
            self._write_env(env_path, "test-token")
            with patch("giantpanda_api_tool.http.requests.Session.request") as request:
                self.assertEqual(self._run(td, preview_args, env_path)[0], 1)
                request.assert_not_called()
            before = self._prepare_apply(td, env_path, "example.com")
            with patch(
                "giantpanda_api_tool.http.requests.Session.request",
                side_effect=_mock_json_response({"error": "Example rejection"}, status=400),
            ):
                rc, rejected = self._run(td, before, env_path)
            self.assertEqual(rc, 1)
            self.assertEqual(rejected["receipt"]["status"], "rejected")
            self.assertFalse(rejected["applied_may_have_occurred"])
            after = self._prepare_apply(td, env_path, "example.com")
            with patch(
                "giantpanda_api_tool.http.requests.Session.request", side_effect=_mock_json_response(_created()),
            ) as request:
                self.assertEqual(self._run(td, after, env_path)[0], 0)
                self.assertEqual(request.call_count, 1)

    def test_domains_add_no_token_leak(self) -> None:
        token = "sentinel_token_123"
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            self._write_env(env_path, token=token)
            with patch("giantpanda_api_tool.http.requests.Session.request"):
                _, dry_payload = self._run(td, ["domains", "add", "--domain", "example.com"], env_path)
            self.assertNotIn(token, json.dumps(dry_payload))

            with patch(
                "giantpanda_api_tool.http.requests.Session.request",
                side_effect=_mock_json_response(_created()),
            ):
                _, apply_payload = self._run(
                    td,
                    [
                        "domains",
                        "add",
                        "--apply",
                        "--plan-in",
                        self._state_plan_path(td, dry_payload),
                        "--approve-plan",
                        dry_payload["plan"]["plan_id"],
                        "--ack-no-snapshot",
                        "--domain",
                        "example.com",
                    ],
                    env_path,
                )
            self.assertNotIn(token, json.dumps(apply_payload))
            self.assertNotIn(
                token,
                json.dumps(read_json_file(self._state_receipt_path(td, apply_payload))),
            )
