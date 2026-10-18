"""Two-circuit pilot preview: exact gains and STA costs, no coordinate jitter.

Style-only reuse of the established manuscript palette. All 18 verified jobs
are retained in CSV; identical plotted coordinates list every member arm.
"""
import argparse,csv,hashlib,json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[5]
ARMS=('W0','W1','U0','U1','C','UR1','UR2','UR3','L')
BLUE,ORANGE,GREY='#245B9E','#C77435','#8C949D'
mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
    'font.size':7.5,'axes.labelsize':7.5,'xtick.labelsize':7,'ytick.labelsize':7,
    'axes.linewidth':.6,'axes.spines.top':False,'axes.spines.right':False,
    'svg.fonttype':'none','pdf.fonttype':42,'figure.facecolor':'white',
    'savefig.facecolor':'white','savefig.dpi':600})

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    source=ROOT/'project_docs/evidence/r22_cprime_v3_20261016/PILOT_AUDIT_18.json'
    audit=json.loads(source.read_text(encoding='utf-8'))
    assert audit['all_pilot_verified'] and audit['completed_and_verified']==18
    assert audit['source_stable']
    observed={(row['circuit'],row['arm']) for row in audit['jobs']}
    assert len(audit['jobs'])==18 and observed=={(c,a) for c in ('s27','s382') for a in ARMS}
    rows=[]
    for row in audit['jobs']:
        assert row['sec_proven_points']>0 and row['sec_unproven_points']==0
        gain=float((Decimal(str(row['final_wns']))-Decimal(str(row['baseline_wns'])))*1000)
        assert row['total_sta_process_attempts']==row['candidate_ideal_sta_launches']+row['baseline_sta_process_attempts']
        rows.append({'circuit':row['circuit'],'arm':row['arm'],
            'seed':int(row['arm'][-1]) if row['arm'].startswith('UR') else '',
            'baseline_wns_ns':row['baseline_wns'],'final_wns_ns':row['final_wns'],
            'wns_gain_ps':gain,'candidate_ideal_sta':row['candidate_ideal_sta_launches'],
            'baseline_sta':row['baseline_sta_process_attempts'],'total_sta':row['total_sta_process_attempts'],
            'retained_commits':row['retained_commits'],'completion_sha256':row['completion_sha256'],
            'source_head':audit['head']})
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    stem='r22_pilot_source_cost'
    with (out/(stem+'.csv')).open('x',encoding='utf-8-sig',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    fig,axes=plt.subplots(1,2,figsize=(170/25.4,72/25.4),sharex=True,sharey=True)
    fig.subplots_adjust(left=.105,right=.98,bottom=.22,top=.86,wspace=.20)
    groups_report={};annotations=[]
    for index,(ax,circuit) in enumerate(zip(axes,('s27','s382'))):
        groups=defaultdict(list)
        for row in rows:
            if row['circuit']==circuit:groups[(row['total_sta'],row['wns_gain_ps'])].append(row['arm'])
        groups_report[circuit]=[]
        positives=sorted((xy,names) for xy,names in groups.items() if xy[1]>0)
        for (x,y),names in sorted(groups.items()):
            color=ORANGE if names==['L'] else GREY if y==0 else BLUE
            ax.scatter([x],[y],s=24,marker='s' if names==['L'] else 'o',
                       c=color,edgecolors='white',linewidths=.45,zorder=3)
            if y==0:offset=(8,10);align='left'
            elif names==['L']:offset=(7,-15);align='left'
            else:
                rank=next(i for i,(xy,_) in enumerate(positives) if xy==(x,y))
                if len(names)>1:offset=(-4,18);align='center'
                elif rank==0:offset=(-8,-18);align='right'
                elif rank%2:offset=(12,-18);align='left'
                else:offset=(9,18);align='left'
            text='/'.join(names)
            annotation=ax.annotate(text,(x,y),xytext=offset,textcoords='offset points',
                ha=align,va='center',fontsize=7.2,color=color,
                arrowprops={'arrowstyle':'-','color':color,'lw':.5,'shrinkA':2,'shrinkB':3})
            annotations.append((ax,annotation))
            groups_report[circuit].append({'total_sta':x,'gain_ps':y,'arms':names})
        ax.set(xlim=(0,150),ylim=(-18,190),xticks=(0,50,100,150),yticks=(0,50,100,150))
        ax.axhline(0,color='#D6DADF',lw=.6,zorder=0)
        ax.set_xlabel('Total STA invocations')
        ax.text(0,1.08,chr(97+index),transform=ax.transAxes,fontweight='bold',fontsize=9)
        ax.text(.50,1.08,circuit,transform=ax.transAxes,ha='center',fontsize=8)
    axes[0].set_ylabel('WNS gain over initial netlist (ps)')
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    collisions=[]
    for i,(ax,annotation) in enumerate(annotations):
        box=annotation.get_window_extent(renderer)
        if not fig.bbox.contains(box.x0,box.y0) or not fig.bbox.contains(box.x1,box.y1):
            collisions.append({'type':'outside_canvas','label':annotation.get_text()})
        for other_ax,other in annotations[:i]:
            if other_ax is ax and box.overlaps(other.get_window_extent(renderer)):
                # Annotation extents include their separate connector segments;
                # this conservative flag is reviewed against the rendered panel.
                collisions.append({'type':'annotation_extent_overlap','labels':[other.get_text(),annotation.get_text()]})
    for suffix in ('pdf','svg','png'):
        fig.savefig(out/(stem+'.'+suffix),format=suffix,dpi=600)
    plt.close(fig)
    qa={'status':'pilot preview; no manuscript insertion','source_audit_sha256':sha(source),
        'plotter_sha256':sha(Path(__file__)),'source_head':audit['head'],'observations':len(rows),
        'excluded_observations':0,'groups':groups_report,'jitter_applied':False,
        'coordinate_transform':'ps = 1000 * (final WNS ns - initial WNS ns); no normalization',
        'statistics':'individual runs, no seed averages or inferential intervals',
        'dimensions_mm':[170,72],'minimum_configured_font_pt':7,'render_flags':collisions,
        'visual_review':'pending','files':{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
    with (out/'QA.json').open('x',encoding='utf-8') as file:json.dump(qa,file,ensure_ascii=False,indent=2)
    print(json.dumps({'output':str(out),'rows':len(rows),'render_flags':collisions},ensure_ascii=False))

if __name__=='__main__':main()
