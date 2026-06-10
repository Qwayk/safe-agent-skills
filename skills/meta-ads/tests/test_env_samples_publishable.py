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
    def test_examples_example_env_exists(self) -> None:
        tool_root = Path(__file__).resolve().parents[1]
        example_env = tool_root / "examples" / "example.env"
        self.assertTrue(example_env.exists(), "examples/example.env must exist")

    def test_dotenv_example_has_empty_secret_values(self) -> None:
        tool_root = Path(__file__).resolve().parents[1]
        env_example = tool_root / ".env.example"
        env = _parse_env_file(env_example)

        access_token = (env.get("META_ADS_ACCESS_TOKEN") or "").strip()
        ad_account_id = (env.get("META_ADS_AD_ACCOUNT_ID") or "").strip()

        self.assertTrue(access_token == "", "META_ADS_ACCESS_TOKEN must be empty in .env.example")
        self.assertTrue(ad_account_id == "", "META_ADS_AD_ACCOUNT_ID must be empty in .env.example")

    def test_examples_example_env_uses_obvious_placeholders(self) -> None:
        tool_root = Path(__file__).resolve().parents[1]
        example_env = tool_root / "examples" / "example.env"
        env = _parse_env_file(example_env)

        access_token = (env.get("META_ADS_ACCESS_TOKEN") or "").strip()
        ad_account_id = (env.get("META_ADS_AD_ACCOUNT_ID") or "").strip()

        self.assertTrue(access_token.startswith("YOUR_"), "META_ADS_ACCESS_TOKEN must start with YOUR_ in examples/example.env")
        self.assertTrue(ad_account_id.startswith("act_YOUR_"), "META_ADS_AD_ACCOUNT_ID must start with act_YOUR_ in examples/example.env")
