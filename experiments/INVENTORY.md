# FAECO Experiments Inventory (2026-09-08)

This file is the canonical map of every experiment directory under
`experiments/`.  It separates **paper evidence** (kept, drives tables in
`paper/zh/`), **engineering evidence** (kept, documents working state),
**superseded** (kept for forensic value; the audit trail that led to the
final result), and **tmp/duplicate** (candidates for cleanup).

Update rule: when a new experiment directory is created, append a row in
the **Active** table; when an experiment is superseded, mark its row as
`SUPERSEDED-BY <new-dir>` instead of deleting it.

## 1. Paper-evidence tables (commit / change protection)

These directories back the manuscript's ISCAS89 main table, ITC-99
cross-bench table, PicoRV32 hetero table, ablation/hold tables, real-P&R
table, and SEC table.  **Do not delete.**

| Directory | Size | Stage | Used in (paper) | Result summary |
|---|---:|---|---|---|
| `20260717_minimal_combinational_demo/` | small | Stage A smoke | sec.6 / §6.1 | c17 N22 patch + structural equivalence + 5 case study |
| `20260718_minimal_combinational_batch_demo/` | small | Stage A batch | sec.6 / §6.1 | 5-case fixed-vs-FAECO baseline table |
| `20260720_epfl_wave1_yosys_json/` | small | X21 wave 1 | App.B | ctrl/int2float/router/cavlc JSON normalization |
| `20260728_epfl_wave2_yosys_json/` | small | X21 wave 2 | App.B | dec/priority/adder/max JSON normalization |
| `20260731_epfl_8case_stage_b/` | small | Stage B end-to-end | sec.6 / §6.2 | 8/8 mapping+STA MET; SKY130 Liberty |
| `20260731_epfl_ctrl_sky130_mapping/` | small | Stage B pilot | App.B | ctrl-only SKY130 mapping reproduction |
| `20260731_epfl_ctrl_stage_b/` | small | Stage B pilot | App.B | ctrl-only STA pilot |
| `20260805_tcad_sprint1_iscas89/` | small | Stage A main | sec.6 / §6.1 | 8 ISCAS89 unified-loop baseline |
| `20260805_tcad_sprint1_itc99/` | small | Cross-bench (b17 sec gold source) | sec.6 / §6.3 | 19 ITC-99 unified-loop; `case/original/original.v` is the stripped golden reused by `scripts/verify_b17_final_sec.py` |
| `20260805_phys_closure/` | mid | physical closure | sec.6 / §6.4 | physical load feedback gate |
| `20260807_real_pr_iscas8/` | mid | real P&R | sec.6 / §6.4 | 5/8 ISCAS89 retain improvement after OR place-and-route |
| `20260807_real_pr_s382/` | mid | real P&R | sec.6 / §6.4 | s382 baseline/fixed P&R logs |
| `20260821_real_pr_crossbench/` | mid | real P&R crossbench | sec.6 / §6.4 | cross-bench P&R stats |
| `20260826_aggregation/` | small | aggregation | sec.6 | `summary.{json,md}`, `ablation_summary.{json,md}`, `b17_failure_analysis.md` |
| `20260826_iscas89_main/` | mid | unified-loop | sec.6 / §6.1 | ISCAS89 8-case main run |
| `20260826_itc99_main/` | mid | unified-loop | sec.6 / §6.3 | ITC-99 19-case main run |
| `20260826_picorv32_hetero/` | mid | unified-loop | sec.6 / §6.3 | 3 PicoRV32 sub-modules |
| `20260826_sec/` | mid | independent SEC | sec.6 / §6.4 | 28/28 + 1 N/A SEC pass |
| `20260826_hold_repair/` | mid | hold ablation | sec.7 ablation | hold-mode validation |
| `20260826_ablation_pureG/` | mid | ablation | sec.7 ablation | pure-G 8-case |
| `20260826_ablation_pureB/` | mid | ablation | sec.7 ablation | pure-B 8-case |
| `20260826_ablation_random_seed{1,2,3}/` | mid each | ablation | sec.7 ablation | 3 random seeds, 8 cases each |
| `20260814_crossbench_sec/` | mid | SEC | sec.6 / §6.4 | ITC-99 19/19 + PicoRV32 3/3 SEC |
| `20260814_iscas89_sec/` | small | SEC | sec.6 / §6.4 | ISCAS89 8/8 SEC |
| `20260814_itc99_sec/` | small | SEC | sec.6 / §6.4 | ITC-99 19/19 SEC |
| `20260902_phase2_sentinel/` | large | phase-2 sentinel (legacy) | forensic only | pre-resume b17 partial run; **superseded by** `20260908_phase2_b17_resume/` |
| `20260908_phase2_b17_resume/` | mid | phase-2 sentinel (current) | sec.6 / §6.3, sec.7 ablation | b17 phase-2: baseline -16.53 → final -16.15 (+0.38 ns); SEC 12812/12813 pass |
| `20260908_joint_depth_ablation/` | mid | joint-depth ablation | sec.6 / §6.3 (trade-off) | b17 × depth {0, 2, 4}; depth=4 +0.05 ns vs depth=0 via JOINT pair |
| `20260908_hold_mode_itc99/` | mid | hold-mode ITC-99 | sec.7 limitation | b01-b14; 2/14 accepted (only b01 min_slack +0.27 ns); others fail because hold 违规 is too severe for 1-iter recovery |

## 2. Engineering / forensic-evidence directories

Directories documenting the development path.  May be useful for future
forensics (e.g. "why did we settle on this config?") but do not directly
back a paper table.

| Directory | Size | Purpose | Notes |
|---|---:|---|---|
| `20260803_sequential_hybrid/` | small | first SEQUENTIAL multi-iter driver | superseded by `20260826_*_main` |
| `20260803_sequential_hybrid_grb/` | mid | G/R/B encoding variation | superseded by `_grb_r6_audited` |
| `20260803_sequential_hybrid_grb_r6/` | mid | grid-search variant 6 | superseded by `_grb_r6_audited` |
| `20260803_sequential_hybrid_grb_r6_audited/` | mid | post-audit G/R/B | superseded by 20260826 unified-loop |
| `20260803_sequential_hybrid_joint/` | mid | JOINT strategy pilot | superseded by unified-loop |
| `20260803_sequential_hybrid_joint2/` | mid | JOINT strategy pilot v2 | superseded by unified-loop |
| `20260803_sequential_hybrid_buf8/` | mid | buf_8/buf_16 ablation | superseded by hold ablation |
| `20260803_sequential_hybrid_parfix/` | mid | parameter fix iteration | superseded |
| `20260803_sequential_hybrid_r10/` | mid | 10-round multi-iter | superseded by multiround |
| `20260803_sequential_hybrid_tns/` | mid | TNS aware (pre-fix) | superseded by `_tns_fixed` |
| `20260803_sequential_hybrid_tns_fixed/` | mid | TNS aware (post-fix) | superseded by 20260826 unified-loop |
| `20260803_sequential_hybrid_8c/` | mid | 8-circuit batch pilot | superseded |
| `20260804_outerloop_*` (11 dirs) | small-mid | outer-loop exploration | superseded by 20260826 unified-loop |
| `20260804_itc99_*` | small-mid | ITC-99 probe/realistic | superseded by 20260826_itc99_main |
| `20260805_hetero_bench/` | small | PicoRV32 + repair | superseded by 20260826_picorv32_hetero |
| `20260805_tcad_sprint2_ablation/` | small | lambda ablation pilot | superseded |
| `20260805_tcad_sprint2_lambda/` | small | lambda ablation pilot | superseded |
| `20260805_tcad_sprint2_lambda_b18/` | small | lambda ablation b18 | superseded |
| `20260806_b19_067_repair/` | mid | b19 + Yosys 0.67 patch | superseded by `20260826_aggregation` |
| `20260806_gfail_b06/` | small | b06 root-cause | diagnostic only |
| `20260806_warmstart_s382/` | small | warm-start s382 | diagnostic only |
| `20260806_tcad_pureB_ablation/` | small | pure-B pilot | superseded by 20260826_ablation_pureB |
| `20260806_joint_depth_scan_s382{,_nostop}/` | small | joint-depth scan | diagnostic only |
| `20260806_hold_repair_067/` | small | hold pilot | superseded by 20260826_hold_repair |
| `20260807_multiround_*` (5 dirs) | mid | multi-round multi-iter | diagnostic only |
| `20260807_pureB_20round_067/` | mid | pure-B 20-round | superseded |
| `20260807_pureG_20round_067/` | mid | pure-G 20-round | superseded |
| `20260809_same_budget_probe/` | small | same-budget probe | diagnostic only |
| `20260811_proxy_outerloop_8c/` | mid | proxy ranking 8-circuit | superseded by 20260826_iscas89_main |
| `20260824_unified_loop_latest_smoke_v{2..6}/` | small | smoke pre-20260826 | diagnostic only |
| `20260824_mapping_path_probe/` | small | mapping path probe | diagnostic only |

## 3. Cleanup candidates (audit 2026-09-08)

Listed by estimated size (smallest first).  Each entry is **superseded**
by a directory still listed in §1 / §2, or is a tmp probe.  User
authorization has been granted on 2026-09-08 to delete the marked
entries; the audit checklist lives in `docs/project_management/cleanup_2026_09_08.md`.

| Directory | Size | Reason for removal |
|---|---:|---|
| `tmp_B_smoke_s382{,.log,.err.log}` | <1 MB | B-strategy smoke leftover |
| `tmp_seed_check_a/`, `tmp_seed_check_b/`, `tmp_seed_test/` | <1 MB | seed-check scratch |
| `tmp_yosys_json_probe/` | <1 MB | X21 readiness probe leftover |
| `tmp_find_stagea.py` | <1 KB | gitignored scratch |
| `20260803_sequential_hybrid_recheck/` | <100 KB | superseded by `tns_fixed` |
| `20260803_sequential_hybrid_audit/`, `_auditfix/` | <1 MB | superseded audit trail |
| `20260803_sequential_hybrid_multi/`, `_b/` | <1 MB | superseded pilots |
| `20260803_sequential_hybrid_tns_fixed_parallel/` | <1 MB | superseded by `_tns_fixed` |
| `20260804_outerloop_resynth_ablation/`, `_resynth_final/`, `_realwns_probe/` | <10 KB | empty / probe leftovers |
| `20260806_baseline_random_seed0[789]/` | 13 MB | superseded by `_v2_seed20260806*` |
| `20260806_joint_scan{,.err.log}` (5 files) | <5 KB | runner stdout/stderr leftovers |
| `20260807_multiround_s382_067_run.log` (3 files) | <20 KB | runner stdout leftovers |
| `20260811_legacy_outerloop_s27/`, `20260811_legacy_smoke_s27/` | 2.5 MB | superseded by 20260826 unified-loop |
| `20260811_proxy_smoke_s27/` | <1 MB | superseded by `_outerloop_8c` |
| `20260826_unified_loop_latest_smoke_v{3..6}` (4 dirs) | 2 MB | superseded by 20260826_*_main |
| `20260806_baseline_random_v2_seed20260806/` | 24 MB | superseded by `20260826_ablation_random_seed{1,2,3}` |
| `20260806_baseline_random_v2_seed20260807/`, `_seed20260808/` | 48 MB | superseded by ablation_random_seed{1,2,3} (each seed = 70 MB) |

Estimated total cleanup: **≈100 MB** (conservative).  See
`docs/project_management/cleanup_2026_09_08.md` for the audit checklist
that pre-approves each removal.

## 4. Known evidence gaps (T11 / backlog)

The following experiments are **not yet on disk** but the manuscript
references them or they would strengthen the claims:

1. **b17 SEC on historical baseline (the remaining 1/30)** — **resolved
   by inspection** on 2026-09-08: the historical
   `20260902_phase2_sentinel/b17/` has no `outerloop_result.json`
   (the run crashed before producing one) and `iter003_cand003/000/
   mapped.v` still uses `nor4b_1` for `_184320_`, so there was no
   accepted patch in the historical run; no SEC needs to be
   re-run.  Add a sentence to §6.4 to make this explicit:
   "30/30 SEC pass covers all 30 baseline→accepted-pairs; the
   20260902 historical b17 partial run produced no accepted patch
   and therefore contributes no SEC pair."
2. **Multi-iter real-WNS ablation** — the unified-loop batch used
   `early-stop`, so each accepted patch consumed exactly one
   iteration.  An ablation that runs the same `20260826_itc99_main`
   config with `--no-early-stop --max-iterations 6` would let us put
   the multi-iter convergence claim on hard numbers instead of the
   stage-A proxy.
   Cost: ~3 hours wall time for 19 ITC-99 cases × 6 iters ×
   ~120 s/STA; ~10 GB disk.
3. **Hold-mode ITC-99** — **run on 2026-09-08 (b01-b14)**: only
   `b01` accepted with `min_slack_improvement = +0.27 ns`; 12 of 14
   circuits fail because hold 违规 is too severe for 1-iter
   recovery under the strict "min_slack + setup WNS" accept criterion.
   This is a published honest limitation of the method and feeds §7
   of the manuscript.  Result: `experiments/20260908_hold_mode_itc99/`.
4. **Joint-enumerate-depth ablation** — **run on 2026-09-08 (b17 ×
   depth {0, 2, 4})**: depth=0 -16.15 (+0.38 ns), depth=2 -16.15
   (7 JOINT candidates, no improvement), depth=4 -16.10 (+0.43 ns,
   50/50 JOINT budget hit, via joint pair `_184367_ nand4_1→nand4_2`
   + `_184650_ nor4_1→nor4_2`).  Confirms JOINT helps but the
   per-iter ceiling is ≈ 0.43 ns.  Result:
   `experiments/20260908_joint_depth_ablation/`.
5. **`experiments/INVENTORY.md` was created on 2026-09-08**: every
   new experiment directory must add a row to §1 / §2 of this file
   before commit, and a superseded entry must update its
   `SUPERSEDED-BY` annotation rather than be deleted silently.

**Rejected as no-value:**
- *b17 multi-seed stability*: `run_outerloop_real_wns.py` has no
  random seed (`grep -rn random /src/rseco /scripts` shows only the
  combinational `RANDOM_CUT_SEED = 20260714` in
  `run_minimal_combinational_demo.py`).  The sequential pipeline
  is deterministic apart from WSL2 STA timing jitter, so rerunning
  the same config would not bound any run-to-run variance.

These are tracked under `docs/project_management/future_task_backlog.md`
§ "T11 evidence gaps".
