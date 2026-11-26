#!/usr/bin/env python3
"""Save the already-completed asap7_aes::fixed_boxed arm into WINDOWED_ABLATION_VERIFIED.json."""
import hashlib, json
from pathlib import Path

p = Path("/home/toylog/faeco_v4_windowed_ablation_20261126_v1/asap7_aes/fixed_boxed/cell_01/fixed")
prog = json.loads((p / "progress.json").read_text())
summ = json.loads((p / "summary.json").read_text())
cps = prog["checkpoints"]
ref_area = 1181.81106
pool_ceil = 1.76418
best_a = 0.0
pts = [(0.0, 0.0)]
for cp in sorted(cps, key=lambda c: c["elapsed_seconds"]):
    t = float(cp["elapsed_seconds"])
    if t <= 720.0 and cp.get("accepted"):
        s = ref_area - float(cp["endpoint"]["area"])
        if s > best_a:
            best_a = s
            pts.append((t, best_a))
pts.append((720.0, best_a))
auc = sum(max(0.0, t1 - t0) * v0 for (t0, v0), (t1, _) in zip(pts, pts[1:])) / 720.0
best_gates = max((len(r["actions"]) for r in prog["logical_requests"] if r.get("failures") == []), default=0)
diag_secs = [json.loads(dj.read_text())["seconds"] for dj in sorted((p / "diagnosis").glob("*/diagnosis.json"))]

# Also verify unlocked_drc and sec_pass from request 02
ud_path = p / "02/initial/unlocked_drc/audit.json"
unlocked_drc = json.loads(ud_path.read_text()).get("drc_markers") if ud_path.is_file() else None
best_sec = any(cp.get("accepted") and cp["endpoint"].get("sec_pass") for cp in cps)

row = {
    "design": "asap7_aes",
    "mode": "fixed_boxed",
    "diagnosis": "boxed_1.0_Hrow",
    "base_area_um2": ref_area,
    "pool_ceiling_um2": pool_ceil,
    "qualified_area_saved_um2": best_a,
    "qualified_gates": best_gates,
    "area_saved_pct": 100.0 * best_a / ref_area,
    "pool_capture_pct": 100.0 * best_a / pool_ceil,
    "anytime_auc_um2": auc,
    "first_target_s": summ["window"]["time_to_target_seconds"],
    "logical_finished": summ["logical_finished"],
    "logical_admitted": summ["logical_admitted"],
    "diag_calls": len(diag_secs),
    "diag_mean_s": sum(diag_secs) / len(diag_secs) if diag_secs else None,
    "unlocked_drc_markers": unlocked_drc,
    "sec_pass": best_sec,
    "checkpoints": [
        {
            "elapsed_s": cp["elapsed_seconds"],
            "accepted": cp["accepted"],
            "area_saved_um2": ref_area - cp["endpoint"]["area"],
        }
        for cp in cps
    ],
    "run_dir": str(p.parent.parent),
}
out_p = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/tcad_v4_revision_20261126/WINDOWED_ABLATION_VERIFIED.json")
d = json.loads(out_p.read_text())
d["arms"]["asap7_aes::fixed_boxed"] = row
out_p.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
print("Saved asap7_aes::fixed_boxed! SHA-256:", hashlib.sha256(out_p.read_bytes()).hexdigest())
for k, v in d["arms"].items():
    print(f"  {k:38s}: area={v['qualified_area_saved_um2']:.6f} ({v['qualified_gates']}g, {v['pool_capture_pct']:.1f}%), AUC={v['anytime_auc_um2']:.4f}, diag_mean={v['diag_mean_s']:.2f}s, drc={v['unlocked_drc_markers']}, sec={v['sec_pass']}")
