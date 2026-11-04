#!/usr/bin/env bash
# ECO 前后 · **同布局** 三臂对照 · OpenROAD 26Q3（只在 WSL 内运行）
#
#   MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash code/scripts/run_eco_phys_samelayout.sh
#   可选：CASES="s27 s382"  ARMS="base eco ecofix"  UTIL=35  TIMEOUT=3600  DRT_ITER=15
#
# 三臂含义
# --------
#   base   : 基线网表，种子布局 → CTS → 布线。序列与独立布局族完全相同，
#            故其读数必须与 experiments/20261029_eco_phys_contrast/ 的 base 逐位相同（自检 A）。
#   eco    : ECO 网表，**同一份 CTS 前布局** → 重跑 CTS → 布线（对齐到布局层）。
#   ecofix : ECO 网表，**直接以 base 的 CTS 后 DEF 为起点**，只 replace_cell 换门
#            → 重新合法化 → 布线。布局与时钟树与 base 逐位相同，最贴近真实 ECO。
#
# 为什么要有两条 eco 臂
# --------------------
# eco 允许 CTS 重跑，会把布局打散（s27 实测 CTS 后 72.7% 单元位移）；
# ecofix 不重跑 CTS，位移只来自换门后的局部合法化。两者一致时结论稳，
# 不一致时差异量本身就是「重跑 CTS 的代价」，可单独报告。
#
# 布局种子必须取 **CTS 之前** 的 placed DEF（v1 的血的教训）
# ------------------------------------------------------
# 首版拿 base 的**布线后** DEF 当布局来源，那份 DEF 已含 CTS 缓冲位置；两臂从
# 「已被缓冲占据」的布局重跑 CTS 时新缓冲无处落脚，第二次 legalize 大幅挪单元，
# DRT 随后不收敛：16 次运行 12 次带 li1 Metal Spacing 违规，而此前四个物理族
# 全部 0 违规。故种子阶段单独跑 floorplan→place_pins→GP→legalize，两臂共用。
#
# 为什么 replace_cell 合法
# ----------------------
# CO 臂（pureG）只换 drive strength：8 例实测 base/eco 实例名 100% 相同、
# 连接关系 0 差异，仅 1~5 个 master 不同（gen_swap_list.py 会校验并拒绝结构改动）。
#
# 四条内建自检
# -----------
#   A) base 读数与独立布局族逐位相同（同序列同网表，应当完全一致）
#   B) base 第一次 legalize 位移 = 0（种子位置本来就合法）
#   C) 三臂 ideal 档 WNS 全等（ideal 不含寄生，与布局无关）
#   D) 布线 0 DRC 违规；否则该例读数作废
set -uo pipefail

R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
BASE=/home/toylog/faeco_eda
OR=$BASE/or26Q3/bin/openroad
STA=$BASE/or26Q3/bin/sta
PY=${PY:-python3}          # 在 WSL 内执行，不能用 Windows 的 .venv/Scripts/python.exe

PLAT=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629
LIB=$PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib

INDEP=$R/experiments/20261029_eco_phys_contrast
OUT=$R/experiments/20261029_eco_phys_samelayout

CASES=${CASES:-"s27 s382 s420 s641 s713 s820 s832 s953"}
ARMS=${ARMS:-"base eco ecofix"}
UTIL=${UTIL:-35}
TIMEOUT=${TIMEOUT:-3600}
DRT_ITER=${DRT_ITER:-15}

mkdir -p "$OUT"
READ=$OUT/readings.tsv
[ -s "$READ" ] || printf 'circuit\tarm\tideal\tpost\tdrc\tmoved_pct\tmean_moved\tmax_shift\n' > "$READ"

echo "== 工具 =="
"$OR" -version 2>&1 | head -1
"$STA" -version 2>&1 | head -1
echo "  OUT=$OUT  UTIL=$UTIL  ARMS=$ARMS"
echo

has_arm () { case " $ARMS " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

for c in $CASES; do
  echo "########## $c ##########"
  SEEDD=$OUT/$c/seed
  mkdir -p "$SEEDD"

  # ---------- 种子布局（仅 base/eco 需要） ----------
  if has_arm base || has_arm eco; then
    if [ ! -s "$SEEDD/$c.placed.def" ]; then
      if [ ! -s "$INDEP/$c/base/clean.v" ]; then echo "  缺 base 网表"; continue; fi
      cat > "$SEEDD/seed_flow.tcl" <<EOT
read_lef $PLAT/lef/sky130_fd_sc_hd.tlef
read_lef $PLAT/lef/sky130_fd_sc_hd_merged.lef
read_liberty $LIB
read_verilog $INDEP/$c/base/clean.v
link_design $c
source $INDEP/$c/base/constraint.sdc
initialize_floorplan -utilization $UTIL -aspect_ratio 1 -core_space 2 -site unithd
source $PLAT/make_tracks.tcl
place_pins -hor_layers met3 -ver_layers met2
global_placement -density 0.55
detailed_placement
write_def $SEEDD/$c.placed.def
puts "STAGE=seed_done cells=[llength [get_cells *]]"
EOT
      ( cd "$SEEDD" && timeout "$TIMEOUT" "$OR" -no_init -exit -log "$SEEDD/openroad.log" "$SEEDD/seed_flow.tcl" \
          | grep -E "STAGE=" ) || true
      [ -s "$SEEDD/$c.placed.def" ] || { echo "  种子布局失败"; continue; }
    fi
    echo "  种子布局就绪"
  fi

  # ---------- 臂 base / eco：共用种子布局 ----------
  for k in base eco; do
    has_arm "$k" || continue
    D=$OUT/$c/$k
    mkdir -p "$D"
    SRC=$INDEP/$c/$k/clean.v
    [ -s "$SRC" ] || { echo "  缺网表: $SRC"; continue; }
    cp -f "$SRC" "$D/mapped.v"
    cp -f "$INDEP/$c/$k/constraint.sdc" "$D/constraint.sdc" 2>/dev/null || true
    "$PY" "$R/code/scripts/gen_place_from_def.py" "$SEEDD/$c.placed.def" "$D/place_from_seed.tcl" \
      --only-from "$SRC" | sed "s/^/  [$k] place: /"

    if [ ! -s "$D/$c.spef" ]; then
      cat > "$D/flow.tcl" <<EOT
read_lef $PLAT/lef/sky130_fd_sc_hd.tlef
read_lef $PLAT/lef/sky130_fd_sc_hd_merged.lef
read_liberty $LIB
read_verilog $D/mapped.v
link_design $c
puts "STAGE=linked cells=[llength [get_cells *]] nets=[llength [get_nets *]]"
if {[catch {source $D/constraint.sdc} e]} { puts "SDC_FAIL: \$e" }
if {[catch {read_def -floorplan_initialize -continue_on_errors $SEEDD/$c.placed.def} e]} { puts "STAGE=fp_err: \$e" }
if {[catch {source $D/place_from_seed.tcl} e]} { puts "STAGE=placeinst_err: \$e" }
write_def $D/seed.def
detailed_placement
write_def $D/legal.def
puts "STAGE=legalized"
clock_tree_synthesis -buf_list {sky130_fd_sc_hd__clkbuf_4 sky130_fd_sc_hd__clkbuf_8} -root_buf sky130_fd_sc_hd__clkbuf_16
repair_clock_nets
detailed_placement
write_def $D/cts.def
puts "STAGE=cts done"
set_propagated_clock [all_clocks]
source $PLAT/setRC.tcl
set_routing_layers -signal met1-met5 -clock met3-met5
pin_access
global_route
detailed_route -output_drc $D/drc.rpt -verbose 0 -droute_end_iter $DRT_ITER
puts "STAGE=route done"
write_def $D/$c.def
write_verilog $D/$c.routed.v
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $PLAT/rcx/rcx_patterns.rules
write_spef $D/$c.spef
puts "STAGE=ALL_OK"
EOT
      ( cd "$D" && timeout "$TIMEOUT" "$OR" -no_init -exit -log "$D/openroad.log" "$D/flow.tcl" \
          | grep -E "STAGE=|RCX-0114" ) || true
      rm -f "$D/route.guide" "$R/route.guide"
    fi
    if [ -s "$D/legal.def" ]; then
      "$PY" "$R/code/scripts/compare_def_place.py" "$SEEDD/$c.placed.def" "$D/legal.def" > "$D/shift_legal.txt" 2>&1
      cat "$D/shift_legal.txt" | head -1 | sed "s/^/  [$k] 合法化: /"
    fi
    echo "  [$k] DRC=$(grep -c 'violation type' "$D/drc.rpt" 2>/dev/null | head -1)"
  done

  # ---------- 臂 ecofix：base 的 CTS 后 DEF + 只换门 ----------
  if has_arm ecofix; then
    D=$OUT/$c/ecofix
    mkdir -p "$D"
    BCP=$OUT/$c/base/cts.def
    if [ ! -s "$BCP" ]; then echo "  [ecofix] 缺 base 的 CTS 后 DEF，跳过"; else
      "$PY" "$R/code/scripts/gen_swap_list.py" "$INDEP/$c/base/clean.v" "$INDEP/$c/eco/clean.v" "$D/swap.tcl" \
        | head -1 | sed "s/^/  [ecofix] /"
      cp -f "$INDEP/$c/base/constraint.sdc" "$D/constraint.sdc" 2>/dev/null || true
      if [ ! -s "$D/$c.spef" ]; then
        cat > "$D/flow.tcl" <<EOT
read_lef $PLAT/lef/sky130_fd_sc_hd.tlef
read_lef $PLAT/lef/sky130_fd_sc_hd_merged.lef
read_liberty $LIB
read_def $BCP
puts "STAGE=def_read cells=[llength [get_cells *]] nets=[llength [get_nets *]]"
source $D/constraint.sdc
source $D/swap.tcl
puts "STAGE=swapped"
detailed_placement
write_def $D/legal.def
puts "STAGE=legalized"
set_propagated_clock [all_clocks]
source $PLAT/setRC.tcl
set_routing_layers -signal met1-met5 -clock met3-met5
pin_access
global_route
detailed_route -output_drc $D/drc.rpt -verbose 0 -droute_end_iter $DRT_ITER
puts "STAGE=route done"
write_def $D/$c.def
write_verilog $D/$c.routed.v
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $PLAT/rcx/rcx_patterns.rules
write_spef $D/$c.spef
puts "STAGE=ALL_OK"
EOT
        ( cd "$D" && timeout "$TIMEOUT" "$OR" -no_init -exit -log "$D/openroad.log" "$D/flow.tcl" \
            | grep -E "STAGE=|RCX-0114" ) || true
        rm -f "$D/route.guide" "$R/route.guide"
      fi
      if [ -s "$D/legal.def" ] && [ -s "$OUT/$c/base/cts.def" ]; then
        "$PY" "$R/code/scripts/compare_def_place.py" "$OUT/$c/base/cts.def" "$D/legal.def" > "$D/shift_legal.txt" 2>&1
        cat "$D/shift_legal.txt" | head -1 | sed "s/^/  [ecofix] 合法化: /"
      fi
      echo "  [ecofix] DRC=$(grep -c 'violation type' "$D/drc.rpt" 2>/dev/null | head -1)"
    fi
  fi
  echo
done

# ---------- STA 读数 ----------
sta_pair () {
  local D=$1 t=$2
  [ -s "$D/$t.routed.v" ] && [ -s "$D/$t.spef" ] || { echo ""; return; }
  cat > "$D/sta_ideal.tcl" <<EOT
read_liberty $LIB
read_verilog $D/$t.routed.v
link_design $t
source $D/constraint.sdc
report_worst_slack -max
EOT
  cat > "$D/sta_post.tcl" <<EOT
read_liberty $LIB
read_verilog $D/$t.routed.v
link_design $t
source $D/constraint.sdc
read_spef $D/$t.spef
report_worst_slack -max
EOT
  local iw pw
  iw=$("$STA" -no_init -exit "$D/sta_ideal.tcl" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}')
  pw=$("$STA" -no_init -exit "$D/sta_post.tcl"  2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}')
  echo "$iw $pw"
}

echo "== 读数（重算整表）=="
printf 'circuit\tarm\tideal\tpost\tdrc\tmoved_pct\tmean_moved\tmax_shift\n' > "$READ"
for c in $CASES; do
  for k in $ARMS; do
    D=$OUT/$c/$k
    [ -d "$D" ] || continue
    read -r IW PW <<< "$(sta_pair "$D" "$c")"
    NV=$(grep -c 'violation type' "$D/drc.rpt" 2>/dev/null || true); NV=${NV:-NA}
    MP=$(grep -o 'moved_pct=[0-9.]*%' "$D/shift_legal.txt" 2>/dev/null | head -1 | cut -d= -f2)
    MM=$(grep -o 'mean_moved=[0-9.]*' "$D/shift_legal.txt" 2>/dev/null | head -1 | cut -d= -f2)
    MX=$(grep -o 'max=[0-9.]*' "$D/shift_legal.txt" 2>/dev/null | head -1 | cut -d= -f2)
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$k" "${IW:--}" "${PW:--}" "$NV" \
      "${MP:--}" "${MM:--}" "${MX:--}" >> "$READ"
  done
done
column -t -s $'\t' "$READ"

echo
echo "== 汇总 =="
"$PY" "$R/code/scripts/summarize_eco_samelayout.py" "$READ" "$OUT/summary.tsv" "$INDEP/eco_phys_contrast.tsv" || true
[ -s "$OUT/summary.tsv" ] && column -t -s $'\t' "$OUT/summary.tsv"
