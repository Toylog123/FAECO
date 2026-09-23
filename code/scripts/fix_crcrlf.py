"""Collapse the `\\r\\r\\n` (blank-line-doubling) defect across tracked text files.

Root cause: writing text that already contains `\\r\\n` through a stream opened in
text mode with `newline=None` on Windows translates every `\\n` to `\\r\\n`,
yielding `\\r\\r\\n`.  Python's universal-newline reader then reports a spurious
extra blank line between every real line, so the file appears twice as long.

Usage:
    python fix_crcrlf.py           # dry run: report only
    python fix_crcrlf.py --apply   # rewrite the affected files in place
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

TEXT_SUFFIXES = {
    ".py", ".md", ".json", ".txt", ".tcl", ".ys", ".bat", ".sh",
    ".yaml", ".yml", ".cfg", ".toml", ".csv", ".v", ".sv", ".tex", ".bib",
}


def tracked_text_files(root: pathlib.Path) -> list[str]:
    """Relative paths of git-tracked files that the checker should inspect."""
    listed = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.split()
    return [
        rel for rel in listed
        if (root / rel).is_file()
        and pathlib.Path(rel).suffix.lower() in TEXT_SUFFIXES
    ]


def scan_and_fix(root: pathlib.Path, apply: bool = False) -> list[tuple[str, int, int]]:
    """Collapse ``\\r\\r\\n`` in every tracked text file of *root*.

    Returns ``(relative_path, markers_removed, newline_count)`` per repaired file.
    """
    hits: list[tuple[str, int, int]] = []
    for rel in tracked_text_files(root):
        path = root / rel
        raw = path.read_bytes()
        n = raw.count(b"\r\r\n")
        if not n:
            continue
        fixed = raw.replace(b"\r\r\n", b"\r\n")
        hits.append((rel, n, fixed.count(b"\n")))
        if apply:
            path.write_bytes(fixed)
    return hits


def main() -> int:
    apply = "--apply" in sys.argv
    root = pathlib.Path(__file__).resolve().parents[2]
    hits = scan_and_fix(root, apply=apply)
    mode = "APPLIED" if apply else "DRY-RUN"
    print(f"[{mode}] files with \\r\\r\\n: {len(hits)}")
    for rel, n, after in hits:
        print(f"  {rel:60} markers={n:5}  lines_after={after}")
    if not apply and hits:
        print("\nre-run with --apply to rewrite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
