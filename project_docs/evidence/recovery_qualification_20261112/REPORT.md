# Recovery qualification: first physical gate

2026-11-13; status **NON_PROMOTION**. This report records a bounded qualification milestone, not completion of the ICCAD research objective.

## What changed

The old summary overstated total mapped-cell percentage savings because escaped instance names were not counted by the CLI. Complete parsing of 28 original/recovered exports gives 14-design mean reduction **3.071500828%** (arithmetic mean); maximum b07 **7.810443177%**. Absolute savings are unchanged in every pair. Source: `area_audit.json`, independent Decimal Liberty parsing, all connected instances accounted for. This scope includes every Liberty-known exported cell including clock/probe cells and excludes explicitly listed unconnected physical tap cells. It is not die area. Historical added-area recovery percentages still require hierarchy-aware baseline accounting.

## s382 same-state physical pilot

Phase0 reconstructs archived DEF, checks complete named connectivity, and exactly reproduces archived setup/hold/TNS under the old ideal-clock model. All phase1_v2 arms then use the same reconstructed OpenDB state, placement legalization, full rerouting and RCX extraction. No second clock tree is built. Endpoint STA reads each arm's own final netlist and new SPEF. Native recovery uses the installed 26Q3 `recover_power 100`; no tuning claim is made.

| Arm | Complete mapped-cell area (um²) | Change vs CONTROL | Propagated setup slack (ns) | Propagated hold slack (ns) | TNS (ns) | Route DRC |
|---|---:|---:|---:|---:|---:|---:|
| CONTROL | 1052.2592 | 0 | -0.8484588032 | 0.4636368511 | -13.422543 | 0 |
| RECOVERY_V2 | 1005.9648 | -4.399524% | -0.8584304378 | 0.4636182549 | -13.735190 | 0 |
| NATIVE | 1052.2592 | 0 | -0.8484588032 | 0.4636368511 | -13.422543 | 0 |

The archived 13-swap recipe saves area but violates the preregistered strict non-worsening tolerance (1e-6 ns): setup degrades **0.009971635 ns**, hold **0.000018596 ns**, and TNS **0.312647 ns**. This is a failed strict safety gate, not proof that recovery cannot work. It is within some historical user-set WNS budgets; that tradeoff must not be relabeled as unchanged timing. All arms retain setup violations.

Native recovery resized zero cells. This pilot therefore does not establish superiority over a tuned native or strong sequential baseline. Reports show no slew/capacitance violations, but complete SDC and constraint coverage have not been established; empty reports alone do not close that gate. SEC is recorded separately under `sec/`, with explicit model-domain and normalization receipts; only those receipts determine proof status.

Both full-netlist SEC comparisons passed: CONTROL vs RECOVERY_V2 and CONTROL vs NATIVE, each 101 proven / 0 unproven, with all102 functional cells and21 flip-flops represented. Each proof input explicitly removes only3026 unconnected tap instances. The legacy SEC cell scanner also missed escaped FF names; an evidence-local adapter supplies the complete parsed cell set to the unchanged Liberty model generator. Its preregistration, failure-original and complete hashes are retained. This establishes Boolean sequential equivalence in the documented model domain, not physical safety. DRC=0 is limited to supported rules: route logs warn that LEF58_ENCLOSURE rules without CUTCLASS were skipped.

## Engineering validation and preserved failures

- Full regression: **1113 passed, 156 subtests**, 144.22 s. Affected conversion/demo/CEC tests rechecked after a concurrent cleanup race: **24 passed**, 29.35 s.
- Recovery zero-value/import bugs fixed with red/green tests. Installed Yosys remains unchanged; same-byte colocated DLL mirror solves packaged Windows loader failures. `prepare_packaged_yosys.py` makes that workaround reproducible.
- CONTROL v1 failed DRT-0626 because existing signal wires left no new guides. Original driver/logs retained. Version2 clears regular signal wires in the copied database before all-arm rerouting; special power wiring and original artifacts are preserved.
- Structural replay: all3128 instances,335pin bindings,10ports,109declarations,4assigns match; only top-level port ordering changes. This does not license positional parent connections.

## Required next gates

1. Repair production instance parsing and baseline hierarchical area accounting with regression tests, without silently expanding the scientific candidate set.
2. Put complete physical constraints into acceptance, distinguish absolute closure from non-worsening, and attribute fixed-SPEF vs new-SPEF and ideal vs propagated-clock differences.
3. After the measurement chain is sound, compare strong iterative/sequential and tuned native recovery at equal budgets, then test whether joint selection adds anything.

Frozen manuscripts are unchanged. The 14 archived outputs were audited without 14 new physical runs; only s382 has the new three-arm physical pilot. Do not extrapolate its outcome to all circuits.
