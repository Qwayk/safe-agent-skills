from __future__ import annotations

import importlib
import pkgutil
import unittest
from pathlib import Path

import tomllib


def _load_project_name(root: Path) -> str:
    pyproject = root / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return str(((data.get("project") or {}).get("name") or "")).strip()


class TestImports(unittest.TestCase):
    def test_package_modules_importable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        project_name = _load_project_name(root)
        self.assertTrue(project_name, "Missing [project].name in pyproject.toml")
        module_name = project_name.replace("-", "_")
        pkg = importlib.import_module(module_name)
        if not hasattr(pkg, "__path__"):
            self.fail(f"{module_name} is not a package")

        errors: list[str] = []
        for mod in pkgutil.walk_packages(pkg.__path__, prefix=f"{module_name}."):
            try:
                importlib.import_module(mod.name)
            except Exception as e:  # noqa: BLE001
                errors.append(f"{mod.name}: {type(e).__name__}: {e}")

        if errors:
            self.fail("Import failures:\n" + "\n".join(errors))
