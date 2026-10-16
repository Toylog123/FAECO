"""A two-state prover must never certify a high-impedance counterexample."""
import pytest
from test_r22_batch import module

LIB='''cell ("sky130_fd_sc_hd__einvn_1") {
 pin ("A") { direction : "input"; }
 pin ("TE_B") { direction : "input"; }
 pin ("Z") { direction : "output"; function : "!A"; three_state : "TE_B"; }
}'''

@pytest.mark.parametrize('role', ['gold', 'gate', 'both', 'helper'])
def test_tristate_is_nonpass_before_two_state_tool(tmp_path, monkeypatch, role):
    batch=module()
    lib=tmp_path/'test.lib'
    lib.write_text(LIB,encoding='utf-8')
    monkeypatch.setattr(batch,'LIB',lib)
    tri="module top(EN,Y); input EN; output Y; sky130_fd_sc_hd__einvn_1 g(.A(1'b1),.TE_B(EN),.Z(Y)); endmodule\n"
    zero="module top(EN,Y); input EN; output Y; assign Y=1'b0; endmodule\n"
    gold=tri if role in ('gold','both') else zero
    gate=tri if role in ('gate','both') else zero
    if role=='helper':
        helper=tri.replace('module top(', 'module helper(')
        gold+=helper
        gate+=helper
    monkeypatch.setattr(batch.subprocess,'run',lambda *a,**k:pytest.fail('Z reached two-state prover'))
    result=batch.final_sec(gold,gate,'top',tmp_path/'proof')
    assert result['status']=='unsupported'
    assert 'three-state' in result['reason']
    assert result['returncode'] is None
    assert (tmp_path/'proof/result.json').is_file()
    assert not (tmp_path/'proof/sec.ys').exists()

def test_explicit_z_also_cannot_reach_two_state_tool(tmp_path,monkeypatch):
    batch=module()
    lib=tmp_path/'test.lib'
    lib.write_text(LIB,encoding='utf-8')
    monkeypatch.setattr(batch,'LIB',lib)
    gold="module top(EN,Y); input EN; output Y; assign Y=EN ? 1'bz : 1'b0; endmodule\n"
    gate=gold.replace("1'bz", "1'b0")
    monkeypatch.setattr(batch.subprocess,'run',lambda *a,**k:pytest.fail('literal Z reached two-state prover'))
    result=batch.final_sec(gold,gate,'top',tmp_path/'proof')
    assert result['status']=='unsupported'
    assert 'high-impedance' in result['reason']

@pytest.mark.parametrize('literal',["'z", "4'hz", "2'b?1", "8'sbz0"])
def test_high_impedance_spellings_are_unsupported(literal):
    from rseco.real_wns import two_state_sec_unsupported_reason
    assert two_state_sec_unsupported_reason(f'assign Y={literal};',{})

def test_comments_strings_and_net_names_are_not_impedance():
    from rseco.real_wns import two_state_sec_unsupported_reason
    assert two_state_sec_unsupported_reason('wire z; assign z=1\'b0; // 1\'bz\n(* note="bufif1 1\'bz" *)',{}) is None

def test_full_checker_refuses_z_before_backend(tmp_path,monkeypatch):
    from rseco import real_wns as rw
    monkeypatch.setattr('rseco.yosys_abc.check_yosys_abc_equivalence',lambda *a,**k:pytest.fail('Z reached ABC'))
    text="module top(A,Y); input A; output Y; assign Y=A ? 1'bz : 1'b0; endmodule"
    check=rw.build_full_netlist_sec_checker(top_module='top',artifact_dir=tmp_path,liberty_text=LIB)
    assert check(text,text).status=='unsupported'
