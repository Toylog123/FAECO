#!/usr/bin/env bash
# 常量网（1'h0/1'h1 直接赋值的 wire）→ tie cell 修复后重跑
#
# 报错：DRT-0305 Net one_ of signal type POWER is not routable by TritonRoute
# 原因：OpenROAD 的 Verilog 前端口把 `assign X = 1'h1;` 建成名为 one_ 的 POWER 网；
#       26Q3 的 TritonRoute 拒绝布 POWER 网（v2.0 不检查，才"能跑"）。
# 修法：yosys hilomap 把常量换成库内 tie cell sky130_fd_sc_hd__conb_1（liberty/LEF 均存在）。
# 已实测：对无常量的电路（s27）hilomap 输出与原文逐字节相同，故该修法不引入额外差异。
set -uo pipefail

R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
BASE=/home/toylog/faeco_eda
OSS=$BASE/oss-latest
Y=$OSS/bin/yosys
export YOSYS_DATDIR=$OSS/share/yosys
LIB=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
OR=$BASE/or26Q3/bin/openroad
STA=$BASE/or26Q3/bin/sta

ISC_IN=$R/experiments/20261029_iscas17_yosys_latest/_in
ISC_OUT=$R/experiments/20261029_openroad26q3
ISC_SDC=$R/experiments/20261029_iscas17_yosys_latest/paper_sta_0p5.sdc

ITC_IN=$R/experiments/20261029_itc99_physical/_in
ITC_OUT=$R/experiments/20261029_itc99_26q3
ITC_SDC=$R/experiments/20261029_itc99_physical/paper_sta_0p5.sdc

remap () {  # $1=src.v $2=top $3=outdir
  local src=$1 top=$2 out=$3
  mkdir -p "$out"
  "$Y" -q -p "read_verilog $src; synth -top $top -flatten; \
dfflibmap -liberty $LIB; abc -liberty $LIB; \
hilomap -hicell sky130_fd_sc_hd__conb_1 HI -locell sky130_fd_sc_hd__conb_1 LO; \
clean; write_verilog -noattr $out/mapped.v" > "$out/map_hilo.log" 2>&1
  if [ -s "$out/mapped.v" ]; then
    echo "  $top $(stat -c%s "$out/mapped.v") B  常量=$(grep -cE "1'h[01]" "$out/mapped.v")  conb=$(grep -c conb_1 "$out/mapped.v")"
    return 0
  fi
  echo "  $top 映射失败: $(head -3 "$out/map_hilo.log" | tr '\n' ' ')"
  return 1
}

run_phys () {  # $1=top $2=outdir $3=sdc
  local top=$1 out=$2 sdc=$3 ok=0 u rc
  rm -f "$out/$top.spef" "$out/$top.def" "$out/$top.routed.v"
  for u in 35 20 15 5; do
    POSTCTS_LEGALIZE=1 PIN_ACCESS=1 OR_BIN="$OR" \
      timeout 1800 bash "$R/code/scripts/run_physical_flow_sky130.sh" \
      -n "$out/mapped.v" -t "$top" --sdc "$sdc" -o "$out" --util $u > "$out.runlog" 2>&1
    rc=$?
    if [ -s "$out/$top.spef" ]; then ok=1; echo "  $top util=$u 成功"; break; fi
    if [ "$rc" -eq 124 ]; then echo "  $top util=$u 超时"; break; fi
    echo "  $top util=$u 失败：$(grep -oE 'DRT-0[0-9]+|RCX-0[0-9]+|order_wires failed' "$out.runlog" | head -1)"
  done
  [ "$ok" -eq 1 ] || echo "  $top 未产出 SPEF"
  rm -f "$out/route.guide" "$R/route.guide"
}

sta_pair () {  # $1=top $2=outdir $3=sdc
  local top=$1 out=$2 sdc=$3 iw it pw pt dw dt
  [ -s "$out/$top.routed.v" ] || { echo "  $top 无 routed.v"; return; }
  cat > "$out/sta_ideal.tcl" <<EOT
read_liberty $LIB
read_verilog $out/$top.routed.v
link_design $top
source $sdc
report_worst_slack -max
report_tns
EOT
  cat > "$out/sta_post.tcl" <<EOT
read_liberty $LIB
read_verilog $out/$top.routed.v
link_design $top
source $sdc
read_spef $out/$top.spef
report_worst_slack -max
report_tns
EOT
  iw=$("$STA" -no_init -exit "$out/sta_ideal.tcl" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}')
  it=$("$STA" -no_init -exit "$out/sta_ideal.tcl" 2>/dev/null | grep -m1 "tns max" | awk '{print $3}')
  pw=$("$STA" -no_init -exit "$out/sta_post.tcl" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}')
  pt=$("$STA" -no_init -exit "$out/sta_post.tcl" 2>/dev/null | grep -m1 "tns max" | awk '{print $3}')
  dw=$(awk -v a="$pw" -v b="$iw" 'BEGIN{printf "%.4f", a-b}')
  dt=$(awk -v a="$pt" -v b="$it" 'BEGIN{printf "%.4f", a-b}')
  echo "  $top ideal $iw/$it  post $pw/$pt  dWNS=$dw dTNS=$dt"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$top" "$iw" "$it" "$pw" "$pt" "$dw" "$dt" >> "$4"
}

echo "== A. ISCAS: s713 s444 =="
for c in s713 s444; do
  remap "$ISC_IN/$c.v" "$c" "$ISC_OUT/$c" || continue
  run_phys "$c" "$ISC_OUT/$c" "$ISC_SDC"
  sta_pair "$c" "$ISC_OUT/$c" "$ISC_SDC" "$ISC_OUT/phys_hilo_26q3.tsv"
done

echo
echo "== B. ITC99: b11 b13 =="
for c in b11 b13; do
  remap "$ITC_IN/$c.v" "$c" "$ITC_OUT/$c" || continue
  run_phys "$c" "$ITC_OUT/$c" "$ITC_SDC"
  sta_pair "$c" "$ITC_OUT/$c" "$ITC_SDC" "$ITC_OUT/phys_itc_hilo.tsv"
done
