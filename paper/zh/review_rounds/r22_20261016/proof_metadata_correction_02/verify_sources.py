"""Read-only A proof metadata verification for a bilingual patch proposal."""
from pathlib import Path
import csv, hashlib, io, json, re

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent/'actual_verification'
OUT.mkdir(exist_ok=False)
manifest = {}
def read(path):
    path = ROOT/path
    data = path.read_bytes()
    manifest[path.relative_to(ROOT).as_posix()] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    return data.decode('utf-8-sig')
def load(path):
    return json.loads(read(path))
def top(text, name):
    found = re.search(r'\bmodule\s+'+name+r'\b[\s\S]*?\bendmodule', text)
    assert found
    return '\n'.join(line.strip() for line in found.group().splitlines() if line.strip())

zh = Path('paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex')
en = Path('paper/en/manuscript/FAECO.tex')
manuscripts = {str(path): read(path) for path in (zh,en)}
read('paper/zh/review_rounds/r22_20261016/CLAIM_REPLACEMENT_MAP.md')
load('paper/zh/review_rounds/r22_20261016/CLAIM_REPLACEMENT_MAP.json')
base = Path('project_docs/evidence/r22_a_sec_20261016_frozen')
load(base/'input_manifest.json')
load(base/'OBJECT_BINDING_VERIFICATION.json')
load(base/'TRISTATE_IMPACT_CHECK.json')
rows = []
for circuit in ['s382','s420','s641','s713','s832','s953']:
    folder = base/'proofs'/circuit
    receipt = load(folder/'receipt.json')
    for name, expected in receipt['artifacts'].items():
        read(folder/name)
        assert manifest[(folder/name).as_posix()]['sha256'] == expected, (circuit,name)
    result = load(folder/'result.json')
    log = read(folder/'sec.log')
    script = read(folder/'sec.ys')
    counts = re.findall(r'Of those cells\s+(\d+) are proven and\s+(\d+) are unproven', log)
    assert counts and int(counts[-1][0])>0 and int(counts[-1][1])==0
    assert result['status']=='pass' and result['returncode']==0 and 'equiv_status -assert' in script
    rows.append({'circuit':circuit,'batch':'P1','proven':int(counts[-1][0]),'unproven':0,
                 'runtime_s':result['runtime_s'],'runtime_source':str(folder/'result.json'),
                 'source_pin':receipt['source_pin']['head'],
                 'script':str(folder/'sec.ys'),'log':str(folder/'sec.log'),
                 'gold_input':receipt['gold'],'gate_input':receipt['gate'],
                 'artifacts_sha_verified':True})
old=load('project_docs/evidence/r22_historical_correctness_20261014/correctness_audit.json')
summary = list(csv.DictReader(io.StringIO(read('experiments/20260826_sec/summary.csv'))))
for circuit in ['s27','s820']:
    a=next(r for r in old['runs'] if r['family']=='A' and r['circuit']==circuit)
    b=next(r for r in old['runs'] if r['family']=='B' and r['circuit']==circuit)
    sec=b['sec'];script=read(sec['script']);log=read(sec['log'])
    gold=read(sec['gold_file']);gate=read(sec['gate_file'])
    ainitial=read(Path(a['run'].replace('\\','/'))/'mapped.v');afinal=read(a['final_source'].replace('\\','/'))
    state=load(Path(b['run'].replace('\\','/'))/'outerloop_result.json')['state']
    assert top(gold,circuit)==top(ainitial,circuit)
    assert top(gate,circuit)==top(afinal,circuit)==top(state['current_netlist_text'],circuit)
    assert hashlib.sha256(state['current_netlist_text'].encode()).hexdigest()==state['current_netlist_hash']
    counts=re.findall(r'Of those cells\s+(\d+) are proven and\s+(\d+) are unproven',log)
    assert counts and int(counts[-1][0])>0 and int(counts[-1][1])==0
    assert f'rename {circuit} gold' in script and f'rename {circuit} gate' in script
    assert 'equiv_make gold gate equiv' in script and 'prep -top equiv' in script
    summ=next(row for row in summary if row['circuit']==circuit)
    assert (int(summ['proven']),int(summ['unproven']))==tuple(map(int,counts[-1]))
    rows.append({'circuit':circuit,'batch':'P2','proven':int(counts[-1][0]),'unproven':0,
                 'recommended_main_table_runtime_s':None,'archived_summary_seconds':float(summ['seconds']),
                 'archived_summary_runtime_binding':'No per-invocation receipt recovered; not certified as the same timing procedure as P1',
                 'log_cpu_user_system_s':re.findall(r'CPU: user ([\d.]+)s system ([\d.]+)s',log),
                 'script':sec['script'],'log':sec['log'],'gold_file':sec['gold_file'],'gate_file':sec['gate_file'],
                 'A_initial_top_matches_gold_nonblank_lines':True,'A_final_top_matches_gate_nonblank_lines':True,
                 'gate_matches_actual_B_final_state':True,'state_hash_matches':True,
                 'equiv_status_assert':False})
rows.sort(key=lambda row: ['s27','s382','s420','s641','s713','s820','s832','s953'].index(row['circuit']))
for path, entry in manifest.items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==entry['sha256'],path
snippets={}
for path,text in manuscripts.items():
    lines=text.splitlines()
    snippets[path]=[{'line':i,'text':line} for i,line in enumerate(lines,1)
                    if ('tab:sec_iscas8' in line or re.search(r'^s(?:27|382|420|641|713|820|832|953)\s*&',line))]
(OUT/'VERIFIED_A_METADATA.json').write_text(json.dumps({'scope':'Only C03/C04 proof metadata/source proposal; no manuscript/source/Git/EDA mutation',
    'rows':rows,'manuscript_exact_locations':snippets,'read_sha_before_after_stable':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'READ_SHA_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':[(r['circuit'],r['batch'],r['proven'],r.get('runtime_s'),r.get('archived_summary_seconds')) for r in rows],
                  'read_files':len(manifest),'read_sha_stable':True},indent=2))
