from __future__ import annotations

import importlib
import pkgutil
import unittest
from pathlib import Path



def _load_package_name(root: Path) -> str:
    src_root = root / "src"
    packages = sorted(
        p.name for p in src_root.iterdir() if p.is_dir() and (p / "__init__.py").exists()
    )
    if len(packages) != 1:
        raise AssertionError(f"Expected exactly one top-level package under src/, found: {packages}")
    return packages[0]


class TestImports(unittest.TestCase):
    def test_package_modules_importable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        module_name = _load_package_name(root)
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
