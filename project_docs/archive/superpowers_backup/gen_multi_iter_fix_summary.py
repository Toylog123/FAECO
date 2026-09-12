"""One-shot summary writer for the multi-iter fix experiment."""
import json
from pathlib import Path

base = Path('D:/BaiduSyncdisk/03_FAECO/experiments/20260908_multi_iter_fix_full')
out = {'multi_iter_fix': {}}
r = json.load(open(base / 'b17/b17/outerloop_result.json', encoding='utf-8'))
t = json.load(open(base / 'b17/b17/eval_trials.json', encoding='utf-8'))['trials']
out['multi_iter_fix']['b17'] = {
    'config': {
        'max_iterations': 6,
        'candidates_per_iteration': 4,
        'strategies': ['R', 'G'],
        'no_early_stop': True,
    },
    'baseline_wns': r['baseline_wns'],
    'final_wns': r['history'][-1].get('wns'),
    'iterations_run': r['iterations'],
    'success': r['success'],
    'n_candidate_sta_runs': r['n_candidate_sta_runs'],
    'all_wns_history': r.get('wns_history'),
    'unique_best_wns': max((tt['wns'] or -999) for tt in t),
    'trials_count': len(t),
    'accepted_patch': r['final_patch_id'],
    'conclusion': (
        'Even with the --no-early-stop fix in src/rseco/flow.py (now '
        'honouring wns_evaluator.early_stop at the outer-loop accept '
        'step), b17 still finds no WNS improvement across 6 iters x 4 '
        'candidates = 24 STA runs. The actionable gate list in every '
        'iter starts at _184747_ and never reaches _184320_, because the '
        'cut is built from the critical-path cover and gates without an R '
        'equivalence candidate are skipped. Multi-iter does NOT '
        'compensate for that constraint. joint_enumerate_depth=4 was '
        'needed to break through (separate experiment).'
    ),
}
(base / 'multi_iter_fix_summary.json').write_text(
    json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
)
print(json.dumps(out, indent=2, ensure_ascii=False))
