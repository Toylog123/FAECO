#!/usr/bin/env bash
# ISCAS89 17 例（8 论文用例 + 9 扩面）物理档复现驱动（**只在 WSL 内运行**）
#
#   wsl.exe -d Ubuntu -- bash code/scripts/run_iscas17_physical_wsl.sh
#   可选环境变量：SKIP_PREP=1 跳过前处理；SKIP_MAP=1 跳过映射；OSS=<oss-cad-suite 根>
#
# 流程：统一输入 → yosys 映射(synth -flatten) → OpenROAD 物理流程 → 双档 STA
# 口径要点：双档都读 <top>.routed.v（布线后网表，含 CTS 缓冲），
#   ideal = 该网表 + SDC（无寄生）；post = 该网表 + SDC + read_spef。
#   差异只来自线网寄生，不含"布局前/布线后网表不同"这个混淆因素。
#   若首轮未写 routed.v，则从 DEF 复原（def2v），并在日志中标注。
#
# 依赖：与论文主实验相同的 liberty 与 sky130hd 平台资产（已归档 data/raw）；
#       yosys 0.70+255（oss-cad-suite nightly 20261028）、openroad v2.0、OpenSTA 3.1.0。
set -uo pipefail

R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
BASE=/home/toylog/faeco_eda
OSS=${OSS:-$BASE/oss-latest}
Y=$OSS/bin/yosys
export YOSYS_DATDIR=$OSS/share/yosys

OUT=$R/experiments/20261029_iscas17_yosys_latest
PLAT=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629
LIB=$PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
IN=$OUT/_in
PRE=$OUT/_preprocessed

BASE8="s27 s382 s420 s641 s713 s820 s832 s953"
NEW9="s298 s344 s349 s386 s400 s444 s510 s526 s838"

mkdir -p "$OUT"

echo "== 工具 =="
$Y -V 2>&1 | head -1
sta -version 2>&1 | head -1
/usr/local/bin/openroad -version 2>&1 | head -1
echo

if [ "${SKIP_PREP:-0}" != "1" ]; then
  echo "== 1/4 前处理 =="
  python3 "$R/code/scripts/wsl_preprocess_iscas9.py" "$PRE" || exit 4
  python3 "$R/code/scripts/wsl_build_inputs17.py" || exit 4
  echo
fi

if [ "${SKIP_MAP:-0}" != "1" ]; then
  echo "== 2/4 映射（synth -flatten）=="
  printf 'circuit\tbytes\tsha256\tleftover_internal\tleftover_dff\tdfxtp_cells\n' > "$OUT/map17.tsv"
  map_one () {
    local c=$1
    mkdir -p "$OUT/$c"
    $Y -q -p "read_verilog $IN/$c.v; synth -top $c -flatten; \
dfflibmap -liberty $LIB; abc -liberty $LIB; clean; \
write_verilog -noattr $OUT/$c/mapped.v" > "$OUT/$c/map.log" 2>&1
    if [ ! -s "$OUT/$c/mapped.v" ]; then
      echo "   $c 映射失败：$(head -2 "$OUT/$c/map.log" | tr '\n' ' ')"
      printf '%s\t0\t-\tMAPFAIL\t-\t0\n' "$c" >> "$OUT/map17.tsv"
      return 1
    fi
    local left dfl dfx
    left=$(grep -oE '\$_[A-Z][A-Z0-9_]*' "$OUT/$c/mapped.v" | sort -u | tr '\n' ' ')
    dfl=$(grep -cE '^[[:space:]]+dff ' "$OUT/$c/mapped.v" || true)
    dfx=$(grep -oE 'sky130_fd_sc_hd__df[a-z0-9_]+' "$OUT/$c/mapped.v" | wc -l)
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$(stat -c%s "$OUT/$c/mapped.v")" \
      "$(sha256sum "$OUT/$c/mapped.v" | awk '{print $1}')" "${left:-none}" "$dfl" "$dfx" >> "$OUT/map17.tsv"
    echo "   $c  $(stat -c%s "$OUT/$c/mapped.v") B  内部单元=${left:-none} 残留dff=$dfl dfxtp=$dfx"
  }
  for c in $BASE8 $NEW9; do map_one "$c"; done
  echo
fi

echo "== 3/4 物理流程 =="
SDC=$OUT/paper_sta_0p5.sdc
printf 'create_clock -name clk -period 0.5 [get_ports CK]\n' > "$SDC"

def2v () {  # 从 DEF 复原布线后网表
  local c=$1 D=$OUT/$1
  cat > "$D/def2v.tcl" <<EOT
read_lef $PLAT/lef/sky130_fd_sc_hd.tlef
read_lef $PLAT/lef/sky130_fd_sc_hd_merged.lef
read_liberty $LIB
read_def $D/$c.def
write_verilog $D/$c.routed.v
EOT
  openroad -no_init -exit -log "$D/def2v.log" "$D/def2v.tcl" > /dev/null 2>&1
  [ -s "$D/$c.routed.v" ]
}

for c in $BASE8 $NEW9; do
  D=$OUT/$c
  [ -s "$D/mapped.v" ] || { echo "  $c 无网表，跳过"; continue; }
  if [ -s "$D/$c.spef" ]; then
    echo "  $c 复用已有 DEF/SPEF（$(stat -c%s "$D/$c.spef") B）"
  else
    ok=0
    for U in 35 15 5; do
      timeout 420 bash "$R/code/scripts/run_physical_flow_sky130.sh" \
        -n "$D/mapped.v" -t "$c" --sdc "$SDC" -o "$D" --util $U > "$D.runlog" 2>&1
      rc=$?
      if [ -s "$D/$c.spef" ]; then ok=1; echo "  $c util=$U 成功"; break; fi
      if [ "$rc" -eq 124 ]; then echo "  $c util=$U 超时挂死"; break; fi
      echo "  $c util=$U 失败：$(grep -oE 'DRT-00[0-9]+|order_wires failed' "$D.runlog" | head -1)"
    done
    [ "$ok" -eq 1 ] || echo "  $c 布线后档未产出"
  fi
  if [ ! -s "$D/$c.routed.v" ] && [ -s "$D/$c.def" ]; then
    def2v "$c" && echo "  $c routed.v 由 DEF 复原（$(stat -c%s "$D/$c.routed.v") B）"
  fi
  rm -f "$D/route.guide" "$R/route.guide"
done
echo

echo "== 4/4 双档 STA（同一份 routed.v）=="
RESULT=$OUT/phys17.tsv
printf 'circuit\tgroup\tideal_wns\tideal_tns\tpost_wns\tpost_tns\tdelta_wns\tdelta_tns\tutil\tdef_bytes\tspef_bytes\n' > "$RESULT"

sta_wns () { sta -no_init -exit "$1" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}'; }
sta_tns () { sta -no_init -exit "$1" 2>/dev/null | grep -m1 "tns max" | awk '{print $3}'; }

for c in $BASE8 $NEW9; do
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
echo "===== 17 例 ====="
column -t -s $'\t' "$RESULT"
