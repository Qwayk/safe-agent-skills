from __future__ import annotations

import importlib
import pkgutil
import tomllib
import unittest
from pathlib import Path


class TestImports(unittest.TestCase):
    def test_package_modules_importable(self) -> None:
        package = importlib.import_module("asana_safe_agent_cli")
        names = [item.name for item in pkgutil.walk_packages(package.__path__, package.__name__ + ".")]
        self.assertIn("asana_safe_agent_cli.commands.asana", names)
        for name in names:
            importlib.import_module(name)

    def test_project_metadata_matches_package(self) -> None:
        root = Path(__file__).resolve().parents[1]
        data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["name"], "qwayk-asana-safe-agent-cli")
        self.assertEqual(data["project"]["scripts"]["asana-safe"], "asana_safe_agent_cli.__main__:main")


if __name__ == "__main__":
    unittest.main()
