from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from urllib.parse import quote

from gsc_api_tool.cli import main


class _FakeCredentials:
    token = "fake-token"
    valid = True
    expired = False


class _FakeHttpResponse:
    def __init__(self, status: int, payload: object) -> None:
        self.status = status
        self.json = payload


class _FakeHttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout_s: float,
        verbose: bool,
        creds: object,
    ) -> None:
        _ = base_url, timeout_s, verbose, creds

    def request_json(self, *, http_method: str, path: str, query: dict | None, body: object | None) -> _FakeHttpResponse:
        _ = query, body
        if http_method.upper() == "GET":
            if path.startswith("webmasters/v3/sites/") and "/sitemaps" in path:
                return _FakeHttpResponse(200, {"ok": True})
            if path == "webmasters/v3/sites":
                return _FakeHttpResponse(200, {"siteEntry": [{"siteUrl": "https://example.com/"}]})
            return _FakeHttpResponse(200, {})
        return _FakeHttpResponse(200, {"siteUrl": "https://example.com/"})


class TestWriteMethodsDryRunPlanShape(unittest.TestCase):
    def _run_and_parse(self, args: list[str]) -> dict:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GSC_TIMEOUT_S=30\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "gsc_api_tool.commands.discovery_methods.GscHttpClient", _FakeHttpClient
            ), patch(
                "gsc_api_tool.commands.discovery_methods.load_credentials_from_config",
                return_value=(_FakeCredentials(), None),
            ), redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--run-id", "2026-03-05T130000Z_plan1", *args])
            self.assertEqual(rc, 0)
            return json.loads(buf.getvalue())

    def _assert_before_state_snapshot(
        self,
        *,
        before_state: dict,
        method_id: str,
        resource: str,
        target: dict[str, str],
        present: bool,
    ) -> None:
        self.assertEqual(before_state["method_id"], method_id)
        self.assertIsInstance(before_state["captured_at_utc"], str)
        self.assertIsInstance(before_state.get("selector"), (str, type(None)))
        self.assertIsInstance(before_state.get("before_state"), dict)
        observed = before_state["before_state"]
        self.assertEqual(observed["resource"], resource)
        self.assertEqual(observed["target"], target)
        self.assertEqual(observed["present"], present)
        self.assertIn("snapshot", observed)
        self.assertIn("entry", observed)

    def test_sites_add_dry_run_writes_plan_and_emits_shape(self) -> None:
        payload = self._run_and_parse(["sites", "add", "--site-url", "https://example.com/"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["write_capable"])
        self.assertIn("plan", payload)
        self.assertIn("plan_path", payload)
        self.assertIn("artifacts_dir", payload)
        self.assertEqual(payload["plan"]["method_id"], "webmasters.sites.add")
        self.assertEqual(payload["plan"]["selector"], "siteUrl=https://example.com/")
        recovery = payload["plan"]["recovery"]
        self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
        self.assertEqual(recovery["strategy"], "sites.delete")
        self.assertTrue(recovery["rollback_ready"])
        self.assertEqual(recovery["rollback_plan"]["method_id"], "webmasters.sites.delete")
        self._assert_before_state_snapshot(
            before_state=payload["plan"]["before_state"],
            method_id="webmasters.sites.add",
            resource="site",
            target={"site_url": "https://example.com/"},
            present=True,
        )
        self.assertEqual(payload["plan"]["before_state"]["before_state"]["entry"], {"siteUrl": "https://example.com/"})

    def test_sitemaps_submit_dry_run_recovery_contract(self) -> None:
        payload = self._run_and_parse(
            [
                "sitemaps",
                "submit",
                "--site-url",
                "https://example.com/",
                "--feedpath",
                "https://example.com/sitemap.xml",
            ]
        )
        recovery = payload["plan"]["recovery"]
        self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
        self.assertEqual(recovery["strategy"], "sitemaps.delete")
        self.assertTrue(recovery["rollback_ready"])
        self.assertEqual(recovery["rollback_plan"]["method_id"], "webmasters.sitemaps.delete")
        self._assert_before_state_snapshot(
            before_state=payload["plan"]["before_state"],
            method_id="webmasters.sitemaps.submit",
            resource="sitemap",
            target={"site_url": "https://example.com/", "feedpath": "https://example.com/sitemap.xml"},
            present=False,
        )
        self.assertIsNone(payload["plan"]["before_state"]["before_state"]["entry"])

    def test_sites_delete_dry_run_is_explicitly_irreversible(self) -> None:
        payload = self._run_and_parse(["sites", "delete", "--site-url", "https://example.com/"])
        recovery = payload["plan"]["recovery"]
        self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
        self.assertFalse(recovery["rollback_ready"])
        self.assertIsNone(recovery["rollback_plan"])
        self._assert_before_state_snapshot(
            before_state=payload["plan"]["before_state"],
            method_id="webmasters.sites.delete",
            resource="site",
            target={"site_url": "https://example.com/"},
            present=True,
        )
        self.assertEqual(payload["plan"]["before_state"]["before_state"]["entry"], {"siteUrl": "https://example.com/"})

    def test_sitemaps_delete_dry_run_is_explicitly_irreversible(self) -> None:
        payload = self._run_and_parse(
            [
                "sitemaps",
                "delete",
                "--site-url",
                "https://example.com/",
                "--feedpath",
                "https://example.com/sitemap.xml",
            ]
        )
        recovery = payload["plan"]["recovery"]
        self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
        self.assertFalse(recovery["rollback_ready"])
        self.assertIsNone(recovery["rollback_plan"])
        self._assert_before_state_snapshot(
            before_state=payload["plan"]["before_state"],
            method_id="webmasters.sitemaps.delete",
            resource="sitemap",
            target={"site_url": "https://example.com/", "feedpath": "https://example.com/sitemap.xml"},
            present=False,
        )
        self.assertIsNone(payload["plan"]["before_state"]["before_state"]["entry"])

    def test_sites_add_apply_receipt_includes_recovery(self) -> None:
        expected_path = "webmasters/v3/sites/" + quote("https://example.com/", safe="")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GSC_TIMEOUT_S=30\n", encoding="utf-8")
            buf = io.StringIO()
            with patch("gsc_api_tool.commands.discovery_methods.GscHttpClient", _FakeHttpClient), patch(
                "gsc_api_tool.commands.discovery_methods.load_credentials_from_config",
                return_value=(_FakeCredentials(), None),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--run-id",
                        "2026-03-05T130500Z_apply1",
                        "sites",
                        "add",
                        "--site-url",
                        "https://example.com/",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertIn("receipt_path", payload)
            receipt_payload = json.loads(Path(payload["receipt_path"]).read_text(encoding="utf-8"))
            recovery = receipt_payload["recovery"]
            self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
            self.assertEqual(recovery["strategy"], "sites.delete")
            self.assertEqual(recovery["rollback_plan"]["method_id"], "webmasters.sites.delete")
            self.assertEqual(recovery["rollback_plan"]["path"], expected_path)
            self.assertIn("before_state", receipt_payload)
            self.assertIn("before_state_path", receipt_payload)
            before_state_path = Path(receipt_payload["before_state_path"])
            self.assertTrue(before_state_path.exists())
            self._assert_before_state_snapshot(
                before_state=receipt_payload["before_state"],
                method_id="webmasters.sites.add",
                resource="site",
                target={"site_url": "https://example.com/"},
                present=True,
            )
            self.assertEqual(receipt_payload["before_state"], json.loads(before_state_path.read_text(encoding="utf-8")))

    def test_sitemaps_submit_apply_receipt_includes_recovery(self) -> None:
        expected_path = "webmasters/v3/sites/" + quote("https://example.com/", safe="") + "/sitemaps/" + quote(
            "https://example.com/sitemap.xml",
            safe="",
        )
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GSC_TIMEOUT_S=30\n", encoding="utf-8")
            buf = io.StringIO()
            with patch("gsc_api_tool.commands.discovery_methods.GscHttpClient", _FakeHttpClient), patch(
                "gsc_api_tool.commands.discovery_methods.load_credentials_from_config",
                return_value=(_FakeCredentials(), None),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--run-id",
                        "2026-03-05T131000Z_apply2",
                        "sitemaps",
                        "submit",
                        "--site-url",
                        "https://example.com/",
                        "--feedpath",
                        "https://example.com/sitemap.xml",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertIn("receipt_path", payload)
            receipt_payload = json.loads(Path(payload["receipt_path"]).read_text(encoding="utf-8"))
            recovery = receipt_payload["recovery"]
            self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
            self.assertEqual(recovery["strategy"], "sitemaps.delete")
            self.assertEqual(recovery["rollback_plan"]["method_id"], "webmasters.sitemaps.delete")
            self.assertEqual(recovery["rollback_plan"]["path"], expected_path)
            self.assertIn("before_state", receipt_payload)
            self.assertIn("before_state_path", receipt_payload)
            before_state_path = Path(receipt_payload["before_state_path"])
            self.assertTrue(before_state_path.exists())
            self._assert_before_state_snapshot(
                before_state=receipt_payload["before_state"],
                method_id="webmasters.sitemaps.submit",
                resource="sitemap",
                target={"site_url": "https://example.com/", "feedpath": "https://example.com/sitemap.xml"},
                present=False,
            )
            self.assertEqual(receipt_payload["before_state"], json.loads(before_state_path.read_text(encoding="utf-8")))

    def test_sites_delete_apply_receipt_includes_before_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GSC_TIMEOUT_S=30\n", encoding="utf-8")
            plan_path = root / "plan.json"
            buf_plan = io.StringIO()
            with patch("gsc_api_tool.commands.discovery_methods.GscHttpClient", _FakeHttpClient), patch(
                "gsc_api_tool.commands.discovery_methods.load_credentials_from_config",
                return_value=(_FakeCredentials(), None),
            ), redirect_stdout(buf_plan):
                rc_plan = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "--run-id",
                        "2026-03-05T133000Z_plan_delete",
                        "sites",
                        "delete",
                        "--site-url",
                        "https://example.com/",
                    ]
                )
            self.assertEqual(rc_plan, 0)

            buf_apply = io.StringIO()
            with patch("gsc_api_tool.commands.discovery_methods.GscHttpClient", _FakeHttpClient), patch(
                "gsc_api_tool.commands.discovery_methods.load_credentials_from_config",
                return_value=(_FakeCredentials(), None),
            ), redirect_stdout(buf_apply):
                rc_apply = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                        "--run-id",
                        "2026-03-05T133500Z_apply_delete",
                        "sites",
                        "delete",
                        "--site-url",
                        "https://example.com/",
                    ]
                )
            self.assertEqual(rc_apply, 0)
            payload = json.loads(buf_apply.getvalue())
            self.assertTrue(payload["ok"])
            self.assertIn("receipt_path", payload)
            receipt_payload = json.loads(Path(payload["receipt_path"]).read_text(encoding="utf-8"))
            recovery = receipt_payload["recovery"]
            self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
            self.assertFalse(recovery["rollback_ready"])
            self.assertIsNone(recovery["rollback_plan"])
            self.assertIn("before_state", receipt_payload)
            self.assertIn("before_state_path", receipt_payload)
            before_state_path = Path(receipt_payload["before_state_path"])
            self.assertTrue(before_state_path.exists())
            self._assert_before_state_snapshot(
                before_state=receipt_payload["before_state"],
                method_id="webmasters.sites.delete",
                resource="site",
                target={"site_url": "https://example.com/"},
                present=True,
            )
            self.assertEqual(receipt_payload["before_state"], json.loads(before_state_path.read_text(encoding="utf-8")))

    def test_sitemaps_delete_apply_receipt_includes_before_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GSC_TIMEOUT_S=30\n", encoding="utf-8")
            plan_path = root / "plan.json"
            buf_plan = io.StringIO()
            with patch("gsc_api_tool.commands.discovery_methods.GscHttpClient", _FakeHttpClient), patch(
                "gsc_api_tool.commands.discovery_methods.load_credentials_from_config",
                return_value=(_FakeCredentials(), None),
            ), redirect_stdout(buf_plan):
                rc_plan = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "--run-id",
                        "2026-03-05T134000Z_plan_delete_sitemap",
                        "sitemaps",
                        "delete",
                        "--site-url",
                        "https://example.com/",
                        "--feedpath",
                        "https://example.com/sitemap.xml",
                    ]
                )
            self.assertEqual(rc_plan, 0)

            buf_apply = io.StringIO()
            with patch("gsc_api_tool.commands.discovery_methods.GscHttpClient", _FakeHttpClient), patch(
                "gsc_api_tool.commands.discovery_methods.load_credentials_from_config",
                return_value=(_FakeCredentials(), None),
            ), redirect_stdout(buf_apply):
                rc_apply = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                        "--run-id",
                        "2026-03-05T134500Z_apply_delete_sitemap",
                        "sitemaps",
                        "delete",
                        "--site-url",
                        "https://example.com/",
                        "--feedpath",
                        "https://example.com/sitemap.xml",
                    ]
                )
            self.assertEqual(rc_apply, 0)
            payload = json.loads(buf_apply.getvalue())
            self.assertTrue(payload["ok"])
            self.assertIn("receipt_path", payload)
            receipt_payload = json.loads(Path(payload["receipt_path"]).read_text(encoding="utf-8"))
            recovery = receipt_payload["recovery"]
            self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
            self.assertFalse(recovery["rollback_ready"])
            self.assertIsNone(recovery["rollback_plan"])
            self.assertIn("before_state", receipt_payload)
            self.assertIn("before_state_path", receipt_payload)
            before_state_path = Path(receipt_payload["before_state_path"])
            self.assertTrue(before_state_path.exists())
            self._assert_before_state_snapshot(
                before_state=receipt_payload["before_state"],
                method_id="webmasters.sitemaps.delete",
                resource="sitemap",
                target={"site_url": "https://example.com/", "feedpath": "https://example.com/sitemap.xml"},
                present=False,
            )
            self.assertEqual(receipt_payload["before_state"], json.loads(before_state_path.read_text(encoding="utf-8")))
