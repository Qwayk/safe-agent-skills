from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from dynadot_api_tool.cli import build_parser, main
from dynadot_api_tool.commands.api3 import cmd_api3_call
from dynadot_api_tool.commands._api3_specs import API3_PARAM_SPECS
from dynadot_api_tool.config import Config
from dynadot_api_tool.dynadot_api import DynadotApiResult
from dynadot_api_tool.output import Output
from dynadot_api_tool.audit_log import AuditLogger


def _kebab(s: str) -> str:
    return s.replace("_", "-")


def _flag(s: str) -> str:
    return str(s).strip().lower().replace("_", "-")


def _list_bases_for_command(cmd: str) -> set[str]:
    # Only treat numeric-suffix params as list params when an index-0 key exists.
    rows = API3_PARAM_SPECS.get(cmd, [])
    bases_to_idxs: dict[str, set[int]] = {}
    for r in rows:
        name = str(r.get("name") or "")
        for i in range(len(name) - 1, -1, -1):
            if not name[i].isdigit():
                base = name[: i + 1]
                idx_s = name[i + 1 :]
                if idx_s:
                    try:
                        idx = int(idx_s)
                    except Exception:
                        idx = -1
                    if idx >= 0 and base and base[-1].isalpha():
                        bases_to_idxs.setdefault(base, set()).add(idx)
                break
    return {b for b, idxs in bases_to_idxs.items() if 0 in idxs}


def _minimal_api3_args_for_command(cmd: str) -> list[str]:
    rows = API3_PARAM_SPECS.get(cmd, [])
    list_bases = _list_bases_for_command(cmd)

    scalar_required: list[tuple[str, str]] = []
    list_required_idxs: dict[str, set[int]] = {}

    for r in rows:
        name = str(r.get("name") or "")
        required = bool(r.get("required"))
        sample = r.get("sample")
        sample_s = "x" if sample is None else str(sample)
        if not required:
            continue

        # numeric-suffix?
        base = None
        idx = None
        for i in range(len(name) - 1, -1, -1):
            if not name[i].isdigit():
                base = name[: i + 1]
                idx_s = name[i + 1 :]
                if idx_s:
                    try:
                        idx = int(idx_s)
                    except Exception:
                        idx = None
                break

        if base and idx is not None and base in list_bases:
            list_required_idxs.setdefault(base, set()).add(idx)
        else:
            scalar_required.append((name, sample_s))

    args: list[str] = ["api3", _kebab(cmd)]

    for base, idxs in sorted(list_required_idxs.items()):
        # Provide at least max required index + 1 values.
        count = max(idxs) + 1
        for i in range(count):
            args.extend([f"--{_flag(base)}", f"v{i+1}"])

    for name, sample in sorted(scalar_required):
        args.extend([f"--{_flag(name)}", sample])

    return args


class TestApi3Commands(unittest.TestCase):
    def test_official_command_snapshot_matches_generated_specs(self) -> None:
        root = Path(__file__).resolve().parents[1]
        official_path = root / "docs" / "official_commands.txt"
        official: set[str] = set()
        for raw in official_path.read_text(encoding="utf-8").splitlines():
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            official.add(s)

        self.assertEqual(official, set(API3_PARAM_SPECS.keys()))

    def test_all_api3_commands_are_registered_and_parseable(self) -> None:
        p = build_parser()
        for cmd in sorted(API3_PARAM_SPECS.keys()):
            argv = _minimal_api3_args_for_command(cmd)
            parsed = p.parse_args(argv)
            self.assertTrue(callable(getattr(parsed, "func", None)), cmd)

    def test_get_open_backorder_auctions_currency_is_optional(self) -> None:
        p = build_parser()
        parsed = p.parse_args(["api3", "get-open-backorder-auctions"])
        self.assertTrue(callable(getattr(parsed, "func", None)))

    def test_get_transfer_auth_code_is_write_capable_and_apply_gated(self) -> None:
        # Dynadot's request examples include params that can mutate state (e.g. regenerate the auth code
        # and/or unlock the domain for transfer), so this must follow the write safety contract.
        p = build_parser()
        parsed = p.parse_args(
            [
                "api3",
                "get-transfer-auth-code",
                "--domain",
                "example.com",
                "--new-code",
                "0",
                "--unlock-domain-for-transfer",
                "0",
            ]
        )
        self.assertTrue(bool(getattr(parsed, "write_capable", False)))

        class _Args:
            api3_command = "get_transfer_auth_code"
            domain = "example.com"
            new_code = "0"
            unlock_domain_for_transfer = "0"

        class _FakeApi:
            def __init__(self) -> None:
                self.calls: list[tuple[str, dict[str, str]]] = []

            def call(self, *, command: str, params: dict[str, str] | None = None) -> DynadotApiResult:
                self.calls.append((command, dict(params or {})))
                raise AssertionError("API call should not run when apply is refused due to missing --plan-in")

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = Config(base_url="http://example.invalid/api3.json", api_key="", timeout_s=30.0)
            fake_api = _FakeApi()
            ctx = {
                "cfg": cfg,
                "out": Output(mode="json"),
                "audit": AuditLogger(path=None, enabled=False),
                "tool": "dynadot-api-tool",
                "tool_version": "0.5.0",
                "command_str": "dynadot-api-tool api3 get-transfer-auth-code --domain example.com --new-code 0 --unlock-domain-for-transfer 0",
                "timeout_s": 30.0,
                "verbose": False,
                "ack_irreversible": False,
                "api": fake_api,
                "apply": True,
                "yes": True,
                "plan_out": None,
                "plan_in": None,
                "receipt_out": None,
                "artifacts_dir": root,
            }
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_api3_call(_Args(), ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", " ".join(payload.get("reasons") or []))
            self.assertEqual(fake_api.calls, [])

    def test_apply_without_plan_in_refuses_for_write_commands(self) -> None:
        # Ensure write safety: apply requires a reviewed plan file.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("DYNADOT_API_BASE_URL=http://example.invalid\nDYNADOT_TIMEOUT_S=30\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "api3",
                        "set-note",
                        "--domain",
                        "example.com",
                        "--note",
                        "hello",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_set_ns_apply_refuses_until_before_state_exists(self) -> None:
        class _Args:
            api3_command = "set_ns"
            domain = "example.com"
            ns = ["ns1.example.net", "ns2.example.net"]

        class _FakeApi:
            def __init__(self) -> None:
                self.calls: list[tuple[str, dict[str, str]]] = []

            def call(self, *, command: str, params: dict[str, str] | None = None) -> DynadotApiResult:
                p = dict(params or {})
                self.calls.append((command, p))
                if command == "set_ns":
                    return DynadotApiResult(command=command, response={"Status": "success", "ResponseCode": "0"})
                if command == "get_ns":
                    return DynadotApiResult(
                        command=command,
                        response={
                            "Status": "success",
                            "ResponseCode": "0",
                            "NsContent": {"Host0": "ns1.example.net", "Host1": "ns2.example.net"},
                        },
                    )
                raise AssertionError(f"Unexpected command: {command}")

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"

            cfg = Config(base_url="http://example.invalid/api3.json", api_key="K", timeout_s=30.0)
            fake_api = _FakeApi()

            ctx_base = {
                "cfg": cfg,
                "out": Output(mode="json"),
                "audit": AuditLogger(path=None, enabled=False),
                "tool": "dynadot-api-tool",
                "tool_version": "0.5.0",
                "command_str": "dynadot-api-tool api3 set-ns --domain example.com --ns0 ns1 --ns1 ns2",
                "timeout_s": 30.0,
                "verbose": False,
                "ack_irreversible": False,
                "api": fake_api,
            }

            # Dry-run first to produce a matching reviewed plan file.
            ctx_plan = dict(ctx_base)
            ctx_plan.update({"apply": False, "yes": False, "plan_out": str(plan_path), "plan_in": None, "receipt_out": None})
            buf0 = io.StringIO()
            with redirect_stdout(buf0):
                cmd_api3_call(_Args(), ctx_plan)
            self.assertTrue(plan_path.exists())

            # Apply from plan requires explicit no-snapshot approval before set_ns or verification calls.
            ctx_apply = dict(ctx_base)
            ctx_apply.update(
                {
                    "apply": True,
                    "yes": True,
                    "plan_out": None,
                    "plan_in": str(plan_path),
                    "receipt_out": str(receipt_path),
                }
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_api3_call(_Args(), ctx_apply)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            self.assertNotIn("receipt", payload)
            self.assertFalse(receipt_path.exists())
            self.assertEqual(fake_api.calls, [])

    def test_set_note_apply_refuses_until_before_state_exists(self) -> None:
        class _Args:
            api3_command = "set_note"
            domain = "example.com"
            note = "hello"

        class _FakeApi:
            def __init__(self) -> None:
                self.calls: list[tuple[str, dict[str, str]]] = []

            def call(self, *, command: str, params: dict[str, str] | None = None) -> DynadotApiResult:
                p = dict(params or {})
                self.calls.append((command, p))
                if command == "set_note":
                    return DynadotApiResult(command=command, response={"Status": "success", "ResponseCode": "0"})
                if command == "domain_info":
                    return DynadotApiResult(
                        command=command,
                        response={"Status": "success", "ResponseCode": "0", "DomainName": p.get("domain", "")},
                    )
                raise AssertionError(f"Unexpected command: {command}")

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"

            cfg = Config(base_url="http://example.invalid/api3.json", api_key="K", timeout_s=30.0)
            fake_api = _FakeApi()

            ctx_base = {
                "cfg": cfg,
                "out": Output(mode="json"),
                "audit": AuditLogger(path=None, enabled=False),
                "tool": "dynadot-api-tool",
                "tool_version": "0.5.0",
                "command_str": "dynadot-api-tool api3 set-note --domain example.com --note hello",
                "timeout_s": 30.0,
                "verbose": False,
                "ack_irreversible": False,
                "api": fake_api,
            }

            ctx_plan = dict(ctx_base)
            ctx_plan.update({"apply": False, "yes": False, "plan_out": str(plan_path), "plan_in": None, "receipt_out": None})
            buf0 = io.StringIO()
            with redirect_stdout(buf0):
                cmd_api3_call(_Args(), ctx_plan)
            self.assertTrue(plan_path.exists())

            ctx_apply = dict(ctx_base)
            ctx_apply.update({"apply": True, "yes": True, "plan_out": None, "plan_in": str(plan_path), "receipt_out": str(receipt_path)})
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_api3_call(_Args(), ctx_apply)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            self.assertNotIn("receipt", payload)
            self.assertFalse(receipt_path.exists())
            self.assertEqual(fake_api.calls, [])

    def test_irreversible_requires_ack_irreversible_after_plan_in(self) -> None:
        # Build a plan, then attempt apply without --ack-irreversible; should require explicit no-snapshot approval before any API call.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("DYNADOT_API_BASE_URL=http://example.invalid\nDYNADOT_TIMEOUT_S=30\n", encoding="utf-8")

            plan_path = root / "plan.json"

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "api3",
                        "register",
                        "--domain",
                        "example.com",
                        "--duration",
                        "1",
                        "--currency",
                        "USD",
                    ]
                )
            self.assertEqual(rc1, 0)
            self.assertTrue(plan_path.exists())

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "api3",
                        "register",
                        "--domain",
                        "example.com",
                        "--duration",
                        "1",
                        "--currency",
                        "USD",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertIn("ack-irreversible", " ".join(payload2.get("reasons") or []))
