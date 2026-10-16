# Independent B2 explicit-X review — 2026-10-16

This review is independent of the primary checker author. It changes no production source or tests and runs no EDA. The primary API reviewed is `project_docs/evidence/r22_b_model_audit_20261016/x_identity_certificate.py`, SHA256 `66fe72ff542c55f421bce6a2c234749ed802095372a0e2ed0189b1f695cab91a`. The review is valid only for these bytes and the four raw hashes below; a later checker change requires replay.

## Actual source scope

The scope JSON and all four raw files were opened and independently tokenized, rather than accepting a text substring scan. `independent_x_review.py` imports neither the production parser nor the primary API. Its `B2_X_INDEPENDENT_REVIEW.json` records all exact assignments, declarations, header order, width, port role, and byte hashes. Both core raws have seven identical isolated constant-X sources: internal `cpuregs[0]` (32), `decoded_rs` (5), `pcpi_int_rd`, `pcpi_div_rd`, `pcpi_mul_rd` (32 each), and direct primary outputs `trace_data` (36), `pcpi_insn` (32). The internal sources occur only in declaration and constant assignment; the outputs occur only in header, output/wire declarations, and constant assignment. No other whole identifier token is used. Both mul raws contain zero explicit X literals in this supported mapped syntax.

| Object | Raw SHA256 |
|---|---|
| core original `experiments/20260826_picorv32_hetero/picorv32/mapped.v` | `67a47d9d78215ed2422bf5076fb609baae096c74e8e557aa54aa42fc2f3e0429` |
| core accepted `experiments/20260826_picorv32_hetero/picorv32/eval/iter008_cand008/001__07114__B/mapped.v` | `b5fd51c45519123c9eb293a7d347ad57c4bed053e83875d51752a01e0297704b` |
| mul original `experiments/20260826_picorv32_hetero/picorv32_pcpi_mul/mapped.v` | `1097f15e277ed20a86b75e94c1bd996002ed3413a15ef305e5eebcbd3f6a5232` |
| mul accepted `experiments/20260826_picorv32_hetero/picorv32_pcpi_mul/eval/iter005_cand005/048__0790__B/mapped.v` | `d64a98ec6e5b105aa736352d3733551918cd4308a0cf696bf51449b8c707180c` |

An exact identity certificate can separately discharge these isolated constant-output expressions: they do not influence any other signal, and their declarations and drivers are unchanged. The five dead internal sources need no functional propagation argument. This permits a *scoped* combination with an independently bound proof of the remaining supported logic. It does not establish that arbitrary other signals are always binary: uninitialized state, implicit/undriven nets, reset assumptions, sequential matching, library models, and Z/tristate semantics remain obligations of the separate proof. Neither a zero-X certificate nor a Yosys pass may be promoted to unrestricted four-state equivalence or reset equivalence.

## Primary API review and adversarial results

`B2_X_PRIMARY_REVIEW.json` contains full synthetic source text and expected/actual result/reason for each independent probe, plus full actual-pair certificates. It can be replayed by importing the named checker and passing each text twice to `certify_pair`; no EDA is needed. The invocation code is retained at `scratch/r22_tristate_20261016/independent_primary_x_probes.py`. Logs are `independent_primary_x_probes.log` (first diagnostic, exit 1) and `independent_primary_x_probes_final.log` (exit 0, explicit known conservative mismatch retained), in the same scratch directory.

All 20 negative probes were rejected: concat/replication/select consumers, variable-select use, ordinary and escaped-name consumers in cell pins, partial/concat/escaped extra drivers, behavioral/function/primitive/parameter/attribute access, hierarchical access, duplicate module and comma/escaped duplicate declarations, non-assign X cell literals, and a helper-module X output escaping to its parent. Five of six positive controls certified, including comma declarations/outputs, an escaped source, prefix-distinct identifiers, and separate module namespaces. Both actual B2 pairs certified with seven and zero sources respectively. Source hash was stable before/after.

One conservative false negative was found, with no unsafe acceptance: `wire [3:0] \\output ; assign \\output =4'hx;` in otherwise valid mapped text is rejected because the canonical escaped name `output` also matches an unescaped declaration keyword in the global token-use scan. The full one-backslash Verilog source is stored in the JSON. This does not affect the four actual files; widening grammar to accept this unused case is unnecessary for B2. The first diagnostic's failure must not be described as 26/26 matched expectations: the accurate count is 20/20 negative rejection, 5/6 positive acceptance, and 2/2 actual pair certification.

No explicit-X false positive was found within the reviewed bounded grammar. Every complete statement is consumed, unsupported procedural/preprocessor/primitive/parameter/attribute constructs fail closed, X literals must be the complete RHS of one whole-net assignment, all uses are scanned across each module, and an instantiated module carrying an X output is rejected. This is a bounded review, not a formal proof of the Python checker.

## Independent scanner self-challenge

The independent scanner was strengthened during review to canonicalize escaped simple identifiers: `\\trace_data ` and `trace_data` denote the same Verilog name. This avoids a potential blind spot in the independent implementation. The primary checker already handled that alias correctly. The final independent scan rejected eight injected controls, including both escaped simple-name consumers and a bracket-bearing escaped identifier followed by a bit select. Final independent log: `scratch/r22_tristate_20261016/independent_b2_x_review_final.log`, exit 0, two pairs, eight negative probes, source stable.

Reproduce that independent check with:

```powershell
bash code/scripts/run_with_timeout.sh 120 .venv/Scripts/python.exe -X utf8 project_docs/evidence/r22_correctness_20261016/independent_x_review.py
```

## Binding required at use

A formal B2 receipt must bind raw **byte** hashes (not only text hashes normalized by reading), primary-checker bytes, each returned certificate, the exact initial/final raw and model/Lib/source artifacts used by the separate SEC, selected top, and its proof result. The certificate alone proves no equivalence. Re-run `certify_pair` at registration/execution and validate stored certificate/hash correspondence on resume; a static scope JSON is insufficient. Actual-used tristate/Z must retain the established unsupported/non-pass guard. Any changed input, model, checker, or production proof source requires a new pin and receipt.
