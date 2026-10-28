# A SEC metadata correction — selected final build

The selected Chinese source/build is the original correction v1 (12 pages, Table 8 on page 8). The selected English source/build is `en_float_refinement_v5/` (26 pages, Figure 3 and Table 8 on page 15, next experiment on page 16). Both languages contain the eight accepted A8 proof counts and same-batch prover wall times. No WNS, B3/C/D result, algorithm or scientific run was changed here.

`FINAL_QA_v2.json` binds exact source/PDF bytes, actual PDF row readback, two-pass compiler results, all-page rendered visual review and the root's 14-vector comparison against fixed f761 HEAD. The vector comparison is not a before-filesystem snapshot by this child. `SYNC_RECEIPT.json` and `POST_SYNC_VALIDATION.json` bind the synchronized three Chinese PDF locations, English canonical PDF and current English submission metadata.

The final English layout keeps the accepted short proof note and a single A/B FloatBarrier; only the unchanged Figure 3 inclusion width changes from 0.78 to 0.70 linewidth. All 29 actual embedded plot text spans have minimum size 7.34552 pt, above the 6.8 pt requirement. The other 13 table blocks, references and figure artwork are preserved.

History is retained: initial QA regex failure; canonical PDF write-lock failure; v2/v3 table placement on page 16; v4 28-page sparse layout; all source/PDF snapshots, execution scripts and bounded compile/render logs. The selected v5 resolves the observed layout regression. The earlier FINAL_QA remains an original record; v2 adds precise vector provenance.

This closes only the A proof metadata and its layout/synchronization task. Other historical scientific evidence, author declarations and full-paper finalization remain governed by the current claim map and shared project records.
