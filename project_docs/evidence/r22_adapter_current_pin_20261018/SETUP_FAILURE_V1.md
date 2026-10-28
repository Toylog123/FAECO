# Harness v1 setup failure (not a test or EDA failure)

Actual root tool invocation: `.venv/Scripts/python.exe -u -X utf8 scratch/recheck_external_adapters_20261018.py`, exit 1, 2026-10-18. The original harness is preserved as `harness_v1_before_tests.py`.

The call stopped at `before=snapshot()` before writing SOURCE_BEFORE/INVOCATION or starting pytest. `snapshot()` mixed absolute `ROOT/code` paths with relative adapter paths, causing `Path.relative_to(ROOT)` to raise `ValueError` (path is not in the subpath, or one path is relative and the other absolute). The tool returned the traceback; no standalone raw stdout/stderr file was captured for this first call. This note is a transcription of the observed failure, not a recreated raw log.

No pytest, STA, SEC, formal registration or source edit occurred. The v2 harness uses ROOT-absolute adapter paths and an exclusive new `v2/` output directory. The empty v1 output and original script remain preserved. Production source and frozen D HEAD are unchanged.
