from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from google_ads_api_tool.presets.loader import PresetLoader


class TestPresetsValidationFailures(unittest.TestCase):
    def test_validate_catches_multiple_errors(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.json"
            p.write_text(
                json.dumps(
                    {
                        "preset_schema_version": 1,
                        "name": "bad",
                        "description": "bad preset",
                        "join_map": {"campaign.resource_name": {"description": "x", "fields": ["campaign.resource_name"]}},
                        "query_groups": [
                            {
                                "group_id": "dup",
                                "required": True,
                                "output": "oops.jsonl",
                                "join_keys": ["missing.join_key"],
                                "gaql_templates": {"base": "SELECT campaign.id FROM campaign"},
                            },
                            {
                                "group_id": "dup",
                                "required": False,
                                "output": "oops.jsonl",
                                "join_keys": ["campaign.resource_name"],
                                "gaql_templates": {"base": "SELECT campaign.id FROM campaign WHERE segments.date >= '{since}'"},
                            },
                            {
                                "group_id": "unsafe_out",
                                "required": False,
                                "output": "../unsafe.jsonl",
                                "join_keys": ["campaign.resource_name"],
                                "gaql_templates": {
                                    "base": "SELECT campaign.resource_name FROM campaign WHERE segments.date >= '{since}' AND segments.date <= '{until}'"
                                },
                            },
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            loader = PresetLoader(extra_search_paths=[Path(td)])
            # The loader name comes from filename stem.
            result = loader.validate_preset("bad")
            self.assertFalse(result.ok)
            joined = "\n".join(result.errors)
            self.assertIn("output must be a safe filename", joined)
            self.assertIn("duplicates an earlier group_id", joined)
            self.assertIn("duplicates an earlier output filename", joined)
            self.assertIn("references missing join key", joined)
            self.assertIn("missing required placeholders", joined)
