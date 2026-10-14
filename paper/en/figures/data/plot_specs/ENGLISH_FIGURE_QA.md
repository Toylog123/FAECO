# English r21 figure contract and visual audit

Backend: Python, inherited from the native r21 figure sources. This local preference applies to the English derivative package. Original evidence, circuit inclusion, units, transformations and negative outcomes are preserved. English labels and figure placement are adapted; no new measurements, interpolation, statistical tests, confidence intervals or averaging of budget curves are introduced.

Figures 1–2 reuse `paper/zh/figures/data/scripts/review_r21_figures.py`; Figure 3 adapts only the current `gen_figures.py` paired plot and its `pre_layout_audit_summary.json` input. Figures 4–7 reuse r21 calculations. The full experiment paths and input hashes are in `r21_source_manifest.json`; adaptation-source hashes are in `../../../submission/source_binding.json`.

| Figure/panel | Unique evidence role | Summary and repeat unit | Spread | Visual check |
|---|---|---|---|---|
| 1 | Candidate evaluation, feedback and iterative submission | Conceptual workflow; no data unit | Not applicable | All arrows/labels checked; final SEC remains after search |
| 2a | Cone dependencies, critical path and R availability | Illustrative six-gate construction | Not applicable | Node/edge labels and legend clear |
| 2b | Node-splitting capacities and candidate construction/ranking | Same conceptual construction | Not applicable | Internal capacities and infinite links distinguishable; lower strategy boxes clear |
| 3 | Baseline versus repair in the single-round family | Raw paired WNS, eight circuits | No repeated runs claimed | Near-zero gain label and legend moved into clear space; all eight pairs retained |
| 4a | Unified ISCAS89 gains | Raw circuit gain, eight circuits | No repeated runs claimed | All values/labels visible |
| 4b | Unified ITC-99 gains and unchanged b06 | Raw circuit gain, 19 circuits | No repeated runs claimed | Full inclusion, long-tail circuits and zero result retained |
| 4c | PicoRV32 gains and no-setup-path exclusion | Two assessable modules; register bank excluded explicitly | No repeated runs claimed | Both values and denominator note visible |
| 5, s27 | Measurement cost and natural stopping points | Individual Fixed/EMA/three-seed curves | All seed traces shown | Curves/endpoints clear; no extrapolation |
| 5, s382 | Measurement cost and seed-dependent endpoint quality | Individual curves | All seed traces shown | Same axes/legend semantics; no averaging |
| 5, s420 | Accumulation under five configurations | Individual curves | All seed traces shown | Full trajectories retained |
| 5, s641 | Random seed 1 exceeds Fixed terminal gain | Individual curves | All seed traces shown | Unfavorable comparison preserved |
| 5, s713 | Similar endpoints at different measurement costs | Individual curves | All seed traces shown | Terminal dots distinguish natural lengths |
| 5, s820 | Small gains with different measurement costs | Individual curves | All seed traces shown | Tick labels/curves readable |
| 5, s832 | Lower randomized endpoint gains | Individual curves | All seed traces shown | Full differences retained |
| 5, s953 | All randomized endpoints exceed Fixed | Individual curves | All seed traces shown | Unfavorable comparison preserved |
| 6 | Gain retention under estimated physical parasitics | Paired gains, eight circuits in the single-round family | No repeated runs claimed | Five positive, one unchanged and two negative results visible |
| 7a | Depth reduction is an insufficient timing proxy | Candidate counts by circuit; same 126-candidate pool | Deterministic archive, no interval | All circuits, including zero-window s641, shown |
| 7b | No timing improvement from expanded S pool | WNS classification of the same 126 candidates | Deterministic archive, no interval | 36 unchanged and 90 worsened outcomes retained |

No microscopy, raster scientific observation or image-intensity processing is involved. PDF/SVG text remains editable. All seven exported PDFs have a 7-point minimum glyph size. Full manuscript rendering was reviewed after figure inclusion; the preprint scale remains readable. Publisher/journal upload dimensions and allowed preview formats are still subject to the official Integration guide check.
