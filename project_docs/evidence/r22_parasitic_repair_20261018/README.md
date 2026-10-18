# OpenSTA report order and two-sided SPEF measurement repair

Client date: 2026-10-18. Historical raw timestamps are retained; new receipts
record actual UTC separately. This directory contains implementation QA, not
new scientific OpenSTA/SEC/physical EDA measurements.

Implementation scope: code/src/rseco/opensta.py,
code/scripts/run_parasitic_aware_check.py, and the dedicated
code/tests/test_r22_parasitic_measurement.py. SPEF connectivity/parser repair
and production evaluator integration belong to the main agent.

## Counterexamples retained

- red/RED_RECEIPT.json: 8 failed / 1 passed. The actual generated sequential
  Tcl's first path report preceded read_spef; a native deterministic boundary
  executable therefore emitted ideal path slack -0.1 and annotated WNS -0.9.
  Nonzero exits and actual-format Error/Warning 1647/1652 missing-pin diagnostics
  still yielded floats. The comparison generated only one baseline SPEF.
- red2/RED_RECEIPT.json: 12 failed / 2 passed. Additional launch, timeout,
  immutable output, and unparseable-result controls failed before production
  modification. The ordinary error_counter_reg report text control passed.
- red3/RED_RECEIPT.json: 2 failed / 17 passed. A Tcl modified during the tool
  invocation could be certified with an after-only SHA; an SPEF modified between
  generation and its physical measurement could similarly be accepted.
- red4/RED_RECEIPT.json: 2 failed / 19 passed. Concatenating stdout without a
  trailing newline with stderr hid an anchored Error diagnostic in both runners.

The synthetic miniature Liberty in the tests uses explicitly named probe cells
and real pin direction declarations. It is a test fixture, not a claim about
an actual SKY130 production cell. The first neighboring run used unsupported
generic cell syntax in this fixture; the fixture was adapted to the existing
SKY130 Liberty extractor, retaining the independently specified Y-to-Z pin change.

## Final bounded QA and behavior

green4/GREEN_RECEIPT.json records 71 passed in 6.43 seconds, wrapper 10 seconds,
exit 0, bounded by 300 seconds. It contains exact source/test/log and generated
control artifacts. The local command captured exact sources at completion,
not a before/after stability claim; the main integrated regression must bind
the frozen sources before and after its run.

With SPEF, all sequential timing reports follow annotation. Successful
non-SPEF sequential Tcl order and result fields retain their existing behavior.
Tool errors and confirmed missing-pin warnings are checked in each output
stream separately. Failed sequential launches, timeouts, and diagnosed runs
return null metrics and keep numbered failure Tcl/log snapshots plus receipts.

The comparison parses baseline and repaired netlists separately with explicit
actual Liberty text and top, produces separate SPEFs with the same RC parameters,
and measures each side's own files. Receipts bind netlist, Liberty, RC, SPEF,
before/after Tcl, log, period, clock, and argv. Generated SPEFs are pinned across
measurement stages. Failed/unparseable/changed inputs cannot yield valid floats.
The original required period and default CK clock are retained; --clock-port
allows the actual clock to be specified. Existing comparison output directories
are rejected without overwriting. Early parser/input failures leave failure.json;
no timing Tcl exists if measurement was never reached.

No source commit, formal experiment registration, EDA campaign, manuscript,
or figure change was performed by this bounded implementation task.
