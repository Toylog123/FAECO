#!/usr/bin/env bash
# 从产物机械生成 ITC'99 六例物理档表（不手打任何数字）
#
# 每个数字都来自磁盘：
#   ideal/post WNS/TNS  <- 现场重跑 sta_ideal.tcl / sta_post.tcl
#   cells/dfxtp         <- mapped.v
#   DRC 违规数          <- drc.rpt
#   spef/def 字节数     <- 文件大小
#
# 用法（WSL 内）：
#   wsl.exe -d Ubuntu -- bash code/scripts/gen_itc6_table.sh
#   输出 experiments/20261029_itc99_scale_26q3/phys_itc6_final.tsv
set -u
R=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
STA=/home/toylog/faeco_eda/or26Q3/bin/sta
OUT=$R/experiments/20261029_itc99_scale_26q3/phys_itc6_final.tsv

# case:family_dir:util
CASES="b11:20261029_itc99_26q3:35 b12:20261029_itc99_26q3:35 b13:20261029_itc99_26q3:35 b14:20261029_itc99_scale_26q3:35 b15:20261029_itc99_scale_26q3:35 b20:20261029_itc99_scale_26q3:35"

printf 'circuit\tcells\tdff\tideal_wns\tideal_tns\tpost_wns\tpost_tns\tdelta_wns\tdelta_tns\tdeg_pct\tutil\tdrc\tspef_bytes\tdef_bytes\n' > "$OUT"

for spec in $CASES; do
  c=${spec%%:*}; rest=${spec#*:}; fam=${rest%%:*}; u=${rest##*:}
  D=$R/experiments/$fam/$c
  if [ ! -s "$D/$c.spef" ]; then
    printf '%s\t-\t-\t-\t-\tNO_ROUTED\t-\t-\t-\t-\t%s\t-\t-\t-\n' "$c" "$u" >> "$OUT"
    continue
  fi
  cd "$D" || continue
  i=$($STA -no_init -exit sta_ideal.tcl 2>&1 | grep 'worst slack max' | awk '{print $4}')
  ti=$($STA -no_init -exit sta_ideal.tcl 2>&1 | grep 'tns max' | awk '{print $3}')
  p=$($STA -no_init -exit sta_post.tcl 2>&1 | grep 'worst slack max' | awk '{print $4}')
  tp=$($STA -no_init -exit sta_post.tcl 2>&1 | grep 'tns max' | awk '{print $3}')
  cells=$(grep -c 'sky130_fd_sc_hd__' mapped.v)
  dff=$(grep -c 'sky130_fd_sc_hd__dfxtp' mapped.v)
  drc=$(grep -c 'violation type' drc.rpt 2>/dev/null | head -1)
  spef=$(stat -c%s "$c.spef")
  def=$(stat -c%s "$c.def" 2>/dev/null || echo 0)
  awk -v c="$c" -v ce="$cells" -v df="$dff" -v i="$i" -v ti="$ti" -v p="$p" -v tp="$tp" \
      -v u="$u" -v dr="$drc" -v sp="$spef" -v de="$def" 'BEGIN{
        if (i+0 == 0) { printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\tNA\tNA\tNA\t%s\t%s\t%s\t%s\n", c,ce,df,i,ti,p,tp,u,dr,sp,de; exit }
        dw=p-i; dt=tp-ti; deg=(i!=0)? (dw<0?-dw:dw)/((i<0?-i:i))*100 : 0;
        printf "%s\t%s\t%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.1f\t%s\t%s\t%s\t%s\n", c,ce,df,i,ti,p,tp,dw,dt,deg,u,dr,sp,de
      }' >> "$OUT"
  echo "  $c done"
done

echo "== 写好 $OUT =="
column -t -s $'\t' "$OUT"
