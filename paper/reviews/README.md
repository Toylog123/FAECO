# Paper Reviews (自审稿占位)

更新时间：2026-07-31

论文自审稿与修改记录目录。当前为空，等待章节初稿全部获用户审定后从 `paper/draft/` 迁入并启动模拟审稿 (PM29)。

## 计划结构

```
paper/reviews/
├── README.md
├── round1_self_audit.md       (PM29 第 1 轮自审 — 已落地 2026-07-31)
├── round1_external_audit.md   (PM29 模拟审稿意见)
├── round1_revision_notes.md   (PM30 第 1 轮修订说明 — 已落地 2026-07-31)
├── round2_self_audit.md       (PM30 第 2 轮自审 — 已落地 2026-08-03)
├── round2_*.md                (PM30 第 2 轮修订)
└── final_review.md            (PM30 终审)
```

## 自审稿检查清单（草案）

每轮自审稿按以下维度评估论文章节：

### 1. 方法 (Method, PM27 + N05)

- [ ] METH-01 partial：combinational fanin cone；待 PM23 sequential
- [ ] METH-02 ready：Yosys 规范化命令序列已 TDD 实现
- [ ] METH-05 ready：weighted s-t min-cut 已 TDD 实现
- [ ] METH-08 partial：Stage A CEC 5/5 pass；Stage B CEC unavailable (R31-01)
- [ ] METH-09 partial：F1-F5 taxonomy 已写；X19 multi-iteration 待启动
- [ ] METH-10 partial：failure-aware refinement single-iteration proxy
- [ ] METH-12 partial：deterministic ranking
- [ ] METH-15 ready：runtime schema
- [ ] METH-17 partial：Stage A 5-case + Stage B 8-case

### 2. 实验 (Experiments, PM28)

- [ ] Stage A 5-case multi-baseline 表格（6 baselines）
- [ ] Stage B 8-case per-case mapping + STA 表格
- [ ] Stage B 8-case runtime breakdown
- [ ] Stage A 5-case failure recovery proxy 表
- [ ] Stage B 8-case CEC unavailable limitation 明确标注
- [ ] Stage B 8-case STA slack=null limitation 明确标注

### 3. 相关工作 (Related Work, L01)

- [ ] 6 大主题分组覆盖 25A/1B 文献
- [ ] [F08-B] / [B06] 禁止引用算法细节与数字
- [ ] [T01]/[T02]/[T05]/[F01]/[F03]/[F07] 工业数据禁止作为对比
- [ ] 公开性边界（可写 / 禁写）声明完整

### 4. 限制与未来工作

- [ ] L31-01 / R31-01 SKY130 `clkinv_1` limitation 透明
- [ ] L31-02 STA slack=null limitation 透明
- [ ] L31-04 / X19 failure_recovery proxy limitation 透明
- [ ] N31-03 / N31-05 / N31-06 未来工作明确

### 5. 工具链与可复现性

- [ ] Yosys 0.9 / ABC 1.01 / OpenSTA 3.1.0 版本明确
- [ ] SKY130 Liberty SHA256 与 manifest 一致
- [ ] EPFL `v2025.1` commit 固定
- [ ] 每个实验目录有 toolchain_snapshot.json
- [ ] runner 命令可复现

## 边界

- 自审稿与外部审稿分离，避免混淆
- 自审稿必须诚实标注 limitation，禁止掩盖已知问题
- [F08-B] DAC 2018 / [B06] BUFFALO 数据禁止作为自审稿支撑
- 任何审稿意见必须可追溯到具体章节或实验产物