from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from freepik_api_tool.commands.resource import cmd_resource_shoot_pack
from freepik_api_tool.config import Config
from freepik_api_tool.freepik_api import FreepikApi


class TestResourceShootPack(unittest.TestCase):
    def _cfg(self) -> Config:
        return Config(
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

    def test_structured_groups_default_to_same_series(self) -> None:
        args = SimpleNamespace(
            id="root",
            limit=10,
            same_series=False,
            same_collection=False,
            same_author=False,
            suggested=False,
            write_jobs=None,
            job_format="jpg",
            job_image_size=None,
        )
        out = Mock()
        ctx = {"cfg": self._cfg(), "timeout_s": 1.0, "verbose": False, "out": out}

        detail = {"data": {"related_resources": {"same_series": [{"id": "3"}, {"id": "2"}, {"id": "root"}]}}}

        with patch.object(FreepikApi, "get_resource", autospec=True, return_value=detail):
            rc = cmd_resource_shoot_pack(args, ctx)

        self.assertEqual(rc, 0)
        emitted = out.emit.call_args[0][0]
        self.assertEqual(emitted["mode"], "related_groups")
        self.assertEqual(emitted["ids"], ["2", "3"])
        self.assertEqual(emitted["selected_groups"], ["same_series"])

    def test_structured_groups_default_to_first_available_by_priority(self) -> None:
        args = SimpleNamespace(
            id="root",
            limit=10,
            same_series=False,
            same_collection=False,
            same_author=False,
            suggested=False,
            write_jobs=None,
            job_format="jpg",
            job_image_size=None,
        )
        out = Mock()
        ctx = {"cfg": self._cfg(), "timeout_s": 1.0, "verbose": False, "out": out}

        detail = {
            "data": {
                "related_resources": {"same_collection": [{"id": "3"}, {"id": "2"}, {"id": "root"}]}
            }
        }

        with patch.object(FreepikApi, "get_resource", autospec=True, return_value=detail):
            rc = cmd_resource_shoot_pack(args, ctx)

        self.assertEqual(rc, 0)
        emitted = out.emit.call_args[0][0]
        self.assertEqual(emitted["mode"], "related_groups")
        self.assertEqual(emitted["ids"], ["2", "3"])
        self.assertEqual(emitted["selected_groups"], ["same_collection"])

    def test_fallback_search_is_deterministic(self) -> None:
        args = SimpleNamespace(
            id="root",
            limit=3,
            same_series=False,
            same_collection=False,
            same_author=False,
            suggested=False,
            write_jobs=None,
            job_format="jpg",
            job_image_size=None,
        )
        out = Mock()
        ctx = {"cfg": self._cfg(), "timeout_s": 1.0, "verbose": False, "out": out}

        detail = {"data": {"id": "root", "tags": [{"name": "a"}, {"name": "b"}]}}
        search = {"data": [{"id": "2"}, {"id": "1"}, {"id": "root"}]}

        with patch.object(FreepikApi, "get_resource", autospec=True, return_value=detail), patch.object(
            FreepikApi,
            "get_resources",
            autospec=True,
            return_value=search,
        ):
            rc = cmd_resource_shoot_pack(args, ctx)

        self.assertEqual(rc, 0)
        emitted = out.emit.call_args[0][0]
        self.assertEqual(emitted["mode"], "fallback_search")
        self.assertEqual(emitted["ids"], ["1", "2"])

    def test_write_jobs_csv(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            jobs = Path(d) / "jobs.csv"
            args = SimpleNamespace(
                id="root",
                limit=10,
                same_series=True,
                same_collection=False,
                same_author=False,
                suggested=False,
                write_jobs=str(jobs),
                job_format="jpg",
                job_image_size="2000px",
            )
            out = Mock()
            ctx = {"cfg": self._cfg(), "timeout_s": 1.0, "verbose": False, "out": out}

            detail = {"data": {"related_resources": {"same_series": [{"id": "3"}, {"id": "2"}]}}}

            with patch.object(FreepikApi, "get_resource", autospec=True, return_value=detail):
                rc = cmd_resource_shoot_pack(args, ctx)

            self.assertEqual(rc, 0)
            self.assertTrue(jobs.exists())
            self.assertEqual(
                jobs.read_text(encoding="utf-8").splitlines(),
                ["resource_id,format,image_size", "2,jpg,2000px", "3,jpg,2000px"],
            )
