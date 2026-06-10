from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from dynadot_api_tool.commands.domains import (
    cmd_domains_name_servers_diff,
    cmd_domains_name_servers_export,
    cmd_domains_name_servers_set,
)
from dynadot_api_tool.dynadot_api import DynadotApiResult
from dynadot_api_tool.output import Output


class _Audit:
    def write(self, event: str, payload: object) -> None:  # noqa: ARG002
        return


class _StubApi:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.ns_by_domain: dict[str, list[str]] = {
            "a.com": ["ns1.example.net", "ns2.example.net"],
            "b.com": ["ns1.example.net", "ns2.example.net"],
            "c.com": ["ns1.other.net", "ns2.other.net"],
        }
        self.available_servers: list[str] = ["ns1.example.net", "ns2.example.net", "ns1.other.net", "ns2.other.net"]
        self.fail_set_ns = False

    def call(self, *, command: str, params: dict | None = None) -> DynadotApiResult:  # type: ignore[override]
        p = dict(params or {})
        self.calls.append((command, p))
        if command == "server_list":
            return DynadotApiResult(
                command=command,
                response={
                    "ResponseCode": "0",
                    "Status": "success",
                    "NameServerList": {"List": [{"ServerId": str(i + 1), "ServerName": s} for i, s in enumerate(self.available_servers)]},
                },
            )
        if command == "get_ns":
            domain = str(p.get("domain") or "").strip().lower()
            ns = self.ns_by_domain.get(domain, [])
            ns_content = {f"Host{i}": (ns[i] if i < len(ns) else "") for i in range(0, 13)}
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "NsContent": ns_content})
        if command == "set_ns":
            if self.fail_set_ns:
                raise RuntimeError("simulated set_ns failure")
            domain_list = str(p.get("domain") or "").strip()
            domains = [d.strip().lower() for d in domain_list.split(",") if d.strip()]
            desired: list[str] = []
            for i in range(0, 13):
                v = p.get(f"ns{i}")
                if v is None:
                    continue
                s = str(v).strip().lower().rstrip(".")
                if s:
                    desired.append(s)
            for d in domains:
                self.ns_by_domain[d] = desired
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success"})
        raise AssertionError(f"Unexpected command: {command}")


class TestNameServersCommands(unittest.TestCase):
    def _ctx(self, *, api: object, **overrides) -> dict:
        ctx = {
            "cfg": SimpleNamespace(base_url="http://example.invalid", api_key=None),
            "tool": "dynadot-api-tool",
            "tool_version": "0.0.0",
            "command_str": "dynadot-api-tool",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "timeout_s": 30.0,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _Audit(),
            "artifacts_dir": None,
            "api": api,
        }
        ctx.update(overrides)
        return ctx

    def test_export_writes_file_and_normalizes(self) -> None:
        api = _StubApi()
        with tempfile.TemporaryDirectory() as td:
            out_path = f"{td}/ns.export.json"
            args = SimpleNamespace(domains_file=None, domains_export_in=None, sleep_s=0.0, max_domains=None, out=out_path)
            # Use a domains-export-in path instead of a domains file.
            domains_list_path = f"{td}/domains.list.json"
            with open(domains_list_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps({"domains": [{"Name": "A.com"}, {"Name": "c.com"}]}))
            args.domains_export_in = domains_list_path

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_name_servers_export(args, self._ctx(api=api))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["out_path"], out_path)
            with open(out_path, "r", encoding="utf-8") as fp:
                export = json.loads(fp.read())
            self.assertEqual(export["command"], "get_ns")
            self.assertEqual(export["count"], 2)
            rows = {r["domain"]: r["name_servers"] for r in export["results"] if r.get("ok")}
            self.assertEqual(rows["a.com"], ["ns1.example.net", "ns2.example.net"])

    def test_diff_counts_changes(self) -> None:
        api = _StubApi()
        with tempfile.TemporaryDirectory() as td:
            current_path = f"{td}/current.json"
            export_args = SimpleNamespace(domains_file=None, domains_export_in=None, sleep_s=0.0, max_domains=None, out=current_path)
            domains_list_path = f"{td}/domains.list.json"
            with open(domains_list_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps({"domains": [{"Name": "a.com"}, {"Name": "b.com"}, {"Name": "c.com"}]}))
            export_args.domains_export_in = domains_list_path
            export_buf = io.StringIO()
            with redirect_stdout(export_buf):
                _ = cmd_domains_name_servers_export(export_args, self._ctx(api=api))

            diff_out = f"{td}/diff.json"
            diff_args = SimpleNamespace(current_in=current_path, desired_ns=["ns1.example.net", "ns2.example.net"], desired_ns_file=None, out=diff_out)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_name_servers_diff(diff_args, self._ctx(api=api))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["to_change"], 1)
            with open(diff_out, "r", encoding="utf-8") as fp:
                diff_obj = json.loads(fp.read())
            self.assertEqual(diff_obj["to_change"], 1)
            self.assertEqual(len(diff_obj["changes"]), 1)
            self.assertEqual(diff_obj["changes"][0]["domain"], "c.com")

    def test_set_dry_run_emits_plan(self) -> None:
        api = _StubApi()
        with tempfile.TemporaryDirectory() as td:
            diff_path = f"{td}/diff.json"
            with open(diff_path, "w", encoding="utf-8") as fp:
                fp.write(
                    json.dumps(
                        {
                            "params": {"desired_name_servers": ["ns1.example.net", "ns2.example.net"]},
                            "changes": [
                                {
                                    "domain": "c.com",
                                    "from": ["ns1.other.net", "ns2.other.net"],
                                    "to": ["ns1.example.net", "ns2.example.net"],
                                }
                            ],
                        }
                    )
                )
            plan_out = f"{td}/plan.json"
            args = SimpleNamespace(
                diff_in=diff_path,
                sleep_between_batches_s=0.0,
                sleep_between_verifications_s=0.0,
                max_batches=None,
                max_domains=None,
                continue_on_error=False,
                resume_from_receipt=None,
                skip_availability_check=False,
                require_available_name_servers=False,
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_name_servers_set(args, self._ctx(api=api, apply=False, yes=False, plan_out=plan_out))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)
            self.assertEqual(payload["plan_out"], plan_out)
            with open(plan_out, "r", encoding="utf-8") as fp:
                plan = json.loads(fp.read())
            self.assertIn("baseline", plan)
            self.assertIn("diff_sha256", plan["baseline"])

    def test_set_dry_run_prefers_changes_list_when_to_change_is_int(self) -> None:
        api = _StubApi()
        with tempfile.TemporaryDirectory() as td:
            diff_path = f"{td}/diff.json"
            with open(diff_path, "w", encoding="utf-8") as fp:
                fp.write(
                    json.dumps(
                        {
                            "params": {"desired_name_servers": ["ns1.example.net", "ns2.example.net"]},
                            "to_change": 1,
                            "changes": [
                                {
                                    "domain": "c.com",
                                    "from": ["ns1.other.net", "ns2.other.net"],
                                    "to": ["ns1.example.net", "ns2.example.net"],
                                }
                            ],
                        }
                    )
                )
            args = SimpleNamespace(
                diff_in=diff_path,
                sleep_between_batches_s=0.0,
                sleep_between_verifications_s=0.0,
                max_batches=None,
                max_domains=None,
                continue_on_error=False,
                resume_from_receipt=None,
                skip_availability_check=False,
                require_available_name_servers=False,
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_name_servers_set(args, self._ctx(api=api, apply=False, yes=False, plan_out=None))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["count"], 1)

    def test_set_dry_run_marks_server_list_check_as_advisory(self) -> None:
        api = _StubApi()
        api.available_servers = []
        with tempfile.TemporaryDirectory() as td:
            diff_path = f"{td}/diff.json"
            with open(diff_path, "w", encoding="utf-8") as fp:
                fp.write(
                    json.dumps(
                        {
                            "params": {"desired_name_servers": ["ns1.example.net", "ns2.example.net"]},
                            "changes": [
                                {
                                    "domain": "c.com",
                                    "from": ["ns1.other.net", "ns2.other.net"],
                                    "to": ["ns1.example.net", "ns2.example.net"],
                                }
                            ],
                        }
                    )
                )
            args = SimpleNamespace(
                diff_in=diff_path,
                sleep_between_batches_s=0.0,
                sleep_between_verifications_s=0.0,
                max_batches=None,
                max_domains=None,
                continue_on_error=False,
                resume_from_receipt=None,
                skip_availability_check=False,
                require_available_name_servers=False,
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_name_servers_set(args, self._ctx(api=api, apply=False, yes=False, plan_out=None))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["dry_run"])
            self.assertTrue(payload["availability_check"]["advisory_only"])
            self.assertIn("Cloudflare", payload["availability_check"]["warning"])

    def test_set_apply_requires_plan_in(self) -> None:
        api = _StubApi()
        with tempfile.TemporaryDirectory() as td:
            diff_path = f"{td}/diff.json"
            with open(diff_path, "w", encoding="utf-8") as fp:
                fp.write(
                    json.dumps(
                        {
                            "params": {"desired_name_servers": ["ns1.example.net", "ns2.example.net"]},
                            "changes": [
                                {
                                    "domain": "c.com",
                                    "from": ["ns1.other.net", "ns2.other.net"],
                                    "to": ["ns1.example.net", "ns2.example.net"],
                                }
                            ],
                        }
                    )
                )
            args = SimpleNamespace(
                diff_in=diff_path,
                sleep_between_batches_s=0.0,
                sleep_between_verifications_s=0.0,
                max_batches=None,
                max_domains=None,
                continue_on_error=False,
                resume_from_receipt=None,
                skip_availability_check=False,
                require_available_name_servers=False,
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_name_servers_set(args, self._ctx(api=api, apply=True, yes=True, plan_in=None))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])

    def test_set_apply_refuses_before_set_ns_calls(self) -> None:
        api = _StubApi()
        with tempfile.TemporaryDirectory() as td:
            diff_path = f"{td}/diff.json"
            with open(diff_path, "w", encoding="utf-8") as fp:
                fp.write(
                    json.dumps(
                        {
                            "params": {"desired_name_servers": ["ns1.example.net", "ns2.example.net"]},
                            "changes": [
                                {"domain": "a.com", "from": ["ns1.example.net", "ns2.example.net"], "to": ["ns1.example.net", "ns2.example.net"]},
                                {"domain": "b.com", "from": ["ns1.example.net", "ns2.example.net"], "to": ["ns1.example.net", "ns2.example.net"]},
                                {"domain": "c.com", "from": ["ns1.other.net", "ns2.other.net"], "to": ["ns1.example.net", "ns2.example.net"]},
                            ],
                        }
                    )
                )
            # Build the baseline expected by the apply path.
            from dynadot_api_tool.commands.domains import _sha256_file  # type: ignore[attr-defined]

            digest = _sha256_file(diff_path)
            baseline = {
                "diff_sha256": digest,
                "desired_name_servers_comma": "ns1.example.net,ns2.example.net",
                "domains_comma": "a.com,b.com,c.com",
                "sleep_between_batches_s": "0.0",
                "sleep_between_verifications_s": "",
                "max_batches": "",
                "max_domains": "2",
                "continue_on_error": "0",
                "availability_check_mode": "",
                "resume_receipt_sha256": "",
            }
            plan_path = f"{td}/plan.json"
            with open(plan_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps({"env_fingerprint": "http://example.invalid", "baseline": baseline}))
            args = SimpleNamespace(
                diff_in=diff_path,
                sleep_between_batches_s=0.0,
                sleep_between_verifications_s=0.0,
                max_batches=None,
                max_domains=2,
                continue_on_error=False,
                resume_from_receipt=None,
                skip_availability_check=False,
                require_available_name_servers=False,
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_name_servers_set(args, self._ctx(api=api, apply=True, yes=True, plan_in=plan_path))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(api.calls, [])

    def test_set_resume_from_receipt_skips_done_domains(self) -> None:
        api = _StubApi()
        with tempfile.TemporaryDirectory() as td:
            diff_path = f"{td}/diff.json"
            with open(diff_path, "w", encoding="utf-8") as fp:
                fp.write(
                    json.dumps(
                        {
                            "params": {"desired_name_servers": ["ns1.example.net", "ns2.example.net"]},
                            "changes": [
                                {"domain": "a.com", "from": ["ns1.other.net"], "to": ["ns1.example.net"]},
                                {"domain": "b.com", "from": ["ns1.other.net"], "to": ["ns1.example.net"]},
                            ],
                        }
                    )
                )
            from dynadot_api_tool.commands.domains import _sha256_file  # type: ignore[attr-defined]

            digest = _sha256_file(diff_path)
            receipt_path = f"{td}/receipt.json"
            with open(receipt_path, "w", encoding="utf-8") as fp:
                fp.write(
                    json.dumps(
                        {
                            "selector": {"kind": "domains.name_servers.set", "value": digest},
                            "preview": {"desired_name_servers": ["ns1.example.net", "ns2.example.net"]},
                            "verification": {"details": {"verified": {"a.com": True}}},
                            "diff_applied": [{"domain": "a.com", "to_name_servers": ["ns1.example.net", "ns2.example.net"]}],
                        }
                    )
                )
            plan_out = f"{td}/plan.json"
            receipt_sha = _sha256_file(receipt_path)
            args = SimpleNamespace(
                diff_in=diff_path,
                sleep_between_batches_s=0.0,
                sleep_between_verifications_s=0.0,
                max_batches=None,
                max_domains=None,
                continue_on_error=False,
                resume_from_receipt=receipt_path,
                skip_availability_check=False,
                require_available_name_servers=False,
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_name_servers_set(args, self._ctx(api=api, apply=False, yes=False, plan_out=plan_out))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["preview"]["skipped_already_done_count"], 1)
            self.assertEqual(payload["preview"]["count"], 1)
            self.assertEqual(payload["plan"]["baseline"]["resume_receipt_sha256"], receipt_sha)

    def test_set_apply_refuses_before_availability_check_when_before_state_missing(self) -> None:
        api = _StubApi()
        api.available_servers = ["ns1.other.net", "ns2.other.net"]
        with tempfile.TemporaryDirectory() as td:
            diff_path = f"{td}/diff.json"
            with open(diff_path, "w", encoding="utf-8") as fp:
                fp.write(
                    json.dumps(
                        {
                            "params": {"desired_name_servers": ["ns1.example.net", "ns2.example.net"]},
                            "changes": [{"domain": "c.com", "from": ["ns1.other.net"], "to": ["ns1.example.net"]}],
                        }
                    )
                )
            from dynadot_api_tool.commands.domains import _sha256_file  # type: ignore[attr-defined]

            digest = _sha256_file(diff_path)
            baseline = {
                "diff_sha256": digest,
                "desired_name_servers_comma": "ns1.example.net,ns2.example.net",
                "domains_comma": "c.com",
                "sleep_between_batches_s": "0.0",
                "sleep_between_verifications_s": "",
                "max_batches": "",
                "max_domains": "",
                "continue_on_error": "0",
                "availability_check_mode": "require",
                "resume_receipt_sha256": "",
            }
            plan_path = f"{td}/plan.json"
            with open(plan_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps({"env_fingerprint": "http://example.invalid", "baseline": baseline}))
            args = SimpleNamespace(
                diff_in=diff_path,
                sleep_between_batches_s=0.0,
                sleep_between_verifications_s=0.0,
                max_batches=None,
                max_domains=None,
                continue_on_error=False,
                resume_from_receipt=None,
                skip_availability_check=False,
                require_available_name_servers=True,
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_name_servers_set(args, self._ctx(api=api, apply=True, yes=True, plan_in=plan_path))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(api.calls, [])

    def test_set_apply_refusal_does_not_sleep_for_verification(self) -> None:
        api = _StubApi()
        with tempfile.TemporaryDirectory() as td:
            diff_path = f"{td}/diff.json"
            with open(diff_path, "w", encoding="utf-8") as fp:
                fp.write(
                    json.dumps(
                        {
                            "params": {"desired_name_servers": ["ns1.example.net", "ns2.example.net"]},
                            "changes": [
                                {"domain": "b.com", "from": ["ns1.other.net"], "to": ["ns1.example.net"]},
                                {"domain": "c.com", "from": ["ns1.other.net"], "to": ["ns1.example.net"]},
                            ],
                        }
                    )
                )
            from dynadot_api_tool.commands.domains import _sha256_file  # type: ignore[attr-defined]

            digest = _sha256_file(diff_path)
            baseline = {
                "diff_sha256": digest,
                "desired_name_servers_comma": "ns1.example.net,ns2.example.net",
                "domains_comma": "b.com,c.com",
                "sleep_between_batches_s": "0.0",
                "sleep_between_verifications_s": "0.5",
                "max_batches": "",
                "max_domains": "",
                "continue_on_error": "0",
                "availability_check_mode": "",
                "resume_receipt_sha256": "",
            }
            plan_path = f"{td}/plan.json"
            with open(plan_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps({"env_fingerprint": "http://example.invalid", "baseline": baseline}))
            args = SimpleNamespace(
                diff_in=diff_path,
                sleep_between_batches_s=0.0,
                sleep_between_verifications_s=0.5,
                max_batches=None,
                max_domains=None,
                continue_on_error=False,
                resume_from_receipt=None,
                skip_availability_check=False,
                require_available_name_servers=False,
            )
            buf = io.StringIO()
            with patch("dynadot_api_tool.commands.domains.time.sleep") as sleep_mock:
                with redirect_stdout(buf):
                    rc = cmd_domains_name_servers_set(args, self._ctx(api=api, apply=True, yes=True, plan_in=plan_path))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertFalse(sleep_mock.called)
            self.assertEqual(api.calls, [])
