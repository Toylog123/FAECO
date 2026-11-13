# User-directed WNS-primary policy

2026-11-13. The user explicitly prioritizes WNS and considers TNS secondary after WNS qualifies. Adopt positive complete-cell area saving with propagated WNS >= fixed CONTROL -1e-6 ns, hold >= CONTROL -1e-6 ns and hold>=0, exact intended structure, supported-rule DRC0/configured DRV checks and final two-state SEC. TNS is reported in full, without a veto or hidden cap. Rank qualified measured endpoints by maximum area saving, then higher (less negative) TNS, then higher WNS, higher hold and lexical identity.

First reclassify all52 previously measured candidate endpoints (13+12+13+3 and9+2) using archived raw logs and hashes. No new optimization/routing/STA is executed for this reclassification. Original three-metric strict failures remain unchanged. This is post-measurement policy reuse prompted by the user, not an independently prospective algorithm experiment, not evidence that the original strict method improved, and not new independent samples.

Select the best audited point and bind the exact existing netlist/ODB/SPEF for full two-state equivalence proof against CONTROL. No reroute or logical regeneration. Each proof timeout180s, outer240s; preserve failure, no silent retry. Numerical eligibility is not accepted physical/logical qualification until proof and independent review finish. Disclose absolute WNS, hold and TNS plus their changes, area and missing IO constraints. Negative setup remains; no claim of complete timing closure or whole-design timing nondegradation.

The planned25 new library-target evaluations remain not executed until their new policy version is explicitly frozen and reviewed. Current historical eligibility does not resolve full IO constraints, multicorner/generalization, baseline tuning or ICCAD novelty.
