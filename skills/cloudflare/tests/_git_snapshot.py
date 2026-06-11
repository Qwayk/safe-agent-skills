from __future__ import annotations

import csv
import io
import subprocess
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(15):
        if (cur / "api-tools").exists() and (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise RuntimeError("Could not locate repo root (expected api-tools/ and .git)")


def git_show_bytes(*, repo_root: Path, rev: str, relpath: str) -> bytes:
    res = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{rev}:{relpath}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if res.returncode != 0:
        err = res.stderr.decode("utf-8", errors="replace").strip()
        err_line = err.splitlines()[0] if err else "unknown error"
        raise RuntimeError(f"git show failed for {rev}:{relpath} ({err_line})")
    return res.stdout


def read_csv_rows_via_git_show(*, repo_root: Path, relpath: str, rev: str = "HEAD") -> list[dict[str, str]]:
    raw = git_show_bytes(repo_root=repo_root, rev=rev, relpath=relpath)
    text = raw.decode("utf-8", errors="strict")
    return list(csv.DictReader(io.StringIO(text)))

