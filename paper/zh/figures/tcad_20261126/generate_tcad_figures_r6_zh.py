#!/usr/bin/env python3
"""Render the R6 anytime and window-diagnosis figures from verified receipts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, NullLocator, StrMethodFormatter
from matplotlib.transforms import ScaledTranslation

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = REPO / "project_docs" / "evidence"
OUT = Path(__file__).resolve().parent
AUDIT_DIR = Path(os.environ.get(
    "FAECO_FIGURE_AUDIT_DIR", Path.home() / ".codex/skills/nature-figure/scripts"
))
sys.path.insert(0, str(AUDIT_DIR))
from audit_panel_alignment import require_matplotlib_panel_alignment

HORIZON = 720.0
SOURCES = {
    "boxed": "tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json",
    "replay": "tcad_boxed_drc_20261126/BOXED_DRC_RECALL_AUDIT.json",
    "riscv": "tcad_rank_alignment_20261125/RISCV_RANK_ALIGNED_VERIFIED.json",
    "uart": "tcad_wallclock_schedule_20261125/UART_WALLCLOCK_VERIFIED.json",
    "ablation": "tcad_v4_revision_20261126/WINDOWED_ABLATION_VERIFIED.json",
    "hybrid": "tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json",
    "extension": "tcad_v4_revision_20261126/TIMING_CLOSED_DRC_SENS_VERIFIED.json",
}

BLUE = "#125994"
GREEN = "#087653"
ORANGE = "#AC5600"
GRAY = "#4C5664"
SLATE = "#628FC4"
TEXT = "#202832"
SCREEN = "#E8EDF2"
GRID = "#DEE4EB"

DESIGN_ORDER = ("sky130hd_aes", "sky130hd_riscv32i", "asap7_uart", "asap7_aes")
DESIGN_NAMES = {
    "sky130hd_aes": "SKY130HD AES",
    "sky130hd_riscv32i": "SKY130HD riscv32i",
    "asap7_uart": "ASAP7 UART",
    "asap7_aes": "ASAP7 AES",
}
METHODS = {
    "window": {"label": "FAECO（微批次）", "color": BLUE, "linestyle": "-", "linewidth": 1.65},
    "hybrid": {"label": "Hybrid FAECO", "color": GREEN, "linestyle": "-", "linewidth": 1.45,
               "marker": "s", "markersize": 3.0},
    "fixed": {"label": "固定微批次", "color": ORANGE, "linestyle": (0, (4, 2)), "linewidth": 1.25},
    "single": {"label": "灵敏度单门", "color": GRAY, "linestyle": "-.", "linewidth": 1.10},
    "full": {"label": "FAECO（全块诊断）", "color": SLATE, "linestyle": ":", "linewidth": 1.45,
             "marker": "o", "markersize": 3.5, "markerfacecolor": "white"},
}
DIAGNOSIS_STYLES = {
    "sky130hd_aes": (BLUE, "o"),
    "asap7_aes": (GREEN, "s"),
    "asap7_uart": (ORANGE, "^"),
}
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "Noto Sans CJK SC", "DejaVu Sans"],
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "svg.hashsalt": "faeco-tcad-r6",
    "font.size": 8.3,
    "axes.titlesize": 9.0,
    "axes.labelsize": 8.4,
    "xtick.labelsize": 8.1,
    "ytick.labelsize": 8.1,
    "legend.fontsize": 8.1,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": .75,
    "axes.edgecolor": "#526072",
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
    "xtick.major.width": .7,
    "ytick.major.width": .7,
    "xtick.major.size": 2.7,
    "ytick.major.size": 2.7,
    "legend.frameon": False,
    "figure.facecolor": "white",
})


def load_sources():
    source_hashes, raw = {}, {}
    for key, relpath in SOURCES.items():
        payload = (EVIDENCE / relpath).read_bytes()
        raw[key] = json.loads(payload)
        source_hashes[relpath] = hashlib.sha256(payload).hexdigest()
    return raw, source_hashes


def only(rows, **fields):
    matches = [row for row in rows if all(row[key] == value for key, value in fields.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one receipt for {fields!r}, found {len(matches)}")
    return matches[0]


def accepted(rows, time_key, area_key):
    return [(row[time_key], row[area_key]) for row in rows if row.get("accepted", True)]


def anytime_tracks(raw):
    boxed = raw["boxed"]
    sky = boxed["sky130hd_aes"]["arms"]
    aes7 = boxed["asap7_aes"]["arms"]
    riscv = raw["riscv"]["arms"]
    uart = raw["uart"]["arms"]
    ablation = raw["ablation"]["arms"]
    hybrid = raw["hybrid"]["designs"]

    def cp(arm):
        return accepted(arm["checkpoints"], "elapsed_s", "area_saved_um2")

    def fwd(arms, strategy):
        return accepted(
            only(arms, strategy=strategy, direction="forward")["accepted"],
            "elapsed_seconds",
            "area_saved",
        )

    panels = {
        "sky130hd_aes": {
            "window": cp(only(sky, diagnosis_mode="boxed", order="forward")),
            "fixed": cp(ablation["sky130hd_aes::fixed_boxed"]),
            "single": cp(ablation["sky130hd_aes::single_sens_boxed"]),
            "full": cp(only(sky, diagnosis_mode="full", order="forward")),
        },
        "sky130hd_riscv32i": {
            "window": fwd(riscv, "faeco_dedup"),
            "single": fwd(riscv, "single_sensitivity"),
            "fixed": fwd(riscv, "fixed_online"),
        },
        "asap7_uart": {
            "window": fwd(uart, "faeco_dedup"),
            "single": fwd(uart, "single_sensitivity"),
            "fixed": fwd(uart, "fixed_online"),
        },
        "asap7_aes": {
            "window": cp(only(aes7, strategy="faeco_boxed_drc", direction="forward")),
            "fixed": cp(ablation["asap7_aes::fixed_boxed"]),
            "single": cp(only(aes7, strategy="single_boxed_drc", direction="forward")),
            "full": cp(only(aes7, strategy="faeco_full_drc", direction="forward")),
        },
    }
    rows = []
    for design in DESIGN_ORDER:
        arms = panels[design]
        arms["hybrid"] = cp(hybrid[design])
        screen = hybrid[design]["charged_screening_s"]
        for method, points in arms.items():
            if not points or not all(screen < t <= HORIZON and a > 0 for t, a in points):
                raise ValueError(f"Invalid checkpoints for {design}/{method}")
            if any(t1 >= t2 or a1 > a2 for (t1, a1), (t2, a2) in zip(points, points[1:])):
                raise ValueError(f"Checkpoints are out of order for {design}/{method}")
            for i, (t, a) in enumerate(points, start=1):
                rows.append({
                    "design": design, "method": method, "checkpoint": i,
                    "charged_screening_s": screen, "time_s": t, "area_um2": a,
                })
    return panels, rows


def diagnosis_pairs(raw):
    rows = []
    for design, cases in raw["replay"].items():
        for case in cases:
            window = case["halos"]["1.0"]
            if not window["exact_marker_match"] or not window["exact_neighbor_match"]:
                raise ValueError(f"Replay disagrees on {design}/{case['case_idx']}")
            rows.append({
                "design": design, "family": "replay", "case": case["case_idx"],
                "edits": case["num_actions"], "full_s": case["full_seconds"],
                "window_s": window["seconds"], "markers": case["full_unique_markers"],
            })
    for family, key in [
        ("downsizing", "asap7_nonzero_drc"), ("pin_shift", "asap7_pinshift_exact_drc")
    ]:
        for case in raw["extension"][key]["cases"]:
            if not case["exact_match"] or case["full_unique_markers"] != 0:
                raise ValueError(f"Unexpected extension definition on {case['batch']}")
            rows.append({
                "design": case["design"], "family": family, "case": case["batch"],
                "edits": case["num_edits"], "full_s": case["full_seconds"],
                "window_s": case["boxed_seconds"], "markers": case["full_unique_markers"],
            })
    for pair in rows:
        if min(pair["edits"], pair["full_s"], pair["window_s"]) <= 0:
            raise ValueError(f"Nonpositive input for log scale: {pair!r}")
        pair["speedup"] = pair["full_s"] / pair["window_s"]
    keys = [(p["design"], p["family"], p["case"]) for p in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate diagnosis pair")
    return rows


def panel_title(ax, letter, title):
    ax.set_title(title, loc="left", fontweight="bold", pad=8, x=.080)
    ax.text(
        0, 1, letter, transform=ax.transAxes + ScaledTranslation(
            0, 8 / 72, ax.figure.dpi_scale_trans
        ), va="baseline", ha="left", fontsize=10.3, fontweight="bold",
    )


def render_anytime(raw, tracks):
    fig, axes = plt.subplots(2, 2, figsize=(6.69, 4.15))
    fig.subplots_adjust(left=.112, right=.980, bottom=.205, top=.927, wspace=.26, hspace=.49)
    notes = (
        ("全池探针通过", 214, [0, 50, 100, 150, 200]),
        ("探针超时，交付推迟", 89, [0, 20, 40, 60, 80]),
        ("自适应调度提高终态回收", 1.02, [0, .25, .5, .75, 1]),
        ("固定批与纯 FAECO 终态相同", .775, [0, .2, .4, .6]),
    )
    for letter, ax, design, (note, top, ticks) in zip("abcd", axes.flat, DESIGN_ORDER, notes):
        screen = raw["hybrid"]["designs"][design]["charged_screening_s"]
        ax.axvspan(0, screen, color=SCREEN, zorder=0)
        for method in ("full", "single", "window", "fixed", "hybrid"):
            if method not in tracks[design]:
                continue
            points = tracks[design][method]
            times, areas = zip((0.0, 0.0), *points, (HORIZON, points[-1][1]))
            style = METHODS[method]
            marks = {"markevery": range(1, len(points) + 1)} if "marker" in style else {}
            ax.step(times, areas, where="post", **style, **marks)
        ax.set(xlim=(0, HORIZON), ylim=(-top * .038, top), yticks=ticks)
        ax.set_xticks((0, 180, 360, 540, 720))
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:g}"))
        ax.yaxis.grid(color=GRID, linewidth=.52)
        ax.set_axisbelow(True)
        panel_title(ax, letter, DESIGN_NAMES[design])
        title_offset = ScaledTranslation(0, 8 / 72, fig.dpi_scale_trans)
        ax.text(1, 1, note, transform=ax.transAxes + title_offset, ha="right", va="baseline",
                color="#344355", fontsize=8.0)
    fig.supxlabel("含公共预筛的墙钟时间（s）", x=.55, y=.118, fontsize=8.5)
    fig.supylabel("合格回收面积（μm²）", x=.023, y=.565, fontsize=8.5)
    legend = [Line2D([], [], **METHODS[key])
              for key in ["window", "hybrid", "fixed", "single", "full"]]
    legend.append(Patch(color=SCREEN, label="公共预筛"))
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(.55, .007), ncol=3,
               labelspacing=.55, columnspacing=1.85, handlelength=2.5, handletextpad=.55)
    return fig


def render_diagnosis(rows):
    fig, axes = plt.subplots(1, 2, figsize=(6.69, 2.73))
    fig.subplots_adjust(left=.098, right=.979, bottom=.274, top=.902, wspace=.36)
    seconds_ax, ratio_ax = axes
    for pair in rows:
        color, marker = DIAGNOSIS_STYLES[pair["design"]]
        edit_count = pair["edits"]
        for field, filled in (("full_s", True), ("window_s", False)):
            seconds_ax.scatter(edit_count, pair[field], s=29, marker=marker,
                               edgecolor=color, facecolor=color if filled else "none", linewidth=.95)
        replay = pair["family"] == "replay"
        ratio_ax.scatter(edit_count, pair["speedup"], s=34, marker=marker,
                         edgecolor=color, facecolor=color if replay else "none", linewidth=.95)
    ratio_ax.axhline(1, color="#657180", linewidth=.9, linestyle=(0, (4, 2)), zorder=1)
    for ax in axes:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(.82, 142)
        ax.xaxis.set_major_locator(FixedLocator((1, 3, 6, 12, 25, 60, 120)))
        ax.xaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_minor_locator(NullLocator())
        ax.xaxis.set_major_formatter(StrMethodFormatter("{x:g}"))
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:g}"))
        ax.yaxis.grid(color=GRID, linewidth=.52)
        ax.set_axisbelow(True)
    seconds_ax.set(ylim=(1.85, 61), ylabel="预检耗时（s）")
    seconds_ax.yaxis.set_major_locator(FixedLocator((2, 4, 8, 16, 32)))
    ratio_ax.set(ylim=(.49, 22), ylabel="加速比（倍）")
    ratio_ax.yaxis.set_major_locator(FixedLocator((.5, 1, 2, 4, 8, 16)))
    panel_title(seconds_ax, "a", "单次预检耗时")
    panel_title(ratio_ax, "b", "同提议的全块／窗口用时比")
    fig.supxlabel("单次验证的累计换门或引脚偏移数", x=.53, y=.142)
    design_keys = [
        Line2D([], [], label=DESIGN_NAMES[design], linestyle="none", marker=marker,
               markeredgecolor=color, markerfacecolor=color, markersize=5.5)
        for design, (color, marker) in DIAGNOSIS_STYLES.items()
    ]
    fig.legend(handles=design_keys, loc="lower center", bbox_to_anchor=(.53, .000), ncol=3,
               handlelength=.90, columnspacing=1.70, handletextpad=.45)
    seconds_ax.text(.95, .09, "实心：全块  空心：窗口", ha="right", va="bottom",
                    transform=seconds_ax.transAxes, fontsize=8.0, color=GRAY)
    ratio_ax.text(.95, .88, "实心：历史回放  空心：扩展提议", ha="right", va="top",
                  transform=ratio_ax.transAxes, fontsize=8.0, color=GRAY)
    return fig


def write_csv(path, records):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=tuple(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def export(fig, output, stem, preview_dir):
    require_matplotlib_panel_alignment(
        fig, json_out=str(output / f"{stem}.alignment.json"),
        tolerance_pt=1.5, gutter_tolerance_pt=1.5, require_panel_labels=True, strict=True,
    )
    fig.savefig(output / f"{stem}.pdf", metadata={"CreationDate": None})
    svg_path = output / f"{stem}.svg"
    fig.savefig(svg_path, metadata={"Date": None})
    svg_lines = svg_path.read_text(encoding="utf-8").splitlines()
    svg_path.write_text("\n".join(line.rstrip() for line in svg_lines) + "\n", encoding="utf-8", newline="\n")
    if preview_dir:
        preview_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(preview_dir / f"{stem}.png", dpi=600)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--preview-dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw, checksums = load_sources()
    tracks, checkpoints = anytime_tracks(raw)
    pairs = diagnosis_pairs(raw)
    for plot, records, stem in [
        (render_anytime(raw, tracks), checkpoints, "fig3_anytime_r6_zh"),
        (render_diagnosis(pairs), pairs, "fig4_window_diagnosis_r6_zh"),
    ]:
        export(plot, args.output_dir, stem, args.preview_dir)
        write_csv(args.output_dir / f"{stem}.csv", records)
    (args.output_dir / "r6_plot_source_sha256.json").write_text(
        json.dumps(checksums, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
