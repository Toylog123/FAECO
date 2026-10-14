import pytest

from rseco.verilog_modules import module_spans, target_module_text, replace_target_module
from rseco.real_wns import build_boundary_closure_checker

HELPER = '''module helper(D,Q);
input D;
output Q;
buf helper_gate(Q,D);
endmodule
'''
TOP = '''module top(A,Y);
input A;
output Y;
wire n;
buf g1(n,A);
buf g2(Y,n);
endmodule
'''


def test_comments_and_string_literals_do_not_create_fake_modules():
    text='// module fake; endmodule\n'+HELPER+'/* module fake2; endmodule */\n'+TOP
    spans=module_spans(text)
    assert [s.name for s in spans]==['helper','top']
    assert all(text[s.start:s.end]==s.text for s in spans)


def test_replacement_preserves_helper_and_outside_text_byte_for_byte():
    text=HELPER+'// marker\n'+TOP
    result=replace_target_module(text,'top',target_module_text(TOP,'top').replace('g2','g3'))
    assert result.startswith(HELPER+'// marker\n')
    assert target_module_text(result,'helper')==target_module_text(text,'helper')


@pytest.mark.parametrize('text', [TOP+TOP,'module top; module inner; endmodule endmodule','module top;'])
def test_duplicate_nested_or_unterminated_modules_fail_closed(text):
    with pytest.raises(ValueError):
        module_spans(text)


def test_multimodule_boundary_check_requires_explicit_target():
    check=build_boundary_closure_checker()
    assert check(HELPER+TOP,HELPER+TOP).status=='fail'


def test_scoped_boundary_does_not_merge_module_namespaces():
    check=build_boundary_closure_checker(top_module='top')
    assert check(HELPER+TOP,HELPER+TOP).status=='pass'
    # A driver in helper cannot close an undriven net in the actual top.
    changed_helper=HELPER.replace('helper_gate(Q,D)','helper_gate(n_new,D)')
    changed_top=TOP.replace('wire n;','wire n;\nwire n_new;').replace('g2(Y,n)','g2(Y,n_new)')
    assert check(HELPER+TOP,changed_helper+changed_top).status=='fail'


def test_target_undriven_net_cannot_use_helper_net_with_same_name():
    check=build_boundary_closure_checker(top_module='top')
    helper=HELPER.replace('Q','n_new')
    changed=TOP.replace('wire n;','wire n;\nwire n_new;').replace('g2(Y,n)','g2(Y,n_new)')
    assert check(helper+TOP,helper+changed).status=='fail'


def test_strip_target_does_not_include_modules_that_follow_it():
    from rseco.real_wns import strip_to_single_module
    result=strip_to_single_module(TOP+HELPER,'top')
    assert [s.name for s in module_spans(result)]==['top']


def test_sizing_and_joint_actions_cannot_modify_same_named_helper_instance():
    from rseco.real_wns import RealWnsEvaluator
    mapped_helper=HELPER.replace('buf helper_gate(Q,D);',
        'sky130_fd_sc_hd__and2_1 g1 (.A(D),.B(D),.X(Q));')
    mapped_top=TOP.replace('buf g1(n,A);',
        'sky130_fd_sc_hd__and2_1 g1 (.A(A),.B(A),.X(n));')
    ev=RealWnsEvaluator.__new__(RealWnsEvaluator)
    ev.top_module='top'
    for result in (ev._apply(mapped_helper+mapped_top,'g1','G','sky130_fd_sc_hd__and2_2',{}),
                   ev._apply_joint(mapped_helper+mapped_top,{'g1':('sky130_fd_sc_hd__and2_2',{},'G')})):
        assert target_module_text(result,'helper')==target_module_text(mapped_helper,'helper')
        assert 'sky130_fd_sc_hd__and2_2' in target_module_text(result,'top')


def test_patch_ratio_counts_target_instances_including_flop_wrappers(tmp_path,monkeypatch):
    import rseco.real_wns as rw
    from test_r22_static_action_gates import _evaluator,_job
    ev=_evaluator(tmp_path,max_patch_ratio=0.095)
    top=ev.mapped_text.replace('module top(A, B, Y);','module top(A, B, Y, Q);')
    top=top.replace('output Y;','output Y, Q;')
    top=top.replace('endmodule','dff seq1 (.CK(A), .D(B), .Q(Q));\nendmodule')
    helper='module dff(CK,D,Q);\ninput CK,D;\noutput Q;\nbuf ff(Q,D);\nendmodule\n'
    ev.mapped_text=helper+top
    ev.equivalence_checker=rw.build_real_equivalence_checker(ev.liberty_text,top_module='top')
    ev.boundary_checker=rw.build_boundary_closure_checker(top_module='top')
    monkeypatch.setattr(rw,'run_opensta_sequential',lambda **kw: {'wns':-0.5,'tns':-1})
    result=ev._eval_one(_job(ev,'G'))
    # One changed cell / 11 target instances, not /10 SKY cells or /12 merged cells.
    assert result['sta_executed'] is True
    assert not any(e['type']=='F3_patch_too_large' for e in result['failure_events'])
