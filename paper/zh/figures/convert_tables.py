# -*- coding: utf-8 -*-
import re, io, sys
path = r"D:/BaiduSyncdisk/03_FAECO/paper/zh/manuscript/faeco_paper.tex"
with io.open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 转换清单: (label, figfile, env, width)
# 全部表格转图已完成（2026-08-06）：
#   stageb / iscas_main / beam_feedback / decision_early / adaptive_vs_static /
#   ablation / itc99 / ood / loocv / parasitic -> 对应 fig_*.png
# 保留表格：tab:symbols / tab:failures / tab:selector / tab:limitations / tab:hold
convs = []
fail = []
for label, fig, env, width in convs:
    li = content.find("\\label{" + label + "}")
    if li < 0:
        fail.append(label + ":label-not-found")
        continue
    # 从 label 位置向前找最近的 \begin{table}[!t]
    bs = content.rfind("\\begin{table}[!t]", 0, li)
    if bs < 0:
        bs = content.rfind("\\begin{table}", 0, li)
    if bs < 0:
        fail.append(label + ":begin-not-found")
        continue
    # 从 label 位置向后找最近的 \end{table}
    es = content.find("\\end{table}", li)
    if es < 0:
        fail.append(label + ":end-not-found")
        continue
    es += len("\\end{table}")
    block = content[bs:es]
    capm = re.search(r"\\caption\{(.*?)\}", block, re.S)
    cap = capm.group(1) if capm else ""
    newlabel = label.replace("tab:", "fig:")
    newfig = ("\\begin{" + env + "}[!t]\r\n"
              "\\centering\r\n"
              "\\caption{" + cap + "}\r\n"
              "\\label{" + newlabel + "}\r\n"
              "\\includegraphics[width=" + width + "]{" + fig + "}\r\n"
              "\\end{" + env + "}")
    content = content[:bs] + newfig + content[es:]
    print("OK", label, "->", fig, "len", len(block))

# 同步引用
for label, fig, env, width in convs:
    newlabel = label.replace("tab:", "fig:")
    content = content.replace("{" + label + "}", "{" + newlabel + "}")
content = content.replace("表~\\ref{fig:", "图~\\ref{fig:")
content = content.replace("Tab.~\\ref{fig:", "图~\\ref{fig:")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(content)
if fail:
    print("PARTIAL-FAIL", fail)
    sys.exit(1)
print("ALL DONE")
