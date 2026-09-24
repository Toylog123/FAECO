"""Guard tests for the equivalence-sweep launcher (``run_equivalence_sweep.sh``).

The launcher encodes three failure modes that are *silent* when they go wrong:

* a per-side entry-point path (``code/scripts/...`` vs ``scripts/...``),
* a per-side ``PYTHONPATH`` that stops the codex worktree from importing the main
  repo's ``rseco``,
* a Git Bash ``pwd`` that yields ``/d/...`` and breaks the Windows interpreter.

None of those would show up as a red test anywhere else, so the script gets its
own cheap checks here.

Host caveat, deliberately handled rather than glossed over: this machine has
several ``bash`` implementations on ``PATH`` (PortableGit's MSYS bash and the
WSL launcher in ``System32``).  A Git Bash answers ``pwd -W`` with a Windows
path; a WSL bash does not, so it would report ``/mnt/d/...`` and make the script
look broken when it is not.  ``_probe_bash`` therefore picks the interpreter
that behaves like the one a human would use, and the dynamic tests skip (rather
than fail) when none is available.  Static checks always run.

Only argument-validation and dry-run paths are exercised: a valid invocation
launches real Yosys/OpenSTA runs and must never happen in unit tests.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "code" / "scripts" / "run_equivalence_sweep.sh"
# repo-relative, forward-slash: absolute ``D:/...`` paths are not accepted by the
# MSYS bash on this host (it reports "No such file or directory").
SCRIPT_ARG = "code/scripts/run_equivalence_sweep.sh"

_WINDOWS_PATH = re.compile(r"^[A-Za-z]:/")


def _probe_bash() -> str | None:
    """Return a bash whose ``pwd -W`` yields a Windows path, else ``None``."""
    seen: list[str] = []
    for cand in (shutil.which("bash"), r"C:\Windows\System32\bash.exe"):
        if cand and cand not in seen:
            seen.append(cand)
    for exe in seen:
        try:
            probe = subprocess.run([exe, "-c", "pwd -W"], cwd=str(REPO_ROOT),
                                   capture_output=True, text=True,
                                   encoding="utf-8", errors="replace",
                                   timeout=30)
        except (OSError, subprocess.SubprocessError):
            continue
        if probe.returncode == 0 and _WINDOWS_PATH.match(probe.stdout.strip()):
            return exe
    return None


BASH = _probe_bash()
needs_bash = pytest.mark.skipif(
    BASH is None,
    reason="no bash on this host answers `pwd -W` with a Windows path",
)


def _run(*args: str, **overrides: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(overrides)
    return subprocess.run(
        [BASH, SCRIPT_ARG, *args],
        cwd=str(REPO_ROOT), env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


# --------------------------------------------------------------------------- #
# static checks — host independent
# --------------------------------------------------------------------------- #


def test_root_uses_windows_path_probe() -> None:
    """`pwd` alone yields /d/...; the script must ask for the Windows form."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert "pwd -W" in text


def test_all_configs_are_recognised() -> None:
    """Each config name must map to its own output dir (no accidental aliasing)."""
    text = SCRIPT.read_text(encoding="utf-8")
    for config, out_dir in (("artifact", "configA_artifact"),
                            ("k1tns", "configA2_k1tns"),
                            ("gateA", "configB_gateA"),
                            ("ctrl", "configC_ctrl")):
        assert f"{config})" in text
        assert out_dir in text
    # only the k1tns config carries --tns-aware; the control drops --early-stop
    artifact_block = text.split("artifact)")[1].split(";;")[0]
    k1tns_block = text.split("k1tns)")[1].split(";;")[0]
    gatea_block = text.split("gateA)")[1].split(";;")[0]
    ctrl_block = text.split("ctrl)")[1].split(";;")[0]
    for name, block in (("artifact", artifact_block), ("gateA", gatea_block)):
        assert "--early-stop" in block
        assert "--tns-aware" not in block, name
    assert "--early-stop" in k1tns_block
    assert "--tns-aware" in k1tns_block
    assert "--early-stop" not in ctrl_block


def test_per_side_entry_point_and_pythonpath_are_distinct() -> None:
    """The two silent-failure guards must stay in the script."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'rel="code/scripts/run_outerloop_real_wns.py"' in text
    assert 'rel="scripts/run_outerloop_real_wns.py"' in text
    assert 'PYTHONPATH="$root/src"' in text


# --------------------------------------------------------------------------- #
# dynamic checks — need a usable bash
# --------------------------------------------------------------------------- #


@needs_bash
def test_script_is_syntactically_valid() -> None:
    result = subprocess.run([BASH, "-n", SCRIPT_ARG], cwd=str(REPO_ROOT),
                            capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    assert result.returncode == 0, result.stderr


@needs_bash
def test_unknown_config_is_rejected() -> None:
    result = _run("nonsense", "main")
    assert result.returncode == 2
    assert "unknown config" in result.stderr


@needs_bash
def test_unknown_side_is_rejected() -> None:
    result = _run("gateA", "sideways")
    assert result.returncode == 2
    assert "unknown side" in result.stderr


@needs_bash
def test_missing_config_argument_prints_usage() -> None:
    result = _run()
    assert result.returncode != 0
    assert "usage" in (result.stdout + result.stderr).lower()


@needs_bash
def test_missing_worktree_is_reported_not_launched(tmp_path: Path) -> None:
    """Point the worktree at an empty dir: must fail loudly, not run main twice."""
    result = _run(
        "gateA", "codex", "s27",
        FAECO_WORKTREE=str(tmp_path / "does_not_exist"),
        FAECO_OUT_ROOT=str(tmp_path / "out"),
    )
    assert result.returncode == 2
    assert "codex worktree not found" in result.stderr


@needs_bash
def test_dry_run_paths_are_windows_form_not_posix() -> None:
    """Guards the bug that made every run die with ``circuit not found: \\d\\...``."""
    result = _run("ctrl", "main", "s382", FAECO_DRY_RUN="1")
    assert result.returncode == 0, result.stderr
    fields = dict(
        line.split("=", 1) for line in result.stdout.splitlines() if "=" in line
    )
    for key in ("ROOT", "WORKTREE", "ISCAS"):
        value = fields[key]
        assert _WINDOWS_PATH.match(value), f"{key} is not a Windows path: {value}"
    assert fields["ISCAS"].endswith("/data/raw/benchmarks/raw/iscas89")
    assert Path(fields["ISCAS"]).is_dir(), fields["ISCAS"]
    # the emitted command must carry the same, un-mangled source dir
    assert f"--iscas89-dir {fields['ISCAS']}" in fields["COMMON"]


@needs_bash
def test_dry_run_does_not_create_output_dirs(tmp_path: Path) -> None:
    out_root = tmp_path / "out"
    result = _run("gateA", "codex", "s27",
                  FAECO_DRY_RUN="1", FAECO_OUT_ROOT=str(out_root))
    assert result.returncode == 0, result.stderr
    assert not out_root.exists()
