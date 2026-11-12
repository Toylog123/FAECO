# CONTROL candidate-space audit

Static audit of this package's complete `inputs/CONTROL/routed.v` and fixed TT Liberty, with no EDA execution or changes to the registered nine-pair study. `SPACE_AUDIT.json` binds the CONTROL, recipe, Liberty, complete structural Reader and audit script by SHA-256 and records all candidates, all functional instance bindings, exact excluded tap IDs and full source/target logical signatures. Sources were unchanged across the read.

## Result

The original 13-action rollback recipe covers **10 of 62 strictly smaller-area compatible instance/target pairs (16.129%)**. Its other three actions have zero area saving. There are **33 instances** with at least one enumerated downsize. Thus, the historical recipe is a small candidate subset, not a complete area-recovery candidate generator.

| Category | CONTROL instances | Instances with downsizes | Compatible smaller-area pairs | Recipe pairs covered |
|---|---:|---:|---:|---:|
| Other combinational families | 73 | 21 | 36 | 10 |
| Sequential | 21 | 8 | 12 | 0 |
| Clock buffer/inverter families | 8 | 4 | 14 | 0 |
| Total | 102 | 33 | 62 | 10 |

Complete parse: 3,128 instances, including exactly 3,026 zero-connected-pin `sky130_fd_sc_hd__tapvpwrvgnd_1` physical taps; 102 functional cells and 335 connected pin bindings. Functional mapped Liberty area is **1052.2592**, excluding those physical taps. Taps have no entry in this timing Liberty; exclusion is explicit and does not assert their physical area is zero. The 52 omitted pairs comprise 51 pairs on 23 entirely unrepresented instances, plus one extra target on a recipe instance. There were zero smaller same-family alternatives rejected by the conservative signature equality rule in this CONTROL's families.

## Specific omissions

- `_054_`: current `or3b_4` can target `or3b_2` as well as the historical `or3b_1`. Both targets have area 8.7584 versus source 11.2608, saving **2.5024**. An intermediate drive need not have intermediate area; its timing is unknown here.
- Four escaped FF instances `DFF_0/_0_`, `DFF_1/_0_`, `DFF_11/_0_`, `DFF_12/_0_` use `dfxtp_4`. Each has `dfxtp_2` and `dfxtp_1` alternatives, saving 2.5024 and 3.7536 respectively. Four more (`DFF_9/_0_`, `DFF_10/_0_`, `DFF_18/_0_`, `DFF_19/_0_`) use `dfxtp_2` and have `dfxtp_1` alternatives saving 1.2512. The remaining 13 FF instances use `dfxtp_1` and have no smaller-area same-family target.
- All FF alternatives have exactly the same complete state group: `ff("IQ","IQ_N")`, `clocked_on: "CLK"`, `next_state: "D"`; no clear or preset field is present in either source or target. CLK/D/Q pin names, directions, clock flags, Q function `IQ`, power-down function and all PG metadata match. Full state-group attribute equality, not output-function-only matching, is required.
- Three `clkbuf_16` clock instances each have targets 1/2/4/8; `clkload0` (`clkbuf_4`) has targets 1/2. `clkload0` has an intentionally unconnected X output, retained in the inventory and full library signature; it is a clock loading element, so its downsize can change clock behavior despite no output connection. Four `clkinv_1` instances have no smaller target. Clock-family is a library-name category, not an inferred clock-net graph classification.
- Other omitted instances include `_051_` (`nor4b_4`→1/2), `_059_` and `_063_` (`o21ai_2`→0/1), and eight `rebuffer*` instances with smaller `buf` variants. Full IDs and target lists are in JSON.

## Rule and limitations

Enumeration visits every functional instance, including escaped identifiers, and every cell in its fixed-Liberty family. A target must have strictly smaller Decimal area and identical complete functional pin names/directions/non-electrical attributes, all output functions and three-state conditions, all PG pin metadata, all sequential group headers and attributes, and remaining cell metadata. Family is the full name excluding its final integer drive suffix. No renaming, Boolean-equivalence solver or cross-family substitution is used. Unknown syntax or missing connected pins fails closed; unconnected outputs are recorded. The existing repository Liberty parser independently agrees on family, inputs, outputs, three-state and FF semantics for all 62 emitted pairs.

Electrical capacitance/limits, timing tables, internal/leakage power and waveform data are deliberately not equality requirements: those vary with sizing and must be evaluated later. No candidate is certified for setup/TNS/hold, DRV, legalization, routing, clock integrity or formal equivalence. The enumeration is conservative within the stated family definition and excludes equal-area changes, cross-family equivalents, cell removal, buffering/topology edits and placement-specific restrictions. Counts of targets at one instance are alternative choices; their area savings must not be added together.

The finding supports expanding candidate generation beyond rollback history, with provenance retained as an optional feature. It does not demonstrate improved area under the strict physical timing gate, validate a new optimizer, or establish novelty. The current frozen nine-pair scheduling experiment remains scoped to its registered historical-action subset.

## Reproduce

Run `.venv/Scripts/python.exe project_docs/evidence/strict_area_search_20261113/space_audit/audit_space.py` from the repository root. This regenerates only `space_audit/SPACE_AUDIT.json`; it invokes no EDA. Initial fail-closed parsing encountered unrelated full-library `statetable`/`test_cell` structures, then parsing was scoped to the complete set of CONTROL families, as required by this audit. The reader also exposed the valid unconnected `clkload0.X`; output omissions are now explicitly recorded rather than silently dropped.
