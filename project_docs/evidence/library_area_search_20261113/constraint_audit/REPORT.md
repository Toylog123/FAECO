# Existing constraint coverage

Two exact-endpoint read-only STA calls completed, no routing or optimization. CONTROL and accepted096 both report3 missing input delays (CLR/FM/TEST),6 missing output delays and6 unconstrained output endpoints (GRN1/GRN2/RED1/RED2/YLW1/YLW2). The clock and original constraints were unchanged. WNS/hold reproduce the archived measurements; this does not certify IO timing. The unconnected tap black-box warning is retained and does not supply timing paths.

The user subsequently changed optimization preference to WNS-primary/TNS-secondary; this does not resolve missing IO coverage. Future papers must state the actual constrained scope and supply a justified complete SDC before claiming whole-design timing closure. Do not invent IO budgets and present them as original benchmark specifications. New cost:2 diagnostic STA,0 routes, separate from the unexecuted25-candidate proposal.
