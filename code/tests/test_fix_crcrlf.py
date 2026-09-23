"""Tests for the ``\\r\\r\\n`` (blank-line-doubling) repair utility.

The defect: writing text that already contains ``\\r\\n`` through a stream opened
in text mode on Windows translates every ``\\n`` to ``\\r\\n``, producing
``\\r\\r\\n``.  Python's universal-newline reader then reports one spurious blank
line per real line, so the file looks twice as long.  It is semantically
harmless for Python (extra blank lines), which is why it survived a fully green
test suite -- so the repair needs its own coverage.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "code" / "scripts" / "fix_crcrlf.py"

sys.path.insert(0, str(SCRIPT.parent))
from fix_crcrlf import scan_and_fix, tracked_text_files  # noqa: E402


def _git(root: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, capture_output=True, check=True)


def _repo_with(root: pathlib.Path, files: dict[str, bytes]) -> None:
    _git(root, "init", "-q")
    for rel, payload in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    _git(root, "add", "-A")


def test_dry_run_reports_without_touching_files(tmp_path: pathlib.Path) -> None:
    payload = b"line one\r\r\nline two\r\r\n"
    _repo_with(tmp_path, {"a.py": payload})

    hits = scan_and_fix(tmp_path, apply=False)
    assert hits == [("a.py", 2, 2)]
    assert (tmp_path / "a.py").read_bytes() == payload


def test_apply_collapses_markers_and_shrinks_logical_length(tmp_path: pathlib.Path) -> None:
    _repo_with(tmp_path, {"a.py": b"line one\r\r\nline two\r\r\n"})

    hits = scan_and_fix(tmp_path, apply=True)
    assert hits and hits[0][0] == "a.py"
    fixed = (tmp_path / "a.py").read_bytes()
    assert fixed == b"line one\r\nline two\r\n"
    assert fixed.count(b"\r\r\n") == 0
    # the doubling is gone: two real lines, not four
    assert fixed.decode("utf-8").splitlines() == ["line one", "line two"]


def test_clean_repository_reports_nothing(tmp_path: pathlib.Path) -> None:
    _repo_with(tmp_path, {"a.py": b"line one\r\nline two\r\n"})
    assert scan_and_fix(tmp_path, apply=False) == []


def test_only_declared_text_suffixes_are_inspected(tmp_path: pathlib.Path) -> None:
    """A binary artefact that happens to contain the byte pair must be left alone."""
    _repo_with(tmp_path, {"blob.bin": b"\r\r\n\r\r\n", "a.py": b"ok\r\n"})
    assert tracked_text_files(tmp_path) == ["a.py"]
    assert scan_and_fix(tmp_path, apply=False) == []


def test_real_repository_is_clean() -> None:
    """Regression guard: the repository must not reintroduce the defect."""
    assert scan_and_fix(REPO_ROOT, apply=False) == []
