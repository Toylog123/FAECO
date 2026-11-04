#!/usr/bin/env bash
# 批量生成 ITC'99 六例的 ECO 网表（在 WSL 内运行）
#   bash code/scripts/gen_eco_itc_all.sh [cases...]
set -uo pipefail
R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
L=$R/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
OUT=$R/experiments/20261029_itc99_eco_fournum
A=$R/experiments/20261029_itc99_26q3        # b11 b12 b13
B=$R/experiments/20261029_itc99_scale_26q3  # b14 b15 b20

CASES=${*:-"b11 b12 b13 b14 b15 b20"}
cd "$R" || exit 1

for c in $CASES; do
  case "$c" in
    b11|b12|b13) SRC=$A/$c ;;
    *)           SRC=$B/$c ;;
  esac
  if [ ! -s "$SRC/mapped.v" ]; then echo "### $c  缺网表 $SRC/mapped.v"; continue; fi
  if [ -s "$OUT/$c/swap.tsv" ] && [ -s "$OUT/$c/mapped.v" ] && [ "$c" != "b13" ]; then
    echo "### $c  已存在，跳过"; continue
  fi
  echo "### $c  ($SRC)"
  python3 "$R/code/scripts/gen_itc_eco.py" \
    --net "$SRC/mapped.v" --top "$c" --sdc "$SRC/constraint.sdc" --lib "$L" \
    --out-dir "$OUT/$c" 2>&1 | tail -8
  echo
done
