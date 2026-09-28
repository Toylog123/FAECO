"""三层裁决 + 固定指标集：L1 窗口来源杠杆（tech design §13.4）。

固定指标（用户 2026-09-28 裁定）：`windows_offered` **不得**作 L1 主证据（含重复扫描的割
边界）。本脚本固定产出 `N_unique_window`（按 `patch_id` 的 canonical 窗口哈希去重）、
`N_extracted`、`N_S candidate`、`N_measured`、`N_accepted` —— 后四个最关键。

三层（不得跳级）：
  Tier 1 enumeration : 非饱和电路 `N_S,L1 > N_S,old`（只证明枚举瓶颈被解除）
  Tier 2 candidate quality : R_S/CEC 通过率、`ΔWNS` 分布（若枚举涨而全 `ΔWNS≤0` ⇒
                             问题在 S transformation quality，不在 L1）
  Tier 3 repair capability : `N_accepted,S > 0` 且 ≥1 电路 `ΔWNS_on−off > 0`（决定 OI-014）

用法：
  python code/scripts/summarize_s_l1.py --root experiments/20260928_s_l1_ablation \
      [--baseline-root experiments/20260924_l3s_ablation] [--json-out out.json]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median

ALL8 = ("s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953")


def _load(p: Path) -> dict | None:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _budget(d: dict) -> dict:
    return ((d.get("state") or {}).get("budget") or {})


def tier2_for_circuit(on_root: Path, circ: str) -> dict | None:
    """复用 analyze_s_candidates 的并发基线重建，返回 ΔWNS 分布与深度交叉表。"""
    res = _load(on_root / circ / "outerloop_result.json")
    tj = _load(on_root / circ / "eval_trials.json")
    if res is None or tj is None:
        return None
    trials = tj.get("trials", tj) if isinstance(tj, dict) else tj
    baseline = res.get("baseline_wns")
    rows = []
    for t in trials:
        if t.get("kind") == "S":
            r = t.get("resynth") or {}
            db, da = r.get("depth_before_sky130"), r.get("depth_after_sky130")
            dwns = (None if (t.get("wns") is None or baseline is None)
                    else round(t["wns"] - baseline, 6))
            rows.append({
                "patch_id": t.get("patch_id"),
                "variant": r.get("variant"),
                "r_s_verdict": r.get("r_s_verdict"),
                "dl_blif": (None if (r.get("depth_before") is None
                                     or r.get("depth_after") is None)
                            else r["depth_before"] - r["depth_after"]),
                "dl_sky130": (None if (db is None or da is None) else db - da),
                "dwns": dwns,
            })
        if t.get("accepted") and t.get("wns") is not None:
            baseline = t["wns"]
    if not rows:
        return {"n": 0}
    dw = [r["dwns"] for r in rows if r["dwns"] is not None]
    return {
        "n": len(rows),
        "n_unique_window": len({r["patch_id"] for r in rows}),
        "n_variant_S0": sum(1 for r in rows if r["variant"] == "S0"),
        "rs_ok": sum(1 for r in rows if r["r_s_verdict"] == "ok"),
        "rs_soft": sum(1 for r in rows if r["r_s_verdict"] == "soft"),
        "rs_hard": sum(1 for r in rows if r["r_s_verdict"] == "hard"),
        "dl_blif_pos": sum(1 for r in rows if (r["dl_blif"] or 0) > 0),
        "dl_sky130_pos": sum(1 for r in rows if (r["dl_sky130"] or 0) > 0),
        "dwns_pos": sum(1 for d in dw if d > 0),
        "dwns_zero": sum(1 for d in dw if d == 0),
        "dwns_neg": sum(1 for d in dw if d < 0),
        "dwns_min": min(dw) if dw else None,
        "dwns_median": median(dw) if dw else None,
        "dwns_max": max(dw) if dw else None,
        "both": sum(1 for r in rows
                    if (r["dl_sky130"] or 0) > 0 and (r["dwns"] or 0) > 0),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--baseline-root", type=Path,
                    default=Path("experiments/20260924_l3s_ablation"))
    ap.add_argument("--circuits", default=",".join(ALL8))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    circuits = [c.strip() for c in args.circuits.split(",") if c.strip()]
    out: dict = {"root": str(args.root), "circuits": {}, "totals": {}}

    print("=" * 84)
    print("固定指标集（§13.4-4）—— `windows_offered` 不作 L1 主证据")
    print("=" * 84)
    print(f"  {'circuit':8} {'N_unique_win':>12} {'N_extracted':>11} {'N_S cand':>9} "
          f"{'N_measured':>10} {'N_accepted':>10}  {'pool_max':>8}")
    tot = {"uniq": 0, "extr": 0, "cand": 0, "meas": 0, "acc": 0}
    for c in circuits:
        d = _load(args.root / "on" / c / "outerloop_result.json")
        if d is None:
            print(f"  {c:8} {'--':>12}")
            continue
        sr = d.get("structure_resynth") or {}
        census = (sr.get("pool_census") or {}).get("candidates_len") or []
        t2 = tier2_for_circuit(args.root / "on", c)
        uniq = (t2 or {}).get("n_unique_window")
        if uniq is None:
            uniq = sr.get("candidates")
        row = {"n_unique_window": uniq,
               "n_extracted": sr.get("windows_extracted"),
               "n_candidate": sr.get("candidates"),
               "n_measured": sr.get("measured"),
               "n_accepted": sr.get("accepted"),
               "pool_max": max(census) if census else None,
               "window_pool": sr.get("window_pool")}
        out["circuits"][c] = row
        for k, key in (("uniq", "n_unique_window"), ("extr", "n_extracted"),
                       ("cand", "n_candidate"), ("meas", "n_measured"),
                       ("acc", "n_accepted")):
            if isinstance(row[key], int):
                tot[k] += row[key]
        print(f"  {c:8} {str(row['n_unique_window']):>12} {str(row['n_extracted']):>11} "
              f"{str(row['n_candidate']):>9} {str(row['n_measured']):>10} "
              f"{str(row['n_accepted']):>10}  {str(row['pool_max']):>8}")
    print(f"  {'TOTAL':8} {tot['uniq']:>12} {tot['extr']:>11} {tot['cand']:>9} "
          f"{tot['meas']:>10} {tot['acc']:>10}")
    out["totals"] = tot

    print("=" * 84)
    print("Tier 0 · 纪律 —— 单变量是否干净？（两臂非 S 试验序列须逐位相同）")
    print("=" * 84)
    single_var = {}
    for c in circuits:
        seqs = {}
        for arm in ("off", "on"):
            tj = _load(args.root / arm / c / "eval_trials.json")
            if tj is None:
                seqs[arm] = None
                continue
            tr = tj.get("trials", tj) if isinstance(tj, dict) else tj
            seqs[arm] = [(t.get("kind"), t.get("patch_id"), t.get("wns"),
                          t.get("accepted")) for t in tr if t.get("kind") != "S"]
        a, b = seqs.get("off"), seqs.get("on")
        if a is None or b is None:
            print(f"  {c:8} --")
            continue
        same = a == b
        single_var[c] = same
        print(f"  {c:8} non-S trials off={len(a)} on={len(b)} "
              f"identical={same}" + ("" if same else "   *** CONFOUND ***"))
    if single_var:
        n_ok = sum(1 for v in single_var.values() if v)
        print(f"  ⇒ {n_ok}/{len(single_var)} 电路的 R/G/B/JOINT 轨迹逐位相同"
              f"（L1 只增加 S 候选，未扰动搜索路径）")
    out["single_variable"] = single_var

    print()
    print("=" * 84)
    print("Tier 1 · enumeration —— 池子上限是否被解除？（只证明枚举瓶颈被解除）")
    print("=" * 84)
    print(f"  {'circuit':8} {'old':>5} {'L1':>5} {'delta':>6} {'pool_max':>9} "
          f"{'L1 offered':>11} {'engaged':>8}  status")
    t1_pass, t1_testable, t1_saturated, t1_noeng = [], [], [], []
    for c in circuits:
        d_new = _load(args.root / "on" / c / "outerloop_result.json")
        d_old = _load(args.baseline_root / "on" / c / "outerloop_result.json")
        if d_new is None:
            print(f"  {c:8} {'--':>5}")
            continue
        sr = d_new.get("structure_resynth") or {}
        n_new = sr.get("candidates")
        n_old = ((d_old.get("structure_resynth") or {}).get("candidates")
                 if d_old else None)
        census = (sr.get("pool_census") or {}).get("candidates_len") or []
        pool_max = max(census) if census else None
        offered = sr.get("window_pool_offered")
        engaged = sr.get("rounds_with_s") or []
        # 饱和的直接证据：L1 的专属枚举（k=window_pool）返回的边界数并不比 k=8 枚举更多
        saturated = (offered is not None and pool_max is not None
                     and offered <= pool_max)
        noeng = not engaged
        status = "SATURATED" if saturated else ("NO-ENGAGE" if noeng else "LIFTED")
        if saturated:
            out.setdefault("saturated", []).append(c)
            t1_saturated.append(c)
        elif noeng:
            t1_noeng.append(c)
        else:
            t1_testable.append(c)
            if n_new is not None and n_old is not None and n_new > n_old:
                t1_pass.append(c)
        d_txt = (f"+{n_new - n_old}" if (isinstance(n_old, int) and isinstance(n_new, int))
                 else "--")
        print(f"  {c:8} {str(n_old):>5} {str(n_new):>5} {d_txt:>6} {str(pool_max):>9} "
              f"{str(offered):>11} {str(len(engaged)):>8}  {status}")
    print(f"  ⇒ Tier 1: {len(t1_pass)}/{len(t1_testable)} 可测电路上候选严格增加")
    print(f"     （饱和 {len(t1_saturated)} 个：{t1_saturated}；未参与 {len(t1_noeng)} 个：{t1_noeng}）")
    out["tier1"] = {"pass": t1_pass, "testable": t1_testable,
                    "saturated": t1_saturated, "no_engage": t1_noeng}

    print()
    print("=" * 84)
    print("Tier 2 · candidate quality —— 枚举涨了，候选质量如何？")
    print("=" * 84)
    print(f"  {'circuit':8} {'n':>4} {'RS ok':>6} {'dL(sky)>0':>10} {'dWNS>0':>7} "
          f"{'=0':>4} {'<0':>4} {'min':>7} {'median':>7} {'max':>7}")
    agg = {"n": 0, "ok": 0, "sky": 0, "pos": 0, "zero": 0, "neg": 0}
    for c in circuits:
        t2 = tier2_for_circuit(args.root / "on", c)
        if t2 is None or t2.get("n", 0) == 0:
            print(f"  {c:8} {'--':>4}")
            continue
        out["circuits"].setdefault(c, {})["tier2"] = t2
        for k, key in (("n", "n"), ("ok", "rs_ok"), ("sky", "dl_sky130_pos"),
                       ("pos", "dwns_pos"), ("zero", "dwns_zero"),
                       ("neg", "dwns_neg")):
            agg[k] += t2[key]
        fmt = lambda v: f"{v:.3f}" if isinstance(v, float) else str(v)  # noqa: E731
        print(f"  {c:8} {t2['n']:>4} {t2['rs_ok']:>6} {t2['dl_sky130_pos']:>10} "
              f"{t2['dwns_pos']:>7} {t2['dwns_zero']:>4} {t2['dwns_neg']:>4} "
              f"{fmt(t2['dwns_min']):>7} {fmt(t2['dwns_median']):>7} {fmt(t2['dwns_max']):>7}")
    print(f"  {'TOTAL':8} {agg['n']:>4} {agg['ok']:>6} {agg['sky']:>10} "
          f"{agg['pos']:>7} {agg['zero']:>4} {agg['neg']:>4}")
    out["tier2_totals"] = agg
    if agg["n"]:
        print(f"  ⇒ 权威层深度下降 {agg['sky']}/{agg['n']}，但 ΔWNS>0 仅 {agg['pos']}/{agg['n']}"
              f"；ΔWNS≤0 占 {(agg['zero'] + agg['neg'])}/{agg['n']}")

    print()
    print("=" * 84)
    print("Tier 3 · repair capability —— 决定 OI-014")
    print("=" * 84)
    print(f"  {'circuit':8} {'wns_off':>9} {'wns_on':>9} {'dWNS(on-off)':>13} {'accepted':>9}")
    paired_improved, paired_tied, paired_worse = 0, 0, 0
    total_acc = 0
    for c in circuits:
        d_on = _load(args.root / "on" / c / "outerloop_result.json")
        d_off = _load(args.root / "off" / c / "outerloop_result.json")
        if d_on is None or d_off is None:
            print(f"  {c:8} {'--':>9}")
            continue
        w_on, w_off = d_on.get("wns"), d_off.get("wns")
        acc = (d_on.get("structure_resynth") or {}).get("accepted")
        if isinstance(acc, int):
            total_acc += acc
        try:
            d = round(w_on - w_off, 6)
        except TypeError:
            d = None
        if d is not None:
            if d > 0:
                paired_improved += 1
            elif d < 0:
                paired_worse += 1
            else:
                paired_tied += 1
        print(f"  {c:8} {str(w_off):>9} {str(w_on):>9} {str(d):>13} {str(acc):>9}")
    n_paired = paired_improved + paired_tied + paired_worse
    print(f"  ⇒ 配对 dWNS：improved {paired_improved} / tied {paired_tied} / worse {paired_worse}"
          f"（共 {n_paired}）；S 总接受数 = {total_acc}")
    out["tier3"] = {"paired_improved": paired_improved, "paired_tied": paired_tied,
                    "paired_worse": paired_worse, "n_paired": n_paired,
                    "total_accepted": total_acc}

    print()
    print("=" * 84)
    print("VERDICT（§13.4-3 三层，不得跳级）")
    print("=" * 84)
    print(f"  Tier 1 (enumeration)      : {'PASS' if t1_pass else 'not demonstrated'}"
          f"  ({len(t1_pass)}/{len(t1_testable)} 非饱和电路候选严格增加)")
    tier2_verdict = ("NO GAIN" if agg["n"] and agg["pos"] == 0
                     else ("GAIN" if agg["pos"] else "n/a"))
    print(f"  Tier 2 (candidate quality): ΔWNS>0 {agg['pos']}/{agg['n']}  -> {tier2_verdict}")
    tier3_ok = total_acc > 0 and paired_improved >= 1
    print(f"  Tier 3 (repair capability): accepted={total_acc}, "
          f"paired improved={paired_improved}  -> {'PASS' if tier3_ok else 'FAIL'}")
    if not tier3_ok:
        print()
        print("  判定：**NEGATIVE (capability)** —— 枚举瓶颈已排除，但当前 S 构造在该")
        print("  benchmark/regime 下没有体现 timing repair capability。")
        print("  ⇒ OI-014 选 **(B) 降级为可选候选类型/探索性能力**。")
        print("  ⇒ **不得**继续扩池 32→64→128；转 §13.7 S 候选质量归因。")
    else:
        print()
        print("  判定：达到第三层 ⇒ 有资格重新考虑 (A) 独立贡献（仍须给出归因证据）。")

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
