"""Explicit, auditable candidate sources for the r22 controlled experiment.

The weighted source is one genuine node-split s-t solution, not the legacy
bounded region search. Cover-first is a scheduling policy, not a fusion score.
"""
from types import SimpleNamespace

from .cut import (build_weighted_cut_graph, solve_weighted_cut,
                  _cut_for_selected_gates, _critical_path_cover_cut,
                  canonical_cut_hash)

WEIGHT_NAMES = ('boundary_penalty', 'size_penalty', 'critical_coverage_reward',
                'verification_cost_penalty', 'equivalence_stability_reward')


def validate_policy(policy='legacy', sources='full', cost_mode='configured'):
    if policy not in ('legacy', 'weighted_st'):
        raise ValueError(f'Unknown cut search policy: {policy}')
    if sources not in ('full', 'weighted', 'cover'):
        raise ValueError(f'Unknown cut sources: {sources}')
    if cost_mode not in ('configured', 'uniform'):
        raise ValueError(f'Unknown node cost mode: {cost_mode}')
    if policy == 'legacy' and (sources != 'full' or cost_mode != 'configured'):
        raise ValueError('Source/cost controls require weighted_st policy')


def generate_candidate_boundaries(cone, weights, critical_instances, r_available,
                                  *, sources='full', cost_mode='configured'):
    validate_policy('weighted_st', sources, cost_mode)
    configured = {name: float(getattr(weights, name, 1.0)) for name in WEIGHT_NAMES}
    effective = {name: 0.0 for name in WEIGHT_NAMES} if cost_mode == 'uniform' else configured
    trace = {'policy': 'weighted_st', 'sources': sources, 'cost_mode': cost_mode,
             'configured_weights': configured, 'effective_weights': effective,
             'node_costs': {}, 'candidates': []}
    if not cone.gates:
        return [], trace
    pool = []
    if sources in ('full', 'cover'):
        # R availability discounts the weighted graph only. Removing non-R
        # gates from cover would also remove legal G/B/JOINT opportunities.
        cover = _critical_path_cover_cut(cone, critical_instances or [], r_available=None)
        if cover is not None and cover.gates:
            pool.append((cover, 'cover'))
    if sources in ('full', 'weighted'):
        graph = build_weighted_cut_graph(cone, SimpleNamespace(**effective), r_available)
        trace['node_costs'] = dict(graph.node_costs)
        solved = solve_weighted_cut(cone, graph)
        trace['weighted_cut_cost'] = solved.cut_cost
        if solved.selected_gates:
            pool.append((_cut_for_selected_gates(cone, solved.selected_gates,
                                               method='weighted_st'), 'weighted'))
    rows, by_hash = [], {}
    for boundary, origin in pool:
        key = canonical_cut_hash(boundary)
        if key in by_hash:
            by_hash[key]['origins'].append(origin)
            continue
        record = {'cut_hash': key, 'origins': [origin], **boundary.to_dict()}
        record['node_cost_sum'] = (sum(trace['node_costs'][g] for g in boundary.gates)
                                   if trace['node_costs'] else None)
        by_hash[key] = record
        trace['candidates'].append(record)
        rows.append(boundary)
    return rows, trace
