#!/usr/bin/env bash
# ITC'99 b11/b13 常量网修复（hilomap 插 conb_1 tie cell）后重跑
#
# 背景：b11/b13 的映射网表含 `assign X = 1'h1;` 常量连接，OpenROAD 的 Verilog 前端
#   会把它建成名为 one_ 的网并标为 POWER 类型；26Q3 的 TritonRoute 拒绝布线
#   （DRT-0305 Net one_ of signal type POWER is not routable）。v2.0 的 DRT 不检查，
#   所以旧族"能跑"其实是把一条无驱动的常量当信号布了线。
# 处置：用 yosys hilomap 把常量换成库里的 tie cell sky130_fd_sc_hd__conb_1
#   （该单元在 liberty 与 LEF 中均存在）。
set -uo pipefail

R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
BASE=/home/toylog/faeco_eda
OSS=$BASE/oss-latest
Y=$OSS/bin/yosys
export YOSYS_DATDIR=$OSS/share/yosys
LIB=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
SDC=$R/experiments/20261029_itc99_physical/paper_sta_0p5.sdc
OUT=$R/experiments/20261029_itc99_26q3
OR=$BASE/or26Q3/bin/openroad
STA=$BASE/or26Q3/bin/sta
CASES=${CASES:-"b11 b13"}

echo "== 1/3 hilomap 重映射（只需常量网）=="
for c in $CASES; do
  D=$OUT/$c
  mkdir -p "$D"
  $Y -q -p "read_verilog $R/experiments/20261029_itc99_physical/_in/$c.v; \
synth -top $c -flatten; \
dfflibmap -liberty $LIB; abc -liberty $LIB; \
hilomap -hicell sky130_fd_sc_hd__conb_1 HI -locell sky130_fd_sc_hd__conb_1 LO; \
clean; write_verilog -noattr $D/mapped.v" > "$D/map_hilo.log" 2>&1
  if [ -s "$D/mapped.v" ]; then
    echo "  $c $(stat -c%s "$D/mapped.v") B  常量行=$(grep -cE "1'h[01]" "$D/mapped.v")  conb=$(grep -c conb_1 "$D/mapped.v")"
  else
    echo "  $c 映射失败：$(head -3 "$D/map_hilo.log" | tr '\n' ' ')"
  fi
done
echo

echo "== 2/3 物理流程 =="
for c in $CASES; do
  D=$OUT/$c
  [ -s "$D/mapped.v" ] || continue
  rm -f "$D/$c.spef" "$D/$c.def" "$D/$c.routed.v"
  ok=0
  for U in 35 20 15 5; do
    POSTCTS_LEGALIZE=1 PIN_ACCESS=1 OR_BIN="$OR" \
      timeout 1800 bash "$R/code/scripts/run_physical_flow_sky130.sh" \
      -n "$D/mapped.v" -t "$c" --sdc "$SDC" -o "$D" --util $U > "$D.runlog" 2>&1
    rc=$?
    if [ -s "$D/$c.spef" ]; then ok=1; echo "  $c util=$U 成功"; break; fi
    if [ "$rc" -eq 124 ]; then echo "  $c util=$U 超时"; break; fi
    echo "  $c util=$U 失败：$(grep -oE 'DRT-0[0-9]+|RCX-[0-9]+|order_wires failed' "$D.runlog" | head -1)"
  done
  [ "$ok" -eq 1 ] || echo "  $c 未产出 SPEF"
  rm -f "$D/route.guide" "$R/route.guide"
done
echo

echo "== 3/3 双档 STA =="
sta_wns () { "$STA" -no_init -exit "$1" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}'; }
sta_tns () { "$STA" -no_init -exit "$1" 2>/dev/null | grep -m1 "tns max" | awk '{print $3}'; }
for c in $CASES; do
  D=$OUT/$c
  [ -s "$D/$c.routed.v" ] || { echo "  $c 无 routed.v"; continue; }
  cat > "$D/sta_ideal.tcl" <<EOT
read_liberty $LIB
read_verilog $D/$c.routed.v
link_design $c
source $SDC
report_worst_slack -max
report_tns
EOT
  cat > "$D/sta_post.tcl" <<EOT
read_liberty $LIB
read_verilog $D/$c.routed.v
link_design $c
source $SDC
read_spef $D/$c.spef
report_worst_slack -max
report_tns
EOT
  IW=$(sta_wns "$D/sta_ideal.tcl"); IT=$(sta_tns "$D/sta_ideal.tcl")
  PW=$(sta_wns "$D/sta_post.tcl"); PT=$(sta_tns "$D/sta_post.tcl")
  DW=$(awk -v a="$PW" -v b="$IW" 'BEGIN{printf "%.4f", a-b}')
  DT=$(awk -v a="$PT" -v b="$IT" 'BEGIN{printf "%.4f", a-b}')
  echo "  $c ideal $IW/$IT  post $PW/$PT  dWNS=$DW dTNS=$DT"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$IW" "$IT" "$PW" "$PT" "$DW" "$DT" >> "$OUT/phys_itc_hilo.tsv"
done
