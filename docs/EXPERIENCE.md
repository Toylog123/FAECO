# 开发经验库（踩坑记录）

> 解决问题后当天登记。历史坑位自 work_log 摘录高频项，完整记录见 `project_docs/LOGS.md`。

## 工具链

1. **Windows Yosys 0.9（32 位）映射大电路 OOM**
   - 现象：b18/b19（原型约 7.0 万/23.1 万门；**2026-09-28 更正**：原记「37.6 万/75.5 万门」在任何证据文件中均无法定位，映射后为 7.57 万/15.10 万个 SKY130 单元，见 `project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md` §6）read_verilog bad_alloc；$shr 技术映射 OOM。
   - 解决：WSL2 64 位 Yosys 0.33（`run_yosys_mapping` 增加 `yosys_cmd` 参数）。
   - 验证：b18/b19 映射成功（峰值 4.7 GB）。

2. **SKY130 `clkinv_1` 不在 Liberty → CEC unavailable**
   - 解决：从 Liberty boolean function 提取 assign-style `sky130_cells_v2.v` + Yosys `miter -equiv` + `sat -prove-asserts`；8/8 等价证明通过（20260803）。

3. **b19（7.5 万单元）WSL2 STA 输出截断**
   - 解决：`run_opensta()` 3 次重试 + 手工复测校验（WNS=-17.42 一致）。

## 形式验证

4. **顺序 SEC `find_same_wires` 局限（b17 剩 1 个未证明点）**
   - 现象：nor4b_1→nor4b_2 同函数尺寸替换因两侧 wire 命名不一致未匹配。
   - 结论：Liberty function 等价即 effective_pass；论文如实单独报告（12812/12813）。

## 流程 / 工程

5. **多轮 ablation 被 early-stop 截断（假阴性）**
   - 原因：flow.py 接受分支无条件 return True。
   - 解决：仅 `early_stop` 开启时提前返回（flow.py:471）；264 测试全绿；备份 `project_docs/archive/superpowers_backup/T19_20260908/`。

6. **论文数字与实验产物混源（2026-09-11 审计）**
   - 教训：同一小节混用两轮运行数字（1012 次 STA、b21 +2.16、JOINT-12 均无产物支持）。
   - 规则：先更新聚合 summary 再动论文；审计记录 `project_docs/review_history/paper_audit/consistency_audit_20260911.md`。

7. **仓库迁移（2026-09-12）**
   - 目录 rename 被 BaiduSync 客户端句柄阻塞（Device or resource busy）→ robocopy 复制（316,765 文件/117.7 GB，0 失败）+ 源目录留作归档。
   - `.venv` 可编辑安装路径失效 → 重新 `pip install -e .`；硬编码绝对路径脚本改为 `__file__` 锚定。

8. **LaTeX 双栏 `figure*` 独占整页造成版面塌陷（2026-09-28）**
   - 现象：第 5 页仅 7 行、约 80% 空白；且 §3.3 正文在上一页末被截断，跨过图页才续上，阅读流断裂。
   - 根因三重叠加：① 图为 1254×1254 正方形、宽度 `0.85\textwidth`（14.4×14.4 cm）过高；② 位置参数 `[!htbp]` 含 `p`，允许 LaTeX 生成"只含浮动体"的浮动页；③ 图前 `\FloatBarrier`（`placeins` 包）强制立即输出，与图后屏障形成夹逼。
   - 解决：改 `[!tb]` 禁用浮动页 + 宽度降到 `0.55\textwidth` + 删除图前屏障 + 合并相邻重复 `\FloatBarrier`（全文 20 处，其中 2 组为连续重复，功能等价无意义）。
   - 结果：10 页 → **9 页**；第 5 页 7→43 行（图 + 正文 + 表 3 同页共存），末页结论与参考文献同页、不再孤立成页；0 Error / 0 Overfull / 0 Underfull。
   - 规则：双栏文档慎用 `figure*` + `p` 位置 + `\FloatBarrier` 三者叠加；`\FloatBarrier` 只在节边界保留 1 个，禁止连续重复（重复调用无额外作用，却让版面僵硬）。

9. **PDF SHA256 不能作为"内容一致"的判据（2026-09-28）**
   - 现象：同一 `.tex` 一字未改，重编译后 PDF SHA256 由 `5c98b77d…` 变为 `611741c5…`，看似"内容变了"。
   - 根因：PDF 内嵌编译时间戳（CreationDate / ModDate）元数据，每次编译字节必变。
   - 解决：判定内容是否真一致改用 **`pdftotext -layout` 全文的 SHA256**（本次 `856fac5b…`），并配合页数与质量门；实测两次编译文本指纹完全相同、`diff` 无差异，确认仅元数据变化。
   - 规则：冻结记录须同时给出「PDF 字节 SHA256」（标识该文件副本）与「文本指纹」（标识内容）；不可只用前者断言内容一致，也不可因前者变化就判内容被改。
