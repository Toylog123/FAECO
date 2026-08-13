# -*- coding: utf-8 -*-
import io
path = r"D:/BaiduSyncdisk/03_FAECO/paper/zh/manuscript/faeco_paper.tex"
with io.open(path, "r", encoding="utf-8") as f:
    c = f.read()
# 定位 tab:parasitic 表的 end{table}，在其后插入图
li = c.find("\\label{tab:parasitic}")
assert li >= 0, "label not found"
es = c.find("\\end{table}", li)
assert es >= 0, "end not found"
es += len("\\end{table}")
fig = ("\r\n\r\n图~\\ref{fig:spef} 对比不同修复类型在 SPEF 负载扫描下的 WNS 改善保持性：b18 的单门 R 候选随线长增加衰减，b18 JOINT 与 b19 G 候选（驱动增强为主）在 2--40\\,$\\mu$m 下保持改善。\r\n\r\n"
       "\\begin{figure}[!t]\r\n"
       "\\centering\r\n"
       "\\caption{SPEF 负载扫描下 WNS 改善随线长的变化：单门 R 候选衰减归零，驱动增强（G/JOINT）候选保持。}\r\n"
       "\\label{fig:spef}\r\n"
       "\\includegraphics[width=\\columnwidth]{fig_spef.png}\r\n"
       "\\end{figure}\r\n")
c = c[:es] + fig + c[es:]
# 结论段加图引用
old = "结论：在理想网络下有效的修复"
new = "结论（见图~\\ref{fig:spef}）：在理想网络下有效的修复"
assert old in c
c = c.replace(old, new, 1)
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(c)
print("SPEF FIG INSERTED")
