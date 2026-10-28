from pathlib import Path
import sys,hashlib,json
R=Path('paper/zh/review_rounds/r23_20261018');role=sys.argv[1]
parts=['<sprint_contract>\n'+(R/'contract.json').read_text(encoding='utf-8')+'\n</sprint_contract>',
       '<phase1_output>\n'+(R/f'seats/{role}_phase1.md').read_text(encoding='utf-8')+'\n</phase1_output>',
       '<paper_content>\n'+(R/'inputs/manuscript.tex').read_text(encoding='utf-8')+'\n</paper_content>']
out=R/f'seats/{role}_phase2_input.txt'
with out.open('x',encoding='utf-8') as f:f.write('\n\n'.join(parts))
print(json.dumps({'role':role,'payload_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
