# Current implementation independent acceptance

Client date: 2026-10-18. Exact verification time, inputs and SHA values are recorded in `STAGE_CURRENT_IMPLEMENTATION_ACCEPTANCE.json`.

The reviewed current implementation and v5 full regression are accepted within the implementation scope below. All 174 current Python source files match v5 SOURCE_BEFORE, SOURCE_AFTER and every source ZIP member byte for byte. The run receipt binds the raw pytest log to exit code 0 and explicit PYTHONUTF8=1. The actual log reports **1056 passed, 156 subtests passed in 208.27s**, with no skips or warnings. Its SHA-256 is `3f5f39fa113c8e0f0b7a15d0e63de9f0427532450f4f8cd0b0ac75b65f74bb26`.

`REVIEW_V1_V5.json` preserves the distinct v1–v5 source snapshots, ZIP members, run/log bindings and native source-top counterexample evidence. The earlier v1, v3 and v4 failures remain failures in the history; v5 does not rewrite them. Earlier independent code review covers S evidence/model binding, shared normalization and top/status selection; the OpenSTA review covers the explicitly bounded tiny tool-binding examples.

Fixture cleanup metadata was also independently checked without Git operations: the 85-member original ZIP matches its pre-cleanup manifest, all 5 restored tracked files match saved HEAD copies and recorded blob identities, and all 72 files in 6 moved items match the source and destination manifests. This review did not independently query Git status or index.

| Pending gate | Current disposition |
| --- | --- |
| OI048 historical top/proof impact, including P08 | Open; per-object historical evidence still needs restoration and assessment. |
| OI046 b18 inout domain | Open; no inout implementation or scientific acceptance is supplied here. |
| OI049 timeout bytes handling | Open static finding, reserved for the next implementation gate. |
| Four-state support and B3/C/D/S/SPEF scientific evidence | Open; tiny binding and regression acceptance do not establish these results. |
| RC calibration and paper/figure evidence replacement | Open. |
| Formal EDA restart | Requires the main line's clean commit, source pin and experiment registration. |

The reviewer ran no new tests, EDA or Git operations in this final check and changed no production sources. This directory is frozen after the final closure receipt is written; subsequent work must use a new receipt or directory.
