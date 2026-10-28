"""Family-B timing observations; mark three unsupported functional proofs."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
UNSUPPORTED={'b09','b20','b21'}
BLUE,GREY='#516779','#87949F'
mpl.rcParams.update({'font.family':'sans-serif',
    'font.sans-serif':['Microsoft YaHei','SimHei','Arial','DejaVu Sans'],
    'axes.unicode_minus':False,'font.size':7.5,'axes.labelsize':7.5,
    'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,'axes.linewidth':.6,
    'axes.spines.top':False,'axes.spines.right':False,
    'svg.fonttype':'none','pdf.fonttype':42,'savefig.dpi':600,
    'figure.facecolor':'white','savefig.facecolor':'white'})


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--alignment-auditor',type=Path,required=True)
    args=parser.parse_args()
    source=ROOT/'experiments/20260826_aggregation/summary.json'
    previous=ROOT/'paper/zh/figures/data/final/fig4_unified_gain_r21.csv'
    auditpath=ROOT/'project_docs/evidence/r22_b_model_audit_20261016/audit.json'
    if sha(source)!='1ca58f0fca289551557a138fc3b7c8ca1f88db777f4c91a9fa0d86d421cf5eaf':
        raise ValueError('Family B source bytes changed')
    if sha(previous)!='c4cd3c60020ea923e814e3165ff88bc10d9633e6883c2d6bb4e643d750c4eeac':
        raise ValueError('Previous accepted source CSV changed')
    if sha(auditpath)!='0869d234751af08715a15a58c98636e7ae193d8a1d423401f6181fc88a83365d':
        raise ValueError('Historical model audit bytes changed')
    summary=json.loads(source.read_text()); audit=json.loads(auditpath.read_text())
    flagged={r['circuit'] for r in audit['runs'] if r.get('used_tristate_types')}
    if flagged!=UNSUPPORTED: raise ValueError('Unsupported tristate set differs from audit')
    groups=[summary[k] for k in ('iscas89','itc99','picorv32')]
    if list(map(len,groups))!=[8,19,3]:raise ValueError('Incomplete original familyB population')
    old={r['circuit']:r for r in csv.DictReader(previous.open(encoding='utf-8-sig'))}
    rows=[]
    for group in groups:
        for row in group:
            applicable=row['circuit']!='picorv32_regs'
            base,final=row['baseline_wns'],row['final_wns']
            gain=round(final-base,8) if applicable else None
            before=old[row['circuit']]
            if applicable:
                assert np.isfinite(gain) and gain>=-1e-8
                assert float(before['baseline_wns_ns'])==base and float(before['final_wns_ns'])==final
                assert float(before['gain_ns'])==gain
            else:assert not before['gain_ns'] and before['applicable']=='False'
            rows.append({'family':'B','circuit':row['circuit'],'baseline_wns_ns':base,
                'final_wns_ns':final,'gain_ns':gain,'applicable':applicable,
                'functional_proof_annotation':'unsupported_true_tristate' if row['circuit'] in UNSUPPORTED
                    else ('not_applicable_no_setup_path' if not applicable else 'not_flagged_by_this_annotation')})
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    with (out/'fig4_r24_source.csv').open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # Adapt the original lollipop panels; equal widths satisfy shared row geometry.
    fig,axes=plt.subplots(1,3,figsize=(6.6929133858,3.5433070866))
    fig.subplots_adjust(left=.065,right=.965,bottom=.20,top=.88,wspace=.50)
    by={r['circuit']:r for r in rows}
    for ax,group,title,lim,panel in zip(axes,groups,['ISCAS89','ITC-99','PicoRV32'],[.65,3,1.35],'abc'):
        valid=[by[r['circuit']] for r in group if by[r['circuit']]['applicable']]
        y=np.arange(len(valid))
        labels=[r['circuit'].replace('picorv32_pcpi_mul','PCPI mul').replace('picorv32','主核') for r in valid]
        for yy,row in zip(y,valid):
            gain=row['gain_ns']; unsupported=row['circuit'] in UNSUPPORTED
            ax.hlines(yy,0,gain,color=BLUE,lw=1.5,linestyle='--' if unsupported else '-')
            ax.plot(gain,yy,'o' if gain>0 else 's',ms=3.6,
                markerfacecolor='white' if unsupported else (BLUE if gain>0 else GREY),
                markeredgecolor=BLUE if gain>0 else GREY,markeredgewidth=.9)
            ax.text(gain+lim*.035,yy,f'{gain:+.2f}',va='center',fontsize=7)
        ax.set_yticks(y,labels)
        ax.set_xlim(-lim*.02,lim)
        ax.set_ylim(len(valid)-.35,-.75)
        ax.set_xlabel('ΔWNS (ns)')
        ax.set_title(title,loc='left',fontsize=8,pad=7)
        ax.text(-.15,1.05,panel,transform=ax.transAxes,weight='bold',fontsize=8)
        # The left spine supplies the zero reference; do not cross zero labels.
        if title=='PicoRV32':
            ax.text(.03,.10,'regs：无 setup 路径\nN/A，不计入分母',transform=ax.transAxes,fontsize=7,color=GREY)
    handle=Line2D([],[],color=BLUE,linestyle='--',marker='o',markersize=3.6,
        markerfacecolor='white',markeredgecolor=BLUE,lw=1.5)
    fig.legend([handle],['功能证明不支持（b09、b20、b21）'],loc='lower center',
        bbox_to_anchor=(.5,.015),frameon=False,fontsize=7,handlelength=2.5)
    spec=importlib.util.spec_from_file_location('alignment',args.alignment_auditor)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    helper.require_matplotlib_panel_alignment(fig,axes=axes,panel_ids=['a','b','c'],
        row_groups=[['a','b','c']],require_panel_labels=True,
        json_out=out/'PANEL_ALIGNMENT.json',overlay_svg=out/'PANEL_ALIGNMENT_OVERLAY.svg')
    fig.savefig(out/'fig4_r24.pdf',format='pdf')
    fig.savefig(out/'fig4_r24.svg',format='svg')
    fig.savefig(out/'fig4_r24.png',format='png',dpi=600)
    plt.close(fig)
    shutil.copyfile(__file__,out/'plotter_snapshot.py')
    shutil.copyfile(args.alignment_auditor,out/'alignment_auditor_snapshot.py')
    dump(out/'SOURCE_BINDING.json',{'family':'B','population':30,'displayed_numeric_rows':29,
        'preserved_not_applicable':['picorv32_regs'],'unsupported_functional_proof_cases':sorted(UNSUPPORTED),
        'data_values_identical_to_previous':True,'no_new_eda':True,
        'sources':{p.relative_to(ROOT).as_posix():sha(p) for p in [source,previous,auditpath]},
        'status_scope':'Only three actual-tristate cases marked unsupported; unmarked is not a new proof-pass assertion.',
        'reuse':'original unified_results() lollipop design, all timing values; three open markers/dashes; equal panel widths, group labels without ratio, no vertical grid through values',
        'physical_size_mm':[170,90],'exports':{p.name:sha(p) for p in out.iterdir() if p.is_file()}})
    print(json.dumps({'output':str(out),'all_rows':len(rows),'itc_rows':len(groups[1]),'unsupported':sorted(UNSUPPORTED)}))


if __name__=='__main__':main()
