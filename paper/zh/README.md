# paper/zh — FAECO 论文（LaTeX 唯一源）

2026-08-04 起，FAECO 论文只以 LaTeX 形式维护于本目录。**当前主稿已进入内容冻结**（用户指令，2026-09-29）：
tag `faeco-paper-final-20260929`（= `a8142b6`），9 页 / 0 Error / 0 Overfull / 0 Underfull。

## 结构

- `manuscript/FAECO_面向预布局门级时序ECO的结构化候选搜索与失效归因.tex`：**唯一主稿**（单文件 ctexart，lualatex 编译；JCAD 版式近似）
- `manuscript/FAECO_….pdf` 与 `FAECO_….pdf`（本目录）：**双副本**，字节 SHA256 须一致
- `submission/`：**T20 投稿件打包**（目标期刊 JCAD）——投稿检查单、cover letter 草稿、补充材料清单
- `figures/`：图源（`fig_iscas89.pdf` 为编译依赖，禁删）
- `responses/`、`review_rounds/`：审稿轮次记录
- `build/`：编译中间产物
- `CHANGE_LOG.md`：论文改动日志（每次改 `.tex` 必须登记）

## 编译与验收

```bash
cd paper/zh/manuscript
lualatex -interaction=nonstopmode "FAECO_面向预布局门级时序ECO的结构化候选搜索与失效归因.tex"   # 跑两遍
python ../scripts/checks/latex_quality_gate.py   # Errors/Overfull/Underfull 全 0，PAGES=9
cp "FAECO_….pdf" "../FAECO_….pdf"                # 同步双副本，字节 SHA256 一致
pdftotext -layout "FAECO_….pdf" - | sha256sum    # 内容指纹（判内容一致用这个，不用字节 SHA）
```

- 质量门的 `Undefined: 5` 是字体替身警告，非引用未解析（判引用看 `??` 计数）。
- 版面异常**先查 `\FloatBarrier`**（双栏下会退化为 `\clearpage`），禁止缩字体/行距/砍内容。

## 内容维护

- **内容修改已冻结**：任何内容改动须先取得用户同意；改 `.tex` 前先读 `project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md`（逐数字绑定）。
- 数字只认 `experiments/20260826_aggregation/summary.json` 等已钉定实验族产物；铁律 `same claim ⇒ same revision + same config family`。
- 诚实记录负面结论（EMA 无独立增益、S 无 timing repair capability 等已如实写入）。
- 参考文献使用手写 thebibliography（19 条），新增引用时同步更新编号。
