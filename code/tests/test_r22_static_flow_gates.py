"""Controlled flow probes use the real cut/state loop and no EDA tools."""
from pathlib import Path

from rseco.flow import run_multi_iteration_case

TEXT = '''module top(A,Y);
input A;
output Y;
wire n;
buf g1(n,A);
buf g2(Y,n);
endmodule
'''


def case(tmp_path):
    for folder in ('original','resynthesized'):
        (tmp_path/folder).mkdir(parents=True)
        (tmp_path/folder/(folder+'.v')).write_text(TEXT)
    (tmp_path/'case.yaml').write_text('case_id: probe\ntarget:\n  output: Y\n')
    return tmp_path


class ProbeEvaluator:
    baseline_wns = -1.0
    baseline_tns = -2.0
    mapped_text = TEXT
    cut_search_policy = 'weighted_st'
    cut_sources = 'full'
    node_cost_mode = 'configured'
    use_constrained_cuts = True
    refresh_cone = False
    strict_gates = False

    def __init__(self, critical):
        self.critical_instances = critical
        self.r_scopes = []
        self.trials = []
        self.sta_launch_events = []
        self.windows = []

    def r_available_for(self, instances):
        self.r_scopes.append(list(instances))
        return set(instances)

    def __call__(self, patch, weights, *, state=None):
        self.windows.append(list(patch.gates))
        return {'wns':-1.0,'tns':-2.0,'improved':False,'failure_events':[]}


def test_r_available_domain_includes_noncritical_cone_gates(tmp_path):
    evaluator = ProbeEvaluator(['g2'])
    result = run_multi_iteration_case(case(tmp_path), max_iterations=1,
        enable_feedback=False, wns_evaluator=evaluator)
    assert set(evaluator.r_scopes[0]) == {'g1','g2'}
    assert result['candidate_pool_trace'][0]['r_available'] == ['g1','g2']


def test_legacy_r_available_domain_is_unchanged(tmp_path):
    evaluator = ProbeEvaluator(['g2'])
    evaluator.cut_search_policy = 'legacy'
    run_multi_iteration_case(case(tmp_path),max_iterations=1,enable_feedback=False,
        wns_evaluator=evaluator)
    assert evaluator.r_scopes[0] == ['g2']


def test_random_order_keeps_exact_same_current_epoch_pool(tmp_path):
    traces = []
    for seed in (None,1,2,3):
        evaluator = ProbeEvaluator(['g1','g2'])
        result = run_multi_iteration_case(case(tmp_path/str(seed)),max_iterations=1,
            enable_feedback=False,wns_evaluator=evaluator,
            random_order=seed is not None,seed=seed or 0)
        traces.append(result['candidate_pool_trace'][0])
    assert len(traces[0]['pool_hashes'])==2
    for trace in traces[1:]:
        assert trace['pool_hashes']==traces[0]['pool_hashes']
        assert sorted(trace['dispatch_hashes'])==sorted(traces[0]['dispatch_hashes'])
        assert trace['base_netlist_hash']==traces[0]['base_netlist_hash']
