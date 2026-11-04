#!/usr/bin/env bash
# ITC'99 b11/b12/b13 · OpenROAD 26Q3 栈（**只在 WSL 内运行**）
#
#   wsl.exe -d Ubuntu -- bash code/scripts/run_itc99_physical_26q3.sh
#
# 与 run_itc99_physical_wsl.sh（v2.0 族）唯一差异：换 26Q3 的 openroad / sta，
# 并补 POSTCTS_LEGALIZE=1 + PIN_ACCESS=1。网表与 SDC 完全沿用旧族。
# b* 与 s* 严格分族，不拼表。
set -uo pipefail

R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
BASE=/home/toylog/faeco_eda
OR=$BASE/or26Q3/bin/openroad
STA=$BASE/or26Q3/bin/sta

SRC=$R/experiments/20261029_itc99_physical
OUT=$R/experiments/20261029_itc99_26q3
PLAT=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629
LIB=$PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
SDC=$SRC/paper_sta_0p5.sdc
CASES=${CASES:-"b13 b11 b12"}

mkdir -p "$OUT"

echo "== 工具 =="
echo -n "  openroad: "; "$OR" -version 2>&1 | head -1
echo -n "  sta     : "; "$STA" -version 2>&1 | head -1
echo

echo "== 1/3 复用旧族网表 =="
for c in $CASES; do
  mkdir -p "$OUT/$c"
  if [ -s "$SRC/$c/mapped.v" ]; then
    cp -p "$SRC/$c/mapped.v" "$OUT/$c/mapped.v"
    echo "  $c $(stat -c%s "$OUT/$c/mapped.v") B"
  else
    echo "  $c 旧族无网表，跳过"
  fi
done
echo

echo "== 2/3 物理流程（26Q3）=="
for c in $CASES; do
  D=$OUT/$c
  [ -s "$D/mapped.v" ] || continue
  if [ -s "$D/$c.spef" ]; then
    echo "  $c 复用已有 SPEF"
    continue
  fi
  ok=0
  for U in 35 20 15 5; do
    POSTCTS_LEGALIZE=1 PIN_ACCESS=1 OR_BIN="$OR" \
      timeout 1800 bash "$R/code/scripts/run_physical_flow_sky130.sh" \
      -n "$D/mapped.v" -t "$c" --sdc "$SDC" -o "$D" --util $U > "$D.runlog" 2>&1
    rc=$?
    if [ -s "$D/$c.spef" ]; then ok=1; echo "  $c util=$U 成功"; break; fi
    if [ "$rc" -eq 124 ]; then echo "  $c util=$U 超时"; break; fi
    echo "  $c util=$U 失败：$(grep -oE 'DRT-00[0-9]+|RCX-[0-9]+|order_wires failed' "$D.runlog" | head -1)"
  done
  [ "$ok" -eq 1 ] || echo "  $c 布线后档未产出"
  rm -f "$D/route.guide" "$R/route.guide"
done
echo

echo "== 3/3 双档 STA =="
RESULT=$OUT/phys_itc_26q3.tsv
printf 'circuit\tideal_wns\tideal_tns\tpost_wns\tpost_tns\tdelta_wns\tdelta_tns\tutil\tdef_bytes\tspef_bytes\n' > "$RESULT"

sta_wns () { "$STA" -no_init -exit "$1" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}'; }
sta_tns () { "$STA" -no_init -exit "$1" 2>/dev/null | grep -m1 "tns max" | awk '{print $3}'; }

for c in $CASES; do
  D=$OUT/$c
  echo "######## $c ########"
  if [ ! -s "$D/$c.routed.v" ] && [ ! -s "$D/$c.spef" ]; then
    echo "  无布线后产物 → 记未评估"
    printf '%s\t-\t-\tNO_SPEF\t\t\t\t-\t\t\n' "$c" >> "$RESULT"
    continue
  fi
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
  if [ -z "$PW" ]; then
    printf '%s\t%s\t%s\tSTAFail\t\t\t\t-\t%s\t%s\n' "$c" "$IW" "$IT" \
      "$(stat -c%s "$D/$c.def" 2>/dev/null || echo 0)" "$(stat -c%s "$D/$c.spef" 2>/dev/null || echo 0)" >> "$RESULT"
    echo "  ideal $IW ；post 无输出"
    continue
  fi
  DW=$(awk -v a="$PW" -v b="$IW" 'BEGIN{printf "%.4f", a-b}')
  DT=$(awk -v a="$PT" -v b="$IT" 'BEGIN{printf "%.4f", a-b}')
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$IW" "$IT" "$PW" "$PT" "$DW" "$DT" \
    "routed" "$(stat -c%s "$D/$c.def")" "$(stat -c%s "$D/$c.spef")" >> "$RESULT"
  echo "  ideal $IW / $IT   post $PW / $PT   dWNS=$DW dTNS=$DT"
done

echo
echo "===== 汇总 ====="
column -t -s $'\t' "$RESULT"
