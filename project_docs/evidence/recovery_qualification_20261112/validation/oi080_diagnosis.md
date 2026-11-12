# OI080 diagnosis 2026-11-12

The five failures in takeover_20261112_pytest.log are environment failures, not application-code regressions.

## Historical comparison
Reused docs/EXPERIENCE.md r116 and docs/environment.md section 5.2. Historical failure was 0xC0000139 (entrypoint missing) resolved by bin+lib PATH order. Current failure is 0xC0000135 (DLL missing), and correct PATH ordering is insufficient.

## Evidence
- oi080_environment.json: yosys executable correctly resolves to C:/oss-cad-suite-build/oss-cad-suite/bin/yosys.EXE; bin+lib lead PATH; returncode 3221225781, stdout/stderr empty.
- oi080_loader_probe.py: same failure with cwd bin/lib/project and minimal PATH. Both PowerShell and Git Bash reproduce.
- oi080_dll_probe.py: recursively resolves static imports; ctypes explicit DLL loading succeeds.
- oi080_exeonly_probe.py: byte-identical executable copied without DLLs still fails.
- oi080_isolate_probe.py: same executable with eight dependent DLLs colocated runs Yosys 0.67+146 (468ba27d9-dirty).
- oi080_package_identity.log: native Python inherits package identity OpenAI.Codex_26.1106.6628.0_x64__2p2nqsd0c76g0.
- Microsoft primary documentation https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order : packaged-app standard search includes executable directory and System32 but excludes PATH/current directory. This explains the observed intervention result; no evidence of corrupted Yosys binary.

## Bounded workaround and verification
scratch/oi080_suite/bin contains byte-identical copies of Yosys, ABC, and their eight required DLLs, with source/destination SHA256 values in oi080_suite/receipt.json. share/yosys is copied from the same installed distribution. Original installation is untouched.

Command (Git Bash):
export PATH="$PWD/scratch/oi080_suite/bin:/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:$PATH"
bash code/scripts/run_with_timeout.sh 180 .venv/Scripts/python.exe -m pytest code/tests/test_convert_itc99_blif_to_v.py code/tests/test_demo_runner.py code/tests/test_yosys_abc_flow.py -q --tb=short

Result: 24 passed in 29.73s; wrapper 31s, rc0, oi080_targeted.log. Includes all five previously failing tests. No source edits, no tracked case changes, no scientific experiment/rerun. Full integrated regression remains root-owned. This scratch mirror is a verified local workaround, not a durable environment bootstrap change.

## Test artifact side effects and concurrency correction
The targeted demo tests modified six tracked minimal case result files and generated untracked normalization outputs despite output-directory fixtures. The pre-test git status had no case changes. A full case results backup was copied to scratch/oi080_generated_case_backup/results; tracked changes were restored with git restore; untracked files were moved under oi080_generated_case_backup/untracked, with resolved-path containment checked. The root's request to stop cleanup arrived just after cleanup completed: its integrated regression had already started. Root was warned immediately; concurrent test results need inspection and potentially a clean rerun. No further cleanup mutations are owned by this agent.
