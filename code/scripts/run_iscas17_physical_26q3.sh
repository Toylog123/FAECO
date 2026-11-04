#!/usr/bin/env bash
# ISCAS89 17 例 · OpenROAD 26Q3 栈（**只在 WSL 内运行**）
#
#   wsl.exe -d Ubuntu -- bash code/scripts/run_iscas17_physical_26q3.sh
#
# 与 run_iscas17_physical_wsl.sh（v2.0 族）的唯一差异：
#   - OpenROAD 二进制换成 26Q3（/home/toylog/faeco_eda/or26Q3/bin/openroad）
#   - STA 换成同源 26Q3 自带 sta
#   - 物理流程补 POSTCTS_LEGALIZE=1 + PIN_ACCESS=1（26Q3 官方 flow.tcl 顺序）
# 网表、SDC、liberty、平台资产**完全沿用旧族**，因此两族逐例可比，
# 差异只来自工具版本（换栈即换数字，两族数字不得拼表）。
set -uo pipefail

R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
BASE=/home/toylog/faeco_eda
OR=$BASE/or26Q3/bin/openroad
STA=$BASE/or26Q3/bin/sta

SRC=$R/experiments/20261029_iscas17_yosys_latest
OUT=$R/experiments/20261029_openroad26q3
PLAT=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629
LIB=$PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
SDC=$SRC/paper_sta_0p5.sdc

BASE8="s27 s382 s420 s641 s713 s820 s832 s953"
NEW9="s298 s344 s349 s386 s400 s444 s510 s526 s838"
ONLY=${CASES:-"$BASE8 $NEW9"}

mkdir -p "$OUT"

echo "== 工具 =="
echo -n "  openroad: "; "$OR" -version 2>&1 | head -1
echo -n "  sta     : "; "$STA" -version 2>&1 | head -1
echo

echo "== 1/3 复用旧族网表（同网表是可比性前提）=="
for c in $ONLY; do
  D=$OUT/$c
  mkdir -p "$D"
  if [ -s "$SRC/$c/mapped.v" ]; then
    cp -p "$SRC/$c/mapped.v" "$D/mapped.v"
    echo "  $c $(stat -c%s "$D/mapped.v") B"
  else
    echo "  $c 旧族无网表，跳过"
  fi
done
echo

echo "== 2/3 物理流程（26Q3）=="
def2v () {
  local c=$1 D=$OUT/$1
  cat > "$D/def2v.tcl" <<EOT
read_lef $PLAT/lef/sky130_fd_sc_hd.tlef
read_lef $PLAT/lef/sky130_fd_sc_hd_merged.lef
read_liberty $LIB
read_def $D/$c.def
write_verilog $D/$c.routed.v
EOT
  "$OR" -no_init -exit -log "$D/def2v.log" "$D/def2v.tcl" > /dev/null 2>&1
  [ -s "$D/$c.routed.v" ]
}

for c in $ONLY; do
  D=$OUT/$c
  [ -s "$D/mapped.v" ] || { echo "  $c 无网表，跳过"; continue; }
  if [ -s "$D/$c.spef" ]; then
    echo "  $c 复用已有 DEF/SPEF（$(stat -c%s "$D/$c.spef") B）"
  else
    ok=0
    for U in 35 15 5; do
      POSTCTS_LEGALIZE=1 PIN_ACCESS=1 OR_BIN="$OR" \
        timeout 900 bash "$R/code/scripts/run_physical_flow_sky130.sh" \
        -n "$D/mapped.v" -t "$c" --sdc "$SDC" -o "$D" --util $U > "$D.runlog" 2>&1
      rc=$?
      if [ -s "$D/$c.spef" ]; then ok=1; echo "  $c util=$U 成功"; break; fi
      if [ "$rc" -eq 124 ]; then echo "  $c util=$U 超时挂死"; break; fi
      echo "  $c util=$U 失败：$(grep -oE 'DRT-00[0-9]+|RCX-[0-9]+|order_wires failed' "$D.runlog" | head -1)"
    done
    [ "$ok" -eq 1 ] || echo "  $c 布线后档未产出"
  fi
  if [ ! -s "$D/$c.routed.v" ] && [ -s "$D/$c.def" ]; then
    def2v "$c" && echo "  $c routed.v 由 DEF 复原（$(stat -c%s "$D/$c.routed.v") B）"
  fi
  rm -f "$D/route.guide" "$R/route.guide"
done
echo

echo "== 3/3 双档 STA（同一份 routed.v，26Q3 自带 sta）=="
RESULT=$OUT/phys17_26q3.tsv
printf 'circuit\tgroup\tideal_wns\tideal_tns\tpost_wns\tpost_tns\tdelta_wns\tdelta_tns\tutil\tdef_bytes\tspef_bytes\n' > "$RESULT"

sta_wns () { "$STA" -no_init -exit "$1" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}'; }
sta_tns () { "$STA" -no_init -exit "$1" 2>/dev/null | grep -m1 "tns max" | awk '{print $3}'; }

for c in $ONLY; do
  D=$OUT/$c
  grp=base8; case " $NEW9 " in *" $c "*) grp=new9 ;; esac
  echo "######## $c ($grp) ########"
  if [ ! -s "$D/$c.routed.v" ]; then
    echo "  无布线后网表 → 记为未评估"
    printf '%s\t%s\t-\t-\tNO_ROUTED_V\t\t\t\t-\t\t\n' "$c" "$grp" >> "$RESULT"
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
  if [ ! -s "$D/$c.spef" ]; then
    printf '%s\t%s\t%s\t%s\tNO_SPEF\t\t\t\t-\t%s\t\n' "$c" "$grp" "$IW" "$IT" "$(stat -c%s "$D/$c.def" 2>/dev/null || echo 0)" >> "$RESULT"
    echo "  ideal $IW / $IT ；无 SPEF，布线后档未评估"
    continue
  fi
  PW=$(sta_wns "$D/sta_post.tcl"); PT=$(sta_tns "$D/sta_post.tcl")
  if [ -z "$PW" ]; then
    printf '%s\t%s\t%s\t%s\tSTAFail\t\t\t\t-\t%s\t%s\n' "$c" "$grp" "$IW" "$IT" \
      "$(stat -c%s "$D/$c.def")" "$(stat -c%s "$D/$c.spef")" >> "$RESULT"
    echo "  ideal $IW ；read_spef 后无输出"
    continue
  fi
  DW=$(awk -v a="$PW" -v b="$IW" 'BEGIN{printf "%.4f", a-b}')
  DT=$(awk -v a="$PT" -v b="$IT" 'BEGIN{printf "%.4f", a-b}')
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$grp" "$IW" "$IT" "$PW" "$PT" "$DW" "$DT" \
    "routed" "$(stat -c%s "$D/$c.def")" "$(stat -c%s "$D/$c.spef")" >> "$RESULT"
  echo "  ideal $IW / $IT   post $PW / $PT   dWNS=$DW dTNS=$DT"
done

echo
echo "===== 汇总 ====="
column -t -s $'\t' "$RESULT"
