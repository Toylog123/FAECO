#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 FAECO 的最新编译产物同步一份到 01_Papers/00_Summary。

背景
----
`01_Papers/00_Summary` 是 01_Papers 下的论文汇总目录，同一论文只保留**一份最新的作者版 PDF**，
命名约定 ``<代号>_<中文标题>_作者版.pdf``。约定：**每次编译论文后刷新该副本**。
本脚本是 `02_RSECO/tools/sync_to_summary.py` 的 FAECO 版（同款契约，仅路径与目录结构不同）：
RSECO 是项目根 `main.pdf` + `figures/pdf|raster`，FAECO 是 `paper/zh/manuscript/*.pdf`
+ `paper/zh/figures/*`，因此不能直接复用同一份配置。

用法
----
    python tools/sync_to_summary.py              # 同步；内容一致则跳过（幂等）
    python tools/sync_to_summary.py --dry-run    # 只报告计划，不写任何文件
    python tools/sync_to_summary.py --check      # 只做一致性体检，不写文件
    python tools/sync_to_summary.py --force      # 内容一致也强制覆盖

退出码
------
    0  已同步 / 内容已是最新 / --dry-run 计划可行
    1  运行错误（读写失败、回读校验失败）
    2  构建过期（有 .tex 或图件比源 PDF 新）—— 未同步，请先重编译
    3  汇总目录已同步，但 `paper/zh/` 中文名副本刷新被跳过（疑似手工导出，拒绝覆盖）

设计要点
--------
- **只用标准库**，避免在同步盘上引入环境依赖。
- **拒绝同步过期产物**：源 PDF 若早于 `paper/zh/manuscript/*.tex` 或 `paper/zh/figures/*`，
  说明 PDF 不是最新编译结果，直接报警退出（这是本项目最容易踩的坑：改了 .tex 忘了编译就归档）。
- **顺带刷新 paper/zh/ 中文名副本**：编译只产出 `manuscript/<中文标题>.pdf`，
  `paper/zh/<中文标题>.pdf` 需有人刷新；若它比源更新且内容不同，判定为手工导出，拒绝覆盖。
- **幂等**：目标内容与源一致时不做写入，避免同步盘无谓回传。
- **可核验**：复制后重新算 SHA-256 并比对，输出证据而非「假设成功」。
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 配置（FAECO）
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parents[1]          # 03_FAECO
DEST_DIR = PROJECT_DIR.parent / "00_Summary"               # 01_Papers/00_Summary

PAPER_ZH = PROJECT_DIR / "paper" / "zh"
MANUSCRIPT = PAPER_ZH / "manuscript"
FIGURES = PAPER_ZH / "figures"

PDF_STEM = "FAECO_面向预布局门级时序ECO的结构化候选搜索与失效归因"
SRC_PDF = MANUSCRIPT / f"{PDF_STEM}.pdf"        # 编译产物
DELIVERABLE = PAPER_ZH / f"{PDF_STEM}.pdf"      # paper/zh/ 中文名副本
DEST_NAME = f"{PDF_STEM}_作者版.pdf"             # 00_Summary 固定文件名

# 构建新鲜度依赖：这些文件只要比源 PDF 新，就说明 PDF 不是最新编译结果
DEP_GLOBS = (
    (MANUSCRIPT, "*.tex"),
    (FIGURES, "*"),
)


def _log(tag: str, msg: str) -> None:
    print(f"[sync-summary] {tag} {msg}", flush=True)


def _mtime(path: Path) -> float:
    return path.stat().st_mtime


def _fmt_ts(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for block in iter(lambda: fp.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def _newer_deps(src: Path) -> list[Path]:
    src_t = _mtime(src)
    stale: list[Path] = []
    for root, pattern in DEP_GLOBS:
        if not root.is_dir():
            continue
        for dep in root.glob(pattern):
            if not dep.is_file():
                continue
            if root is not MANUSCRIPT and dep.name.startswith("_"):
                continue          # 实验中间产物不入依赖
            if _mtime(dep) > src_t:
                stale.append(dep)
    return sorted(stale)


def refresh_deliverable(dry_run: bool) -> int:
    """把 manuscript 里的编译产物复制为 paper/zh/ 的中文名副本。"""
    if not SRC_PDF.is_file():
        _log("ERROR", f"找不到编译产物 {SRC_PDF.relative_to(PROJECT_DIR)}")
        return 1

    if DELIVERABLE.is_file() and _sha256(DELIVERABLE) == _sha256(SRC_PDF):
        _log("OK", f"{DELIVERABLE.name} 已与编译产物一致，无需刷新。")
        return 0

    if DELIVERABLE.is_file() and _mtime(DELIVERABLE) > _mtime(SRC_PDF):
        _log("WARN", f"{DELIVERABLE.name}（{_fmt_ts(_mtime(DELIVERABLE))}）比编译产物"
                     f"（{_fmt_ts(_mtime(SRC_PDF))}）更新且内容不同，疑似手工导出，已跳过覆盖。")
        return 2

    if dry_run:
        _log("PLAN", f"将刷新 {DELIVERABLE.name} ← {SRC_PDF.name}（--dry-run 未写入）")
        return 0

    try:
        shutil.copy2(SRC_PDF, DELIVERABLE)
    except OSError as exc:
        _log("ERROR", f"刷新 {DELIVERABLE.name} 失败：{exc}")
        return 1

    if _sha256(DELIVERABLE) != _sha256(SRC_PDF):
        _log("ERROR", f"刷新 {DELIVERABLE.name} 后回读校验失败。")
        return 1
    _log("OK", f"已刷新 paper/zh 副本 {DELIVERABLE.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="同步 FAECO 最新作者版 PDF 到 00_Summary")
    ap.add_argument("--dest-dir", type=Path, default=DEST_DIR, help="汇总目录")
    ap.add_argument("--dest-name", default=DEST_NAME, help="汇总目录中的固定文件名")
    ap.add_argument("--dry-run", action="store_true", help="只报告，不写文件")
    ap.add_argument("--check", action="store_true", help="只体检，不写文件")
    ap.add_argument("--force", action="store_true", help="内容一致也强制覆盖")
    ap.add_argument("--skip-staleness", action="store_true", help="跳过构建过期检查")
    ap.add_argument("--no-refresh-deliverable", action="store_true",
                    help="不刷新 paper/zh 中文名副本")
    args = ap.parse_args(argv)

    dest = args.dest_dir / args.dest_name
    no_write = args.dry_run or args.check

    refresh_code = 0
    if not args.no_refresh_deliverable:
        refresh_code = refresh_deliverable(dry_run=no_write)

    def _finish(code: int) -> int:
        if code != 0:
            return code
        if refresh_code == 1:
            return 1
        if refresh_code == 2:
            return 3
        return 0

    if not SRC_PDF.is_file():
        _log("ERROR", f"找不到编译产物 {SRC_PDF.relative_to(PROJECT_DIR)}")
        return 2

    src_hash = _sha256(SRC_PDF)
    _log("INFO", f"源   {SRC_PDF.relative_to(PROJECT_DIR)}（{_fmt_ts(_mtime(SRC_PDF))}）")
    _log("INFO", f"源 SHA-256 {src_hash}")

    if not args.skip_staleness:
        stale = _newer_deps(SRC_PDF)
        if stale:
            _log("STALE", f"以下 {len(stale)} 个源文件晚于该 PDF，构建已过期，拒绝同步：")
            for dep in stale[:10]:
                _log("STALE", f"  - {dep.relative_to(PROJECT_DIR)}  （{_fmt_ts(_mtime(dep))}）")
            if len(stale) > 10:
                _log("STALE", f"  ... 另有 {len(stale) - 10} 个")
            _log("STALE", "请先重新编译（cd paper/zh/manuscript && lualatex ×2），再同步。")
            return 2

    if not args.dest_dir.is_dir():
        if no_write:
            _log("WARN", f"汇总目录不存在，正式运行时将创建：{args.dest_dir}")
        else:
            args.dest_dir.mkdir(parents=True, exist_ok=True)
            _log("INFO", f"已创建汇总目录 {args.dest_dir}")

    same = dest.is_file() and _sha256(dest) == src_hash
    if same and not args.force:
        _log("OK", f"目标 {dest.name} 内容与源一致，已是最新，未重复复制。")
        return _finish(0)

    if no_write:
        state = "内容不同，待复制" if dest.is_file() else "目标不存在，待新建"
        _log("PLAN", f"将复制到 {dest}：{state}（--dry-run/--check 未写入）")
        return _finish(0)

    try:
        shutil.copy2(SRC_PDF, dest)
    except OSError as exc:
        _log("ERROR", f"复制失败：{exc}")
        return _finish(1)

    dest_hash = _sha256(dest)
    if dest_hash != src_hash:
        _log("ERROR", f"回读校验失败：目标 {dest_hash[:16]}... != 源 {src_hash[:16]}...")
        return _finish(1)

    _log("OK", f"已同步到 00_Summary（{dest.stat().st_size / 1024 / 1024:.2f} MB，SHA-256 校验通过）")
    return _finish(0)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass
    raise SystemExit(main())
