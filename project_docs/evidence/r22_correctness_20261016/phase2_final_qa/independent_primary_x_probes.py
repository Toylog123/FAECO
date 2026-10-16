from pathlib import Path
import importlib.util, json, hashlib
ROOT=Path.cwd(); checker=ROOT/'project_docs/evidence/r22_b_model_audit_20261016/x_identity_certificate.py'
before=hashlib.sha256(checker.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('primary_x',checker); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
base="module top(A,Y); input A; output Y; wire [3:0] n; assign n = 4'hx; assign Y=A; endmodule"
source="assign Y=A;"
neg={
'escaped_plain_consumer':r'assign Y=\n [0];',
'concat_consumer':'assign Y={n[0], A};',
'replicated_consumer':'assign Y={2{n[0]}};',
'variable_select':'assign Y=A[n[0]];',
'extra_partial_driver':"assign n[0]=1'b0; assign Y=A;",
'extra_concat_driver':"assign {n[0],Y}=2'b00;",
'escaped_partial_driver':r"assign \n [0]=1'b0; assign Y=A;",
'pin_consumer':'cell u(.A({n[0],A}),.Y(Y));',
'escaped_pin_consumer':r'cell u(.A(\n [0]),.Y(Y));',
'procedural_consumer':'always @* Y=n[0];',
'hierarchical_consumer':'assign Y=top.n[0];',
'module_duplicate':source+' endmodule module top();',
'escaped_duplicate_declaration':r'wire [3:0] \n ; assign Y=A;',
'comma_duplicate_declaration':'wire [3:0] z,n; assign Y=A;',
'parameter_escape':'parameter P=n; assign Y=A;',
'attribute_escape':'(* keep=n *) cell u(.A(A),.Y(Y));',
'X_in_unconnected_pin':"cell u(.A(1'bx),.Y(Y));",
'primitive_consumer':'buf u(Y,n[0]);',
'function_consumer':'function f; input a; f=n[0]; endfunction assign Y=A;',
}
cases=[]
for name,replacement in neg.items():
    text=base.replace(source,replacement); result=m.certify_pair(text,text)
    cases.append({'name':name,'expected':False,'actual':result['certified'],'reason':result['reason'],'text':text})
helper="module top(Y); output Y; helper u(.Y(Y)); endmodule module helper(Y); output Y; assign Y=1'bx; endmodule"
r=m.certify_pair(helper,helper); cases.append({'name':'helper_output_boundary','expected':False,'actual':r['certified'],'reason':r['reason'],'text':helper})
positives={
'comma_declarations':"module top(A,Y); input A; output Y; wire [3:0] n,m; assign n=4'hx; assign Y=A; endmodule",
'comma_outputs':"module top(Y,Z); output [3:0] Y,Z; wire [3:0] Y,Z; assign Y=4'hx; assign Z=4'b0000; endmodule",
'escaped_source':r"module top(Y); output Y; wire [3:0] \n ; assign \n =4'hx; assign Y=1'b0; endmodule",
'escaped_keyword_source':r"module top(Y); output Y; wire [3:0] \output ; assign \output =4'hx; assign Y=1'b0; endmodule",
'prefix_distinct':"module top(Y); output Y; wire [3:0] n,n1; assign n=4'hx; assign Y=n1[0]; endmodule",
'module_local_namespace':base+' module helper(n,Y); input n; output Y; assign Y=n; endmodule',
}
for name,text in positives.items():
    r=m.certify_pair(text,text); cases.append({'name':name,'expected':True,'actual':r['certified'],'reason':r['reason'],'text':text})
scope=json.loads((ROOT/'project_docs/evidence/r22_correctness_20261016/B2_X_SCOPE_CHECK.json').read_text(encoding='utf-8')); actual=[]
for pair in scope['pairs']:
    contents=[(ROOT/row['path']).read_bytes() for row in pair['sides']]
    r=m.certify_pair(*[b.decode('utf-8') for b in contents]); assert r['certified'],r
    actual.append({'top':pair['top_module'],'raw_sha256':[hashlib.sha256(b).hexdigest() for b in contents],'certificate':r})
after=hashlib.sha256(checker.read_bytes()).hexdigest(); assert before==after
result={'checker_path':str(checker.relative_to(ROOT)), 'checker_sha256':before,'source_stable':True,'eda_executed':False,'independent_primary_api_probes':cases,'actual_pairs':actual}
output=ROOT/'project_docs/evidence/r22_correctness_20261016/B2_X_PRIMARY_REVIEW.json'; output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checker_sha256':before,'probes':len(cases),'mismatches':[r for r in cases if r['expected']!=r['actual']],'actual_pairs':len(actual)}))
assert all(r['expected'] or not r['actual'] for r in cases), 'unsound acceptance of a negative probe'

