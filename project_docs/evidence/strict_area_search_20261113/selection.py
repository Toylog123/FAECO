"""Pure frozen ordering and actual-only strict selection; owns no runtime state."""
import copy
import math
from decimal import Decimal

METRICS=('setup_ns','tns_ns','hold_ns')
NORMS=dict(zip(METRICS,(.010,.312647,.001)))
TOL=1e-6
CHECKS=('complete','structure','provenance','drc','drv')
ROLES=('netlist','spef','odb','def','manifest')


def number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError('Missing/nonfinite numeric value')
    return value


def judge_actual(point,control):
    """Return numeric feasibility; never infer actual evidence from predictions."""
    reasons=[]
    try:
        if point.get('evidence_kind')!='actual':reasons.append('not_actual')
        if any(point.get('checks',{}).get(k) is not True for k in CHECKS):reasons.append('incomplete_evidence')
        for role in ROLES:
            ref=point.get('endpoint',{}).get(role,{})
            if not ref.get('path') or len(ref.get('sha256',''))!=64 or any(c not in '0123456789abcdef' for c in ref.get('sha256','')):
                reasons.append('missing_endpoint_'+role)
        area=number(point.get('area'));reference=number(control.get('area'))
        saving=Decimal(str(reference))-Decimal(str(area))
        if area<=0 or saving<=0:reasons.append('nonpositive_area_saving')
        for metric in METRICS:
            value=number(point.get('metrics',{}).get(metric));baseline=number(control.get('metrics',{}).get(metric))
            if value<baseline-TOL:reasons.append(metric)
        if point['metrics']['hold_ns']<0:reasons.append('absolute_hold')
    except (ValueError,KeyError,TypeError):
        reasons.append('missing_or_nonfinite_metric');saving=Decimal(0)
    return {'feasible':not reasons,'reasons':reasons,'area_saved':float(saving)}


def freeze_orders(candidates,control,seed,observations):
    """Freeze proposal-only predictions from single-action observations."""
    frozen=[];seen=set()
    for candidate in candidates:
        ident=candidate['candidate_id']
        if ident in seen:raise ValueError('Duplicate candidate')
        seen.add(ident);saving=number(candidate['area_saved'])
        prediction={k:number(seed['metrics'][k])+number(observations[candidate['extra_action']][k])-number(control['metrics'][k]) for k in METRICS}
        deficits={k:max(0.0,control['metrics'][k]-prediction[k]-TOL)/NORMS[k] for k in METRICS}
        frozen.append(dict(copy.deepcopy(candidate),prediction=prediction,normalized_deficits=deficits,
                           timing_risk=[max(deficits.values()),sum(deficits.values())],evidence_kind='prediction'))
    order_area=sorted(frozen,key=lambda c:(-Decimal(str(c['area_saved'])),c['candidate_id']))
    order_risk=sorted(frozen,key=lambda c:(*c['timing_risk'],-Decimal(str(c['area_saved'])),c['candidate_id']))
    return {'candidates':frozen,'orders':{'area_first':[c['candidate_id'] for c in order_area],
                                        'timing_risk':[c['candidate_id'] for c in order_risk]}}


def replay(orders,points,control,seed):
    """Replay shared measurements; every prefix charges each visited candidate."""
    seed_gate=judge_actual(seed,control)
    if not seed_gate['feasible'] or seed.get('sec_status')!='pass':raise ValueError('Seed must be accepted and SEC-proven')
    if not orders:raise ValueError('No orders')
    expected=set(points)
    result={}
    for strategy,order in orders.items():
        if len(order)!=len(set(order)) or set(order)!=expected:raise ValueError('Ordering/pool mismatch')
        best=copy.deepcopy(seed);best_saving=seed_gate['area_saved'];trace=[]
        for k,ident in enumerate(order,1):
            point=points[ident]
            if point.get('candidate_id')!=ident:raise ValueError('Candidate identity mismatch')
            gate=judge_actual(point,control)
            if gate['feasible'] and (gate['area_saved']>best_saving or (gate['area_saved']==best_saving and ident<best['candidate_id'])):
                best=copy.deepcopy(point);best_saving=gate['area_saved']
            trace.append({'charged_verifications':k,'visited':ident,'gate':gate,
                          'best_area_saved':best_saving,'selected':copy.deepcopy(best)})
        assert all(a['best_area_saved']<=b['best_area_saved'] for a,b in zip(trace,trace[1:]))
        result[strategy]=trace
    finals=[trace[-1]['selected'] for trace in result.values() if trace]
    if finals and any(p!=finals[0] for p in finals):raise AssertionError('Complete-pool optimum differs by ordering')
    return result
