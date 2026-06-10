from __future__ import annotations

import argparse
import unittest
from unittest import mock

from google_ads_api_tool.commands.helpers import cmd_helpers_entities_lookup_by_name


class _Out:
    def __init__(self) -> None:
        self.last = None

    def emit(self, obj):  # noqa: ANN001
        self.last = obj


class TestHelperLookupByName(unittest.TestCase):
    @mock.patch("google_ads_api_tool.commands.helpers._gaql_rows")
    def test_lookup_by_name_emits_rows(self, mock_rows: mock.Mock) -> None:
        mock_rows.return_value = [
            {
                "campaign": {
                    "resource_name": "customers/123/campaigns/99",
                    "id": "99",
                    "name": "Main Search",
                    "status": "ENABLED",
                }
            }
        ]
        out = _Out()
        rc = cmd_helpers_entities_lookup_by_name(
            argparse.Namespace(
                customer_id="123",
                resource_type="campaign",
                name="Main Search",
                match="exact",
                limit=20,
            ),
            {"cfg": object(), "out": out},
        )
        self.assertEqual(rc, 0)
        self.assertTrue(out.last["ok"])
        self.assertEqual(out.last["meta"]["row_count"], 1)
        self.assertEqual(out.last["rows"][0]["campaign"]["resource_name"], "customers/123/campaigns/99")


if __name__ == "__main__":
    unittest.main()
