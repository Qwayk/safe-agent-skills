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

    def test_use_cases_stays_human_and_specific(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")

        required = [
            "# What you can do with PayPal",
            "Orders, payments, refunds, and tracking",
            "Invoices, products, plans, and subscriptions",
            "Webhooks, disputes, payouts, and partner areas",
            "Preview-first changes",
            "What the agent should show you",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

        rejected = [
            "Use this page when you want ideas",
            "What this tool is good for",
            "Common requests you can give an agent",
            "What safe behavior looks like",
        ]
        for phrase in rejected:
            self.assertNotIn(phrase, text)
