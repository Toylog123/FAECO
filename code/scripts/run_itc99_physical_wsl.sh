#!/usr/bin/env bash
# ITC'99 b11/b12/b13 物理档复现驱动（**只在 WSL 内运行**）
#
#   wsl.exe -d Ubuntu -- bash code/scripts/run_itc99_physical_wsl.sh
#   可选环境变量：STAGE=map|phys|all（默认 all）；OSS=<oss-cad-suite 根>
#
# 为什么单独成族
#   ITC'99 与 ISCAS'89 是两套独立基准（触发器数、端口、结构完全不同）。
#   按项目铁律 `same claim ⇒ same revision + same config family`，
#   b* 的数字不得与 s* 拼进同一张表，须单列一节。
#
# 输入形态（重要）
#   用官方 Verilog 版本 data/raw/benchmarks/raw/itc99/v/<c>.v，它由 yosys 0.9 生成，
#   已是门级网表且**自带 `module dff(input CK, D, output Q)` 与顶层 CK 端口**。
#   注意其 dff 端口序是 (CK, D, Q)，与 ISCAS'89 那批 (CK, Q, D) **相反**；
#   但两边模块定义与实例化都在同一文件内自洽，故各自 flatten 后语义正确。
#   切勿交叉套用 —— 这正是当初 ISCAS'89 补 dff 模型时踩过的坑。
#
# 为什么不用 BLIF
#   BLIF 的 `.latch` 无时钟字段，yosys 读成 $ff，techmap 后落成"使能恒 1 的透明锁存器"，
#   时序路径消失且不报错。若必须走 BLIF，须先显式注入时钟（见 code/scripts/blif2v_itc99.py，
#   本批未采用）。
#
# 口径（与 ISCAS'89 那批逐字一致）
#   SDC = create_clock -name clk -period 0.5 [get_ports CK]（与主实验 sta.tcl 同款，
#   无 I/O delay / load / driving cell）。
#   双档都读 <c>.routed.v；ideal 无寄生，post 加 read_spef。差异只来自线网寄生。
set -uo pipefail

R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
BASE=/home/toylog/faeco_eda
OSS=${OSS:-$BASE/oss-latest}
Y=$OSS/bin/yosys
export YOSYS_DATDIR=$OSS/share/yosys

OUT=$R/experiments/20261029_itc99_physical
SRC=$R/data/raw/benchmarks/raw/itc99/v
PLAT=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629
LIB=$PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
IN=$OUT/_in

# 由小到大：b13(53 dff) → b11(31 dff，组合更大) → b12(121 dff)
CASES=${CASES:-"b13 b11 b12"}
STAGE=${STAGE:-all}

mkdir -p "$OUT" "$IN"

echo "== 工具 =="
$Y -V 2>&1 | head -1
sta -version 2>&1 | head -1
/usr/local/bin/openroad -version 2>&1 | head -1
echo

# ---------- 1/4 输入核对 ----------
echo "== 1/4 输入核对 =="
printf 'circuit\tbytes\tlines\tdff_inst\tdff_port_order\tck_port\n' > "$OUT/input_itc.tsv"
for c in $CASES; do
  s=$SRC/$c.v
  [ -s "$s" ] || { echo "  缺输入 $s"; exit 4; }
  cp -f "$s" "$IN/$c.v"
  nd=$(grep -cE '^[[:space:]]*dff[[:space:]]' "$IN/$c.v")
  po=$(grep -m1 -oE 'module dff\([^)]*\)' "$IN/$c.v" | tr -d ' ')
  ck=$(grep -m1 '^module ' "$IN/$c.v" | grep -c 'CK')
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$(stat -c%s "$IN/$c.v")" \
    "$(wc -l < "$IN/$c.v")" "$nd" "${po:-none}" "$ck" >> "$OUT/input_itc.tsv"
  echo "   $c  $(stat -c%s "$IN/$c.v") B  dff=$nd  ${po:-none}  CK端口=$ck"
  [ "$ck" -eq 1 ] || { echo "   $c 顶层无 CK 端口，口径不成立"; exit 4; }
done
echo

# ---------- 2/4 映射 ----------
if [ "$STAGE" = "map" ] || [ "$STAGE" = "all" ]; then
  echo "== 2/4 映射（synth -flatten）=="
  printf 'circuit\tbytes\tsha256\tleftover_internal\tleftover_dff\tdfxtp_cells\tsrc_dff\n' > "$OUT/map_itc.tsv"
  for c in $CASES; do
    D=$OUT/$c; mkdir -p "$D"
    $Y -q -p "read_verilog $IN/$c.v; synth -top $c -flatten; \
dfflibmap -liberty $LIB; abc -liberty $LIB; clean; \
write_verilog -noattr $D/mapped.v" > "$D/map.log" 2>&1
    if [ ! -s "$D/mapped.v" ]; then
      echo "   $c 映射失败：$(head -3 "$D/map.log" | tr '\n' ' ')"
      printf '%s\t0\t-\tMAPFAIL\t-\t0\t-\n' "$c" >> "$OUT/map_itc.tsv"
      continue
    fi
    left=$(grep -oE '\$_[A-Z][A-Z0-9_]*' "$D/mapped.v" | sort -u | tr '\n' ' ')
    dfl=$(grep -cE '^[[:space:]]+dff ' "$D/mapped.v" || true)
    # 注意 grep -c 数的是行数，多实例同行会漏计，必须用 -o 再 wc -l
    dfx=$(grep -oE 'sky130_fd_sc_hd__df[a-z0-9_]+' "$D/mapped.v" | wc -l)
    nd=$(grep -cE '^[[:space:]]*dff[[:space:]]' "$IN/$c.v" || true)
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$(stat -c%s "$D/mapped.v")" \
      "$(sha256sum "$D/mapped.v" | awk '{print $1}')" "${left:-none}" "$dfl" "$dfx" "$nd" >> "$OUT/map_itc.tsv"
    echo "   $c  $(stat -c%s "$D/mapped.v") B  内部单元=${left:-none} 残留dff=$dfl dfxtp=$dfx / 源dff=$nd"
    # 守门一：不得残留未映射的内部单元（黑盒会让路径静默消失，只报 wns 0.00）
    if [ "${left:-none}" != "none" ]; then
      echo "   !! $c 存在未映射内部单元：$left —— 该例时序不可信"
    fi
    # 守门二：dfxtp 不得为 0；允许少于源 dff（opt 会删不可观测寄存器或合并等价寄存器），
    # 但差距超过 5% 视为异常，需人工核。
    if [ "$dfx" -eq 0 ]; then
      echo "   !! $c 无任何 dfxtp，触发器全部丢失"
    elif [ "$((nd - dfx))" -gt "$((nd / 20))" ]; then
      echo "   !! $c 触发器减少过多（dfxtp=$dfx 源=$nd），需核查"
    elif [ "$dfx" -ne "$nd" ]; then
      echo "   .. $c 触发器 $nd→$dfx，差值由 opt 删除不可观测寄存器所致（<5%）"
    fi
  done
  echo
fi

[ "$STAGE" = "map" ] && { echo "STAGE=map，结束"; exit 0; }

# ---------- 3/4 物理流程 ----------
echo "== 3/4 物理流程 =="
SDC=$OUT/paper_sta_0p5.sdc
printf 'create_clock -name clk -period 0.5 [get_ports CK]\n' > "$SDC"

def2v () {
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

for c in $CASES; do
  D=$OUT/$c
  [ -s "$D/mapped.v" ] || { echo "  $c 无网表，跳过"; continue; }
  if [ -s "$D/$c.spef" ]; then
    echo "  $c 复用已有 DEF/SPEF（$(stat -c%s "$D/$c.spef") B）"
  else
    ok=0
    # b12 约 s953 的 14 倍，单例给 40 min
    for U in 35 15 5; do
      timeout 2400 bash "$R/code/scripts/run_physical_flow_sky130.sh" \
        -n "$D/mapped.v" -t "$c" --sdc "$SDC" -o "$D" --util $U > "$D.runlog" 2>&1
      rc=$?
      if [ -s "$D/$c.spef" ]; then ok=1; echo "  $c util=$U 成功"; break; fi
      if [ "$rc" -eq 124 ]; then echo "  $c util=$U 超时挂死"; break; fi
      echo "  $c util=$U 失败：$(grep -oE 'DRT-00[0-9]+|order_wires failed|GPL-0[0-9]+' "$D.runlog" | head -1)"
    done
    [ "$ok" -eq 1 ] || echo "  $c 布线后档未产出"
  fi
  if [ ! -s "$D/$c.routed.v" ] && [ -s "$D/$c.def" ]; then
    def2v "$c" && echo "  $c routed.v 由 DEF 复原（$(stat -c%s "$D/$c.routed.v") B）"
  fi
  rm -f "$D/route.guide" "$R/route.guide"
done
echo

# ---------- 4/4 双档 STA ----------
echo "== 4/4 双档 STA（同一份 routed.v）=="
RESULT=$OUT/phys_itc.tsv
printf 'circuit\tideal_wns\tideal_tns\tpost_wns\tpost_tns\tdelta_wns\tdelta_tns\tutil\tdef_bytes\tspef_bytes\n' > "$RESULT"

sta_wns () { sta -no_init -exit "$1" 2>/dev/null | grep -m1 "worst slack max" | awk '{print $4}'; }
sta_tns () { sta -no_init -exit "$1" 2>/dev/null | grep -m1 "tns max" | awk '{print $3}'; }

for c in $CASES; do
  D=$OUT/$c
  echo "######## $c ########"
  if [ ! -s "$D/$c.routed.v" ]; then
    echo "  无布线后网表 → 记为未评估"
    printf '%s\t-\t-\tNO_ROUTED_V\t\t\t\t-\t\t\n' "$c" >> "$RESULT"
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
    printf '%s\t%s\t%s\tNO_SPEF\t\t\t\t-\t%s\t\n' "$c" "$IW" "$IT" \
      "$(stat -c%s "$D/$c.def" 2>/dev/null || echo 0)" >> "$RESULT"
    echo "  ideal $IW / $IT ；无 SPEF，布线后档未评估"
    continue
  fi
  PW=$(sta_wns "$D/sta_post.tcl"); PT=$(sta_tns "$D/sta_post.tcl")
  if [ -z "$PW" ]; then
    printf '%s\t%s\t%s\tSTAFail\t\t\t\t-\t%s\t%s\n' "$c" "$IW" "$IT" \
      "$(stat -c%s "$D/$c.def")" "$(stat -c%s "$D/$c.spef")" >> "$RESULT"
    echo "  ideal $IW ；read_spef 后无输出"
    continue
  fi
  DW=$(awk -v a="$PW" -v b="$IW" 'BEGIN{printf "%.4f", a-b}')
  DT=$(awk -v a="$PT" -v b="$IT" 'BEGIN{printf "%.4f", a-b}')
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$IW" "$IT" "$PW" "$PT" "$DW" "$DT" \
    "routed" "$(stat -c%s "$D/$c.def")" "$(stat -c%s "$D/$c.spef")" >> "$RESULT"
  echo "  ideal $IW / $IT   post $PW / $PT   dWNS=$DW dTNS=$DT"
done

echo
echo "===== ITC'99 ====="
column -t -s $'\t' "$RESULT"
