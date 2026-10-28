"""Root text-only terminology check, preserving the frozen image/figure audits."""
from pathlib import Path
import json,hashlib
root=Path.cwd().resolve();base=root/'paper/zh/figures/data/previews/r22_D_feedback_mechanism_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=(base/'CAPTION_EN.md').read_bytes();new=(base/'CAPTION_EN_v2.md').read_bytes()
assert old.count(b'ideal-wire STA')==1 and new==old.replace(b'ideal-wire STA',b'ideal-net STA')
receipt=json.loads((base/'FINAL_RECEIPT.json').read_text(encoding='utf-8'))
for name in ['iteration02/r22_D_feedback_mechanism.pdf','iteration02/r22_D_feedback_mechanism.png','CAPTION_EN.md']:
    assert sha(base/name)==receipt['artifacts'][name]['sha256']
assert sha(base/'CAPTION_EN_v2.md')=='86831fdb2a9408cbb5ab64bfb7e8f508722795b25a1f339b369f3cefbcf2662b'
out={'accepted':True,'selected_caption':'CAPTION_EN_v2.md','selected_caption_sha256':sha(base/'CAPTION_EN_v2.md'),
 'change':'Only ideal-wire STA to existing manuscript term ideal-net STA; evidence, counts, scope and figure bytes unchanged',
 'frozen_caption_and_figure_receipt_preserved':True,'supplement_sha256':sha(base/'CAPTION_EN_V2_SUPPLEMENT.json')}
with (base/'ROOT_CAPTION_EN_V2_ACCEPTANCE.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
(base/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print(json.dumps(out))
