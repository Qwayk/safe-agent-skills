from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from freepik_api_tool.commands.search import cmd_search_photos
from freepik_api_tool.config import Config
from freepik_api_tool.freepik_api import FreepikApi


class TestSearchPhotosDefaults(unittest.TestCase):
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

    def test_default_photo_filter_is_applied(self) -> None:
        args = SimpleNamespace(
            query="x",
            page=1,
            limit=2,
            param=[],
            shortlist=False,
            write_jobs=None,
            job_format="jpg",
            job_image_size=None,
            exclude_ai=False,
        )
        out = Mock()
        ctx = {"cfg": self._cfg(), "timeout_s": 1.0, "verbose": False, "out": out}

        with patch.object(FreepikApi, "get_resources", autospec=True, return_value={"data": []}) as m:
            rc = cmd_search_photos(args, ctx)

        self.assertEqual(rc, 0)
        self.assertEqual(m.call_args.kwargs["extra_params"].get("filters[content_type][]"), "photo")

    def test_param_overrides_default_deterministically(self) -> None:
        args = SimpleNamespace(
            query="x",
            page=1,
            limit=2,
            param=["filters[content_type][]=vector"],
            shortlist=False,
            write_jobs=None,
            job_format="jpg",
            job_image_size=None,
            exclude_ai=False,
        )
        out = Mock()
        ctx = {"cfg": self._cfg(), "timeout_s": 1.0, "verbose": False, "out": out}

        with patch.object(FreepikApi, "get_resources", autospec=True, return_value={"data": []}) as m:
            rc = cmd_search_photos(args, ctx)

        self.assertEqual(rc, 0)
        self.assertEqual(m.call_args.kwargs["extra_params"].get("filters[content_type][]"), "vector")
