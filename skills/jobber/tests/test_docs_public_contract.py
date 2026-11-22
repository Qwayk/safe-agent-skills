from __future__ import annotations

import re
import unittest
from pathlib import Path

from jobber_safe_agent_cli.commands.common import (
    mutation_requires_ack_irreversible,
    mutation_requires_no_snapshot,
)


class TestDocsPublicContract(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.docs = self.root / "docs"

    def test_local_doc_links_resolve(self) -> None:
        docs = [self.root / "README.md", self.root / "SKILL.md", *self.docs.glob("*.md")]
        for doc in docs:
            for target in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", doc.read_text(encoding="utf-8")):
                path = target.partition("#")[0]
                if path and "://" not in path:
                    with self.subTest(doc=doc.name, target=target):
                        self.assertTrue((doc.parent / path).exists(), target)

    def test_install_checks_and_quickstart_have_no_live_apply(self) -> None:
        for name in ("quickstart.md", "proof.md"):
            with self.subTest(name=name):
                self.assertNotIn("--apply", (self.docs / name).read_text(encoding="utf-8"))

    def test_public_write_apply_examples_require_plan_in(self) -> None:
        roots = [
            self.root / "README.md",
            self.root / "docs",
            self.root / "examples",
            self.root / "SKILL.md",
        ]
        files: list[Path] = []
        for root in roots:
            if root.is_file():
                files.append(root)
            else:
                files.extend(path for path in root.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".csv"})

        bad_apply_lines: list[str] = []
        residue_lines: list[str] = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(self.root)
            for line_no, line in enumerate(text.splitlines(), start=1):
                if "--apply --yes write" in line and "--plan-in" not in line:
                    bad_apply_lines.append(f"{rel}:{line_no}: {line}")
                if "read.ping" in line or "write.ping" in line:
                    residue_lines.append(f"{rel}:{line_no}: {line}")
        if bad_apply_lines:
            self.fail("Direct write apply examples found without --plan-in:\n" + "\n".join(bad_apply_lines))
        if residue_lines:
            self.fail("Local ping job residue found in public files:\n" + "\n".join(residue_lines))

    def test_public_docs_do_not_show_high_risk_apply_without_ack_no_snapshot(self) -> None:
        roots = [
            self.root / "README.md",
            self.root / "docs",
            self.root / "examples",
            self.root / "SKILL.md",
        ]
        files: list[Path] = []
        for root in roots:
            if root.is_file():
                files.append(root)
            else:
                files.extend(path for path in root.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".csv"})

        bad_apply_lines: list[str] = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(self.root)
            for line_no, line in enumerate(text.splitlines(), start=1):
                if "--apply" not in line or "--yes" not in line:
                    continue
                if "--ack-no-snapshot" in line:
                    continue
                match = re.search(r"\bwrite\s+([A-Za-z_][A-Za-z0-9_]*)", line)
                if not match:
                    continue
                if mutation_requires_no_snapshot(match.group(1)):
                    bad_apply_lines.append(f"{rel}:{line_no}: {line}")
        if bad_apply_lines:
            self.fail("High-risk write apply examples are missing --ack-no-snapshot:\n" + "\n".join(bad_apply_lines))

    def test_public_docs_do_not_show_irreversible_apply_without_ack_irreversible(self) -> None:
        roots = [
            self.root / "README.md",
            self.root / "docs",
            self.root / "examples",
            self.root / "SKILL.md",
        ]
        files: list[Path] = []
        for root in roots:
            if root.is_file():
                files.append(root)
            else:
                files.extend(path for path in root.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".csv"})

        bad_apply_lines: list[str] = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(self.root)
            for line_no, line in enumerate(text.splitlines(), start=1):
                if "--apply" not in line or "--yes" not in line:
                    continue
                if "--ack-irreversible" in line:
                    continue
                match = re.search(r"\bwrite\s+([A-Za-z_][A-Za-z0-9_]*)", line)
                if not match:
                    continue
                if mutation_requires_ack_irreversible(match.group(1)):
                    bad_apply_lines.append(f"{rel}:{line_no}: {line}")
        if bad_apply_lines:
            self.fail("Irreversible write apply examples are missing --ack-irreversible:\n" + "\n".join(bad_apply_lines))
