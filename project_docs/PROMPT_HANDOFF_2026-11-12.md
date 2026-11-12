# FAECO 项目接手提示词

> **2026-11-13 最新接手裁定**：先读 `project_docs/evidence/recovery_repair_20261113/REPORT.md` 与CANON顶部。完整14例面积已核算，平均下降3.071500828%；旧“14%”分母不等于总面积，136/202也不是逐个零贡献证明。新41候选物理研究已封口：s382仅回收 `_096_` 得面积下降0.594530321%、propagated WNS/TNS改善及hold不变，SEC 101/0通过；这是局部简单基线，自有联合机制/跨设计/完整约束仍未建立。全回收4.399524%因时序失败不得晋级。旧摘要/HEAD/未push状态仅供溯源；当前Git以实查为准。论文冻结，上一生产全回归1113 passed/156 subtests；工具镜像见 `docs/environment.md`。

你是 FAECO 项目的接手者。以下是需要知道的一切，按顺序执行。

## 第一步：理解项目（5 分钟）

读 `project_docs/HANDOFF_2026-11-12.md` 全文（10 节，约 20 分钟读完核心部分）。

**当前项目一句话**：我们在 OpenROAD Resizer 的最佳 WNS 基础上，做了一个选择性面积恢复机制（Faeco-Recovery），发现在 14 个电路（ISCAS89 + ITC-99）上 Resizer 的 67% 门级改动对 WNS 无任何贡献，我们把这些改动安全回退，平均回收 14.0% 面积。

## 第二步：验证环境可运行

```bash
cd /d/BaiduSyncdisk/01_Papers/03_FAECO
export PATH="/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:$PATH"

# 1. 全量测试
.venv/Scripts/python.exe -m pytest code/tests -q --tb=line
# 预期：1095 passed, 7 skipped, 156 subtests

# 2. Recovery CLI 冒烟（秒级，不跑 STA）
.venv/Scripts/python.exe code/scripts/recover_area.py --help

# 3. 论文编译
cd paper/en/manuscript && pdflatex -interaction=nonstopmode FAECO_recovery.tex && pdflatex -interaction=nonstopmode FAECO_recovery.tex
# 预期：4 pages, 0 errors
```

## 第三步：阅读关键文件

| 顺序 | 文件 | 重点 |
|------|------|------|
| 1 | `project_docs/CANON.md` §1 | 裁定 15–22（方向转折 + Recovery 裁定） |
| 2 | `project_docs/HANDOFF_2026-11-12.md` §2 | 项目演变（为什么我们现在在做 Recovery） |
| 3 | `paper/en/manuscript/FAECO_recovery.tex` | 当前论文（4 页，14 电路 / 2 基准族） |
| 4 | `code/scripts/recover_area.py` | Recovery 主算法（555 行，生产级 CLI） |

## 第四步：当前状态

| 项目 | 数值 |
|------|------|
| 电路数 / 基准族 | **14 / 2**（ISCAS89 8 例 + ITC-99 6 例） |
| Resizer 改动 | 202 处 |
| 可回退 | 136 (67%) |
| 面积回收 | 14.0%（最大 b07 33.3%） |
| ΔWNS | max 0.0057 ns |
| 论文 | IEEEtran 4 页，0 错误 |
| 测试 | 1095 passed, 7 skipped |
| Git HEAD | `7776ccb`（ahead 55，未 push） |

## 第五步：后续工作（三条路线）

**推荐：路线 A + C 组合**
- **C（叙事重构）**：把论文叙事从"我们做了一个 Recovery 算法"改成"我们发现 Resizer 67% 的改动是浪费的"——定义新问题 + 提供审计方法论 + Recovery 作为解决方案的一个实例
- **A（学习驱动）**：在现有的贪心评估基础上，训练一个轻量分类器预测"改动是否可安全回退"，做跨设计 zero-shot 迁移（ISCAS89 → ITC-99）
- **预期**：2–3 周工作量，论文可投 DAC/ICCAD 2027

**备选：路线 B（实验扩面）**
- 加 PDK（ASAP7）、加基准族（OpenCores）、加指标（wirelength/power）
- 1 周工作量，不改论文叙事

## 第六步：注意事项

1. **不要回到「预布局门级 ECO 判据优化」老路上去**——那个方向已经封口（五轮实验全不晋级）。当前唯一活跃的方向是 Recovery。
2. **push 被 GitHub 超时阻断**——网络恢复后 `git push` 即可。
3. **每次跑代码前 PATH 必须前置 oss-cad-suite**（见第二步）。
4. **凡涉及 WSL 的命令必须 `export MSYS_NO_PATHCONV=1`**。
5. **端点缓存必须带 netlist sha256**——只按 (arm,circuit,util) 键控会命中旧读数。
6. **Resizer 输出的 `routed.v` 不能塞回标准路由流程**（扁平化格式会导致 segfault）。用 Resizer 自己的 SPEF + 独立 `sta` 读 WNS。

## 核心文档速查

| 问题 | 去哪个文件 |
|------|-----------|
| 这个数字从哪来的？ | `project_docs/CANON.md` §3 |
| 这个东西能不能做？ | CANON §5（不可翻） + §8（待决） |
| Recovery 怎么跑？ | `code/scripts/recover_area.py` |
| 论文写到哪了？ | `paper/en/manuscript/FAECO_recovery.tex` |
| 之前的实验在哪？ | `experiments/202611*/**/REPORT.md` |
| 遇到坑了？ | `project_docs/HANDOFF_2026-11-12.md` §6
