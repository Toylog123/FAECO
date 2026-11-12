"""Run only after root preregistration/go; no routing or source changes."""
import hashlib,json,pathlib,subprocess,time
root=pathlib.Path(__file__).resolve().parents[2]; out=root/'scratch/recovery_repair_pathdiag'
manifest_path=out/'manifest.json';m=json.loads(manifest_path.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save():manifest_path.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
for arm,entry in m['arms'].items():
 for p,h in entry['inputs'].items():
  if sha(root/p)!=h:raise ValueError('Input changed: '+p)
 script=root/entry['script']
 if sha(script)!=entry['script_sha256']:raise ValueError('Script changed')
 log=out/(arm+'.log')
 if log.exists():raise ValueError('Refusing existing log '+str(log))
 wsl='/mnt/'+script.drive[0].lower()+script.as_posix()[2:]
 argv=['wsl.exe','-d','Ubuntu','--','/usr/bin/timeout','--kill-after=10s','300s','/usr/local/bin/sta','-no_splash','-exit',wsl]
 entry['run']={'argv':argv,'status':'running'};save();start=time.monotonic()
 with log.open('wb') as stream:
  try:p=subprocess.run(argv,stdout=stream,stderr=subprocess.STDOUT,timeout=325);rc=p.returncode
  except subprocess.TimeoutExpired:rc=124
 raw=log.read_text(errors='replace')
 entry['run'].update(status='complete',returncode=rc,elapsed_s=time.monotonic()-start,log_sha256=sha(log),sentinel='PATHDIAG_DONE' in raw,errors=[line for line in raw.splitlines() if line.startswith('Error')])
 save();print(arm,entry['run'],flush=True)
 if rc or not entry['run']['sentinel'] or entry['run']['errors']:raise SystemExit(1)
m['status']='two_sta_diagnostics_complete';save()
