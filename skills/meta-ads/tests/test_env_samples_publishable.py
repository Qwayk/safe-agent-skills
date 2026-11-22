from __future__ import annotations

import unittest
from pathlib import Path


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip("'").strip('"')
        if k:
            out[k] = v
    return out


class TestEnvSamplesPublishable(unittest.TestCase):
    def test_dotenv_example_has_empty_secret_values(self) -> None:
        tool_root = Path(__file__).resolve().parents[1]
        env_example = tool_root / ".env.example"
        self.assertTrue(env_example.is_file())
        env = _parse_env_file(env_example)

        access_token = env["META_ADS_ACCESS_TOKEN"].strip()
        ad_account_id = env["META_ADS_AD_ACCOUNT_ID"].strip()

        self.assertTrue(access_token == "", "META_ADS_ACCESS_TOKEN must be empty in .env.example")
        self.assertTrue(ad_account_id == "", "META_ADS_AD_ACCOUNT_ID must be empty in .env.example")
