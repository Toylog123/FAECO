"""Reproducible evidence panels and editable mechanism diagrams for r21."""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

ROOT = Path(__file__).resolve().parents[5]
FIGROOT = ROOT / 'paper/zh/figures'
DATA = FIGROOT / 'data/final'
MANUAL = FIGROOT / 'manual/figures'
SPEC = FIGROOT / 'data/plot_specs'
for directory in (DATA, MANUAL, SPEC):
    directory.mkdir(parents=True, exist_ok=True)
mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'Arial', 'DejaVu Sans'],
    'axes.unicode_minus': False, 'font.size': 7.5,
    'axes.labelsize': 7.5, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
    'legend.fontsize': 7, 'axes.linewidth': .6,
    'axes.spines.top': False, 'axes.spines.right': False,
    'svg.fonttype': 'none', 'pdf.fonttype': 42,
    'figure.facecolor': 'white', 'savefig.facecolor': 'white',
    'savefig.dpi': 600,
})
BLUE = '#245B9E'
GREY = '#8C949D'
ORANGE = '#C77435'
INK = '#263442'
PALE = '#EEF3F8'
sources = {}


def load(name):
    path = ROOT / name
    sources[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text(encoding='utf-8'))


def export(fig, stem, directory=DATA):
    # Fixed physical size; margins are designed explicitly, with no tight crop.
    fig.savefig(directory / f'{stem}.pdf', format='pdf')
    fig.savefig(directory / f'{stem}.svg', format='svg')
    svg_path=directory / f'{stem}.svg'
    svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    fig.savefig(directory / f'{stem}.png', format='png', dpi=600)
    plt.close(fig)
    print('exported', stem, flush=True)


def csv_out(stem, rows):
    with (DATA / f'{stem}.csv').open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def box(ax, xy, size, text, color=BLUE, fill=PALE, fontsize=7.5, dashed=False):
    x, y = xy
    w, h = size
    patch = FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008,rounding_size=0.015',
                          ec=color,fc=fill,lw=.9,linestyle='--' if dashed else '-')
    ax.add_patch(patch)
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fontsize,color=INK,linespacing=1.6)


def arrow(ax, start, end, color=BLUE, dashed=False, rad=0, lw=1):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=8,
                               lw=lw,color=color,linestyle='--' if dashed else '-',
                               connectionstyle=f'arc3,rad={rad}'))


def canvas(width_mm, height_mm):
    fig = plt.figure(figsize=(width_mm/25.4,height_mm/25.4))
    ax = fig.add_axes([.02,.03,.96,.94])
    ax.set(xlim=(0,1),ylim=(0,1))
    ax.axis('off')
    return fig, ax


def method_flow():
    fig, ax = canvas(170,60)
    box(ax,(.018,.58),(.202,.33),'映射准备\nYosys / Liberty\n基线网表 N0')
    box(ax,(.295,.58),(.28,.33),'当前网表 N → 违例锥\nCw / Cc 生成与融合排序\nR / G / B / JOINT')
    box(ax,(.65,.58),(.335,.33),'分层候选验证\n局部函数 / 结构 → 理想线网 STA\n简化 SPEF 复测（可选）')
    arrow(ax,(.22,.75),(.29,.75))
    arrow(ax,(.575,.75),(.645,.75))
    box(ax,(.65,.15),(.20,.22),'满足接受判据\n提交 N ← N + Δ')
    arrow(ax,(.75,.57),(.75,.38))
    arrow(ax,(.65,.25),(.45,.25))
    arrow(ax,(.45,.25),(.45,.57))
    ax.text(.47,.39,'下一轮\n重新提锥',ha='left',va='center',color=BLUE,fontsize=7)
    box(ax,(.018,.15),(.257,.23),'F1–F6 记录 / 搜索分析\n权重更新（可选）',color=GREY,fill='#F7F8FA',dashed=True)
    ax.plot([.815,.815,.145,.145],[.58,.47,.47,.39],ls='--',lw=.8,color=GREY)
    arrow(ax,(.145,.415),(.145,.39),GREY,True)
    arrow(ax,(.27,.27),(.36,.575),GREY,True,rad=.1)
    box(ax,(.885,.15),(.10,.23),'搜索\n停止',color=GREY,fill='white')
    arrow(ax,(.852,.25),(.88,.25),GREY)
    ax.text(.82,.065,'最终网表 → 独立全网表 SEC',ha='center',va='center',fontsize=7.5)
    arrow(ax,(.935,.14),(.935,.105),GREY)
    export(fig,'fig1_iterative_flow_r21',MANUAL)


def mechanisms():
    fig, ax = canvas(170,92)
    ax.text(.005,.975,'a',weight='bold',fontsize=8)
    ax.text(.045,.975,'违例扇入锥',fontsize=8)
    ax.text(.49,.975,'b',weight='bold',fontsize=8)
    ax.text(.535,.975,'节点分裂与容量',fontsize=8)
    coords={'g1':(.075,.85),'g2':(.075,.70),'g3':(.075,.55),
            'g4':(.255,.80),'g5':(.255,.62),'g6':(.40,.71)}
    edges=[('g1','g4'),('g2','g4'),('g2','g5'),('g3','g5'),('g4','g6'),('g5','g6')]
    critical={('g1','g4'),('g4','g6')}
    for a,b in edges:
        arrow(ax,coords[a],coords[b],ORANGE if (a,b) in critical else GREY,
              dashed=(a,b) in critical,lw=1.2 if (a,b) in critical else .8)
    for g,(x,y) in coords.items():
        ax.add_patch(Circle((x,y),.025,fc='white',ec=BLUE,lw=.9))
        ax.text(x,y,g,ha='center',va='center',fontsize=7)
        ax.text(x,y-.044,'R+' if g not in ('g3','g6') else 'R−',ha='center',va='top',
                fontsize=7,color=BLUE if g not in ('g3','g6') else GREY)
    arrow(ax,(.425,.71),(.465,.71),ORANGE,True)
    ax.text(.467,.71,'t',fontsize=7,va='center')
    ax.text(.03,.45,'虚线：关键路径；R+ / R−：R 可用 / 不可用',fontsize=7)
    # Every source-to-sink dependency follows the six-gate cone above.
    split={
        'g1':((.58,.855),(.645,.855)), 'g2':((.58,.705),(.645,.705)),
        'g3':((.58,.555),(.645,.555)), 'g4':((.735,.805),(.80,.805)),
        'g5':((.735,.62),(.80,.62)), 'g6':((.865,.705),(.925,.705)),
    }
    for g,(pin,pout) in split.items():
        arrow(ax,(pin[0]+.018,pin[1]),(pout[0]-.018,pout[1]),BLUE,lw=.9)
        ax.text((pin[0]+pout[0])/2,pin[1]+.027,'w'+g[1],ha='center',fontsize=7,color=BLUE)
    for a,b in edges:
        start=split[a][1];end=split[b][0]
        arrow(ax,(start[0]+.018,start[1]),(end[0]-.018,end[1]),GREY,lw=.7)
    for g,(pin,pout) in split.items():
        for point,suffix in ((pin,'i'),(pout,'o')):
            ax.add_patch(Circle(point,.019,fc='white',ec=BLUE,lw=.8))
            ax.text(*point,g[1]+suffix,ha='center',va='center',fontsize=7)
    for point,label in (((.505,.705),'s'),((.982,.705),'t')):
        ax.add_patch(Circle(point,.018,fc='white',ec=GREY,lw=.8))
        ax.text(*point,label,ha='center',va='center',fontsize=7)
    for g in ('g1','g2','g3'):
        arrow(ax,(.523,.705),(split[g][0][0]-.02,split[g][0][1]),GREY,lw=.7)
    arrow(ax,(.946,.705),(.963,.705),GREY,lw=.7)
    ax.text(.52,.50,'i / o：入 / 出节点；内部边 wi = cost(gi)',fontsize=7)
    ax.text(.52,.455,'灰边：依赖或源 / 汇连接，容量 ∞',fontsize=7,color=GREY)
    box(ax,(.018,.31),(.265,.10),'加权最小割 Cw → Pw',fontsize=7.5)
    box(ax,(.018,.17),(.265,.10),'关键路径覆盖 Cc → Pc',fontsize=7.5)
    box(ax,(.365,.24),(.25,.12),'候选实例化\nR / G / B / JOINT',fontsize=7.5)
    box(ax,(.70,.24),(.28,.12),'候选融合排序\n割代价 / 覆盖 / 策略优先级',fontsize=7.5)
    arrow(ax,(.285,.36),(.36,.315))
    arrow(ax,(.285,.22),(.36,.285))
    arrow(ax,(.62,.30),(.695,.30))
    for i,(name,label) in enumerate([('R','逻辑等价替换'),('G','门尺寸调整'),('B','缓冲器插入'),('JOINT','关键路径区段联合')]):
        x=.015+i*.247
        box(ax,(x,.02),(.22,.10),f'{name}\n{label}',fill='white',fontsize=7.5)
    export(fig,'fig2_candidate_mechanism_r21',MANUAL)


def unified_results():
    summary=load('experiments/20260826_aggregation/summary.json')
    groups=[summary[k] for k in ('iscas89','itc99','picorv32')]
    rows=[]
    audit_rows=[]
    fig,axes=plt.subplots(1,3,figsize=(170/25.4,86/25.4),
                          gridspec_kw={'width_ratios':[1,1.22,1.15]})
    fig.subplots_adjust(left=.065,right=.965,bottom=.16,top=.88,wspace=.50)
    for ax,group,title,lim,panel in zip(axes,groups,['ISCAS89','ITC-99','PicoRV32'],[.65,3,1.35],'abc'):
        valid=[]
        for row in group:
            base,final=row['baseline_wns'],row['final_wns']
            # The archived register bank has no setup path; preserve it as N/A.
            applicable=row['circuit']!='picorv32_regs'
            gain=round(final-base,8) if applicable else None
            rows.append({'family':'B','circuit':row['circuit'],'baseline_wns_ns':base,
                         'final_wns_ns':final,'gain_ns':gain,'applicable':applicable})
            if applicable:
                assert np.isfinite(gain) and gain>=-1e-8
                valid.append((row['circuit'],gain))
        y=np.arange(len(valid))
        gains=[v for _,v in valid]
        labels=[c.replace('picorv32_pcpi_mul','PCPI mul').replace('picorv32','主核') for c,_ in valid]
        ax.hlines(y,0,gains,color=BLUE,lw=2)
        for yy,gain in zip(y,gains):
            ax.plot(gain,yy,'o' if gain>0 else 's',color=BLUE if gain>0 else GREY,ms=3.6)
            ax.text(gain+lim*.035,yy,f'{gain:+.2f}',va='center',fontsize=7)
        ax.set_yticks(y,labels)
        ax.set_xlim(-lim*.02,lim)
        ax.set_ylim(len(valid)-.35,-.75)
        ax.set_xlabel('ΔWNS (ns)')
        ax.set_title(f'{title} · {sum(v>0 for v in gains)}/{len(gains)}',loc='left',fontsize=8,pad=7)
        ax.text(-.15,1.05,panel,transform=ax.transAxes,weight='bold',fontsize=8)
        ax.axvline(0,color=GREY,lw=.5)
        ax.grid(axis='x',color='#D9DEE4',lw=.5,ls=':')
        if title=='PicoRV32':
            ax.text(.03,.10,'regs：无 setup 路径\nN/A，不计入分母',transform=ax.transAxes,fontsize=7,color=GREY)
    csv_out('fig4_unified_gain_r21',rows)
    export(fig,'fig4_unified_gain_r21')


def physical_transfer():
    pre=load('experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json')
    post=load('experiments/20260807_real_pr_iscas8/post_route_audit_summary.json')
    premap={(r['circuit'],r['variant']):r['wns'] for r in pre['records']}
    rows=[]
    for r in post['records']:
        gain=premap[r['circuit'],'fixed']-premap[r['circuit'],'baseline']
        assert abs(r['fixed']-r['baseline']-r['delta'])<1e-8
        rows.append({'circuit':r['circuit'],'pre_gain_ns':round(gain,8),'route_gain_ns':r['delta'],
                     'pre_family':'A','physical_family':'A_prime'})
    assert len(rows)==8
    fig,ax=plt.subplots(figsize=(80/25.4,68/25.4))
    fig.subplots_adjust(left=.20,right=.965,bottom=.18,top=.81)
    y=np.arange(8)
    ax.barh(y-.17,[r['pre_gain_ns'] for r in rows],height=.28,color='#ACB5C0',label='预布局理想线网')
    ax.barh(y+.17,[r['route_gain_ns'] for r in rows],height=.28,
            color=[ORANGE if r['route_gain_ns']<0 else BLUE for r in rows],label='全局布线寄生估计')
    for yy,r in zip(y,rows):
        v=r['route_gain_ns']
        ax.text(v+(.006 if v>=0 else -.006),yy+.17,f'{v:+.2f}',ha='left' if v>=0 else 'right',va='center',fontsize=7)
        if v==0: ax.plot(0,yy+.17,'D',ms=3,color=GREY)
    ax.set(yticks=y,yticklabels=[r['circuit'] for r in rows],xlim=(-.06,.185),ylim=(7.7,-.8),xlabel='修复网表相对基线的 ΔWNS (ns)')
    ax.axvline(0,color=INK,lw=.6)
    ax.grid(axis='x',ls=':',color='#D9DEE4',lw=.5)
    ax.legend(loc='lower left',bbox_to_anchor=(-.2,1.015),frameon=False)
    csv_out('fig6_physical_transfer_r21',rows)
    export(fig,'fig6_physical_transfer_r21')


def s_boundary():
    report=load('experiments/20260928_s_l1_ablation/aggregation/summarize_s_l1.json')
    pair=load('experiments/20260928_s_l1_ablation/aggregation/s_ablation_summary_l1.json')
    rows=[]
    for c,r in report['circuits'].items():
        if r['n_candidate']==0:
            assert r['n_measured']==0 and r['n_extracted']==0
            tier={'dl_sky130_pos':0,'dwns_pos':0,'dwns_zero':0,'dwns_neg':0}
        else:
            tier=r['tier2']
        rows.append({'circuit':c,'n_candidates':r['n_candidate'],'depth_reduced':tier['dl_sky130_pos'],
                     'wns_positive':tier['dwns_pos'],'wns_zero':tier['dwns_zero'],'wns_negative':tier['dwns_neg']})
        assert tier['dwns_pos']+tier['dwns_zero']+tier['dwns_neg']==r['n_candidate']
    assert sum(r['n_candidates'] for r in rows)==126
    assert sum(r['depth_reduced'] for r in rows)==76
    assert sum(r['wns_positive'] for r in rows)==0
    assert sum(r['wns_zero'] for r in rows)==36
    assert sum(r['wns_negative'] for r in rows)==90
    assert all(abs(float(v))<1e-8 for _,v in pair['paired_dwns'])
    fig,axes=plt.subplots(2,1,figsize=(80/25.4,94/25.4))
    fig.subplots_adjust(left=.17,right=.975,bottom=.11,top=.87,hspace=1.0)
    x=np.arange(8)
    n=np.array([r['n_candidates'] for r in rows])
    dep=np.array([r['depth_reduced'] for r in rows])
    axes[0].bar(x-.17,n,.30,color='#B4BDC7',label='实测候选数')
    axes[0].bar(x+.17,dep,.30,color=BLUE,label='映射后逻辑深度降低')
    for xx,nn,dd in zip(x,n,dep):
        axes[0].text(xx-.17,nn+.7,str(nn),ha='center',fontsize=7)
        axes[0].text(xx+.17,dd+.7,str(dd),ha='center',fontsize=7,color=BLUE)
    zero=np.array([r['wns_zero'] for r in rows])
    neg=np.array([r['wns_negative'] for r in rows])
    axes[1].bar(x,neg,.55,color=ORANGE,label='WNS 下降（90）')
    axes[1].bar(x,zero,.55,bottom=neg,color='#B4BDC7',label='WNS 不变（36）')
    for xx,nn in zip(x,n): axes[1].text(xx,nn+.7,str(nn),ha='center',fontsize=7)
    for ax,label in zip(axes,'ab'):
        ax.set_xticks(x,[r['circuit'] for r in rows],rotation=40,ha='right',rotation_mode='anchor')
        ax.set_ylim(0,39)
        ax.set_ylabel('候选数')
        ax.set_yticks([0,10,20,30])
        ax.grid(axis='y',color='#E3E7EB',lw=.5,ls=':')
        ax.set_axisbelow(True)
        ax.legend(loc='lower left',bbox_to_anchor=(-.02,1.05),frameon=False,ncol=1,fontsize=7)
        ax.text(-.12,1.10,label,transform=ax.transAxes,weight='bold',fontsize=8)
    fig.text(.59,.51,'WNS 改善：0 / 126',ha='center',fontsize=7.5,color=BLUE)
    csv_out('fig7_s_boundary_r21',rows)
    export(fig,'fig7_s_boundary_r21')


def budget_curves():
    """Same-runner archive, with every seed and natural stopping point visible."""
    circuits=['s27','s382','s420','s641','s713','s820','s832','s953']
    arms=['fixed','adaptive','random_s1','random_s2','random_s3']
    rows=[]
    audit_rows=[]
    fig,axes=plt.subplots(2,4,figsize=(170/25.4,94/25.4))
    fig.subplots_adjust(left=.08,right=.975,bottom=.14,top=.82,wspace=.43,hspace=.60)
    styles={'fixed':(BLUE,'-',1.5),'adaptive':('#33404E','--',.8),
            'random_s1':('#C7B3A1','-',.7),'random_s2':('#B0947A','-',.7),'random_s3':(ORANGE,':',.9)}
    labels=['固定权重','EMA 自适应','随机种子 1','随机种子 2','随机种子 3']
    handles=[]
    for ax,c in zip(axes.flat,circuits):
        ends=[]
        base_config=None
        for arm,label in zip(arms,labels):
            result=load(f'experiments/20260924_threearm/{arm}/{c}/outerloop_result.json')
            ledger=load(f'experiments/20260924_threearm/{arm}/{c}/eval_trials.json')
            config=load(f'experiments/20260924_threearm/{arm}/{c}/run_config.json')
            assert config['resolved_args']['sta_budget']==500
            comparable_keys=['period','max_iterations','candidates_per_iteration','joint_k',
                             'joint_enumerate_depth','strategies','tns_aware','early_stop',
                             'physical_gate','enable_buffer']
            current_config={key:config['resolved_args'][key] for key in comparable_keys}
            if base_config is None: base_config=current_config
            assert current_config==base_config,(c,arm,current_config,base_config)
            measured=[]
            provenance_count=0
            cache_count=0
            best=0.0
            for trial_index,trial in enumerate(ledger['trials'],1):
                if not trial.get('sta_provenance'):
                    continue
                provenance_count+=1
                if trial.get('skipped_duplicate',False):
                    cache_count+=1
                    continue
                value=float(trial['wns'])
                assert np.isfinite(value)
                best=max(best,value-float(result['baseline_wns']))
                measured.append((trial_index,best))
            curve=np.asarray([value for _,value in measured],dtype=float)
            assert len(curve)>0 and np.all(np.diff(curve)>=-1e-9)
            assert abs(curve[-1]-(result['wns_history'][-1]-result['baseline_wns']))<1e-8
            assert provenance_count-cache_count==len(curve)
            audit_rows.append({'circuit':c,'arm':arm,'all_trials':len(ledger['trials']),
                               'provenance_records':provenance_count,'cache_reuse':cache_count,
                               'actual_sta':len(curve)})
            x=np.arange(1,len(curve)+1)
            color,ls,lw=styles[arm]
            handle=ax.step(np.r_[0,x],np.r_[0,curve],where='post',color=color,ls=ls,lw=lw,label=label,
                           zorder=4 if arm=='fixed' else 5 if arm=='adaptive' else 2)[0]
            ax.plot(x[-1],curve[-1],'o',ms=2,color=color,zorder=6)
            if c==circuits[0]: handles.append(handle)
            rows.extend({'circuit':c,'arm':arm,'actual_sta_index':int(k),
                         'trial_record_index':int(record),'best_gain_ns':float(v)}
                        for k,(record,v) in zip(x,measured))
            ends.append((arm,float(curve[-1])))
        assert abs(ends[0][1]-ends[1][1])<1e-8
        ax.set_title(c,loc='left',fontsize=8,pad=4)
        ax.set_ylim(bottom=0)
        ax.grid(color='#E0E5E9',lw=.45,ls=':')
        ax.tick_params(labelsize=7)
    for ax in axes[:,0]: ax.set_ylabel('B(k) (ns)')
    for ax in axes[-1,:]: ax.set_xlabel('STA 测量序号 k')
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.995),ncol=3,frameon=False,fontsize=7)
    csv_out('fig5_budget_curves_r21',rows)
    csv_out('fig5_sta_count_audit_r21',audit_rows)
    counts={arm:sum(r['actual_sta'] for r in audit_rows if r['arm']==arm) for arm in arms}
    assert counts=={'fixed':1947,'adaptive':2003,'random_s1':2439,'random_s2':2476,'random_s3':2527},counts
    export(fig,'fig5_budget_curves_r21')


if __name__=='__main__':
    method_flow()
    mechanisms()
    unified_results()
    physical_transfer()
    s_boundary()
    budget_curves()
    (SPEC/'r21_source_manifest.json').write_text(json.dumps(sources,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
