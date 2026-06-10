from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from stripe_api_tool.cli import main


def _write_env(tmpdir: str, *, api_key: str) -> str:
    p = Path(tmpdir) / ".env"
    p.write_text("\n".join([f"STRIPE_API_KEY={api_key}", "STRIPE_TIMEOUT_S=30"]) + "\n", encoding="utf-8")
    return str(p)


def _run_plan(*, env_file: str) -> dict:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(
            [
                "--output",
                "json",
                "--env-file",
                env_file,
                "api",
                "post-customers",
                "--data",
                "name=Alice",
            ]
        )
    payload = json.loads(buf.getvalue())
    if rc != 0:
        raise AssertionError(payload)
    return payload


class TestIdempotency(unittest.TestCase):
    def test_derived_idempotency_is_stable_for_same_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = _write_env(td, api_key="sk_test_dummy_123")
            p1 = _run_plan(env_file=env_file)["plan"]
            p2 = _run_plan(env_file=env_file)["plan"]
            self.assertEqual(p1.get("stable_hash"), p2.get("stable_hash"))
            self.assertEqual(p1.get("idempotency_key"), p2.get("idempotency_key"))

