"""Behavior tests for pure fixed-reference strict area selection; no EDA."""
import copy
import math
import pytest
from selection import judge_actual, freeze_orders, replay

CONTROL={'area':100.0,'metrics':{'setup_ns':-1.0,'tns_ns':-10.0,'hold_ns':.2}}

def actual(name='seed',area=99.0,**metrics):
    return {'candidate_id':name,'evidence_kind':'actual','area':area,
            'metrics':dict(CONTROL['metrics'],**metrics),
            'checks':dict.fromkeys(['complete','structure','provenance','drc','drv'],True),
            'endpoint':{role:{'path':'local/'+name+'/'+role,'sha256':'a'*64} for role in ['netlist','spef','odb','def','manifest']},
            'sec_status':'pass' if name=='seed' else 'pending'}

@pytest.mark.parametrize('metric',['setup_ns','tns_ns','hold_ns'])
@pytest.mark.parametrize('value',[None,float('nan'),float('inf'),-float('inf')])
def test_missing_nonfinite_actual_rejected(metric,value):
    p=actual(**{metric:value});assert not judge_actual(p,CONTROL)['feasible']

@pytest.mark.parametrize('metric',['setup_ns','tns_ns','hold_ns'])
def test_each_timing_constraint_is_required(metric):
    p=actual(area=90,**{metric:CONTROL['metrics'][metric]-.001});assert not judge_actual(p,CONTROL)['feasible']

def test_wns_gain_cannot_hide_tns_loss():
    assert not judge_actual(actual(setup_ns=-.9,tns_ns=-10.1),CONTROL)['feasible']

def test_prediction_cannot_masquerade_as_measurement():
    p=actual(area=80);p['evidence_kind']='prediction';assert not judge_actual(p,CONTROL)['feasible']

@pytest.mark.parametrize('check',['complete','structure','provenance','drc','drv'])
def test_each_evidence_gate_required(check):
    p=actual();p['checks'][check]=False;assert not judge_actual(p,CONTROL)['feasible']

@pytest.mark.parametrize('area',[None,float('nan'),float('inf'),100,101])
def test_area_must_be_finite_positive_saving(area):
    assert not judge_actual(actual(area=area),CONTROL)['feasible']

def test_hold_absolute_gate_even_if_reference_negative():
    c=copy.deepcopy(CONTROL);c['metrics']['hold_ns']=-.2
    assert not judge_actual(actual(hold_ns=-.1),c)['feasible']

def test_zero_is_valid_and_fixed_control_not_seed_reference():
    p=actual(setup_ns=0,tns_ns=0,hold_ns=0)
    c=copy.deepcopy(CONTROL);c['metrics']['hold_ns']=0
    assert judge_actual(p,c)['feasible']
    assert judge_actual(actual(setup_ns=-1.0),CONTROL)['feasible']

def test_exact_tie_lexical_and_immutable_fallback():
    seed=actual();saved=copy.deepcopy(seed)
    points={'a':actual('a',98),'b':actual('b',98),'z':actual('z',99,tns_ns=-11)}
    out=replay({'area_first':['b','a','z'],'timing_risk':['z','a','b']},points,CONTROL,seed)
    assert out['area_first'][-1]['selected']['candidate_id']=='a'
    assert out['timing_risk'][0]['selected']==seed
    assert seed==saved
    assert out['timing_risk'][0]['selected']['endpoint']==seed['endpoint']

def test_complete9_prefix_monotonic_and_equal_final():
    seed=actual();points={str(i):actual(str(i),99-i/10,tns_ns=-11 if i%3==0 else -10) for i in range(9)}
    out=replay({'area_first':list(points),'timing_risk':list(reversed(points))},points,CONTROL,seed)
    for trace in out.values():
        values=[row['best_area_saved'] for row in trace];assert values==sorted(values)
        assert len(trace)==9 and trace[-1]['charged_verifications']==9
    assert out['area_first'][-1]['selected']==out['timing_risk'][-1]['selected']

def test_all_failure_returns_exact_seed():
    seed=actual();p={str(i):actual(str(i),90,hold_ns=.1) for i in range(9)}
    out=replay({'area_first':list(p),'timing_risk':list(reversed(p))},p,CONTROL,seed)
    assert all(row['selected']==seed for trace in out.values() for row in trace)

def test_unproven_seed_and_incomplete_pool_rejected():
    seed=actual();seed['sec_status']='pending'
    with pytest.raises(ValueError):replay({'a':['x']},{'x':actual('x')},CONTROL,seed)
    with pytest.raises(ValueError):replay({'a':['x']},{},CONTROL,actual())

def test_orders_are_fixed_by_prior_only_and_use_same_candidates():
    candidates=[{'candidate_id':'a','extra_action':'A','area_saved':3.0},{'candidate_id':'b','extra_action':'B','area_saved':2.0}]
    observations={'A':{'setup_ns':-1.1,'tns_ns':-10,'hold_ns':.2},'B':dict(CONTROL['metrics'])}
    original=copy.deepcopy((candidates,observations))
    frozen=freeze_orders(candidates,CONTROL,actual(),observations)
    assert frozen['orders']=={'area_first':['a','b'],'timing_risk':['b','a']}
    assert (candidates,observations)==original
    assert frozen['candidates'][0]['prediction']['setup_ns']==pytest.approx(-1.1)
