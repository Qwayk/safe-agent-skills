from __future__ import annotations

import importlib
import pkgutil
import unittest
from pathlib import Path


class TestImports(unittest.TestCase):
    def test_package_modules_importable(self) -> None:
        module_name = "jobber_safe_agent_cli"
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

    def test_template_demo_command_module_removed(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertFalse((root / "src" / "jobber_safe_agent_cli" / "commands" / "demo.py").exists())
