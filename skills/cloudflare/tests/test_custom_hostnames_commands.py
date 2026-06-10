from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cloudflare_api_tool.cli import main


def _write_env(root: Path, *, token: str = "T") -> Path:
    p = root / ".env"
    p.write_text(
        "\n".join(
            [
                "CLOUDFLARE_API_BASE_URL=http://example.invalid/client/v4",
                f"CLOUDFLARE_API_TOKEN={token}",
                "CLOUDFLARE_TIMEOUT_S=30",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return p


class TestCustomHostnamesCommands(unittest.TestCase):
    def test_custom_hostnames_list_is_dry_run_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "custom-hostnames", "list", "--zone-id", "z1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

    def test_custom_hostnames_apply_missing_out_refuses_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--project-dir", str(root), "--apply", "custom-hostnames", "list", "--zone-id", "z1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

