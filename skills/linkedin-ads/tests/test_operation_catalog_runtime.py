from __future__ import annotations

import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import requests

from linkedin_ads_api_tool.cli import build_parser, main
from linkedin_ads_api_tool.operation_catalog import OPERATIONS_BY_FAMILY


_PATH_PLACEHOLDER_RE = re.compile(r"{([^{}]+)}")


class TestOperationCatalogRuntime(unittest.TestCase):
    def _build_argv_for_spec(self, family: str, spec) -> list[str]:
        argv = [family, spec.command]
        placeholders = sorted(set(_PATH_PLACEHOLDER_RE.findall(spec.path)))
        for placeholder in placeholders:
            argv.append(f"--{placeholder.replace('_', '-')}")
            argv.append(f"urn:li:test:{placeholder}")
        return argv

    def test_each_family_has_a_parsable_command(self) -> None:
        parser = build_parser()
        for family, operations in OPERATIONS_BY_FAMILY.items():
            for spec in operations:
                with self.subTest(family=family, operation=spec.command):
                    argv = self._build_argv_for_spec(family, spec)
                    parsed = parser.parse_args(argv)
                    self.assertEqual(parsed.cmd, family)
                    self.assertEqual(parsed.operation, spec.command)

    def test_campaign_report_preserves_linkedin_query_format(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict("os.environ", {}, clear=True):
            env_file = Path(td) / ".env"
            env_file.write_text("LINKEDIN_ADS_TOKEN=fixture-token\n", encoding="utf-8")
            response = requests.Response()
            response.status_code = 200
            response._content = b'{"elements":[{"impressions":45}]}'
            argv = [
                "--env-file", str(env_file), "--output", "json", "ad-analytics", "analytics",
                "--param", "accounts=List(urn:li:sponsoredAccount:123456)",
                "--param", "dateRange=(start:(year:2026,month:11,day:1),end:(year:2026,month:11,day:7))",
                "--param", "pivot=CAMPAIGN",
                "--param", "timeGranularity=ALL",
                "--param", "fields=pivotValues,impressions,clicks,costInLocalCurrency",
            ]

            buf = io.StringIO()
            with patch.object(requests.Session, "send", return_value=response) as send, redirect_stdout(buf):
                self.assertEqual(main(argv), 0)

            send.assert_called_once()
            request = send.call_args.args[0]
            self.assertEqual(request.method, "GET")
            self.assertEqual(
                request.url,
                "https://api.linkedin.com/rest/adAnalytics?q=analytics"
                "&accounts=List(urn%3Ali%3AsponsoredAccount%3A123456)"
                "&dateRange=(start:(year:2026,month:11,day:1),end:(year:2026,month:11,day:7))"
                "&pivot=CAMPAIGN&timeGranularity=ALL"
                "&fields=pivotValues,impressions,clicks,costInLocalCurrency",
            )
            self.assertEqual(json.loads(buf.getvalue())["response"]["elements"], [{"impressions": 45}])
