from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from freepik_api_tool.commands.download import run_download
from freepik_api_tool.config import Config
from freepik_api_tool.freepik_api import FreepikApi
from freepik_api_tool.http import HttpClient


class TestDownloadImageSize(unittest.TestCase):
    def test_apply_refuses_before_download_endpoint(self) -> None:
        cfg = Config(
            base_url="https://api.freepik.com/v1",
            api_key="k",
            timeout_s=1.0,
            auth_header="x-freepik-api-key",
            auth_prefix="",
            accept_language=None,
            image_size=None,
            download_url_jsonpath=None,
            license_url_jsonpath=None,
        )

        detail = {
            "data": {
                "title": "Example",
                "type": "photo",
                "url": "https://www.freepik.com/example",
                "licenses": [{"url": "https://license.example/pdf"}],
                "is_ai_generated": False,
                "has_prompt": False,
            }
        }
        download_payload = {"data": {"url": "https://download.example/file.jpg", "filename": "file.jpg"}}

        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            out_dir = tmp / "out"
            inv_path = tmp / "inventory.csv"

            args = SimpleNamespace(
                id="123",
                format="jpg",
                out_dir=str(out_dir),
                inventory=str(inv_path),
                force=False,
                image_size="1000px",
                download_url_jsonpath=None,
                license_url_jsonpath=None,
            )
            ctx = {
                "cfg": cfg,
                "timeout_s": 1.0,
                "verbose": False,
                "apply": True,
                "audit": Mock(),
            }

            def _fake_download_to_path(self: HttpClient, url: str, path: Path, retries: int = 2) -> None:  # noqa: ARG001
                path.write_bytes(b"abc")

            with patch.object(FreepikApi, "get_resource", autospec=True, return_value=detail), patch.object(
                FreepikApi,
                "download_by_id",
                autospec=True,
                return_value=download_payload,
            ) as m_download_by_id, patch.object(
                FreepikApi,
                "download_by_id_and_format",
                autospec=True,
            ) as m_download_by_id_and_format, patch.object(
                HttpClient,
                "download_to_path",
                autospec=True,
                side_effect=_fake_download_to_path,
            ) as m_download_to_path:
                result = run_download(args, ctx)

            self.assertFalse(result["ok"])
            self.assertTrue(result["refused"])
            self.assertEqual(result["refusal_type"], "SafetyError")
            self.assertIn("before-state", result["reasons"][0])
            before_state = result["plan"]["before_state"]
            self.assertTrue(before_state["required"])
            self.assertFalse(before_state["supported"])
            self.assertEqual(before_state["status"], "no_snapshot_available")
            self.assertEqual(before_state["provider_write"]["endpoint"], "/resources/123/download")
            self.assertEqual(result["verification_plan"]["status"], "best_effort_after_apply")
            recovery = result["recovery"]
            self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
            self.assertEqual(recovery["strategy"], "no_inverse")
            self.assertFalse(recovery["rollback_ready"])
            self.assertFalse(recovery["automatic_rollback"])
            self.assertIsInstance(recovery["backups"], list)
            self.assertIsInstance(recovery["snapshots"], list)
            self.assertIsNone(recovery["rollback_plan"])
            self.assertIn("License", recovery["restore_note"])
            m_download_by_id.assert_not_called()
            m_download_by_id_and_format.assert_not_called()
            m_download_to_path.assert_not_called()
            self.assertFalse(inv_path.exists())
            self.assertFalse(out_dir.exists())

    def test_dry_run_includes_no_recovery_contract(self) -> None:
        cfg = Config(
            base_url="https://api.freepik.com/v1",
            api_key="k",
            timeout_s=1.0,
            auth_header="x-freepik-api-key",
            auth_prefix="",
            accept_language=None,
            image_size=None,
            download_url_jsonpath=None,
            license_url_jsonpath=None,
        )

        detail = {
            "data": {
                "title": "Example",
                "type": "photo",
                "url": "https://www.freepik.com/example",
                "licenses": [{"url": "https://license.example/pdf"}],
                "is_ai_generated": False,
                "has_prompt": False,
            }
        }

        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            out_dir = tmp / "out"
            inv_path = tmp / "inventory.csv"
            out_dir.mkdir(parents=True, exist_ok=True)

            args = SimpleNamespace(
                id="123",
                format="jpg",
                out_dir=str(out_dir),
                inventory=str(inv_path),
                force=False,
                image_size=None,
                post_slug="",
                ghost_id="",
                usage_role="",
                download_url_jsonpath=None,
                license_url_jsonpath=None,
            )
            ctx = {
                "cfg": cfg,
                "timeout_s": 1.0,
                "verbose": False,
                "apply": False,
                "audit": Mock(),
            }

            with patch.object(FreepikApi, "get_resource", autospec=True, return_value=detail):
                result = run_download(args, ctx)

        self.assertTrue(result["dry_run"])
        self.assertIn("plan", result)
        before_state = result["plan"]["before_state"]
        self.assertTrue(before_state["required"])
        self.assertFalse(before_state["supported"])
        self.assertEqual(before_state["status"], "no_snapshot_available")
        self.assertEqual(result["plan"]["verification_plan"]["status"], "best_effort_after_apply")
        recovery = result["recovery"]
        self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
        self.assertEqual(recovery["strategy"], "no_inverse")
        self.assertFalse(recovery["rollback_ready"])
        self.assertFalse(recovery["automatic_rollback"])
        self.assertIsInstance(recovery["backups"], list)
        self.assertIsInstance(recovery["snapshots"], list)
        self.assertIsNone(recovery["rollback_plan"])
        self.assertIn("Local cleanup is manual", recovery["restore_note"])
