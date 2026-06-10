from __future__ import annotations

import importlib
import pkgutil
import unittest
from pathlib import Path

import tomllib


def _load_package_name(root: Path) -> str:
    pyproject = root / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    scripts = ((data.get("project") or {}).get("scripts") or {})
    if isinstance(scripts, dict) and scripts:
        target = str(next(iter(scripts.values())) or "").strip()
        if ":" in target:
            module_name = target.split(":", 1)[0].strip()
            if module_name.endswith(".__main__"):
                module_name = module_name[: -len(".__main__")]
            if module_name:
                return module_name
    return str(((data.get("project") or {}).get("name") or "")).strip().replace("-", "_")


class TestImports(unittest.TestCase):
    def test_package_modules_importable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        module_name = _load_package_name(root)
        self.assertTrue(module_name, "Missing package import target in pyproject.toml")
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
