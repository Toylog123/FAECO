"""Admission tests only; never invoke a prover or physical tools."""
import copy
import pytest
from run_selected_sec import check_selection_header


def fixture():
    arms=['PAIR_096_'+str(n) for n in range(9)]
    plan={'measurement_order':arms,'seed':{'candidate_id':'FORWARD__096_'},'singletons':{a:[] for a in arms}}
    summary={'status':'all9_finished','actual_new_cost':{'charged_verifications':9,'completed_routes':9,'completed_sta':18},
             'jobs':[{'arm':a,'returncode':0,'status':'complete'} for a in arms],
             'selected':{'candidate_id':arms[0],'evidence_kind':'actual','sec_status':'pending'},
             'next_sec':'selected_exact_endpoint_pending_SEC'}
    return summary,plan


def test_completed_selected_is_admissible():
    summary,plan=fixture()
    assert check_selection_header(summary,plan)=='PAIR_096_0'


@pytest.mark.parametrize('failure',['running','missing_job','failed_job','wrong_cost','seed','unregistered','prediction'])
def test_incomplete_or_wrong_selection_rejected(failure):
    summary,plan=fixture()
    if failure=='running':summary['status']='running'
    if failure=='missing_job':summary['jobs'].pop()
    if failure=='failed_job':summary['jobs'][0]['returncode']=1
    if failure=='wrong_cost':summary['actual_new_cost']['completed_sta']=17
    if failure=='seed':summary['selected']=copy.deepcopy(plan['seed'])
    if failure=='unregistered':summary['selected']['candidate_id']='OTHER'
    if failure=='prediction':summary['selected']['evidence_kind']='prediction'
    with pytest.raises(ValueError):check_selection_header(summary,plan)
