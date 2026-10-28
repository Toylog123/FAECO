"""Editable six-gate artificial static example; no STA or SEC is run."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[5]
EVIDENCE_SHA = 'b0eff5f45bf8d6ef91798e37cbbbdf5f92f9aa6ed509d4eafeaa9858471967b2'
BLUE, GREY, INK, PALE = '#245B9E', '#8C949D', '#263442', '#EEF3F8'
mpl.rcParams.update({'font.family':'sans-serif',
    'font.sans-serif':['Microsoft YaHei','SimHei','Arial','DejaVu Sans'],
    'axes.unicode_minus':False, 'font.size':7.5, 'axes.labelsize':7.5,
    'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,
    'svg.fonttype':'none','pdf.fonttype':42,'savefig.dpi':600,
    'figure.facecolor':'white','savefig.facecolor':'white'})


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')


def arrow(ax,start,end,color=GREY,lw=.8):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=6,
        linewidth=lw,color=color,shrinkA=0,shrinkB=0))


def setup(ax,panel,title):
    ax.set(xlim=(0,1),ylim=(0,1)); ax.axis('off')
    ax.text(0,1.08,panel,transform=ax.transAxes,fontsize=8,fontweight='bold')
    ax.text(.045,1.08,title,transform=ax.transAxes,fontsize=7.5,color=INK)


def validate_toy(t):
    if hashlib.sha256(t['netlist_fulltext'].encode()).hexdigest()!=t['netlist_sha256']:
        raise ValueError('Toy netlist SHA mismatch')
    if t['critical_instances']!=['g1','g4','g6'] or t['r_available']!=['g1','g2','g4','g5']:
        raise ValueError('Unexpected static example')
    if t['input']['gate_inputs']['g3']!=['c','c']:
        raise ValueError('The same c signal must drive both g3 pins')
    if t['boundary_dispatch_order']!=['critical_path_cover','weighted_st']:
        raise ValueError('Unexpected dispatch order')
    if set(t['trace']['configured_weights'].values())!={1.0}:
        raise ValueError('The worked example must use all-one weights')
    drivers={net:g for g,net in t['input']['gate_outputs'].items()}
    n=len(t['input']['gates']); S2=sum(v*v for v in t['fanin_size'].values())
    assert S2==t['sum_squares']==57
    rows=[]
    for g in t['input']['gates']:
        r=g in t['r_available']; s=t['fanin_size'][g]; f=t['fanout'][g]
        depth=t['depth'][g]
        numerator=1+1/(1+depth)+.1*f*r+s*s/S2+.01*n
        cost=max(.05,numerator/(1+depth/max(t['depth'].values())*r))
        assert abs(cost-t['trace']['node_costs'][g])<1e-12
        rows.append({'gate':g,'inputs':','.join(t['input']['gate_inputs'][g]),
            'output':t['input']['gate_outputs'][g],'depth':t['depth'][g],
            'fanin_size':s,'cone_internal_fanout':f,'R_available':r,'cost':cost})
    for item in t['trace']['candidates']:
        selected=set(item['gates']); inputs=[]; outputs=[]; internal=[]
        for g in item['gates']:
            for net in t['input']['gate_inputs'][g]:
                if drivers.get(net) not in selected and net not in inputs: inputs.append(net)
            net=t['input']['gate_outputs'][g]
            external=net in t['input']['boundary_outputs'] or any(net in ins and other not in selected
                for other,ins in t['input']['gate_inputs'].items())
            (outputs if external else internal).append(net)
        assert inputs==item['boundary_inputs'] and outputs==item['boundary_outputs'] and internal==item['internal_nets']
        assert abs(sum(t['trace']['node_costs'][g] for g in selected)-item['node_cost_sum'])<1e-12
    assert t['weighted_solution']['selected_gates']==['g6']
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--method-evidence',type=Path,default=ROOT/'paper/zh/review_rounds/r24_20261018/METHOD_EVIDENCE.json')
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--alignment-auditor',type=Path,required=True)
    args=parser.parse_args()
    if sha(args.method_evidence)!=EVIDENCE_SHA:
        raise ValueError('Method evidence bytes differ from finalized r24 source')
    evidence=json.loads(args.method_evidence.read_text(encoding='utf-8')); t=evidence['toy']
    rows=validate_toy(t)
    out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=False)
    dump(out/'TOY_INPUT.json',t)
    (out/'toy.v').write_bytes(t['netlist_fulltext'].encode('utf-8'))
    with (out/'node_costs.csv').open('x',encoding='utf-8-sig',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    dump(out/'FIGURE_CONTRACT.json',{'scope':'人工指定六门静态例；未运行STA、SEC或计时',
        'claim':'边界到区域是可复算的，实际cover-first次序不同于节点和升序；R−仍可进入weighted区域。',
        'panel_a':'六门有向依赖、相同c驱动两引脚、全1权重cost/R匹配可用性',
        'panel_b':'第1项Cc的门、边界、内部网及实例顺序',
        'panel_c':'第2项Cw的门、边界及实例顺序',
        'archetype':'schematic-led composite','physical_size_mm':[170,98],
        'style':'inherit manuscript font/palette; original graph data and geometry preserved conceptually',
        'no_new_eda':True,'no_gain_claim':True})
    # Literal dimensions retain the manuscript's 170 mm width without tight crop.
    fig=plt.figure(figsize=(6.6929133858,3.8582677165))
    ax=fig.add_axes((.035,.46,.93,.43)); setup(ax,'a','六门输入锥与节点代价')
    ax.text(.57,1.08,'全 λ = 1；P = (g1, g4, g6)',fontsize=7.5,color=INK)
    coords={'g1':(.17,.79),'g2':(.17,.46),'g3':(.17,.13),
        'g4':(.50,.68),'g5':(.50,.28),'g6':(.82,.48)}
    for g,inp in t['input']['gate_inputs'].items():
        for net in dict.fromkeys(inp):
            driver=next((v for v,n in t['input']['gate_outputs'].items() if n==net),None)
            if driver:
                sx,sy=coords[driver]; ex,ey=coords[g]
                arrow(ax,(sx+.08,sy),(ex-.08,ey))
    # Every internal net is labelled near its driver, outside the gate box.
    signals={'n1':(.31,.85),'n2':(.31,.48),'n3':(.31,.13),'n4':(.65,.73),'n5':(.65,.23)}
    for net,(x,y) in signals.items(): ax.text(x,y,net,fontsize=7,ha='center',va='center',color=INK)
    for name,y in [('a',.79),('b',.46)]:
        ax.text(.025,y+.065,name,ha='center',fontsize=7)
        arrow(ax,(.015,y),(.09,y))
    ax.text(.025,.205,'c → A/B',ha='center',fontsize=7)
    # Two separate sink pin arrows carry the same c net.
    ax.plot([.015,.055],[.13,.13],color=GREY,lw=.8)
    arrow(ax,(.055,.13),(.09,.17)); arrow(ax,(.055,.13),(.09,.09))
    arrow(ax,(.90,.48),(.98,.48)); ax.text(.96,.56,'n6',fontsize=7,ha='center')
    for g,(x,y) in coords.items():
        patch=FancyBboxPatch((x-.08,y-.10),.16,.20,boxstyle='round,pad=0.004,rounding_size=0.02',
            ec=BLUE,fc=PALE if g in t['critical_instances'] else 'white',lw=.8)
        patch.set_gid('node-'+g); ax.add_patch(patch)
        availability='R+' if g in t['r_available'] else 'R−'
        ax.text(x,y,f'{g} · {availability}\n{t["trace"]["node_costs"][g]:.6f}',
            ha='center',va='center',fontsize=7,linespacing=1.5,color=INK)
    ax.text(.55,.025,'浅蓝：P 中的实例；R+ / R−：有 / 无 R 匹配',fontsize=7,color=INK,ha='center')
    axes=[ax]
    for index,(x,item) in enumerate(zip((.035,.535),t['trace']['candidates'])):
        current=fig.add_axes((x,.125,.43,.22)); axes.append(current)
        name='Cc' if item['method']=='critical_path_cover' else 'Cw'
        title=('覆盖区域 Cc · 第1项' if name=='Cc' else '加权区域 Cw · 第2项')
        setup(current,chr(98+index),title)
        body=FancyBboxPatch((.01,.04),.98,.87,boxstyle='round,pad=0.003,rounding_size=0.02',
            ec=BLUE if name=='Cc' else GREY,fc=PALE if name=='Cc' else '#F7F8FA',lw=.8)
        body.set_gid('region-'+name); current.add_patch(body)
        fmt=lambda values:'{'+', '.join(values)+'}'
        current.text(.045,.76,'门 '+fmt(item['gates'])+'；Σcost = '+f'{item["node_cost_sum"]:.6f}',fontsize=7,color=INK)
        current.text(.045,.56,'输入 '+fmt(item['boundary_inputs'])+' → 输出 '+fmt(item['boundary_outputs']),fontsize=7,color=INK)
        current.text(.045,.36,'内部网 '+(fmt(item['internal_nets']) if item['internal_nets'] else '无'),fontsize=7,color=INK)
        current.text(.045,.16,'实例顺序 '+' → '.join(item['gates']),fontsize=7,color=INK)
    fig.text(.035,.035,'调度：先 Cc 后 Cw；相同规范区域合并来源。R−不禁止该门进入区域。',fontsize=7,color=INK)
    spec=importlib.util.spec_from_file_location('panel_alignment',args.alignment_auditor)
    helper=importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    helper.require_matplotlib_panel_alignment(fig,axes=axes,panel_ids=['a','b','c'],
        row_groups=[['b','c']],require_panel_labels=True,
        json_out=out/'PANEL_ALIGNMENT.json',overlay_svg=out/'PANEL_ALIGNMENT_OVERLAY.svg')
    stem='r24_toy_mechanism'
    fig.savefig(out/f'{stem}.pdf',format='pdf')
    fig.savefig(out/f'{stem}.svg',format='svg')
    # Matplotlib emits an optional external SVG DTD. Remove this declaration;
    # all geometry/text remains byte-for-byte in the self-contained SVG body.
    svg=out/f'{stem}.svg'
    svg_text=re.sub(r'<!DOCTYPE[^>]*>\s*','',svg.read_text(encoding='utf-8'))
    # Equivalent explicit user-unit sizes let SVG readers inspect the existing
    # Matplotlib CSS font shorthand; the shorthand and all text stay unchanged.
    svg_text=re.sub(r'(<text style="[^"]*font: (?:700 )?([0-9.]+)px[^"]*")',
                    r'\1 font-size="\2"',svg_text)
    svg.write_text(svg_text,encoding='utf-8')
    fig.savefig(out/f'{stem}.png',format='png',dpi=600)
    plt.close(fig)
    shutil.copyfile(__file__,out/'plotter_snapshot.py')
    shutil.copyfile(args.alignment_auditor,out/'alignment_auditor_snapshot.py')
    dump(out/'SOURCE_BINDING.json',{'method_evidence_path':args.method_evidence.relative_to(ROOT).as_posix(),
        'method_evidence_sha256':sha(args.method_evidence),'toy_input_sha256':sha(out/'TOY_INPUT.json'),
        'netlist_sha256':t['netlist_sha256'],'liberty':t['liberty'],
        'all_six_costs_recomputed':True,'both_boundaries_recomputed':True,
        'no_new_eda':True,'scope':t['scope'],
        'files':{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()}})
    print(json.dumps({'output':str(out),'costs_checked':6,'boundaries_checked':2}))


if __name__=='__main__': main()
