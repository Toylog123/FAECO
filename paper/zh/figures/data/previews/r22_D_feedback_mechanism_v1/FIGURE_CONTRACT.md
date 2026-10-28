# Figure contract — D feedback diagnosis, two completed pilot circuits

Question: Why do fixed and EMA D/beam8 runs on s27 and s382 have identical endpoints and actual candidate STA sequences?

Claim: EMA feedback updates weights and can change candidate order, while the retained traces show no new dispatch identities after feedback starts in these two cases; evaluator-side work remains identical. This is a bounded diagnosis, not evidence for general effectiveness or ineffectiveness.

Scope: only D/fixed and D/adaptive, s27/s382, 20 rounds, legacy constrained cut policy, beam8, max_instances8. No other six circuits, k1, historical D result replacement or full56 conclusion. No new EDA or algorithm modification.

Archetype: quantitative grid, two complementary evidence rows. a/b show actual in-force boundary, size and critical-coverage weights per round for s27/s382, with fixed weights at1. c/d show round-level order/set differences relative to fixed, and whether adaptive dispatch contains any identity not offered earlier at the same base. Actual candidate and STA sequence agreement is separately labelled with measured counts, so candidate set equality is never substituted for evaluation equality.

Source binding: immutable MECHANISM_AUDIT.json from actual_v2, its original read manifest, ROOT_COMPLETION_AUDIT_07, and four exact completion bytes. Rendering must refuse mismatched hashes, wrong circuits/arms/beam or unmatched actual STA sequences. Source CSV keeps all80 arm/circuit/round weight observations and all40 matched round diagnostic rows, no interpolation/sampling/aggregation.

Display: Python/Matplotlib only; style-only inheritance from existing matrix plot (sans-serif/editable text, color families, export settings), fresh semantics. Preview 170x135mm, minimum6.8pt, PDF+SVG+600dpi PNG. No significance/uncertainty claims: each arm is one deterministic run, raw traces, no error bars. Three adaptive weights may coincide at1; markers/line styles and caption disclose coincident paths, fixed baseline stays1.

Mandatory QA: actual render-time comparable-panel alignment <=1.5pt, source validator, actual PDF font floor >=5pt, rendered collision auditor, whole-figure and every-panel PNG/PDF visual review. Preserve each failed render/audit in its own exclusive iteration folder. Main manuscript untouched.
