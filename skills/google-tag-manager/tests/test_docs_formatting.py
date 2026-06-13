from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestDocsFormatting(unittest.TestCase):
    def test_no_double_bullet_lines(self) -> None:
        root = Path(__file__).resolve().parents[1]
        patterns = [
            root / "README.md",
            root / "docs",
        ]
        bad_lines: list[str] = []
        for p in patterns:
            if p.is_file():
                files = [p]
            else:
                files = list(p.rglob("*.md"))
            for f in files:
                try:
                    text = f.read_text(encoding="utf-8")
                except Exception:
                    continue
                for i, line in enumerate(text.splitlines(), start=1):
                    if re.match(r"^\s*-\s+-\s", line):
                        rel = f.relative_to(root)
                        bad_lines.append(f"{rel}:{i}: {line}")
        if bad_lines:
            joined = "\n".join(bad_lines)
            self.fail("Double-bullet lines found:\n" + joined)

    def test_no_template_placeholders_in_docs_and_examples(self) -> None:
        root = Path(__file__).resolve().parents[1]
        forbidden = re.compile(
            r"(<tool>|<package>|<command>|<resource-id-or-query>|\(template\)|copy this template)",
            flags=re.IGNORECASE,
        )
        scan_roots = [
            root / "README.md",
            root / "docs",
            root / "examples",
        ]
        rules_file = next(root.glob("AGENTS.*"), None)
        if rules_file and rules_file.is_file():
            scan_roots.append(rules_file)
        hits: list[str] = []
        for p in scan_roots:
            files: list[Path] = []
            if p.is_file():
                files = [p]
            elif p.is_dir():
                files = list(p.rglob("*.md")) + list(p.rglob("*.json"))
            for f in files:
                try:
                    text = f.read_text(encoding="utf-8")
                except Exception:
                    continue
                for i, line in enumerate(text.splitlines(), start=1):
                    if forbidden.search(line):
                        rel = f.relative_to(root)
                        hits.append(f"{rel}:{i}: {line}")
        if hits:
            self.fail("Template placeholders found (remove before shipping):\n" + "\n".join(hits))

    def test_use_cases_stays_human_and_specific(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")

        required = [
            "# What you can do with Google Tag Manager",
            "Tracking setup review",
            "Version and workspace checks",
            "Careful change planning",
            "What the agent should show you",
            "Good first tracking path",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

        rejected = [
            "Use this page when you want ideas",
            "Good first asks",
            "Good fits",
            "Not a good fit",
        ]
        for phrase in rejected:
            self.assertNotIn(phrase, text)
