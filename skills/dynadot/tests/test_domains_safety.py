from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from dynadot_api_tool.commands.domains import cmd_domains_name_servers_set, cmd_domains_push, cmd_push_requests_accept
from dynadot_api_tool.output import Output


class _Audit:
    def write(self, event: str, payload: object) -> None:  # noqa: ARG002
        return


class TestDomainsSafety(unittest.TestCase):
    def _ctx(self, **overrides):
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
        }
        ctx.update(overrides)
        return ctx

    def test_domains_push_apply_requires_plan_in(self) -> None:
        args = SimpleNamespace(to_username="receiver", domain=["a.com"], domains_file=None, no_unlock=False)
        ctx = self._ctx(apply=True, yes=True, plan_in=None, command_str="dynadot-api-tool --apply --yes domains push")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_domains_push(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])

    def test_push_requests_accept_apply_requires_plan_in(self) -> None:
        args = SimpleNamespace(domain=["a.com"], domains_file=None)
        ctx = self._ctx(apply=True, yes=True, plan_in=None, command_str="dynadot-api-tool --apply --yes domains push-requests accept")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_push_requests_accept(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])

    def test_nameservers_set_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            diff_path = f"{td}/diff.json"
            with open(diff_path, "w", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "params": {"desired_name_servers": ["ns1.example.com", "ns2.example.com"]},
                            "changes": [{"domain": "a.com", "from": ["ns1.old.com", "ns2.old.com"], "to": ["ns1.example.com", "ns2.example.com"]}],
                        }
                    )
                )

            args = SimpleNamespace(
                diff_in=diff_path,
                sleep_between_batches_s=0.0,
                max_batches=None,
                max_domains=None,
                continue_on_error=False,
            )
            ctx = self._ctx(apply=True, yes=True, plan_in=None, command_str="dynadot-api-tool --apply --yes domains name-servers set")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_name_servers_set(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
