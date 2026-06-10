from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from plausible_api_tool.cli import main


class TestCliStatsValidateRoundtrip(unittest.TestCase):
    def test_stats_validate_outputs_ok_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "PLAUSIBLE_BASE_URL=https://example.com",
                        "PLAUSIBLE_API_KEY=placeholder",
                        "PLAUSIBLE_SITE_ID=example.com",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            query_path = Path(d) / "query.json"
            query_path.write_text(
                json.dumps(
                    {
                        "site_id": "example.com",
                        "date_range": "7d",
                        "metrics": ["pageviews"],
                        "dimensions": ["event:page"],
                        "order_by": [["pageviews", "desc"]],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = int(main(["--output", "json", "--env-file", str(env_path), "stats", "validate", "--file", str(query_path)]))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["valid"])

