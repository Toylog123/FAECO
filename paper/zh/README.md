# paper/zh — FAECO 论文（LaTeX 唯一源）

2026-08-04 起，FAECO 论文只以 LaTeX 形式维护于本目录，paper/draft/*.md 草稿不再更新（保留在 git 历史中仅作存档）。

## 结构

- manuscript/faeco_paper.tex：单文件 IEEEtran + ctex 稿件（xelatex 编译）
- faeco_paper.pdf：编译产物（发布版）
- build/：latexmk 中间产物 + qa_faeco/ 逐页 PNG 渲染 QA

## 编译

```powershell
Push-Location manuscript
latexmk -g -xelatex -interaction=nonstopmode -halt-on-error -outdir=../build faeco_paper.tex
Pop-Location
Copy-Item build/faeco_paper.pdf faeco_paper.pdf -Force
```

## 内容维护

- 内容以实验产物（experiments/）和代码实现为准，禁止沿用不可复现数字。
- 诚实记录负面结论（如 buf_8/16 有害、消融 ON/OFF 无差异）。
- 参考文献使用手写 thebibliography，新增引用时同步更新编号。
