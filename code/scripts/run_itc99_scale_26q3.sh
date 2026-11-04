#!/usr/bin/env bash
# ITC'99 大规模补测（b14/b15/b17 …）· OpenROAD 26Q3 栈（**只在 WSL 内运行**）
#
#   wsl.exe -d Ubuntu -- bash code/scripts/run_itc99_scale_26q3.sh
#   可选：STAGE=map|phys|all（默认 all）；CASES="b14 b15 b17"；UTILS="35 25 15 5"
#         PHYS_TIMEOUT=7200
#
# 目的
#   论文 §4.3 的 ITC-99 是 19 例，其中 b14/b15/b17/b20/b21/b22 是「大规模」主力。
#   已有物理档只有 b11/b12/b13（292/629/174 cells），规模差两个数量级。
#   本脚本把小例补到含大例的 6 例，物理档才有资格进正文。
#
# 与 run_itc99_physical_26q3.sh 的差异
#   1) 不复用旧族网表（旧族没有 b14/b15/b17），直接在本目录映射；
#   2) 映射**恒带 hilomap**（大例普遍有 `assign X = 1'h1;`，会被 26Q3 的 DRT-0305 拒）；
#      对无常量电路 hilomap 输出与原 mapped.v 逐字节相同，已验证（s27）。
#   3) 大例放宽 timeout，util 逐档下探。
#
# 族纪律
#   b* 与 s* 严格分族，禁拼表。dff 端口序 (CK,D,Q) 与 ISCAS'89 的 (CK,Q,D) 相反，
#   定义与实例化在同一文件内自洽，切勿交叉套用。
set -uo pipefail

R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
BASE=/home/toylog/faeco_eda
OSS=${OSS:-$BASE/oss-latest}
Y=$OSS/bin/yosys
export YOSYS_DATDIR=$OSS/share/yosys
OR=$BASE/or26Q3/bin/openroad
STA=$BASE/or26Q3/bin/sta

SRC=$R/data/raw/benchmarks/raw/itc99/v
PLAT=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629
LIB=$PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
SDC=$R/experiments/20261029_itc99_physical/paper_sta_0p5.sdc
OUT=$R/experiments/20261029_itc99_scale_26q3
IN=$OUT/_in

CASES=${CASES:-"b14 b15 b17"}
STAGE=${STAGE:-all}
UTILS=${UTILS:-"35 25 15 5"}
PHYS_TIMEOUT=${PHYS_TIMEOUT:-7200}

mkdir -p "$OUT" "$IN"

echo "== 工具 =="
$Y -V 2>&1 | head -1
"$OR" -version 2>&1 | head -1
"$STA" -version 2>&1 | head -1
echo

# ---------- 1/3 输入核对 ----------
echo "== 1/3 输入核对 =="
printf 'circuit\tbytes\tlines\tdff_inst\tdff_port_order\tck_port\n' > "$OUT/input_itc_scale.tsv"
for c in $CASES; do
  s=$SRC/$c.v
  [ -s "$s" ] || { echo "  缺输入 $s"; exit 4; }
  cp -f "$s" "$IN/$c.v"
  nd=$(grep -cE '^[[:space:]]*dff[[:space:]]' "$IN/$c.v")
  po=$(grep -m1 -oE 'module dff\([^)]*\)' "$IN/$c.v" | tr -d ' ')
  ck=$(grep -m1 '^module ' "$IN/$c.v" | grep -c 'CK')
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$(stat -c%s "$IN/$c.v")" \
    "$(wc -l < "$IN/$c.v")" "$nd" "${po:-none}" "$ck" >> "$OUT/input_itc_scale.tsv"
  echo "   $c  $(stat -c%s "$IN/$c.v") B  dff=$nd  ${po:-none}  CK端口=$ck"
  [ "$ck" -eq 1 ] || { echo "   $c 顶层无 CK 端口，口径不成立"; exit 4; }
done
echo

# ---------- 2/3 映射（恒带 hilomap） ----------
map_one () {  # $1=top
  local c=$1 D=$OUT/$1
  mkdir -p "$D"
  "$Y" -q -p "read_verilog $IN/$c.v; synth -top $c -flatten; \
dfflibmap -liberty $LIB; abc -liberty $LIB; \
hilomap -hicell sky130_fd_sc_hd__conb_1 HI -locell sky130_fd_sc_hd__conb_1 LO; \
clean; write_verilog -noattr $D/mapped.v" > "$D/map_hilo.log" 2>&1
  if [ -s "$D/mapped.v" ]; then
    local cells dfx cons
    cells=$(grep -cE '^[[:space:]]+sky130_fd_sc_hd__' "$D/mapped.v")
    dfx=$(grep -c 'sky130_fd_sc_hd__dfxtp' "$D/mapped.v")
    cons=$(grep -cE "1'h[01]" "$D/mapped.v")
    echo "   $c mapped=$(stat -c%s "$D/mapped.v") B  cells=$cells  dfxtp=$dfx  残留常量=$cons"
    return 0
  fi
  echo "   $c 映射失败: $(head -5 "$D/map_hilo.log" | tr '\n' ' ')"
  return 1
}

if [ "$STAGE" = "map" ] || [ "$STAGE" = "all" ]; then
  echo "== 2/3 映射（synth -flatten + dfflibmap + abc + hilomap）=="
  for c in $CASES; do
    t0=$(date +%s)
    map_one "$c" && echo "     耗时 $(( $(date +%s) - t0 )) s"
  done
  echo
fi

if [ "$STAGE" = "map" ]; then
  echo "STAGE=map，结束。"
  exit 0
fi

# ---------- 3/3 物理流程 + 双档 STA ----------
RESULT=$OUT/phys_itc_scale_26q3.tsv
if [ ! -s "$RESULT" ]; then
  printf 'circuit\tideal_wns\tideal_tns\tpost_wns\tpost_tns\tdelta_wns\tdelta_tns\tutil\tdef_bytes\tspef_bytes\n' > "$RESULT"
fi

sta_wns () { "$STA" -no_init -exit "$1" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}'; }
sta_tns () { "$STA" -no_init -exit "$1" 2>/dev/null | grep -m1 "tns max" | awk '{print $3}'; }

for c in $CASES; do
  D=$OUT/$c
  echo "######## $c ########"
  if [ ! -s "$D/mapped.v" ]; then
    echo "  无网表，跳过"
    continue
  fi

  if [ -s "$D/$c.spef" ]; then
    echo "  复用已有 SPEF"
    USED=$(awk -F'\t' -v k="$c" '$1==k{print $8}' "$RESULT" 2>/dev/null | tail -1)
    USED=${USED:-reuse}
  else
    USED=""
    for U in $UTILS; do
      t0=$(date +%s)
      POSTCTS_LEGALIZE=1 PIN_ACCESS=1 OR_BIN="$OR" \
        timeout "$PHYS_TIMEOUT" bash "$R/code/scripts/run_physical_flow_sky130.sh" \
        -n "$D/mapped.v" -t "$c" --sdc "$SDC" -o "$D" --util $U > "$D.runlog" 2>&1
      rc=$?
      el=$(( $(date +%s) - t0 ))
      if [ -s "$D/$c.spef" ]; then
        echo "  util=$U 成功（${el}s）"; USED=$U; break
      fi
      if [ "$rc" -eq 124 ]; then
        echo "  util=$U 超时（${el}s，上限 ${PHYS_TIMEOUT}s）"
        USED="TIMEOUT"
        break
      fi
      echo "  util=$U 失败（${el}s）：$(grep -oE 'DRT-0[0-9]+|RCX-0[0-9]+|order_wires failed|ERROR [A-Z]+-[0-9]+' "$D.runlog" | head -1)"
    done
    rm -f "$D/route.guide" "$R/route.guide"
  fi

  if [ ! -s "$D/$c.routed.v" ]; then
    echo "  无 routed.v → 记未评估"
    printf '%s\t-\t-\tNO_ROUTED\t\t\t\t%s\t\t\n' "$c" "${USED:-none}" >> "$RESULT"
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
  PW=$(sta_wns "$D/sta_post.tcl");  PT=$(sta_tns "$D/sta_post.tcl")
  if [ -z "$PW" ]; then
    printf '%s\t%s\t%s\tSTAFail\t\t\t\t%s\t\t\n' "$c" "${IW:--}" "${IT:--}" "${USED:-none}" >> "$RESULT"
    echo "  ideal $IW ；post 无输出"
    continue
  fi
  DW=$(awk -v a="$PW" -v b="$IW" 'BEGIN{printf "%.4f", a-b}')
  DT=$(awk -v a="$PT" -v b="$IT" 'BEGIN{printf "%.4f", a-b}')
  # 触发器守恒核对：mapped.v 与 routed.v 的 dfxtp 必须相等
  CM=$(grep -c 'sky130_fd_sc_hd__dfxtp' "$D/mapped.v")
  CR=$(grep -c 'sky130_fd_sc_hd__dfxtp' "$D/$c.routed.v")
  GUARD="OK"; [ "$CM" = "$CR" ] || GUARD="MISMATCH($CM/$CR)"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$IW" "$IT" "$PW" "$PT" "$DW" "$DT" \
    "${USED:-none}" "$(stat -c%s "$D/$c.def")" "$(stat -c%s "$D/$c.spef")" >> "$RESULT"
  echo "  ideal $IW / $IT   post $PW / $PT   dWNS=$DW dTNS=$DT   dfxtp $CM→$CR [$GUARD]"
done

echo
echo "===== 汇总 ====="
column -t -s $'\t' "$RESULT"
