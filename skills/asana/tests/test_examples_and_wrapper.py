from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path


def _wrapper_path(root: Path) -> Path:
    for candidate in (root / "skills" / "asana" / "SKILL.md", root / "SKILL.md"):
        if candidate.is_file():
            return candidate
    raise AssertionError("Expected skills/asana/SKILL.md or top-level SKILL.md")


def _validate_wrapper(root: Path) -> None:
    wrapper = _wrapper_path(root).read_text(encoding="utf-8")
    required = (
        "name: asana",
        "description:",
        "asana-safe",
        "auth check",
        "commands show COMMAND",
        "saved before-state",
        "--plan-in PLAN_PATH --apply --approve PLAN_ID",
        "--acknowledge-no-snapshot",
        "--acknowledge-risk",
        "asynchronous",
        "receipt",
        "App Components",
        "SCIM",
        "OAuth app registration or token lifecycle",
        "arbitrary HTTP requests",
        "POST /batch",
    )
    for value in required:
        if value not in wrapper:
            raise AssertionError(f"Wrapper is missing required runtime or boundary guidance: {value}")
    for relative in (
        "docs/command_reference.md",
        "docs/api_coverage.md",
        "docs/safety_model.md",
        "docs/proof.md",
    ):
        if relative not in wrapper or not (root / relative).is_file():
            raise AssertionError(f"Wrapper documentation target is missing: {relative}")


class TestExamplesAndWrapper(unittest.TestCase):
    def test_json_examples_parse_and_contain_no_secret_values(self) -> None:
        root = Path(__file__).resolve().parents[1]
        paths = [*root.glob("examples/*.json"), *root.glob("docs/examples/**/*.json")]
        self.assertGreaterEqual(len(paths), 4)
        for path in paths:
            value = json.loads(path.read_text(encoding="utf-8"))
            rendered = json.dumps(value).lower()
            self.assertNotRegex(rendered, r"bearer [a-z0-9_-]{16,}")
            self.assertNotIn("personal_access_token", rendered)

    def test_wrapper_names_runtime_and_boundary(self) -> None:
        root = Path(__file__).resolve().parents[1]
        _validate_wrapper(root)

    def test_public_top_level_wrapper_layout_has_the_same_complete_contract(self) -> None:
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as td:
            public = Path(td)
            shutil.copy2(_wrapper_path(source), public / "SKILL.md")
            shutil.copytree(source / "docs", public / "docs")
            _validate_wrapper(public)

    def test_wrapper_validation_fails_when_neither_supported_layout_exists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(AssertionError, "top-level SKILL.md"):
                _validate_wrapper(Path(td))


if __name__ == "__main__":
    unittest.main()
