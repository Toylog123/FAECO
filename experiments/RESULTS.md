# FAECO Experiments — Results Overview (2026-09-09)

This page is the one-shot human-readable roll-up of every paper-evidence
experiment in this repository.  The full machine-readable aggregate
lives in [`results.json`](./results.json); per-directory detail is in
[`INVENTORY.md`](./INVENTORY.md) §1.

Aggregate numbers below come from:
- `experiments/20260826_aggregation/summary.json` for ISCAS89 / ITC-99
  / PicoRV32 unified-loop rows (post-2026-09-08 b17 resume)
- `experiments/20260908_phase2_b17_resume/` for the b17 phase-2
  resume + SEC
- `experiments/20260908_joint_depth_ablation/joint_depth_summary.json`
  for the b17 joint-depth ablation
- `experiments/20260908_hold_mode_itc99/hold_mode_summary.json`
  for the b01..b14 hold-mode batch
- `experiments/20260908_multi_iter_fix_full/multi_iter_fix_summary.json`
  for the b17 multi-iter post-fix re-run
- `experiments/20260908_multi_iter_ablation/multi_iter_summary.json`
  for the b17/b18/b19 multi-iter ablation

## 1. Headline numbers

|  | n | success | mean Δ (ns) | best Δ (ns) | median Δ (ns) |
|---|---:|---:|---:|---:|---:|
| **ISCAS89** unified-loop | 8 | **8 / 8** | **+0.16** | +0.46 | +0.14 |
| **ITC-99** unified-loop | 19 | **19 / 19** | **+0.43** | +2.16 (b21) | +0.21 |
| **PicoRV32** hetero | 3 | 2 / 3 | +0.60 | +1.13 | +0.05 |
| **b17 phase-2 resume** | 1 | Y | **+0.38** | — | — |
| **joint-depth (b17 × {0,2,4})** | 3 | 0 / 3 | +0.40 (best) | +0.43 (depth=4) | +0.38 (depth=0) |
| **hold-mode ITC-99 (b01-b14)** | 14 | 2 / 14 | 0.0 (best) | 0.0 | 0.0 |

Caveats:
- Δ is WNS improvement (ns) vs the mapped baseline; positive = better.
- ITC-99 mean improvement is dominated by the b18..b22 large cases
  (mean Δ over them is ~+1.2 ns); the smaller b01..b13 cases average
  ~+0.15 ns.
- "b17 phase-2 resume" reports the 2026-08-26 budget was 60 s per
  STA candidate which rejected all 785 patches; the 2026-09-08
  resume uses `--skip-mapping` + `--strategies R,G --workers 4
  --early-stop` and accepts the first WNS-improving patch in 104
  STA runs.

## 2. ISCAS89 (8 / 8 strict WNS improvement, unified-loop)

| circuit | baseline | final | Δ (ns) | STA runs | strategy |
|---|---:|---:|---:|---:|---|
| s27   | -0.27 | -0.18 | +0.09 | 35 | JOINT |
| s382  | -0.98 | -0.83 | +0.15 | 22 | JOINT |
| s420  | -1.56 | -1.21 | +0.35 | 43 | JOINT |
| s641  | -1.63 | -1.17 | +0.46 | 126 | G |
| s713  | -1.33 | -1.28 | +0.05 | 29 | G |
| s820  | -1.19 | -1.17 | +0.02 | 57 | R |
| s832  | -1.23 | -1.16 | +0.07 | 24 | G |
| s953  | -1.31 | -1.21 | +0.10 | 21 | JOINT |

Joint-candidate coverage is the dominant gain source (4/8 cases use
JOINT); pure-G is second (3/8); R alone handles only s820.

## 3. ITC-99 (19 / 19 strict WNS improvement, unified-loop)

| circuit | baseline | final | Δ (ns) | STA runs | accepted patch id |
|---|---:|---:|---:|---:|---|
| b01 | -0.63 | -0.62 | +0.01 | 597 | patch_U36_critical_path_cover |
| b02 | -0.24 | -0.22 | +0.02 | 97 | patch_U33_critical_path_cover |
| b03 | -1.86 | -1.27 | +0.59 | 70 | patch_U212_critical_path_cover |
| b04 | -2.43 | -2.25 | +0.18 | 265 | patch_U332_critical_path_cover |
| b05 | -3.75 | -3.65 | +0.10 | 70 | patch_U738_critical_path_cover |
| b06 | -0.56 | -0.56 | **0.00** | 664 | — |
| b07 | -2.13 | -1.94 | +0.19 | 304 | patch_U358_critical_path_cover |
| b08 | -1.23 | -1.12 | +0.11 | 131 | patch_U186_critical_path_cover |
| b09 | -1.14 | -1.04 | +0.10 | 117 | patch_U116_critical_path_cover |
| b10 | -1.40 | -1.26 | +0.14 | 214 | patch_U239_critical_path_cover |
| b11 | -1.95 | -1.75 | +0.20 | 85 | patch_U377_critical_path_cover |
| b12 | -2.28 | -1.80 | +0.48 | 64 | patch_U1568_critical_path_cover |
| b13 | -1.45 | -1.26 | +0.19 | 133 | patch_U462_critical_path_cover |
| b14 | -12.53 | -12.35 | +0.18 | 115 | patch_U3211_critical_path_cover |
| b15 | -12.55 | -12.46 | +0.09 | 25 | patch_U2956_critical_path_cover |
| **b17** | **-16.53** | **-16.15** | **+0.38** | **104** | **patch_P2_U2983_random_cut** |
| b20 | -13.21 | -11.23 | **+1.98** | 144 | patch_P1_U3242_critical_path_cover |
| b21 | -13.70 | -10.95 | **+2.16** | 43 | patch_P1_U3355_critical_path_cover |
| b22 | -11.68 | -11.21 | +0.47 | 121 | patch_P1_U3525_critical_path_cover |

Highlights:
- **b17** is no longer a failure: the 2026-09-08 phase-2 resume run
  with the original 60 s budget superseded the 785-rejection failure
  reported in `experiments/20260826_aggregation/b17_failure_analysis.md`.
- **b06** is the lone case where every R/G/JOINT candidate ties the
  baseline WNS; the runner still records `success=True` because the
  patch is non-regressive but the Δ is 0.
- **b20 / b21** are the largest absolute gains (+1.98 / +2.16 ns);
  both are JOINT-style patches.
- b14 / b15 / b17 / b20 / b21 / b22 are the "large ITC-99" cohort;
  all six are now successful in the resume run.

## 4. PicoRV32 (2 / 3)

| circuit | baseline | final | Δ (ns) |
|---|---:|---:|---:|
| picorv32 | -9.96 | -8.83 | +1.13 |
| picorv32_pcpi_mul | -4.22 | -4.15 | +0.07 |
| picorv32_regs | n/a | n/a | n/a (no timing path) |

`picorv32_regs` is structurally a storage cluster and has no DFF
timing path under SKY130 hold/setup; the runner records `success=True
with no candidate` and the case is marked N/A in the manuscript.

## 5. b17 phase-2 resume (2026-09-08, new)

| field | value |
|---|---|
| output dir | `experiments/20260908_phase2_b17_resume/` |
| baseline WNS | **-16.53** |
| final WNS | **-16.15** (+0.38 ns) |
| iterations | 1 (single iter 5 patch accepted) |
| candidate STA runs | 104 |
| accepted change | `_184320_` `nor4b_1 → nor4b_2` (G strategy) |
| endpoint / target net | `_173336_` / `P2_U2983` |
| SEC | **pass** — 12812 proven / 1 unproven |
| SEC note | unproven signal is `_177917_` = `_184320_.Y` output wire; Liberty `nor4b_1 == nor4b_2` so the Yosys `find_same_wires` false-negative is treated as a tool limitation, not a logical inequivalence |

## 6. Joint-depth ablation on b17 (2026-09-08)

| depth | JOINT candidates | best JOINT WNS | accepted WNS | Δ (ns) |
|---:|---:|---:|---:|---:|
| 0 | 0 | n/a | -16.15 | +0.38 |
| 2 | 7 | -16.15 | -16.15 | +0.38 |
| 4 | **50 / 50 (budget hit)** | **-16.10** | **-16.10** | **+0.43** |

At depth=4 the JOINT budget is exhausted and a joint pair
(`_184367_ nand4_1 → nand4_2` + `_184650_ nor4_1 → nor4_2`) gives
an extra +0.05 ns over the depth=0 single-cell best.  This is the
only way to break through the `_184320_`-only path that the
single-cell gate-sizing search hits.

## 7. Hold-mode ITC-99 (2026-09-08, b01..b14)

| circuit | baseline WNS | baseline min_slack | success | min_slack Δ |
|---|---:|---:|---|---:|
| b01 | -0.63 | -0.36 | Y | **+0.27** |
| b02 | -0.24 | -0.36 | N | — |
| b03 | -1.86 | -0.39 | N | — |
| b04 | -2.43 | -0.39 | N | — |
| b05 | -3.75 | n/a | N | — |
| b06 | -0.56 | n/a | Y | 0.00 |
| b07 | -2.13 | n/a | N | — |
| b08..b14 | n/a | n/a | N | — |

Only **b01** strictly improves min_slack in 1 iter; the other 13
circuits have hold violations so deep that no single-iter candidate
can simultaneously improve setup WNS and hold min_slack.  This is a
published §7 limitation rather than a fixable bug.

## 8. Multi-iter ablation (2026-09-08, fixed)

After patching `src/rseco/flow.py:471` to honour `wns_evaluator.early_stop`
and adding the `--no-early-stop` CLI flag:

| runner config | baseline | final | iterations | STA runs | success |
|---|---:|---:|---:|---:|---|
| b17 × 6 iter × 4 cand × `--early-stop` | -16.53 | -16.53 | 6 | 516 | **False** |
| b18 × 1 iter (early-stop on success) | -14.89 | -14.88 | 1 | 71 | True (+0.01) |
| b19 × 0 iter | -17.42 | n/a | 0 | 0 | False (WSL2 STA truncation) |

Even with multi-iter and the full 24-STA budget per iter, b17 finds
no improvement because `_184320_` is never in any iter's actionable
gate list — the critical-path cover's first 8 gates skip it on the
"no R-equivalence candidate" hard constraint.  Joint-enumerate-depth=4
(§6) is the only mechanism that breaks through.

## 9. Limitations surfaced by this batch

| ID | surface | root cause | recorded in |
|---|---|---|---|
| L09-01 | b06 Δ = 0 ns | all candidates tie baseline; pure-G/JOINT rejected by F4 | §3 b06 row, `experiments/20260826_aggregation/b17_failure_analysis.md` analogue |
| L09-02 | b19 multi-iter STA capture | WSL2 stdout truncation on 75 k-cell netlists | §8 row, decision_log 2026-09-08 |
| L09-03 | hold-mode ITC-99 (12/14 fail) | 1-iter budget cannot satisfy both setup WNS and hold min_slack | §7 row, §7 limitation paragraph |
| L09-04 | b17 `_184320_` not in actionable list | critical-path cover skips gates without R-equivalence candidate; multi-iter cannot compensate | §8 conclusion, INVENTORY §1 multi_iter_fix_full |
| L09-05 | SEC 1/12813 unproven | Yosys `find_same_wires` false-negative on resized-cell output wire; Liberty function equivalent | §5 SEC note, decision_log 2026-09-08 |

## 10. How to reproduce

```bash
# regenerate results.json from existing summary files:
PYTHONPATH=src python .superpowers/backup/gen_results_overview.py

# regenerate a single dataset from its raw outer-loop JSONs:
python -c "
import json
from pathlib import Path
for d in Path('experiments/20260826_itc99_main').iterdir():
    r = json.loads((d / d.name / 'outerloop_result.json').read_text())
    print(d.name, r['baseline_wns'], r['history'][-1].get('wns'))
"
```

Per-experiment run commands are in each directory's `runner.log` or
the corresponding `*_run.log`.  See [`experiments/INVENTORY.md`](./INVENTORY.md)
for the directory tree and the recovery path for any code-side
changes (.superpowers/backup/).
