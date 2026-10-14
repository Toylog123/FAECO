import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('r22_batch',
    Path(__file__).resolve().parents[1] / 'scripts/run_r22_cut_ablation.py')


def module():
    m = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(m)
    return m


def test_locked_matrix_and_common_budget():
    m = module()
    assert len(m.ARMS) == 9
    for arm in m.ARMS:
        cmd = m.job_command(arm, 's27', Path('scratch/test_run'))
        assert cmd[cmd.index('--workers')+1] == '1'
        assert cmd[cmd.index('--sta-budget')+1] == '500'
        assert '--disable-topology' in cmd and '--no-feedback' in cmd
        assert '--skip-mapping' in cmd
        assert '--tns-aware' not in cmd and '--structure-resynth' not in cmd


def test_random_is_same_policy_and_only_changes_order_seed():
    m = module()
    a = m.job_command('W1','s27',Path('same'))
    for seed in (1,2,3):
        b = m.job_command('UR'+str(seed),'s27',Path('same'))
        assert b[:-3] == a
        assert b[-3:] == ['--random-order','--seed',str(seed)]


def test_uniform_control_explicit_and_cover_only():
    m = module()
    cmd = m.job_command('U0','s27',Path('same'))
    assert cmd[cmd.index('--cut-sources')+1] == 'weighted'
    assert cmd[cmd.index('--node-cost-mode')+1] == 'uniform'
    cmd = m.job_command('C','s27',Path('same'))
    assert cmd[cmd.index('--cut-sources')+1] == 'cover'


def test_driver_matches_real_cli_directory_contract(monkeypatch, tmp_path):
    import json
    from types import SimpleNamespace
    m = module()
    baseline = tmp_path/'inputs'/'s27'
    baseline.mkdir(parents=True)
    (baseline/'mapped.v').write_text('mapped baseline')
    manifest = {'source_manifest':m.source_manifest(),'inputs':{'s27':'source'},'lib_sha256':'library'}
    m.save(baseline/'input.json',{'source_manifest':manifest['source_manifest'],
                                'mapped_sha256':m.sha(baseline/'mapped.v')})
    original_sha = m.sha
    monkeypatch.setattr(m,'sha',lambda p: 'library' if Path(p)==Path(m.LIB) else
                        'source' if str(p).endswith('iscas89/s27.v')
                        or str(p).endswith(r'iscas89\s27.v') else original_sha(p))
    commands=[]
    def runner(cmd, **kwargs):
        # Actual entry point appends circuit to --output-dir.
        out = Path(cmd[cmd.index('--output-dir')+1])/cmd[cmd.index('--circuit')+1]
        assert (out/'mapped.v').read_text() == 'mapped baseline'
        m.save(out/'outerloop_result.json',{'n_new_sta_runs':1,'state':{
            'budget':{'sta_used':1},'current_netlist_text':'final'},
            'baseline_wns':-1,'wns':-0.9,'stop_reason':'stagnation'})
        m.save(out/'eval_trials.json',{'trials':[],'sta_launch_events':[]})
        m.save(out/'run_config.json',{'resolved_args':{}})
        commands.append(cmd)
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(m.subprocess,'run',runner)
    def sec(initial, final, circuit, out):
        out.mkdir()
        (out/'initial_raw.v').write_text(initial)
        (out/'final_raw.v').write_text(final)
        for name in ('sec.log','sec.ys','helpers.v','cells.v'):
            (out/name).write_text('stub proof')
        result={'status':'pass','initial_sha256':m.sha(out/'initial_raw.v'),
                'final_sha256':m.sha(out/'final_raw.v')}
        m.save(out/'result.json',result)
        return result
    monkeypatch.setattr(m,'final_sec',sec)
    done=m.execute_circuit('s27',tmp_path,manifest)
    assert len(done)==9 and len(commands)==9
    # Resume reuses registered, completed results and never launches tools.
    assert m.execute_circuit('s27',tmp_path,manifest)==done
    assert len(commands)==9

    # A completion label alone must not bypass original proof/ledger checks.
    (tmp_path/'W0/s27/final_sec/result.json').unlink()
    import pytest
    with pytest.raises(RuntimeError,match='receipt'):
        m.execute_circuit('s27',tmp_path,manifest)


def test_sec_isolates_identical_shared_helper_and_rejects_changed_helper():
    import pytest
    m=module()
    helper='module dff(input CK,D,output reg Q); always @(posedge CK) Q <= D; endmodule'
    top='module s27(input CK,D,output Q); dff u(CK,D,Q); endmodule'
    gold, gate, helpers=m.sec_designs(top+'\n'+helper,top+'\n'+helper,'s27')
    assert 'module dff' not in gold and 'module dff' not in gate
    assert helpers.count('module dff')==1
    with pytest.raises(ValueError,match='helper'):
        m.sec_designs(top+'\n'+helper,top+'\n'+helper.replace('Q <= D','Q <= ~D'),'s27')


def test_stopped_batch_does_not_launch_or_map(tmp_path):
    import threading
    import pytest
    m=module()
    stop=threading.Event()
    stop.set()
    with pytest.raises(RuntimeError,match='stopped'):
        m.execute_circuit('s27',tmp_path,{},stop)
    assert not (tmp_path/'inputs').exists()
