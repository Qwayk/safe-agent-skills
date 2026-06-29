from __future__ import annotations

import importlib
import pkgutil
import tomllib
from pathlib import Path
import unittest


def _project_module_name(root: Path) -> str:
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return str(((data.get("project") or {}).get("name") or "")).strip()


class TestImports(unittest.TestCase):
    def test_all_package_modules_importable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        project_name = _project_module_name(root)
        module_name = project_name.replace("-", "_")

        package = importlib.import_module(module_name)
        if not hasattr(package, "__path__"):
            self.fail(f"{module_name} is not a package")

        failures: list[str] = []
        for mod in pkgutil.walk_packages(package.__path__, prefix=f"{module_name}."):
            try:
                importlib.import_module(mod.name)
            except Exception as e:
                failures.append(f"{mod.name}: {type(e).__name__}: {e}")

        if failures:
            self.fail("Import failures:\n" + "\n".join(failures))
