from __future__ import annotations

from pathlib import Path
import unittest


class TestSkillWrapper(unittest.TestCase):
    def test_skill_wrapper_exists_and_names_safe_make_behavior(self) -> None:
        root = Path(__file__).resolve().parents[1]
        candidates = [
            root / "skills" / "make-com" / "SKILL.md",
            root / "SKILL.md",
        ]
        for path in candidates:
            if path.exists():
                text = path.read_text(encoding="utf-8")
                break
        else:
            self.fail("Make.com skill wrapper is missing")

        self.assertIn("name: make-com", text)
        self.assertIn("make-com-safe api list", text)
        self.assertIn("--plan-in --apply --yes", text)
        self.assertIn("--ack-no-snapshot", text)
        self.assertIn("Do not use this skill as a generic HTTP bridge", text)
