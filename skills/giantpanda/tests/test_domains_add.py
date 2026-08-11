from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from giantpanda_api_tool.cli import main
from giantpanda_api_tool.commands.domains import DOMAINS_ADD_MAX_DOMAINS, DOMAINS_ADD_PATH
from giantpanda_api_tool.safety_state import read_json_file


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
                side_effect=_mock_json_response({"added": ["example.com", "shop.example.com"]}),
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

    def test_domains_add_default_receipt_path_is_unique_per_apply(self) -> None:
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
                side_effect=_mock_json_response({"verification": "ok"}),
            ) as req:
                _, first_apply = self._run(td, apply_args, env_path)
                _, second_apply = self._run(td, apply_args, env_path)
            self.assertEqual(req.call_count, 2)
            self.assertNotEqual(first_apply["receipt_out"], second_apply["receipt_out"])
            self.assertTrue(os.path.exists(self._state_receipt_path(td, first_apply)))
            self.assertTrue(os.path.exists(self._state_receipt_path(td, second_apply)))
            self.assertNotEqual(
                os.stat(self._state_receipt_path(td, first_apply)).st_ino,
                os.stat(self._state_receipt_path(td, second_apply)).st_ino,
            )

    def test_domains_add_exact_plan_binding_is_deterministic(self) -> None:
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
            self.assertEqual(payload1["plan"]["plan_id"], payload2["plan"]["plan_id"])
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
                side_effect=_mock_json_response({"verification": "ok"}),
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
            self.assertEqual(receipt["verification"], {"verification": "ok"})
            self.assertEqual(payload["provider"]["verification"], {"verification": "ok"})

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
            response_payload = {"verification": "ok"}
            with patch("giantpanda_api_tool.commands.domains.write_private_json", side_effect=OSError("write denied")):
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
            self.assertEqual(payload["provider"]["verification"], response_payload)
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
                side_effect=_mock_json_response({"verification": "ok"}),
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
                side_effect=_mock_json_response({"verification": "ok"}),
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
                side_effect=_mock_json_response({"verification": "ok"}),
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
