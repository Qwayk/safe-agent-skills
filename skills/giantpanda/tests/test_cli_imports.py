from __future__ import annotations

import importlib
import pkgutil
import unittest
from pathlib import Path


def _load_project_name(root: Path) -> str:
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("[") or "=" not in s:
            continue
        key, value = [part.strip() for part in s.split("=", 1)]
        if key == "name":
            return value.strip().strip('"')
    return ""


class TestImports(unittest.TestCase):
    def test_package_modules_importable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        project_name = _load_project_name(root)
        self.assertTrue(project_name, "Missing project name in pyproject.toml")
        package_name = "giantpanda_api_tool"
        package = importlib.import_module(package_name)
        if not hasattr(package, "__path__"):
            self.fail(f"{package_name} is not a package")

        failures: list[str] = []
        for mod in pkgutil.walk_packages(package.__path__, prefix=f"{package_name}."):
            try:
                importlib.import_module(mod.name)
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{mod.name}: {type(exc).__name__}: {exc}")
        if failures:
            self.fail("Import failures:\n" + "\n".join(failures))
