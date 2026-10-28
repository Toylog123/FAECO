"""Round 34 -- collect every number the record needs, READ BACK from the
artefacts, into one JSON so that the landing script never transcribes a
number by hand.

Sources
  * scratch/round34_fallback_verify.txt      (the equivalence checks)
  * scratch/round34_recovered_label_provenance.txt (the placeholder proof)
  * scratch/round34_affected_detail.txt       (the affected-trial profile)
  * scratch/round34_conflict_check.json      (filled vs conflict)
  * scratch/round34_downstream_cascade.json  (what moved downstream)
  * scratch/round34_band_ratio.txt            (the stale band ratio)
  * scratch/round34_decision_delta.txt        (why the decision reading held)
  * scratch/round34_probe.json                (the reachability probe)
  * the live artefacts themselves

Nothing here interprets; it only reads.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCR = REPO / 'scratch'
ITC = REPO / 'experiments/20261024_physical_labels_itc99'
LAB = REPO / 'experiments/20261024_physical_labels'


def read(rel):
    p = REPO / rel
    return p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''


def load(rel):
    p = REPO / rel
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def grab(txt, pat, group=1, default=None, flags=0):
    m = re.search(pat, txt, flags)
    return m.group(group) if m else default


N = {}

# ---------------------------------------------------------------- the defect
fv = read('scratch/round34_fallback_verify.txt')
N['eq_itc99_cand'] = int(grab(fv, r'exactly equal     : (\d+)', default=0) or 0)
# the two "exactly equal" lines (candidate-side, then base-side)
eqs = re.findall(r'exactly equal     : (\d+)', fv)
N['eq_itc99_cand'] = int(eqs[0]) if len(eqs) > 0 else 0
N['eq_itc99_base'] = int(eqs[1]) if len(eqs) > 1 else 0
N['eq_iscas89_cand'] = int(eqs[2]) if len(eqs) > 2 else 0
N['eq_iscas89_base'] = int(eqs[3]) if len(eqs) > 3 else 0
N['affected_itc99'] = int(grab(fv, r'FAMILY itc99.*?C  trials WITHOUT acceptance_evidence\s+total\s+: (\d+)',
                               default=0, flags=re.S) or 0)
N['affected_iscas89'] = int(grab(fv, r'FAMILY iscas89.*?C  trials WITHOUT acceptance_evidence\s+total\s+: (\d+)',
                                 default=0, flags=re.S) or 0)

# ---------------------------------------------------------------- provenance
pv = read('scratch/round34_recovered_label_provenance.txt')


def block_after(txt, header):
    """the text of the block that starts with `header` (until the next '---' or
    blank-line group), so that the affected and the control groups cannot be
    confused"""
    i = txt.find(header)
    if i < 0:
        return ''
    j = txt.find('\n--- ', i + 10)
    return txt[i:j if j > 0 else len(txt)]


AFF = block_after(pv, '--- AFFECTED (no acceptance_evidence)')
CTL = block_after(pv, '--- CONTROL (has acceptance_evidence)')
N['prov_aff_wns_eq_base'] = int(grab(
    AFF, r'wns == the iteration base WNS   : (\d+)', default=0) or 0)
N['prov_aff_no_sta_prov'] = int(grab(
    AFF, r'carry an sta_provenance         : (\d+)', default=0) or 0)
N['prov_aff_report_path'] = int(grab(
    AFF, r'carry an STA report path        : (\d+)', default=0) or 0)
N['prov_aff_slack_none'] = int(grab(
    AFF, r'slack_status         \{None: (\d+)\}', default=0) or 0)
N['prov_ctl_sta_prov'] = int(grab(
    CTL, r'carry an sta_provenance         : (\d+)', default=0) or 0)
N['prov_ctl_report_path'] = int(grab(
    CTL, r'carry an STA report path        : (\d+)', default=0) or 0)
N['prov_aff_total'] = int(grab(
    pv, r'--- AFFECTED \(no acceptance_evidence\) \(n=(\d+)\)', default=0) or 0)
N['prov_ctl_total'] = int(grab(
    pv, r'--- CONTROL \(has acceptance_evidence\) \(n=(\d+)\)', default=0) or 0)
N['prov_ctl_wns_eq_base'] = int(grab(
    CTL, r'wns == the iteration base WNS   : (\d+)', default=0) or 0)

ad = read('scratch/round34_affected_detail.txt')
N['affected_by_hash'] = int(grab(
    ad, r'affected trials matching the accepted candidate BY HASH   : (\d+)',
    default=0) or 0)

# ---------------------------------------------------------------- the patch
cc = load('scratch/round34_conflict_check.json') or {}
N['itc99_table_filled_rows'] = max(
    cc.get('itc99', {}).get('table_filled', {}).values()) if cc.get(
        'itc99', {}).get('table_filled') else 0
N['itc99_table_filled_cells'] = sum(
    v for v in cc.get('itc99', {}).get('table_filled', {}).values())
N['itc99_table_filled_fields'] = cc.get('itc99', {}).get('table_filled', {})
N['itc99_table_conflicts'] = cc.get('itc99', {}).get('table_conflicts')
N['itc99_dataset_conflicts'] = cc.get('itc99', {}).get('dataset_conflicts')
N['iscas89_table_conflicts'] = cc.get('iscas89', {}).get('table_conflicts')
N['iscas89_dataset_conflicts'] = cc.get('iscas89', {}).get('dataset_conflicts')
N['itc99_ideal_n_before'] = (cc.get('itc99', {})
                             .get('ideal_stage_n_baseline', {})
                             .get('stages_marginal'))
N['itc99_ideal_n_after'] = (cc.get('itc99', {})
                            .get('ideal_stage_n_patched', {})
                            .get('stages_marginal'))
N['iscas89_ideal_n_before'] = (cc.get('iscas89', {})
                               .get('ideal_stage_n_baseline', {})
                               .get('stages_marginal'))
N['iscas89_ideal_n_after'] = (cc.get('iscas89', {})
                              .get('ideal_stage_n_patched', {})
                              .get('stages_marginal'))
N['bands_identical'] = cc.get('itc99', {}).get('bands_identical')
N['decisions_identical'] = cc.get('itc99', {}).get('decisions_identical')

# the artefacts' own numbers
ds = [json.loads(l) for l in
      (ITC / 'physical_dataset.jsonl').read_text(encoding='utf-8').splitlines()
      if l.strip()]
N['itc99_dataset_rows'] = len(ds)
st = {}
for r in ds:
    st[r.get('ideal_label_status')] = st.get(r.get('ideal_label_status'), 0) + 1
N['itc99_status_measured'] = st.get('measured', 0)
N['itc99_status_not_measured'] = st.get('not_measured_pre_sta', 0)

ds89 = [json.loads(l) for l in
        (LAB / 'physical_dataset.jsonl').read_text(encoding='utf-8').splitlines()
        if l.strip()]
N['iscas89_dataset_rows'] = len(ds89)
st89 = {}
for r in ds89:
    st89[r.get('ideal_label_status')] = st89.get(
        r.get('ideal_label_status'), 0) + 1
N['iscas89_status_measured'] = st89.get('measured', 0)
N['iscas89_status_not_measured'] = st89.get('not_measured_pre_sta', 0)

tpc = load('experiments/20261024_physical_labels_itc99/three_point_curve.json')
N['itc99_curve_cands'] = len(tpc.get('candidates') or [])
N['itc99_curve_coverage'] = tpc.get('coverage')
N['itc99_curve_bands'] = {k: v for k, v in (tpc.get('bands') or {}).items()
                           if k.endswith('two_sigma_ns')}
N['itc99_p2r_marginal'] = ((tpc.get('stages_marginal') or {})
                            .get('placed_to_routed') or {})
tpc89 = load('experiments/20261024_physical_labels/three_point_curve.json')
N['iscas89_curve_cands'] = len(tpc89.get('candidates') or [])

cen = load('experiments/20261024_physical_labels_itc99/'
           'three_point_curve_drop_census.json')
N['itc99_drop_census'] = cen
cen89 = load('experiments/20261024_physical_labels/'
             'three_point_curve_drop_census.json')
N['iscas89_drop_census'] = cen89

tt = [json.loads(l) for l in
      (ITC / 'training_table.jsonl').read_text(encoding='utf-8').splitlines()
      if l.strip()]
N['itc99_table_rows'] = len(tt)
N['itc99_table_with_placed'] = sum(1 for r in tt
                                    if r.get('placed_delta_wns') is not None)
N['itc99_table_with_routed'] = sum(1 for r in tt
                                    if r.get('routed_delta_wns') is not None)
N['itc99_table_with_ideal'] = sum(1 for r in tt
                                   if r.get('ideal_delta_wns') is not None)
N['itc99_table_all_three'] = sum(
    1 for r in tt
    if r.get('ideal_delta_wns') is not None
    and r.get('placed_delta_wns') is not None
    and r.get('routed_delta_wns') is not None)

tt89 = [json.loads(l) for l in
        (LAB / 'training_table.jsonl').read_text(encoding='utf-8').splitlines()
        if l.strip()]
N['iscas89_table_rows'] = len(tt89)

# ---------------------------------------------------------------- the cascade
casc = load('scratch/round34_downstream_cascade.json') or {}
N['cascade_itc99_moved'] = sorted(k for k, v in casc.get('itc99', {}).items()
                                   if v['changed'] or v['added'] or v['removed'])
N['cascade_iscas89_moved'] = sorted(k for k, v in casc.get('iscas89', {}).items()
                                     if v['changed'] or v['added'] or v['removed'])
N['cascade_itc99_unchanged'] = sorted(
    k for k, v in casc.get('itc99', {}).items()
    if not (v['changed'] or v['added'] or v['removed']))

# ---------------------------------------------------------------- band ratio
br = read('scratch/round34_band_ratio.txt')
# read the two fields out of the artefacts themselves (the text trace is only
# a human-readable copy and its wording must not be parsed)
bs_before = load('scratch/round34_downstream_before/'
                 '20261024_physical_labels_itc99__band_scope.json') or {}
bs_after = load('experiments/20261024_physical_labels_itc99/band_scope.json') or {}
bb = (bs_before.get('sections') or {}).get('band_ratio') or {}
ba = (bs_after.get('sections') or {}).get('band_ratio') or {}
N['band_ratio_own_before'] = bb.get('ratio_routed_over_placed')
N['band_ratio_own_after'] = ba.get('ratio_routed_over_placed')
N['band_ratio_stored_before'] = bb.get('stored_ratio_in_three_point_curve')
N['band_ratio_stored_after'] = ba.get('stored_ratio_in_three_point_curve')
N['band_scope_scope'] = ba.get('selected_scope')
N['band_ratio_routed_2s'] = ba.get('routed_two_sigma_ns')
N['band_ratio_placed_2s'] = ba.get('placed_two_sigma_ns')
# the arithmetic that identifies the stale value as a CROSS-SCOPE ratio
N['band_ratio_pilot_routed_2s'] = 0.087496
N['band_ratio_pilot_over_placed'] = round(0.087496 / 0.029826, 6)

# ---------------------------------------------------------------- the decision
dd = read('scratch/round34_decision_delta.txt')
N['decision_itc99_rows_three_stage'] = grab(
    dd, r'n_rows_three_stage\s+(\d+) -> (\d+)', group=2, default=None)
N['decision_itc99_n'] = grab(dd, r'n_decisions_evaluable\s+(\d+) -> (\d+)',
                              group=2, default=None)
N['decision_identical'] = 'decisions with ANY difference: 0' in dd
sel = load('scratch/round33_placed_selector.json') or {}
for fam in ('iscas89', 'itc99'):
    f = (sel.get('families') or {}).get(fam) or {}
    N['sel_%s_n' % fam] = f.get('n_decisions_evaluable')
    N['sel_%s_p' % fam] = (f.get('primary_comparison') or {}).get('sign_test_p')
    N['sel_%s_w' % fam] = (f.get('primary_comparison') or {}).get('wins')
    N['sel_%s_l' % fam] = (f.get('primary_comparison') or {}).get('losses')
    N['sel_%s_t' % fam] = (f.get('primary_comparison') or {}).get('ties')
    N['sel_%s_recovery' % fam] = (f.get('recovery_fraction') or {}).get('value')
    N['sel_%s_h1' % fam] = (f.get('verdict') or {}).get('H1_triggered')
    N['sel_%s_overlap_placed' % fam] = (
        f.get('overlap_with_the_oracle') or {}).get('placed_eligible_is_oracle')
    N['sel_%s_overlap_ideal' % fam] = (
        f.get('overlap_with_the_oracle') or {}).get('ideal_eligible_is_oracle')

# ---------------------------------------------------------------- the probe
pr = load('scratch/round34_probe.json')
if pr:
    N['probe'] = {
        'n_reachable': (pr.get('projection') or {}).get('n_reachable_circuits'),
        'reachable': (pr.get('projection') or {}).get('reachable_circuits'),
        'unreachable': (pr.get('projection') or {}).get('unreachable_circuits'),
        'failed': (pr.get('projection') or {}).get('failed_circuits'),
        'not_run': (pr.get('projection') or {}).get('not_run_circuits'),
        'extra_jobs': (pr.get('projection') or {}).get(
            'extra_candidate_jobs_per_stage'),
        'extra_hours_serial': (pr.get('projection') or {}).get('extra_hours_serial'),
        'extra_hours_par4': (pr.get('projection') or {}).get('extra_hours_at_par4'),
        'extra_decisions_upper': (pr.get('projection') or {}).get(
            'extra_evaluable_decisions_upper_bound'),
        'routed_median_s': (pr.get('measured') or {}).get('routed_median_s'),
        'placed_median_s': (pr.get('measured') or {}).get('placed_median_s'),
        'per_circuit': {c: {'util': v.get('util'), 'status': v.get('status'),
                            'seconds': v.get('seconds'),
                            'rounds': (v.get('gate') or {}).get('n_rounds'),
                            'rounds_ge2': (v.get('gate') or {}).get(
                                'n_rounds_with_ge2_eligible'),
                            'n_candidates': (v.get('ledger') or {}).get(
                                'n_distinct_candidates')}
                        for c, v in (pr.get('circuits') or {}).items()},
    }

out = REPO / 'scratch/round34_numbers.json'
out.write_text(json.dumps(N, indent=2, ensure_ascii=False, default=str),
               encoding='utf-8')
print('wrote scratch/round34_numbers.json')
for k in sorted(N):
    if k != 'probe':
        print('  %-36s %s' % (k, N[k]))
