#!/usr/bin/env bash
# ECO 前后 · 物理档四数对照（base/eco × ideal/post）· OpenROAD 26Q3（**只在 WSL 内运行**）
#
#   wsl.exe -d Ubuntu -- bash code/scripts/run_eco_phys_contrast.sh
#   可选：CASES="s27 s382"  ARM=pureG  UTILS="35 25 15"
#
# 为什么要有这个脚本
#   之前那批（run_iscas17_physical_26q3.sh / run_itc99_*）测的是
#       Δ = W_同一网表_布线后 − W_同一网表_理想档
#   它只说明「寄生让这个电路整体差多少」，**不能**回答「ECO 的改善在物理档还剩多少」。
#   论文要的是四数对照：
#                  预布局(ideal)   布线后(post)
#       基线 base        A                B
#       ECO  eco         C                D
#   理想档改善 = C−A；物理档改善 = D−B；保持率 = (D−B)/(C−A)。
#
# 为什么要先清理网表
#   主实验网表（20260826_*）里 `dff` 是**行为级黑盒子模块**且未 flatten：
#   s641 有 19 个 dff 实例但全设计只有 1 个 dfxtp ⇒ 触发器不进时序，路径断开。
#   直接跑物理流程得到的是残缺电路。故 base 与 ECO **都**走同一条清理链：
#       read_verilog → hierarchy -top → flatten → dfflibmap -liberty → hilomap → clean
#   两边处理完全一致，唯一差异是 ECO 本身。**不得只清一边**。
#
# 口径
#   base/eco 各自独立 floorplan→place→CTS→route→SPEF（真实 ECO 后要重新布线），
#   差异里含布局差异；同布局对照（固定 DEF）另做，见 --same-layout（本版未启用）。
set -uo pipefail

R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
BASE=/home/toylog/faeco_eda
OSS=${OSS:-$BASE/oss-latest}
Y=$OSS/bin/yosys
export YOSYS_DATDIR=$OSS/share/yosys
OR=$BASE/or26Q3/bin/openroad
STA=$BASE/or26Q3/bin/sta

PLAT=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629
LIB=$PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
SDC=$R/experiments/20261029_iscas17_yosys_latest/paper_sta_0p5.sdc

MAIN=$R/experiments/20260826_iscas89_main
OUT=$R/experiments/20261029_eco_phys_contrast

CASES=${CASES:-"s27 s382"}
ARM=${ARM:-pureG}
UTILS=${UTILS:-"35 25 15"}
PHYS_TIMEOUT=${PHYS_TIMEOUT:-3600}

mkdir -p "$OUT"

echo "== 工具 =="
$Y -V 2>&1 | head -1
"$OR" -version 2>&1 | head -1
"$STA" -version 2>&1 | head -1
echo "  ARM=$ARM  CASES=$CASES"
echo

# ---------- 1/4 取原始网表 + 一致性核对 ----------
echo "== 1/4 取网表 =="
for c in $CASES; do
  D=$OUT/$c
  mkdir -p "$D/base" "$D/eco"
  b=$MAIN/$c/$c/mapped.v
  e=$R/experiments/20260826_ablation_$ARM/$c/mapped_hybrid.v
  [ -s "$b" ] || { echo "  缺 base: $b"; continue; }
  [ -s "$e" ] || { echo "  缺 eco : $e"; continue; }
  cp -f "$b" "$D/base/raw.v"
  cp -f "$e" "$D/eco/raw.v"
  printf '  %-5s base %s B (dfxtp=%s, dff=%s)  eco %s B (dfxtp=%s, dff=%s)  %s\n' "$c" \
    "$(stat -c%s "$b")" "$(grep -c 'sky130_fd_sc_hd__dfxtp' "$b")" "$(grep -cE '^[[:space:]]+dff[[:space:]]' "$b")" \
    "$(stat -c%s "$e")" "$(grep -c 'sky130_fd_sc_hd__dfxtp' "$e")" "$(grep -cE '^[[:space:]]+dff[[:space:]]' "$e")" \
    "$([ "$(md5sum < "$b")" = "$(md5sum < "$e")" ] && echo 'IDENTICAL!!' || echo 'differs')"
done
echo

# ---------- 2/4 同一条清理链 ----------
clean_one () {  # $1=电路 $2=base|eco
  local c=$1 k=$2 D=$OUT/$1/$2
  "$Y" -q -p "read_verilog $D/raw.v; hierarchy -top $c; flatten; \
dfflibmap -liberty $LIB; \
hilomap -hicell sky130_fd_sc_hd__conb_1 HI -locell sky130_fd_sc_hd__conb_1 LO; \
clean; write_verilog -noattr $D/clean.v" > "$D/clean.log" 2>&1
  if [ -s "$D/clean.v" ]; then
    local dfx subs
    dfx=$(grep -c 'sky130_fd_sc_hd__dfxtp' "$D/clean.v")
    subs=$(grep -cE '^module ' "$D/clean.v")
    printf '   %-5s %-4s clean=%s B  dfxtp=%s  modules=%s\n' "$c" "$k" \
      "$(stat -c%s "$D/clean.v")" "$dfx" "$subs"
    [ "$subs" -eq 1 ] || echo "      ⚠ 仍有子模块（未完全 flatten）"
    return 0
  fi
  echo "   $c/$k 清理失败: $(head -3 "$D/clean.log" | tr '\n' ' ')"
  return 1
}

echo "== 2/4 清理（flatten + dfflibmap + hilomap，两边同一处理）=="
for c in $CASES; do
  clean_one "$c" base || continue
  clean_one "$c" eco  || continue
  CM=$(grep -c 'sky130_fd_sc_hd__dfxtp' "$OUT/$c/base/clean.v")
  CE=$(grep -c 'sky130_fd_sc_hd__dfxtp' "$OUT/$c/eco/clean.v")
  [ "$CM" = "$CE" ] && echo "      dfxtp 守恒 OK（$CM）" || echo "      ⚠ dfxtp 不一致 base=$CM eco=$CE"
done
echo

# ---------- 3/4 物理流程（各自独立） ----------
run_phys () {  # $1=电路 $2=base|eco
  local c=$1 k=$2 D=$OUT/$1/$2 u rc
  if [ -s "$D/$c.spef" ]; then echo "   $c/$k 复用已有 SPEF"; return 0; fi
  for u in $UTILS; do
    POSTCTS_LEGALIZE=1 PIN_ACCESS=1 OR_BIN="$OR" \
      timeout "$PHYS_TIMEOUT" bash "$R/code/scripts/run_physical_flow_sky130.sh" \
      -n "$D/clean.v" -t "$c" --sdc "$SDC" -o "$D" --util $u > "$D.runlog" 2>&1
    rc=$?
    if [ -s "$D/$c.spef" ]; then echo "   $c/$k util=$u 成功"; echo "$u" > "$D/util.used"; return 0; fi
    [ "$rc" -eq 124 ] && { echo "   $c/$k util=$u 超时"; return 1; }
    echo "   $c/$k util=$u 失败：$(grep -oE 'DRT-0[0-9]+|RCX-0[0-9]+|order_wires failed' "$D.runlog" | head -1)"
  done
  echo "   $c/$k 未产出 SPEF"
  return 1
}

echo "== 3/4 物理流程 =="
for c in $CASES; do
  run_phys "$c" base
  run_phys "$c" eco
  rm -f "$OUT/$c/base/route.guide" "$OUT/$c/eco/route.guide" "$R/route.guide"
done
echo

# ---------- 4/4 四数 STA ----------
RESULT=$OUT/eco_phys_contrast.tsv
printf 'circuit\tarm\tbase_ideal\tbase_post\teco_ideal\teco_post\td_ideal\td_post\tretention\tutil_base\tutil_eco\n' > "$RESULT"

sta_pair () {  # $1=dir $2=top → 输出 "wns tns"
  local D=$1 c=$2
  [ -s "$D/$c.routed.v" ] || { echo ""; return; }
  cat > "$D/sta_ideal.tcl" <<EOT
read_liberty $LIB
read_verilog $D/$c.routed.v
link_design $c
source $SDC
report_worst_slack -max
EOT
  cat > "$D/sta_post.tcl" <<EOT
read_liberty $LIB
read_verilog $D/$c.routed.v
link_design $c
source $SDC
read_spef $D/$c.spef
report_worst_slack -max
EOT
  local iw pw
  iw=$("$STA" -no_init -exit "$D/sta_ideal.tcl" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}')
  pw=$("$STA" -no_init -exit "$D/sta_post.tcl"  2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}')
  echo "$iw $pw"
}

echo "== 4/4 四数 STA =="
for c in $CASES; do
  read -r BI BP <<< "$(sta_pair "$OUT/$c/base" "$c")"
  read -r EI EP <<< "$(sta_pair "$OUT/$c/eco"  "$c")"
  if [ -z "${BI:-}" ] || [ -z "${EI:-}" ]; then
    echo "   $c 缺读数 base=[$BI/$BP] eco=[$EI/$EP]"
    printf '%s\t%s\t%s\t%s\t%s\t%s\t-\t-\t-\t-\t-\n' "$c" "$ARM" "${BI:--}" "${BP:--}" "${EI:--}" "${EP:--}" >> "$RESULT"
    continue
  fi
  DI=$(awk -v c="$EI" -v a="$BI" 'BEGIN{printf "%.4f", c-a}')
  DP=$(awk -v d="$EP" -v b="$BP" 'BEGIN{printf "%.4f", d-b}')
  RET=$(awk -v d="$DP" -v i="$DI" 'BEGIN{ if (i+0==0) printf "NA"; else printf "%.3f", d/i }')
  UB=$(cat "$OUT/$c/base/util.used" 2>/dev/null || echo -)
  UE=$(cat "$OUT/$c/eco/util.used"  2>/dev/null || echo -)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$ARM" "$BI" "$BP" "$EI" "$EP" "$DI" "$DP" "$RET" "$UB" "$UE" >> "$RESULT"
  echo "   $c base $BI→$BP | eco $EI→$EP | d_ideal=$DI d_post=$DP 保持率=$RET"
done

echo
echo "===== 汇总 ====="
column -t -s $'\t' "$RESULT"
