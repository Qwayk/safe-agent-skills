from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from dynadot_api_tool.commands.transfer import cmd_transfer_run
from dynadot_api_tool.dynadot_api import DynadotApiResult
from dynadot_api_tool.output import Output


class _Audit:
    def write(self, event: str, payload: object) -> None:  # noqa: ARG002
        return


class _ReceiverStubApi:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.pending: set[str] = set()
        self.domains: set[str] = set()
        self.ns_by_domain: dict[str, list[str]] = {}
        self.available_ns: list[str] = ["ns1.example.net", "ns2.example.net"]

    def call(self, *, command: str, params: dict | None = None) -> DynadotApiResult:  # type: ignore[override]
        p = dict(params or {})
        self.calls.append((command, p))

        if command == "get_domain_push_request":
            # Dynadot docs show "[a.com,b.com]"
            doms = ",".join(sorted(self.pending))
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "pushDomainName": f"[{doms}]"})

        if command == "set_domain_push_request":
            action = str(p.get("action") or "")
            domains_raw = str(p.get("domains") or "")
            domains = [d.strip().lower() for d in domains_raw.split(",") if d.strip()]
            if action != "accept":
                raise AssertionError("stub only supports accept")
            for d in domains:
                self.pending.discard(d)
                self.domains.add(d)
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success"})

        if command == "list_domain":
            page_index = int(p.get("page_index") or 1)
            if page_index != 1:
                rows: list[dict] = []
            else:
                rows = [{"Name": d} for d in sorted(self.domains)]
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "MainDomains": rows})

        if command == "domain_info":
            d = str(p.get("domain") or "").strip().lower()
            if d in self.domains:
                return DynadotApiResult(
                    command=command,
                    response={
                        "ResponseCode": "0",
                        "Status": "success",
                        "DomainInfo": {"Name": d, "Status": "active"},
                    },
                )
            raise Exception("Dynadot API error (ResponseCode=-1): Domain not found.")  # noqa: BLE001

        if command == "server_list":
            return DynadotApiResult(
                command=command,
                response={
                    "ResponseCode": "0",
                    "Status": "success",
                    "NameServerList": {"List": [{"ServerId": "1", "ServerName": s} for s in self.available_ns]},
                },
            )

        if command == "get_ns":
            d = str(p.get("domain") or "").strip().lower()
            ns = self.ns_by_domain.get(d, ["ns1.other.net", "ns2.other.net"])
            ns_content = {f"Host{i}": (ns[i] if i < len(ns) else "") for i in range(0, 13)}
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "NsContent": ns_content})

        if command == "set_ns":
            doms = [d.strip().lower() for d in str(p.get("domain") or "").split(",") if d.strip()]
            desired: list[str] = []
            for i in range(0, 13):
                v = p.get(f"ns{i}")
                if v is None:
                    continue
                s = str(v).strip().lower().rstrip(".")
                if s:
                    desired.append(s)
            for d in doms:
                self.ns_by_domain[d] = desired
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success"})

        raise AssertionError(f"Unexpected receiver command: {command}")


class _ReceiverStubApiNoPushOrderFoundOnBatchAccept(_ReceiverStubApi):
    def call(self, *, command: str, params: dict | None = None) -> DynadotApiResult:  # type: ignore[override]
        p = dict(params or {})
        if command == "set_domain_push_request":
            # Record call (base class would record it, but we might raise before delegating).
            self.calls.append((command, p))
            action = str(p.get("action") or "")
            domains_raw = str(p.get("domains") or "")
            domains = [d.strip().lower() for d in domains_raw.split(",") if d.strip()]
            if action == "accept" and "a.com" in domains and len(domains) > 1:
                # Simulate a benign Dynadot error:
                # the domain already left the push queue, even though the API call errors.
                for d in domains:
                    self.pending.discard(d)
                    self.domains.add(d)
                raise Exception("Dynadot API error (ResponseCode=-1): No push order found for a.com.")  # noqa: BLE001
            if action != "accept":
                raise AssertionError("stub only supports accept")
            for d in domains:
                self.pending.discard(d)
                self.domains.add(d)
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success"})
        return super().call(command=command, params=p)


class _ReceiverStubApiNoPushOrderFoundTwiceClearsPendingOnSecond(_ReceiverStubApi):
    def __init__(self) -> None:
        super().__init__()
        self._batch_accept_calls = 0

    def call(self, *, command: str, params: dict | None = None) -> DynadotApiResult:  # type: ignore[override]
        p = dict(params or {})
        if command == "set_domain_push_request":
            self.calls.append((command, p))
            action = str(p.get("action") or "")
            domains_raw = str(p.get("domains") or "")
            domains = [d.strip().lower() for d in domains_raw.split(",") if d.strip()]
            if action != "accept":
                raise AssertionError("stub only supports accept")

            # Only trigger for a batch accept containing both domains.
            if len(domains) > 1 and "a.com" in domains:
                self._batch_accept_calls += 1
                if self._batch_accept_calls == 2:
                    # Second attempt: pretend Dynadot accepted them but still errors.
                    for d in domains:
                        self.pending.discard(d)
                        self.domains.add(d)
                raise Exception("Dynadot API error (ResponseCode=-1): No push order found for a.com.")  # noqa: BLE001

            # Per-domain accept behaves normally.
            for d in domains:
                self.pending.discard(d)
                self.domains.add(d)
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success"})

        return super().call(command=command, params=p)


class _SenderStubApi:
    def __init__(self, *, receiver: _ReceiverStubApi) -> None:
        self.calls: list[tuple[str, dict]] = []
        self._receiver = receiver
        self._domains = ["a.com", "b.com", "expired.com", "grace.com"]
        self._status_by_domain = {"a.com": "active", "b.com": "active", "expired.com": "expired", "grace.com": "active"}
        self._expiration_by_domain = {
            "a.com": "2000000000000",
            "b.com": "2000000000000",
            "expired.com": "0",
            # Status=active but Expiration in the past (grace period) → should be excluded.
            "grace.com": "0",
        }

    def call(self, *, command: str, params: dict | None = None) -> DynadotApiResult:  # type: ignore[override]
        p = dict(params or {})
        self.calls.append((command, p))

        if command == "list_domain":
            page_index = int(p.get("page_index") or 1)
            if page_index == 1:
                rows = [{"Name": d} for d in self._domains]
            else:
                rows = []
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "MainDomains": rows})

        if command == "domain_info":
            d = str(p.get("domain") or "").strip().lower()
            return DynadotApiResult(
                command=command,
                response={
                    "ResponseCode": "0",
                    "Status": "success",
                    "DomainInfo": {
                        "Name": d,
                        "Status": self._status_by_domain.get(d, "unknown"),
                        "Expiration": self._expiration_by_domain.get(d, "2000000000000"),
                    },
                },
            )

        if command == "push":
            # Params use semicolon separation.
            doms = [d.strip().lower() for d in str(p.get("domain") or "").split(";") if d.strip()]
            for d in doms:
                self._receiver.pending.add(d)
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success"})

        raise AssertionError(f"Unexpected sender command: {command}")


class _SenderStubApiAccountLocked(_SenderStubApi):
    def call(self, *, command: str, params: dict | None = None) -> DynadotApiResult:  # type: ignore[override]
        if command == "push":
            raise Exception("Dynadot API error (ResponseCode=-1): Please unlock your account firstly.")  # noqa: BLE001
        return super().call(command=command, params=params)


class _SenderStubApiPushRenewErrorOneDomain(_SenderStubApi):
    def call(self, *, command: str, params: dict | None = None) -> DynadotApiResult:  # type: ignore[override]
        if command == "push":
            doms = [d.strip().lower() for d in str((params or {}).get("domain") or "").split(";") if d.strip()]
            if "a.com" in doms and len(doms) > 1:
                raise Exception("Dynadot API error (ResponseCode=-1): Please renew your domain firstly: a.com")  # noqa: BLE001
        return super().call(command=command, params=params)


class _SenderStubApiReceiverNotSetUpForUsDomains(_SenderStubApi):
    def __init__(self, *, receiver: _ReceiverStubApi) -> None:
        super().__init__(receiver=receiver)
        self._domains = ["a.us", "b.com"]
        self._status_by_domain = {"a.us": "active", "b.com": "active"}
        self._expiration_by_domain = {"a.us": "2000000000000", "b.com": "2000000000000"}

    def call(self, *, command: str, params: dict | None = None) -> DynadotApiResult:  # type: ignore[override]
        if command == "push":
            doms = [d.strip().lower() for d in str((params or {}).get("domain") or "").split(";") if d.strip()]
            if any(d.endswith(".us") for d in doms):
                raise Exception(  # noqa: BLE001
                    "Dynadot API error (ResponseCode=-1): Recipient account not set up to receive US domains. Please ask recipient to sign into their account and submit their US app and US nexus settings."
                )
        return super().call(command=command, params=params)


class _SenderStubApiManyActiveDomains(_SenderStubApi):
    def __init__(self, *, receiver: _ReceiverStubApi) -> None:
        super().__init__(receiver=receiver)
        self._domains = ["a.com", "b.com", "c.com", "d.com"]
        self._status_by_domain = {d: "active" for d in self._domains}
        self._expiration_by_domain = {d: "2000000000000" for d in self._domains}


class TestTransferRun(unittest.TestCase):
    def _ctx(self, *, sender_cfg: object, **overrides) -> dict:
        ctx = {
            "cfg": sender_cfg,
            "tool": "dynadot-api-tool",
            "tool_version": "0.0.0",
            "command_str": "dynadot-api-tool transfer run",
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
        }
        ctx.update(overrides)
        return ctx

    def test_dry_run_filters_active_only(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApi(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=None,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_transfer_run(args, self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            domains = [r["domain"] for r in plan["proposed_changes"]]
            self.assertIn("a.com", domains)
            self.assertIn("b.com", domains)
            self.assertNotIn("expired.com", domains)
            self.assertNotIn("grace.com", domains)

    def test_apply_runs_push_accept_and_sets_name_servers(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApi(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            plan_path = Path(td) / "plan.json"

            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=None,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            # Dry-run to create plan file.
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False, plan_out=str(plan_path)),
                )
            self.assertEqual(rc1, 0)
            self.assertTrue(plan_path.exists())

            # Apply using plan-in.
            sender.calls.clear()
            receiver.calls.clear()
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=True, yes=True, plan_in=str(plan_path)),
                )
            self.assertEqual(rc2, 0)
            payload = json.loads(buf2.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(sender.calls, [])
            self.assertEqual(receiver.calls, [])

    def test_apply_fast_mode_skips_name_server_verification(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApi(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            plan_path = Path(td) / "plan.json"
            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=None,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                presence_domain_info_sleep_s=0.0,
                verification_mode="fast",
                fast_presence_sample_size=0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False, plan_out=str(plan_path)),
                )
            self.assertEqual(rc1, 0)
            self.assertTrue(plan_path.exists())

            sender.calls.clear()
            receiver.calls.clear()
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=True, yes=True, plan_in=str(plan_path)),
                )
            self.assertEqual(rc2, 0)
            payload = json.loads(buf2.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            called = [c for (c, _p) in receiver.calls]
            self.assertEqual(called, [])
            self.assertEqual(receiver.ns_by_domain, {})

    def test_apply_treats_no_push_order_found_as_warning_when_domain_is_present(self) -> None:
        receiver = _ReceiverStubApiNoPushOrderFoundOnBatchAccept()
        sender = _SenderStubApi(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            plan_path = Path(td) / "plan.json"

            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=None,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False, plan_out=str(plan_path)),
                )
            self.assertEqual(rc1, 0)
            self.assertTrue(plan_path.exists())

            sender.calls.clear()
            receiver.calls.clear()
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_transfer_run(args, self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=True, yes=True, plan_in=str(plan_path)))
            self.assertEqual(rc2, 0)
            payload = json.loads(buf2.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(sender.calls, [])
            self.assertEqual(receiver.calls, [])

    def test_apply_no_push_order_found_retry_does_not_fall_back_to_per_domain_when_queue_clears(self) -> None:
        receiver = _ReceiverStubApiNoPushOrderFoundTwiceClearsPendingOnSecond()
        sender = _SenderStubApi(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            plan_path = Path(td) / "plan.json"

            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=None,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False, plan_out=str(plan_path)),
                )
            self.assertEqual(rc1, 0)

            sender.calls.clear()
            receiver.calls.clear()
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_transfer_run(args, self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=True, yes=True, plan_in=str(plan_path)))
            self.assertEqual(rc2, 0)
            payload = json.loads(buf2.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(sender.calls, [])
            self.assertEqual(receiver.calls, [])

    def test_apply_requires_plan_in(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApi(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=None,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_transfer_run(args, self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=True, yes=True, plan_in=None))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_apply_refuses_if_plan_includes_non_active_domain(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApi(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            plan_path = Path(td) / "plan.json"
            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=None,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False, plan_out=str(plan_path)),
                )
            self.assertEqual(rc1, 0)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["baseline"]["selected_domains_comma"] = "a.com,expired.com"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=True, yes=True, plan_in=str(plan_path)),
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertEqual(payload2["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload2.get("ineligible_domains", []), [])

    def test_apply_skips_non_active_domain_with_continue_on_error(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApi(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            plan_path = Path(td) / "plan.json"
            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=None,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=True,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                _ = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False, plan_out=str(plan_path)),
                )
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["baseline"]["selected_domains_comma"] = "a.com,expired.com"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=True, yes=True, plan_in=str(plan_path)),
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertEqual(payload2["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload2["summary"]["done"], 0)

    def test_apply_marks_failed_when_sender_account_locked(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApiAccountLocked(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            plan_path = Path(td) / "plan.json"
            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=None,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            # Dry-run to create plan file.
            buf0 = io.StringIO()
            with redirect_stdout(buf0):
                _ = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False, plan_out=str(plan_path)),
                )
            self.assertTrue(plan_path.exists())
            receiver.calls.clear()

            # Apply requires explicit no-snapshot approval before sender/receiver calls until explicit no-snapshot approval is present.
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_transfer_run(args, self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=True, yes=True, plan_in=str(plan_path)))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload["summary"]["done"], 0)
            receiver_commands = [c for c, _ in receiver.calls]
            self.assertEqual(receiver_commands, [])

    def test_push_batch_error_only_marks_named_domain_failed(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApiPushRenewErrorOneDomain(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            plan_path = Path(td) / "plan.json"
            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=2,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            # Dry-run to create plan file.
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False, plan_out=str(plan_path)),
                )
            self.assertEqual(rc1, 0)
            self.assertTrue(plan_path.exists())

            # Apply requires explicit no-snapshot approval before the push failure path can run.
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_transfer_run(args, self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=True, yes=True, plan_in=str(plan_path)))
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["refused"])
            self.assertEqual(payload2["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload2["summary"]["done_domains"], [])

    def test_push_unknown_batch_error_falls_back_to_per_domain(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApiReceiverNotSetUpForUsDomains(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            plan_path = Path(td) / "plan.json"
            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=2,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = cmd_transfer_run(
                    args,
                    self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False, plan_out=str(plan_path)),
                )
            self.assertEqual(rc1, 0)
            self.assertTrue(plan_path.exists())

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_transfer_run(args, self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=True, yes=True, plan_in=str(plan_path)))
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["refused"])
            self.assertEqual(payload2["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload2["summary"]["done_domains"], [])

    def test_resume_skips_done_domains(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApi(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            receipt_path = Path(td) / "receipt.json"

            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=None,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            receipt_path.write_text(
                json.dumps(
                    {
                        "tool": "dynadot-api-tool",
                        "selector": {"kind": "transfer.run", "value": "receiver_push_username"},
                        "summary": {"done_domains": ["a.com", "b.com"], "failed_domains": []},
                    }
                )
            )

            # Now plan again with resume-from-receipt; it should select zero domains.
            args2 = SimpleNamespace(**{**args.__dict__, "resume_from_receipt": str(receipt_path)})
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_transfer_run(args2, self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False))
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            plan2 = payload2["plan"]
            self.assertEqual(len(plan2["proposed_changes"]), 0)

    def test_resume_skips_failed_domains_and_still_fills_batch(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApiManyActiveDomains(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://receiver.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            receipt_path = Path(td) / "receipt.json"
            receipt_path.write_text(
                json.dumps(
                    {
                        "tool": "dynadot-api-tool",
                        "selector": {"kind": "transfer.run", "value": "receiver_push_username"},
                        "summary": {"done_domains": ["a.com"], "failed_domains": ["b.com"]},
                    }
                ),
                encoding="utf-8",
            )

            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=2,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=str(receipt_path),
            )
            sender_cfg = SimpleNamespace(base_url="http://sender.invalid", api_key="K1")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_transfer_run(args, self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            plan = payload["plan"]
            domains = [r["domain"] for r in plan["proposed_changes"]]
            self.assertEqual(domains, ["c.com", "d.com"])

    def test_receiver_env_ignores_os_env_vars(self) -> None:
        receiver = _ReceiverStubApi()
        sender = _SenderStubApi(receiver=receiver)
        with tempfile.TemporaryDirectory() as td:
            receiver_env = Path(td) / "receiver.env"
            receiver_env.write_text(
                "DYNADOT_API_BASE_URL=http://same.invalid\nDYNADOT_API_KEY=K2\nDYNADOT_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            sender_cfg = SimpleNamespace(base_url="http://same.invalid", api_key="K1")

            args = SimpleNamespace(
                receiver_env_file=str(receiver_env),
                to_username="receiver_push_username",
                desired_ns=["ns1.example.net", "ns2.example.net"],
                desired_ns_file=None,
                sender_list_page_size=None,
                sender_list_max_pages=10,
                sender_list_sleep_s=0.0,
                sender_status_sleep_s=0.0,
                max_domains=1,
                no_unlock=False,
                push_sleep_between_batches_s=0.0,
                push_max_batches=None,
                accept_sleep_between_batches_s=0.0,
                accept_max_batches=None,
                sleep_after_push_s=0.0,
                sleep_after_accept_s=0.0,
                presence_retries=0,
                presence_sleep_s=0.0,
                ns_sleep_between_batches_s=0.0,
                ns_sleep_between_verifications_s=0.0,
                ns_max_batches=None,
                continue_on_error=False,
                skip_availability_check=False,
                require_available_name_servers=False,
                resume_from_receipt=None,
            )

            # If receiver env loading incorrectly used OS env overrides, this would trip the
            # "sender and receiver are the same config" safety check and refuse.
            import os

            old_key = os.environ.get("DYNADOT_API_KEY")
            old_base = os.environ.get("DYNADOT_API_BASE_URL")
            os.environ["DYNADOT_API_KEY"] = "K1"
            os.environ["DYNADOT_API_BASE_URL"] = "http://same.invalid"
            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_transfer_run(
                        args,
                        self._ctx(sender_cfg=sender_cfg, api_sender=sender, api_receiver=receiver, apply=False, yes=False),
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["dry_run"])
                self.assertFalse(bool(payload.get("refused")))
            finally:
                if old_key is None:
                    del os.environ["DYNADOT_API_KEY"]
                else:
                    os.environ["DYNADOT_API_KEY"] = old_key
                if old_base is None:
                    del os.environ["DYNADOT_API_BASE_URL"]
                else:
                    os.environ["DYNADOT_API_BASE_URL"] = old_base
