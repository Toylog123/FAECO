# TNS hard-gate evidence (read-only, r25)

The exact Cprime-v3 runtime has a preceding setup-TNS hard gate. The earlier r24 acceptance expression omitted that gate; its WNS-only expression is incomplete. No EDA, source, or manuscript edits were performed.

## Exact runtime

- ZIP: `project_docs/evidence/r22_cprime_v3_20261016/source_snapshot/runtime_inputs.zip`, SHA256 `620a0eb9809dd08720fd4fdf4bdb85781668ff161a9b061936e7447ade442d7f`. Scientific runtime HEAD `3ea0f757f5e9bab4a2df75c458b0c665eabcb258`.
- `code/src/rseco/real_wns.py` member SHA256 `812bafab38f44c889ecb32b5503509b5a0d8e5ed78052507ffcf4a326a92918e`. Lines2269-2272 append setup_tns when candidate TNS < current reference TNS - epsilon. Lines2337-2342 mark this severity=hard/hard_gate=true; lines2673-2677 reject any hard event before WNS ordering. Lines2747-2753 implement WNS strict gain or optional TNS-aware tie.
- `code/scripts/run_outerloop_real_wns.py` member SHA256 `3d1c11bb9c6b1d061a960f879e009d55464d9c0b52a551bd6a64bf47adaabe0b`. Lines392-395 set strict_gates=true and strict_budgets=true, then pass required_metrics/epsilon. These two strict flags are hardcoded in the actual caller, not serialized fields in run_config.

### `code/src/rseco/real_wns.py`

Lines 2259-2272:
```python
        metric_references = {
            "setup_wns": res.get("physical_baseline") if paired else self.baseline_wns,
            "setup_tns": res.get("physical_baseline_tns") if paired else self.baseline_tns,
            "hold_min_slack": (res.get("physical_baseline_min_slack")
                               if paired else self.baseline_min_slack),
        }
        unavailable_metrics = [metric for metric in self.required_metrics
                               if metric_values.get(metric) is None]
        unavailable = tuple(unavailable_metrics)
        violations: list[str] = []
        if (self.strict_budgets and metric_references["setup_tns"] is not None
                and metric_values["setup_tns"] is not None
                and metric_values["setup_tns"] < metric_references["setup_tns"] - self.epsilon):
            violations.append("setup_tns")
```

Lines 2335-2343:
```python
            evidence_payload = evidence.to_dict()
            evidence_payload["metric_budgets"] = metric_budgets
            failure_events.append({
                "type": "acceptance_budget_unavailable" if evidence.unavailable else "acceptance_budget_violation",
                "candidate_hash": candidate_hash, "cut_hash": candidate_hash,
                "severity": "hard", "hard_gate": True, "runtime_s": time.perf_counter() - started_at,
                "threshold": {"unavailable": list(evidence.unavailable), "violations": list(evidence.violations)},
                "observed_value": evidence_payload, "evidence": evidence_payload,
            })
```

Lines 2670-2677:
```python
        def _accept_result(r: dict) -> bool:
            nonlocal best_wns, best_tns, best_min, best_physical_wns, best_physical_hold, best
            wns = r["wns"]
            if any(e.get("severity") == "hard" or e.get("type") in {
                "F1_equivalence_failure", "F2_boundary_invalid",
                "F3_patch_too_large", "F5_verification_too_expensive",
            } for e in r.get("failure_events", [])):
                return False
```

Lines 2747-2753:
```python
            if wns > best_wns + self.epsilon or (
                self.tns_aware
                and abs(wns - best_wns) <= self.epsilon
                and tns is not None
                and best_tns is not None
                and tns > best_tns + self.epsilon
            ):
```

### `code/scripts/run_outerloop_real_wns.py`

Lines 392-395:
```python
        strict_gates=True,
        strict_budgets=True,
        required_metrics=tuple(m.strip() for m in args.required_metrics.split(",") if m.strip()),
        epsilon=args.epsilon,
```

## Actual W1 settings

All eight W1 run_config files were read. required_metrics=setup_wns,setup_tns; epsilon=0; tns_aware=false; hold_mode=false; physical_gate=false; no_feedback=true; weighted_st/full/configured; period=0.5 ns; CK; workers=1; 20 iterations,20 patch cap,500 new-STA cap. Full per-file SHA/settings are in JSON. Strict flags are absent in these configs and proven true only by the exact caller above.

## Observed counterexample that isolates the gate

`experiments/20261016_r22_cut_ablation_v3/W0/s27/eval_trials.json`, SHA256 `09cf97e0c6fa28a381e5e2ca139375a966aa5444108d4ba2da8de37a6200926e`, `/trials/0`: G `_11_`, a21boi_0 to a21boi_1. WNS improves -0.27 to -0.26 ns while TNS degrades -0.49 to -0.50 ns. Only failure violation is setup_tns, severity hard; accepted=false,committed=false,sta_executed=true,sta_launch_seq=1. Hold slack also falls0.44 to0.43 ns but is not a hard violation in this configuration.

Baseline decoded netlist SHA `3010c393dc085a30b359dbe09b5e15eefd9c814056a9fa4b0f09d44974ca1495`; candidate decoded SHA `92085689c92eed9168da24e1c3a2416d025631d6e042cdc6713ae369164b6a14`. Both match their native mapped.v under the runtime text normalization. Native baseline sta.log lines322/324 report TNS -0.49/WNS -0.27; candidate sta.log lines293/295 report TNS -0.50/WNS -0.26. Raw mapped.v/log/Tcl byte hashes and exact failure event are in JSON. This is W0 evidence under the same hard-budget runtime, not an invented W1 measurement. The checked W1/s27 violation also worsens WNS and is not used to isolate this effect.

## Minimal manuscript statement

For the controlled Cprime matrix: a candidate can be committed only after the hard gates pass, WNS strictly improves, and setup TNS does not degrade relative to the current accepted baseline. Optional TNS-aware ties are disabled here. Do not infer hold, power, or electrical acceptance from this setup-only rule. Detailed flags and this rejected-trial witness can be placed in the supplement.
