import sys, json
sys.path.insert(0, r"D:/BaiduSyncdisk/03_FAECO/scripts")
sys.path.insert(0, r"D:/BaiduSyncdisk/03_FAECO/src")
from pathlib import Path
from run_sequential_timing_check import run_opensta
from run_outerloop_real_wns import parse_critical_instances
import rseco.real_wns as rw
ROOT = Path(r"D:/BaiduSyncdisk/03_FAECO")
mapped = ROOT / "experiments/20260806_b19_067_repair/b19/mapped.v"
out = ROOT / "experiments/20260806_b19_067_repair/b19"
mapped_text = mapped.read_text(encoding="utf-8", errors="replace")
LIB = ROOT / "benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
lib_text = LIB.read_text(encoding="utf-8", errors="replace")
base = run_opensta(mapped, 17.04, out)
crit = parse_critical_instances((out/"sta.log").read_text(encoding="utf-8", errors="replace"))
print("baseline:", base["wns"], "crit:", len(crit))
ev = rw.RealWnsEvaluator(
    mapped_text=mapped_text, top_module="b19", period=17.04,
    liberty_text=lib_text, baseline_wns=base["wns"],
    output_dir=out/"eval", critical_instances=crit, workers=4,
    strategy_filter=("R","G","B"), joint_enumerate_depth=3,
    max_instances=8, clock_port="CK")
class P:
    gates = list(crit[:8])
    patch_id = "critical_path_cover"
weights = {"boundary_penalty": 1.0, "size_penalty": 1.0, "critical_coverage_reward": 1.0}
res = ev(P, weights)
print("eval result:", {k: res[k] for k in ("wns","improved","accepted","instance","kind","to_type") if k in res})
ev.write_trials(out/"eval_trials.json")
print("trials written")