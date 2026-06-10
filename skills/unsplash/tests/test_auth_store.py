from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from unsplash_api_tool.auth_store import (
    auth_path_for_env_file,
    get_access_key_from_store,
    get_auth_status,
    read_auth_json,
    redact_auth_dict,
    write_auth_from_file,
)


class TestAuthStore(unittest.TestCase):
    def test_status_missing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".state" / "auth.json"
            st = get_auth_status(p)
            self.assertFalse(st.exists)

    def test_write_and_redact(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "auth_in.json"
            dest = Path(d) / ".state" / "auth.json"
            src.write_text(json.dumps({"access_key": "A", "note": "x"}), encoding="utf-8")
            st = write_auth_from_file(src_file=src, dest_file=dest)
            self.assertTrue(st.exists)
            data = read_auth_json(dest)
            assert data is not None
            safe = redact_auth_dict(data)
            self.assertEqual(safe["access_key"], "***REDACTED***")
            self.assertEqual(safe["note"], "x")
            self.assertEqual(get_access_key_from_store(dest), "A")

    def test_auth_path_for_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / "prod.env"
            p = auth_path_for_env_file(str(env))
            self.assertEqual(p, Path(d) / ".state" / "auth.json")

