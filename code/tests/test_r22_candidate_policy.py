from types import SimpleNamespace

import pytest

from rseco.cut import FaninCone, canonical_cut_hash
from rseco.candidate_policy import generate_candidate_boundaries


def cone():
    return FaninCone(roots=['Y'], boundary_inputs=['A'], boundary_outputs=['Y'],
        internal_nets=['N'], gates=['g1','g2'], gate_outputs={'g1':'N','g2':'Y'},
        gate_inputs={'g1':['A'],'g2':['N']})


def weights():
    return SimpleNamespace(boundary_penalty=1, size_penalty=1,
        critical_coverage_reward=1, verification_cost_penalty=1,
        equivalence_stability_reward=1, max_cone_gates=1000)


def test_weighted_only_does_not_leak_cover_or_legacy_baselines():
    rows, trace = generate_candidate_boundaries(cone(), weights(), ['g1','g2'],
        {'g2'}, sources='weighted', cost_mode='configured')
    assert len(rows) == 1
    assert rows[0].method == 'weighted_st'
    assert trace['candidates'][0]['origins'] == ['weighted']


def test_cover_only_keeps_non_r_gates_for_rgb_actions():
    rows, trace = generate_candidate_boundaries(cone(), weights(), ['g1','g2'],
        {'g2'}, sources='cover', cost_mode='configured')
    assert rows[0].gates == ['g1','g2']
    assert trace['node_costs'] == {}


def test_uniform_cost_is_one_and_does_not_mutate_input_weights():
    w = weights()
    rows, trace = generate_candidate_boundaries(cone(), w, ['g1','g2'], set(),
        sources='weighted', cost_mode='uniform')
    assert set(trace['node_costs'].values()) == {1.0}
    assert w.boundary_penalty == 1


def test_full_is_cover_first_and_records_both_sources():
    rows, trace = generate_candidate_boundaries(cone(), weights(), ['g1','g2'], None,
        sources='full', cost_mode='configured')
    assert rows[0].method == 'critical_path_cover'
    assert len(rows) == 2
    assert [r['cut_hash'] for r in trace['candidates']] == [canonical_cut_hash(r) for r in rows]


def test_overlap_is_evaluated_once_with_both_origins():
    rows, trace = generate_candidate_boundaries(cone(), weights(), ['g2'], None,
        sources='full', cost_mode='configured')
    assert len(rows) == 1
    assert trace['candidates'][0]['origins'] == ['cover','weighted']


@pytest.mark.parametrize('sources,cost', [('all','configured'),('weighted','bogus')])
def test_unknown_controls_fail_closed(sources, cost):
    with pytest.raises(ValueError):
        generate_candidate_boundaries(cone(), weights(), [], None, sources=sources, cost_mode=cost)


def test_flow_explicit_path_bypasses_legacy_constrained_enumerator():
    from rseco.flow import _cone_candidates
    rows = _cone_candidates(cone(), weights(), ['g1','g2'], None,
        constrained=True, cut_search_policy='weighted_st', cut_sources='weighted')
    assert len(rows) == 1 and rows[0].method == 'weighted_st'


def test_cost_can_change_cut_identity_and_preserves_degenerate_case():
    w = weights()
    w.size_penalty = 30
    a, _ = generate_candidate_boundaries(cone(), w, [], None, sources='weighted')
    b, _ = generate_candidate_boundaries(cone(), w, [], None,
        sources='weighted', cost_mode='uniform')
    c, _ = generate_candidate_boundaries(cone(), weights(), [], None, sources='weighted')
    assert a[0].gates != c[0].gates
    assert b[0].gates == ['g1']  # unit-capacity tie resolves deterministically
    assert c[0].gates == ['g2']  # endpoint degeneration remains visible


@pytest.mark.parametrize('reward', [0, 1, 20])
def test_cover_switch_is_independent_of_critical_discount(reward):
    w = weights()
    w.critical_coverage_reward = reward
    rows, _ = generate_candidate_boundaries(cone(), w, ['g1','g2'], None, sources='cover')
    assert rows[0].gates == ['g1','g2']
