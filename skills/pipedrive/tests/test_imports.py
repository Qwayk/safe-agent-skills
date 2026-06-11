from __future__ import annotations

import importlib
import pkgutil
import unittest


class TestImports(unittest.TestCase):
    def test_package_modules_importable(self) -> None:
        module_name = "qwayk_pipedrive_safe_agent_cli"
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
