#!/usr/bin/env bash
# FAECO sky130hd 物理档生成器（在 WSL 内执行）
#
# 用途：把一份 RTL/门级源映射到 sky130_fd_sc_hd，再走完 floorplan -> place ->
# CTS -> global route -> detail route -> OpenRCX 提取，产出 DEF 与 SPEF，
# 供 OpenSTA 以 read_spef 方式计算布线后（post-route）时序。
#
# 依赖（均在 WSL 内）：
#   yosys     >= 0.33   （需支持 dfflibmap；否则寄存器会留成 $_DFF_* 黑盒）
#   openroad  v2.0      （本机为 1 a5a56584，装在 WSL 发行版 `Ubuntu`）
#
# 平台资产全部取自项目归档，不依赖 ORFS 完整检出：
#   data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a.../
#
# 用法（两种入口，二选一）：
#   A. 从 RTL 起： -v <src.v> -t <top> -c <clock_port> -p <period_ns>
#   B. 复用既有网表： -n <mapped.v> -t <top>      （跳过 yosys，保证网表不变）
#   两者都需 -o <outdir>；可选 --util <35>（初始利用率，%）、--drt-iter <15>
#   （详细布线迭代上限）、--sdc <file>
#   （给 --sdc 时原样使用该 SDC，用于与既有实验逐字对齐口径）
#
# 产出（<outdir> 下）：
#   mapped.v          yosys 映射后网表（含 dfflibmap；入口 B 下为 -n 的副本）
#   constraint.sdc    约束（--sdc 原样复制；否则按 code/src/rseco/sdc.py 生成）
#   <top>.def         布线后 DEF
#   <top>.spef        OpenRCX 提取的寄生参数
#   phys_flow.tcl     本次运行的完整 Tcl（可复现）
#   openroad.log      全量日志
#
# 说明：本流程用 OpenROAD 内核命令直接驱动，不经 ORFS 的 Makefile 与 metrics
# 封装层，因为那层脚本与 OpenROAD v2.0 二进制存在 API 代差（utl:: 命名空间）。
set -euo pipefail

FAECO_ROOT="${FAECO_ROOT:-/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO}"
PLAT_REL="data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629"
PLAT="$FAECO_ROOT/$PLAT_REL"

VERILOG="" ; NETLIST="" ; TOP="" ; CLK="" ; PERIOD="" ; OUT="" ; UTIL=35 ; SDC="" ; DRT_ITER=15

# 可切换 OpenROAD 二进制（换栈时用；同一次实验族内必须保持同一个）
#   默认: PATH 里的 openroad（当前为 v2.0）
#   26Q3: OR_BIN=/home/toylog/faeco_eda/or26Q3/bin/openroad
OR_BIN="${OR_BIN:-openroad}"

# 26Q3 起必须补两步，v2.0 不需要；默认关闭以保证旧族仍可逐位复现
#   POSTCTS_LEGALIZE=1 : CTS 后补 repair_clock_nets + detailed_placement
#                        否则时钟缓冲停在非站点位置，DRT 报 DRT-0073 No access point
#   PIN_ACCESS=1       : 全局布线前先跑 pin_access（26Q3 官方 flow.tcl 的顺序）
POSTCTS_EXTRA=""
if [ "${POSTCTS_LEGALIZE:-0}" = "1" ]; then
  POSTCTS_EXTRA="repair_clock_nets
detailed_placement"
fi
PREGRT_EXTRA=""
if [ "${PIN_ACCESS:-0}" = "1" ]; then
  PREGRT_EXTRA="pin_access"
fi

while [ $# -gt 0 ]; do
  case "$1" in
    -v) VERILOG=$2 ; shift 2 ;;
    -n) NETLIST=$2 ; shift 2 ;;
    -t) TOP=$2 ; shift 2 ;;
    -c) CLK=$2 ; shift 2 ;;
    -p) PERIOD=$2 ; shift 2 ;;
    -o) OUT=$2 ; shift 2 ;;
    --util) UTIL=$2 ; shift 2 ;;
    --drt-iter) DRT_ITER=$2 ; shift 2 ;;
    --sdc) SDC=$2 ; shift 2 ;;
    *) echo "未知参数: $1" >&2 ; exit 2 ;;
  esac
done

[ -n "$TOP" ] || { echo "缺少参数: TOP (-t)" >&2 ; exit 2 ; }
[ -n "$OUT" ] || { echo "缺少参数: OUT (-o)" >&2 ; exit 2 ; }

if [ -n "$NETLIST" ] && [ -n "$VERILOG" ]; then
  echo "-n 与 -v 只能二选一" >&2 ; exit 2
fi
if [ -n "$NETLIST" ]; then
  [ -f "$NETLIST" ] || { echo "网表不存在: $NETLIST" >&2 ; exit 1 ; }
else
  for n in VERILOG CLK PERIOD; do
    [ -n "${!n}" ] || { echo "缺少参数: $n" >&2 ; exit 2 ; }
  done
  [ -f "$VERILOG" ] || { echo "源文件不存在: $VERILOG" >&2 ; exit 1 ; }
fi
if [ -n "$SDC" ] && [ ! -f "$SDC" ]; then
  echo "SDC 不存在: $SDC" >&2 ; exit 1
fi
for f in "$PLAT/lef/sky130_fd_sc_hd.tlef" "$PLAT/lef/sky130_fd_sc_hd_merged.lef" \
         "$PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib" "$PLAT/make_tracks.tcl" \
         "$PLAT/setRC.tcl" "$PLAT/rcx/rcx_patterns.rules" ; do
  [ -f "$f" ] || { echo "平台资产缺失: $f" >&2 ; exit 1 ; }
done
command -v yosys    >/dev/null || { echo "找不到 yosys" >&2 ; exit 1 ; }
command -v "$OR_BIN" >/dev/null 2>&1 || [ -x "$OR_BIN" ] || { echo "找不到 openroad: $OR_BIN" >&2 ; exit 1 ; }
echo "   OpenROAD 二进制: $OR_BIN"
echo "   版本: $("$OR_BIN" -version 2>&1 | head -1)"

mkdir -p "$OUT"

echo "== 1/3 网表 =="
if [ -n "$NETLIST" ]; then
  if [ "$(readlink -f "$NETLIST")" = "$(readlink -f "$OUT/mapped.v" 2>/dev/null || echo none)" ]; then
    echo "   网表已在输出目录: $NETLIST"
  else
    cp -p "$NETLIST" "$OUT/mapped.v"
    echo "   复用既有网表: $NETLIST"
  fi
else
  yosys -q -p "read_verilog $VERILOG; hierarchy -check -top $TOP; proc; flatten; opt; \
synth -top $TOP -noabc; dfflibmap -liberty $PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib; \
abc -liberty $PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib; clean; \
write_verilog -noattr -noexpr $OUT/mapped.v"
fi
[ -s "$OUT/mapped.v" ] || { echo "映射失败" >&2 ; exit 1 ; }
echo "   mapped.v = $(stat -c%s "$OUT/mapped.v") B"

echo "== 2/3 SDC =="
if [ -n "$SDC" ]; then
  cp -p "$SDC" "$OUT/constraint.sdc"
  echo "   原样使用: $SDC"
else
cat > "$OUT/constraint.sdc" <<EOT
# FAECO physical-flow SDC（写法对齐 code/src/rseco/sdc.py）
create_clock -name clk -period $PERIOD [get_ports $CLK]
set in_ports {}
foreach p [all_inputs] { if { [string equal \$p $CLK] == 0 } { lappend in_ports \$p } }
set_input_delay -clock clk [expr {$PERIOD * 0.2}] \$in_ports
set_output_delay -clock clk [expr {$PERIOD * 0.2}] [all_outputs]
set_load 0.100 [all_outputs]
EOT
fi

echo "== 3/3 OpenROAD 物理流程 =="
cat > "$OUT/phys_flow.tcl" <<EOT
read_lef $PLAT/lef/sky130_fd_sc_hd.tlef
read_lef $PLAT/lef/sky130_fd_sc_hd_merged.lef
read_liberty $PLAT/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog $OUT/mapped.v
link_design $TOP
puts "STAGE=linked cells=[llength [get_cells *]]"
source $OUT/constraint.sdc
initialize_floorplan -utilization $UTIL -aspect_ratio 1 -core_space 2 -site unithd
source $PLAT/make_tracks.tcl
place_pins -hor_layers met3 -ver_layers met2
global_placement -density 0.55
detailed_placement
puts "STAGE=place done"
clock_tree_synthesis -buf_list {sky130_fd_sc_hd__clkbuf_4 sky130_fd_sc_hd__clkbuf_8} -root_buf sky130_fd_sc_hd__clkbuf_16
$POSTCTS_EXTRA
set_propagated_clock [all_clocks]
puts "STAGE=cts done"
source $PLAT/setRC.tcl
set_routing_layers -signal met1-met5 -clock met3-met5
$PREGRT_EXTRA
global_route
detailed_route -output_drc $OUT/drc.rpt -verbose 0 -droute_end_iter $DRT_ITER
puts "STAGE=route done"
write_def $OUT/$TOP.def
write_verilog $OUT/$TOP.routed.v
puts "STAGE=routed_verilog written"
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $PLAT/rcx/rcx_patterns.rules
write_spef $OUT/$TOP.spef
puts "STAGE=spef written"
puts "STAGE=ALL_OK"
EOT

# OpenROAD 会把 route.guide 之类的工作文件写进当前目录，故在输出目录内运行
cd "$OUT"
"$OR_BIN" -no_init -exit -log "$OUT/openroad.log" "$OUT/phys_flow.tcl" \
  | grep -E "STAGE=|RCX-|DRT-0198" || true
cd - >/dev/null

[ -s "$OUT/$TOP.spef" ] || { echo "SPEF 未生成，见 $OUT/openroad.log" >&2 ; exit 1 ; }
echo "== 完成 =="
echo "  DEF  : $OUT/$TOP.def  ($(stat -c%s "$OUT/$TOP.def") B)"
echo "  ROUTED: $OUT/$TOP.routed.v ($(stat -c%s "$OUT/$TOP.routed.v" 2>/dev/null || echo 0) B)"
echo "  SPEF : $OUT/$TOP.spef ($(stat -c%s "$OUT/$TOP.spef") B)"
echo "  DRC  : $OUT/drc.rpt   ($(grep -c 'violation' "$OUT/drc.rpt" 2>/dev/null || true) 行)"
