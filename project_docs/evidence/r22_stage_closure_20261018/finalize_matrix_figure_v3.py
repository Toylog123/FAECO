from pathlib import Path
import hashlib, json, shutil, subprocess, sys
root=Path.cwd()
parent=root/'paper/zh/figures/data/previews'
old=parent/'r22_matrix_gain_cost_v1'
out=parent/'r22_matrix_gain_cost_v3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
same={s:sha(old/('r22_matrix_gain_cost'+s))==sha(out/('r22_matrix_gain_cost'+s)) for s in ['_raw.csv','_paired.csv']}
assert all(same.values())
plotter=root/'paper/zh/figures/data/scripts/review_r22_matrix_gain_cost.py'
helper=Path.home()/'.codex/skills/nature-figure/scripts/audit_panel_alignment.py'
probe=root/'scratch/r22_matrix_v3_incomplete_refusal'
p=subprocess.run([sys.executable,'-X','utf8',str(plotter),'--audit',str(root/'project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_51.json'),'--output-dir',str(probe),'--alignment-auditor',str(helper)],capture_output=True,text=True,encoding='utf-8',timeout=30)
assert p.returncode!=0 and not probe.exists() and 'Only the independently accepted' in p.stderr
for source,name in [(plotter,'plotter_snapshot.py'),(helper,'alignment_auditor_snapshot.py')]:
    assert not (out/name).exists()
    shutil.copyfile(source,out/name)
text=(old/'README.md').read_text(encoding='utf-8')
text+='\n\n## 2026-10-18 最终布局修订 v3\n\nv1 自动碰撞审计检出6处斜排标签边界重叠；v2先试竖排，v3将渲染前对齐门纳入生成器。v1/v2保留，数据CSV与v1逐字节相同。v3实际PDF碰撞0FAIL/0WARN，对齐门PASS，最小字形6.8pt；四panel及全图已由主线实际查看。旧v1独立数据/机制审查继续适用，v3独立视觉复查另附。\n\n重建须向生成器传 `--alignment-auditor alignment_auditor_snapshot.py`（本目录保存准确副本），并选全新输出目录；从ZIP/7z恢复原始72completion后可按既有输入路径重建。PNG为600dpi预览；170mm项目图幅，不声明特定期刊终稿。\n'
(out/'README.md').write_text(text,encoding='utf-8')
receipt={'raw_and_paired_csv_identical_to_v1':same,'incomplete51_refused_before_output':True,'guard_returncode':p.returncode,'guard_stderr':p.stderr,'panel_visual_review':{'a':'all72 gain values visible','b':'all72 total actualSTA counts visible','c':'all64 gain differences and zero controls visible','d':'all64 cost contrasts with unfavorable values visible'},'full_figure_visual_review':'root viewed actual final PNG, clear vertical labels and no clipping; automated PDF collision pass; final physical size170x128mm','plotter_sha256':sha(plotter),'files_sha256':{x.name:sha(x) for x in out.iterdir() if x.is_file()}}
with (out/'FINAL_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
print(json.dumps({'csv_same':same,'incomplete_guard':'pass','source_sha256':sha(plotter)}))
