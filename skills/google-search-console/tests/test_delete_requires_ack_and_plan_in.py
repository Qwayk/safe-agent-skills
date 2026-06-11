from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from gsc_api_tool.cli import main


class TestDeleteRequiresAckAndPlanIn(unittest.TestCase):
    def _run_delete(self, *, args: list[str], run_id: str) -> dict:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--run-id", run_id, "--apply", *args])
            self.assertEqual(rc, 0)
            return json.loads(buf.getvalue())

    def test_delete_refuses_without_yes(self) -> None:
        payload = self._run_delete(args=["sites", "delete", "--site-url", "https://example.com/"], run_id="2026-03-05T131000Z_del1")
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertIn("Refusing delete without --yes", payload["reasons"][0])

    def test_delete_refuses_without_ack_irreversible(self) -> None:
        payload = self._run_delete(
            args=["--yes", "sites", "delete", "--site-url", "https://example.com/"],
            run_id="2026-03-05T131500Z_del2",
        )
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertIn("Refusing delete without --ack-irreversible", payload["reasons"][0])

    def test_delete_refuses_without_plan_in(self) -> None:
        payload = self._run_delete(
            args=["--yes", "--ack-irreversible", "sites", "delete", "--site-url", "https://example.com/"],
            run_id="2026-03-05T132000Z_del3",
        )
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertIn("Missing --plan-in", payload["reasons"][0])

    def test_sitemaps_delete_refuses_without_yes(self) -> None:
        payload = self._run_delete(
            args=[
                "sitemaps",
                "delete",
                "--site-url",
                "https://example.com/",
                "--feedpath",
                "https://example.com/sitemap.xml",
            ],
            run_id="2026-03-05T132500Z_del4",
        )
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertIn("Refusing delete without --yes", payload["reasons"][0])

    def test_sitemaps_delete_refuses_without_ack_irreversible(self) -> None:
        payload = self._run_delete(
            args=[
                "--yes",
                "sitemaps",
                "delete",
                "--site-url",
                "https://example.com/",
                "--feedpath",
                "https://example.com/sitemap.xml",
            ],
            run_id="2026-03-05T133000Z_del5",
        )
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertIn("Refusing delete without --ack-irreversible", payload["reasons"][0])

    def test_sitemaps_delete_refuses_without_plan_in(self) -> None:
        payload = self._run_delete(
            args=[
                "--yes",
                "--ack-irreversible",
                "sitemaps",
                "delete",
                "--site-url",
                "https://example.com/",
                "--feedpath",
                "https://example.com/sitemap.xml",
            ],
            run_id="2026-03-05T133500Z_del6",
        )
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertIn("Missing --plan-in", payload["reasons"][0])
