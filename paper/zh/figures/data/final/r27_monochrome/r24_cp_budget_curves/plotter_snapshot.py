"""All72 C-prime committed-gain curves; no search/STA, natural stops retained."""
import argparse,csv,hashlib,importlib.util,json,shutil
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
CIRCUITS=['s27','s382','s420','s641','s713','s820','s832','s953']
ARMS=['W0','W1','U0','U1','C','UR1','UR2','UR3','L']
mpl.rcParams.update({'font.family':'sans-serif',
    'font.sans-serif':['Microsoft YaHei','SimHei','Arial','DejaVu Sans'],
    'axes.unicode_minus':False,'font.size':7.5,'axes.labelsize':7.5,
    'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,'axes.linewidth':.6,
    'axes.spines.top':False,'axes.spines.right':False,
    'svg.fonttype':'none','pdf.fonttype':42,'savefig.dpi':600,
    'figure.facecolor':'white','savefig.facecolor':'white'})
STYLES={'W0':('#727272',':',.9,'s'),'W1':('#3B3B3B','-',1.3,'o'),
    'C':('#626262','--',1.0,'D'),'UR1':('#8A8A8A','--',.8,'v'),
    'UR2':('#8A8A8A',':',.8,'^'),'UR3':('#8A8A8A','-.',.8,'>'),
    'L':('#727272','-.',.9,'p')}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--curve-audit-dir',type=Path,default=ROOT/'paper/zh/figures/data/previews/r24_cp_curve_audit_v1')
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--alignment-auditor',type=Path,required=True)
    args=ap.parse_args();src=args.curve_audit_dir.resolve()
    audit=json.loads((src/'CURVE_RECONSTRUCTION_AUDIT.json').read_text(encoding='utf-8'))
    assert sha(src/'CURVE_RECONSTRUCTION_AUDIT.json')=='77b1ecff89b023759c99da2e8b1ff9c08b53579924a96745c52625ae7556d471'
    assert sha(src/'SOURCE_BINDING.json')=='48694ea14d4c08ca7004bb355361269372c85da225e41885c911805a3f28c272'
    original_binding=json.loads((src/'SOURCE_BINDING.json').read_text(encoding='utf-8'))
    for name,digest in original_binding['plot_data'].items():
        assert sha(src/name)==digest
    assert audit['total_candidate_sta']==6858 and audit['total_retained_commits']==192 and len(audit['checks'])==72
    rows=list(csv.DictReader((src/'CANDIDATE_STA_COMMITTED_CURVES.csv').open(encoding='utf-8-sig')))
    series=defaultdict(list)
    for r in rows:series[r['circuit'],r['arm']].append((int(r['k']),float(r['committed_gain_ns'])))
    assert len(series)==72 and len(rows)==6930
    checks={(r['circuit'],r['arm']):r for r in audit['checks']}
    for key,points in series.items():
        c=checks[key]
        assert points[0]==(0,0.0) and len(points)==c['candidate_sta']+1
        assert [k for k,v in points]==list(range(c['candidate_sta']+1))
        assert points[-1]==(c['candidate_sta'],c['endpoint_gain_ns'])
        assert all(a[1]<=b[1] for a,b in zip(points,points[1:]))
    for c in CIRCUITS:
        assert series[c,'W0']==series[c,'U0'] and series[c,'W1']==series[c,'U1']
    groups=audit['complete_curve_equality_groups']
    for group in groups:
        names=group['identical_complete_curve_arms'];base=series[group['circuit'],names[0]]
        assert all(series[group['circuit'],a]==base for a in names)
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    for name in ['CANDIDATE_STA_COMMITTED_CURVES.csv','COMMIT_EVENTS.csv','CURVE_RECONSTRUCTION_AUDIT.json']:
        shutil.copyfile(src/name,out/name)
    shutil.copyfile(src/'SOURCE_BINDING.json',out/'RECONSTRUCTION_SOURCE_BINDING.json')
    dump(out/'FIGURE_CONTRACT.json',{'question':'C′各区域政策在逐次真实候选STA预算下何时提交收益并停止？',
        'claim':'收益轨迹必须结合实际测量成本和自然停止点解释；weighted/uniform全程重合，局部不利比较保留。',
        'archetype':'quantitative grid','backend':'Python/matplotlib','physical_size_mm':[170,108],
        'observations':'8circuits×9arms; all6858 actualSTA and192 explicit commits',
        'curve_definition':audit['policy'],'overlap':'merge only identical complete(k,B)arrays including stop; list all72 membership',
        'uncertainty':'individual runs/seeds only, no aggregation/error bars/significance','new_eda':False})
    fig,axes=plt.subplots(2,4,figsize=(6.6929133858,4.2519685039))
    fig.subplots_adjust(left=.08,right=.975,bottom=.13,top=.80,wspace=.56,hspace=.64)
    plotted=[]
    for index,(ax,c) in enumerate(zip(axes.flat,CIRCUITS)):
        local=[g for g in groups if g['circuit']==c]
        # Draw secondary alternatives first; W1 is visible on top of crossings.
        local.sort(key=lambda g:('W1' in g['identical_complete_curve_arms']))
        for group in local:
            members=group['identical_complete_curve_arms']
            representative='W1' if 'W1' in members else 'W0' if 'W0' in members else members[0]
            points=series[c,representative];color,ls,lw,marker=STYLES[representative]
            ax.step([k for k,v in points],[v for k,v in points],where='post',
                color=color,ls=ls,lw=lw,zorder=5 if representative=='W1' else 3)
            ax.plot(points[-1][0],points[-1][1],marker=marker,ms=2.8,color=color,
                markerfacecolor='white' if representative in ['C','L'] else color,
                markeredgewidth=.7,zorder=7,linestyle='none')
            plotted.append({'circuit':c,'representative':representative,'covered_arms':members,
                'k_stop':points[-1][0],'gain_stop_ns':points[-1][1],
                'series_sha256':group['series_sha256']})
        xmax=max(series[c,a][-1][0] for a in ARMS)
        ymax=max(series[c,a][-1][1] for a in ARMS)
        ax.set_xlim(-.025*xmax,1.06*xmax)
        ax.set_ylim(-.04*max(.02,ymax),1.10*max(.02,ymax))
        ax.xaxis.set_major_locator(MaxNLocator(nbins=3,integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=3))
        ax.tick_params(labelsize=7,length=2,pad=2)
        ax.set_title(c,loc='left',fontsize=7.5,pad=6)
        ax.text(-.20,1.08,chr(97+index),transform=ax.transAxes,fontsize=8,fontweight='bold')
    for ax in axes[:,0]:ax.set_ylabel('B(k) (ns)',fontsize=7.5,labelpad=3)
    for ax in axes[-1,:]:ax.set_xlabel('候选 STA 序号 k',fontsize=7,labelpad=3)
    handles=[];labels=[]
    for a,label in [('W0','W0 = U0'),('W1','W1 = U1'),('C','C'),('UR1','UR1'),('UR2','UR2'),('UR3','UR3'),('L','L')]:
        color,ls,lw,marker=STYLES[a]
        handles.append(Line2D([],[],color=color,ls=ls,lw=lw,marker=marker,ms=2.8,
            markerfacecolor='white' if a in ['C','L'] else color,markeredgewidth=.7));labels.append(label)
    handles.append(Line2D([],[],ls='none'));labels.append('完全重合曲线合并')
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.995),ncol=4,
        frameon=False,fontsize=7,handlelength=2.2,columnspacing=1.7,labelspacing=.7)
    spec=importlib.util.spec_from_file_location('alignment',args.alignment_auditor)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    helper.require_matplotlib_panel_alignment(fig,axes=list(axes.flat),panel_ids=list('abcdefgh'),
        row_groups=[list('abcd'),list('efgh')],column_groups=[list(x) for x in ['ae','bf','cg','dh']],
        require_panel_labels=True,json_out=out/'PANEL_ALIGNMENT.json',overlay_svg=out/'PANEL_ALIGNMENT_OVERLAY.svg')
    renderer=fig.canvas.get_renderer()
    dump(out/'PANEL_CONTENT_BOXES.json',{'coordinate_system':'Matplotlib bottom-left points',
        'figure_height_pt':fig.get_size_inches()[1]*72,
        'panels':{label:[float(v)*72/fig.dpi for v in ax.get_tightbbox(renderer).extents]
                  for label,ax in zip('abcdefgh',axes.flat)}})
    stem='r24_cp_budget_curves'
    fig.savefig(out/f'{stem}.pdf',format='pdf')
    fig.savefig(out/f'{stem}.svg',format='svg')
    fig.savefig(out/f'{stem}.png',format='png',dpi=600)
    plt.close(fig)
    dump(out/'PLOTTED_CURVE_GROUPS.json',{'original_curves':72,'plotted_complete_curves':len(plotted),
        'data_excluded':0,'groups':plotted})
    shutil.copyfile(__file__,out/'plotter_snapshot.py')
    shutil.copyfile(ROOT/'paper/zh/figures/data/scripts/audit_r24_cp_budget_curves.py',out/'reconstructor_snapshot.py')
    shutil.copyfile(args.alignment_auditor,out/'alignment_auditor_snapshot.py')
    dump(out/'SOURCE_BINDING.json',{'curve_audit_sha256':sha(src/'CURVE_RECONSTRUCTION_AUDIT.json'),
        'matrix_audit_sha256':audit['audit_sha256'],'plotter_sha256':sha(__file__),
        'all_data_and_exports':{p.name:sha(p) for p in out.iterdir() if p.is_file()}})
    print(json.dumps({'output':str(out),'source_curves':72,'rendered_exact_groups':len(plotted),'source_points':len(rows)}))


if __name__=='__main__':main()
