from pathlib import Path
import hashlib,json,shutil,difflib
r=Path.cwd();base=r/'paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02/actual_correction_v1';out=base/'en_float_refinement_v5';out.mkdir(exist_ok=False)
src=r/'paper/en/manuscript/FAECO.tex';before=src.read_bytes();assert hashlib.sha256(before).hexdigest()=='d7c5c180d67bcd92fee534056adb8f63d404fbc3d93c0b69d2d431470ae9ebb1'
old=br'\includegraphics[width=0.78\linewidth]{fig3_single_round_r21.pdf}';new=old.replace(b'0.78',b'0.70');assert before.count(old)==1
(out/'en_v4_before.tex').write_bytes(before);shutil.copy2(base/'en_float_refinement_v4/build/FAECO.pdf',out/'en_v4_before.pdf');after=before.replace(old,new);src.write_bytes(after);(out/'en_after.tex').write_bytes(after)
(out/'width_only.diff').write_text(''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='v4',tofile='v5')),encoding='utf-8')
for name in ('compile_A8_metadata.py','qa_render_A8_metadata.py'):shutil.copy2(base/'en_float_refinement_v4'/name,out/name)
receipt={'source_before_sha256':hashlib.sha256(before).hexdigest(),'source_after_sha256':hashlib.sha256(after).hexdigest(),'scope':'Only EN Fig3 include width 0.78 to 0.70 linewidth; source figure, data, note, barrier and table all preserved','reverse_binding_pass':after.replace(new,old)==before,'measurement_sha256':hashlib.sha256((base/'fig3_layout_measurement/MEASUREMENT.json').read_bytes()).hexdigest()}
(out/'EDIT_RECEIPT_V5.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
