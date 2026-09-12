# b06 root-cause analysis (2026-09-09)

## 1. Baseline and headroom

- circuit: **b06** (ITC-99)
- baseline WNS: **-0.56** ns
- baseline TNS: -3.92 ns (one path)
- baseline min_slack: +0.53 (hold is fine; only setup fails)
- period: 0.5 ns; headroom to baseline = -0.56 + 0.5 = -0.06 ns
- **b06's WNS deficit is only -0.06 ns**, the smallest absolute
  deficit of all 19 ITC-99 circuits (b07=-2.13, b17=-16.53).

## 2. Head-to-head: pure G vs unified (R+G+B+JOINT)

| metric | pure_G_only | unified |
|---|---:|---:|
| strategies | ['G'] | ['R', 'G', 'B'] |
| STA runs | 148 | 664 |
| success | False | True |
| best trial WNS | -0.56 | -0.56 |
| trials == baseline | 12 | 333 |
| trials < baseline | 136 | 331 |

**Verdict**: pure G in b06: 0 improvement; unified R+G+B+JOINT also 0.
**Not a strategy-choice problem -- b06 is structurally hard-fail for every local candidate.**

## 3. Why every strategy ties baseline

Looking at the critical instance `_276_` (or4b_1, the single most
tested cell in b06):

| strategy | new type | WNS | Delta vs baseline |
|---|---|---:|---:|
| G | or4b_2 (drive x2) | -0.71 | -0.15 |
| G | or4b_4 (drive x4) | -0.57 | -0.01 |
| B | buf_1 on input A | -0.56 | 0.00 |
| B | buf_2 on input A | -0.56 | 0.00 |
| B | buf_1 on input B | -0.62 | -0.06 |
| B | buf_2 on input C | -0.60 | -0.04 |

In pre-layout (ideal-net) timing:
- **G**: upsizing increases input capacitance on or4b's 4 inputs;
  the previous stage now has to drive 2-4x more cap, which makes
  the *upstream* delay longer. b06's critical path has multiple
  consecutive or4b instances, so the chain reaction dominates.
- **B**: buffer insertion adds a new gate on the high-fanout
  net feeding or4b, increasing the input delay. B helps when
  there is a single low-fanout net between two critical gates;
  b06's structure does not have that pattern.
- **R**: or4b_1 has no functionally-equivalent cell of a different
  family in SKY130 HD (verified by `equivalence_candidates` in
  `src/rseco/logic_rewrite.py`).
- **JOINT**: cannot rescue because every R and G candidate ties
  baseline; nothing to joint.

## 4. Magnitude of the bound

- best WNS in 664 unified trials: **-0.56** (= baseline).
- 333/664 trials reach exactly -0.56; **0 trials exceed baseline**.
- 57 trials land at -0.57, only -0.01 ns worse.
- This is consistent with the small absolute headroom: the setup
  constraint is *barely* violated (-0.06 ns), and the OpenSTA
  delay model has intrinsic discretization around 0.01 ns.
- **Realistic conclusion**: at the pre-layout stage b06 sits at
  the floor of the perturbation budget that the library can
  resolve; post-layout wire-load feedback is needed for the next
  -0.06 ns.

## 5. Comparison with other 'zero' circuits

- In the unified 19 ITC-99 batch, b06 is the only circuit with
  zero improvement. b17 *was* zero in the 60s-budget 20260826
  run but the 20260908 resume recovered +0.38 ns.
- In the pure-G 20260806 ablation (gfail_b06 baseline), b06 was
  the *named* failure case -- this is why the directory is
  called 'gfail_b06'. The pure-G run produced 0 improvement and
  flagged b06 as the worst case; the unified R+G+B+JOINT was
  then designed to address exactly this failure mode.
- After unification, b06 went from 0/148 pure-G to 0/664 unified
  (same outcome). The other 18 ITC-99 circuits improved; b06
  is genuinely the circuit where no candidate can lift the
  WNS.

## 6. What FAECO can still do to address b06

1. **SPEF gate re-measure**: this is already in the runner as
  `--physical-gate`; with physical wire load the input-cap
  effect of G/B changes is partially absorbed (the upstream
  driver sees real wire RC, not pure cell delay). The unified
  batch did not enable --physical-gate for ITC-99; rerunning
  b06 with `--physical-gate --physical-unit-len 5` may lift
  the bound.
2. **Hold-mode multi-iter**: not in scope here; b06 fails on
  setup, not hold.
3. **Add an explicit 'no-improvement' ceiling**: the runner
  currently keeps searching until max_iterations. Once best
  trial WNS equals baseline for 2 consecutive iterations, the
  runner could exit early with a documented 'ceiling reached'
  status. This would save ~664 STA runs on b06 (and similar
  on other 'barely violated' circuits in future batches).
4. **Net restructuring** (move or split the four back-to-back
  or4b instances): requires a higher-level topology change,
  outside FAECO's local cone scope.

## 7. Recommendation for the manuscript

- **Keep the section 7 limitation paragraph** for b06. It is honest
  and well-grounded.
- **Add the structural root cause** in one sentence: 'b06's
 critical path contains four consecutive or4b_1 instances
 whose only viable candidates (size up, buffer on input) all
 degrade the upstream delay in pre-layout ideal-net timing.'
- **Cite the unified R+G+B+JOINT evidence**: 0/664 trials
 exceed baseline, 333 tie baseline -- the search exhausted
 every candidate, not just the 'easy' ones.
- **Forward-point**: mention `--physical-gate` as a known
 remediation for the next paper / future work, without
 claiming it on the current dataset.

