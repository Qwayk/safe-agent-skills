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

    def test_public_docs_do_not_leak_private_workspace_paths(self) -> None:
        root = Path(__file__).resolve().parents[1]
        files = [
            root / "docs" / "proof.md",
            root / "docs" / "examples" / "outputs" / "version.json",
            root / "docs" / "examples" / "outputs" / "auth_check.json",
            root / "docs" / "examples" / "outputs" / "commerce_campaigns_invalid_secret.json",
        ]
        forbidden = [
            "/home/" + "ubuntu/",
            "api" + "-tools-for-ai-agents",
            "pro" + "jects/" + "qwayk-skills-control-room/",
            "api" + "-tools/" + "qwayk-sovrn-safe-agent-cli/",
        ]
        for path in files:
            text = path.read_text(encoding="utf-8")
            for needle in forbidden:
                with self.subTest(path=path.name, needle=needle):
                    self.assertNotIn(needle, text)
