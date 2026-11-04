#!/usr/bin/env bash
# ITC'99 · ECO 前后四数对照 · 同布局三臂 · OpenROAD 26Q3（只在 WSL 内运行）
#
#   CASE=b13 SRC_DIR=experiments/20261029_itc99_26q3/b13 \
#     MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash code/scripts/run_eco_phys_itc.sh
#
# 与 ISCAS 八例（run_eco_phys_samelayout.sh）是同一套流程、同一套自检，
# 只把网表来源换成 ITC'99：base = 原族 mapped.v，eco = gen_itc_eco.py 生成的换门网表。
#
# 四数口径（本族存在的唯一理由）
# ---------------------------
#                预布局(ideal)   布线后(post)
#   base  (未修改)     A                B
#   eco   (已修改)     C                D
#   预布局档改善 = C−A        布线后档改善 = D−B        保持率 = (D−B)/(C−A)
#   同一网表自己的 C→D 差不是效果量，不报告、不入表。
#
# 三臂
#   base   : 原网表，种子布局 → CTS → 布线
#   eco    : ECO 网表，**同一份 CTS 前布局** → 重跑 CTS → 布线
#   ecofix : 以 base 的 CTS 后 DEF 为起点，只 replace_cell 换门 → 合法化 → 布线
#
# 布局种子取 **CTS 之前**（与 ISCAS 族同一条血的教训：拿布线后 DEF 当种子会 DRT 不收敛）
set -uo pipefail

R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
BASE=/home/toylog/faeco_eda
OR=$BASE/or26Q3/bin/openroad
STA=$BASE/or26Q3/bin/sta
PY=${PY:-python3}

PLAT=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629
LIB=$PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib

CASES=${CASES:-"b13"}
ARMS=${ARMS:-"base eco ecofix"}
UTIL=${UTIL:-35}
TIMEOUT=${TIMEOUT:-5400}
DRT_ITER=${DRT_ITER:-15}
# base 臂只跑到 CTS（只为给 ecofix 提供起点，B 改用「之前不修改的实际布线」时用）
BASE_STOP_AT=${BASE_STOP_AT:-}
# 原族目录：b11–b13 在 20261029_itc99_26q3，b14/b15/b20 在 20261029_itc99_scale_26q3
SRC_ROOT=${SRC_ROOT:-$R/experiments/20261029_itc99_26q3}
SRC_ROOTS=${SRC_ROOTS:-"$SRC_ROOT $R/experiments/20261029_itc99_26q3 $R/experiments/20261029_itc99_scale_26q3"}
ECO_OUT=${ECO_OUT:-$R/experiments/20261029_itc99_eco_fournum}

pick_src () {
  local c=$1 d
  for d in $SRC_ROOTS; do
    [ -s "$d/$c/mapped.v" ] && { echo "$d/$c"; return; }
  done
  echo ""
}

echo "== 工具 =="
"$OR" -version 2>&1 | head -1
"$STA" -version 2>&1 | head -1
echo "  SRC_ROOT=$SRC_ROOT  ECO_OUT=$ECO_OUT  UTIL=$UTIL  ARMS=$ARMS"
echo

has_arm () { case " $ARMS " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

mkdir -p "$ECO_OUT"
READ=$ECO_OUT/readings.tsv
[ -s "$READ" ] || printf 'circuit\tarm\tideal\tpost\tdrc\tmoved_pct\tmean_moved\tmax_shift\n' > "$READ"

for c in $CASES; do
  echo "########## $c ##########"
  SRC=$(pick_src "$c")
  OUT=$ECO_OUT/$c
  SEEDD=$OUT/seed
  mkdir -p "$SEEDD"

  if [ ! -s "$SRC/mapped.v" ]; then echo "  缺 base 网表: $SRC/mapped.v"; continue; fi
  if [ ! -s "$OUT/mapped.v" ]; then echo "  缺 eco 网表: $OUT/mapped.v（先跑 gen_itc_eco.py）"; continue; fi
  SDC=$SRC/constraint.sdc
  cp -f "$SDC" "$OUT/constraint.sdc"

  # ---------- 种子布局（CTS 之前） ----------
  if has_arm base || has_arm eco; then
    if [ ! -s "$SEEDD/$c.placed.def" ]; then
      cat > "$SEEDD/seed_flow.tcl" <<EOT
read_lef $PLAT/lef/sky130_fd_sc_hd.tlef
read_lef $PLAT/lef/sky130_fd_sc_hd_merged.lef
read_liberty $LIB
read_verilog $SRC/mapped.v
link_design $c
source $SDC
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
    D=$OUT/$k
    mkdir -p "$D"
    if [ "$k" = base ]; then SRCV=$SRC/mapped.v; else SRCV=$OUT/mapped.v; fi
    cp -f "$SRCV" "$D/mapped.v"
    cp -f "$SDC" "$D/constraint.sdc"
    "$PY" "$R/code/scripts/gen_place_from_def.py" "$SEEDD/$c.placed.def" "$D/place_from_seed.tcl" \
      --only-from "$SRCV" | sed "s/^/  [$k] place: /"

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
foreach _nm {one_ zero_} { if {[catch {set _n [[ord::get_db_block] findNet \$_nm]; if {\$_n ne "NULL"} { \$_n setSigType SIGNAL ; puts "STAGE=tie_net_fixed \$_nm" }} _e]} { puts "TIE_FIX_SKIP \$_nm: \$_e" } }
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
      # base 只到 CTS：截断 flow，在 write_def cts.def 之后退出
      if [ "$BASE_STOP_AT" = "cts" ] && [ "$k" = "base" ]; then
        sed -i '/puts "STAGE=cts done"/a exit' "$D/flow.tcl"
        echo "  [base] 只跑到 CTS（BASE_STOP_AT=cts）"
      fi
      ( cd "$D" && timeout "$TIMEOUT" "$OR" -no_init -exit -log "$D/openroad.log" "$D/flow.tcl" \
          | grep -E "STAGE=|RCX-0114" ) || true
      rm -f "$D/route.guide" "$R/route.guide"
    fi
    if [ -s "$D/legal.def" ]; then
      "$PY" "$R/code/scripts/compare_def_place.py" "$SEEDD/$c.placed.def" "$D/legal.def" > "$D/shift_legal.txt" 2>&1
      head -1 "$D/shift_legal.txt" | sed "s/^/  [$k] 合法化: /"
    fi
    echo "  [$k] DRC=$(grep -c 'violation type' "$D/drc.rpt" 2>/dev/null | head -1)"
  done

  # ---------- 臂 ecofix：base 的 CTS 后 DEF + 只换门 ----------
  if has_arm ecofix; then
    D=$OUT/ecofix
    mkdir -p "$D"
    BCP=$OUT/base/cts.def
    if [ ! -s "$BCP" ]; then echo "  [ecofix] 缺 base 的 CTS 后 DEF，跳过"; else
      "$PY" "$R/code/scripts/gen_swap_list.py" "$SRC/mapped.v" "$OUT/mapped.v" "$D/swap.tcl" \
        | head -1 | sed "s/^/  [ecofix] /"
      cp -f "$SDC" "$D/constraint.sdc"
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
foreach _nm {one_ zero_} { if {[catch {set _n [[ord::get_db_block] findNet \$_nm]; if {\$_n ne "NULL"} { \$_n setSigType SIGNAL ; puts "STAGE=tie_net_fixed \$_nm" }} _e]} { puts "TIE_FIX_SKIP \$_nm: \$_e" } }
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
      if [ -s "$D/legal.def" ] && [ -s "$OUT/base/cts.def" ]; then
        "$PY" "$R/code/scripts/compare_def_place.py" "$OUT/base/cts.def" "$D/legal.def" > "$D/shift_legal.txt" 2>&1
        head -1 "$D/shift_legal.txt" | sed "s/^/  [ecofix] 合法化: /"
      fi
      echo "  [ecofix] DRC=$(grep -c 'violation type' "$D/drc.rpt" 2>/dev/null | head -1)"
    fi
  fi
  echo
done

# ---------- STA 读数 ----------
# post_src 列记录 B 的来源：out = 本次同布局重跑；legacy_orig = 原族「之前那次不修改的
# 实际布线」（同网表、同 util、同流程，不同一次布局），仅当 base 臂没有布线产物时启用。
echo "== 读数（重算整表） =="
printf 'circuit\tarm\tideal\tpost\tdrc\tmoved_pct\tmean_moved\tmax_shift\tpost_src\n' > "$READ"
for c in $CASES; do
  SRC=$(pick_src "$c")
  for k in $ARMS; do
    D=$ECO_OUT/$c/$k
    mkdir -p "$D"
    V=""; S=""; SDCF=""; SRCK=""; DRCF=""
    if [ -s "$D/$c.routed.v" ] && [ -s "$D/$c.spef" ]; then
      V=$D/$c.routed.v; S=$D/$c.spef; SDCF=$D/constraint.sdc; SRCK=out; DRCF=$D/drc.rpt
    elif [ "$k" = "base" ] && [ -s "$SRC/$c.routed.v" ] && [ -s "$SRC/$c.spef" ]; then
      V=$SRC/$c.routed.v; S=$SRC/$c.spef; SDCF=$SRC/constraint.sdc; SRCK=legacy_orig; DRCF=$SRC/drc.rpt
    else
      continue
    fi
    cat > "$D/_sta_i.tcl" <<EOT
read_liberty $LIB
read_verilog $V
link_design $c
source $SDCF
report_worst_slack -max
EOT
    cat > "$D/_sta_p.tcl" <<EOT
read_liberty $LIB
read_verilog $V
link_design $c
source $SDCF
read_spef $S
report_worst_slack -max
EOT
    IW=$("$STA" -no_init -exit "$D/_sta_i.tcl" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}')
    PW=$("$STA" -no_init -exit "$D/_sta_p.tcl" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}')
    NV=$(grep -c 'violation type' "$DRCF" 2>/dev/null || true); NV=${NV:-NA}
    MP=$(grep -o 'moved_pct=[0-9.]*%' "$D/shift_legal.txt" 2>/dev/null | head -1 | cut -d= -f2)
    MM=$(grep -o 'mean_moved=[0-9.]*' "$D/shift_legal.txt" 2>/dev/null | head -1 | cut -d= -f2)
    MX=$(grep -o 'max=[0-9.]*' "$D/shift_legal.txt" 2>/dev/null | head -1 | cut -d= -f2)
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$k" "${IW:--}" "${PW:--}" "$NV" \
      "${MP:--}" "${MM:--}" "${MX:--}" "$SRCK" >> "$READ"
  done
done
column -t -s $'\t' "$READ"

echo
echo "== 汇总（C−A / D−B） =="
"$PY" "$R/code/scripts/summarize_eco_samelayout.py" "$READ" "$ECO_OUT/summary.tsv" || true
[ -s "$ECO_OUT/summary.tsv" ] && column -t -s $'\t' "$ECO_OUT/summary.tsv"
