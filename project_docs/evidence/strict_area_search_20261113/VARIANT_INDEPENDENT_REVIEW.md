# Independent intermediate-drive review

Accepted as two valid negative measurements under final variant PLAN `e600cd53f9899d179152d6c84c0cc84476a96998f7e4f117d7f1b4fc4772c7f7`. `independent_variant_check.py` reuses the independent structural/raw-evidence checking approach, without importing the author's selection implementation. Its final `VARIANT_INDEPENDENT_AUDIT.json` binds source/receipt hashes and includes full endpoint identities, strict deficits and paired comparisons.

Both actual netlists match the entire CONTROL structure except exactly their registered one/two substitutions. `_054_` is `or3b_2`, with `_096_` changed only in the pair. Source and output SHA checks, raw ideal/propagated metrics, actual netlist/SPEF paths in STA scripts, wire clearing, extraction, supported DRC and configured slew/cap report checks all pass. The complete netlists retain all escaped FF instances and all original bindings/assignments. The original nine-pair summary remains unchanged.

| Variant | Saving | Δsetup vs CONTROL (ns) | ΔTNS (ns) | Δhold (ns) | Strict |
|---|---:|---:|---:|---:|---|
| `_054_` → `or3b_2` | 2.5024 | −0.034445057917 | −0.286940575 | −0.001212918654 | Fail |
| `_096_` plus `_054_` → `or3b_2` | 8.7584 | −0.034445057917 | −0.282325745 | −0.001212918654 | Fail |

At the same area as the corresponding historical `or3b_1` target, the singleton variant is worse by 0.031076086149 ns setup, 0.197851181 ns TNS and 0.000002692291 ns hold. The pair variant is worse by 0.033145597378 ns setup, 0.203731537 ns TNS and 0.000028560487 ns hold. Both comparison endpoints were read and hash-checked against their own archived rows. All four endpoints fail the strict gate; the pair-improvement hypothesis is not supported. The singleton was only an equal-area target diagnostic and cannot exceed the seed's saving by construction.

The first reported setup path changes from `DFF_20/_0_`→`DFF_11/_0_` in both `or3b_1` comparators to `DFF_12/_0_`→`DFF_3/_0_` in both `or3b_2` variants. The latter report explicitly traverses `_054_/X (sky130_fd_sc_hd__or3b_2)`. This confirms a changed limiting path containing the intended target. It does not isolate a Liberty-arc cause from input slew, loads or rerouting; no isolated delay-table or physical-location counterfactual was performed. Equal area and an intermediate drive suffix do not guarantee better timing in these measured implementations.

Independent final selection remains the exact SEC-proven `FORWARD__096_` endpoint, saving 6.2560 (0.594530321%). No new SEC is needed. These two failed targets do not imply the other omitted static targets are infeasible or disprove broader library-based candidate generation.

New cost is separately **2 routes / 4 STA**; runner time 55.484 s and summed jobs 55.375 s, shared-host observations. They do not enter the frozen nine-pair ordering results. Existing limited DRC/DRV coverage and two-state seed proof boundaries remain; this is not signoff or absolute timing closure. This review executed no EDA or SEC and changed no frozen source, PLAN or run artifact.
