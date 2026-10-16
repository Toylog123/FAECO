"""Recheck the exact archived F1 counterexample and legal size control."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'code/scripts'),str(ROOT/'code/src')]
import run_r22_cut_ablation as b
from rseco.logic_rewrite import parse_liberty_cells,equivalence_candidates
from rseco.real_wns import build_real_equivalence_checker
from rseco.gate_sizing import parse_mapped_netlist

def main():
    directory=Path(__file__).resolve().parent
    parser=argparse.ArgumentParser()
    parser.add_argument('--receipt',type=Path,default=directory/'SEQUENTIAL_GATE_VERIFICATION.json')
    args=parser.parse_args()
    old=directory/'SEQUENTIAL_GATE_COUNTEREXAMPLE.json'
    case=json.loads(old.read_text(encoding='utf-8'))
    source=b.source_manifest()
    text=b.LIB.read_text(encoding='utf-8')
    check=build_real_equivalence_checker(text)
    rejected=check(case['gold'],case['gate'])
    sizing=check(case['gold'],case['gold'].replace('dfrtp_1','dfrtp_2'))
    cells=parse_liberty_cells(text)
    candidates=equivalence_candidates(cells['sky130_fd_sc_hd__dfrtp_1'],cells)
    counts=[len(parse_mapped_netlist(case[role])) for role in ('gold','gate')]
    result=dict(source_manifest=source,liberty_sha256=b.sha(b.LIB),
                counterexample_sha256=b.sha(old),verifier_sha256=b.sha(Path(__file__)),
                reset_to_set_status=rejected.status,reset_to_set_reason=rejected.reason,
                legal_same_family_G_status=sizing.status,sequential_R_candidates=candidates,
                parsed_cell_counts=counts,
                eda_executed=False,source_stable=source==b.source_manifest())
    result['passed']=(result['source_stable'] and rejected.status=='fail' and sizing.status=='pass'
                      and not candidates and counts==[1,1] and 'sequential' in rejected.reason)
    target=args.receipt
    with target.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2)
    print(result['reset_to_set_status'],result['legal_same_family_G_status'],len(candidates),result['passed'])
    return 0 if result['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
