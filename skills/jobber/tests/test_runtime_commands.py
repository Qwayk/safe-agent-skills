from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from jobber_safe_agent_cli.cli import main
from jobber_safe_agent_cli.commands.common import mutation_requires_ack_irreversible, mutation_requires_no_snapshot
from jobber_safe_agent_cli.schema_registry import mutation_fields, query_fields


class _FakeClient:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def execute(self, query: str, variables=None) -> dict:
        return {"data": {"ok": True, "query": query}, "variables": variables}


class _NeverCalledClient:
    def __init__(self, *args, **kwargs) -> None:
        self.called = False

    def execute(self, query: str, variables=None) -> dict:
        self.called = True
        raise RuntimeError("GraphQL should not be called")


class _NeverConstructedClient:
    def __init__(self, *args, **kwargs) -> None:
        raise AssertionError("GraphQL client should not be constructed")

    def execute(self, query: str, variables=None) -> dict:
        raise AssertionError("GraphQL should not be called")


class TestRuntimeCommands(unittest.TestCase):
    @staticmethod
    def _high_risk_mutation() -> str:
        for op in mutation_fields():
            if mutation_requires_no_snapshot(op.name):
                return op.name
        return mutation_fields()[0].name

    def test_read_named_query_invokes_graphql(self) -> None:
        read_op = query_fields()[0].name
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "JOBBER_API_BASE_URL=http://example.invalid\nJOBBER_API_TOKEN=token\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.read.GraphQLClient", _FakeClient):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "read",
                            read_op,
                            "--selection",
                            "__typename",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["operation"], read_op)
            self.assertFalse(payload["dry_run"])
            self.assertIn(read_op, payload["graphql"]["document"])

    def test_read_named_query_requires_token_before_http(self) -> None:
        read_op = query_fields()[0].name
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("JOBBER_API_BASE_URL=http://example.invalid\n", encoding="utf-8")

            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.read.GraphQLClient", _NeverCalledClient):
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "--output", "json", "read", read_op])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Missing access token", payload["error"])

    def test_write_named_mutation_defaults_to_plan(self) -> None:
        write_op = mutation_fields()[0].name
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("JOBBER_API_BASE_URL=http://example.invalid\n", encoding="utf-8")

            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.write.GraphQLClient", _FakeClient):
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "--output", "json", "write", write_op])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], write_op)
            self.assertEqual(payload["plan"]["mutation"], write_op)
            self.assertIn("arguments_hash", payload["plan"])

    def test_write_requires_apply_yes(self) -> None:
        write_op = mutation_fields()[0].name
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("JOBBER_API_BASE_URL=http://example.invalid\n", encoding="utf-8")

            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.write.GraphQLClient", _NeverCalledClient):
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "--apply", "--output", "json", "write", write_op])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["refused"])
            self.assertIn("requires --plan-in", payload["reasons"][0])

    def test_write_apply_yes_without_plan_in_refuses_before_http(self) -> None:
        write_op = "clientCreate"
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "JOBBER_API_BASE_URL=http://example.invalid\nJOBBER_API_TOKEN=token\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.write.GraphQLClient", _NeverConstructedClient):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "--apply",
                            "--yes",
                            "write",
                            write_op,
                            "--args-json",
                            '{"input":{"firstName":"Sample","lastName":"Client"}}',
                            "--selection",
                            "client { id name } userErrors { message path }",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("requires --plan-in", payload["reasons"][0])

    def test_write_high_risk_apply_refuses_without_ack_no_snapshot(self) -> None:
        write_op = self._high_risk_mutation()
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            plan_path = Path(d) / "plan.json"
            env_path.write_text(
                "JOBBER_API_BASE_URL=http://example.invalid\nJOBBER_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with redirect_stdout(io.StringIO()):
                rc_plan = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "write",
                        write_op,
                    ]
                )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(plan_path.exists())

            flags = [
                "--plan-in",
                str(plan_path),
            ]
            if mutation_requires_ack_irreversible(write_op):
                flags.extend(["--ack-irreversible"])

            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.write.GraphQLClient", _NeverConstructedClient):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "--apply",
                            "--yes",
                            *flags,
                            "write",
                            write_op,
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("ack-no-snapshot", payload["reasons"][0])

    def test_write_high_risk_apply_with_matching_plan_and_ack_no_snapshot_executes(self) -> None:
        write_op = self._high_risk_mutation()
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            plan_path = Path(d) / "plan.json"
            receipt_path = Path(d) / "receipt.json"
            env_path.write_text(
                "JOBBER_API_BASE_URL=http://example.invalid\nJOBBER_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with redirect_stdout(io.StringIO()):
                rc_plan = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "write",
                        write_op,
                    ]
                )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(plan_path.exists())

            flags = [
                "--plan-in",
                str(plan_path),
                "--ack-no-snapshot",
            ]
            if mutation_requires_ack_irreversible(write_op):
                flags.extend(["--ack-irreversible"])

            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.write.GraphQLClient", _FakeClient):
                with redirect_stdout(buf):
                    rc_apply = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "--apply",
                            "--yes",
                            "--receipt-out",
                            str(receipt_path),
                            *flags,
                            "write",
                            write_op,
                        ]
                    )
            self.assertEqual(rc_apply, 0)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["plan"]["snapshot_status"], "No snapshot available")
            self.assertIn("recovery_notes", payload["plan"])
            self.assertEqual(payload["snapshot_status"], "No snapshot available")
            self.assertIn("recovery_notes", payload)
            self.assertTrue(receipt_path.exists())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["snapshot_status"], "No snapshot available")
            self.assertIn("recovery_notes", receipt)
            self.assertIn("recovery", receipt)

    def test_write_apply_from_matching_plan_executes(self) -> None:
        write_op = "clientCreate"
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            plan_path = Path(d) / "plan.json"
            env_path.write_text(
                "JOBBER_API_BASE_URL=http://example.invalid\nJOBBER_API_TOKEN=token\n",
                encoding="utf-8",
            )
            args_json = '{"input":{"firstName":"Sample","lastName":"Client"}}'
            selection = "client { id name } userErrors { message path }"

            with redirect_stdout(io.StringIO()):
                rc_plan = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "write",
                        write_op,
                        "--args-json",
                        args_json,
                        "--selection",
                        selection,
                    ]
                )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(plan_path.exists())

            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.write.GraphQLClient", _FakeClient):
                with redirect_stdout(buf):
                    rc_apply = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                            "write",
                            write_op,
                            "--args-json",
                            args_json,
                            "--selection",
                            selection,
                        ]
                    )
            self.assertEqual(rc_apply, 0)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["operation"], write_op)
            self.assertIn("result", payload)

    def test_write_apply_refuses_plan_drift_before_http(self) -> None:
        write_op = "clientCreate"
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            plan_path = Path(d) / "plan.json"
            bad_plan_path = Path(d) / "bad-plan.json"
            env_path.write_text(
                "JOBBER_API_BASE_URL=http://example.invalid\nJOBBER_API_TOKEN=token\n",
                encoding="utf-8",
            )
            args_json = '{"input":{"firstName":"Sample","lastName":"Client"}}'
            selection = "client { id name } userErrors { message path }"

            with redirect_stdout(io.StringIO()):
                rc_plan = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "write",
                        write_op,
                        "--args-json",
                        args_json,
                        "--selection",
                        selection,
                    ]
                )
            self.assertEqual(rc_plan, 0)
            base_plan = json.loads(plan_path.read_text(encoding="utf-8"))

            mutations = [
                ("env_fingerprint", "https://other.invalid/api/graphql"),
                ("operation", "clientDelete"),
                ("mutation", "clientDelete"),
                ("intended_mutation", "clientDelete"),
                ("arguments_hash", "bad-hash"),
                ("selection_hash", "bad-hash"),
            ]
            for key, value in mutations:
                with self.subTest(key=key):
                    plan = json.loads(json.dumps(base_plan))
                    plan[key] = value
                    bad_plan_path.write_text(json.dumps(plan), encoding="utf-8")

                    buf = io.StringIO()
                    with patch("jobber_safe_agent_cli.commands.write.GraphQLClient", _NeverConstructedClient):
                        with redirect_stdout(buf):
                            rc = main(
                                [
                                    "--env-file",
                                    str(env_path),
                                    "--output",
                                    "json",
                                    "--apply",
                                    "--yes",
                                    "--plan-in",
                                    str(bad_plan_path),
                                    "write",
                                    write_op,
                                    "--args-json",
                                    args_json,
                                    "--selection",
                                    selection,
                                ]
                            )
                    self.assertEqual(rc, 0)
                    payload = json.loads(buf.getvalue())
                    self.assertTrue(payload["refused"])

            plan = json.loads(json.dumps(base_plan))
            plan["graphql"]["document_hash"] = "bad-hash"
            bad_plan_path.write_text(json.dumps(plan), encoding="utf-8")
            buf = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.write.GraphQLClient", _NeverConstructedClient):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(bad_plan_path),
                            "write",
                            write_op,
                            "--args-json",
                            args_json,
                            "--selection",
                            selection,
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertTrue(json.loads(buf.getvalue())["refused"])
